import mysql.connector

def iniciar_conexao():

  return mysql.connector.connect(
  host = "gateway01.ap-northeast-1.prod.aws.tidbcloud.com",
  user = "2KQqXb3M53HDBbJ.root",
  password = "ikBTU35jXuSldNNr",
  database = "modulo15",
  port = 4000,
  ssl ={"ssl": True}
 )

