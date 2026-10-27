class Produto:

    def __init__(self, id_produto, nome, categoria, preco, stock, descricao):
        self.id_produto = id_produto
        self.nome = nome
        self.categoria = categoria
        self.preco = preco
        self.stock = stock
        self.descricao = descricao

    def mostrar_informacoes(self):
        print("ID:", self.id_produto)
        print("Nome:", self.nome)
        print("Categoria:", self.categoria)
        print("Preço:", self.preco, "€")
        print("Stock:", self.stock)
        print("Descrição:", self.descricao)