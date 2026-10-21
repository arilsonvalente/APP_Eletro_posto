import os
from dotenv import load_dotenv
import time
import hashlib
from decimal import Decimal
import mysql.connector
from mysql.connector import Error, IntegrityError

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

# Configurações da conexão online com o banco de dados MySQL (Aiven Cloud)
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT"))
}

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SQL_SCRIPT_PATH = os.path.join(BASE_DIR, "eletrobel_posto.sql")
# EXTERNAL_SQL_SCRIPT_PATH = os.path.abspath(
#     os.path.join(BASE_DIR, "..", "..", "Banco de Dados", "Banco de Dados Eletrobel_Posto.sql")
# )


# =====================================================================
# CLASSE DE CONEXÃO UNIFICADA (ANTIGO conecta_database.py)
# =====================================================================

class _ConexaoPersistenteContext:
    """Context manager que reutiliza a conexão MySQL ativa sem fechá-la a cada consulta."""

    def __init__(self, db_instance):
        self.db_instance = db_instance
        self.conn = None

    def __enter__(self):
        self.conn = self.db_instance.obter_conexao()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn and self.conn.is_connected():
            try:
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Error:
                pass
        return False


class Database:
    """Gerencia a conexão online persistente com o banco de dados MySQL do EletroBel Posto."""

    def __init__(
        self,
        host=None,
        user=None,
        password=None,
        database=None,
        port=None,
    ):
        raw_host = host if host is not None else DB_CONFIG["host"]
        self.host = "127.0.0.1" if raw_host == "localhost" else raw_host
        self.user = user if user is not None else DB_CONFIG["user"]
        self.password = password if password is not None else DB_CONFIG["password"]
        self.database = database if database is not None else DB_CONFIG["database"]
        self.port = int(port if port is not None else DB_CONFIG["port"])
        self.conexao = None

    def criar_banco_se_nao_existir(self):
        """Garante que o banco de dados exista no servidor MySQL antes de conectar."""
        try:
            conn_temp = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                use_pure=True,
                connection_timeout=15,
            )
            cursor = conn_temp.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            conn_temp.commit()
            cursor.close()
            conn_temp.close()
            return True
        except Error as e:
            print(f"[ERRO] Erro ao verificar/criar base de dados MySQL: {e}")
            return False

    def conectar(self):
        """Estabelece e retorna a conexão ativa com o banco de dados MySQL com reconexão automática."""
        ultimo_erro = None
        for tentativa in range(1, 4):
            try:
                if self.conexao is not None and self.conexao.is_connected():
                    try:
                        self.conexao.ping(reconnect=True, attempts=2, delay=1)
                        return self.conexao
                    except Error:
                        self.conexao = None

                self.conexao = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    charset="utf8mb4",
                    use_unicode=True,
                    autocommit=False,
                    use_pure=True,
                    connection_timeout=15,
                )
                if self.conexao.is_connected():
                    return self.conexao
            except Error as e:
                ultimo_erro = e
                # Erro 1049 = Unknown database: cria automaticamente o banco no MySQL
                if getattr(e, "errno", None) == 1049:
                    if self.criar_banco_se_nao_existir():
                        continue
                if tentativa < 3:
                    time.sleep(0.8 * tentativa)

        print("[ERRO] Erro Critico: Nao foi possivel conectar ao banco de dados MySQL online.")
        print(f"Detalhes do erro para debug: {ultimo_erro}")
        raise ultimo_erro

    def obter_conexao(self):
        """Retorna a conexão persistente ativa, reconectando se necessário."""
        return self.conectar()

    def desconectar(self):
        """Encerra a conexão com o banco de forma segura."""
        if self.conexao and self.conexao.is_connected():
            try:
                self.conexao.close()
            except Error:
                pass
            self.conexao = None


# Instância global persistente para evitar múltiplas aberturas de socket TLS seguidas
_db_global = Database()


def conectar():
    """Retorna um gerenciador de contexto com a conexão MySQL online reutilizável."""
    return _ConexaoPersistenteContext(_db_global)


def verificar_conexao():
    """Testa a conexão com o servidor MySQL e retorna (sucesso: bool, mensagem: str)."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE(), VERSION()")
            db_atual, versao = cursor.fetchone()
            cursor.close()
            msg = f"Conectado ao MySQL {versao} | Banco: {db_atual} ({_db_global.host}:{_db_global.port})"
            return True, msg
    except Exception as e:
        return False, f"Falha na conexão com o MySQL: {e}"


def _normalizar_linha(row: dict) -> dict:
    """Converte objetos Decimal do MySQL para float mantendo compatibilidade com a interface."""
    if not row:
        return row
    normalizado = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            normalizado[k] = float(v)
        else:
            normalizado[k] = v
    return normalizado


def hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 da senha para armazenamento seguro."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def inicializar_banco(exportar_sql: bool = False):
    """Cria todas as tabelas necessárias no MySQL online e popula dados iniciais caso esteja vazio."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)

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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
                CONSTRAINT fk_veiculos_usuario
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
                CONSTRAINT fk_recargas_usuario
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_recargas_estacao
                    FOREIGN KEY (estacao_id) REFERENCES estacoes (id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_recargas_veiculo
                    FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
                    ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 5. Tabela de Serviços e Manutenções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(150) NOT NULL,
                descricao TEXT,
                preco DECIMAL(10, 2),
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        conn.commit()

        # Popula dados iniciais se necessário
        _popular_dados_iniciais(cursor, conn)
        cursor.close()

    print(f"[OK] Conectado ao banco de dados MySQL online ({_db_global.host}:{_db_global.port}/{_db_global.database})")
    if exportar_sql:
        atualizar_arquivo_sql()


def _popular_dados_iniciais(cursor, conn):
    """Insere dados de exemplo e usuários iniciais se a tabela estiver vazia."""

    # 1. Usuário Administrador padrão (admin / 123)
    cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", ("admin",))
    if not cursor.fetchone():
        senha_admin = hash_senha("123")
        cursor.execute("""
            INSERT INTO usuarios (id, nome, email, usuario, senha, tipo, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (1, "Administrador EletroBel", "admin@eletrobel.com", "admin", senha_admin, "admin", "2026-10-16 22:51:54"))

    # Usuário local existente (arilsonvalente)
    cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", ("arilsonvalente",))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT IGNORE INTO usuarios (id, nome, email, usuario, senha, tipo, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            3,
            "arilson",
            "arilsonvalente@gmail.com",
            "arilsonvalente",
            "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",
            "cliente",
            "2026-10-16 23:23:22",
        ))

    # 2. Estações de Recarga iniciais (Belém, Ananindeua e Região Metropolitana)
    cursor.execute("SELECT COUNT(*) as total FROM estacoes")
    row_est = cursor.fetchone()
    total_estacoes = row_est["total"] if row_est else 0

    if total_estacoes == 0:
        estacoes_iniciais = [
            (5, "Estação EletroBel Doca", "Av. Visconde de Souza Franco (Doca), 500 - Belém, PA", 150.0, "CCS2 / Tipo 2", 1.95, "Disponível", "2026-10-16 23:40:26"),
            (6, "Estação Shopping Bosque Grão-Pará", "Av. Centenário, 1052 - Belém, PA", 60.0, "CCS2", 2.10, "Disponível", "2026-10-16 23:40:26"),
            (7, "Estação Metrópole Ananindeua", "Rodovia BR-316, Km 4 - Coqueiro, Ananindeua, PA", 120.0, "CCS2 / CHAdeMO", 1.90, "Disponível", "2026-10-16 23:40:26"),
            (8, "Estação Cidade Nova", "Av. Arterial 18, 400 - Cidade Nova, Ananindeua, PA", 22.0, "Tipo 2", 1.45, "Disponível", "2026-10-16 23:40:26"),
            (9, "Estação Aeroporto Internacional", "Val-de-Cans - Estacionamento VIP, Belém, PA", 100.0, "CCS2", 2.30, "Ocupado", "2026-10-16 23:40:26"),
            (10, "Estação BRT Augusto Montenegro", "Av. Augusto Montenegro, Km 8 - Parque Verde, Belém, PA", 90.0, "CCS2 / Tipo 2", 1.85, "Disponível", "2026-10-16 23:40:26"),
        ]
        cursor.executemany("""
            INSERT INTO estacoes (id, nome, endereco, potencia_kw, tipo_conector, preco_kwh, status, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, estacoes_iniciais)

    # 3. Serviços iniciais
    cursor.execute("SELECT COUNT(*) as total FROM servicos")
    row_serv = cursor.fetchone()
    total_servicos = row_serv["total"] if row_serv else 0

    if total_servicos == 0:
        servicos_iniciais = [
            (1, "Instalação de Wallbox Residencial", "Instalação completa e homologada de carregador até 22kW.", 1200.00, "2026-10-16 22:51:54"),
            (2, "Diagnóstico de Bateria de Tração", "Varredura computadorizada e verificação de degradação das células.", 350.00, "2026-10-16 22:51:54"),
            (3, "Manutenção Preventiva de Conectores", "Inspeção e limpeza técnica dos conectores de carga rápida.", 180.00, "2026-10-16 23:40:26"),
        ]
        cursor.executemany("""
            INSERT INTO servicos (id, titulo, descricao, preco, criado_em)
            VALUES (%s, %s, %s, %s, %s)
        """, servicos_iniciais)

    conn.commit()


def _sql_val(v):
    """Formata um valor Python para literal SQL seguro."""
    if v is None:
        return "NULL"
    if isinstance(v, (int, float, Decimal)):
        return str(v)
    texto = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{texto}'"


def atualizar_arquivo_sql():
    """Exporta a estrutura e os dados atuais do banco para o arquivo eletrobel_posto.sql."""
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)

            linhas = [
                "-- =====================================================================",
                "-- SCRIPT SQL ATUALIZADO COM O BANCO DE DADOS - ELETROBEL POSTO",
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
                "-- DADOS DO BANCO DE DADOS",
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
            with open(SQL_SCRIPT_PATH, "w", encoding="utf-8") as f:
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
            cursor.execute("""
                INSERT INTO usuarios (nome, email, usuario, senha, tipo)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, email, usuario, senha_cripto, tipo))
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
        cursor.execute("""
            SELECT id, nome, email, usuario, tipo, criado_em
            FROM usuarios
            WHERE usuario = %s AND senha = %s
        """, (usuario, senha_cripto))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return _normalizar_linha(row)
        return None


def listar_usuarios():
    """Retorna a lista de todos os usuários cadastrados."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, usuario, tipo, criado_em FROM usuarios ORDER BY id DESC")
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


def obter_usuario_por_id(usuario_id: int):
    """Retorna os dados cadastrais atualizados de um usuário pelo ID."""
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
    """Retorna estatísticas do usuário: total de recargas, kWh consumidos, valor investido e qtd de veículos."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_recargas,
                COALESCE(SUM(energia_kwh), 0.0) as total_kwh,
                COALESCE(SUM(valor_total), 0.0) as total_valor
            FROM recargas
            WHERE usuario_id = %s
        """, (usuario_id,))
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
    """Retorna todas as estações de recarga cadastradas."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estacoes ORDER BY id ASC")
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


def cadastrar_estacao(nome: str, endereco: str, potencia_kw: float, tipo_conector: str, preco_kwh: float, status: str = "Disponível"):
    """Adiciona uma nova estação de recarga."""
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO estacoes (nome, endereco, potencia_kw, tipo_conector, preco_kwh, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, endereco, potencia_kw, tipo_conector, preco_kwh, status))
            conn.commit()
            cursor.close()
        atualizar_arquivo_sql()
        return True, "Estação cadastrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar estação: {e}"


def buscar_estacoes(cidade: str = None, apenas_rapida: bool = False):
    """
    Retorna estações filtradas por cidade (Belém, Ananindeua, Região Metropolitana)
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
    """Cadastra um novo veículo vinculado a um usuário."""
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO veiculos (usuario_id, marca, modelo, placa, ano, tipo_conector, capacidade_bateria_kwh)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (usuario_id, marca, modelo, placa.upper().strip(), ano, tipo_conector, capacidade_bateria_kwh))
            conn.commit()
            cursor.close()
        atualizar_arquivo_sql()
        return True, "Veículo cadastrado com sucesso!"
    except IntegrityError:
        return False, "Já existe um veículo cadastrado com esta placa!"
    except Exception as e:
        return False, f"Erro ao cadastrar veículo: {e}"


def listar_veiculos(usuario_id: int = None):
    """Lista os veículos de um usuário específico ou todos os veículos."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        if usuario_id:
            cursor.execute("SELECT * FROM veiculos WHERE usuario_id = %s ORDER BY id DESC", (usuario_id,))
        else:
            cursor.execute("""
                SELECT v.*, u.nome as proprietario
                FROM veiculos v
                JOIN usuarios u ON v.usuario_id = u.id
                ORDER BY v.id DESC
            """)
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


# =====================================================================
# FUNÇÕES DE RECARGAS
# =====================================================================

def registrar_recarga(usuario_id: int, estacao_id: int, veiculo_id: int, energia_kwh: float, valor_total: float, status: str = "Concluída"):
    """Registra uma sessão de recarga."""
    try:
        with conectar() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO recargas (usuario_id, estacao_id, veiculo_id, energia_kwh, valor_total, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (usuario_id, estacao_id, veiculo_id, energia_kwh, valor_total, status))
            conn.commit()
            cursor.close()
        atualizar_arquivo_sql()
        return True, "Recarga registrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar recarga: {e}"


def listar_recargas(usuario_id: int = None):
    """Lista as recargas registradas."""
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        if usuario_id:
            cursor.execute("""
                SELECT r.*, e.nome as estacao_nome, v.modelo as veiculo_modelo
                FROM recargas r
                JOIN estacoes e ON r.estacao_id = e.id
                LEFT JOIN veiculos v ON r.veiculo_id = v.id
                WHERE r.usuario_id = %s
                ORDER BY r.id DESC
            """, (usuario_id,))
        else:
            cursor.execute("""
                SELECT r.*, u.nome as usuario_nome, e.nome as estacao_nome, v.modelo as veiculo_modelo
                FROM recargas r
                JOIN usuarios u ON r.usuario_id = u.id
                JOIN estacoes e ON r.estacao_id = e.id
                LEFT JOIN veiculos v ON r.veiculo_id = v.id
                ORDER BY r.id DESC
            """)
        rows = [_normalizar_linha(row) for row in cursor.fetchall()]
        cursor.close()
        return rows


if __name__ == "__main__":
    print("Verificando conexao com o banco de dados MySQL online...")
    ok, info = verificar_conexao()
    print(f"[{'OK' if ok else 'ERRO'}] {info}")

    inicializar_banco(exportar_sql=True)
    print(f"[OK] Script SQL sincronizado em: {SQL_SCRIPT_PATH}")

    with conectar() as conn:
        cursor = conn.cursor()
        for tabela in ["usuarios", "veiculos", "estacoes", "recargas", "servicos"]:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            qtd = cursor.fetchone()[0]
            print(f"- Tabela '{tabela}': {qtd} registro(s)")
        cursor.close()
    _db_global.desconectar()
