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

def indeed_scraper(wd, results, job_title, city):
    list_o_divs = []
    #tot_pg = ((results // 10) + 1)
    res_left = results
    tot_pg = ((results // 10) + 1)
    print('indeed total pages: ' + str(tot_pg))
    #print('indeed total pages: ' + str(tot_pg))
    ID = [('i-ID-'  + str(time.strftime("%m%d%Y", time.localtime(time.time()))) + '-' + str(n)) for n in range(0, results)]
    indeed_df = pd.DataFrame({'ID' : ID}).set_index('ID')
    #################### search results ####################     
    for i in range(tot_pg):
        
        ### Put together URL string and then get the page
        url = 'https://www.indeed.com/jobs?q=' + job_title + '&l=' + city + '&start=' + str(i*10) + '&sort=' + 'date' + '&radius=' + '25'
        print('Page {} url : {}'.format(i, url))
        wd.get(url)
        
        ### Gets 10 IDs relevant to page
        pg_IDs = ID[i*15:(i+1)*15]
        
        ### Length of page
        listing_len = len(wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']"))
        
        ### minimum between the (number of results on the page, number of results left to scrap)
        result_length = min(listing_len, int(res_left)) 
        
        ### Scrap different parts of page into `result_length` length lists and put them in the df
        indeed_df.loc[pg_IDs, 'company_name'] = [company.text for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:result_length]
        #indeed_df.loc[pg_IDs, 'job_title'] = [title.text for title in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//h2[@class='jobtitle']")][:result_length]
        indeed_df.loc[pg_IDs, 'location'] = [title.text for title in wd.find_elements_by_xpath("//span[@class='location']")][:result_length]
        indeed_df.loc[pg_IDs, 'description'] = [description.text for description in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='summary']")][:result_length]
        indeed_df.loc[pg_IDs, 'post_link'] = [post_link.get_attribute('href') for post_link in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//h2[@class='jobtitle']//a")][:result_length]
        indeed_df.loc[pg_IDs, 'comp_link'] = ['https://www.indeed.com/cmp/' + str(company.text).replace(' ', '-') for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:result_length]
        post_links = [post_link.get_attribute('href') for post_link in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//h2[@class='jobtitle']//a")][:result_length]
        comp_links = ['https://www.indeed.com/cmp/' + str(company).replace(' ', '-') for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")][:result_length]
        
        ### Subtract length of this page of results from the total results left
        res_left = res_left - result_length
        
        # Repeat loop through `tot_pg` pages then go to next section

    #################### comp list ####################     
    comp_list = []
    comp_links = indeed_df['comp_link']
    for index, link in enumerate(comp_links):
        index = ID[index]
        wd.get(link)
        
        ### If it can't find the company name or either link, just call the whole thing off
        try:
            indeed_df.loc[index, 'company_name'] = wd.find_element_by_xpath("//div[@class='cmp-company-name-container']").text
            indeed_df.loc[index, 'salaries_link'] = 'https://www.indeed.com/cmp/' + wd.find_element_by_xpath("//div[@class='cmp-company-name-container']").text + '/salaries/'
            indeed_df.loc[index, 'reviews_link'] = 'https://www.indeed.com/cmp/' + wd.find_element_by_xpath("//div[@class='cmp-company-name-container']").text + '/reviews/'
            try:
                indeed_df.loc[index, 'average_comp_rating'] = wd.find_element_by_xpath("//span[@class='cmp-header-rating-average']").text
            except:
                indeed_df.loc[index, 'average_comp_rating'] = 'Not ranked.'
        except:
            indeed_df.loc[index, 'company_name'] = ''
            indeed_df.loc[index, 'salaries_link'] = ''
            indeed_df.loc[index, 'reviews_link'] = ''
            continue

    #################### Post list ####################     
    post_list = []
    post_links = indeed_df['post_link']
    for index, link in enumerate(post_links):
        index = ID[index]
        wd.get(link)
        line = wd.find_element_by_xpath("//div[contains(@class, 'jobsearch-InlineCompanyRating')]").text
        indeed_df.loc[index, 'company_location'] = line.split('\n')[0] + ', ' + line.split('\n')[-1]
        
        indeed_df.loc[index, 'job_title'] = wd.find_element_by_xpath("//h3[contains(@class, 'jobsearch-JobInfoHeader-title')]").text
        indeed_df.loc[index, 'post_body'] = wd.find_element_by_xpath("//div[contains(@class, 'jobsearch-JobComponent-description')]").text
        indeed_df.loc[index, 'post_time'] = wd.find_element_by_xpath("//div[@class='jobsearch-JobMetadataFooter']").text.split(' - ')[1].strip()
        
    #################### Column Rename and Reorder ####################  
    return indeed_df