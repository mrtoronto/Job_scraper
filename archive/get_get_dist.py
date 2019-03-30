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

def get_address(query, api_key):
    base = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input='
    locationbias= '42.3314584645106, -71.1039191294055'
    #key = api_key
    query = query
    fields = 'formatted_address,name,geometry'
    inputtype = 'textquery'
    
    url_search = base + query + '&inputtype=' + inputtype + '&fields=' + fields + '&locationbias=circle:2000@' + locationbias + '&key=' + api_key
    print(url_search)
    my_dict = requests.get(url_search).json()
    return my_dict
        
def get_commute(dest, origin, api_key):
    
    base = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&'
    origin = 'origins=' + origin + '&'
    dest_str = 'destinations=' + dest + '&'
    api_key = 'key=' + api_key
    
    url_search = base + origin + dest_str + api_key
    print(url_search)
    my_dict = requests.get(url_search).json()
    return my_dict
    
def dist_duration(company_list, id_list, api_key):
    comm_df = pd.DataFrame(columns=['company', 'place', 'address', 'distance', 'duration'])
    for index, company in enumerate(company_list):
        comm_dict = {}
        company = company
        tmp_id = id_list[int(index)]
        text_dict = get_address(str(company), api_key=api_key)
        #print(text_dict)
        if text_dict['status'] == 'ZERO_RESULTS':
            print(company + ' has 0 results in get_address.')
            base = 'https://maps.googleapis.com/maps/api/staticmap?'
            place = 'None'
            address = 'None'
            distance = 'None'
            duration = 'None'
            #params = {'center' : 'Boston, MA' , 'zoom' : '20', 'size' : '200x200' , 'maptype' : 'roadmap', 'key': api_key}
            params = {'center' : 'Boston MA 02120' , 'zoom' : '10', 'size' : '200x200' , 'maptype' : 'roadmap', 'key': api_key}
            map_url = requests.get(base, params).url
        else:
            address = text_dict['candidates'][0]['formatted_address']
            place = text_dict['candidates'][0]['name']    
            res_lat_lng = str(text_dict['candidates'][0]['geometry']['location']['lat']) + ',' + str(text_dict['candidates'][0]['geometry']['location']['lng'])
            base = 'https://maps.googleapis.com/maps/api/staticmap?'
            #params = {'center' : 'Boston MA 02120' , 'zoom' : '18', 'size' : '200x200' , 'maptype' : 'roadmap', 'markers': 'color:blue|label:S|' + res_lat_lng, 'key': api_key} 
            params = {'center' : 'Boston MA 02120' , 'size' : '200x200' , 'maptype' : 'roadmap', 'markers': 'color:blue|label:S|' + res_lat_lng, 'key': api_key} 
            map_url = requests.get(base, params).url
            
            
            comm = get_commute(dest=res_lat_lng, origin='Boston, MA', api_key=api_key)
            if comm['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
                print(company + ' has 0 results in get_commute.')
                continue
            else:
                try:
                    distance = (comm['rows'][0]['elements'][0]['distance']['text'])
                    duration = (comm['rows'][0]['elements'][0]['duration']['text'])
                except:
                    #print(comm)
                    break

        comm_dict['company'] = company
        comm_dict['place'] = place
        comm_dict['address'] = address
        comm_dict['distance'] = distance
        comm_dict['duration'] = duration
        comm_dict['sID'] = tmp_id
        comm_dict['map_url'] = map_url
        comm_tmp_df = pd.DataFrame(comm_dict, index = [comm_dict['sID']])
        comm_df = comm_df.append(comm_tmp_df, sort=False)
    return comm_df
    

    
