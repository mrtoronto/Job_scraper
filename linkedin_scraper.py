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

def linkedin_scraper(wd, results, job_title, city, linkedin_username, linkedin_password):
    tot_pg = ((results // 25) + 1)
    res_left = results
    print('linkedin total pages: ' + str(tot_pg))
    """login_url = 'https://www.linkedin.com/'
    wd.get(login_url)
    #wd.find_element_by_xpath("//a[@class='sign-in-link']").click
    #wd.find_element_by_xpath("//a[@class='form-toggle']").click
    """
    #pickle.dump( wd.get_cookies() , open("cookies.pkl","wb"))
    #cookies = wd.get_cookie('bcookie')
    
    ID = [('L-ID-' + str(time.strftime("%m%d%Y", time.localtime(time.time()))) + str(n)) for n in range(1, results + 1)]
    #pulldates = [str(time.strftime("%m%d%Y", time.localtime(time.time()))) for n in range(0, results)]
    linkedin_df = pd.DataFrame({'ID' : ID}).set_index('ID', drop=True)
    
    for i in range(tot_pg):
        url = 'http://www.linkedin.com/jobs/search/?keywords=' + job_title + '&location=' + city + '&sortBy=DD&start=' + str(i*25)
        print('Page {} url : {}'.format(i, url))
        wd.get(url)
        
        ### First run through, log into linkedin
        if i == 0:
            ### Sign in button
            wd.find_element_by_xpath("//li[@class='nav-header__link-item nav-header__link-item--jobs-search']").click()
            
            ### Logging in 
            login_email = wd.find_element_by_id("username")
            login_email.send_keys(linkedin_username)
            login_pass = wd.find_element_by_id("password")
            login_pass.send_keys(linkedin_password)
            wd.find_element_by_xpath("//div[@class='login__form_action_container ']").click()
            
            wd.get(url)
            
            ### Change to classic view
            wd.find_element_by_xpath("//div[@id='view-select']").click()
            time.sleep(1)
            wd.find_element_by_xpath("//button[@class='jobs-search-dropdown__option-button jobs-search-dropdown__option-button--single ']").click()
        else: ### If not first run, skip log in and just get url
            wd.get(url)
        
        ### Scroll to bottom and wait then back to top to load all the elements 
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        wd.execute_script("window.scrollTo(0, 0);")
        
        ### Set up res_len as the min(# of jobs on page, # of results left)
        page_len = len(wd.find_elements_by_xpath("//ul[@class='jobs-search-results__list artdeco-list artdeco-list--offset-4']/li"))
        res_len = min(page_len, int(res_left))
        #pg_IDs = ID[i*25:(i+1)*25][:res_len]
        print('page_len : ', page_len, ' // res_len : ', res_len)

        comp_links = []
        #print("elem loop : ", len(wd.find_elements_by_xpath("//ul[@class='jobs-search-results__list artdeco-list artdeco-list--offset-4']/li")))
        #print("trunc elem loop : ", len(wd.find_elements_by_xpath("//ul[@class='jobs-search-results__list artdeco-list artdeco-list--offset-4']/li")[:res_len]))
        
        for index, elem in enumerate(wd.find_elements_by_xpath("//ul[@class='jobs-search-results__list artdeco-list artdeco-list--offset-4']/li")[:res_len]):
            #print(elem.get_attribute('innerHTML'))
            ### Parse the HTML of the element
            soup = BeautifulSoup(elem.get_attribute('innerHTML'), 'html.parser')
            #print(soup.get_text())
            ### Scroll some each time to bring everything into view.
            wd.execute_script("window.scrollBy(0, 150);")
            
            
            ### Set up indexes
            elem_id = ID[(results - res_left)]
            res_left = res_left - 1
            
            ### Debug
            # print("elem_id", elem_id, " // res_left : ", res_left)
            
            ### If comp link spot is None, there isn't a company link
            if soup.find('a', attrs={'data-control-name':'job_card_company_link'}) == None:
                linkedin_df.loc[elem_id, 'comp_link'] = 'NA'
            else:
                linkedin_df.loc[elem_id, 'comp_link'] = 'http://www.linkedin.com' + soup.find('a', attrs={'data-control-name':'job_card_company_link'}).get('href') + 'about'
            
            ### If ezapply spot is None, it ain't easy
            if soup.find('span', attrs={'class':'job-card-search__easy-apply'}) == None:
                linkedin_df.loc[elem_id, 'ezapply'] = 'NA'
            else:
                linkedin_df.loc[elem_id, 'ezapply'] = 'Yes!'
            
            ### Company name
            try:
                linkedin_df.loc[elem_id, 'company'] = soup.find('h4', attrs={'class':'job-card-search__company-name t-14 t-black artdeco-entity-lockup__subtitle ember-view'}).get_text().replace('\n', '').strip()
            except:
                linkedin_df.loc[elem_id, 'company'] = 'NA'
            
            ### Location
            try:
                linkedin_df.loc[elem_id, 'location'] = soup.find('h5', attrs={'class':'job-card-search__location artdeco-entity-lockup__caption ember-view'}).get_text().replace('\n', '')
            except:
                linkedin_df.loc[elem_id, 'location'] = 'NA'
            
            ### Post Link
            try:
                linkedin_df.loc[elem_id, 'post_link'] = 'http://www.linkedin.com' + soup.find('a', attrs={'class':'job-card-search__link-wrapper js-focusable-card ember-view'}).get('href')
            except:
                linkedin_df.loc[elem_id, 'post_link'] = 'NA'
            
            ### Job title
            try:
                linkedin_df.loc[elem_id, 'job_title'] = soup.find('h3', attrs={'class':'job-card-search__title artdeco-entity-lockup__title ember-view'}).get_text().replace('\n', '')
            except:
                linkedin_df.loc[elem_id, 'job_title'] = 'NA'
            
            ### Description 
            try:
                linkedin_df.loc[elem_id, 'brief_descr'] = soup.find('div', attrs={'class':'job-card-search__body'}).get_text().replace('\n', ' ')
            except:
                linkedin_df.loc[elem_id, 'brief_descr'] = 'NA'
    
    
    ### Post links
    for index, link in enumerate(linkedin_df['post_link']):
        wd.get(link)
        
        post_id = ID[index]
        
        ### Scroll to bottom and wait then back to top to load all the elements 
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        wd.execute_script("window.scrollTo(0, 0);")
        try:
            soup = BeautifulSoup(wd.find_element_by_xpath("//div[@class='jobs-top-card ember-view']").get_attribute('innerHTML'), 'html.parser')
        except:
            print(wd.url)
            continue
        body_text = soup.find('div', attrs={'id':'job-details'}).get_text()
        
        body_text = body_text.strip()
        
        linkedin_df.loc[post_id, 'body_text'] = body_text
        try:# mt1 full-width flex-grow-1 t-14 t-black--light
            post_time_line = soup.find('p', attrs={'class' : 'mt1 full-width flex-grow-1 t-14 t-black--light'}).get_text().strip()
            post_time_line = post_time_line.split('\n')[2][7:] ### Grabs the time posted and cuts out posted
            linkedin_df.loc[post_id, 'post_time'] = post_time_line
        except:
            linkedin_df.loc[post_id, 'post_time'] = 'NA'
        #try:
        job_details = soup.find('div', attrs={'class':'jobs-description__details'}).get_text()
        njb = []
        jb = [row.split('\n') for row in job_details.split('\n\n\n') if row.split('n')]
        for top_list in jb:
            njb.append([i for i in top_list if i not in ['', ' ']])
        #print(njb)
        
        for group in njb:
            if len(group) > 1:
                if group[0] == 'Seniority Level':
                    linkedin_df.loc[post_id, 'sen_level'] = '-'.join(group[1:])
                if group[0] == 'Industry':
                    linkedin_df.loc[post_id, 'industry'] = '-'.join(group[1:])
                if group[0] == 'Employment Type':
                    linkedin_df.loc[post_id, 'employ_type'] = '-'.join(group[1:])
                if group[0] == 'Job Functions':
                    linkedin_df.loc[post_id, 'job_fxn'] = '-'.join(group[1:])

            linkedin_df.loc[post_id, 'job_details'] = job_details.replace('\n\n\n', '')
        #except:
            #linkedin_df.loc[post_id, 'job_details'] = 'NA'
    
    ### Comp links
    for index, link in enumerate(linkedin_df['comp_link']):
        wd.get(link)
        
        post_id = ID[index]
        
        ### Scroll to bottom and wait then back to top to load all the elements 
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        wd.execute_script("window.scrollTo(0, 0);")
        
        soup = BeautifulSoup(wd.find_element_by_xpath("//div[@role='main']").get_attribute('innerHTML'), 'html.parser')
        
        try:
            company_overview = soup.find('div', attrs={'class':'org-grid__core-rail--wide'}).get_text()
            linkedin_df.loc[post_id, 'company_overview'] = company_overview[17:]
        except:
            linkedin_df.loc[post_id, 'company_overview'] = 'NA'
            
        try:
            linkedin_df.loc[post_id, 'company_details'] = soup.find('dl', attrs={'class':'overflow-hidden'}).get_text()
        except:
            linkedin_df.loc[post_id, 'company_details'] = 'NA'
            
            
            
    return linkedin_df