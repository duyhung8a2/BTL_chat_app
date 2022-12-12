#import everything while you can
from fileinput import filename
import tkinter
from tkinter import Listbox, Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, Variable, filedialog, messagebox #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading
from turtle import width # for multiple proccess 
import os
import tqdm

DISCONNECT_MESSAGE = "!DISCONNECT"
BUFFER_SIZE = 1024
FORMAT = 'utf-8'
DEFAULT_HOST_IP = socket.gethostbyname(socket.gethostname())
LISTENER_PORT = 19999

class P2PGUIClient:
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
        self.filename = None
        self.filesize = 0
        self.isFileTransfering = False
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
        frame = Frame(self.root)
        Label(frame, text='Private Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_p2p_transcript_area = Text(frame, width=58, height=24, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_p2p_transcript_area.yview, orient=VERTICAL)
        self.chat_p2p_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_p2p_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_p2p_transcript_area.pack(side='left')
        scrollbar.pack(side='right', fill='y')
        frame.pack(side = "top", pady = (25, 10))

    def display_chat_entry_box(self):
        frame = Frame(self.root)
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
        frame = Frame(self.root)
        self.sendfile_button = Button(frame, text = "Send file", width = 10, command = self.on_sendfile).pack(side="left")
        #frame.place(x = 500, y = 512)
        frame.pack(side = "left", anchor="n", padx = (10, 30), pady = (20, 0))

    def on_sendfile(self):
        print('sent')

    def initialize_thread(self):
        #If this is a user that receive request connect, connect to user who request connect
        #Else start a thread to listen to connection made by receive user
        if (self.target_ip != None and self.target_port != None):
            self.initialize_socket(self.target_ip, self.target_port)
            self.client_socket.send(("CONNECTED:" + self.name).encode(FORMAT))
            self.listen_for_private_incoming_messages_in_a_thread()
        else:
            self.listen_server_in_a_thread()
        
    def listen_server_in_a_thread(self):
        #Create a thread to listen to connection
        l_thread = threading.Thread(target=self.create_listening_server, args=()) 
        l_thread.start()

    def create_listening_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket using TCP port and ipv4
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(local_ip)
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
        so = self.client_socket

        thread = threading.Thread(target=self.receive_private_message_from_friend, args=(so,)) # Create a thread for the send and receive in same time 
        thread.start()

    #function to recieve msg
    def receive_private_message_from_friend(self, so):
        while True:
            if self.isFileTransfering == True:
                with open(self.filename, "wb") as f:
                    while True:
                        # read 1024 bytes from the socket (receive)
                        bytes_read = self.client_socket.recv(BUFFER_SIZE)
                        if not bytes_read:    
                            # nothing is received
                            # file transmitting is done

                            self.isFileTransfering = False
                            self.filename = None
                            self.filesize = None
                            break
                        # write to the file the bytes we just received
                        f.write(bytes_read)
                    f.close()


            else:
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
            reply = "CONNECTED_WITH:" + self.name 
            self.client_socket.send(reply.encode(FORMAT))
            self.chat_p2p_transcript_area.insert('end', message + '\n')
            self.chat_p2p_transcript_area.yview(END)   
            return True
        if 'SEND_FILE:' in message:
            self.isFileTransfering = True
            self.filename, self.filesize = message.split(':')[1].split(',')
            self.filesize = int(self.filesize)
            sendfile_message = (f"Received file {self.filename} at default folder")
            self.chat_p2p_transcript_area.insert('end', sendfile_message + '\n')
            self.chat_p2p_transcript_area.yview(END)
            return True

        return False

    def initialize_socket(self, remote_ip, remote_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    def on_sendfile(self):
        global file_path
        #filename = filedialog.askopenfilename(initialdir = os.getcwd(),
        #                                      title = 'Select Image File',
        #                                      filetype = ('all files', '*.*'))
        filepath = filedialog.askopenfilename()
        print(filepath)
        filesize = os.path.getsize(filepath)
        print(filesize)
        filename = os.path.basename(filepath).split('/')[-1]
        print (filename)
        #say that we will send file
        self.client_socket.send(f"SEND_FILE:{filename},{filesize}".encode(FORMAT))
        #notify that file is sending
        sendfile_message = (f"Sended file {filename} to opponent")
        self.chat_p2p_transcript_area.insert('end', sendfile_message + '\n')
        self.chat_p2p_transcript_area.yview(END)

        # start sending the file
        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filepath, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                self.client_socket.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        print("\nFinished")
        
    #def on_close_window(self):
    #    if messagebox.askokcancel("Quit", "Do you want to quit"):
    #        self.root.destroy()
    #        if (self.client_socket != None):
    #            self.client_socket.close()
    #        exit(0)

class GUIClient:
    client_socket = None
    last_receive_message = None
    

    def __init__(self, master):
        self.root = master
        self.address_text_widget = None
        self.port_text_widget = None
        self.connect_button = None
        self.sendfile_button = None
        self.listfriend_widget = None
        self.chat_transcript_area = None
        self.list_friends = ['You']
        self.initialize_gui()

    def initialize_gui(self): #GUI initializer
        self.root.title("Just a demo")
        self.root.resizable(0, 0)
        self.set_geometry()
        self.display_address_box()
        self.display_port_box()
        self.display_connect_button()
        self.display_name_box()
        #self.display_sendfile_button()
        self.display_disconnect_button()
        self.display_online_list()
        self.display_chat_box()
        self.display_chat_entry_box()

    def set_geometry(self):
        window_width = 800
        window_height = 600

        # get the screen dimension
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def display_address_box(self):
        frame = Frame()
        Label(frame, text = "Address:", font=("Serif", 12)).pack(side = "left", anchor = "w")
        self.address_text_widget = Entry(frame, width = 20, font = ("Serif", 12))
        self.address_text_widget.insert(0, DEFAULT_HOST_IP)
        self.address_text_widget.pack(side = "top")
        #self.address_text_widget.bind('<Return>', self.on_address_entered)
        #frame.pack(side = "left",anchor="nw", padx = 30, pady = 30)
        frame.place(x = 30, y = 30)

    def display_port_box(self):
        frame = Frame()
        Label(frame, text = "Port:", font=("Serif", 12)).pack(side = "left", anchor = "w")
        self.port_text_widget = Entry(frame, width = 12, font = ("Serif", 12))
        self.port_text_widget.insert(0, "9999")
        self.port_text_widget.pack(side = "top")
        #self.address_text_widget.bind('<Return>', self.on_port_entered)
        #frame.pack(side = "left", anchor="nw", padx = 30, pady = 30)
        frame.place(x = 300, y = 30)

    def display_name_box(self):
        frame = Frame()
        Label(frame, text = "Name:", font=("Serif", 12)).pack(side = "left", anchor = "w")
        self.name_text_widget = Entry(frame, width = 20, font = ("Serif", 12))
        self.name_text_widget.insert(0, "hung")
        self.name_text_widget.pack(side = "top")
        #frame.pack(side = "bottom", anchor="sw", padx = 30, pady = 80)
        frame.place(x = 47, y = 80)

    def display_connect_button(self):
        frame = Frame()
        self.connect_button = Button(frame, text = "Connect", width = 10, command = self.on_connect).pack(side="left")
        frame.place(x = 480, y = 28)

    def display_sendfile_button(self):
        frame = Frame()
        self.sendfile_button = Button(frame, text = "Send file", width = 15, command = self.on_sendfile).pack(side="left")
        frame.place(x = 338, y = 78)

    def display_disconnect_button(self):
        frame = Frame()
        self.disconnect_button = Button(frame, text = "Disconnect", width = 10, command = self.on_disconnect).pack(side="left")
        frame.place(x = 480, y = 78)

    def display_online_list(self):
        #first create a var that hold list of friends
        friends = self.list_friends
        var = Variable(value = friends)
        frame = Frame()
        #select single for 1 line, EXTENDED for multiple line
        Label(frame, text = "Friends online:", font=("Serif", 12)).pack(side = "top", anchor = "w")
        self.listfriend_widget = Listbox(frame, listvariable=var,width = 18, height=24, font=('Serif', 12), selectmode='SINGLE')
        self.listfriend_widget.bind('<<ListboxSelect>>', self.on_friend_selected)
        self.listfriend_widget.pack()
        frame.place(x = 600, y = 78)

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=58, height=18, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left')
        scrollbar.pack(side='right', fill='y')
        frame.place(x = 35, y = 120)

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=58, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left')
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.place(x = 35, y= 480)

    def check_valid_ip(self, ip):
        try: socket.inet_aton(ip)
        except socket.error:
            return False

    def check_valid_port(self, port):
        return port.isnumeric()

    def on_connect(self):
        address_ip = self.address_text_widget.get()
        address_port = self.port_text_widget.get()
        name = self.name_text_widget.get()
        if(len(address_ip) == 0 or self.check_valid_ip(address_ip) == False):
            messagebox.showerror("Fill all info", "Please fill address field correctly")
            return
        elif(len(address_port) == 0 or self.check_valid_port(address_port) == False):
            messagebox.showerror("Fill all info", "Please fill port field correctly")
            return
        elif(len(name) == 0):
            messagebox.showerror("Fill all info", "Please fill name field correctly")
            return

        #Disable all input after connect, prevent little shit change it
        self.address_text_widget.config(state = 'disabled')
        self.port_text_widget.config(state = 'disabled')
        self.name_text_widget.config(state = 'disabled')
        #After receive info about ip and port, we handshake our server
        self.initialize_socket(address_ip, address_port)
        #Then we send it greeting message
        self.client_socket.send(("CONNECTED:" + name).encode(FORMAT))
        #Then start create a thread to listen
        self.listen_for_incoming_messages_in_a_thread()



    def initialize_socket(self, remote_ip, remote_port):
        self.client_socket = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((remote_ip, int(remote_port)))

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()

    #function to recieve msg
    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(BUFFER_SIZE)
            if not buffer:
                break
            message = buffer.decode('utf-8')
            print(message)
            is_a_command = self.process_command(so, message)
            
            if is_a_command == False:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)   
        so.close()

    def process_command(self, so, message):
        if "FRIEND_LIST" in message:
            friend_string = message.split(":")[1]
            if friend_string == '':
                return True
            new_list_friend = friend_string.split(",")
            # Check if our name in it
            new_list_friend.remove(self.name_text_widget.get())

            self.list_friends = ['You'] + new_list_friend
            self.display_online_list()
            return True
              
        if "joined" in message:
            user = message.split(":")[1]
            message = user + " has joined"
            self.chat_transcript_area.insert('end', message + '\n')
            self.chat_transcript_area.yview(END)

        if "REQUEST_ADDR_FROM:" in message:
            own_ip = self.address_text_widget.get()
            own_port = self.port_text_widget.get()
            own_name = self.name_text_widget.get()
            addr = message.split(":")[1].split(",")
            ip = addr[0]
            port = addr[1]
            #print(addr, ip[2:], port[4:])
            self.start_p2p_window(own_name, own_ip, own_port, ip[2:], port[4:])
            return True

        return False

    def start_p2p_window(self,own_name, own_ip, own_port, ip = None, port = None):

        p2p_window = tkinter.Toplevel(self.root)
        p2p_gui = P2PGUIClient(p2p_window, own_name, own_ip, own_port, ip, port)
        #p2p_window.protocol("WM_DELETE_WINDOW", p2p_gui.on_close_window)
        



    def update_friend_list(self):
        print('updated')

    def on_enter_key_pressed(self, event):
        self.send_chat()
        self.clear_text()

    def send_chat(self):
        senders_name = self.name_text_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode(FORMAT)
        self.chat_transcript_area.insert('end', message.decode(FORMAT) + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def on_sendfile(self):
        #global filename
        #filename = filedialog.askopenfilename(initialdir = os.getcwd(),
        #                                      title = 'Select Image File',
        #                                      filetype = ('all files', '*.*'))

        #file = open(filename, "rb")
        #file_data = file.read(BUFFER_SIZE - len('SENDFILE:'.encode(FORMAT)))
        #self.client_socket.send(('SENDFILE:' + file_data).encode(FORMAT))
        pass


    def on_disconnect(self):
        self.client_socket.close()
        self.address_text_widget.config(state = 'normal')
        self.port_text_widget.config(state = 'normal')
        self.name_text_widget.config(state = 'normal')

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit"):
            self.root.destroy()
            if (self.client_socket != None):
                self.client_socket.close()
            exit(0)

    def on_friend_selected(self, event):
        senders_name = self.name_text_widget.get().strip()
        if (self.client_socket == None):
            return
        #get selected incide
        selected_indice = self.listfriend_widget.curselection()
        if selected_indice[0] == 0:
            return
        #get selected friend
        selected_friend = self.listfriend_widget.get(selected_indice)
        if(senders_name != selected_friend):
            own_ip = self.address_text_widget.get()
            own_port = self.port_text_widget.get()
            own_name = self.name_text_widget.get()
            # command REQUEST_ADDR:
            message = 'REQUEST_ADDR:' + senders_name + ',' + selected_friend + ',' + str(LISTENER_PORT)
            self.client_socket.send(message.encode(FORMAT))
            # then open P2P_GUI
            self.start_p2p_window(own_name, own_ip, own_port)


#the main function
if __name__ == "__main__":
    root = Tk()
    gui = GUIClient(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()


