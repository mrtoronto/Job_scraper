import pandas as pd
import time 
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

from indeed_scraper import indeed_scraper
from docs_push import push_to_docs
from linkedin_scraper import linkedin_scraper

def gen_scraper(results, job_title, city, site_list, linkedin_username, linkedin_password, chromedriver_location, api_key, headless_arg, push_to_docs_flag=False, google_docs_email, docs_book, docs_sheet):

    options = Options()
    for arg in [ '--no-sandbox', '--disable-gpu', 'start-maximized', 'disable-infobars', '--disable-extensions']:
        options.add_argument(arg)
    if headless_arg == True:
        options.add_argument('--headless')
    wd = webdriver.Chrome(chromedriver_location, options=options)
    
    job_df = pd.DataFrame()
    
    for site in site_list: 
        
        if site == 'stack':
            stack_df = stack_scraper(wd, results, job_title, city)
            job_df = job_df.append(stack_df, sort=False)
            
        if site == 'indeed':
            indeed_df = indeed_scraper(wd, results, job_title, city)
            job_df = job_df.append(indeed_df, sort=False)
            
                    
        if site == 'linkedin':
            linkedin_df = linkedin_scraper(wd, results, job_title, city, linkedin_username, linkedin_password)
            job_df = job_df.append(linkedin_df, sort=False)
            
    wd.stop_client()
    wd.quit()
    
    if push_to_docs_flag == True:
        push_to_docs(df=job_df, email=google_docs_email, book_name=docs_book, sheet_name=docs_sheet)
    return job_df