# import packages
import re
import bs4
from bs4 import BeautifulSoup
import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument('--no-sandbox')
options.add_argument("--disable-extensions")
options.add_argument('--log-level=3')

# Create new Instance of Chrome in incognito mode
#browser = webdriver.Chrome(executable_path=r'PATH_HERE', chrome_options=options)

# get soup object
def get_soup(text):
	return BeautifulSoup(text, "lxml")
    
#indeed
    
# extract company
def extract_company(div, site): #indeed
    listboi = []
    if site == 'indeed':
        company = div.find(name="span", attrs={"class":"company"}).text
        try:
            company = company.replace('\n', '').strip()
            return company
        except:
            return company
        #else:
            #return 'NOT_FOUND'
        
    if site == 'stack':
        company = div.find(name="div", attrs={"class":"-company"})
        if company is None:
            return 'NOT_FOUND'
        return company.text.replace('\n', '').replace('\r','')
        #return ''.join(v.text.replace('\n', '').replace('\r','') for v in listboi)
        
    if site == 'linkedin':
        company = div.find_all(name="a", attrs={"class":"job-card-search__company-name-link ember-view"})
        for span in company:
            listboi.append(span.text)
        return listboi
            

        
#########


# extract job salary

def extract_salary(div, site):
    listboi = []
    if site == 'indeed':
        span = div.find('span', attrs={'class': 'no-wrap'})
        try:
            return span.text.strip()
        except:
            return 'Unspecified'
    if site == 'stack':
        sal = div.find('div', attrs={'class': '-perks'})
        try:
            fin_str = sal.text.replace('\n', ' ').replace('\r', '').strip()
            return fin_str
        except:
            return 'NA'
    if site == 'linkedin':
        return 'no salary'


    
########
   
# extract ID 
def extract_id(div, site):
    if site == 'indeed':
        sal = div.find('h2', attrs={'class': 'jobTitle'})
        return div['id']
    if site == 'stack':
        sal = div.find('span', attrs={'class': 'fav-toggle'})
        return sal['data-jobid']
    if site == 'linkedin':
        return 'no id'
    
########

# extract job location
def extract_location(div, site): 
    listboi = []
    if site == 'indeed':
        '''locations = div.find_all('div', attrs={'class': 'location'})
        for span in locations:
            listboi.append(span.text)
        return ''.join(listboi)'''
        locations = div.find('span', attrs={'class': 'location'})
        try:
            return locations.text
        except:
            locations = div.find('div', attrs={'class': 'location'})
            return locations.text
        
    if site == 'stack':
        locations = div.find_all('div', attrs={'class': '-company'})
        for span in locations:
            title_loc = span.text
            location = title_loc.split('-', 1)[1].replace('\r', '').replace('\n', '')
        return location
    if site == 'linkedin':
        locations = div.find_all('span', attrs={'class': 'job-location'})
        for span in locations:
            listboi.append(span.text)
        return listboi




# extract job title
def extract_job_title(div, site):
    listboi = []
    if site == 'indeed':
        title = div.find(name='a', attrs={'class':'turnstileLink'})['title']
        return title
    if site == 'stack':
        title = div.find_all(name='a', attrs={'class':'s-link'})[0]['title']
        return title
    if site == 'linkedin':
        title = div.find_all('span', attrs={'class': 'job-title-text'})
        for span in title:
            listboi.append(span.text)
        return listboi
    

def extract_link(div, site): 
    listboi = []
    if site == 'indeed':
        link = div.find(name='a', attrs={'class':'turnstileLink'})
        return 'http://www.indeed.com' + link['href']
    if site == 'stack':
        tit_link = div.find_all(name='a', attrs={'class':'s-link'})
        for a in tit_link:
            return 'https://www.stackoverflow.com' + a['href']
        if tit_link is None:
            return 'done broke'
    if site == 'linkedin':
        tit_link = div.find_all(name='a', attrs={'class':'job-title-link'})
        for a in tit_link:
            return ['href']
        if tit_link is None:
            return 'done broke'

# extract jd summary indeed
def extract_postdate(div, site):
    if site == 'indeed':
        span = div.find('div', attrs={'class': 'result-link-bar'}).text.split('-')[0].strip()
        return span
    if site == 'stack':
        span = div.find('span', attrs={'class': 'ps-absolute pt2 r0 fc-black-500 fs-body1 pr12 t24'})
        try:
            return span.text
        except:
            span = div.find('span', attrs={'class': 'ps-absolute pt2 r0 fc-black-500 fs-body1 pr12 t32'})
            return span.text
    if site == 'linkedin':
        spans = div.find_all('span', attrs={'class': 'job-description'})
        for span in spans:
            return span.text

# extract jd summary indeed
def extract_summary(div, site):
    if site == 'indeed':
        span = div.find('span', attrs={'class': 'summary'})
        return span.text.strip()
    if site == 'stack':
        return 'No summary on stack'
    if site == 'linkedin':
        spans = div.find_all('span', attrs={'class': 'job-description'})
        for span in spans:
            return span.text
    
def extract_tags(div, site): #stack
    if site == 'stack':
        tag = ''
        spans = div.find_all('a', attrs={'class': 'post-tag job-link no-tag-menu'})
        for a in spans:
            tag = tag + a.text + ', '
        return tag
    else:
        return 'Tags on Stack Overflow'
        

 

# extract link of job description 
#indeed
def extract_easyapply(div, site):
    if site == 'indeed':
        spans = div.find('div', attrs={'class': 'iaP'})
        if spans is not None:
            return True
        else:
            return False
    if site == 'linkedin':
        spans = div.find('div', attrs={'class': 'job-flavor-in-apply-container'})
        if spans == None:
            return False
        else:
            return True
    else:
        return 'Easy apply on Indeed/Linkedin only'
