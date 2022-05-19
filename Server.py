import socket
import threading
import sys
import datetime

global clients
clients = []
groups=[]
lock=threading.Lock()

buff=[]

class Group:
    def __init__(self,name, owner):
        self.name=name
        self.owner = owner
        self.members=[]

    def set_owner(self, owner):
        self.owner=owner

    def add_member(self,member):
        self.members.append(member)

    def remove_member(self,member):
        self.members.remove(member)
    
    def get_members(self):
        return self.members

   

class Client:
    def __init__(self, name, socket, message_history, status):
        self.name = name
        self.socket = socket
        self.message_history = list(message_history)
        self.groups=[]
        self.status = status
        self.last_online = datetime.datetime.now()

    def set_last_online(self, timestamp):
        self.last_online = timestamp

    def get_last_online(self):
        return self.last_online

    def save_message(self, sender, message,time):
            #save messages to message_history sorted by name
            self.message_history.append((sender, message,time))
            self.message_history.sort(key=lambda x: x[2])
            
    def set_status(self,status):
            self.status = status
            
    def add_group(self,group):
        self.groups.append(group)

    def remove_group(self,group):
        self.groups.remove(group)
        
def toDo():
    try:
        while True:
            
            if len(buff)>0:
                for i in range(len(buff)):
                    if buff[i][0].status==1:
                        buff[i][0].socket.send(str("$"+buff[i][1]+" : "+buff[i][2]+buff[i][3]).encode())
                        print(buff)
                        lock.acquire()
                        buff.pop(i)
                        lock.release()
                    break
    except KeyboardInterrupt:
        print("\nClosing server...")
        sys.exit()

def client_serv(c,count):
    t = threading.Thread(target=toDo)
    t.start()
    try:
        while True:
            data=c.recv(1024).decode()
            names=[]
            if data == "users":
                for client in clients:
                    if client.status==1:
                        names.append(client.name)
                c.send(str(names).encode())
            elif data == "history":
                c.send(str(clients[count].message_history).encode())
            elif data == "my_groups":
                c.send(str(clients[count].groups).encode())
            elif data == "exit":
                lock.acquire()
                clients[count].status=0
                lock.release()
                print("Client "+clients[count].name+" is offline.")
                print("Client status is ", clients[count].status)
                clients[count].set_last_online(datetime.datetime.now())
                break
            else:
                print(data)
                
                rec,msg=data.split(' ',1)
                ch=data[:1]
                print(ch)
                if ch == '#':
                    receiver_name=rec.strip('#')
                    flag=0
                    for client in clients:
                        if client.name==receiver_name:
                            flag=1
                            client.save_message(clients[count].name,msg, str(datetime.datetime.now()))
                            clients[count].save_message(clients[count].name,msg, str(datetime.datetime.now()))
                            if(client.status==1):
                                print("status =", client.status)
                                client.socket.send(str("$"+clients[count].name + ": " + msg + " " + " " + str(datetime.datetime.now())).encode())
                            else:
                                c.send(str(client.name+" is offline but your message will be forwarded when he is online").encode())
                                c.send(str(client.name + " was last online " + str(client.last_online)).encode())
                                buff.append([client,clients[count].name,msg,str(datetime.datetime.now())])
                            break
                    if flag==0:
                        print("User not found")
                        c.send(str("User not found. Message not delivered").encode())
                elif ch == '*':
                    receiver_name,file_name,file_data=data.split(' ',2)
                    receiver_name=receiver_name.strip('*')
                    flag=0
                    for client in clients:
                        if client.name==receiver_name:
                            flag=1
                            if(client.status==1):
                                print("status =", client.status)
                                client.socket.send(str("*"+clients[count].name+" "+ file_name+" "+file_data).encode())
                            else:
                                c.send(str(client.name+" is offline. Send file again when client is online").encode())
                                c.send(str(client.name + " was last online " + str(client.last_online)).encode())
                            break
                    if flag==0:
                        print("User not found")
                        c.send(str("User not found. Message not delivered").encode())

                    #ale test.txt test test test

                elif ch == '>':
                    group_name=rec.strip('>')
                    flag=0
                    for group in groups:
                        if group.name==group_name:
                            flag=1
                            flagc=0
                            print(group.members)
                            if(clients[count].name not in group.members):
                                c.send(str("You are not a member of this group. Message not sent.").encode())
                                break
                            for member in group.members:
                                for client in clients:
                                    if client.name==member:
                                        flagc=1
                                        client.save_message(clients[count].name,"From group \'" + group_name + "\' " + msg, str(datetime.datetime.now()))
                                        if(client.status==1):
                                            print("status =", client.status)
                                            client.socket.send(str("From group \'"+group_name+"\' $"+clients[count].name + ": " + msg + " " + " " + str(datetime.datetime.now())).encode());
                                        else:
                                            c.send(str(client.name+" is offline but your group message will be forwarded when he is online").encode())
                                            c.send(str(client.name + " was last online " + str(client.last_online)).encode())
                                            buff.append([client,clients[count].name,"From group \'" + group_name + "\' " + msg ,str(datetime.datetime.now())])
                                        break
                                if flagc==0:
                                    print("User",member,"not found")
                                    c.send(str("User not found. Message not delivered").encode())
                            break
                    if flag==0:
                        print("Group not found")
                        c.send(str("Group not found. Message not delivered").encode())

                
                #@ok Ale
                elif ch == '@':
                    group_name,owner_name=data.split(' ',1)
                    group_name = group_name.strip('@')
                    
                    print('group_name',group_name)
                    print('owner_name',owner_name)

                    lock.acquire()
                    group=Group(group_name,owner_name)
                    for client in clients:
                        if client.name==owner_name:                        
                            client.add_group(group_name)
                            group.add_member(owner_name)
                            break
                    groups.append(group)
                    for group in groups:
                        print(group.name)
                    lock.release()

                elif ch == '!':
                    list=data.split(' ')

                    list[0]=list[0].strip('!')
                    index=-1
                    for i in range(0,len(groups)):
                        if list[1]==groups[i].name:
                            index=i
                            break
                    if index!=-1:
                        if list[0]==groups[index].owner:
                            for i in range(2,len(list)):
                                group.add_member(list[i])
                                for client in clients:
                                    if client.name==list[i]:
                                        client.add_group(group_name)
                        else:
                            c.send(str("You are not the owner of the group").encode())
                    else:
                        c.send(str("Group not found").encode())

                elif ch == '-':
                    list=data.split(' ')
                    list[0]=list[0].strip('-')
                    index=-1
                    for i in range(0,len(groups)):
                        if list[1] == groups[i].name:
                            index=i
                            break
                    if index!=-1:
                        if list[0]==groups[index].owner:
                            group.remove_member(list[2])
                            for client in clients:
                                if client.name == list[2]:
                                    client.remove_group(list[1])
                        else:
                            c.send(str("You are not the owner of the group").encode())
                    else:
                        c.send(str("Group not found").encode())
    except KeyboardInterrupt:
        pass
 # !alex1 group alex2 alex3 alex4

if sys.argv[1]=="-ipv4":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
elif sys.argv[1]=="-ipv6":
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
host = socket.gethostname()
port = sys.argv[2]
count=0
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, int(port)))
s.listen()
try:
    while True:
        c, addr = s.accept()
        print ('connection from' ,addr)
        name=c.recv(1024)
        name=name.decode()
        print(name)
        cl=Client(name,c,[],1)
        flag = 0
        for i in clients:
            if i.name == name:
                i.socket=c
                i.status=1
                print("Client "+name+" is online")
                flag = 1
                break

        if flag == 0:
            clients.append(cl)
            count+=1

        t = threading.Thread(target=client_serv, args=(c,count-1))
        t.start()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Exiting...")
    s.close()
    for i in clients:
        i.socket.close()
    sys.exit()