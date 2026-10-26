import socket
import json

HOST = "gateway01.ap-northeast-1.prod.aws.tidbcloud.com"
PORTA = 4000


def ligar_servidor():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORTA))
    return cliente


def enviar_pedido(cliente, pedido):
    mensagem = json.dumps(pedido)
    cliente.sendall(mensagem.encode("utf-8"))

    resposta = cliente.recv(4096).decode("utf-8")
    return json.loads(resposta)


def menu():
    print("\n LOJA DE PRODUTOS SUSTENTÁVEIS ")
    print("1 - Login")
    print("2 - Registar conta")
    print("3 - Consultar produtos")
    print("4 - Comprar produto")
    print("0 - Sair")


if __name__ == "__main__":
    menu()