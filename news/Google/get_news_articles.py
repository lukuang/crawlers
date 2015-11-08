# -*- coding: utf-8 -*-
import requests
import os
import json
import re
import argparse
import codecs
import sys
import time
from datetime import date, timedelta
from crawl_html import crawl_html
from bs4 import BeautifulSoup


def get_date(name):
    m = re.search("^(.+?)\-\d+$",name)
    if m is not None:
        return m.group(1)
    else:
        print "error file/dir name %s" %name
        sys.exit(-1)


def parse_html(html_file):
    all_urls = {}
    content = ""
    with open(html_file) as f:
        content = f.read()
    soup = BeautifulSoup(content,'lxml')
    # links = soup.find(id="ires").ol.find_all("h3",class_='r')
 
    # for l in links:
    #     url = l.a['href']
    #     m = re.search('http[^\&]+',url)
    #     if m is not None:
    #         all_urls.append(m.group(0))
    #         print "append",m.group(0)
    #     else:
    #         print "wrong url"
    #         print url
    #         continue
    results = soup.find(id="ires").ol.find_all(class_=re.compile("(_HId)|(_sQb)"))
    for result in results:
        url = result['href']
        m = re.search('http[^\&]+',url)
        if m is not None:
            all_urls[m.group(0)] = 0
            print "append",m.group(0)
        else:
            print "wrong url"
            print url
            continue


    return all_urls

def crawl_news(urls,dest_dir,index):
    news_error_file = os.path.join(dest_dir,"error")
    map_file = open(os.path.join(dest_dir,"map"),"a") 
    for u in urls:
        news_article=crawl_html(u,news_error_file)
        if news_article is not None:
            print "got %s" %u
            name = os.path.join(dest_dir,str(index)+".html")
            with codecs.open(name,"w",encoding='utf-8') as f:
                f.write(news_article)
            map_file.write("%d %s\n" %(index, u))
            index += 1


    map_file.close()
    return index

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest_dir',"-d",default="articles")
    parser.add_argument("--source_dir",'-s',default="data")
    args = parser.parse_args()
    
    # find the days that the urls are crawled, and remove the last date
    # since I want to re-crawl it just to be safe. 
    days = os.walk(args.dest_dir).next()[1]
    days.sort()
    if len(days) != 0:
        days.pop()

    crawling_days = {}
    already_crawled = {}
    all_files = os.walk(args.source_dir).next()[2]
    all_files.sort()
    for a_file in all_files:
        date = get_date(a_file)
        if date not in days:
            urls = parse_html(os.path.join(args.source_dir, a_file))
            for k in urls.keys():
                if k in already_crawled:
                    del urls[k]
                else:
                    already_crawled[k] = 0            

            print "there are %d urls for file %s" %(len(urls),a_file)
            #print already_crawled
            date_dir = os.path.join(args.dest_dir,date)
            if date not in crawling_days:
                crawling_days[date] = 0
                if not os.path.exists(date_dir):
                    os.mkdir(date_dir) 
            crawling_days[date] = crawl_news(urls,date_dir,crawling_days[date])




if __name__ == "__main__":
    main()