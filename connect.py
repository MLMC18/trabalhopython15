import mysql.connector

def iniciar_conexao():

  return mysql.connector.connect(
  host = "gateway01.ap-northeast-1.prod.aws.tidbcloud.com" ,
  usuário = "2KQqXb3M53HDBbJ.root" ,
  senha = "ikBTU35jXuSldNNr" ,
  database = "modulo15"
 )