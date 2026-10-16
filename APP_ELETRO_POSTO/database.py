import sqlite3
import os
import hashlib

# Caminho do arquivo do banco de dados na mesma pasta do projeto
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eletrobel.db")


def conectar():
    """Retorna uma conexão com o banco de dados SQLite com suporte a Foreign Keys."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 da senha para armazenamento seguro."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def inicializar_banco():
    """Cria todas as tabelas necessárias e popula dados iniciais essenciais."""
    with conectar() as conn:
        cursor = conn.cursor()

        # 1. Tabela de Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                tipo TEXT DEFAULT 'cliente',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Tabela de Veículos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                placa TEXT UNIQUE NOT NULL,
                ano INTEGER,
                tipo_conector TEXT NOT NULL,
                capacidade_bateria_kwh REAL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)

        # 3. Tabela de Estações de Recarga
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                endereco TEXT NOT NULL,
                potencia_kw REAL NOT NULL,
                tipo_conector TEXT NOT NULL,
                preco_kwh REAL NOT NULL,
                status TEXT DEFAULT 'Disponível',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Tabela de Histórico de Recargas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recargas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                estacao_id INTEGER NOT NULL,
                veiculo_id INTEGER,
                data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_fim TIMESTAMP,
                energia_kwh REAL DEFAULT 0.0,
                valor_total REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Em andamento',
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                FOREIGN KEY (estacao_id) REFERENCES estacoes (id) ON DELETE CASCADE,
                FOREIGN KEY (veiculo_id) REFERENCES veiculos (id) ON DELETE SET NULL
            )
        """)

        # 5. Tabela de Serviços e Manutenções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                preco REAL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Inserção de dados iniciais (Seed)
        _popular_dados_iniciais(cursor, conn)


def _popular_dados_iniciais(cursor, conn):
    """Insere dados de exemplo e usuário administrador padrão se a tabela estiver vazia."""
    
    # 1. Usuário Administrador padrão (admin / 123)
    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        senha_admin = hash_senha("123")
        cursor.execute("""
            INSERT INTO usuarios (nome, email, usuario, senha, tipo)
            VALUES (?, ?, ?, ?, ?)
        """, ("Administrador EletroBel", "admin@eletrobel.com", "admin", senha_admin, "admin"))

    # 2. Estações de Recarga iniciais
    cursor.execute("SELECT COUNT(*) as total FROM estacoes")
    if cursor.fetchone()[0] == 0:
        estacoes_iniciais = [
            ("Estação Central EletroBel", "Av. Principal, 1000 - Centro", 50.0, "CCS2 / Tipo 2", 1.85, "Disponível"),
            ("Estação Shopping Norte", "Rodovia BR-101, Km 45", 150.0, "CCS2 / CHAdeMO", 2.10, "Disponível"),
            ("Estação Polo Tecnológico", "Rua da Inovação, 250", 22.0, "Tipo 2", 1.50, "Disponível"),
            ("Estação Aeroporto Express", "Terminal 2 - Estacionamento VIP", 100.0, "CCS2", 2.30, "Ocupado"),
        ]
        cursor.executemany("""
            INSERT INTO estacoes (nome, endereco, potencia_kw, tipo_conector, preco_kwh, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, estacoes_iniciais)

    # 3. Serviços iniciais
    cursor.execute("SELECT COUNT(*) as total FROM servicos")
    if cursor.fetchone()[0] == 0:
        servicos_iniciais = [
            ("Instalação de Wallbox Residencial", "Instalação completa e homologada de carregador até 22kW.", 1200.00),
            ("Diagnóstico de Bateria de Tração", "Varredura computadorizada e verificação de degradação das células.", 350.00),
            ("Manutenção Preventiva de Conectores", "Inspeção e limpeza técnica dos conectores de carga rápida.", 180.00),
        ]
        cursor.executemany("""
            INSERT INTO servicos (titulo, descricao, preco)
            VALUES (?, ?, ?)
        """, servicos_iniciais)

    conn.commit()


# =====================================================================
# FUNÇÕES DE USUÁRIOS
# =====================================================================

def cadastrar_usuario(nome: str, email: str, usuario: str, senha: str, tipo: str = "cliente"):
    """
    Cadastra um novo usuário no banco de dados.
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
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nome, email, usuario, senha, tipo)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, email, usuario, senha_cripto, tipo))
            conn.commit()
            return True, f"Usuário '{usuario}' cadastrado com sucesso!"
    except sqlite3.IntegrityError as e:
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
    Verifica as credenciais do usuário.
    Retorna os dados do usuário (dict) em caso de sucesso, ou None se inválido.
    """
    usuario = usuario.strip().lower()
    senha_cripto = hash_senha(senha.strip())

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, email, usuario, tipo, criado_em
            FROM usuarios
            WHERE usuario = ? AND senha = ?
        """, (usuario, senha_cripto))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def listar_usuarios():
    """Retorna a lista de todos os usuários cadastrados."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, usuario, tipo, criado_em FROM usuarios ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


# =====================================================================
# FUNÇÕES DE ESTAÇÕES
# =====================================================================

def listar_estacoes():
    """Retorna todas as estações de recarga cadastradas."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estacoes ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def cadastrar_estacao(nome: str, endereco: str, potencia_kw: float, tipo_conector: str, preco_kwh: float, status: str = "Disponível"):
    """Adiciona uma nova estação de recarga."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO estacoes (nome, endereco, potencia_kw, tipo_conector, preco_kwh, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, endereco, potencia_kw, tipo_conector, preco_kwh, status))
            conn.commit()
            return True, "Estação cadastrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar estação: {e}"


# =====================================================================
# FUNÇÕES DE VEÍCULOS
# =====================================================================

def cadastrar_veiculo(usuario_id: int, marca: str, modelo: str, placa: str, ano: int, tipo_conector: str, capacidade_bateria_kwh: float):
    """Cadastra um novo veículo vinculado a um usuário."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO veiculos (usuario_id, marca, modelo, placa, ano, tipo_conector, capacidade_bateria_kwh)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (usuario_id, marca, modelo, placa.upper().strip(), ano, tipo_conector, capacidade_bateria_kwh))
            conn.commit()
            return True, "Veículo cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Já existe um veículo cadastrado com esta placa!"
    except Exception as e:
        return False, f"Erro ao cadastrar veículo: {e}"


def listar_veiculos(usuario_id: int = None):
    """Lista os veículos de um usuário específico ou todos os veículos."""
    with conectar() as conn:
        cursor = conn.cursor()
        if usuario_id:
            cursor.execute("SELECT * FROM veiculos WHERE usuario_id = ? ORDER BY id DESC", (usuario_id,))
        else:
            cursor.execute("""
                SELECT v.*, u.nome as proprietario
                FROM veiculos v
                JOIN usuarios u ON v.usuario_id = u.id
                ORDER BY v.id DESC
            """)
        return [dict(row) for row in cursor.fetchall()]


# =====================================================================
# FUNÇÕES DE RECARGAS
# =====================================================================

def registrar_recarga(usuario_id: int, estacao_id: int, veiculo_id: int, energia_kwh: float, valor_total: float, status: str = "Concluída"):
    """Registra uma sessão de recarga."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recargas (usuario_id, estacao_id, veiculo_id, energia_kwh, valor_total, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (usuario_id, estacao_id, veiculo_id, energia_kwh, valor_total, status))
            conn.commit()
            return True, "Recarga registrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar recarga: {e}"


def listar_recargas(usuario_id: int = None):
    """Lista as recargas registradas."""
    with conectar() as conn:
        cursor = conn.cursor()
        if usuario_id:
            cursor.execute("""
                SELECT r.*, e.nome as estacao_nome, v.modelo as veiculo_modelo
                FROM recargas r
                JOIN estacoes e ON r.estacao_id = e.id
                LEFT JOIN veiculos v ON r.veiculo_id = v.id
                WHERE r.usuario_id = ?
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
        return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    print("Inicializando o banco de dados...")
    inicializar_banco()
    print(f"Banco de dados criado com sucesso em: {DB_NAME}")
    
    with conectar() as conn:
        cursor = conn.cursor()
        for tabela in ["usuarios", "veiculos", "estacoes", "recargas", "servicos"]:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            qtd = cursor.fetchone()[0]
            print(f"- Tabela '{tabela}': {qtd} registro(s)")
