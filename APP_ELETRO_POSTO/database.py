"""
Módulo unificado de Banco de Dados MySQL para o projeto EletroBel Posto.
Verifica e cria automaticamente o banco de dados `eletrobel_posto` e todas as
suas tabelas no servidor MySQL (Online Aiven Cloud / Local MySQL), além de
migrar automaticamente quaisquer registros legados para o MySQL.
"""
import hashlib
import os
from datetime import date, datetime
from decimal import Decimal

import mysql.connector
from mysql.connector import Error, IntegrityError

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

# Diretórios base e carregamento do .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

for _env_candidate in (
    os.path.join(PROJECT_ROOT, ".env"),
    os.path.join(BASE_DIR, ".env"),
):
    if os.path.exists(_env_candidate):
        load_dotenv(_env_candidate, override=False)
load_dotenv()

# Caminhos dos scripts SQL sincronizados com o banco MySQL
SQL_SCRIPT_PATH = os.path.join(BASE_DIR, "eletrobel_posto.sql")
BANCO_SQL_PATH = os.path.join(BASE_DIR, "banco_de_dados.sql")
BANCO_TXT_PATH = os.path.join(BASE_DIR, "banco_de_dados.txt")
EXTERNAL_SQL_SCRIPT_PATH = os.path.join(
    os.path.dirname(PROJECT_ROOT),
    "Banco de Dados",
    "Banco de Dados Eletrobel_Posto.sql",
)

_raw_port = os.getenv("DB_PORT", "27403").strip()
_default_port = int(_raw_port) if _raw_port.isdigit() else 27403
_raw_host = (os.getenv("DB_HOST") or "arilsonvalente-arilsonvalente-7683.g.aivencloud.com").strip()
if _raw_host.lower() == "localhost":
    _raw_host = "127.0.0.1"

# Configuração principal do MySQL (Aiven Cloud / .env)
DB_CONFIG = {
    "host": _raw_host,
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": _default_port,
}

# Configuração secundária do MySQL Local (127.0.0.1:3306)
LOCAL_MYSQL_CONFIG = {
    "host": os.getenv("LOCAL_DB_HOST"),
    "user": os.getenv("LOCAL_DB_USER"),
    "password": os.getenv("LOCAL_DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("LOCAL_DB_PORT"))
}


class _ManagedMySQLConnection:
    """
    Wrapper sobre a conexão MySQL persistente para uso com `with conectar() as conn:`.
    Faz commit ao sair do bloco sem fechar o socket TCP subjacente.
    """

    def __init__(self, raw_conn):
        self._raw = raw_conn

    def cursor(self, *args, **kwargs):
        return self._raw.cursor(*args, **kwargs)

    def commit(self):
        return self._raw.commit()

    def rollback(self):
        return self._raw.rollback()

    def is_connected(self):
        return self._raw.is_connected()

    def close(self):
        try:
            self._raw.commit()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                self._raw.commit()
            except Exception:
                pass
        else:
            try:
                self._raw.rollback()
            except Exception:
                pass
        return False


class Database:
    """
    Classe gerenciadora de conexão com o Banco de Dados MySQL.
    Verifica se o banco `eletrobel_posto` existe e o cria automaticamente caso não exista.
    """

    def __init__(self, host=None, user=None, password=None, database=None, port=None):
        raw_h = host if host is not None else DB_CONFIG["host"]
        if isinstance(raw_h, str) and raw_h.strip().lower() == "localhost":
            raw_h = "127.0.0.1"
        self.host = raw_h
        self.user = user if user is not None else DB_CONFIG["user"]
        self.password = password if password is not None else DB_CONFIG["password"]
        self.database = database if database is not None else DB_CONFIG["database"]
        self.port = int(port if port is not None else DB_CONFIG["port"])
        self.connection = None
        self.modo = None
        self.ultimo_erro_mysql = None

    def _conectar_servidor_mysql(self, cfg, timeout=6):
        """
        Conecta a um servidor MySQL e garante que o banco de dados exista
        (`CREATE DATABASE IF NOT EXISTS`).
        """
        host = "127.0.0.1" if str(cfg["host"]).strip().lower() == "localhost" else cfg["host"]
        port = int(cfg["port"])
        user = cfg["user"]
        password = cfg["password"]
        database = cfg["database"]

        base_params = {
            "host": host,
            "user": user,
            "password": password,
            "port": port,
            "connection_timeout": timeout,
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": False,
            "use_pure": True,
        }

        try:
            conn = mysql.connector.connect(database=database, **base_params)
            return conn
        except Error as err:
            # 1049 = Unknown database -> cria o banco automaticamente no MySQL
            if getattr(err, "errno", None) == 1049:
                tmp_conn = mysql.connector.connect(**base_params)
                cursor = tmp_conn.cursor()
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{database}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                tmp_conn.commit()
                cursor.close()
                tmp_conn.close()
                return mysql.connector.connect(database=database, **base_params)
            raise

    def conectar(self):
        """Estabelece ou reutiliza a conexão ativa com o banco de dados MySQL."""
        if self.connection is not None:
            try:
                if self.connection.is_connected():
                    self.connection.ping(reconnect=True, attempts=2, delay=1)
                    return _ManagedMySQLConnection(self.connection)
            except Exception:
                try:
                    self.connection.close()
                except Exception:
                    pass
                self.connection = None

        candidatos = []
        if self.host and self.user is not None:
            candidatos.append(
                (
                    "mysql_principal",
                    {
                        "host": self.host,
                        "user": self.user,
                        "password": self.password,
                        "database": self.database,
                        "port": self.port,
                    },
                    6,
                )
            )

        # Fallback automático para o servidor MySQL local (127.0.0.1:3306)
        if (self.host, self.port) != (LOCAL_MYSQL_CONFIG["host"], LOCAL_MYSQL_CONFIG["port"]):
            candidatos.append(("mysql_local", LOCAL_MYSQL_CONFIG, 4))

        erros = []
        for modo_nome, cfg, timeout in candidatos:
            try:
                self.connection = self._conectar_servidor_mysql(cfg, timeout=timeout)
                self.modo = "mysql"
                self.ultimo_erro_mysql = None
                return _ManagedMySQLConnection(self.connection)
            except Exception as e:
                erros.append(f"{cfg['host']}:{cfg['port']} -> {e}")

        self.ultimo_erro_mysql = " | ".join(erros)
        raise RuntimeError(f"Não foi possível conectar ao servidor MySQL: {self.ultimo_erro_mysql}")

    def desconectar(self):
        """Encerra a conexão MySQL ativa."""
        if self.connection is not None:
            try:
                if self.connection.is_connected():
                    self.connection.close()
            except Exception:
                pass
            finally:
                self.connection = None

    def executar_query(self, query, params=None):
        """Executa comandos de modificação (INSERT, UPDATE, DELETE, CREATE) no MySQL."""
        conn = self.conectar()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor
        except Error as e:
            conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()

    def buscar_dados(self, query, params=None):
        """Executa consultas (SELECT) no MySQL e retorna lista de dicionários."""
        conn = self.conectar()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return [_normalizar_linha(r) for r in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()


# Instância global compartilhada
_db_global = Database()


def conectar():
    """Retorna uma conexão ativa com o banco de dados MySQL."""
    return _db_global.conectar()


def verificar_conexao():
    """
    Testa a conexão com o MySQL e retorna uma tupla (sucesso: bool, detalhes: str).
    """
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION(), DATABASE(), CURRENT_USER()")
            versao, banco_atual, usuario_atual = cursor.fetchone()
            cursor.close()
            host_ativo = _db_global.connection.server_host if _db_global.connection else _db_global.host
            porta_ativa = _db_global.connection.server_port if _db_global.connection else _db_global.port
            return (
                True,
                f"Conectado ao MySQL {versao} em {host_ativo}:{porta_ativa} "
                f"| Banco: '{banco_atual}' | Usuário: '{usuario_atual}'",
            )
    except Exception as e:
        return False, f"Falha na conexão com o MySQL: {e}"


def hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 seguro para armazenar senhas."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def _normalizar_linha(row: dict) -> dict:
    """Converte tipos Decimal e datetime do MySQL para tipos nativos (float / str)."""
    if not row:
        return None
    normalizado = {}
    for chave, valor in row.items():
        if isinstance(valor, Decimal):
            normalizado[chave] = float(valor)
        elif isinstance(valor, (datetime, date)):
            normalizado[chave] = valor.strftime("%Y-%m-%d %H:%M:%S")
        else:
            normalizado[chave] = valor
    return normalizado


def _criar_tabelas_mysql(cursor):
    """Cria todas as tabelas do sistema no MySQL caso ainda não existam."""
    # 1. Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            tipo ENUM('cliente', 'admin') DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 2. Tabela de Veículos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            marca VARCHAR(50) NOT NULL,
            modelo VARCHAR(50) NOT NULL,
            placa VARCHAR(10) UNIQUE NOT NULL,
            ano INT,
            tipo_conector VARCHAR(30) NOT NULL,
            capacidade_bateria_kwh DECIMAL(6, 2),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_veiculos_usuario FOREIGN KEY (usuario_id)
                REFERENCES usuarios (id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 3. Tabela de Estações de Recarga
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            endereco VARCHAR(255) NOT NULL,
            potencia_kw DECIMAL(6, 2) NOT NULL,
            tipo_conector VARCHAR(30) NOT NULL,
            preco_kwh DECIMAL(8, 2) NOT NULL,
            status ENUM('Disponível', 'Ocupado', 'Manutenção') DEFAULT 'Disponível',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 4. Tabela de Histórico de Recargas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recargas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            estacao_id INT NOT NULL,
            veiculo_id INT NULL,
            data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_fim TIMESTAMP NULL,
            energia_kwh DECIMAL(8, 2) DEFAULT 0.00,
            valor_total DECIMAL(10, 2) DEFAULT 0.00,
            status ENUM('Em andamento', 'Concluída', 'Cancelada') DEFAULT 'Em andamento',
            CONSTRAINT fk_recargas_usuario FOREIGN KEY (usuario_id)
                REFERENCES usuarios (id) ON DELETE CASCADE,
            CONSTRAINT fk_recargas_estacao FOREIGN KEY (estacao_id)
                REFERENCES estacoes (id) ON DELETE CASCADE,
            CONSTRAINT fk_recargas_veiculo FOREIGN KEY (veiculo_id)
                REFERENCES veiculos (id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 5. Tabela de Serviços e Manutenções
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(150) NOT NULL,
            descricao TEXT,
            preco DECIMAL(10, 2),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # Garante compatibilidade de colunas na tabela recargas (migração de horario_inicio -> data_inicio)
    cursor.execute("SHOW COLUMNS FROM recargas")
    colunas_recargas = {row["Field"] if isinstance(row, dict) else row[0] for row in cursor.fetchall()}
    if "horario_inicio" in colunas_recargas and "data_inicio" not in colunas_recargas:
        cursor.execute("ALTER TABLE recargas CHANGE COLUMN horario_inicio data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    if "horario_final" in colunas_recargas and "data_fim" not in colunas_recargas:
        cursor.execute("ALTER TABLE recargas CHANGE COLUMN horario_final data_fim TIMESTAMP NULL")


def _popular_dados_iniciais(conn, cursor):
    """Insere os dados iniciais (seed) no MySQL caso as tabelas estejam vazias."""
    # 1. Usuários iniciais
    cursor.execute("SELECT COUNT(*) as total FROM usuarios")
    row_user = cursor.fetchone()
    total_usuarios = row_user["total"] if isinstance(row_user, dict) else (row_user[0] if row_user else 0)

    if total_usuarios == 0:
        usuarios_iniciais = [
            (
                1,
                "Administrador EletroBel",
                "admin@eletrobel.com",
                "admin",
                "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
                "admin",
                "2026-10-16 22:51:54",
            ),
            (
                3,
                "arilson",
                "arilsonvalente@gmail.com",
                "arilsonvalente",
                "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",
                "cliente",
                "2026-10-16 23:23:22",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO usuarios (id, nome, email, usuario, senha, tipo, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nome = VALUES(nome),
                email = VALUES(email),
                tipo = VALUES(tipo)
            """,
            usuarios_iniciais,
        )

    # 2. Estações de recarga iniciais
    cursor.execute("SELECT COUNT(*) as total FROM estacoes")
    row_est = cursor.fetchone()
    total_estacoes = row_est["total"] if isinstance(row_est, dict) else (row_est[0] if row_est else 0)

    if total_estacoes == 0:
        estacoes_iniciais = [
            (5, "Estação EletroBel Doca", "Av. Visconde de Souza Franco (Doca), 500 - Belém, PA", 150.0, "CCS2 / Tipo 2", 1.95, "Disponível", "2026-10-16 23:40:26"),
            (6, "Estação Shopping Bosque Grão-Pará", "Av. Centenário, 1052 - Belém, PA", 60.0, "CCS2", 2.10, "Disponível", "2026-10-16 23:40:26"),
            (7, "Estação Metrópole Ananindeua", "Rodovia BR-316, Km 4 - Coqueiro, Ananindeua, PA", 120.0, "CCS2 / CHAdeMO", 1.90, "Disponível", "2026-10-16 23:40:26"),
            (8, "Estação Cidade Nova", "Av. Arterial 18, 400 - Cidade Nova, Ananindeua, PA", 22.0, "Tipo 2", 1.45, "Disponível", "2026-10-16 23:40:26"),
            (9, "Estação Aeroporto Internacional", "Val-de-Cans - Estacionamento VIP, Belém, PA", 100.0, "CCS2", 2.30, "Ocupado", "2026-10-16 23:40:26"),
            (10, "Estação BRT Augusto Montenegro", "Av. Augusto Montenegro, Km 8 - Parque Verde, Belém, PA", 90.0, "CCS2 / Tipo 2", 1.85, "Disponível", "2026-10-16 23:40:26"),
        ]
        cursor.executemany(
            """
            INSERT INTO estacoes (id, nome, endereco, potencia_kw, tipo_conector, preco_kwh, status, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nome = VALUES(nome),
                endereco = VALUES(endereco),
                potencia_kw = VALUES(potencia_kw),
                tipo_conector = VALUES(tipo_conector),
                preco_kwh = VALUES(preco_kwh),
                status = VALUES(status)
            """,
            estacoes_iniciais,
        )

    # 3. Veículos iniciais
    cursor.execute("SELECT COUNT(*) as total FROM veiculos")
    row_veic = cursor.fetchone()
    total_veiculos = row_veic["total"] if isinstance(row_veic, dict) else (row_veic[0] if row_veic else 0)

    if total_veiculos == 0:
        veiculos_iniciais = [
            (1, 3, "byd", "dolphin", "HFJKFKFSL", 2026, "Tipo", 38.00, "2026-10-20 21:41:04"),
            (2, 3, "gwm", "Haval", "BR22FG01", 2025, "Tipo", 50.00, "2026-10-21 22:48:05"),
        ]
        cursor.executemany(
            """
            INSERT INTO veiculos (id, usuario_id, marca, modelo, placa, ano, tipo_conector, capacidade_bateria_kwh, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                marca = VALUES(marca),
                modelo = VALUES(modelo),
                ano = VALUES(ano),
                tipo_conector = VALUES(tipo_conector),
                capacidade_bateria_kwh = VALUES(capacidade_bateria_kwh)
            """,
            veiculos_iniciais,
        )

    # 4. Serviços iniciais
    cursor.execute("SELECT COUNT(*) as total FROM servicos")
    row_serv = cursor.fetchone()
    total_servicos = row_serv["total"] if isinstance(row_serv, dict) else (row_serv[0] if row_serv else 0)

    if total_servicos == 0:
        servicos_iniciais = [
            (1, "Instalação de Wallbox Residencial", "Instalação completa e homologada de carregador até 22kW.", 1200.00, "2026-10-16 22:51:54"),
            (2, "Diagnóstico de Bateria de Tração", "Varredura computadorizada e verificação de degradação das células.", 350.00, "2026-10-16 22:51:54"),
            (3, "Manutenção Preventiva de Conectores", "Inspeção e limpeza técnica dos conectores de carga rápida.", 180.00, "2026-10-16 23:40:26"),
        ]
        cursor.executemany(
            """
            INSERT INTO servicos (id, titulo, descricao, preco, criado_em)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                titulo = VALUES(titulo),
                descricao = VALUES(descricao),
                preco = VALUES(preco)
            """,
            servicos_iniciais,
        )

    conn.commit()


def sincronizar_servidores_mysql():
    """
    Garante que tanto o MySQL Online (Aiven Cloud) quanto o MySQL Local (127.0.0.1:3306),
    quando acessíveis, tenham o banco `eletrobel_posto` criado e todos os registros sincronizados.
    """
    for cfg in (DB_CONFIG, LOCAL_MYSQL_CONFIG):
        try:
            db_temp = Database(
                host=cfg["host"],
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                port=cfg["port"],
            )
            conn = db_temp._conectar_servidor_mysql(cfg, timeout=5)
            cur = conn.cursor(dictionary=True)
            _criar_tabelas_mysql(cur)
            _popular_dados_iniciais(conn, cur)
            cur.close()
            conn.close()
        except Exception:
            pass


def inicializar_banco(exportar_sql: bool = False):
    """
    Verifica se o banco de dados MySQL (`eletrobel_posto`) e todas as tabelas existem;
    caso não existam, cria automaticamente e popula os dados iniciais.
    """
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        _criar_tabelas_mysql(cursor)
        _popular_dados_iniciais(conn, cursor)
        cursor.close()

    if exportar_sql:
        atualizar_arquivo_sql()


def _sql_val(v):
    """Formata um valor Python para literal SQL seguro."""
    if v is None:
        return "NULL"
    if isinstance(v, (int, float, Decimal)):
        return str(v)
    texto = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{texto}'"


def atualizar_arquivo_sql():
    """
    Exporta a estrutura e os dados atuais do banco MySQL para os arquivos SQL do projeto:
    - eletrobel_posto.sql
    - banco_de_dados.sql
    - banco_de_dados.txt
    - Banco de Dados/Banco de Dados Eletrobel_Posto.sql
    """
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)

            linhas = [
                "-- =====================================================================",
                "-- SCRIPT SQL MYSQL ATUALIZADO COM O BANCO DE DADOS - ELETROBEL POSTO",
                "-- Banco de Dados: MySQL (eletrobel_posto)",
                "-- =====================================================================",
                "",
                "CREATE DATABASE IF NOT EXISTS eletrobel_posto",
                "    CHARACTER SET utf8mb4",
                "    COLLATE utf8mb4_unicode_ci;",
                "",
                "USE eletrobel_posto;",
                "",
                "-- 1. Tabela de Usuários",
                "CREATE TABLE IF NOT EXISTS eletrobel_posto.usuarios (",
                "    id INT AUTO_INCREMENT PRIMARY KEY,",
                "    nome VARCHAR(150) NOT NULL,",
                "    email VARCHAR(255) UNIQUE NOT NULL,",
                "    usuario VARCHAR(50) UNIQUE NOT NULL,",
                "    senha VARCHAR(255) NOT NULL, -- Hash SHA-256",
                "    tipo ENUM('cliente', 'admin') DEFAULT 'cliente',",
                "    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
                "",
                "-- 2. Tabela de Veículos",
                "CREATE TABLE IF NOT EXISTS eletrobel_posto.veiculos (",
                "    id INT AUTO_INCREMENT PRIMARY KEY,",
                "    usuario_id INT NOT NULL,",
                "    marca VARCHAR(50) NOT NULL,",
                "    modelo VARCHAR(50) NOT NULL,",
                "    placa VARCHAR(10) UNIQUE NOT NULL,",
                "    ano INT,",
                "    tipo_conector VARCHAR(30) NOT NULL, -- Ex: 'CCS2', 'Tipo 2', 'CHAdeMO'",
                "    capacidade_bateria_kwh DECIMAL(6, 2),",
                "    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
                "    CONSTRAINT fk_veiculos_usuario FOREIGN KEY (usuario_id)",
                "        REFERENCES eletrobel_posto.usuarios (id) ON DELETE CASCADE",
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
                "",
                "-- 3. Tabela de Estações de Recarga",
                "CREATE TABLE IF NOT EXISTS eletrobel_posto.estacoes (",
                "    id INT AUTO_INCREMENT PRIMARY KEY,",
                "    nome VARCHAR(100) NOT NULL,",
                "    endereco VARCHAR(255) NOT NULL,",
                "    potencia_kw DECIMAL(6, 2) NOT NULL,",
                "    tipo_conector VARCHAR(30) NOT NULL,",
                "    preco_kwh DECIMAL(8, 2) NOT NULL,",
                "    status ENUM('Disponível', 'Ocupado', 'Manutenção') DEFAULT 'Disponível',",
                "    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
                "",
                "-- 4. Tabela de Histórico de Recargas",
                "CREATE TABLE IF NOT EXISTS eletrobel_posto.recargas (",
                "    id INT AUTO_INCREMENT PRIMARY KEY,",
                "    usuario_id INT NOT NULL,",
                "    estacao_id INT NOT NULL,",
                "    veiculo_id INT NULL,",
                "    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
                "    data_fim TIMESTAMP NULL,",
                "    energia_kwh DECIMAL(8, 2) DEFAULT 0.00,",
                "    valor_total DECIMAL(10, 2) DEFAULT 0.00,",
                "    status ENUM('Em andamento', 'Concluída', 'Cancelada') DEFAULT 'Em andamento',",
                "    CONSTRAINT fk_recargas_usuario FOREIGN KEY (usuario_id)",
                "        REFERENCES eletrobel_posto.usuarios (id) ON DELETE CASCADE,",
                "    CONSTRAINT fk_recargas_estacao FOREIGN KEY (estacao_id)",
                "        REFERENCES eletrobel_posto.estacoes (id) ON DELETE CASCADE,",
                "    CONSTRAINT fk_recargas_veiculo FOREIGN KEY (veiculo_id)",
                "        REFERENCES eletrobel_posto.veiculos (id) ON DELETE SET NULL",
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
                "",
                "-- 5. Tabela de Serviços e Manutenções",
                "CREATE TABLE IF NOT EXISTS eletrobel_posto.servicos (",
                "    id INT AUTO_INCREMENT PRIMARY KEY,",
                "    titulo VARCHAR(150) NOT NULL,",
                "    descricao TEXT,",
                "    preco DECIMAL(10, 2),",
                "    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
                "",
                "-- =====================================================================",
                "-- DADOS DO BANCO DE DADOS MYSQL",
                "-- =====================================================================",
            ]

            tabelas = [
                ("usuarios", ["id", "nome", "email", "usuario", "senha", "tipo", "criado_em"]),
                ("estacoes", ["id", "nome", "endereco", "potencia_kw", "tipo_conector", "preco_kwh", "status", "criado_em"]),
                ("veiculos", ["id", "usuario_id", "marca", "modelo", "placa", "ano", "tipo_conector", "capacidade_bateria_kwh", "criado_em"]),
                ("recargas", ["id", "usuario_id", "estacao_id", "veiculo_id", "data_inicio", "data_fim", "energia_kwh", "valor_total", "status"]),
                ("servicos", ["id", "titulo", "descricao", "preco", "criado_em"]),
            ]

            for nome_tabela, colunas in tabelas:
                cursor.execute(f"SELECT {', '.join(colunas)} FROM {nome_tabela} ORDER BY id ASC")
                registros = cursor.fetchall()
                if not registros:
                    continue

                linhas.append("")
                linhas.append(f"-- Tabela: {nome_tabela}")
                cols_str = ", ".join(colunas)
                valores_linhas = []
                for reg in registros:
                    vals = ", ".join(_sql_val(reg[c]) for c in colunas)
                    valores_linhas.append(f"({vals})")

                updates = ", ".join(f"{c} = VALUES({c})" for c in colunas if c != "id")
                linhas.append(
                    f"INSERT INTO eletrobel_posto.{nome_tabela} ({cols_str}) VALUES\n"
                    + ",\n".join(valores_linhas)
                    + f"\nON DUPLICATE KEY UPDATE {updates};"
                )

            conteudo_sql = "\n".join(linhas) + "\n"
            for caminho in (SQL_SCRIPT_PATH, BANCO_SQL_PATH, BANCO_TXT_PATH):
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(conteudo_sql)

            if os.path.exists(os.path.dirname(EXTERNAL_SQL_SCRIPT_PATH)):
                with open(EXTERNAL_SQL_SCRIPT_PATH, "w", encoding="utf-8") as f:
                    f.write(conteudo_sql)

            cursor.close()
    except Exception as e:
        print(f"[AVISO] Erro ao exportar arquivo SQL: {e}")


# =====================================================================
# FUNÇÕES DE USUÁRIOS
# =====================================================================

def cadastrar_usuario(nome: str, email: str, usuario: str, senha: str, tipo: str = "cliente"):
    """
    Cadastra um novo usuário no banco de dados MySQL.
    Retorna uma tupla (sucesso: bool, mensagem: str).
    """
    nome = nome.strip()
    email = email.strip().lower()
    usuario = usuario.strip().lower()
    senha = senha.strip()

    if not nome or not email or not usuario or not senha:
        return False, "Todos os campos são obrigatórios!"

    if len(senha) < 3:
        return False, "A senha deve conter no mínimo 3 caracteres!"

    senha_cripto = hash_senha(senha)

    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, usuario, senha, tipo)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nome, email, usuario, senha_cripto, tipo),
            )
            conn.commit()
            cursor.close()
        atualizar_arquivo_sql()
        return True, f"Usuário '{usuario}' cadastrado com sucesso!"
    except IntegrityError as e:
        erro_str = str(e).lower()
        if "email" in erro_str:
            return False, "Este e-mail já está cadastrado!"
        elif "usuario" in erro_str:
            return False, "Este nome de usuário já está em uso!"
        return False, "Usuário ou e-mail já existente no sistema."
    except Exception as e:
        return False, f"Erro ao cadastrar usuário: {e}"


def autenticar_usuario(usuario: str, senha: str):
    """
    Verifica as credenciais do usuário no MySQL.
    Retorna os dados do usuário (dict) em caso de sucesso, ou None se inválido.
    """
    usuario = usuario.strip().lower()
    senha_cripto = hash_senha(senha.strip())

    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nome, email, usuario, tipo, criado_em
            FROM usuarios
            WHERE usuario = %s AND senha = %s
            """,
            (usuario, senha_cripto),
        )
        row = cursor.fetchone()
        cursor.close()
        if row:
            return _normalizar_linha(row)
        return None


def listar_usuarios():
    """Retorna a lista de todos os usuários cadastrados no MySQL."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, usuario, tipo, criado_em FROM usuarios ORDER BY id DESC")
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


def obter_usuario_por_id(usuario_id: int):
    """Retorna os dados cadastrais atualizados de um usuário pelo ID no MySQL."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome, email, usuario, tipo, criado_em FROM usuarios WHERE id = %s",
            (usuario_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        return _normalizar_linha(row) if row else None


def obter_resumo_usuario(usuario_id: int):
    """Retorna estatísticas do usuário no MySQL: total de recargas, kWh consumidos, valor investido e qtd de veículos."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_recargas,
                COALESCE(SUM(energia_kwh), 0.0) as total_kwh,
                COALESCE(SUM(valor_total), 0.0) as total_valor
            FROM recargas
            WHERE usuario_id = %s
            """,
            (usuario_id,),
        )
        row_rec = cursor.fetchone()
        res = {
            "total_recargas": int(row_rec["total_recargas"]) if row_rec else 0,
            "total_kwh": float(row_rec["total_kwh"]) if row_rec else 0.0,
            "total_valor": float(row_rec["total_valor"]) if row_rec else 0.0,
        }

        cursor.execute("SELECT COUNT(*) as total_veiculos FROM veiculos WHERE usuario_id = %s", (usuario_id,))
        row_veic = cursor.fetchone()
        res["total_veiculos"] = int(row_veic["total_veiculos"]) if row_veic else 0
        cursor.close()

        return res


# =====================================================================
# FUNÇÕES DE ESTAÇÕES
# =====================================================================

def listar_estacoes():
    """Retorna todas as estações de recarga cadastradas no MySQL."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estacoes ORDER BY id ASC")
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


def cadastrar_estacao(nome: str, endereco: str, potencia_kw: float, tipo_conector: str, preco_kwh: float, status: str = "Disponível"):
    """Adiciona uma nova estação de recarga no MySQL."""
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO estacoes (nome, endereco, potencia_kw, tipo_conector, preco_kwh, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nome, endereco, potencia_kw, tipo_conector, preco_kwh, status),
            )
            conn.commit()
            cursor.close()
        atualizar_arquivo_sql()
        return True, "Estação cadastrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar estação: {e}"


def buscar_estacoes(cidade: str = None, apenas_rapida: bool = False):
    """
    Retorna estações do MySQL filtradas por cidade (Belém, Ananindeua, Região Metropolitana)
    e opcionalmente apenas com Carga Rápida (DC >= 50kW).
    """
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM estacoes WHERE 1=1"
        params = []

        if cidade:
            cidade_lower = cidade.lower()
            if "belém" in cidade_lower and "ananindeua" not in cidade_lower:
                query += " AND (endereco LIKE %s OR nome LIKE %s)"
                params.extend(["%Belém%", "%Belém%"])
            elif "ananindeua" in cidade_lower and "belém" not in cidade_lower:
                query += " AND (endereco LIKE %s OR nome LIKE %s)"
                params.extend(["%Ananindeua%", "%Ananindeua%"])

        if apenas_rapida:
            query += " AND potencia_kw >= 50.0"

        query += " ORDER BY status ASC, potencia_kw DESC"
        cursor.execute(query, tuple(params))
        resultados = [_normalizar_linha(row) for row in cursor.fetchall()]

        if not resultados and cidade:
            fallback_query = "SELECT * FROM estacoes"
            if apenas_rapida:
                fallback_query += " WHERE potencia_kw >= 50.0"
            fallback_query += " ORDER BY status ASC, potencia_kw DESC"
            cursor.execute(fallback_query)
            resultados = [_normalizar_linha(row) for row in cursor.fetchall()]

        cursor.close()
        return resultados


# =====================================================================
# FUNÇÕES DE VEÍCULOS
# =====================================================================

def cadastrar_veiculo(usuario_id: int, marca: str, modelo: str, placa: str, ano: int, tipo_conector: str, capacidade_bateria_kwh: float):
    """Cadastra um novo veículo vinculado a um usuário no MySQL."""
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO veiculos (usuario_id, marca, modelo, placa, ano, tipo_conector, capacidade_bateria_kwh)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (usuario_id, marca, modelo, placa.upper().strip(), ano, tipo_conector, capacidade_bateria_kwh),
            )
            conn.commit()
            cursor.close()
        atualizar_arquivo_sql()
        return True, "Veículo cadastrado com sucesso!"
    except IntegrityError:
        return False, "Já existe um veículo cadastrado com esta placa!"
    except Exception as e:
        return False, f"Erro ao cadastrar veículo: {e}"


def listar_veiculos(usuario_id: int = None):
    """Lista os veículos de um usuário específico ou todos os veículos no MySQL."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        if usuario_id:
            cursor.execute("SELECT * FROM veiculos WHERE usuario_id = %s ORDER BY id DESC", (usuario_id,))
        else:
            cursor.execute(
                """
                SELECT v.*, u.nome as proprietario
                FROM veiculos v
                JOIN usuarios u ON v.usuario_id = u.id
                ORDER BY v.id DESC
                """
            )
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


# =====================================================================
# FUNÇÕES DE RECARGAS
# =====================================================================

def registrar_recarga(usuario_id: int, estacao_id: int, veiculo_id: int, energia_kwh: float, valor_total: float, status: str = "Concluída"):
    """Registra uma sessão de recarga no MySQL."""
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO recargas (usuario_id, estacao_id, veiculo_id, energia_kwh, valor_total, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (usuario_id, estacao_id, veiculo_id, energia_kwh, valor_total, status),
            )
            conn.commit()
            cursor.close()
        atualizar_arquivo_sql()
        return True, "Recarga registrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar recarga: {e}"


def listar_recargas(usuario_id: int = None):
    """Lista as recargas registradas no MySQL."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        if usuario_id:
            cursor.execute(
                """
                SELECT r.*, e.nome as estacao_nome, v.modelo as veiculo_modelo
                FROM recargas r
                JOIN estacoes e ON r.estacao_id = e.id
                LEFT JOIN veiculos v ON r.veiculo_id = v.id
                WHERE r.usuario_id = %s
                ORDER BY r.id DESC
                """,
                (usuario_id,),
            )
        else:
            cursor.execute(
                """
                SELECT r.*, u.nome as usuario_nome, e.nome as estacao_nome, v.modelo as veiculo_modelo
                FROM recargas r
                JOIN usuarios u ON r.usuario_id = u.id
                JOIN estacoes e ON r.estacao_id = e.id
                LEFT JOIN veiculos v ON r.veiculo_id = v.id
                ORDER BY r.id DESC
                """
            )
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


# =====================================================================
# FUNÇÕES DE SERVIÇOS
# =====================================================================

def listar_servicos():
    """Lista todos os serviços e manutenções cadastrados no MySQL."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servicos ORDER BY id ASC")
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


if __name__ == "__main__":
    print("Verificando e sincronizando servidores MySQL (Online e Local)...")
    sincronizar_servidores_mysql()
    ok, info = verificar_conexao()
    print(f"[{'OK' if ok else 'ERRO'}] {info}")

    inicializar_banco(exportar_sql=True)
    print(f"[OK] Scripts SQL MySQL sincronizados em:\n  - {SQL_SCRIPT_PATH}\n  - {BANCO_SQL_PATH}\n  - {EXTERNAL_SQL_SCRIPT_PATH}")

    with conectar() as conn:
        cursor = conn.cursor()
        for tabela in ["usuarios", "veiculos", "estacoes", "recargas", "servicos"]:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            qtd = cursor.fetchone()[0]
            print(f"- Tabela MySQL '{tabela}': {qtd} registro(s)")
        cursor.close()
    _db_global.desconectar()
