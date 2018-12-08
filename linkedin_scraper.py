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

def linkedin_scraper(wd, results, job_title, city, linkedin_username, linkedin_password, run_key):
    tot_pg = ((results // 25) + 1)
    res_left = results
    print('linkedin total pages: ' + str(tot_pg))
    login_url = 'https://www.linkedin.com/'
    wd.get(login_url)
    #wd.find_element_by_xpath("//a[@class='sign-in-link']").click
    #wd.find_element_by_xpath("//a[@class='form-toggle']").click
    login_email = wd.find_element_by_id("login-email")
    login_email.send_keys(linkedin_username)
    login_pass = wd.find_element_by_id("login-password")
    login_pass.send_keys(linkedin_password)
    wd.find_element_by_id("login-submit").click
    #cookies = wd.get_cookie('bcookie')
    id_string_li = 'L-ID-' + run_key + '-'
    ID = [(id_string_li + str(n)) for n in range(0, results)]
    pulldates = [str(time.strftime("%m%d%Y", time.localtime(time.time()))) for n in range(0, results)]
    sites = ['linkedin' for n in range(0, results)]
    linkedin_df = pd.DataFrame({'sID' : ID, 'pulldates' : pulldates, 'site' : sites}).set_index('sID')
    for i in range(tot_pg):
        url = 'http://www.linkedin.com/jobs/search/?keywords=' + job_title + '&location=' + city + '&sortBy=DD&start=' + str(i*25)
        print('Page {} // Page IDS {} // url : {}'.format(i, str(pg_IDs[0], pg_IDs[-1]), url))
        wd.get(url)
        res_len = min(len(wd.find_elements_by_xpath("//li[@class='job-listing']")), int(res_left))
        pg_IDs = ID[i*res_len:(i+1)*res_len] # Gets 25 IDs relevant to page
        companies = [c.text for c in wd.find_elements_by_xpath("//span[@class='company-name-text']")]
        locations = [L.text for L in wd.find_elements_by_xpath("//span[@class='job-location']/span")]
        comp_links = []
        #for elem in wd.find_elements_by_xpath("//div[@class='company-name']"):
        #    if elem.find_element_by_xpath("/a[@class='company-name-link']") == None:
        #        comp_links.append('NA')
        #    else:
        #        comp_links.append(elem.find_element_by_xpath("/a[@class='company-name-link']").get_attribute('href'))
        #linkedin_df.loc[pg_IDs, 'comp_links'] = comp_links
        linkedin_df.loc[pg_IDs, 'post_links'] = [l.get_attribute('href') for l in wd.find_elements_by_xpath("//a[@class='job-title-link']")][:res_len]
        linkedin_df.loc[pg_IDs, 'titles'] = [t.text.split('\n')[0] for t in wd.find_elements_by_xpath("//div[@class='job-title-line']")][:res_len]
        linkedin_df.loc[pg_IDs, 'locations'] = [L.text for L in wd.find_elements_by_xpath("//span[@class='job-location']/span")][:res_len]
        linkedin_df.loc[pg_IDs, 'companies'] = [c.text for c in wd.find_elements_by_xpath("//span[@class='company-name-text']")][:res_len]
        linkedin_df.loc[pg_IDs, 'brief_sum'] = [d.text for d in wd.find_elements_by_xpath("//div[@class='job-description']")][:res_len]
        linkedin_df.loc[pg_IDs, 'ezapply'] = [e.text for e in wd.find_elements_by_xpath("//div[@class='job-flavor-in-apply-container']")][:res_len]
        linkedin_df.loc[pg_IDs, 'company_pics'] = [i.get_attribute('src') for i in wd.find_elements_by_xpath("//a[@class='company-logo-link']//img")][:res_len]

        comp_loc = []
        for i, elem in enumerate(companies):
            comp_loc_str = (''.join(elem.strip().split(',')[1:]) + ', ' + locations[i].strip())
            comp_loc.append(comp_loc_str)
        linkedin_df.loc[pg_IDs, 'comp_loc'] = comp_loc[:res_len]
        res_left = res_left - res_len
    return linkedin_df