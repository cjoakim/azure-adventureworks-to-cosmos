"""
Usage:
  python wrangle.py gather_table_metadata
  python wrangle.py csv_to_json
  python wrangle.py create_documents
"""

__author__  = 'Chris Joakim'
__email__   = "chjoakim@microsoft.com,christopher.joakim@gmail.com"
__license__ = "MIT"
__version__ = "2021.01.07"

import arrow
import csv
import json
import os
import pprint
import pyodbc
import sys
import time
import uuid

from docopt import docopt

tables = [
  "Address",
  "Customer",
  "CustomerAddress",
  "Product",
  "ProductCategory",
  "ProductModel",
  "ProductDescription",
  "ProductModelProductDescription",
  "SalesOrderHeader",
  "SalesOrderDetail"
]

DB_METADATA_FILE = 'data/wrangled/db_metadata.json'
DB_ROWS_FILE     = 'data/wrangled/db_rows.json'

CUSTOMERS_FILE = 'data/wrangled/customers.json'
CUSTOMER_ORDERS_FILE = 'data/wrangled/customer_orders.json'
PRODUCTS_FILE  = 'data/wrangled/products.json'
PRODUCT_CATEGORIES_FILE  = 'data/wrangled/product_categories.json'

def gather_table_metadata():
    db_metadata = dict()
    db_metadata['table_names'] = tables

    for table in tables:
        print('gather_table_metadata for table {}'.format(table))
        tbl_meta = dict()
        db_metadata[table] = table_column_metadata(table)

    write_obj_as_json_file(db_metadata, DB_METADATA_FILE)

def table_column_metadata(table):
    infile, data = 'data/exported/table_columns_{}.json'.format(table), list()
    table_info = read_json(infile)
    for col_idx, col_info in enumerate(table_info):
        col_dict = dict()
        col_dict['table'] = table
        col_dict['col_idx'] = col_idx
        col_dict['col_name'] = col_info[3]
        col_dict['col_type'] = col_info[5]
        data.append(col_dict)
    return data

def csv_to_json():
    print('csv_to_json')
    db_rows = list()
    db_metadata = read_json(DB_METADATA_FILE)

    for table in tables:
        print('processing table {}'.format(table))
        table_columns  = db_metadata[table]
        column_count   = len(table_columns)
        keys_columns   = keys_columns_for_table(table)
        # print('table_columns:   {}'.format(table_columns))
        # print('column_count:    {}'.format(column_count))
        # print('keys_columns:    {}'.format(keys_columns))

        rows_infile = 'data/exported/table_data_{}.csv'.format(table)
        table_rows = read_csv(infile=rows_infile, delim='|')

        for row_idx, row in enumerate(table_rows):
            if row_idx > 0:
                if len(row) == column_count:
                    obj = row_to_object(table, table_columns, row)
                    obj['__key_value'] = key_value(obj, keys_columns)
                    db_rows.append(obj)
                else:
                    print('mismatched table_metadata to row data')
                    print('actual row; {} cols: {}'.format(len(row), column_count))

    # print('total db row count: {}'.format(len(db_rows)))
    write_obj_as_json_file(db_rows, DB_ROWS_FILE) 

def row_to_object(table, table_columns, row):
    obj = dict()
    obj['__table'] = table
    for col_idx, col_info in enumerate(table_columns):
        col_name = col_info['col_name']
        col_type = col_info['col_type']
        col_val  = row[col_idx]
        obj[col_name] = col_val # default to raw string value, then cast below
        try:
            if 'int' in col_type:
                obj[col_name] = int(col_val)
            if 'money' in col_type:
                obj[col_name] = float(col_val)
            if 'numeric' in col_type:
                obj[col_name] = float(col_val)
                
        except:
            obj[col_name] = ''

    return obj

def key_value(obj, keys_columns):
    values = list()
    values.append(obj['__table'])
    for key_col in keys_columns:
        values.append(str(obj[key_col]))
    return '|'.join(values).strip()

def keys_columns_for_table(table):
    cols = list()
    if table == 'Address':
        return ['AddressID']
    elif table == 'Customer':
        return ['CustomerID']
    elif table == 'CustomerAddress':
        return ['CustomerID', 'AddressID']
    elif table == 'Product':
        return ['ProductID']
    elif table == 'ProductCategory':
        return ['ProductCategoryID']
    elif table == 'ProductDescription':
        return ['ProductDescriptionID']
    elif table == 'ProductModel':
        return ['ProductModelID']
    elif table == 'ProductModelProductDescription':
        return ['ProductModelID', 'ProductDescriptionID', 'Culture']
    elif table == 'SalesOrderHeader':
        return ['SalesOrderID']
    elif table == 'SalesOrderDetail':
        return ['SalesOrderID', 'SalesOrderDetailID']
    else:
        col = '{}ID'.format(table)
        return [col]

def create_documents():
    # Wrangle the CSV files/rows on the left to Documents on the right:
    #   "Address",                          --> Customer
    #   "Customer",                         --> Customer
    #   "CustomerAddress",                  --> Customer
    #   "ProductCategory",                  --> ProductCategory
    #   "Product",                          --> Product
    #   "ProductDescription",               --> Product
    #   "ProductModel",                     --> Product
    #   "ProductModelProductDescription",   --> Product
    #   "SalesOrderDetail",                 --> CustomerOrder
    #   "SalesOrderHeader",                 --> CustomerOrder

    db_rows = read_json(DB_ROWS_FILE)  # array of key-val row objects
    db_dict = dict()  # use a python dictionary for in-memory lookups; alternatively use redis

    order_docs = list()
    customer_docs = list()
    product_categories_docs = list()
    product_docs = list()

    print('{} rows read from {}'.format(len(db_rows), DB_ROWS_FILE))
    for db_row in db_rows:
        key = db_row['__key_value']
        if key in db_dict:
            print('WARNING; duplicate key: {}'.format(key))
        else:
            db_dict[key] = db_row

    for doc in create_customer_order_docs(db_rows, db_dict):
        order_docs.append(doc)

    for doc in create_customer_docs(db_rows, db_dict):
        customer_docs.append(doc)
    
    for doc in create_product_category_docs(db_rows, db_dict):
        product_categories_docs.append(doc)

    for doc in create_product_docs(db_rows, db_dict):
        product_docs.append(doc)

    # Remove the unnecessary attributes from these docs before inserting
    # into CosmosDB
    scrub_customer_docs(customer_docs)
    scrub_customer_order_docs(order_docs)
    scrub_product_categories_docs(product_categories_docs)
    scrub_product_docs(product_docs)

    write_obj_as_json_file(customer_docs, CUSTOMERS_FILE) 
    write_obj_as_json_file(order_docs, CUSTOMER_ORDERS_FILE) 
    write_obj_as_json_file(product_categories_docs, PRODUCT_CATEGORIES_FILE) 
    write_obj_as_json_file(product_docs, PRODUCTS_FILE) 

def create_customer_docs(db_rows, db_dict):
    docs = list()
    for cust_doc in db_rows:
        if cust_doc['__table'] == 'Customer':
            cust_id = cust_doc['CustomerID']
            cust_doc['doctype'] = 'customer'
            cust_doc['pk'] = cust_id
            cust_doc['addresses'] = addresses_for_customer(cust_id, db_rows, db_dict)
            docs.append(cust_doc)
    return docs 

def addresses_for_customer(cust_id, db_rows, db_dict):
    cust_addresses = list()
    for cust_addr_row in find('CustomerAddress', 'CustomerID', cust_id, db_rows):
        addr_rows = find('Address', 'AddressID', cust_addr_row['AddressID'], db_rows)
        for addr_row in addr_rows:
            addr_row['AddressType'] = cust_addr_row['AddressType']
            cust_addresses.append(addr_row)
    return cust_addresses 

def create_product_category_docs(db_rows, db_dict):
    docs = list()
    for cat_doc in db_rows:
        if cat_doc['__table'] == 'ProductCategory':
            cat_doc['heirarchy'] = lookup_product_category_heirarchy(cat_doc, db_dict)
            cat_doc['heirarchy_depth'] = len(cat_doc['heirarchy'])
            cat_doc['doctype'] = 'product_category'
            cat_doc['pk'] = cat_doc['ProductCategoryID']
            docs.append(cat_doc)
    return docs

def create_product_docs(db_rows, db_dict):
    docs = list()
    for product_doc in db_rows:
        if product_doc['__table'] == 'Product':
            product_doc['pk'] = product_doc['ProductID']
            product_doc['doctype'] = 'product'
            prod_model_id = product_doc['ProductModelID']
            pm = find('ProductModel', 'ProductModelID', prod_model_id, db_rows)
            if len(pm) > 0:
                product_doc['ProductModelName'] = pm[0]['Name']
                product_doc['Descriptions'] = lookup_product_model_descriptions(prod_model_id, db_rows, db_dict)
            docs.append(product_doc)
    return docs

def lookup_product_model_descriptions(prod_model_id, db_rows, db_dict):
    descriptions = dict()
    for pmd in db_rows:
        if pmd['__table'] == 'ProductModelProductDescription':
            if pmd['ProductModelID'] == prod_model_id:
                culture = pmd['Culture'].strip()
                desc_id = pmd['ProductDescriptionID']
                key = 'ProductDescription|{}'.format(desc_id)
                desc = lookup(key, db_dict)
                if desc:
                    descriptions[culture] = desc['Description']
    return descriptions

def create_customer_order_docs(db_rows, db_dict):
    # Sales = SalesOrderHeader, SalesOrderDetail
    docs = list()
    for header_doc in db_rows:
        if header_doc['__table'] == 'SalesOrderHeader':
            header_doc['doctype'] = 'customer_order'
            header_doc['pk'] = header_doc['CustomerID']
            order_id = header_doc['SalesOrderID']
            header_doc['line_items'] = list()
            for detail_doc in db_rows:
                if detail_doc['__table'] == 'SalesOrderDetail':
                    if detail_doc['SalesOrderID'] == order_id:
                        header_doc['line_items'].append(detail_doc)
            docs.append(header_doc)
    return docs

def lookup_product_category_heirarchy(cat_doc, db_dict):
    heirarchy = list()
    try:
        parent_id = int(cat_doc['ParentProductCategoryID'])
        for i in range(0, 10):
            if parent_id and (parent_id != 'NULL'):
                key = 'ProductCategory|{}'.format(parent_id)
                parent_cat = lookup(key, db_dict)
                if parent_cat:
                    parent_obj = dict()
                    parent_obj['id'] = parent_cat['ProductCategoryID']
                    parent_obj['name'] = parent_cat['Name']
                    parent_obj['parent_id'] = parent_cat['ParentProductCategoryID']
                    heirarchy.append(parent_obj)
                    parent_id = parent_obj['parent_id']
                else:
                    parent_id = None
            else:
                pass
    except:
        pass
    return heirarchy

def scrub_customer_docs(customer_docs):
    attr_names = ['__key_value', '__table', 'ModifiedDate']  # rowguid
    for cust in customer_docs:
        remove_attrs(attr_names, cust)
        for addr in cust['addresses']:
            remove_attrs(attr_names, addr)

def scrub_customer_order_docs(customer_order_docs):
    attr_names = ['__key_value', '__table', 'ModifiedDate']  # rowguid
    for order in customer_order_docs:
        remove_attrs(attr_names, order)
        for line_item in order['line_items']:
            remove_attrs(attr_names, line_item)

def scrub_product_categories_docs(product_categories_docs):
    attr_names = ['__key_value', '__table', 'ModifiedDate']  # rowguid
    for pc in product_categories_docs:
        remove_attrs(attr_names, pc)

def scrub_product_docs(product_docs):
    attr_names = ['__key_value', '__table', 'ModifiedDate']  # rowguid
    for p in product_docs:
        remove_attrs(attr_names, p)

def remove_attrs(attr_name_list, doc):
    for attr_name in attr_name_list:
        if attr_name in doc.keys():
            del doc[attr_name]

def lookup(key, db_dict):
    if key in db_dict:
        return db_dict[key]
    else:
        return None 

def find(row_type, col_name, col_value, db_rows):
    matches = list()
    for db_row in db_rows:
        if db_row['__table'] == row_type:
            if col_name in db_row:
                if db_row[col_name] == col_value:
                    matches.append(db_row)
    return matches

def strip_unnecessary_attributes(doc):
    for key in doc.keys():
        if key.startswith('__'):
            del doc[key]

def read_json(infile):
    with open(infile, 'rt') as f:
        return json.loads(f.read())

def read_csv(infile, reader='default', delim=',', dialect='excel', skip=0):
    rows = list()
    if reader == 'dict':
        with open(infile, 'rt') as csvfile:
            rdr = csv.DictReader(csvfile, dialect=dialect, delimiter=delim)
            for row in rdr:
                rows.append(row)
    else:
        with open(infile) as csvfile:
            rdr = csv.reader(csvfile, delimiter=delim)
            for idx, row in enumerate(rdr):
                if idx >= skip:
                    rows.append(row)
    return rows

def write_obj_as_json_file(obj, outfile):
    txt = json.dumps(obj, sort_keys=True, indent=2)
    with open(outfile, 'wt') as f:
        f.write(txt)
    print("file written: " + outfile)

if __name__ == "__main__":
    func = sys.argv[1]

    if func == 'gather_table_metadata':
        gather_table_metadata()
    elif func == 'csv_to_json':
        csv_to_json()
    elif func == 'create_documents':
        create_documents()
    elif func == 'load_documents':
        load_documents() 
    else:
        print_options('Error: invalid function: {}'.format(func))
