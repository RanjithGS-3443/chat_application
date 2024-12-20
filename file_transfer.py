import os
import struct

def send_file(sock, file_path):
    # Get file size and name
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    
    # Send file name length and file name
    name_length = len(file_name)
    sock.send(struct.pack('!I', name_length))
    sock.send(file_name.encode())
    
    # Send file size
    sock.send(struct.pack('!Q', file_size))
    
    # Send file data in chunks
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sock.send(data)

def receive_file(sock, save_directory):
    # Receive file name length and file name
    name_length = struct.unpack('!I', sock.recv(4))[0]
    file_name = sock.recv(name_length).decode()
    
    # Receive file size
    file_size = struct.unpack('!Q', sock.recv(8))[0]
    
    # Create save path
    save_path = os.path.join(save_directory, file_name)
    
    # Receive and save file data
    received_size = 0
    with open(save_path, 'wb') as f:
        while received_size < file_size:
            data = sock.recv(min(4096, file_size - received_size))
            if not data:
                break
            f.write(data)
            received_size += len(data)
    
    return save_path 