from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

import threading
import time
import json
from socket import *
from constants import *

"""
    Sending packet:
        Dump string into json object
        Encode json object with utf8
        Send encoded object through the socket
"""
class Peer2ServerListener(object):

    def __init__(self):
        self.logger = assertLog()
        self.hostTCP = server_config['SERVERIP']
        self.portTCP = server_config['TCP_SERVER_PORT']

    def connect_server(self):
        try:
            self.clientSocket = socket(AF_INET, SOCK_STREAM)
            self.clientSocket.connect((self.hostTCP, self.portTCP))
        
        except Exception as e: 
            self.logger.info("Cannot connect to the server")
            self.logger.info(e)

    def closeConnection(self):
        self.socket.close()

    #   TYPE:0; USERNAME, PASSWORD, 15 --- REGISTER
    def request_register(self, username, password):
        try:
            
            packet = json.dumps({
                'type': 0,
                'field1': username,
                'field2': password,
                'key':  KEY ,
            })

            result = self.send_packet(packet)
            # self.request_updateAliveThread(username)

            return result
        except Exception as e:
            print("Cannot send package to request register!")
            print(e)

    #   TYPE:1; USERNAME, PASSWORD; 15 --- LOGIN
    def request_login(self, username, password):
        try:

            packet = json.dumps({
                'type': 1,
                'field1': username,
                'field2': password,
                'key': KEY,
            })

            result = self.send_packet(packet)
            # self.request_updateAliveThread(username)

            return result

        except Exception as e:
            print("Cannot send package to request login!")
            print(e)

    #   TYPE:2  ;   USERNAME    ;   SEARCH_NAME ;   KEY 
    def request_search(self, username, search_name):
        try:

            packet = json.dumps({
                'type': 2,
                'field1': username,
                'field2': search_name,
                'key':  KEY,
            })

            result = self.send_packet(packet)
            # self.request_updateAliveThread(username)

            return result 
         
        except Exception as e:
            print(e)

    #   TYPE:3 ; USERNAME; LOGOUT, 15 --- LOGOUT 
    def request_logout(self, username):     
        try:

            packet = json.dumps({
                'type': 3,
                'field1': username,
                'field2': 'LOGOUT',
                'key': KEY, 
            })

            result = self.send_packet(packet)
            return  result 

        except Exception as e:
            print("Cannot send package to request logout")
            print(e)

    #   TYPE = 4; USERNAME, ALLUSER, 15     --- SEARCH ALL ONLINE USER
    def request_onlineUser(self, username):
        try:

            packet = json.dumps({
                'type': 4,
                'field1': username,
                'field2':   'ALLUSER',
                'key': KEY, 
            }) 

            result = self.send_packet(packet)
            # self.request_updateAliveThread(username)

            return  result 

        except Exception as e:
            print("Cannot get online peers")
            print(e)
    
    #   TYPE = 5; USERNAME; ALIVE, 15 --- UPDATE ALIVE
    def request_updateAliveThread(self, username):
        try:
            packet = json.dumps({
                'type': 5,
                'field1':   username,
                'field2':   'UPDATEALIVE',
                'key': KEY,
            })
            result = self.send_packet(packet)

            return result
        
        except Exception as e:
            print("Cannot send package to request alive")
            print(e)
    
    def request_updateListenInfo(self, username,
                            listenIP, listenPort):

        try:
            connection_info = listenIP + ';' + str(listenPort)
            print(connection_info)      # DELETE
            packet = json.dumps({
                'type': 6,
                'field1': username,
                'field2': connection_info,
                'key': KEY,
            }) 

            result = self.send_packet(packet=packet)
            return result
        except Exception as e:
            print("Cannot request update listen information to server")
    
    def request_updateMessageInfo(self, username, messageIP, messagePort) :

        try:
            
            connection_info = messageIP + ';' + str(messagePort)
            print(connection_info)
            packet = json.dumps({
                'type': 7,
                'field1': username,
                'field2': connection_info,
                'key': KEY,
            })

            result = self.send_packet(packet=packet)
            return result
        except Exception as e:
            print("Cannot request update message information to server")
    def send_packet(self, packet):
        try:

            self.clientSocket.sendall(bytes(packet, encoding='utf-8'))
            responsePacket = self.clientSocket.recv(2048)
            responsePacket = responsePacket.decode('utf-8')         #   Decode the binary data

            jsonObj = json.loads(responsePacket)                    #   Load to the json object
            typ, code, message, key = jsonObj.values()

            if typ == 4:
                message = message.split('\t\n')

                print('Response: {} {} {} {}'.format(typ,code,
                                                        '\n'.join(user for user in message),key))
            else :
                print('Response: {} {} {} {}'.format(typ,code,message,key))
            return [code, message] 

        except Exception as e:
            print(e)
            return [-1, '']

