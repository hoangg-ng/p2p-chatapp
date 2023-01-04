import threading
import struct
from socket import *
from constants import *
from .listenerToServer import *
import json
import random
import time
import os
from datetime import datetime

flagQ = ['name', 0]

class PeerClient(object):

    def __init__(self,username,ui):
        
        self.username = username
        self.chat_list = []
        self.gi = ui
        self.logger = assertLog()
        self._init()

    def _init(self):
        
        listen_socket = socket(AF_INET, SOCK_STREAM) 
        listen_socket.bind((peer_config['PEERIP'], 0))
        ip_listen, port_listen = listen_socket.getsockname()

        print("Update listen socket information")
        self.gi.channel.request_updateListenInfo(self.gi.username, ip_listen, port_listen)
        print('Updated listen info')

        message_socket = socket(AF_INET, SOCK_STREAM)
        message_socket.bind((peer_config['PEERIP'],0))
        ip_mes, port_mes = message_socket.getsockname()

        print('Update message socket information')
        self.gi.channel.request_updateMessageInfo(self.gi.username, ip_mes, port_mes)
        print('Updated message socket info')

        listen_thread = threading.Thread(target=self.listen_server, \
                                        args=(listen_socket, ip_listen, port_listen))
        listen_thread.start()
        get_message_thread = threading.Thread(target=self.get_message, \
                                              args=(message_socket, ip_mes, port_mes))
        get_message_thread.start()

        livenessThread = threading.Thread(target=self.pingToAlive)
        livenessThread.start()

    def pingToAlive(self):
        while True:
            time.sleep(1)
            self.logger.info("Ping to [ {}, {} ]".format(
                self.gi.channel.hostTCP, self.gi.channel.portTCP
            ))
            self.gi.channel.request_updateAliveThread(self.gi.username)

    def packingMessage(self, typeid, username, data):

        return json.dumps({
            'typeid': typeid,
            'username': username,
            'data': data, 
        })

    def unpackingMessage(self, packet):
        try:
            packet = packet.decode('utf-8')
            jsonObject = json.loads(packet)
            return jsonObject.values()
        except Exception as e:
            self.logger.info(e)
            return [-1, '', '']

    #  Init server to listen from other peeers 
    def listen_server(self, listen_socket, ip, port):

        username = self.gi.username
        print("IP: {} - PORT: {}")
        
        host_listen, port_listen = listen_socket.getsockname()
        # self.gi.channel.request_updateListenInfo(username, host_listen, port_listen)
        listen_socket.listen(1)
        self.logger.info("Server is listening on tcp [ {} , {} ] ".format(ip, port))
        
        while 1:
            conn, addr = listen_socket.accept()
            self.logger.info("Connection excepted from {}".format(addr[0]))

            while 1:
                packet = conn.recv(2048)
                if len(packet) == 0:
                    break
                
                code, field1, field2 = self.unpackingMessage(packet)
                field1=self.purge(field1)
                field2 = self.purge(field2)
                self.logger.info("Request ---> Type:{} , Field1:{} , Field2:{}    [ {} , {} ] ".format(code, field1, field2, addr[0], addr[1]))
                
                if code == 0 :

                    # self.broacast_requestConnection(packet)
                    global flagQ
                    flagQ = ['name', 0]
                    self.gi.chatR(field2)         #   Notify the IP address 
                    r = flagQ[1]
                    start_time = 0
                    print(r)
                    while r==0:

                        r = flagQ[1]
                        if start_time > 5:
                            self.resetFlag() 
                            self.gi.onaytext.setText("Incoming Request")
                            break

                        time.sleep(1)
                        start_time = start_time + 1
                        
                    print(r)
                    if r==1:
                        
                        r_packet = self.packingMessage(
                            code,
                            20,
                            'OK',
                        )
                        print("Chat Accepted")
                        # users=packet[26:].decode('utf-8')
                        # print(users)
                        # users=str(users)
                        print("Field 2 in Connection to peer  : {}".format(field2))
                        users=field2.split('\n')[:-1]
                        print("Users in listen server: {}".format(users))
                        for item in users:
                            self.chat_list.append(item)

                        print(self.chat_list)
                        conn.sendall(bytes(r_packet, encoding='utf-8'))
                        self.logger.info("Response ---> Type:{} Status:{} Message: OK    [ {} , {} ]".format(code,20,addr[0],addr[1]))

                    else:
                        
                        r_packet = self.packingMessage(
                            code,
                            40,
                            'REJECTED'
                        )
                        conn.sendall(bytes(r_packet, encoding='utf-8'))
                        self.logger.info("Response ---> Type:{} Status:{} Message: Rejected  [ {} , {} ]".format(code, 40, addr[0],addr[1]))

                    self.resetFlag()
                elif code==1:
                    notification = field1 + ' joined!'
                    self.gi.tb_chatscreen.append(notification)
                    self.chat_list.append(field1)

                elif code == 3:
                    self.chat_list.remove(field1)
                
                elif code == 5:
                    sender, filename, size = field1.split(";;")
                    size = int(size)

                    with conn.makefile('rb') as clientFile:

                        data = clientFile.read(size)
                        with open(filename, 'wb') as f:
                            f.write(data)


            conn.close()
            self.logger.info(" Connection closed [ {} , {} ]".format(ip, port))
        print("listen_server finished")

    #   Listen to other peers to get message
    def get_message(self, message_socket, ip,port):

        try:
            message_socket.listen(1)
            self.logger.info("Server is listening for messages on tcp [ {} , {} ] ".format(ip, port))

            while 1:
                conn, addr = message_socket.accept()
                self.logger.info("Connection excepted from {}".format(addr[0]))
                data = conn.recv(2048)
                
                code, n_username, mess = self.unpackingMessage(data)

                
                mess=self.purge(mess)
                n_username = self.purge(n_username)
                self.logger.info(
                    "Request ---> Type:{} , Field1:{} , Data:{}   [ {} , {} ] ".format(code,n_username,mess, addr[0],addr[1]))
                
                #   NOTIFICATION OF NEW USER
                string=n_username+': '+mess
                self.gi.tb_chatscreen.append(string)

                if code  == 2:
                    self.broadcast_messages(n_username, mess)
               
                conn.close()
                self.logger.info(" Connection closed [ {} , {} ]".format(ip, port))
            print("get_message finished")
        except Exception as e:
            self.logger.info(e)

    def send_message(self,ip,port,packet):
        try:
            ss = socket(AF_INET, SOCK_STREAM)
            ss.connect((ip, port))

            self.logger.info("Connected to [ {} , {} ]".format(ip, port))
            ss.sendall(bytes(packet, encoding='utf-8'))
            self.logger.info("Response ---> Type:{} Username:{} Message: {}  [ {} , {} ]".format(2,self.username,packet,ip,port))
            ss.close()
            self.logger.info(" Connection closed [ {} , {} ]".format(ip, port))
            return True

        except Exception as e:
            print
            self.logger.info(e)
            return False            

    def broadcast_messages(self, sender, message):

        try:
            packet = self.packingMessage(
                4,
                sender, 
                message
            )

            for peer_name in self.chat_list:
                if peer_name != sender:
                    user_infor = self.gi.channel.request_search(self.username, peer_name)[1]
                    port = int(user_infor[0]['messagePort'])
                    ip = user_infor[0]['messageIP']
                    r = self.send_message(ip, port, packet)

                    if r:
                        self.logger.info("Broadcast succsessfully --> [ {}, {} ]".format(ip, port))
        except Exception as e:
            self.logger.error(e)

    def browserFile(self):

        self.gi.browserFiles()

    def sendFile(self):
        try:
            now = datetime.now()
            current_time = now.strftime('%H:%M:%S')
            filename = self.gi.te_file.text()
            name, extension = filename.split('.')
            name = name + '({}-{})'.format(self.username, current_time)

            _filename = name + '.' +  extension
            print(filename)
            for peer in self.chat_list:
                reponse_from_search =  self.gi.channel.request_search(self.username, peer)[1]
                user_infor = reponse_from_search[0]
                listenip = user_infor['listenIP']
                listenport = int(user_infor['listenPort'])

                ss = socket(AF_INET, SOCK_STREAM)
                ss.connect((listenip, listenport))

                file_info = self.username + ';;' + _filename + ';;' + str(os.path.getsize(filename))

                packet = self.packingMessage(
                    5,
                    file_info,
                    ''
                )
                ss.sendall(bytes(packet, encoding='utf-8'))
                with open(filename, 'rb') as f:
                    ss.sendall(f.read())     
                    

                
        except Exception as e:
            self.logger.info(e)
         
    def send_messages(self):

        try:
            print(self.chat_list)
            mess=self.gi.getMessage()
            ms = "Me: " + mess
            self.gi.tb_chatscreen.append(ms)

            packet = self.packingMessage(
                2,
                self.username,
                mess
            )
            for chat_peer in self.chat_list:
                
                reponse_from_search =  self.gi.channel.request_search(self.username, chat_peer)[1]
                user_infor = reponse_from_search[0]

                re=self.send_message(user_infor['messageIP'], int(user_infor['messagePort']), packet)
                if not re:
                    self.chat_list.remove(user_infor['_id'])
                    print("User {} is removed ".format(user_infor['_id']))
        except Exception as e:
            self.logger.info(e)

    def notifyNewuser(self, new_username):
        try:
            packet = self.packingMessage(
                1, 
                new_username, 
                'NEW USER',
            )
            
            print("Chat list existed, ", self.chat_list)
            
            for chat_peer in self.chat_list:

                user_infor = self.gi.channel.request_search(self.username, chat_peer)[1]
                self.logger.info("Request ---> Type: 1 , IP:{} ,Message: New User    [ Destination : {}  ] ".format(new_username, chat_peer))
                re = self.send_message(user_infor['listenIP'], int(user_infor['listenPort']), packet)
                print("Notify user sended: ",packet)
                if not re:
                    self.chat_list.remove(chat_peer)
                    self.logger.info("User {} is removed ".format(chat_peer))
        except Exception as e:
            self.logger.info(e)

    def connect_peer(self, username, ip, port):

        try:
        #   IP, PORT of target
            print(ip, port)
            if not (username in self.chat_list) :
                s = socket(AF_INET, SOCK_STREAM)
                s.connect((str(ip), int(port)))
                self.logger.info("Connected to [ {} , {} ]".format(ip, port))

                #   SEND MESSAGE TO ALL PEERS IN THE PEER #
                string = ''

                string = self.username + '\n'
                #   PACKAGE TYPE:   0   #
                        
                packet = self.packingMessage(
                    0,
                    'CHAT REQUEST',
                    string,
                )
                s.sendall(bytes(packet, encoding='utf-8'))

                #######     CHECK CONNECTION TO PEER    ###################
                self.logger.info(
                    "Response ---> Type:{} , Message: CHAT REQUEST , Username:{}   [ {} , {} ] ".format(0, self.username, ip, port))
                
                received = s.recv(2048)
                print(received)

                code, status, field2 = self.unpackingMessage(received)
                field2=self.purge(field2)

                self.logger.info(
                    "Request ---> Type:{} , Status:{} , Field2:{}   [ {} , {} ] ".format(code,status,field2,ip,port))
                s.close()

                self.logger.info(" Connection closed [ {} , {} ]".format(ip, port))
                if status==20 and field2 == "OK":
                    self.notifyNewuser(self.username)
                    self.chat_list.append(username)
                    print(self.chat_list)
                else:
                    self.logger.info("Request ---> Connection Rejected [ {} , {} ]".format(ip,port))
        except Exception as e:
            self.logger.info(e)

    def getAddress(self):
        try:
            search_name = self.gi.getUsername()
            _, userInfo = self.gi.channel.request_search(self.gi.username, search_name)
            return search_name, userInfo[0]['listenIP'],  userInfo[0]['listenPort']
        except Exception as e:
            self.logger.info(e)

    def resetFlag(self):
        try:
            self.gi.onaytext.setText("Incoming Request")
            self.gi.onayB.setVisible(False)
            self.gi.retB.setVisible(False)
            global flagQ 
            flagQ = ['name', 0]
        except Exception as e:
            self.logger.info(e)

    def purge(self, message):
        return message
    def send_request_to_peer(self):
        try:
            search_name, ip, port = self.getAddress()
            self.connect_peer(search_name, ip, port)
            self.gi.te_username.clear()
        except Exception as e: 
            self.logger.info(e)

    def accept_request(self):
        try: 
            self.gi.onaytext.setText("Incoming Request")
            global flagQ
            flagQ = ['name', 1]
            print(flagQ)
        except Exception as e:
            self.logger.info(e)

    def reject_request(self):
        try:
            self.gi.onaytext.setText("Incoming Request")
            global flagQ
            flagQ = ['name', -1]
        except Exception as e:
            self.logger.info(e)

    def refreshOnline(self):
        # data = self.gi.channel.request_onlineUser(self.gi.username)[1]

        # data_list = [parsed_name.split(";")[0] for parsed_name in data[:len(data) - 1]]
        # if self.gi.username in data_list:
        #     data_list.remove(self.gi.username)
        # listUsers = '\n'.join(data_list)

        try:
            listUsers = self.gi.username + "(me)" + '\n'
            if len(self.chat_list) > 0:
                for _, name in enumerate(self.chat_list):
                    listUsers = listUsers + name + '\n'
            self.gi.textBrowser.setText(listUsers)
        except Exception as e:
            self.logger.info(e)
    
    def logout(self):
        
        try:
            result = self.gi.channel.request_logout(self.gi.username)
            print(result)
            if result[0] == 23:
                self.logger.info(
                    "Response ---> Type:3 Status:{} Message: {} [ {} ]".format(result[0], result[1], self.gi.username))
                
                packet = self.packingMessage(
                    3,
                    self.username, 
                    'LOGOUT'
                )
                for chat_peer in self.chat_list:

                    user_infor = self.gi.channel.request_search(self.username, chat_peer)[1]
                    print(user_infor)
                    re = self.send_message(user_infor[0]['listenIP'], int(user_infor[0]['listenPort']), packet)
                if re:
                    self.gi.onayB.setVisible(False)
                    self.gi.retB.setVisible(False)
                    self.gi.tb_chatscreen.setVisible(False)
                    self.gi.te_message.setVisible(False)
                    self.gi.btn_send.setVisible(False)
                    self.gi.textBrowser.setVisible(False)
                    self.gi.label.setVisible(False)
                    self.gi.label.setVisible(False)
                    # self.gi.te_ip.setVisible(False)
                    # self.gi.label_2.setVisible(False)
                    # self.gi.te_port.setVisible(False)
                    self.gi.btn_connect.setVisible(False)
                    self.gi.btn_refresh.setVisible(False)
                    self.gi.btn_logout.setVisible(False)
                    self.gi.onaytext.setVisible(False)
                    self.gi.onaytext.setVisible(False)
                    self.gi.onayB.setVisible(False)

                    self.gi.logout_message.setVisible(True)

                    self.gi.previousWindow.show()

                    # self.gi.hide()
                return
            else:
                self.logger.info(
                    "Response ---> Type:3 Status:{} Message: {} [ {} ]".format(result[0], result[1], self.gi.username))
        except Exception as e:
            self.logger.info(e)

