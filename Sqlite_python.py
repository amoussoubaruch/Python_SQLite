# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 21:34:16 2015

@author: amoussoubaruch
"""
##############################################################################
# SQLite Python DataBase
# Date : July 2015
# Info : Work with a large Data workflow with pandas
#############################################################################
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine

# Initialise database in test_db file
disk_engine = create_engine('sqlite:///test_db.db')

# Load file on database
def load_data(in_file, disk_engine): 
    # Initialise somes variables
    start = dt.datetime.now()
    chunksize = 20000
    j = 0
    index_start = 1

    # Loop on each chunck of dataframe
    for df in pd.read_csv(in_file, chunksize=chunksize, iterator=True, encoding='utf-8'):
        df = df.rename(columns={c: c.replace(' ', '') for c in df.columns}) # Remove spaces from columns
        df['quantity'] = df['quantity'].astype(float)
        df['spend_amount'] = df['spend_amount'].astype(float)
        df.index += index_start
    
        # Remove the un-interesting columns
        columns = ['quantity', 'spend_amount', 'period', 'hhk_code', 'trx_key_code', 'sub_code']
        for c in df.columns:
            if c not in columns:
                df = df.drop(c, axis=1)
    
        j+=1
        print '{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j*chunksize)
    
        # Append data on database
        df.to_sql('data', disk_engine, if_exists='append')
        index_start = df.index[-1] + 1

in_file="trx_proc_1.csv"
load_data(in_file, disk_engine)
 
# Query data
query = """SELECT period, sub_code,
                  COUNT (DISTINCT hhk_code) AS Nb_client,
                  COUNT (*) AS Nb_UVC, 
                  SUM(quantity) AS Nb_uvc,
                  SUM(spend_amount) AS CA 
          FROM data
          GROUP BY sub_code, period"""

start = dt.datetime.now()
df = pd.read_sql_query(query, disk_engine)
(dt.datetime.now() - start).seconds

df.head()