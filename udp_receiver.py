import socket

def iniciar_agente():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", 9999))
    print("Agente à escuta na porta 9999...")

    while True:
        dados, addr = sock.recvfrom(1024)
        mensagem = dados.decode()
        print(f"Recebido de {addr}: {mensagem}")

iniciar_agente()
