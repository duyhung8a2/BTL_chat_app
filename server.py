#import socket
#import threading

#HEADER = 64
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
#        msg_length = conn.recv(HEADER).decode(FORMAT)
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
#                send_length += b' ' * (HEADER - len(send_length))
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
#                        send_length += b' ' * (HEADER - len(send_length))
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

HEADER = 64
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
        msg_length = conn.recv(HEADER).decode(FORMAT)
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