import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from bs4.element import Tag
from time import sleep
import csv
from parsel import Selector
import parameters
import numpy
import flask
import requests
from flask import request,jsonify
from pymongo import MongoClient
import os
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
import selenium.webdriver
from scrape_linkedin.ProfileScraper import ProfileScraper
from scrape_linkedin.utils import HEADLESS_OPTIONS



class api :
    app = None
    def __init__(self ):
        self.links=[]        
        self.nbp = 1
        self.myclient = MongoClient('localhost',27017)
        self.db = self.myclient['SonicHr']
        self.collection_profiles = self.db['profiles']
        self.titles = []
        self.descriptions = []
        self.driver = webdriver.Chrome()
        self.soup=None 
        self.result_div =None
        self.cookie=None
        self.islogedin=False
    
    def api(self):    
        if 'query' in request.args:
            query = str(request.args['query'])
            print(query)
        else:
            return "Error: No id field provided. Please specify an idQuery."

        if 'nbp' in request.args:
            nbp = str(request.args['nbp'])
            print(nbp)
        else:
            return "Error: No id field provided. Please specify an idPages."
        if 'idf' in request.args:
            idf = str(request.args['idf'])
            print(idf)
        else:
            return "Error: No id field provided. Please specify an idf."
        if 'idUser' in request.args:
            idUser = str(request.args['idUser'])
            print(idUser)
        else:
            return "Error: No id field provided. Please specify an idUser."     


        # driver.get method() will navigate to a page given by the URL address
        self.driver.get('https://www.linkedin.com')

        # locate email form by_class_name
        if not self.islogedin :
            self.linkedinLogin()
    
        self.generateListe(query)
        
        for link in self.links:
            origin=link[8:link.index('.')]
           

            body=link[link.rfind('/')+1:]

            finalLink="https://www.linkedin.com/in/"+body+"?=originalSubdomain="+origin
  
            print(finalLink)            
            data = self.scrapeOneProfile(finalLink)
             
            data['idFolder'] = [idf]
            data['idUser'] = [idUser]
            print(data)
            self.collection_profiles.insert_one(data)
            

        return data


    def linkedinLogin(self):
        username = self.driver.find_element_by_id('session_key')
    

        # send_keys() to simulate key strokes
        username.send_keys(parameters.linkedin_username)
        sleep(0.5)
        # locate password form by_class_name
        password = self.driver.find_element_by_id('session_password')

        # send_keys() to simulate key strokes
        password.send_keys(parameters.linkedin_password)
        sleep(0.5)

        # locate submit button by_class_name
        log_in_button = self.driver.find_element_by_class_name('sign-in-form__submit-button')

        # .click() to mimic button click
        log_in_button.click()
        sleep(0.5)
        self.mycookie =self.driver.get_cookie("li_at")['value']
        print("myccookie :",self.mycookie)
        self.islogedin =True
   
        
    def generateListe(self,query):
        
         # driver.get method() will navigate to a page given by the URL address
        self.driver.get('https://www.google.com')
        sleep(3)

        # locate search form by_name
        search_query = self.driver.find_element_by_name('q')

        # send_keys() to simulate the search text key strokes
        search_query.send_keys(query)

        # .send_keys() to simulate the return key 
        search_query.send_keys(Keys.RETURN)

        self.soup = BeautifulSoup(self.driver.page_source,'lxml')
        self.result_div = self.soup.find_all('div', attrs={'class': 'g'})

        # Function call nbp of function profiles_loop. 
        self.repeat_fun(self.nbp, self.profiles_loop)
        # Separates out just the First/Last Names for the titles variable
        #titles01 = [i.split()[0:2] for i in self.titles]

    def scrapeOneProfile(self,url):
        #if 'url' in request.args:
        #     url = str(request.args['url'])
        # else:
        #     return "Error: No id field provided. Please specify an url."
        driver=selenium.webdriver.Chrome
        driver_type = Firefox if driver == 'Firefox' else Chrome
        driver_options = HEADLESS_OPTIONS
        with ProfileScraper(driver=driver_type, cookie=self.mycookie, driver_options=driver_options) as scraper:
            profile = scraper.scrape(url=url)
            output = profile.to_dict()
            return output  

    # Function call extracting title and linkedin profile iteratively
    def find_profiles(self):
        
        for r in self.result_div:
            # Checks if each element is present, else, raise exception
            try:
                link = r.find('a', href=True)
                title = None
                title = r.find('h3')
                
                # returns True if a specified object is of a specified type; Tag in this instance 
                if isinstance(title,Tag):
                    title = title.get_text()
        
                description = None
                description = r.find('span', attrs={'class': 'st'})
        
                if isinstance(description, Tag):
                    description = description.get_text()
        
                # Check to make sure everything is present before appending
                if link != '' and title != '' and description != '':
                    self.links.append(link['href'])
                    self.titles.append(title)
                    self.descriptions.append(description)
                
            # Next loop if one element is not present
            except Exception as e:
                print(e)
                continue
    # This function iteratively clicks on the "Next" button at the bottom right of the search page. 
    def profiles_loop(self):
        print('before find profiles')
        self.find_profiles()
        
        next_button = self.driver.find_element_by_xpath('//*[@id="pnnext"]') 
        next_button.click()
        
    def repeat_fun(self,times, f):
        for i in range(times): f()



app = flask.Flask(__name__)
app.config["DEBUG"] = True   


apiinstence= api()  

@app.route('/', methods=['POST'])
def start():
    print('start')
    return apiinstence.api() 
      


start
app.run(port=5001)
