import socket
import threading
import configparser
import datetime
import logging
import signal
import sys

# Leer configuración
config = configparser.ConfigParser()
config.read('config.ini')
IP = config['Settings']['IP']
TCP_PORT = int(config['Settings']['TCP_PORT'])
UDP_PORT = int(config['Settings']['UDP_PORT'])

# Configurar logging
logging.basicConfig(
    filename='errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Funciones para TCP Server
def tcp_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP, TCP_PORT))
        server.listen(5)
        print(f"[TCP Server] Listening on {IP}:{TCP_PORT}")

        while True:
            conn, addr = server.accept()
            print(f"[TCP Server] Connection established with {addr}")
            threading.Thread(target=handle_tcp_client, args=(conn,)).start()
    except Exception as e:
        logging.error(f"TCP Server Error: {e}")

def handle_tcp_client(conn):
    try:
        while True:
            msg = conn.recv(1024).decode('utf-8')
            if not msg:
                break
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[TCP Received] {timestamp} - {msg}")
            conn.send(f"[ACK] Received: {msg}".encode('utf-8'))
    except Exception as e:
        logging.error(f"TCP Client Handler Error: {e}")
    finally:
        conn.close()

# Funciones para UDP Server
def udp_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind((IP, UDP_PORT))
        print(f"[UDP Server] Listening on {IP}:{UDP_PORT}")

        while True:
            msg, addr = server.recvfrom(1024)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[UDP Received] {timestamp} - {msg.decode('utf-8')} from {addr}")
    except Exception as e:
        logging.error(f"UDP Server Error: {e}")

# Funciones para TCP Client
def tcp_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((IP, TCP_PORT))
        print(f"[TCP Client] Connected to {IP}:{TCP_PORT}")

        while True:
            msg = input("Enter message (TCP): ")
            if msg.lower() == 'exit':
                break
            client.send(msg.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            print(f"[TCP Response] {response}")
    except Exception as e:
        logging.error(f"TCP Client Error: {e}")
    finally:
        client.close()

# Funciones para UDP Client
def udp_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"[UDP Client] Ready to send to {IP}:{UDP_PORT}")

        while True:
            msg = input("Enter message (UDP): ")
            if msg.lower() == 'exit':
                break
            client.sendto(msg.encode('utf-8'), (IP, UDP_PORT))
    except Exception as e:
        logging.error(f"UDP Client Error: {e}")

# Apagado seguro
def graceful_exit(signal, frame):
    print("\n[INFO] Shutting down servers...")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)

# Ejecución principal
if __name__ == "__main__":
    try:
        # Crear hilos para los servidores
        tcp_thread = threading.Thread(target=tcp_server)
        udp_thread = threading.Thread(target=udp_server)

        tcp_thread.start()
        udp_thread.start()

        # Ejecutar los clientes de forma opcional
        threading.Thread(target=tcp_client).start()
        threading.Thread(target=udp_client).start()

        tcp_thread.join()
        udp_thread.join()
    except Exception as e:
        logging.error(f"Main Thread Error: {e}")
