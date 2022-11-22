#import everything while you can
from tkinter import Listbox, Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, Variable, messagebox #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading
from turtle import width # for multiple proccess 

DISCONNECT_MESSAGE = "!DISCONNECT"
HEADER = 256
FORMAT = 'utf-8'

class GUI:
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
        self.display_sendfile_button()
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
        self.address_text_widget.insert(0, "172.20.8.80")
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
        listfriend_widget = Listbox(frame, listvariable=var,width = 18, height=24, font=('Serif', 12), selectmode='SINGLE')
        listfriend_widget.pack()
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
        self.client_socket.send(("joined:" + name).encode(FORMAT))
        #Then start create a thread to listen
        self.listen_for_incoming_messages_in_a_thread()



    def initialize_socket(self, remote_ip, remote_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((remote_ip, int(remote_port)))

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()

    #function to recieve msg
    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')
         
            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def update_friend_list(self):
        print('updated')

    def on_enter_key_pressed(self, event):
        self.send_chat()
        #self.clear_text()

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
        print("sent")

    def on_disconnect(self):
        self.client_socket.close()
        self.address_text_widget.config(state = 'normal')
        self.port_text_widget.config(state = 'normal')
        self.name_text_widget.config(state = 'normal')

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)

#the main function
if __name__ == "__main__":
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()

