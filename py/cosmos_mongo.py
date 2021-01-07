"""
Usage:
  python cosmos_mongo.py load_db design_a
  python cosmos_mongo.py load_db design_b
  python cosmos_mongo.py load_db design_c
  python cosmos_mongo.py delete_all_docs
  -
  python cosmos_mongo.py query_container_by_pk Product 707
  python cosmos_mongo.py query_container_by_pk_and_doctype Data 707 product
"""

__author__  = 'Chris Joakim'
__email__   = "chjoakim@microsoft.com,christopher.joakim@gmail.com"
__license__ = "MIT"
__version__ = "2021.01.07"

# SDK source code:
# https://github.com/Azure/azure-sdk-for-python/tree/azure-cosmos_4.2.0/sdk/cosmos/azure-cosmos

import json
import sys
import time
import os

from pymongo import MongoClient
from bson.objectid import ObjectId

# Constants for container names:
CUSTOMER = 'Customer'
CUSTOMER_ORDER = 'CustomerOrder'
PRODUCT = 'Product'
PRODUCT_CATEGORY = 'ProductCategory'
DATA = 'Data'
CONTAINERS = [CUSTOMER, CUSTOMER_ORDER, PRODUCT, PRODUCT_CATEGORY, DATA]


MAX_UPSERTS = 10000

class Mongo(object):

    def __init__(self, opts):
        self._opts = opts
        self._db = None
        self._coll = None
        conn_str = os.environ['AZURE_COSMOSDB_MONGODB_CONN_STRING']
        print('Mongo using conn_str: {}'.format(conn_str))
        self._client = MongoClient(conn_str)
        self.set_db(os.environ['AZURE_COSMOSDB_MONGODB_DBNAME'])
        print(self._client)

    def list_databases(self):
        return self._client.list_database_names()

    def list_collections(self):
        return self._db.list_collection_names()

    def set_db(self, dbname):
        self._db = self._client[dbname]
        print(self._db)
        return self._db 

    def set_coll(self, collname):
        self._coll = self._db[collname]
        print(self._coll)
        return self._coll 

    def insert_doc(self, doc):
        return self._coll.insert_one(doc)

    def find_one(self, query_spec):
        return self._coll.find_one(query_spec)

    def find(self, query_spec):
        return self._coll.find(query_spec)

    def find_by_id(self, id):
        return self._coll.find_one({'_id': ObjectId(id)})

    def delete_by_id(self, id):
        return self._coll.delete_one({'_id': ObjectId(id)})

    def delete_one(self, query_spec):
        return self._coll.delete_one(query_spec)

    def delete_many(self, query_spec):
        return self._coll.delete_many(query_spec)

    def update_one(self, filter, update, upsert):
        # 'update only works with $ operators'
        return self._coll.update_one(filter, update, upsert)

    def update_many(self, filter, update, upsert):
        # 'update only works with $ operators'
        return self._coll.update_many(filter, update, upsert)

    def count_docs(self, query_spec):
        return self._coll.count_documents(query_spec)

    def client(self):
        return self._client

    def last_request_stats(self):
        return self._db.command({"getLastRequestStatistics": 1})

        # globaldb:PRIMARY> result = db.runCommand({"getLastRequestStatistics": 1})
        # {
        # 	"CommandName" : "find",
        # 	"RequestCharge" : 12.73,
        # 	"RequestDurationInMilliSeconds" : NumberLong(252),
        # 	"ActivityId" : "1d3b2998-d17c-4693-b247-020f64d18289",
        # 	"ok" : 1
        # }


def load_db(design_name):
    print('load_db, design_name: {}'.format(design_name))
    config = design_config()[design_name]
    print(config)

    mongo_client = Mongo({})

    for json_datafile in config.keys():
        target_container = config[json_datafile]
        mongo_client.set_coll(target_container)
        print('Loading container {} from file {}'.format(target_container, json_datafile))
        json_docs = read_json(json_datafile)  # an array of JSON documents
        for idx, json_doc in enumerate(json_docs):
            if idx < 99999:
                print('doc {}: {}'.format(idx, json_doc))
                result = mongo_client.insert_doc(json_doc)
                print('id: {}'.format(result.inserted_id))

def delete_all_docs():
    mongo_client = Mongo({})

    for container_name in CONTAINERS:
        mongo_client.set_coll(container_name)
        query_spec = {"doctype": {"$ne": "x"}}
        mongo_client.delete_many(query_spec)

def design_config():
    config = dict()
    config['design_a'] = {
        "data/wrangled/customers.json": "Customer",
        "data/wrangled/customer_orders.json": "CustomerOrder",
        "data/wrangled/products.json": "Product",
        "data/wrangled/product_categories.json": "ProductCategory"
    }
    config['design_b'] = {
        "data/wrangled/customers.json": "Customer",
        "data/wrangled/customer_orders.json": "Customer",
        "data/wrangled/products.json": "Product",
        "data/wrangled/product_categories.json": "Product"
    }
    config['design_c'] = {
        "data/wrangled/customers.json": "Data",
        "data/wrangled/customer_orders.json": "Data",
        "data/wrangled/products.json": "Data",
        "data/wrangled/product_categories.json": "Data"
    }
    return config

def query_container_by_pk(cname, pk_value):
    print('query_container: {} by pk: {}'.format(cname, pk_value))
    mongo_client = Mongo({})
    mongo_client.set_coll(cname)

    query_spec = {'pk': pk_value}
    print('query_spec: {}'.format(query_spec))

    for idx, doc in enumerate(mongo_client.find(query_spec)):
        print('--- result idx {}'.format(idx))
        print(doc)

    stats = mongo_client.last_request_stats()
    print(stats)

def query_container_by_pk_and_doctype(cname, pk_value, doctype):
    print('query_container: {} by pk: {} and doctype: {}'.format(cname, pk_value, doctype))
    mongo_client = Mongo({})
    mongo_client.set_coll(cname)

    query_spec = {'pk': pk_value, 'doctype': doctype}
    print('query_spec: {}'.format(query_spec))

    for idx, doc in enumerate(mongo_client.find(query_spec)):
        print('--- result idx {}'.format(idx))
        print(doc)

def read_json(infile):
    with open(infile, 'rt') as f:
        return json.loads(f.read())

def boolean_cli_arg(flag):
    for arg in sys.argv:
        if arg == flag:
            return True
    return False

def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version=__version__)
    print(arguments)


if __name__ == "__main__":
    func = sys.argv[1]
    
    if func == 'load_db':
        design_name = sys.argv[2]
        load_db(design_name)

    elif func == 'delete_all_docs':
        delete_all_docs()

    elif func == 'query_container_by_pk':
        cname = sys.argv[2]
        pk_value = sys.argv[3]
        if boolean_cli_arg('--int'):
            pk_value = int(pk_value)
        query_container_by_pk(cname, pk_value)

    elif func == 'query_container_by_pk_and_doctype':
        cname = sys.argv[2]
        pk_value = sys.argv[3]
        if boolean_cli_arg('--int'):
            pk_value = int(pk_value)
        doctype = sys.argv[4]
        query_container_by_pk_and_doctype(cname, pk_value, doctype)

    else:
        print_options('Error: invalid function: {}'.format(func))
