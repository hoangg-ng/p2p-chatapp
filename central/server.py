from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from socket import *
from constants import server_config
from .monitor import *
from .db_management import *

class CentralServer:

    def __init__(self):
        print("Server started")
        self.monitor_thread = Monitor(
            DBCLient(db_config['DBNAME'], db_config['COLLECTION']),
        )
        self.host = gethostbyname(server_config['SERVERIP'])
        self.port = server_config['TCP_SERVER_PORT'] 
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.monitor_thread.start()
        print("Server is listening!")