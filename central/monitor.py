from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)
import threading
import time
from constants import *
import pymongo


class Monitor(threading.Thread):

    def __init__(self, database):
        
        threading.Thread.__init__(self)
        self.database = database
        self._threadList = []
        self.logger = assertLog()
        self.__stop  = False
    
    def stop(self):
        self.__stop = True

    def run(self):
        self.logger.info("Monitor thread is initialized")
        while self.__stop == False:
            
            time.sleep(10)
            self.logger.info("Checking active peers")
            num_threads_working = len(self._threadList)
            self.logger.info("Currently, there are {} threads working".format(num_threads_working))
            
            if num_threads_working > 0:
                self.logger.info("Verify liveness of {} threads".format(num_threads_working))
                online_peers = self.database.get_documents(filter = {
                })

                ctime = round(time.time())
                for user in online_peers:
                    if(ctime - user['last_access']) > server_config['TIMEOUT']:         #   TIME OUT
 
                        self.database.get_collection().update_one(
                            {'_id': user['_id']},
                            {"$set": {
                                'serverIP': "",
                                'port': -1,
                                'isActive': False
                            }}
                        )

                        for idx, _thread in enumerate(self._threadList):
                            if _thread.host == user['serverIP'] and _thread.port == user['serverPort'] and user['serverIP'] != '':
                                self.logger.info("Time out! Remove connection: [{}. {}]".format(user['serverIP'], user['serverPort']))
                                _thread.stop()
                                self._threadList.remove(_thread)
                                self.logger.info("Remove thread of [ {} , {} ]".format(_thread.host, _thread.port))
                                self.logger.info("Current threads working: {}".format(len(self._threadList)))
                    
                    else:
                        self.logger.info("No threads are time out")