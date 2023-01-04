from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

import threading
import time
from constants import *
import struct
from .db_management import DBCLient
from socket import *
import hashlib
import json

"""
    TCPListener:    a thread of server initialized to listen and handle from 
                    the user thread
    Methods:        
                    processMessage()
                    checkPacket()
                    logOut()
                    allUser()
                    loginUser()
                    searchUser()
                    registerUser()
                    checkAuthentication()
                    update_alive()
                    update_dead()
                    update_Info()
    Attributes:
                    socket: TCP socket of user
                    ip: ip of user
                    port: port number of user
                    db: mongodb instance
    
    Packet: 
                    A JSON Object
"""
class TCPListener(threading.Thread):

    def __init__(self, host, _socket):
        threading.Thread.__init__(self)
        
        self._socket = _socket
        self.host = host[0]
        self.port = host[1]
        self.db = DBCLient(db_config['DBNAME'], db_config['COLLECTION'])
        self.logger = assertLog()
        self.__stop = False

    def stop(self):

        self.logger.info("Connection closed [{}, {}]".format(self.host, self.port))
        self._socket.close()
        self.__stop = True
        
    def run(self):
        while self.__stop == False:
            try:

                packet = self._socket.recv(1024)            #   Listen to receive the packet
                if not packet:                              #   Error occur --> Then break the process
                    break
                result = self.checkPacket(packet)
                self.logger.info(result)
                self._socket.send(bytes(result, encoding='utf-8'))

            except Exception as e:
                self.logger.info(e)
        #         break
        
        self.logger.info("Connection closed [{}, {}]".format(self.host, self.port))
        self._socket.close()
        self.stop()
    
    def packingMessage(self, typeid, logcode, message, key):
        
        return json.dumps({
            'type': typeid,
            'logcode': logcode,
            'message': message,
            'key': key,
        })

    def unpackingMessage(self, packet):

        """ Return the json object values """
        try:
            unpack = packet.decode('utf-8')
            jsonObject= json.loads(unpack)
            self.logger.info(jsonObject)
            return jsonObject.values()
        except Exception as e:
            self.logger.info(e)
            return [-1, '', '', -1]
    def processMessage(self, Message):
        
        return Message
    def checkPacket(self, packet):  

        response = None
        try:

            typeid, field1, field2, key =  self.unpackingMessage(packet)
            field1 = self.processMessage(field1)
            field2 = self.processMessage(field2)
            self.logger.info(
                "Request ---> Type:{} , Field1:{} , Field2:{}    [ {} , {} ] ".format(type, field1, field2, self.host,
                                                                                    self.port))

            # todo add validate manner

            if typeid == 0:  # register
                response = self.registerUser(field1, field2)
            elif typeid == 1:  # login
                response = self.loginUser(field1, field2)
            elif typeid == 2:  # search
                response = self.searchUser(field1, field2)
            elif typeid == 3:  # _assertOUT
                response = self.logOut(field1)
            elif typeid == 4:  # All
                response = self.allUser(field1)
            elif typeid == 5:  #    alive signal
                response = self.update_alive(field1)
            elif typeid == 6:
                response = self.updateListenName(field1, field2)
            elif typeid == 7:
                response = self.updateMessageName(field1, field2)
        except Exception as e:
            self.logger.info(e)
        return response


    def updateListenName(self, username, connection_info):

        try:
            
            listenIP, listenPort = connection_info.split(';')
            self.db.get_collection().update_one(
                {'_id': username},
                {'$set': {
                    'listenIP': listenIP,
                    'listenPort': listenPort,
                    'last_access': time.time()
                }} 
            )

            response = self.packingMessage(
                6,
                200,
                LOGCODE[200],
                15,
            )
            self.printLog(200, username=username)
            return response

        except Exception as e :
            self.printLog(201, username=username)
            response = self.packingMessage(
                6,
                201,
                LOGCODE[201],
                15,
            )
            return response

    def updateMessageName(self, username, connection_info):

        try:
            
            messageIP, messagePort = connection_info.split(';')
            print(messagePort, messageIP)
            self.db.get_collection().update_one(
                {'_id': username},
                {'$set': {
                    'messageIP': messageIP,
                    'messagePort': messagePort,
                    'last_access': time.time()
                }} 
            )

            response = self.packingMessage(
                7,
                200,
                LOGCODE[200],
                15,
            )
            self.printLog(200, username=username)
            
            return response
        except Exception as e :
            self.logger.info(e) 
            self.printLog(201, username=username)
            response = self.packingMessage(
                7,
                201,
                LOGCODE[201],
                15,
            )
            return response
    #   UPDATE ALIVE STATE  -   TYPE: 5
    def update_alive(self, username):
        try:
            self.db.get_collection().update_one(
                {'_id': username},
                {'$set': {
                    'isActive': True,
                    'last_access': time.time()
                }}
            )

            response = self.packingMessage(
                5,              #      TYPE ID 
                100,            #       LOG COCDE
                LOGCODE[100],   #       MESSAGE CODE
                15
            ) 
            self.printLog(100, username)
            return response
            
        except Exception as e:
            response = self.packingMessage(
                5,
                101, 
                LOGCODE[101],
                15
            )
            return response
            self.logger.info(e)
    
    #   UPDATE DEAD STATE  
    def update_dead(self, username):
        try:
            self.db.get_collection().update_one(
                {'_id': username},
                {'$set': {  'isActive': False,
                            'serverIP': '',
                            'serverPort': -1
                }}
            )
        except Exception as e:
            self.logger.info(e)

    #   REGISTER;   TYPE:0;     USERNAME;   PASSWORD;   KEY:15
    def registerUser(self, username, password):
        result = self.db.insert(item = 
            {
                "_id": username, 
                "name": username,
                "password": hashlib.sha256(password.encode('utf-8')).hexdigest(),
                "serverIP": '',
                "serverPort": -1,
                'listenIP': '',
                'listenPort': -1,
                'messageIP': '',
                'messagePort': -1,
                "isActive": False,
                'last_access':  time.time(), 
            }
        )
        
        if result == 0:
            self.printLog(20)
            response = self.packingMessage(
                0,
                20,
                LOGCODE[20],
                15,
            )

        elif result == -1:
            self.printLog(40)
            response = self.packingMessage(
                0,
                40,
                LOGCODE[40], 
                15,
            )

        else:
            self.printLog(50)
            response = self.packingMessage(
                0,
                50,
                LOGCODE[50],
                15,
            )
        return response

    #   LOG IN      -   TYPE: 1
    def loginUser(self, username, password):
        result = self.checkAuthentication(username, password)
        response = ''

        if result:
            response = self.packingMessage(
                1,
                21,
                LOGCODE[21],
                15,
            )
            self.db.get_collection().update_one(
                {'_id': username},
                {"$set": {  'isActive': True, 
                            'serverIP': self.host,  
                            'serverPort': self.port,
                            'last_access': time.time()}}
            )
            self.printLog(21)

        else:
            response = self.packingMessage(
                1,
                41,
                LOGCODE[41],
                15,
            )
            self.printLog(41)
        return response

    #   SEARCH USER -   TYPE: 2
    def searchUser(self, username, search):
        
        string = ''
        search_result = self.db.get_documents(filter= {
            '_id': search
        })

        if search_result != -1:
            response = self.packingMessage(
                2,
                22,
                search_result,
                15
            ) 
            self.printLog(22)
            return response
        
        else:
            response = self.packingMessage(
                2,
                44,
                LOGCODE[44],
                15,
            )
            self.printLog(44)
            return response

    #   LOG OUT     -   TYPET: 3
    def logOut(self, username):
        result = self.db.get_documents(filter={
            '_id': username
        })
        self.update_dead(username)
        response = ''

        if result != -1:
            response = self.packingMessage(
                3,
                23,
                LOGCODE[23],
                15,
            )
            self.printLog(23)
            
        else:
            response = self.packingMessage(
                3,
                45,
                LOGCODE[45],
                15,
            )
            self.printLog(45)

        return response

    #   LIST ALL USERS  -   TYPE: 4
    def allUser(self, username):

        response = ''
        string = ""
        online_peers =  self.db.get_documents(filter = {
            'isActive': True
        }) 
        if len(online_peers) > 0:
            for idx, peer_document in enumerate(online_peers):
                string += peer_document['_id'] + ';' + peer_document['listenIP'] + ';' + str(peer_document['listenPort'])
                string += '\t\n'

        if string == '':
            response = self.packingMessage(
                4,
                46,
                LOGCODE[46],
                15
            )
            self.printLog(46)
        else:
            response = self.packingMessage(
                4, 
                24, 
                string,
                15
            )
            self.printLog(24)
        return response 

    #   CHECK AUTHENTICATION
    def checkAuthentication(self, username, password):
        result = self.db.get_documents(filter={
            "_id": username,
            "password": hashlib.sha256(password.encode('utf-8')).hexdigest()
        })
        return result
    
    def printLog(self, code, username = None):
        if code == 20:
            self.logger.info(
                "Response ---> Type:{} Status:{} Message: {}    [ {} , {} ]".format(0, 20, LOGCODE[20], self.host, self.port))
        elif code == 21:
            self.logger.info(
                "Response ---> Type:{} Status:{} Message: {}    [ {} , {} ]".format(1, 21, LOGCODE[21],'succesfullogin',
                                                                                              self.host, self.port))
        elif code == 22:
            self.logger.info("Response ---> Type:{} Status:{} Message: {}   [ {} , {} ]".format(2, 22, LOGCODE[22], self.host, self.port))
        elif code == 23:    
            self.logger.info("Response ---> Type:{} Status:{} Message: {}    [ {} , {} ]".format(3, 23, LOGCODE[23], self.host,
                                                                                                    self.port))
        elif code == 24:
            self.logger.info(
                "Response ---> Type:{} Status:{} Message: {} [ {} , {} ]".format(4, 24, LOGCODE[24], self.host,
                                                                                                  self.port))
        elif code == 40:
            self.logger.info("Response ---> Type:{} Status:{} Message: {}    [ {} , {} ]".format(0, 40, LOGCODE[40], self.host,
                                                                                                       self.port))
        elif code == 41:
            self.logger.info("Response ---> Type:{} Status:{} Message: {}    [ {} , {} ]".format(1, 41, LOGCODE[41], self.host,
                                                                                                    self.port))
        elif code == 44:
            self.logger.info(
                "Response --->Type:{} Status:{} Message: {}    [ {} , {} ]".format(2, 44, LOGCODE[44], self.host, self.port))
        elif code == 45:
            self.logger.info(
                "Response --->Type:{} Status:{} Message: {}     [ {} , {} ]".format(3, 45, LOGCODE[45], self.host,
                                                                                            self.port))
        elif code == 46:
            self.logger.info(
                "Response --->Type:{} Status:{} Message: {}    [ {} , {} ]".format(4, 46, LOGCODE[46], self.host,
                                                                                              self.port))
        elif code == 50:
            self.logger.info(
                "Response ---> Type:{} Status:{} Message: {}    [ {} , {} ]".format(0, 50, LOGCODE[50], self.host, self.port))
        elif code == 100:
            self.logger.info(
                "Response --> Type:{} Status {} Message: {}     [ {} , {} ]".format(5, 100, LOGCODE[100], self.host, self.port)
            )

        elif code == 101:
            self.logger.info(
                "Response --> Type: {} Status {} Message: {}    [ {} , {} ]".format(5, 101, 'cannotverify', 15)
            )
        
        elif code == 200:
            self.logger.info(
                "Response --> Type:{} Status {} Message: {}     [ {} , {} ]".format(6, 200, LOGCODE[200], self.host, self.port)
            )