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
    company = div.find_all(name="div", attrs={"class":"-title"})
    for b in company:
        return (b.text.strip())
    if company is None:
        return 'NOT_FOUND'


# extract job salary
def extract_salary(div): 
    sal = div.find_all('div', attrs={'class': '-perks'})
    sal_list = []
    for span in sal:
        sal_list.append(span.text.strip().replace('\n', ' ').replace('\r', ''))
    fin_str = ''.join(sal_list)
    return fin_str
    
# extract ID 
def extract_id(div): 
    sal = div.find_all('span', attrs={'class': 'fav-toggle'})
    return sal[0]['data-jobid']


# extract job location
def extract_comp_location(div):
    loc_list = []
    for span in div.find_all('div', attrs={'class': '-company'}):
        title_loc = span.text
        title = title_loc.split('-', 1)[0].replace('\r', '').replace('\n', '')
        location = title_loc.split('-', 1)[1].replace('\r', '').replace('\n', '')
    return ([title.strip(), location])


# extract job title
def extract_title_link(div):
    tit_link = div.find_all(name='a', attrs={'class':'s-link'})
    for a in tit_link:
        return [a['title'], 'https://www.stackoverflow.com' + a['href']]
    if tit_link is None:
        return ['done broke', 'done broke']


# extract jd summary
'''def extract_summary(div): 
    spans = div.find_all('span', attrs={'class': 'summary'})
    for span in spans:
        return (span.text.strip())
    return 'NOT_FOUND'''
 

# extract link of job description 
'''def extract_link(div): 
    for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
        return ('http://www.indeed.com' + a['href'])
    return('NOT_FOUND')'''


# extract date of job when it was posted
def extract_date(div):
    date = div.find_all('span', attrs={'class': 'fc-black-500 fs-body1 pr12 t24'})
    for span in spans:
        return (span.text.strip())
    if date is None:
        return 'done broke'


# extract full job description from link
'''def extract_fulltext(url):         

    # Go to desired website
    browser.get(url)
    full_text = [x.text for x in test]
    return(full_text)
    keywords=['Data', 'data']
    if keywords in full_text:
                print('tities#############')
    browser.quit()'''

#extract indeed resume application avaliability 
def extract_tags(div):
    tag = ''
    spans = div.find_all('a', attrs={'class': 'post-tag job-link no-tag-menu'})
    for a in spans:
        tag = tag + a.text + ', '
    return tag
    
    
# write logs to file
def write_logs(text):
    # print(text + '\n')
    f = open('log.txt','a')
    f.write(text + '\n')  
    f.close()