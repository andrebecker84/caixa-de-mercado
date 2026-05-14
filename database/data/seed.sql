SET NAMES utf8mb4;
USE mercado_at;

INSERT INTO operador (nome, cargo, iniciais, cor) VALUES
('André Becker',    'Supervisor', 'AB', '#7C6FCD'),
('Maria Souza',     'Operador',   'MS', '#00C9A7'),
('Carlos Ferreira', 'Operador',   'CF', '#FF6B6B'),
('Juliana Lima',    'Caixa',      'JL', '#FFB700'),
('Roberto Alves',   'Caixa',      'RA', '#4ECDC4');

INSERT INTO cliente (nome) VALUES
('João Silva'),
('Maria Oliveira'),
('Pedro Santos'),
('Ana Costa'),
('Lucas Ferreira');

INSERT INTO produto (nome, quantidade, preco) VALUES
('Arroz Integral 1kg',    50, 8.99),
('Feijão Preto 1kg',      40, 7.49),
('Macarrão Espaguete 500g', 60, 4.29),
('Leite Integral 1L',     80, 5.99),
('Café Torrado 500g',     35, 14.90),
('Açúcar Refinado 1kg',   45, 4.99),
('Óleo de Soja 900ml',    30, 8.49),
('Farinha de Trigo 1kg',  40, 5.59),
('Sal Refinado 1kg',      55, 2.99),
('Manteiga 200g',         25, 9.90);
