from gen_scraper import gen_scraper
import argparse
from datetime import datetime
import pandas as pd


date = datetime.now().strftime('%m-%d_%H%M')

job_title = 'python'
city_list = ['Boston']
results_per_site = 3000

fetch = pd.DataFrame()

for index, city in enumerate(city_list):

    print('\n', city)
    
    param_dict = {'results_per_site' : results_per_site,
        'job_title' : job_title,
        'city' : city, 
        'site_list' : ['indeed', 'glassdoor'], # Indeed, Glassdoor, linkedin
        'linked_in_username' : 'YOUREMAIL',
        'linked_in_password' : 'YOURPASS', 
        'chromedriver_location' : u'Chromedriverloc', # Where chromedriver.exe is
        'run_key' : city[0:1], # Adds these letters to the ID of each pull
        'api_key' : 'yourAPIKey' # Google maps API
    }

    fetch = fetch.append(gen_scraper(**param_dict))

fetch.to_csv('fetch_loop_' + date + '.csv')

print('Shape of result df : ', fetch.shape)

print(fetch.head())