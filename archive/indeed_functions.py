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
browser = webdriver.Chrome(executable_path=r'/Users/matt/Documents/STUFF/random other shit/chromedriver.exe', chrome_options=options)


# get soup object
def get_soup(text):
	return BeautifulSoup(text, "lxml")


# extract company
def extract_company(div): 
    company = div.find_all(name="span", attrs={"class":"company"})
    if len(company) > 0:
        for b in company:
            return (b.text.strip())
    else:
        sec_try = div.find_all(name="span", attrs={"class":"result-link-source"})
        for span in sec_try:
            return (span.text.strip())
    return 'NOT_FOUND'


# extract job salary
def extract_salary(div): 
   for span in div.find_all('span', attrs={'class': 'no-wrap'}):
        return (span.text.strip())
   return 'Unspecified'
   
# extract ID 
def extract_id(div): 
   for span in div.find_all('div', attrs={'class': 'row'}):
        return (span['id'])
   return 'Unspecified'


# extract job location
def extract_location(div):
    for span in div.find_all('span', attrs={'class': 'location'}):
        return (span.text)
    return 'Unspecified'


# extract job title
def extract_job_title(div):
    for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
        return (a['title'])
    return('NOT_FOUND')


# extract jd summary
def extract_summary(div): 
    spans = div.find_all('span', attrs={'class': 'summary'})
    for span in spans:
        return (span.text.strip())
    return 'NOT_FOUND'
 

# extract link of job description 
def extract_link(div): 
    for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
        return ('http://www.indeed.com' + a['href'])
    return('NOT_FOUND')


# extract date of job when it was posted
def extract_date(div):
    try:
        spans = div.find_all('span', attrs={'class': 'date'})
        for span in spans:
            return (span.text.strip())
    except:
        return 'NOT_FOUND'
    return 'NOT_FOUND'


# extract full job description from link
def extract_fulltext(url):         

    # Go to desired website
    browser.get(url)
    test_1 = browser.find_elements_by_xpath("//div[@class='jobsearch-JobComponent-description icl-u-xs-mt--md']/div")
    test_2 = browser.find_element_by_xpath("//div[@class='jobsearch-JobMetadataFooter']")
    full_text = [x.text for x in test_1]
    return(full_text)
    browser.quit()

#extract indeed resume application avaliability 
def extract_easyapply(div):
    '''try:
        spans = div.find_all('div', attrs={'class': 'iaP'})
        for span in spans:
            return 'Yes'
    except:
        return 'NA'''
    spans = div.find('div', attrs={'class': 'iaP'})
    if spans is not None:
        return True
    else:
        return False

# write logs to file
def write_logs(text):
    # print(text + '\n')
    f = open('log.txt','a')
    f.write(text + '\n')  
    f.close()