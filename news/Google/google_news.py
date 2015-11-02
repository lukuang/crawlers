# -*- coding: utf-8 -*-
import requests
import os
import json
import re
import argparse
import codecs
import sys
import time
from bs4 import BeautifulSoup


def crawl_html(end_point,params={},start=0):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows) Gecko/20080201 Firefox/2.0.0.12',
      'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
      'Connection': 'keep-alive'
    }
    try:
        if start!=0:
            params['start'] = str(start)
        r=requests.get(end_point,params=params,headers=headers)
    # print r.url
    # with codecs.open('temp','w',encoding='utf-8') as f:
    #     f.write(r.text)
    # sys.exit(0)
    except requests.exceptions.HTTPError as error:
        print "http erro occur when the url is:", r.url
        print error
        return None
    except e:
        print "other exceptions"
        print e
        return None
    return r.text

def parse_html(content):
    all_urls = []
    soup = BeautifulSoup(content,'html.parser')
    # table =  soup.body.table
    # tbody = table.find_all("tbody",id='desktop-search')[0]
    # td = tbody.tr.find_all("td",valign='top')[1]
    # center_col = td.find_all("div",id='center_col')[0]
    # res = center_col.find_all("div",id="res")[0]
    # search = res.find_all("div",id="search")[0]
    # ires = search.find_all("div",id="ires")[0]
    # links = ires.ol.find_all("li")
    links = soup.find(id="ires").ol.find_all("h3",class_='r')
 
    for l in links:
        url = l.a['href']
        m = re.search('http[^\&]+',url)
        if m is not None:
            all_urls.append(m.group(0))
            print "append",m.group(0)
        else:
            print "wrong url"
            print url
            continue
    return all_urls

def crawl_news(urls,dest_dir,i):
    index = 0
    for u in urls:
        news_article=crawl_html(u)
        print "got %s" %u
        name = os.path.join(dest_dir,str(10*i+index)+".html")
        with codecs.open(name,"w",encoding='utf-8') as f:
            f.write(news_article)
        index += 1
        time.sleep(10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query_string")
    parser.add_argument("--start",'-s',action='store')
    parser.add_argument("--end",'-e',action='store')
    parser.add_argument('--dest_dir',"-d",default="data")
    args = parser.parse_args()

    end_point = 'http://www.google.com/search?'

    query = "+".join( re.findall('\w+',args.query_string.lower()) )
    print "the query is %s" %(query)
    if args.start is not None:
        print "starts at: %s" %(args.start)
    if args.end is not None:
        print "ends at: %s" %(args.end)

    params = {}
    params['q'] = query
    params['tbs'] = 'cdr:1,cd_min:%s,cd_max:%s' %(args.start,args.end)
    params['tbm'] = 'nws'

    for i in range(10):
        content = crawl_html(end_point, params,start=10*i)
        urls = parse_html(content)
        crawl_news(urls,args.dest_dir,i)
        raw_input("now i is %d, Press Enter to continue" %i)

    

if __name__ == "__main__":
    main()