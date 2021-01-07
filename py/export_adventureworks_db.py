"""
Usage:
  python export_sample_db.py
"""

# https://docs.microsoft.com/en-us/azure/azure-sql/database/connect-query-python?tabs=macos
# brew install unixodbc
# brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
# brew update
# HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17 mssql-tools

__author__  = 'Chris Joakim'
__email__   = "chjoakim@microsoft.com,christopher.joakim@gmail.com"
__license__ = "MIT"
__version__ = "2021.01.07"

import arrow
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
  "ProductDescription",
  "ProductModel",
  "ProductModelProductDescription",
  "SalesOrderDetail",
  "SalesOrderHeader",
]

def export_sample_db_to_csv():
    print('export_sample_db_to_csv')

    server    = os.environ['AZURE_SQL_SERVER']
    server_fn = os.environ['AZURE_SQL_SERVER_FULL_NAME']
    database  = os.environ['AZURE_SQL_DATABASE']
    username  = os.environ['AZURE_SQL_USER']
    password  = os.environ['AZURE_SQL_PASS']
    driver    = '{ODBC Driver 17 for SQL Server}'
    header_rows = dict()

    print('driver:    {}'.format(driver))
    print('server_fn: {}'.format(server_fn))
    print('database:  {}'.format(database))
    print('username:  {}'.format(username))  
    print('password:  {}'.format(password))

    template  = "Driver={};Server=tcp:{},1433;Database={};Uid={};Pwd={};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    conn_str  = template.format(driver, server_fn, database, username, password)
    print('conn_str: {}'.format(conn_str))
    
    with pyodbc.connect(conn_str) as conn:

        for table in tables:
            data = list()
            field_names = list()
            outfile = 'data/exported/table_columns_{}.json'.format(table)
            with conn.cursor() as cursor:
                sql = "exec sp_columns {}".format(table)
                print("=== sql: {}".format(sql))
                cursor.execute(sql)
                row = cursor.fetchone()
                while row:
                    array = [str(elem) for elem in row]
                    data.append(array)
                    row = cursor.fetchone()
                    field_names.append(array[3])

            header_rows[table] = "|".join(field_names)
            write_obj_as_json_file(data, outfile)

        write_obj_as_json_file(header_rows, 'data/exported/table_headers.json')

        for table in tables:
            csv_lines = list()
            csv_lines.append(header_rows[table])
            outfile = 'data/exported/table_data_{}.csv'.format(table)
            with conn.cursor() as cursor:
                sql = "SELECT * from [SalesLT].[{}]".format(table)
                print("=== sql: {}".format(sql))
                cursor.execute(sql)
                row = cursor.fetchone()
                while row:
                    values = list()
                    for col_idx, elem in enumerate(row):
                        # There are some columns that we don't want to port to NoSQL; exclude them here
                        if table == 'Product':
                            if col_idx == 13:  # port the ThumbNailPhoto bytes to Azure Blob Storage
                                product_id = row[0]
                                value = 'product_{}.gif'.format(product_id)
                            else:
                                value = str(elem) 
                        elif table == 'ProductModel':
                            if col_idx == 2:
                                # exclude the column CatalogDescription with occasional XML data
                                # alternatively, we could parse the XML and port what's necessary
                                value = ''
                            else:
                                value = str(elem) 
                        else:
                            value = str(elem)
                        values.append(value)
                    csv_lines.append("|".join(values))  
                    row = cursor.fetchone()
            write_lines(outfile, csv_lines)

def write_obj_as_json_file(obj, outfile):
    txt = json.dumps(obj, sort_keys=True, indent=2)
    with open(outfile, 'wt') as f:
        f.write(txt)
    print("file written: " + outfile)

def write_lines(outfile, lines):
    with open(outfile, 'w') as f:
        for line in lines:
            f.write(line)
            f.write("\n")
        print('file written: {} ({} lines)'.format(outfile, len(lines)))

def flag_cli_arg(flag):
    for arg in sys.argv:
        if arg == flag:
            return True
    return False


if __name__ == "__main__":
    export_sample_db_to_csv()
