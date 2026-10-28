import socket
import json
import struct
import mysql.connector
from decimal import Decimal
from connect import iniciar_conexao

HOST = "0.0.0.0"
PORTA = 4000


def receber_mensagem(sock):
    tamanho = struct.unpack("!I", receber_bytes(sock, 4))[0]
    return receber_bytes(sock, tamanho).decode("utf-8")


def receber_bytes(sock, tamanho):
    dados = b""

    while len(dados) < tamanho:
        parte = sock.recv(tamanho - len(dados))

        if not parte:
            raise ConnectionError("Ligacao encerrada")

        dados += parte

    return dados


def enviar_mensagem(sock, mensagem):
    dados = mensagem.encode("utf-8")
    sock.sendall(struct.pack("!I", len(dados)) + dados)


def resposta(sucesso, mensagem, **extras):
    resultado = {
        "sucesso": sucesso,
        "mensagem": mensagem
    }
    resultado.update(extras)

    return json.dumps(
        resultado,
        ensure_ascii=False,
        default=str
    )



def autenticar_utilizador(dados):
    username = dados.get("username")
    senha = dados.get("senha")

    if not username or not senha:
        return resposta(False, "Preenche o username e a senha")

    conexao = None
    cursor = None

    try:
        conexao = iniciar_servidor()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, username, tipo_utilizador
            FROM Utilizadores
            WHERE username = %s AND senha = %s
            """,
            (username, senha)
        )

        utilizador = cursor.fetchone()

        if utilizador:
            return resposta(
                True,
                "Login efetuado com sucesso",
                utilizador=utilizador
            )

        return resposta(False, "Dados de login incorretos")

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def listar_produtos():
    conexao = None
    cursor = None

    try:
        conexao = iniciar_servidor()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, nome, categoria, `preço`, stock, `descriçao`
            FROM Produtos
            ORDER BY nome
            """
        )

        produtos = cursor.fetchall()

        return resposta(
            True,
            "Produtos consultados com sucesso",
            produtos=produtos
        )

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def realizar_venda(dados):
    utilizador_id = dados.get("utilizador_id")
    produtos = dados.get("produtos", [])

    if not isinstance(utilizador_id, int) or utilizador_id <= 0:
        return resposta(False, "Utilizador invalido")

    if not isinstance(produtos, list) or not produtos:
        return resposta(False, "A venda nao tem produtos")

    # Juntar quantidades de produtos repetidos
    quantidades = {}

    for item in produtos:
        if not isinstance(item, dict):
            return resposta(False, "Produto invalido")

        pid = item.get("produto_id")
        qtd = item.get("quantidade")

        if not isinstance(pid, int) or pid <= 0:
            return resposta(False, "ID de produto invalido")

        if not isinstance(qtd, int) or qtd <= 0:
            return resposta(False, "Quantidade invalida")

        quantidades[pid] = quantidades.get(pid, 0) + qtd

    conexao = None
    cursor = None

    try:
        conexao = iniciar_servidor()
        cursor = conexao.cursor(dictionary=True)
        conexao.start_transaction()

        cursor.execute(
            "SELECT id FROM Utilizadores WHERE id = %s",
            (utilizador_id,)
        )

        if not cursor.fetchone():
            raise ValueError("Utilizador nao encontrado")

        total = Decimal("0.00")
        itens = []

        for produto_id, quantidade in quantidades.items():
            cursor.execute(
                """
                SELECT id, nome, `preço`, stock
                FROM Produtos
                WHERE id = %s
                FOR UPDATE
                """,
                (produto_id,)
            )

            produto = cursor.fetchone()

            if not produto:
                raise ValueError(
                    f"Produto {produto_id} nao encontrado"
                )

            if produto["stock"] < quantidade:
                raise ValueError(
                    f"Stock insuficiente: {produto['nome']}"
                )

            preco = Decimal(str(produto["preço"]))
            total += preco * quantidade

            itens.append({
                "produto_id": produto_id,
                "quantidade": quantidade,
                "preco": preco
            })

        cursor.execute(
            """
            INSERT INTO Vendas (utilizador_id, valor_total)
            VALUES (%s, %s)
            """,
            (utilizador_id, total)
        )

        venda_id = cursor.lastrowid

        for item in itens:
            cursor.execute(
                """
                INSERT INTO Itens_Venda
                (venda_id, produto_id, quantidade, preco_unitario)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    venda_id,
                    item["produto_id"],
                    item["quantidade"],
                    item["preco"]
                )
            )

            cursor.execute(
                """
                UPDATE Produtos
                SET stock = stock - %s
                WHERE id = %s
                """,
                (item["quantidade"], item["produto_id"])
            )

        conexao.commit()

        return resposta(
            True,
            "Venda registada com sucesso",
            venda_id=venda_id,
            valor_total=total
        )

    except Exception as erro:
        if conexao:
            conexao.rollback()

        print("Erro na venda:", erro)
        return resposta(False, str(erro))

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def processar_pedido(pedido):
    try:
        dados = json.loads(pedido)
        tipo = dados.get("tipo")

        if tipo == "LOGIN":
            return autenticar_utilizador(dados)

        elif tipo == "LISTAR_PRODUTOS":
            return listar_produtos()

        elif tipo == "VENDA":
            return realizar_venda(dados)

        else:
            return resposta(False, "Pedido desconhecido")

    except json.JSONDecodeError:
        return resposta(False, "JSON invalido")

    except Exception as erro:
        print("Erro:", erro)
        return resposta(False, "Erro ao processar pedido")



def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    

    try:
        servidor.bind((HOST, PORTA))
        servidor.listen(5)

        print(f"Servidor ativo na porta {PORTA}")

        while True:
            cliente, endereco = servidor.accept()
            print("Cliente ligado:", endereco)

            with cliente:
                try:
                    pedido = receber_mensagem(cliente)
                    print("Pedido:", pedido)

                    resultado = processar_pedido(pedido)
                    enviar_mensagem(cliente, resultado)

                except Exception as erro:
                    print("Erro de comunicacao:", erro)

    except KeyboardInterrupt:
        print("\nServidor encerrado")

    except Exception as erro:
        print("Erro no servidor:", erro)

    finally:
        servidor.close()


def menu():
    while True:
        print("1 - Iniciar servidor")
        print("2 - Testar base de dados")
        print("3 - Sair")

        opcao = input("Opcao: ")

        if opcao == "1":
            iniciar_servidor()

        elif opcao == "2":
            conexao = None
            try:
                conexao = iniciar_servidor()
                print("Ligacao a base de dados efetuada!")
            except Exception as erro:
                print("Erro na base de dados:", erro)
            finally:
                if conexao:
                    conexao.close()

        elif opcao == "3":
            break

        else:
            print("Opcao invalida")


if __name__ == "__main__":
    menu()