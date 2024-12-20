import socket
import threading
import os
from file_transfer import receive_file, send_file

class ChatServer:
    def __init__(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = {}
        self.save_directory = "server_received_files"
        
        # Create directory for received files
        os.makedirs(self.save_directory, exist_ok=True)

    def handle_client(self, client_socket, address):
        while True:
            try:
                # Receive message type
                msg_type = client_socket.recv(1).decode()
                
                if msg_type == 'T':  # Text message
                    message = client_socket.recv(1024).decode()
                    self.broadcast(message, client_socket)
                
                elif msg_type == 'F':  # File transfer
                    # Receive the file
                    save_path = receive_file(client_socket, self.save_directory)
                    
                    # Broadcast file to other clients
                    for client in self.clients:
                        if client != client_socket:
                            client.send('F'.encode())
                            send_file(client, save_path)
                            
            except Exception as e:
                print(f"Error: {e}")
                self.clients.pop(client_socket)
                client_socket.close()
                break

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                client.send('T'.encode())
                client.send(message.encode())

    def start(self):
        print("Server is running...")
        while True:
            client_socket, address = self.server.accept()
            self.clients[client_socket] = address
            thread = threading.Thread(target=self.handle_client, 
                                   args=(client_socket, address))
            thread.start() 