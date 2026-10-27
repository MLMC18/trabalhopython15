class Utilizador:

    def __init__(self, id_utilizador, nome, username, senha, tipo):
        self.id_utilizador = id_utilizador
        self.nome = nome
        self.username = username
        self.senha = senha
        self.tipo = tipo

    def mostrar_informacoes(self):
        print("ID:", self.id_utilizador)
        print("Nome:", self.nome)
        print("Utilizador:", self.username)
        print("Tipo:", self.tipo)