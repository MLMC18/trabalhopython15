
import mysql.connector
from mysql.connector import Error
from decimal import Decimal, InvalidOperation

# Configuração da base de dados
CONFIG = {
    "host": "gateway01.ap-northeast-1.prod.aws.tidbcloud.com" ,
    "user": "2KQqXB3M53HDBbJ.root",
    "password": "ikBTU35jXuSldNNr",
    "database": "modulo15"
}

LIMITE_STOCK_BAIXO = 5


def conectar():
    """Estabelece a ligação à base de dados MySQL."""
    try:
        return mysql.connector.connect(**CONFIG)
    except Error as erro:
        print(f"Erro na ligação ao MySQL: {erro}")
        return None


def ler_inteiro(mensagem, minimo=0):
    while True:
        try:
            valor = int(input(mensagem))
            if valor < minimo:
                print(f"O valor mínimo permitido é {minimo}.")
                continue
            return valor
        except ValueError:
            print("Introduz um número inteiro válido.")


def ler_preco(mensagem):
    while True:
        try:
            valor = Decimal(input(mensagem).replace(",", "."))
            if not valor.is_finite() or valor < 0:
                print("Introduz um preço válido e não negativo.")
                continue
            if valor.as_tuple().exponent < -2:
                print("O preço pode ter, no máximo, duas casas decimais.")
                continue
            return valor
        except InvalidOperation:
            print("Introduz um preço válido.")


def adicionar_produto():
    nome = input("Nome do produto: ").strip()
    if not nome:
        print("O nome é obrigatório.")
        return

    descricao = input("Descrição: ").strip()
    preco = ler_preco("Preço (€): ")
    quantidade = ler_inteiro("Quantidade inicial: ")

    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO produtos (nome, descricao, preco, quantidade)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (nome, descricao, preco, quantidade))
        conn.commit()

        print(f"Produto adicionado com sucesso! ID: {cursor.lastrowid}")
        verificar_stock(quantidade, nome)

    except Error as erro:
        conn.rollback()
        print(f"Erro ao adicionar produto: {erro}")
    finally:
        conn.close()


def listar_produtos():
    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos ORDER BY nome")
        produtos = cursor.fetchall()

        if not produtos:
            print("Não existem produtos cadastrados.")
            return

        print("\n--- CATÁLOGO DE PRODUTOS ---")
        for p in produtos:
            print(
                f"ID: {p['id']} | {p['nome']} | "
                f"Preço: {p['preco']} € | "
                f"Stock: {p['quantidade']}"
            )
            print(f"Descrição: {p['descricao'] or '-'}")
            verificar_stock(p["quantidade"], p["nome"])
            print("-" * 45)

    except Error as erro:
        print(f"Erro ao listar produtos: {erro}")
    finally:
        conn.close()


def pesquisar_produtos():
    termo = input("Nome ou parte do nome: ").strip()
    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nome, descricao, preco, quantidade
            FROM produtos
            WHERE nome LIKE %s
            ORDER BY nome
            """,
            (f"%{termo}%",)
        )
        produtos = cursor.fetchall()

        if not produtos:
            print("Nenhum produto encontrado.")
            return

        for p in produtos:
            print(
                f"ID: {p['id']} | {p['nome']} | "
                f"{p['preco']} € | Stock: {p['quantidade']}"
            )
            verificar_stock(p["quantidade"], p["nome"])

    except Error as erro:
        print(f"Erro na pesquisa: {erro}")
    finally:
        conn.close()


def atualizar_produto():
    produto_id = ler_inteiro("ID do produto a atualizar: ", 1)
    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM produtos WHERE id = %s",
            (produto_id,)
        )
        produto = cursor.fetchone()

        if produto is None:
            print("Produto não encontrado.")
            return

        print("Deixa o campo vazio para manter o valor atual.")

        nome = input(f"Nome [{produto['nome']}]: ").strip()
        descricao = input(
            f"Descrição [{produto['descricao'] or '-'}]: "
        ).strip()
        preco_txt = input(f"Preço [{produto['preco']}]: ").strip()
        qtd_txt = input(
            f"Quantidade [{produto['quantidade']}]: "
        ).strip()

        novo_nome = nome or produto["nome"]
        nova_descricao = (
            descricao if descricao else produto["descricao"]
        )

        if preco_txt:
            try:
                novo_preco = Decimal(preco_txt.replace(",", "."))
                if (
                    not novo_preco.is_finite()
                    or novo_preco < 0
                    or novo_preco.as_tuple().exponent < -2
                ):
                    print("Preço inválido.")
                    return
            except InvalidOperation:
                print("Preço inválido.")
                return
        else:
            novo_preco = produto["preco"]

        if qtd_txt:
            try:
                nova_qtd = int(qtd_txt)
                if nova_qtd < 0:
                    print("A quantidade não pode ser negativa.")
                    return
            except ValueError:
                print("Quantidade inválida.")
                return
        else:
            nova_qtd = produto["quantidade"]

        cursor.execute(
            """
            UPDATE produtos
            SET nome = %s, descricao = %s,
                preco = %s, quantidade = %s
            WHERE id = %s
            """,
            (
                novo_nome, nova_descricao,
                novo_preco, nova_qtd, produto_id
            )
        )
        conn.commit()

        print("Produto atualizado com sucesso!")
        verificar_stock(nova_qtd, novo_nome)

    except Error as erro:
        conn.rollback()
        print(f"Erro ao atualizar produto: {erro}")
    finally:
        conn.close()


def remover_produto():
    produto_id = ler_inteiro("ID do produto a remover: ", 1)
    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome FROM produtos WHERE id = %s",
            (produto_id,)
        )
        produto = cursor.fetchone()

        if produto is None:
            print("Produto não encontrado.")
            return

        confirmacao = input(
            f"Confirmas a remoção de '{produto[0]}'? (s/n): "
        ).strip().lower()

        if confirmacao != "s":
            print("Remoção cancelada.")
            return

        cursor.execute(
            "DELETE FROM produtos WHERE id = %s",
            (produto_id,)
        )
        conn.commit()
        print("Produto removido com sucesso!")

    except Error as erro:
        conn.rollback()
        print(f"Erro ao remover produto: {erro}")
    finally:
        conn.close()


def verificar_stock(quantidade, nome):
    """Alerta quando existem menos de 5 unidades."""
    if quantidade < LIMITE_STOCK_BAIXO:
        print(
            f" ALERTA: Stock baixo de '{nome}'! "
            f"Restam {quantidade} unidade(s)."
        )


def listar_stock_baixo():
    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nome, quantidade
            FROM produtos
            WHERE quantidade < %s
            ORDER BY quantidade ASC
            """,
            (LIMITE_STOCK_BAIXO,)
        )
        produtos = cursor.fetchall()

        print("\n--- ALERTAS DE STOCK BAIXO ---")
        if not produtos:
            print("Não existem produtos com stock baixo.")
            return

        for p in produtos:
            print(
                f" ID: {p['id']} | {p['nome']} | "
                f"Restam {p['quantidade']} unidade(s)"
            )

    except Error as erro:
        print(f"Erro ao consultar stock: {erro}")
    finally:
        conn.close()


def menu():
    while True:
        print("\n===== GESTÃO DE PRODUTOS E STOCK =====")
        print("1. Adicionar produto")
        print("2. Listar produtos")
        print("3. Pesquisar produto")
        print("4. Atualizar produto")
        print("5. Remover produto")
        print("6. Consultar stock baixo")
        print("0. Sair")

        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            adicionar_produto()
        elif opcao == "2":
            listar_produtos()
        elif opcao == "3":
            pesquisar_produtos()
        elif opcao == "4":
            atualizar_produto()
        elif opcao == "5":
            remover_produto()
        elif opcao == "6":
            listar_stock_baixo()
        elif opcao == "0":
            print("Programa terminado.")
            break
        else:
            print("Opção inválida. Tenta novamente.")


if __name__ == "__main__":
    menu()
