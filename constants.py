import logging
import os
import sys


""" DATABASE CONFIG """
db_config = {
    'DBNAME' : "chatapp_users",
    'COLLECTION' : 'authentication',
    'DBPATH': 'mongodb+srv://quangngcs:nguyenhoquangcs22@cluster0.z10zfda.mongodb.net/?retryWrites=true&w=majority'
}

""" SERVER CONFIG """

server_config = {
    'SERVERIP': '127.0.0.1',
    'TCP_SERVER_PORT': 5131,
    'CONNECTIONS': [],
    'TIMEOUT':1000 
}

peer_config = {
    'PEERIP': '127.0.0.1',
    'LISTEN_PORT': 3000,
    'MESSAGE_PORT': 5000, 
}
""" PROTOCOL CONFIG """

LOGCODE = {
    20: 'registered',
    21: 'successfully login',
    22: 'founduser',
    23: 'successullyexit',
    24: 'onlinelistsent',
    40: 'duplicatecredent',
    41: 'invalidcredent',
    44: 'notfounduser',
    45: 'usernotfound',
    46: 'noonlineuser',
    50: 'errorserver',
    100: 'peerstillalive',
    101: 'cannotverifyliveness',
    200: 'updated',
    201: 'updatefailed',
}

REQUEST_TYPEID = {
    0: 'REGISTER',
    1: 'LOGIN',
    2: 'SEARCH',
    3: 'LOGOUT',
    4: 'LISTUSER',
    5: 'UPDATE_ALIVE',
    6: 'UPDATE_CONNECTION',
    7: 'UPDATE_MESSAGE_INFO'
}

#   SENDING KEY CLIENT
KEY = 15
#   FORMAT PACKING AND UNPACKING
REQUEST_CLIENT_FORMAT = 'b 64s 64s b'
RESPONSE_SERVER_FORMAT = 'b b 15s b'

#   INTERFACE CONFIG    #

#   FILE CONFIG     #   
FORMAT = 'utf-8'


def assertLog():
    assertFormatter = logging.Formatter(  
        "%(asctime)s [%(filename)s  %(funcName)s  %(threadName)s ] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    if (len(rootLogger.handlers) > 0):
        return rootLogger
    rootLogger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler('logfile.log')
    fileHandler.setFormatter(assertFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(assertFormatter)
    rootLogger.addHandler(consoleHandler)
    return rootLogger