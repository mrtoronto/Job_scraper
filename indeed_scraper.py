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

def indeed_scraper(wd, results, job_title, city, run_key):
    list_o_divs = []
    #tot_pg = ((results // 10) + 1)
    res_left = results
    tot_pg = ((results // 10)+1)
    print('indeed total pages: ' + str(tot_pg))
    id_string_indeed = 'i-ID-' + run_key + '-'
    ID = [(id_string_indeed + str(n)) for n in range(0, results)]
    pulldates = [str(time.strftime("%m%d%Y", time.localtime(time.time()))) for n in range(0, results)]
    sites = ['indeed' for n in range(0, results)]
    indeed_df = pd.DataFrame({'sID' : ID, 'pulldate' : pulldates, 'site' : sites }).set_index('sID')
    for i in range(tot_pg):
        listing_len = len(wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']"))
        res_len = min(10, int(res_left))
        url = 'https://www.indeed.com/jobs?q=' + job_title + '&l=' + city + '&start=' + str(i*10) + '&sort=' + 'date' + '&radius=' + '25'
        pg_IDs = ID[i*res_len:(i+1)*res_len] # Gets IDs relevant to page
        try:
            pg_id_start = pg_IDs[0]
        except:
            return indeed_df
        pg_id_end = pg_IDs[-1]
        pg_ids_str = pg_IDs[0] + ', ' + pg_IDs[-1]
        print('Page {} // Page IDS {} // url : {}'.format(i, pg_ids_str, url))
        print(res_len)
        wd.get(url)
        search_count = wd.find_element_by_xpath("//div[@id='searchCount']").text.split(' ')[3].replace(',', '')
        if i == 0:
            if res_left > int(search_count):
                res_left = int(search_count)
            print('Res_left = ', res_left, 'search count : ', search_count)
        time.sleep(2)
        #################### search results ####################     
        try:
            indeed_df.loc[pg_IDs, 'company'] = [company.text for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:res_len]
        except:
            print(len([company.text for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:res_len]))
        #indeed_df.loc[pg_IDs, 'l_companies'] = [company.text.lower().split(',')[0] for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:res_len]
        indeed_df.loc[pg_IDs, 'title'] = [title.text for title in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//h2[@class='jobtitle']")][:res_len]
        indeed_df.loc[pg_IDs, 'ex_summary'] = [description.text for description in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='summary']")][:res_len]
        indeed_df.loc[pg_IDs, 'post_link'] = [post_link.get_attribute('href') for post_link in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//h2[@class='jobtitle']//a")][:res_len]
        indeed_df.loc[pg_IDs, 'comp_link'] = ['https://www.indeed.com/cmp/' + str(company.text).replace(' ', '-') for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:res_len]           
        post_links = [post_link.get_attribute('href') for post_link in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//h2[@class='jobtitle']//a")][:res_len]
        comp_links = ['https://www.indeed.com/cmp/' + str(company).replace(' ', '-') for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:res_len]

        #################### comp list ####################
        comp_list = []
        for index, link in enumerate(comp_links):
            index = pg_IDs[index]
            wd.get(link)
            try:
                indeed_df.loc[index, 'salaries_link'] = 'https://www.indeed.com/cmp/' + wd.find_element_by_xpath("//div[@class='cmp-company-name-container']").text + '/salaries/'
                indeed_df.loc[index, 'reviews_link'] = 'https://www.indeed.com/cmp/' + wd.find_element_by_xpath("//div[@class='cmp-company-name-container']").text + '/reviews/'
            except:
                indeed_df.loc[index, 'salaries_link'] = ''
                indeed_df.loc[index, 'reviews_link'] = ''

        #################### Post list ####################     
        post_list = []
        for index, link in enumerate(post_links):
            index = pg_IDs[index]
            wd.get(link)
            #indeed_df.loc[index, 'jobtitle'] = wd.find_element_by_xpath("//h3[contains(@class, 'jobsearch-JobInfoHeader-title')]").text
            try:
                indeed_df.loc[index, 'average_comp_rating'] = wd.find_element_by_xpath("//meta[@itemprop='ratingValue']").get_attribute('content')
                indeed_df.loc[index, 'number_of_comp_ratings'] = wd.find_element_by_xpath("//meta[@itemprop='ratingCount']").get_attribute('content')
            except:
                indeed_df.loc[index, 'average_comp_rating'] = 'NA'
                indeed_df.loc[index, 'number_of_comp_ratings'] = 'NA'
            try:
                indeed_df.loc[index, 'company_pic'] = wd.find_element_by_xpath("//img[@class='jobsearch-CompanyAvatar-image']").get_attribute('src')
            except:
                indeed_df.loc[index, 'company_pic'] = 'NA'
            try:
                line = wd.find_element_by_xpath("//div[contains(@class, 'jobsearch-InlineCompanyRating')]").text
                indeed_df.loc[index, 'location'] = line.split('\n')[-1]
                indeed_df.loc[index, 'comp_loc'] = line.split('\n')[0] + ', ' + line.split('\n')[-1]
            except:
                indeed_df.loc[index, 'location'] = 'NA'
                indeed_df.loc[index, 'comp_loc'] = 'NA'
            indeed_df.loc[index, 'body'] = wd.find_element_by_xpath("//div[contains(@class, 'jobsearch-JobComponent-description')]").text
            indeed_df.loc[index, 'post_time'] = wd.find_element_by_xpath("//div[@class='jobsearch-JobMetadataFooter']").text.split(' - ')[1].strip()
        
        res_left = res_left - res_len
        with open('indeed_archive.csv', 'w', encoding='utf-8') as f:
            indeed_df.to_csv(f, header=False)
    return indeed_df