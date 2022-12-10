#import everything while you can
from fileinput import filename
import tkinter
from tkinter import Listbox, Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, Variable, filedialog, messagebox #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading
from turtle import width # for multiple proccess 
import os

DISCONNECT_MESSAGE = "!DISCONNECT"
BUFFER_SIZE = 1024
FORMAT = 'utf-8'
DEFAULT_HOST_IP = socket.gethostbyname(socket.gethostname())
LISTENER_PORT = 19999


class P2P_GUI:
    #class ChatListener(threading.Thread):

    #    def __init__(self, port):
    #        threading.Thread.__init__(self)
    #        self.target_port = port
    #    def run(self):
    #        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #        listen_socket.bind((DEFAULT_HOST_IP, self.target_port))
    #        listen_socket.listen(1)
    #        connection, address = listen_socket.accept()
    #        print("Established connection with: ", address)

    #        while True:

    #            buffer = connection.recv(BUFFER_SIZE)
    #            message = buffer.decode(FORMAT)
    #            is_a_command = False
    #            if is_a_command == False:
    #                self.chat_p2p_transcript_area.insert('end', message + '\n')
    #                self.chat_p2p_transcript_area.yview(END)   
    #            print("Them: ", message)

    #class ChatSender(threading.Thread):

    #    def __init__(self, ip, port):
    #        threading.Thread.__init__(self)
    #        self.target_ip = ip
    #        self.target_port = int(port) 
    #        self.send_socket = None
    #    def run(self):
    #        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #        self.send_socket.connect((self.target_ip, self.target_port))

    #    def send_message(self, message):
    #        self.send_socket.send(message.encode(FORMAT))
    
    client_socket = None
    server_socket = None
    def __init__(self, master, name, own_ip, own_port, ip = None, port = None):
        self.root = master
        self.own_ip = own_ip
        self.own_port = own_port
        self.target_ip = ip
        self.target_port = port
        self.name = name
        
        self.chat_p2p_transcript_area = None
        #self.chat_listenter = None
        #self.chat_sender = None
        self.initialize_gui()
        self.initialize_thread()

    def initialize_gui(self):
        self.set_geometry()
        self.display_p2p_chat_box()
        self.display_chat_entry_box()
        self.display_sendfile_button()

    def set_geometry(self):
        window_width = 600
        window_height = 600

        # get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def display_p2p_chat_box(self):
        frame = Frame(root)
        Label(frame, text='Private Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_p2p_transcript_area = Text(frame, width=58, height=24, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_p2p_transcript_area.yview, orient=VERTICAL)
        self.chat_p2p_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_p2p_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_p2p_transcript_area.pack(side='left')
        scrollbar.pack(side='right', fill='y')
        frame.pack(side = "top", pady = (25, 10))

    def display_chat_entry_box(self):
        frame = Frame(root)
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=50, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left')
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        #frame.place(x = 35, y= 490)
        frame.pack(side = "left", anchor="n", padx = (30, 0))

    def on_enter_key_pressed(self, event):
        message = self.target_name + ":" + self.enter_text_widget.get(1.0, 'end')
        self.chat_sender.send_message(message)
        self.chat_p2p_transcript_area.insert('end', message.decode(FORMAT) + '\n')
        self.chat_p2p_transcript_area.yview(END)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def display_sendfile_button(self):
        frame = Frame(root)
        self.sendfile_button = Button(frame, text = "Send file", width = 10, command = self.on_sendfile).pack(side="left")
        #frame.place(x = 500, y = 512)
        frame.pack(side = "left", anchor="n", padx = (10, 30), pady = (20, 0))

    def on_sendfile(self):
        print('sent')

    def initialize_thread(self):
        #chat_listener = self.ChatListener(self.target_port)
        #chat_listener.start()

        #chat_sender = self.ChatSender(self.target_ip, self.target_port)
        #chat_sender.start()
        #Start create a thread to listen
        
        #Then wait for other friend to connect
        if (self.target_ip != None and self.target_port != None):
            self.initialize_socket(self.target_ip, self.target_port)
            self.client_socket.send(("CONNECTED:" + self.name).encode(FORMAT))
            self.listen_for_private_incoming_messages_in_a_thread()
        else:
            self.listen_server_in_a_thread()
        
    def listen_server_in_a_thread(self):
        l_thread = threading.Thread(target=self.create_listening_server, args=()) 
        l_thread.start()

    def create_listening_server(self):
    
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket using TCP port and ipv4
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(local_ip)
        #local_ip = '127.0.0.1'
        local_port = LISTENER_PORT
        # this will allow you to immediately restart a TCP server
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # this makes the server listen to requests coming from other computers on the network
        self.server_socket.bind((local_ip, local_port))
        print("Listening for incoming messages..")
        self.server_socket.listen(1) #listen for incomming connections
        self.listen_for_private_incoming_messages_in_a_thread()
    
    def listen_for_private_incoming_messages_in_a_thread(self):
        if (self.target_ip == None and self.target_port == None):
            self.client_socket, (ip,port) = self.server_socket.accept()
            print('Connected to ', ip, ':', port)
        
        thread = threading.Thread(target=self.receive_private_message_from_friend, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()

    #function to recieve msg
    def receive_private_message_from_friend(self, so):
        while True:
            buffer = so.recv(BUFFER_SIZE)
            if not buffer:
                break
            message = buffer.decode('utf-8')
            print(message)
            is_a_command = self.process_private_command(so, message)
            
            if is_a_command == False:
                self.chat_p2p_transcript_area.insert('end', message + '\n')
                self.chat_p2p_transcript_area.yview(END)   
        so.close()

    def process_private_command(self, senders_socket, message):
        if 'CONNECTED:' in message:
            #user = message.split(":")[1]
            self.chat_p2p_transcript_area.insert('end', message + '\n')
            self.chat_p2p_transcript_area.yview(END)   
            return True
           
        return False

    def initialize_socket(self, remote_ip, remote_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((remote_ip, int(remote_port)))

    
    def on_enter_key_pressed(self, event):
        self.send_chat()
        self.clear_text()

    def send_chat(self):
        senders_name = self.name + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode(FORMAT)
        self.chat_p2p_transcript_area.insert('end', message.decode(FORMAT) + '\n')
        self.chat_p2p_transcript_area.yview(END)
        #if (self.target_ip == None and self.target_port == None):
        #    self.server_socket.send(message)
        #else:
        print(message)
        self.client_socket.send(message)

        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

if __name__ == "__main__":
    root = Tk()
    p2p_win1 = P2P_GUI(root, 'hung2', DEFAULT_HOST_IP, 9999)
    root.mainloop()
