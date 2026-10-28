from connect import iniciar_conexao

mydb = iniciar_conexao()

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE Utilizadores (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), senha VARCHAR(255), tipo_utilizador ENUM('admin', 'vendedor', 'cliente') NOT NULL)")

mycursor.execute("DROP TABLE IF EXISTS produtos; CREATE TABLE produtos (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255) NOT NULL, descriçao TEXT, preço DECIMAL(10,2) NOT NULL, quantidade INT NOT NULL")

mycursor.execute("CREATE TABLE Vendas (id INT AUTO_INCREMENT PRIMARY KEY, utilizador_id INT, data_hora DATETIME DEFAULT CURRENT_TIMESTAMP, valor_total DECIMAL(10, 2) NOT NULL, FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id))")

mycursor.execute("CREATE TABLE Itens_Venda (id INT AUTO_INCREMENT PRIMARY KEY, venda_id INT, produto_id INT,quantidade INT NOT NULL, preco_unitario DECIMAL(10, 2) NOT NULL, FOREIGN KEY (venda_id) REFERENCES vendas(id),FOREIGN KEY (produto_id) REFERENCES produtos(id))")

mycursor.execute("SHOW TABLES")

for x in mycursor:
  print(x)

