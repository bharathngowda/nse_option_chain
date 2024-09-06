#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
from datetime import datetime


# In[2]:


# Initializing a dataframe
option_chain=pd.DataFrame()

# URL of the API endpoint
api_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

# Headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}
attempt=1

# Making upto 10 API tries before exiting
while attempt<10:
    print(attempt)
    try:
        # Make a GET request to the API endpoint
        response = requests.get(api_url, headers=headers)
    
        # Load the JSON data
        data = response.json()
    
        # Extract the necessary part of the JSON data
        try:
            # Extract 'records' which contains the option data
            records = data['records']['data']
    
            # Initialize lists to hold call and put option data
            call_data = []
            put_data = []
    
            # Iterate over each record
            for record in records:
                if 'CE' in record:
                    call_data.append(record['CE'])
                if 'PE' in record:
                    put_data.append(record['PE'])
    
            # Convert lists to DataFrames
            df_calls = pd.DataFrame(call_data)
            df_puts = pd.DataFrame(put_data)
    
            # Reindex DataFrames to ensure column alignment
            df_calls = df_calls.reindex(columns=pd.Index(sorted(df_calls.columns), name='CE'))
            df_puts = df_puts.reindex(columns=pd.Index(sorted(df_puts.columns), name='PE'))
    
            # Combine both DataFrames
            option_chain = pd.concat([df_calls, df_puts], axis=1)
    
            # Create multi-level columns
            call_columns = pd.MultiIndex.from_product([['CALLS'], df_calls.columns], names=['Type', 'Attribute'])
            put_columns = pd.MultiIndex.from_product([['PUTS'], df_puts.columns], names=['Type', 'Attribute'])
            option_chain_columns = call_columns.append(put_columns)
    
            # Reassign the columns to the DataFrame
            option_chain.columns = option_chain_columns
    
            # Converting to datetime object
            option_chain[('CALLS','expiryDate')]=pd.to_datetime(option_chain[('CALLS','expiryDate')],format='%d-%b-%Y')
            option_chain[('PUTS','expiryDate')]=pd.to_datetime(option_chain[('PUTS','expiryDate')],format='%d-%b-%Y')
    
        except KeyError as e:
            print(f"KeyError: {e} - The expected key was not found in the JSON response.")
    except:
        print(f"Request failed with status code {response.status_code}")
        attempt=attempt+1
        continue
    break


# In[3]:


# Exporting to excel
if option_chain.empty==False:
    option_chain.to_excel('option_chain_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx')





