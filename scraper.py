from bs4 import BeautifulSoup
from time import sleep
import requests
import time
from random import randint
from html.parser import HTMLParser
import json
import csv

def compare(google_links, bing_links):
    clean_bing = []
    clean_google = []

    for google_link in google_links:

        google_link = google_link.lower()
        if(google_link[-1] == '/'):
            google_link = google_link[:-1]
        google_link = google_link.split("//",1)[1]
        if(google_link[:4]=="www."):
            google_link = google_link[4:]
        clean_google.append(google_link)

    for bing_link in bing_links:

        bing_link = bing_link.lower()
        if(bing_link[-1] == '/'):
            bing_link = bing_link[:-1]
        bing_link = bing_link.split("//",1)[1]
        if(bing_link[:4]=="www."):
            bing_link = bing_link[4:]
        clean_bing.append(bing_link)

    match_count=0

    index_bing=[]
    index_google=[]

    for i in range(0,min(10,len(clean_bing))):
        clean_bing_link = clean_bing[i]
        if(clean_bing_link in clean_google):
            match_count+=1
            index_bing.append(i)
            index_google.append(clean_google.index(clean_bing_link))

    if(match_count==0):
        for i in range(10,len(clean_bing)):
            clean_bing_link = clean_bing[i]
            if(clean_bing_link in clean_google):
                match_count+=1
                index_bing.append(i)
                index_google.append(clean_google.index(clean_bing_link))

    #print(index_bing)
    #print(index_google)

    list_len = len(index_bing)

    if(list_len==0):
        return 0,0
    elif(list_len==1):
        if(index_bing[0] == index_google[0]):
            return 1,1
        else:
            return 1,0
    else:
        d2 = 0
        for j in range(0,list_len):
            d2+=(index_google[j]-index_bing[j])**2
        return match_count, 1 - 6*(d2)/(list_len * (list_len * list_len - 1))

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


class SearchEngine:

    @staticmethod
    def search(query, sleep=True):
        if sleep: # Prevents loading too many pages too soon
            time.sleep(randint(10, 100))
        temp_url = '+'.join(query.split()) #for adding + between words for the query
        temp_url = 'http://www.bing.com/search?q=' + temp_url
        url = temp_url+"&count=30"
        soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text,"html.parser")
        new_results = SearchEngine.scrape_search_result(soup)
        return new_results

    @staticmethod
    def scrape_search_result(soup):
        raw_results = soup.find_all('li', attrs = {'class' : 'b_algo'},limit=30)
        results = []
        #implement a check to get only 10 results and also check that URLs must not be duplicated
        for result in raw_results:
            link = result.find('a').get('href')
            results.append(link)
        return results

#############Driver code############

if __name__ == "__main__":

    try:

        queries_file = open("100QueriesSet1.txt",'r')
        queries = queries_file.readlines()
        #"""
        # TASK 1 - RUN ALL QUERIES ON BING AND STORE IN JSON FILE
        i=0
        json_data_to_encode = dict()
        for query in queries:
            query=query[:-1]
            i+=1
            bing_links = SearchEngine.search(query)
            json_data_to_encode[query[:-1]] = bing_links[:min(10,len(bing_links))]

        with open("task1.json", "w") as write_file:
            json.dump(json_data_to_encode, write_file, indent=4)

        #print(i)

        #"""

        # TASK 2 - USING TASK1.JSON, COMPARE THESE SEARCH RESULTS WITH THAT OF GOOGLE
        #          AND CALCULATE SPEARMAN COEFF., PERCENTAGE OVERLAP

        google_file = open("Google_Result1.json",encoding='utf-16', errors='ignore')
        google_results = json.load(google_file)

        sum_spearman=0
        sum_overlap=0

        bing_file = open("task1.json",encoding='utf-8', errors='ignore')
        bing_results = json.load(bing_file)
        with open('task2.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Queries ", "Number of Overlapping Results", "Percent Overlap" ,"Spearman Coefficient"])
        i=0
        for query in queries:
            i+=1
            #print(google_results[query[:-3]])
            compare_result = compare(google_results[query[:-3]],bing_results[query[:-2]])
            sum_spearman+= compare_result[1]
            sum_overlap+=compare_result[0]
            with open('task2.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Query "+str(i), compare_result[0], compare_result[0]*10.0 ,compare_result[1]])
        with open('task2.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Averages", sum_overlap/100, sum_overlap/10 ,sum_spearman/100])
        #print(i)
    finally:
        queries_file.close()

####################################