import os
import json
import re
import argparse
import codecs
import sys
import time
from crawl_html import crawl_html


def load_record(record_file):
    files = {}
    if os.path.exists(record_file):
        with open(record_file) as f:
            for line in f:
                files[line.rstrip()] = 1

    return files

def crawl_news(urls,dest_dir,news_error_file):
    index = 0
    for u in urls:
        news_article=crawl_html(u,news_error_file)
        print "got %s" %u
        name = os.path.join(dest_dir,str(index)+".html")
        with codecs.open(name,"w",encoding='utf-8') as f:
            f.write(news_article)
        index += 1
        #time.sleep(10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest_dir',"-d",default="data")
    parser.add_argument('--news_error_file',"-n",default="news_error_file")
    parser.add_argument('--source_dir',"-s",default="urls")
    parser.add_argument('--record_file',"-r",default="record")
    args = parser.parse_args()
    files = load_record(args.record_file)
    while True:
        for a_file in os.walk(args.source_dir).next()[2]:
            if a_file not in files:
                print "find new date %s" %a_file
                urls = json.load(open(os.path.join(args.source_dir,a_file) ))
                crawl_news(urls,args.dest_dir,args.news_error_file)

                with open(args.record_file,"a") as f:
                    f.write(a_file+"\n")
                print 'finished crawling for date %s' %a_file
        time.sleep(10)



if __name__ == '__main__':
    main()