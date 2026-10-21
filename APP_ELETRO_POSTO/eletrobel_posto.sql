-- =====================================================================
-- SCRIPT SQL ATUALIZADO COM O BANCO DE DADOS - ELETROBEL POSTO
-- =====================================================================

CREATE DATABASE IF NOT EXISTS eletrobel_posto
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE eletrobel_posto;

-- 1. Tabela de Usuários
CREATE TABLE IF NOT EXISTS eletrobel_posto.usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL, -- Hash SHA-256
    tipo ENUM('cliente', 'admin') DEFAULT 'cliente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tabela de Veículos
CREATE TABLE IF NOT EXISTS eletrobel_posto.veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    placa VARCHAR(10) UNIQUE NOT NULL,
    ano INT,
    tipo_conector VARCHAR(30) NOT NULL, -- Ex: 'CCS2', 'Tipo 2', 'CHAdeMO'
    capacidade_bateria_kwh DECIMAL(6, 2),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_veiculos_usuario FOREIGN KEY (usuario_id)
        REFERENCES eletrobel_posto.usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tabela de Estações de Recarga
CREATE TABLE IF NOT EXISTS eletrobel_posto.estacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    potencia_kw DECIMAL(6, 2) NOT NULL,
    tipo_conector VARCHAR(30) NOT NULL,
    preco_kwh DECIMAL(8, 2) NOT NULL,
    status ENUM('Disponível', 'Ocupado', 'Manutenção') DEFAULT 'Disponível',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabela de Histórico de Recargas
CREATE TABLE IF NOT EXISTS eletrobel_posto.recargas (
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
        REFERENCES eletrobel_posto.usuarios (id) ON DELETE CASCADE,
    CONSTRAINT fk_recargas_estacao FOREIGN KEY (estacao_id)
        REFERENCES eletrobel_posto.estacoes (id) ON DELETE CASCADE,
    CONSTRAINT fk_recargas_veiculo FOREIGN KEY (veiculo_id)
        REFERENCES eletrobel_posto.veiculos (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Tabela de Serviços e Manutenções
CREATE TABLE IF NOT EXISTS eletrobel_posto.servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- DADOS DO BANCO DE DADOS
-- =====================================================================

-- Tabela: usuarios
INSERT INTO eletrobel_posto.usuarios (id, nome, email, usuario, senha, tipo, criado_em) VALUES
(1, 'Administrador EletroBel', 'admin@eletrobel.com', 'admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin', '2026-10-16 22:51:54'),
(3, 'arilson', 'arilsonvalente@gmail.com', 'arilsonvalente', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'cliente', '2026-10-16 23:23:22')
ON DUPLICATE KEY UPDATE nome = VALUES(nome), email = VALUES(email), usuario = VALUES(usuario), senha = VALUES(senha), tipo = VALUES(tipo), criado_em = VALUES(criado_em);

-- Tabela: estacoes
INSERT INTO eletrobel_posto.estacoes (id, nome, endereco, potencia_kw, tipo_conector, preco_kwh, status, criado_em) VALUES
(5, 'Estação EletroBel Doca', 'Av. Visconde de Souza Franco (Doca), 500 - Belém, PA', 150.00, 'CCS2 / Tipo 2', 1.95, 'Disponível', '2026-10-16 23:40:26'),
(6, 'Estação Shopping Bosque Grão-Pará', 'Av. Centenário, 1052 - Belém, PA', 60.00, 'CCS2', 2.10, 'Disponível', '2026-10-16 23:40:26'),
(7, 'Estação Metrópole Ananindeua', 'Rodovia BR-316, Km 4 - Coqueiro, Ananindeua, PA', 120.00, 'CCS2 / CHAdeMO', 1.90, 'Disponível', '2026-10-16 23:40:26'),
(8, 'Estação Cidade Nova', 'Av. Arterial 18, 400 - Cidade Nova, Ananindeua, PA', 22.00, 'Tipo 2', 1.45, 'Disponível', '2026-10-16 23:40:26'),
(9, 'Estação Aeroporto Internacional', 'Val-de-Cans - Estacionamento VIP, Belém, PA', 100.00, 'CCS2', 2.30, 'Ocupado', '2026-10-16 23:40:26'),
(10, 'Estação BRT Augusto Montenegro', 'Av. Augusto Montenegro, Km 8 - Parque Verde, Belém, PA', 90.00, 'CCS2 / Tipo 2', 1.85, 'Disponível', '2026-10-16 23:40:26')
ON DUPLICATE KEY UPDATE nome = VALUES(nome), endereco = VALUES(endereco), potencia_kw = VALUES(potencia_kw), tipo_conector = VALUES(tipo_conector), preco_kwh = VALUES(preco_kwh), status = VALUES(status), criado_em = VALUES(criado_em);

-- Tabela: veiculos
INSERT INTO eletrobel_posto.veiculos (id, usuario_id, marca, modelo, placa, ano, tipo_conector, capacidade_bateria_kwh, criado_em) VALUES
(1, 3, 'byd', 'dophin', 'BR22F22', 2026, 'Tipo', 38.00, '2026-10-21 22:25:45'),
(2, 3, 'gwm', 'Haval', 'BR22FG01', 2025, 'Tipo', 50.00, '2026-10-21 22:48:05')
ON DUPLICATE KEY UPDATE usuario_id = VALUES(usuario_id), marca = VALUES(marca), modelo = VALUES(modelo), placa = VALUES(placa), ano = VALUES(ano), tipo_conector = VALUES(tipo_conector), capacidade_bateria_kwh = VALUES(capacidade_bateria_kwh), criado_em = VALUES(criado_em);

-- Tabela: servicos
INSERT INTO eletrobel_posto.servicos (id, titulo, descricao, preco, criado_em) VALUES
(1, 'Instalação de Wallbox Residencial', 'Instalação completa e homologada de carregador até 22kW.', 1200.00, '2026-10-16 22:51:54'),
(2, 'Diagnóstico de Bateria de Tração', 'Varredura computadorizada e verificação de degradação das células.', 350.00, '2026-10-16 22:51:54'),
(3, 'Manutenção Preventiva de Conectores', 'Inspeção e limpeza técnica dos conectores de carga rápida.', 180.00, '2026-10-16 22:51:54')
ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), descricao = VALUES(descricao), preco = VALUES(preco), criado_em = VALUES(criado_em);
