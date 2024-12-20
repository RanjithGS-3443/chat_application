import socket
import threading
import tkinter as tk
from tkinter import filedialog
from file_transfer import send_file, receive_file
import os

class ChatClient:
    def __init__(self, host='localhost', port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        
        self.save_directory = "client_received_files"
        os.makedirs(self.save_directory, exist_ok=True)
        
        # GUI Setup
        self.window = tk.Tk()
        self.window.title("Chat Application")
        
        self.chat_frame = tk.Frame(self.window)
        self.chat_frame.pack(padx=10, pady=10)
        
        self.chat_log = tk.Text(self.chat_frame, height=20, width=50)
        self.chat_log.pack()
        
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(padx=10, pady=5)
        
        self.message_input = tk.Entry(self.input_frame, width=40)
        self.message_input.pack(side=tk.LEFT)
        
        self.send_button = tk.Button(self.input_frame, text="Send", 
                                   command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.file_button = tk.Button(self.input_frame, text="Send File", 
                                   command=self.send_file)
        self.file_button.pack(side=tk.LEFT)
        
        # Start receiving thread
        threading.Thread(target=self.receive_messages).start()

    def send_message(self):
        message = self.message_input.get()
        if message:
            self.sock.send('T'.encode())  # T for text message
            self.sock.send(message.encode())
            self.chat_log.insert(tk.END, f"You: {message}\n")
            self.message_input.delete(0, tk.END)

    def send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.sock.send('F'.encode())  # F for file transfer
            send_file(self.sock, file_path)
            self.chat_log.insert(tk.END, 
                f"You sent file: {os.path.basename(file_path)}\n")

    def receive_messages(self):
        while True:
            try:
                msg_type = self.sock.recv(1).decode()
                
                if msg_type == 'T':  # Text message
                    message = self.sock.recv(1024).decode()
                    self.chat_log.insert(tk.END, f"Received: {message}\n")
                
                elif msg_type == 'F':  # File transfer
                    save_path = receive_file(self.sock, self.save_directory)
                    self.chat_log.insert(tk.END, 
                        f"Received file: {os.path.basename(save_path)}\n")
                    
            except Exception as e:
                print(f"Error: {e}")
                self.sock.close()
                break

    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.start() 