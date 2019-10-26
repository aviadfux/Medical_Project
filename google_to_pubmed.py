import ast
import os
import sys
import csv
import time
from distutils.util import strtobool

import scholarly as scholarly
from metapub import PubMedFetcher

#import stopwords as stopwords
from selenium import webdriver

URL = "https://www.google.com/search?lang=en&q="

def create_query_csv(query, results, bestMatch, destination_folder):
    if bestMatch:
        sort = "bestMatch"
    else:
        sort = "Recent"
    filename = destination_folder + '\\' + query[0] + "_" + sort + ".csv"
    with open(filename , 'w', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerow(["document_url", "category", "numeric"])
        for item in results:
            wr.writerow([item, ])

def query_from_google(driver, query):
    driver.get(URL + '"' + query + '"+ncbi')
    #driver.get(URL +  query )
    ref = ''
    i = 0
    while ref == '' and i <5:
        try:
            link = driver.find_elements_by_class_name('g')[i].find_element_by_partial_link_text('ncbi')
            ref = link.get_attribute("href")
        except:
            print('No pubmed entr for paper ' + query)
        i += 1
    return ref

    #links = driver.find_elements_by_partial_link_text('https://www.ncbi.nlm.nih.gov/pubmed')



def open_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    return webdriver.Chrome(options=options, executable_path=r'chromedriver')

def google_file_to_csv_file(driver, google_file, pubmed_file):
    urls = []
    with open(google_file, encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['Title']
            url = query_from_google(driver, title)
            urls.append((url, title))

    with open(pubmed_file , 'w', encoding='utf-8', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerow(["document_url", "Title", "category", "numeric"])
        for (url, title) in urls:
            wr.writerow([url,title])

def iterate_dir(google_dir, pubmed_dir):
    driver = open_chrome_driver()
    for filename in os.listdir(google_dir):
        if filename.endswith(".csv"):
            google_file_to_csv_file(driver,google_dir+'/'+filename,pubmed_dir+'/'+filename)
    driver.close()

def single_file_transfer(filename):
    driver = open_chrome_driver()
    google_file_to_csv_file(driver, 'C:\\research\\falseMedicalClaims\\examples\\short queries\\google' + '\\' + filename,
                            'C:\\research\\falseMedicalClaims\\examples\\short queries\\pubmed' + '\\' + filename)
    driver.close()

def main():
    single_file_transfer('benzodiazepines alcohol withdrawal2.csv')
    #iterate_dir('C:\\research\\falseMedicalClaims\\examples\\google','C:\\research\\falseMedicalClaims\\examples\\pubmed')
    #iterate_dir('C:\\research\\falseMedicalClaims\\examples\\long queries\\google','C:\\research\\falseMedicalClaims\\examples\\long queries\\pubmed')

if __name__ == '__main__':
    main()
