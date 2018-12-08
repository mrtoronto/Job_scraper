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

def stack_scraper(wd, results, job_title, city):
    
    res_left = results
    tot_pg = ((results // 25) + 1)
    print('stack total pages: ' + str(tot_pg))
    #print('indeed total pages: ' + str(tot_pg))
    ID = [str('s-ID-' + str(n)) for n in range(0, results)]
    pulldates = [str(time.strftime("%m%d%Y", time.localtime(time.time()))) for n in range(0, results)]
    stack_df = pd.DataFrame({'sID' : ID, 'pulldates' : pulldates}).set_index('sID')
    for i in range(tot_pg):
        url = 'https://stackoverflow.com/jobs?q=python&sort=p&l=boston&d=20&u=Miles&start=' + str(i*25)

        print(url)
        wd.get(url)
        test_len = len([comp_loc.text for comp_loc in wd.find_elements_by_xpath("//div[@class='-job-summary']/div[contains(@class, '-company')]")])
        
        res_len = min(test_len, int(res_left))
        
        pg_IDs = ID[i*res_len:(i+1)*res_len]
        post_links = [title.get_attribute('href') for title in wd.find_elements_by_xpath("//h2[@class='fs-subheading job-details__spaced mb4']//a")][:res_len]
        
        #################### search results ####################     
        #comp_locs = [comp_loc.text for comp_loc in wd.find_elements_by_xpath("//div[@class='-job-summary']/div[contains(@class, '-company')]")]
        stack_df.loc[pg_IDs, 'comp_locs'] = [comp_loc.text for comp_loc in wd.find_elements_by_xpath("//div[@class='-job-summary']/div[contains(@class, '-company')]")][:res_len]
        

        #l_companies = [company.text.lower().split(',')[0] for company in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='company']")]
        stack_df.loc[pg_IDs, 'titles'] = [title.text for title in wd.find_elements_by_xpath("//h2[@class='fs-subheading job-details__spaced mb4']")][:res_len]
        #stack_df.loc[pg_IDs, 'comp_links'] = ['https://www.stackoverflow.com/jobs/company/' + company.text.replace(' ', '-') for company in wd.find_elements_by_xpath("//div[@class='fc-black-700 fs-body2 -company']")][:res_len]
        #stack_df.loc[pg_IDs, 'tags'] = [tag.text for tag in wd.find_elements_by_xpath("//div[@class='mt12 -tags']")][:res_len]
        #stack_df.loc[pg_IDs, 'perks'] = [perk.text for perk in wd.find_elements_by_xpath("//div[@class='mt2 -perks']")]
        stack_df.loc[pg_IDs, 'postdates'] = [date.text for date in wd.find_elements_by_xpath("//span[contains(@class, 'ps-absolute pt2 r0 fc-black-500 fs-body1 pr12')]")][:res_len]
        #description = [description.text for description in wd.find_elements_by_xpath("//div[@data-tn-component='organicJob']//span[@class='summary']")]
        stack_df.loc[pg_IDs, 'post_links'] = [title.get_attribute('href') for title in wd.find_elements_by_xpath("//h2[@class='fs-subheading job-details__spaced mb4']//a")][:res_len]


        #comp_links = ['https://www.indeed.com/cmp/' + str(company).replace(' ', '-') for company in companies]                    

        '''        if res_len < 25:
            comp_locs = comp_locs[:res_len]
            titles = titles[:res_len]
            tags = tags[:res_len]
            perks = perks[:res_len]
            post_links = post_links[:res_len]
            postdates = postdates[:res_len]
            comp_links = comp_links[:res_len]'''
            
            
        #ID = [str('s-ID-' + str(n)) for n in range(results-res_left, results-res_left+len(comp_locs))]
        #comp_loc = ['' for n in range(results-res_left, results-res_left+len(comp_locs))]
        #companies = [company.split(' - ')[0] for company in comp_locs]
        #locations = [location.split(' - ')[1] for location in comp_locs]
                    
        res_left = res_left - res_len

        #print(len(titles), len(companies), len(post_links), len(postdates), len(pulldates), len(comp_links))
        #return 'bitch'
        #stack_df = pd.DataFrame({'ID' : ID, 'title' : titles, 'company' : companies, 'post_link' : post_links, 'comp_link' : comp_links, 'postdate' : postdates, 'pulldate' : pulldates}).set_index('ID') # functional

        
        #################### post list ####################     
        post_list = []
        for index, link in enumerate(post_links):
            post_id = ID[index]
            wd.get(link)
            #average_comp_rating = wd.find_element_by_xpath("//span[@class='cmp-header-rating-average']").text
            stack_df.loc[post_id, 'body'] = wd.find_element_by_xpath("//div[@id='overview-items']").text
            stack_df.loc[post_id, 'comp_link'] = wd.find_element_by_xpath("//a[@class='fc-black-700']").get_attribute('href')
            #tags = [tag.text for tag in wd.find_elements_by_xpath("div[@id='overview-items']//a[@class='post-tag job-link no-tag-menu']")]
            #stack_df.loc[post_id, 'tags'] = ', '.join(tags)
            
            try:
                stack_df.loc[post_id, 'benefits'] = wd.find_element_by_xpath("//section[@class='-benefits mb32']").text
            except:
                stack_df.loc[post_id, 'benefits'] = ''
                #print(link)
            res_len = res_len - len(post_links)    
            
            #post_list.append([str(index), body, benefits])
        #comp_df = pd.DataFrame(post_list, columns=['ID', 'body_text', 'benefits']).set_index('ID')
        #stack_df = stack_df.merge(comp_df)
    return stack_df