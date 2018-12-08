import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
import re
import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def glassdoor_scraper(wd, results, job_title, city):
    
    res_left = results
    tot_pg = ((results // 31)) + 1
    print('glassdoor total pages: ' + str(tot_pg))
    
    id_string_indeed = 'g-ID-' + 'a' + '-'
    ID = [(id_string_indeed + str(n)) for n in range(0, results)]
    pulldates = [str(time.strftime("%m%d%Y", time.localtime(time.time()))) for n in range(0, results)]
    sites = ['glassdoor' for n in range(0, results)]
    glassdoor_df = pd.DataFrame({'sID' : ID, 'pulldate' : pulldates, 'site' : sites }).set_index('sID')
    
    my_dict = {'boston' : '1154532', 'seattle' : '1150505', 'worcestor' : '1154962', 'Worcester, MA' : '1154962'}
    if city.lower() in my_dict.keys():
        city_id = my_dict[city]
    else:
        print('City not in city list. Blank DF returned.')
        return glassdoor_df
    
    print('Number of results : {}'.format(results))
    url = 'https://www.glassdoor.com/Job/jobs.htm?typedKeyword=' + job_title + '&sc.keyword=' + job_title + '&locT=C&locId=' + city_id
    post_list = []
    print('Url : ', url)
    wd.get(url)

    df_index = 0
    print('Res_left = {}'.format(res_left))
    for i in range(tot_pg):
        time.sleep(5)
        print('page : ', str(i), '\nurl : ', str(wd.current_url))
        jl_list = wd.find_elements_by_xpath("//ul[@class='jlGrid hover']/li[@class='jl']/div/a")
        res_len = min(len(jl_list), res_left)
        jl_list_len = len(jl_list)
        print('jl_list_len : ', jl_list_len)
        
        for j in range(0, res_len): # each job on the page            
            # Default Page AKA "Job"
            post_ind = ID[df_index]
            time.sleep(2)
            glassdoor_df.loc[post_ind, 'title'] = wd.find_element_by_xpath("//div[@class='header']").text
            glassdoor_df.loc[post_ind, 'company'] = wd.find_element_by_xpath("//div[@class='compInfo']").text
            glassdoor_df.loc[post_ind, 'jobdescription'] = wd.find_element_by_xpath("//div[@id='JobDescriptionContainer']").text
            try:
                glassdoor_df.loc[post_ind, 'sal_est'] = wd.find_element_by_xpath("//span[@class='green small salary']").text
            except:
                glassdoor_df.loc[post_ind, 'sal_est'] = ''
            
            # Company Page
            actions = webdriver.ActionChains(wd)
            try: # try clicking company button
                actions.move_to_element(wd.find_element_by_xpath("//li[@data-tab-type='overview']")).perform()
                wd.find_element_by_xpath("//li[@data-tab-type='overview']").click()
                glassdoor_df.loc[post_ind, 'comp_overview'] = wd.find_element_by_xpath("//div[@class='info row']").text
            except: # if initial click on "Company" fails
                try:
                    wd.find_element_by_xpath("//div[@class='xBtn']").click()
                    wd.find_element_by_xpath("//li[@data-tab-type='overview']").click()
                    glassdoor_df.loc[post_ind, 'comp_overview'] = wd.find_element_by_xpath("//div[@class='info row']").text
                    # job tab stuff
                except: # Prolly not company at this point
                    # name same variables but blank or something
                    glassdoor_df.loc[post_ind, 'comp_overview'] = ''
                    
            # Ratings Page
            actions = webdriver.ActionChains(wd)
            try: # try clicking Rating button
                actions.move_to_element(wd.find_element_by_xpath("//li[@data-tab-type='rating']")).perform()
                wd.find_element_by_xpath("//li[@data-tab-type='rating']").click()
                glassdoor_df.loc[post_ind, 'average_comp_rating'] = wd.find_element_by_xpath("//div[@class='ratingNum margRtSm']").text
                glassdoor_df.loc[post_ind, 'ceo_approval'] = wd.find_element_by_xpath("//div[contains(@class, 'ceoApprove')]").text[:-1]
                glassdoor_df.loc[post_ind, 'ceo_info'] = wd.find_element_by_xpath("//div[@class='gfxContainer']").text
            except: # if initial click on "Company" fails
                try:
                    wd.find_element_by_xpath("//div[@class='xBtn']").click()
                    wd.find_element_by_xpath("//li[@data-tab-type='rating']").click()
                    glassdoor_df.loc[post_ind, 'average_rating'] = wd.find_element_by_xpath("//div[@class='ratingNum margRtSm']").text
                    glassdoor_df.loc[post_ind, 'ceo_approval'] = wd.find_element_by_xpath("//div[contains(@class, 'ceoApprove')]").text
                    glassdoor_df.loc[post_ind, 'ceo_info'] = wd.find_element_by_xpath("//div[@class='gfxContainer']").text
                    # rating tab stuff
                except: # Prolly not company at this point // No x button to click but still no tab
                    # name same variables but blank or something
                    glassdoor_df.loc[post_ind, 'average_rating'] = ''
                    glassdoor_df.loc[post_ind, 'ceo_approval'] = ''
                    glassdoor_df.loc[post_ind, 'ceo_info'] = ''
            
            # Location Page
            actions = webdriver.ActionChains(wd)
            try: # try clicking Rating button
                actions.move_to_element(wd.find_element_by_xpath("//li[@data-tab-type='map']")).perform()
                wd.find_element_by_xpath("//li[@data-tab-type='map']").click()
                glassdoor_df.loc[post_ind, 'location'] = wd.find_element_by_xpath("//div[@class='padBotSm']").text
            except: # if initial click on "Company" fails
                try:
                    wd.find_element_by_xpath("//div[@class='xBtn']").click()
                    wd.find_element_by_xpath("//li[@data-tab-type='map']").click()
                    glassdoor_df.loc[post_ind, 'location'] = wd.find_element_by_xpath("//div[@class='padBotSm']").text
                    # rating tab stuff
                except: # Prolly not company at this point // No x button to click but still no tab
                    # name same variables but blank or something
                    glassdoor_df.loc[post_ind, 'location'] = ''
                    
            # Benefits Page
            actions = webdriver.ActionChains(wd)
            try: # try clicking Rating button
                actions.move_to_element(wd.find_element_by_xpath("//li[@data-tab-type='benefits']")).perform()
                wd.find_element_by_xpath("//li[@data-tab-type='benefits']").click()
                glassdoor_df.loc[post_ind, 'emp_bene'] = wd.find_element_by_xpath("//div[@class='borderBot empSummary']").text
            except: # if initial click on "Company" fails
                try:
                    wd.find_element_by_xpath("//div[@class='xBtn']").click()
                    wd.find_element_by_xpath("//li[@data-tab-type='benefits']").click()
                    glassdoor_df.loc[post_ind, 'emp_bene'] = wd.find_element_by_xpath("//div[@class='borderBot empSummary']").text
                except: # Prolly not company at this point // No x button to click but still no tab
                    # name same variables but blank or something
                    glassdoor_df.loc[post_ind, 'emp_bene'] = ''
            
                
            # Non data columns
            #sID = 'g-ID-' + str(i * 32 + j)#[('s-ID-' + str(n)) for n in range(num, num + res_len)]
            #pulldate = str(time.strftime("%m%d%Y", time.localtime(time.time())))
            #append_list = [title, companies, sal_est, sID, pulldate, comp_overview, ceo_info, average_rating, ceo_approval, location]
            #post_list.append(append_list)
            #print(append_list)
            #post_list.append([companies, sal_est, body_text, comp_info, comp_rating, ratings_line, ratings_trends, salary_link, review_link, location, empSummary])
            #wd.find_elements_by_xpath("//ul[@class='jlGrid hover']/li[@class='jl']//div[@class='logoWrap']")[j].click()
            actions = webdriver.ActionChains(wd)
            actions.move_to_element(jl_list[j]).perform()
            try:
                jl_list[j].click()
            except:
                wd.find_element_by_xpath("//div[@class='xBtn']").click()
                jl_list[j].click()
            
            if (df_index + 1 == results):
                wd.close()
                print('success')
                return glassdoor_df
            else:
                df_index = df_index + 1
                res_left = res_left - 1
                print('df_index : ', df_index, ' // res_left : ', res_left, ' // Job Title : ', str(glassdoor_df.loc[post_ind, 'title']))
                #print('res_left : ', res_left)
        if i < tot_pg:
            with open('glassdoor_archive.csv', 'w', encoding='utf-8') as f:
                glassdoor_df.to_csv(f, header=False)
            
            action = webdriver.ActionChains(wd)
            element = wd.find_element_by_xpath('//div[@id="ResultsFooter"]')
            action.move_to_element(element)
            wd.find_element_by_xpath("//div[contains(@class,'pagingControls')]//li[@class='next']").click()
    
def glassdoor_scraper_parser(og_glassdoor_df):
    glassdoor_df = og_glassdoor_df.copy()
    id_string_indeed = 'g-ID-' + 'a' + '-'
    ID = [(id_string_indeed + str(n)) for n in range(0, len(glassdoor_df))]

    for index in ID:
        try:
            glassdoor_df.loc[index, 'company']  = glassdoor_df.loc[index, 'company'].split('–')[0][5:]
        except:
            return glassdoor_df
        
        ###### Salary boi
        try:
            glassdoor_df.loc[index, 'lower_sal'] = glassdoor_df.loc[index, 'sal_est'].split('k')[0][1:] + '000'
            glassdoor_df.loc[index, 'upper_sal'] = glassdoor_df.loc[index, 'sal_est'].split('k')[1][2:] + '000'
            glassdoor_df.loc[index, 'sal_est'] = glassdoor_df.loc[index, 'sal_est'][:-16]
        except:
            glassdoor_df.loc[index, 'upper_sal'] = ''
            glassdoor_df.loc[index, 'lower_sal'] = ''
            glassdoor_df.loc[index, 'sal_est'] = ''
                
        # ceo_info
        ceo_info_list = glassdoor_df.loc[index, 'ceo_info'].split('\n')
        try:
            glassdoor_df.loc[index, 'per_rec_friend'] = ceo_info_list[0][:-1]
            glassdoor_df.loc[index, 'per_app_ceo'] = ceo_info_list[2][:-1]
            glassdoor_df.loc[index, 'ceo_name'] = ceo_info_list[4]
            glassdoor_df.loc[index, 'num_ratings'] = ceo_info_list[5][:-8]
        except:
            glassdoor_df.loc[index, 'per_rec_friend'] = ''
            glassdoor_df.loc[index, 'per_app_ceo'] = ''
            glassdoor_df.loc[index, 'ceo_name'] = ''
            glassdoor_df.loc[index, 'num_ratings'] = ''
        
        try: # comp_overview
            comp_overview_list = glassdoor_df.loc[index, 'comp_overview'].split('\n')
            #glassdoor_df.loc[index, 'comp_overview'] = glassdoor_df.loc[index, 'comp_overview'].split('\n')
            HQ_patt = re.compile('(^Headquarters)')
            size_patt = re.compile('(Size).+$')
            found_patt = re.compile('(^Founded).+$')
            type_patt = re.compile('(^Type).+$')
            revenue_patt = re.compile('(^Revenue).+$')
            compet_patt = re.compile('(^Competitors).+$')
            sect_patt = re.compile('(^Sector).+$')
            industry_patt = re.compile('(^Industry).+$')
            
            for line in comp_overview_list:
                for patt, col in [[HQ_patt, 'HQ_loc'], [size_patt, 'comp_size'], [found_patt, 'year_founded'], [type_patt, 'comp_type'], [revenue_patt, 'comp_rev'], [compet_patt, 'compet'], [sect_patt, 'comp_sect'], [industry_patt, 'comp_industy']]:
                    if re.search(patt, line) is not None:
                        if col == 'HQ_loc':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[12:]
                        if col == 'comp_size':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[4:-9]
                        if col == 'year_founded':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[7:]
                        if col == 'comp_type':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[4:]
                        if col == 'comp_rev':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[7:]
                        if col == 'compet':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[11:]
                        if col == 'comp_sect':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[6:]
                        if col == 'comp_industy':
                            glassdoor_df.loc[index, col] = re.search(patt, line).group()[8:]
                        
        except: # comp_overview
            glassdoor_df.loc[index, 'HQ_loc'] = line
            glassdoor_df.loc[index, 'comp_size'] = ''
            glassdoor_df.loc[index, 'year_founded'] = ''
            glassdoor_df.loc[index, 'comp_type'] = ''
            glassdoor_df.loc[index, 'comp_rev'] = ''
            glassdoor_df.loc[index, 'compet'] = ''
            glassdoor_df.loc[index, 'comp_sect'] = '' 
            glassdoor_df.loc[index, 'comp_indu'] = ''
            
    glassdoor_df = glassdoor_df.drop(['comp_overview', 'ceo_info', 'sal_est'], inplace=False, axis='columns')
    return glassdoor_df