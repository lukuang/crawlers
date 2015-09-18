#!/usr/bin/env python
# -*- coding: utf-8 -*-

# crawling the articels of NYTimes between a start data and a stop data
# this is essentially done through tweaking the search API.

import sys,os
import re
import urllib
import urllib2
import codecs
import time
import math
from datetime import date, timedelta
from bs4 import BeautifulSoup
import json
import requests
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')
DEST_DIR = "./data"
MY_KEY = "3215e5e4465ef98e55c3489a30b5143f:8:72984200"

LIMIT = 10000
REQUEST_COUNT = 0

def get_page(url):
  try:
    time.sleep(0.5)
    response = requests.get(url)
    # force the encoding to utf-8
    response.encoding = 'utf-8'
    return response.text
  except:
    print 'Error: ' + url
    return 'ERROR'

def parse_search_results(search_url, content, date_dir):
  # parse the JSON result
  results_json = json.loads(content)

  # first, save how many news documents for this date
  results_cnt = int(results_json['response']['meta']['hits'])
  if not results_cnt > 0:
    print 'No results found for %s' % date_dir
    return

  

  news = []
  results_list = results_json['response']["docs"]
  for result in results_list:
    url = result['web_url']
    news.append(url)

  for i in range(len(news)):
    print news[i]
    content = get_page(news[i])
    if 'ERROR' == content:
      fn = codecs.open(date_dir + 'error', 'ab', 'utf-8')
      fn.write('%s\n' % news[i])
      fn.close
    else:
      file_path = date_dir + str(i + 1) + '.html'
      if not os.path.exists(file_path):
        # save the crawled document
        fn = codecs.open(file_path, 'wb', 'utf-8')
        fn.write(content)
        fn.close
        # save the mapping between the index and original URL
        map_file_path = date_dir + 'map'
        fn = codecs.open(map_file_path, 'ab', 'utf-8')
        fn.write('%s %s\n' %(str(i + 1), news[i]))

  """
  If the number of the search results are greater than 10
  """
  if results_cnt > 10:
    pages_cnt = int(math.ceil(results_cnt * 1.0 / 10))
    for i in range(1, pages_cnt):
      temp_url = search_url + '&page=%s' % str(i)
      content = get_page(temp_url)
      check_request_count()
      if 'ERROR' == content:
        print 'Error: %s' % temp_url
        raw_input("PRESS ENTER TO continue")
        continue

      news = []
      results_list = results_json['response']["docs"]
      results_json = json.loads(content)


      for result in results_list:
        url = result['web_url']
        news.append(url)

      for j in range(len(news)):
        print news[j]
        content = get_page(news[j])
        if 'ERROR' == content:
          fn = codecs.open(date_dir + 'error', 'ab', 'utf-8')
          fn.write('%s\n' % news[j])
          fn.close
        else:
          index = i * 10 + j + 1
          file_path = date_dir + str(index) + '.html'
          if not os.path.exists(file_path):
            # save the crawled document
            fn = codecs.open(file_path, 'wb', 'utf-8')
            fn.write(content)
            fn.close
            # save the mapping between the index and original URL
            map_file_path = date_dir + 'map'
            fn = codecs.open(map_file_path, 'ab', 'utf-8')
            fn.write('%s %s\n' %(str(index), news[j]))

      new_results_cnt = int(results_json['response']['meta']['hits'])
      new_results_end = int(results_json['response']['meta']['offset'])

      # if we reached the end, stop
      if new_results_cnt == new_results_end:
        break
  try:
      map_file_path = date_dir + 'map'
      fn = codecs.open(map_file_path, 'ab', 'utf-8')
      fn.write('%s %d\n' %('all', results_cnt))

  except:
      # Catch any unicode errors while printing to console
      # and just ignore them to avoid breaking application.
      print "Exception in parse_search_results()"
      print '-'*60
      traceback.print_exc(file=sys.stdout)
      print '-'*60
      pass

def check_request_count():
  global REQUEST_COUNT
  REQUEST_COUNT +=1
  if (REQUEST_COUNT >= LIMIT):
    print "reached daily limit, do it next day"
    sys.exit(0)

def crawl(start, end):
  date = start
  crawl_dir = DEST_DIR
  global REQUEST_COUNT
  if not os.path.exists(crawl_dir):
    os.mkdir(crawl_dir)

  while date <= end:
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)

    if len(month) == 1:
      month = '0' + month
    if len(day) == 1:
      day = '0' + day

    date_dir = '%s/%s-%s-%s/' % (crawl_dir, year, month, day)
    if not os.path.exists(date_dir):
      os.mkdir(date_dir)
    else:
      # check whether the date have been crawled
      map_file = date_dir + 'map'
      if os.path.isfile(map_file):
        date += timedelta(days = 1)
        continue

    """
    retrieve all the results in the current date
    """
    date_str = '%s%s%s' %(year, month, day)
    # construct the search URL
    # basically this URL will return in JSON format
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?'\
        'begin_date=%s&end_date=%s&api-key=%s' % (date_str, date_str,MY_KEY)
    print 'Retrieve search results: %s' % url
    content = get_page(url)
    check_request_count()
    parse_search_results(url, content, date_dir)
    # sleep for 1 minute to prevent from being banned
    time.sleep(60)

    date += timedelta(days = 1)

if __name__ == '__main__':
  start = date(2013,6,5)
  end = date(2015,9,16)
  crawl(start, end)
