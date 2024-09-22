import pymongo
from mongo_conn import mongo_configuration


def create():
    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    return client