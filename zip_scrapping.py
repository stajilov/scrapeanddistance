import pandas as pd
import csv
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup



def scrapForZips():
	allZipDFs = pd.read_csv("institutions.csv", sep=",", error_bad_lines=False)

	allZips = set(allZipDFs["Zip"])
	
	
	dfZips = pd.read_csv("crosswalk.csv", header=None, usecols=[0,1], sep=";")
	existingZips = list(dfZips[0])
	print(existingZips)
	
	for zp in allZips:
		cleanZip = str(zp).split("-",2)[0]
		print(cleanZip)
		
		if cleanZip.isdigit() == False:
			continue
		
		if int(cleanZip) in existingZips:
			continue
		
		
		browser = webdriver.Chrome('/Applications/chromedriver')
		url = 'https://www.unitedstateszipcodes.org/' + cleanZip
		print(url)
		browser.get(url)
		delay = 5 # seconds
		try:
			myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'map-info')))
			html_source = browser.page_source
			soup = BeautifulSoup(html_source, 'html.parser')
			table = soup.find( "table" )
			tr1 = table.find("tr").find("td")
			stateString = tr1.text
			r = re.findall('(AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)', stateString)
			print(r)
			if len(r) == 0:
				continue			
			stateName = r[0]
			
			f = open("crosswalk.csv","a+")
			f.write(cleanZip + ";" + stateName + "\n")
			f.close()
			browser.close()
						
			
			
		except TimeoutException:
			print("Loading took too much time!")
			
scrapForZips()