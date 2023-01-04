import pymongo as mongo
from constants import *
from central.server import *
from central.listenerTCP import *
from central.monitor import *

asserter = assertLog()
server = CentralServer()
while True:
    
    connectionSocket, address = server.socket.accept()
    asserter.info("Connection accepted from [{}. {}]".format(address[0], address[1]))    
    thread = TCPListener(host = address, _socket = connectionSocket)
    thread.start()
    server.monitor_thread._threadList.append(thread)   


