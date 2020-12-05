# -*- coding: utf-8 -*-
"""

@author: Adrien Wehrlé, GEUS (Geological Survey of Denmark and Greenland)

"""


import urllib.request
from urllib.error import URLError
import pandas as pd
import numpy as np
import os
from multiprocessing import Pool, freeze_support
import time
import requests
from bs4 import BeautifulSoup


path = '/path/to/Github_repository/'

# load station metadata 
metadata_filename = path + 'GHCNv4_stations.txt'
stations_metadata = pd.read_csv(metadata_filename, delimiter=r"\s+")

# select all stations above min_latitude
min_latitude = 66.5
arctic_stations = stations_metadata[(stations_metadata.Lat > min_latitude) 
                                    & valid_stations
                                    & (stations_metadata.Station != 'nan')]

arctic_stations.reset_index(inplace=True, drop=True)


def GISTEMP_autodownload(k):
    
    # extract station metadata
    station = arctic_stations.iloc[k, :]
          
    try:
        
        # access website
        response = requests.get('https://data.giss.nasa.gov/cgi-bin/gistemp/'
                                + 'stdata_show_v4.cgi?id=' + station.ID 
                                + '&ds=14&dt=1')
        
        # parse html
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # extract hyperlink 
        a_tag = soup.findAll('a')[15]
        link = a_tag['href']
        
        # download file path
        download_url = 'https://data.giss.nasa.gov/' + link
        urllib.request.urlretrieve(download_url, path + 'GHCN_v4_data'
                                    + os.sep + station.ID + '.csv')
        
        print(k, 'Downloading %s' % download_url)
    
    except URLError:
        print(k, '%s not found' % station)
        
        return   


if __name__ == '__main__':

    freeze_support()
    
    nb_cores = 7
    
    start_time = time.time()
    start_local_time = time.ctime(start_time)
    
    with Pool(nb_cores) as p:
        p.map(GISTEMP_autodownload, range(0, len(arctic_stations)))
        
    end_time = time.time()
    end_local_time = time.ctime(end_time)
    processing_time = (end_time - start_time) / 60
    print("--- Processing time: %s minutes ---" % processing_time)
    print("--- Start time: %s ---" % start_local_time)
    print("--- End time: %s ---" % end_local_time)
