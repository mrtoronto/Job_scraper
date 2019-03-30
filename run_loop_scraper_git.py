import pandas as pd
import time 
from datetime import datetime
import math
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request
#import codecs
#import unidecode
import datasheets
import lxml.html
import sys
import pickle
from selenium.webdriver.chrome.options import Options

from gen_scraper import gen_scraper

date = datetime.now().strftime('%m-%d_%H%M')

job_title = 'python'
city_list = ['Boston']
results_per_site = 25

fetch = pd.DataFrame()

for index, city in enumerate(city_list):

    print('\n', city)
    
    param_dict_git = {
    'results' : 8,
    'job_title' : 'python',
    'city' : 'boston',
    'site_list' : ['indeed'],
    'linkedin_username' : 'YOUREMAIL',
    'linkedin_password' : 'YOURPASS',
    'chromedriver_location' : 'YOURCHROMEDRIVERLOC',
    'api_key' : 'APIKEY' ,
    'headless_arg' : True,
    'push_to_docs_flag' : True
    'google_docs_email' : 'DOCSEMAIL', 
    'docs_book' : 'DOCSBOOK', 
    'docs_sheet' : 'test'
}


    fetch = fetch.append(gen_scraper(**param_dict))

fetch.to_csv('fetch_loop_' + date + '.csv')

print('Shape of result df : ', fetch.shape)

print(fetch.head())