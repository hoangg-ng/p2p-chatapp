from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

import pymongo as mongo
from pymongo.errors import BulkWriteError
from constants import assertLog, db_config

class DBCLient(object):

    def __init__(self, database=None, collection=None):
        self.logger = assertLog()
        self.database = database
        self.collection = collection
        self.collectiondb = None
        try:
            self.client = mongo.MongoClient(db_config['DBPATH']) 
        except Exception as e:
            self.logger.info(e)
            
    def check_field(self):
        if self.database == None or self.database == None:
            self.logger.error("please choose databasename or collection,by calling setdatabase orsetcollection ")
            return False
        return True

    def set_database(self, database):
        self.database = database

    def set_collection(self, collection):
        self.collection = collection

    def collections(self):
        if self.check_field() == False: return
        database = self.client[self.database]
        collection = database.collection_names(include_system_collections=False)
        return collection

    def databases(self):
        return self.client.database_names()

    def check_being(self,filter):
        collection = self.get_collection()
        return collection.find(filter).count()


    def get_collection(self):
        if self.check_field() == False: return
        database = self.client[self.database]
        collection = database[self.collection]
        return collection

    def insert(self, item):
        try:
            collection = self.get_collection()
            res = collection.insert_one(item)
            self.logger.info("User Registered Succesfuly: %s "%str(res.inserted_id))
            return 0
        except mongo.errors.DuplicateKeyError as exp:
            self.logger.error(repr(exp))
            # self.update(item)
            return -1
        except Exception as  exp:
            self.logger.error(repr(exp))
            return -2

    def get_documents(self, filter):
        collection = self.get_collection()
        try:
            result = collection.find(filter)
            return list(result)
        except Exception as  exp:
            self.logger.error(repr(exp))
            return -1
