'''
#import socket
#import threading

#BUFFER_SIZE = 64
#PORT = 9999
#hostname = socket.gethostname()
#SERVER = socket.gethostbyname(hostname)
#ADDR = (SERVER, PORT)
#FORMAT = 'utf-8'
#DISCONNECT_MESSAGE = "!DISCONNECT"

#server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.bind(ADDR)
#friend_list = []
#socket_list = []

#def prefix(pre, word):
#    if word.startswith(pre):
#        return True, word[len(pre):]
#    else:
#        return False, None

#def handle_client(conn, addr):
#    global friend_list, socket_list
#    print(f"[NEW CONNECTION] {addr} connected.")

#    connected = True
#    while connected:
#        msg_length = conn.recv(BUFFER_SIZE).decode(FORMAT)
#        if msg_length:
            
#            msg_length = int(msg_length)
#            msg = conn.recv(msg_length).decode(FORMAT)
#            if msg == DISCONNECT_MESSAGE:
#                connected = False

#            print(f"[{addr}] {msg}")
#            choose, word = prefix("USERNAME: ", msg)
#            if choose:
#                friend_list += [[word, addr]]
#                name = "LIST_FRIEND:"
#                for i in friend_list:
#                     name += " " + str(i[0])
#                message = name.encode(FORMAT)
#                msg_length = len(message)
#                send_length = str(msg_length).encode(FORMAT)
#                send_length += b' ' * (BUFFER_SIZE - len(send_length))
#                for lst in socket_list:
#                    lst.send(send_length)
#                    lst.send(message)
#            else:
#                choose, word = prefix("NAME: ", msg)
#                for i in friend_list:
#                    if (i[0] == word):
#                        message = str("IP: " + str(i[1][0]) + " PORT: " + str(i[1][1])).encode(FORMAT)
#                        msg_length = len(message)
#                        send_length = str(msg_length).encode(FORMAT)
#                        send_length += b' ' * (BUFFER_SIZE - len(send_length))
#                        conn.send(send_length)
#                        conn.send(message)
#                        break
#            print(friend_list)
#    conn.close()


#def start():
#    global socket_list
#    server.listen()
#    print(f"[LISTENING] Server is listening on {SERVER}")
#    while True:
#        conn, addr = server.accept()
#        socket_list += [conn]
#        thread = threading.Thread(target=handle_client, args=(conn, addr))
#        thread.start()
#        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


#print("[STARTING] server is starting...")
#start()


import socket
import threading

BUFFER_SIZE = 64
PORT = 9999
hostname = socket.gethostname()
SERVER = socket.gethostbyname(hostname)
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
friend_list = []
socket_list = []

def prefix(pre, word):
    if word.startswith(pre):
        return True, word[len(pre):]
    else:
        return False, None

def handle_client(conn, addr):
    global friend_list, socket_list
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(BUFFER_SIZE).decode(FORMAT)
        if msg_length:
            
            
            msg = conn.recv(512).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            choose, word = prefix("USERNAME: ", msg)
            if choose:
                friend_list += [[word, addr]]
                name = "LIST_FRIEND:"
                for i in friend_list:
                     name += " " + str(i[0])
                message = name.encode(FORMAT)
                
                for lst in socket_list:
                    
                    lst.send(message)
            else:
                choose, word = prefix("NAME: ", msg)
                for i in friend_list:
                    if (i[0] == word):
                        message = str("IP: " + str(i[1][0]) + " PORT: " + str(i[1][1])).encode(FORMAT)
                        
                        conn.send(message)
                        break
            print(friend_list)
    conn.close()


def start():
    global socket_list
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        socket_list += [conn]
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()

'''

#imports
from pickle import TRUE
import socket 
import threading

FORMAT = 'utf-8'
BUFFER_SIZE = 1024

class ChatServer:
    
    clients_list = []
    friends_list = []

    last_received_message = ""

    def __init__(self):
        self.server_socket = None
        self.create_listening_server()
    #listen for incoming connection
    def create_listening_server(self):
    
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket using TCP port and ipv4
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(local_ip)
        #local_ip = '127.0.0.1'
        local_port = 9999
        # this will allow you to immediately restart a TCP server
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # this makes the server listen to requests coming from other computers on the network
        self.server_socket.bind((local_ip, local_port))
        print("Listening for incoming messages..")
        self.server_socket.listen(5) #listen for incomming connections / max 5 clients
        self.receive_messages_in_a_new_thread()
    

            

    #fun to receive new msgs
    def receive_messages(self, so):
        while True:
            incoming_buffer = so.recv(BUFFER_SIZE) #initialize the buffer
            if not incoming_buffer:
                
                break

            #butchering message
            message = incoming_buffer.decode('utf-8')
            print(message)
            is_a_command = self.process_command(so, message)


            # If not command,broadcast
            if (is_a_command == False):
                self.last_received_message = message
                print(self.last_received_message)
                self.broadcast_to_all_clients(so)  # send to all clients
        so.close()

    def process_command(self, senders_socket, message):
        if 'CONNECTED:' in message:
            user = message.split(":")[1]
            
            for client in self.clients_list:
                socket, (ip, port) = client
                if socket is senders_socket:
                    # Update friend list
                    self.friends_list.append((user, client))
                    print(self.friends_list)
            friendlist_message = ("FRIEND_LIST:" + self.return_friends_list())
            for client in self.clients_list:
                socket, (ip, port) = client
                socket.send(friendlist_message.encode(FORMAT))
            return True
        if "REQUEST_ADDR:" in message:
            metadata = message.split(":")[1]
            sender, receiver, listen_at_port = metadata.split(",")
            # find it in friend list
            for friend1 in self.friends_list:
                for friend2 in self.friends_list:
                    if sender == friend1[0] and receiver == friend2[0]:
                        socket1, (ip1, port1) = friend1[1]
                        socket2, (ip2, port2) = friend2[1]
                        # send back specific user request its ip and port with:
                        message = "REQUEST_ADDR_FROM:" + "IP{},PORT{}".format(ip1, listen_at_port)
                        print("reply:" + message)
                        socket2.send(message.encode(FORMAT))
            return True
            
        return False

    #broadcast the message to all clients 
    def broadcast_to_all_clients(self, senders_socket):
        for client in self.clients_list:
            socket, (ip, port) = client
            if socket is not senders_socket:
                socket.sendall(self.last_received_message.encode('utf-8'))

    def receive_messages_in_a_new_thread(self):
        while True:
            client = so, (ip, port) = self.server_socket.accept()
            self.add_to_clients_list(client)
            
            print('Connected to ', ip, ':', str(port))
            t = threading.Thread(target=self.receive_messages, args=(so,))
            t.start()
    #add a new client 
    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)
            self.clients_list

    def return_friends_list(self):
        friend_string = ""
        for friend in self.friends_list:
            friend_string += friend[0] + ","
        return friend_string[:-1]

if __name__ == "__main__":
    ChatServer()
