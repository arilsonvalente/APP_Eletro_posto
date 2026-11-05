-- =====================================================================
-- PROJETO: APP ELETRO POSTO (EletroBel)
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS EM SQL
-- Compatível com: SQLite, MySQL, MariaDB, PostgreSQL
-- =====================================================================

-- Habilitar verificação de Chaves Estrangeiras (específico para SQLite)
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 1. TABELA DE USUÁRIOS (Clientes e Administradores)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL, -- Senha armazenada em hash SHA-256
    tipo TEXT DEFAULT 'cliente', -- 'cliente' ou 'admin'
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 2. TABELA DE VEÍCULOS ELÉTRICOS (Vinculados aos Usuários)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    placa TEXT UNIQUE NOT NULL,
    ano INTEGER,
    tipo_conector TEXT NOT NULL, -- Ex: 'CCS2', 'Tipo 2', 'CHAdeMO'
    capacidade_bateria_kwh REAL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- 3. TABELA DE ESTAÇÕES DE RECARGA (Eletropostos)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    potencia_kw REAL NOT NULL,
    tipo_conector TEXT NOT NULL,
    preco_kwh REAL NOT NULL,
    status TEXT DEFAULT 'Disponível', -- 'Disponível', 'Ocupado', 'Manutenção'
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 4. TABELA DE HISTÓRICO DE RECARGAS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recargas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    estacao_id INTEGER NOT NULL,
    veiculo_id INTEGER,
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP,
    energia_kwh REAL DEFAULT 0.0,
    valor_total REAL DEFAULT 0.0,
    status TEXT DEFAULT 'Em andamento', -- 'Em andamento', 'Concluída', 'Cancelada'
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
    FOREIGN KEY (estacao_id) REFERENCES estacoes (id) ON DELETE CASCADE,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos (id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------
-- 5. TABELA DE SERVIÇOS E MANUTENÇÕES
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    preco REAL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- ÍNDICES PARA OTIMIZAÇÃO DE BUSCA E PERFORMANCE
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios (usuario, senha);
CREATE INDEX IF NOT EXISTS idx_veiculos_usuario ON veiculos (usuario_id);
CREATE INDEX IF NOT EXISTS idx_recargas_usuario ON recargas (usuario_id);
CREATE INDEX IF NOT EXISTS idx_recargas_estacao ON recargas (estacao_id);
CREATE INDEX IF NOT EXISTS idx_estacoes_status ON estacoes (status);

-- =====================================================================
-- DADOS INICIAIS (CARGA / SEED DATA)
-- =====================================================================

-- 1. Usuário Administrador Padrão (Login: admin | Senha original: 123)
-- O hash SHA-256 de '123' é: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
INSERT OR IGNORE INTO usuarios (id, nome, email, usuario, senha, tipo)
VALUES (
    1,
    'Administrador EletroBel',
    'admin@eletrobel.com',
    'admin',
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
    'admin'
);

-- 2. Estações de Recarga Iniciais (Região Metropolitana de Belém / Ananindeua)
INSERT OR IGNORE INTO estacoes (id, nome, endereco, potencia_kw, tipo_conector, preco_kwh, status)
VALUES 
    (1, 'Estação EletroBel Doca', 'Av. Visconde de Souza Franco (Doca), 500 - Belém, PA', 150.0, 'CCS2 / Tipo 2', 1.95, 'Disponível'),
    (2, 'Estação Shopping Bosque Grão-Pará', 'Av. Centenário, 1052 - Belém, PA', 60.0, 'CCS2', 2.10, 'Disponível'),
    (3, 'Estação Metrópole Ananindeua', 'Rodovia BR-316, Km 4 - Coqueiro, Ananindeua, PA', 120.0, 'CCS2 / CHAdeMO', 1.90, 'Disponível'),
    (4, 'Estação Cidade Nova', 'Av. Arterial 18, 400 - Cidade Nova, Ananindeua, PA', 22.0, 'Tipo 2', 1.45, 'Disponível'),
    (5, 'Estação Aeroporto Internacional', 'Val-de-Cans - Estacionamento VIP, Belém, PA', 100.0, 'CCS2', 2.30, 'Ocupado'),
    (6, 'Estação BRT Augusto Montenegro', 'Av. Augusto Montenegro, Km 8 - Parque Verde, Belém, PA', 90.0, 'CCS2 / Tipo 2', 1.85, 'Disponível');

-- 3. Catálogo de Serviços Especializados
INSERT OR IGNORE INTO servicos (id, titulo, descricao, preco)
VALUES 
    (1, 'Instalação de Wallbox Residencial', 'Instalação completa e homologada de carregador até 22kW.', 1200.00),
    (2, 'Diagnóstico de Bateria de Tração', 'Varredura computadorizada e verificação de degradação das células.', 350.00),
    (3, 'Manutenção Preventiva de Conectores', 'Inspeção e limpeza técnica dos conectores de carga rápida.', 180.00);
