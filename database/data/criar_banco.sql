CREATE DATABASE IF NOT EXISTS mercado_at CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mercado_at;
ALTER DATABASE mercado_at CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS compra;
DROP TABLE IF EXISTS produto;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS operador;

CREATE TABLE operador (
    id_operador INT PRIMARY KEY AUTO_INCREMENT,
    nome        VARCHAR(50)  NOT NULL,
    cargo       VARCHAR(30)  NOT NULL,
    iniciais    VARCHAR(4)   NOT NULL,
    cor         VARCHAR(10)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cliente (
    id_cliente INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE produto (
    id_produto INT PRIMARY KEY AUTO_INCREMENT,
    nome       VARCHAR(50)    NOT NULL,
    quantidade INT            NOT NULL,
    preco      DECIMAL(10,2)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE compra (
    id_compra    INT PRIMARY KEY AUTO_INCREMENT,
    data_compra  DATETIME NOT NULL,
    id_cliente   INT NOT NULL,
    id_operador  INT,
    token_compra VARCHAR(36),
    FOREIGN KEY (id_cliente)  REFERENCES cliente(id_cliente),
    FOREIGN KEY (id_operador) REFERENCES operador(id_operador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE item (
    id_item    INT PRIMARY KEY AUTO_INCREMENT,
    quantidade INT NOT NULL,
    id_compra  INT NOT NULL,
    id_produto INT NOT NULL,
    FOREIGN KEY (id_compra)  REFERENCES compra(id_compra),
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
