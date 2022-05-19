import socket
import threading
import sys
import time

s= socket.socket()

mess=[]
files=[]  

def incoming():
    while True:
        data = s.recv(1024)
        data=data.decode()
        if not data:
            break
        d=data[:1]
        if  d== '*':
            rec,f1,f2 = data.split(' ', 2)
            rec = rec.strip('*')
            files.append([rec,f1,f2])
        elif '$' not in data:
            print(data)
        else:
            mess.append(data)
        if exit==True:
            raise SystemExit
        pass
    return

host= socket.gethostname()
port = 9999
s.connect((host, port))
s.send(sys.argv[1].encode())
t = threading.Thread(target=incoming)
t.start()
global exit
exit=False
print("Options: \n 1. Send a message: type \"send\" \n 2. View messages: type \"messages\"\n 3. View history: type \"history\" \n 4. View users: type \"users\"\n 5. Create a new group: type \"group_create\"\n 6. Add a member in group: type \"group_add\"\n 7. Remove a member: type \"group_remove\"\n 8. Send a message to group: type \"group_send\"\n 9. Send File: type \"send_file\"\n 10. View files: type \"files\"\n 11. Options List: type \"help\" \n 12. Exit: type \"exit\"\n")
while(True):
    time.sleep(0.1)
    if(len(mess)>0):
        print("New messages received. Type \"messages\" to check your inbox.")
    
    print("Enter your option: ")
    text = str(input())
    if text=='exit':
        s.send(text.encode())
        exit=True
        s.close()
        raise SystemExit
    elif text=='users':
        s.send(text.encode())
    elif text == 'messages':
        for m in mess:
            print(m)
        mess.clear()

    elif text=="send_file":
        print("Enter the username of the person you want to send the file to:")
        username = str(input())
        text = "*"+username+ " "
        print("Enter the file name:")
        filename = str(input())
        file = open(filename, "r")
        text += filename + " " + file.read()
        s.send(text.encode())
        file.close()
    elif text=="files":
        for f in files:
            print("Do you want to download the file "+f[1]+" from "+f[0]+"?")
            option=str(input())
            if option=="yes":
                f_dir="received_files/"+f[1]
                file=open(f_dir, "w")
                file.write(f[2])
                file.close()
                print("File "+f[1]+" downloaded from "+f[0]+".")
            elif option=="no":
                pass
        files.clear()
    elif text=='history':
        s.send(text.encode())
    elif text == 'send':
        print("Enter the username of the person you want to send a message to:")
        username = str(input())
        text = "#" + username + " "
        print("Enter the message you want to send:")
        msg=str(input())
        text += msg
        s.send(text.encode())

    elif text =="my_groups":
        s.send(text.encode())

    elif text == "group_create":
        print("Enter the name of the group you want to create:")
        group_name = str(input())
        text = "@" + group_name+" "+sys.argv[1]
        s.send(text.encode())
        
    elif text == "group_add":
        print("Enter the name of the group you want to add a user to:")
        group_name = str(input())
        text = "!"+sys.argv[1]+" " + group_name + " "
        print("Enter the username that you want to add:")
        username = str(input())
        while username != "0":
            text += username + " "
            print("Press 0 to exit.")
            print("Enter the username that you want to add:")
            username = str(input())
        s.send(text.encode())

    elif text == "group_remove":
        print("Enter the name of the group you want to remove a user from:")
        group_name = str(input())
        print("Enter the username that you want to remove:")
        username = str(input())
        text = "-" +sys.argv[1] + " " + group_name + " " + username
        s.send(text.encode())

    elif text == "group_send":
        print("Enter the group name:")
        group = str(input())
        text = ">" + group + " "
        print("Enter the message you want to send:")
        msg=str(input())
        text += msg
        s.send(text.encode())

    elif text=='help':
        print("Options: \n 1. Send a message: type \"send\" \n 2. View messages: type \"messages\"\n 3. View history: type \"history\" \n 3. View users: type \"users\"\n 5. Create a new group: type \"group_create\"\n 6. Add a member in group: type \"group_add\"\n 7. Remove a member: type \"group_remove\"\n 8. Send a message to group: type \"group_send\"\n 9. Send File: type \"send_file\"\n 10. View files: type \"files\"\n 11. Options List: type \"help\" \n 12. Exit: type \"exit\"\n")
    else:
        print("Invalid option!")
        print("Type \"help\" for options")
s.close()