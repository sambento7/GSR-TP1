import socket

def enviar_mensagem():
    mensagem = "Teste L-SNMPvS UDP".encode()
    destino = ("localhost", 9999)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(mensagem, destino)
    print("Mensagem enviada para o agente.")

enviar_mensagem()
