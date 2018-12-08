import pandas as pd
import time 
#import ast
#from all_functions import *
import math
import requests
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
from selenium import webdriver
import os
import subprocess
import urllib.request
import codecs
import unidecode
import sys
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from linkedin_scraper import linkedin_scraper
from stack_scraper import stack_scraper
from indeed_scraper import indeed_scraper
from glassdoor_scraper import glassdoor_scraper, glassdoor_scraper_parser

def gen_scraper(**scrap_params):
    
    results = scrap_params['results_per_site']
    job_title = scrap_params['job_title']
    city = scrap_params['city'] 
    site_list = scrap_params['site_list']
    linkedin_username = scrap_params['linked_in_username'] 
    linkedin_password = scrap_params['linked_in_password']
    chromedriver_location = scrap_params['chromedriver_location'] 
    api_key = scrap_params['api_key'] 
    run_key = scrap_params['run_key']
    
    file = 1
    SKIPPER = 0 # Skips this many of the first jobs

    num = 0
    
    headless_options = Options()
    not_headless_options = Options()
    
    headless_arg_list = ['--headless', '--disable-gpu', 'start-maximized', 'disable-infobars', '--disable-extensions', '--log-level=3']
    for arg in headless_arg_list:
        headless_options.add_argument(arg)
    
    not_headless_arg_list = ['--disable-gpu', 'start-maximized', 'disable-infobars', '--disable-extensions', '--log-level=3']
    for arg in not_headless_arg_list:
        not_headless_options.add_argument(arg)
        
    job_df = pd.DataFrame()
    for site in site_list: 
        site_ind = results
        if site == 'stack':
            stack_df = stack_scraper(wd, results, job_title, city)
            job_df = job_df.append(stack_df, sort=False)
            wd.quit()
        if site == 'indeed':
            wd = webdriver.Chrome(chromedriver_location, options=headless_options)
            indeed_df = indeed_scraper(wd, results, job_title, city, run_key)
            job_df = job_df.append(indeed_df, sort=False)
            wd.quit()
        if site == 'linkedin':
            wd = webdriver.Chrome(chromedriver_location, options=headless_options)
            linkedin_df = linkedin_scraper(wd, results, job_title, city, linkedin_username, linkedin_password, run_key)
            job_df = job_df.append(linkedin_df, sort=False)
            wd.quit()
        if site == 'glassdoor':
            wd = webdriver.Chrome(chromedriver_location, options=not_headless_options)
            glassdoor_df = glassdoor_scraper(wd, results, job_title, city)
            job_df = job_df.append(glassdoor_scraper_parser(glassdoor_df), sort=False)
            wd.quit()
    return job_df
    
    companies = job_df['comp_loc']
    ids = job_df.index.tolist()
    
    
    
    comm_df = dist_duration(companies, ids, api_key)

    fin_df = job_df.merge(comm_df, how = 'left', left_index=True, right_on=['ID']).drop(columns=['company_x']).rename({'company_y' : 'company'}, axis='columns')

    file = file + 1

    output_dict = {'job_title' : job_title, 'city' : city}
    return fin_df
