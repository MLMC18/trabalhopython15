import socket
import json
import struct

HOST = "192.168.2.32"
PORTA = 4000



def receber_bytes(sock, tamanho):
    dados = b""

    while len(dados) < tamanho:
        parte = sock.recv(tamanho - len(dados))

        if not parte:
            raise ConnectionError("Ligacao encerrada pelo servidor")

        dados += parte

    return dados


def enviar_pedido(dados):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PORTA))

        mensagem = json.dumps(dados, ensure_ascii=False).encode("utf-8")

        cliente.sendall(struct.pack("!I", len(mensagem)) + mensagem)

        tamanho = struct.unpack("!I", receber_bytes(cliente, 4))[0]
        resposta = receber_bytes(cliente, tamanho).decode("utf-8")

        return json.loads(resposta)

    except Exception as erro:
        print("Erro de comunicacao:", erro)
        return None

    finally:
        cliente.close()



def login():
    print("\nINICIAR SESSAO")

    username = input("Username: ")
    senha = input("Senha: ")

    resultado = enviar_pedido({
        "tipo": "LOGIN",
        "username": username,
        "senha": senha
    })

    if resultado is None:
        return None

    print(resultado["mensagem"])

    if resultado.get("sucesso"):
        utilizador = resultado["utilizador"]

        print("Bem-vindo,", utilizador["username"])
        print("Tipo:", utilizador["tipo_utilizador"])

        return utilizador

    return None


def consultar_produtos():
    resultado = enviar_pedido({
        "tipo": "LISTAR_PRODUTOS"
    })

    if resultado is None:
        return

    print("\n", resultado["mensagem"])

    if resultado.get("sucesso"):
        produtos = resultado.get("produtos", [])

        if not produtos:
            print("Nao existem produtos.")
            return

        for produto in produtos:
            print("ID:", produto["id"])
            print("Nome:", produto["nome"])
            print("Categoria:", produto["categoria"])
            print("Preco:", produto["preço"], "euros")
            print("Stock:", produto["stock"])
            print("Descricao:", produto["descriçao"])


def registar_venda(utilizador):
    print("\nNOVA VENDA")
    print("Escreve 0 no ID do produto para terminar.")

    produtos = []

    while True:
        try:
            produto_id = int(input("ID do produto: "))

            if produto_id == 0:
                break

            quantidade = int(input("Quantidade: "))

            if produto_id < 1 or quantidade < 1:
                print("Os valores devem ser positivos.")
                continue

            produtos.append({
                "produto_id": produto_id,
                "quantidade": quantidade
            })

        except ValueError:
            print("Introduz numeros inteiros validos.")

    if not produtos:
        print("Nenhum produto selecionado.")
        return

    resultado = enviar_pedido({
        "tipo": "VENDA",
        "utilizador_id": utilizador["id"],
        "produtos": produtos
    })

    if resultado is None:
        return

    print("\n", resultado["mensagem"])

    if resultado.get("sucesso"):
        print("Numero da venda:", resultado["venda_id"])
        print("Total:", resultado["valor_total"], "euros")



def menu():
    utilizador = None

    while True:
        print("1 - Iniciar sessao")
        print("2 - Consultar produtos")
        print("3 - Registar venda")
        print("4 - Terminar sessao")
        print("5 - Sair")


        opcao = input("Escolhe uma opcao: ")

        if opcao == "1":
            utilizador = login()

        elif opcao == "2":
            consultar_produtos()

        elif opcao == "3":
            if utilizador is None:
                print("Tens de iniciar sessao primeiro.")
            else:
                registar_venda(utilizador)

        elif opcao == "4":
            utilizador = None
            print("Sessao terminada.")

        elif opcao == "5":
            print("A sair do cliente...")
            break

        else:
            print("Opcao invalida!")


if __name__ == "__main__":
    menu()