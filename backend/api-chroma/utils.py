import os
import csv
import pandas as pd
from json import loads

def find_delimiter(filename):
    sniffer = csv.Sniffer()
    with open(filename) as fp:
        delimiter = sniffer.sniff(fp.read(5000)).delimiter
    return delimiter

def load_dataset(item_id):
    item_path = '../../datos/'+item_id+'.csv'
    if os.path.exists(item_path):
        try:
            delimiter = find_delimiter(item_path)
            df = pd.read_csv(item_path, engine='python',
                             on_bad_lines="skip", encoding='utf-8',
                             sep=delimiter)
            if len(df.columns)>1:
                result = df.to_json(orient="index")
                parsed = loads(result)
                return parsed
            else:
               return None
        except Exception:
            return None
    else:
       return None