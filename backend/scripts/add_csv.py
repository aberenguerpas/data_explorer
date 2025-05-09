import os
import json
from tqdm import tqdm
import concurrent.futures
import polars as pl


def download_multiple_urls(url_list, output_folders):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i, url in enumerate(url_list):
            output_file = output_folders[i]
            futures.append(executor.submit(download_first_50_lines, url, output_file))
        concurrent.futures.wait(futures)  # Wait for all futures to complete



def download_first_50_lines(url, output_file):
    try:
       if 'htm' not in url[-4:]:
        df = pl.read_csv(url, n_rows=12, encoding='utf8', truncate_ragged_lines=True)
        if len(df.columns)>1:
           df.write_csv(output_file)

    except Exception as e:
        print(e)
        print(url)
        return 'Error'


DATA_PATH = '../../datos/'

files = os.listdir(DATA_PATH)
json_file_names = [filename for filename in files if filename.endswith('.json')]

urls = []
output_folders = []
for file in tqdm(json_file_names[52669:]):
    f = open(DATA_PATH + file)
    data = json.load(f)
   
    for r in data['resources']:
        if 'csv' in r['mediaType']:
            urls.append(r['downloadUrl'])
            output_folders.append(DATA_PATH + str(data['id_custom'])+".csv")
            break

download_multiple_urls(urls, output_folders)