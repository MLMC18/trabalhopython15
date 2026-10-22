import mysql.connector

def iniciar_conexao():

  return mysql.connector.connect(
  host = "sql201.infinityfree.com:3306" ,
  usuário = "if0_43244066" ,
  senha = "vBEPgun9iArZ" ,
  database = "if0_43244066_produtos"
 )