
import mysql.connector

from connect import iniciar_conexao


class Produto:
    def __init__(self, nome, descricao, preco, quantidade, id=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.quantidade = quantidade

    def adicionar(self):
        db = conectar()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO produtos (nome, descricao, preco, quantidade)
               VALUES (%s, %s, %s, %s)""",
            (self.nome, self.descricao, self.preco, self.quantidade)
        )
        db.commit()
        db.close()
        print("Produto adicionado!")

    def atualizar(self):
        db = conectar()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE produtos
               SET nome=%s, descricao=%s, preco=%s, quantidade=%s
               WHERE id=%s""",
            (self.nome, self.descricao, self.preco,
             self.quantidade, self.id)
        )
        db.commit()
        print("Produto atualizado!" if cursor.rowcount else "ID não encontrado.")
        db.close()

    @staticmethod
    def remover(id):
        db = conectar()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id=%s", (id,))
        db.commit()
        print("Produto removido!" if cursor.rowcount else "ID não encontrado.")
        db.close()

    @staticmethod
    def listar(filtro=""):
        db = conectar()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM produtos WHERE nome LIKE %s",
            (f"%{filtro}%",)
        )
        produtos = cursor.fetchall()

        for p in produtos:
            print(p)
            if p[4] < 5:
                print(f"ALERTA: Stock baixo de {p[1]} ({p[4]} unidades)")

        db.close()


def menu():
    while True:
        print("""
--- GESTÃO DE PRODUTOS ---
1. Adicionar
2. Listar todos
3. Pesquisar por nome
4. Atualizar
5. Remover
0. Sair
""")
        op = input("Opção: ")

        if op == "1":
            nome = input("Nome: ")
            descricao = input("Descrição: ")
            preco = float(input("Preço: "))
            quantidade = int(input("Quantidade: "))
            Produto(nome, descricao, preco, quantidade).adicionar()

        elif op == "2":
            Produto.listar()

        elif op == "3":
            Produto.listar(input("Nome a pesquisar: "))

        elif op == "4":
            id = int(input("ID: "))
            nome = input("Novo nome: ")
            descricao = input("Nova descrição: ")
            preco = float(input("Novo preço: "))
            quantidade = int(input("Nova quantidade: "))
            Produto(nome, descricao, preco, quantidade, id).atualizar()

        elif op == "5":
            Produto.remover(int(input("ID a remover: ")))

        elif op == "0":
            break

        else:
            print("Opção inválida!")


if __name__ == "__main__":
    menu()
