"""
retrieval links in error which is not retrieved
"""


import os,argparse
import sys
import re
import subprocess
import time
import codecs
import urllib2
import traceback
import requests

def get_page(url):
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows) Gecko/20080201 Firefox/2.0.0.12',
      'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
      'Connection': 'keep-alive'
  }

  try:
    time.sleep(0.5)
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    esponse.encoding = 'utf-8'
    #response = requests.get(url)
    # force the encoding to utf-8
    #response.encoding = 'utf-8'
    return response.text
  except:
    print 'Error: ' + url
    return 'ERROR'

def get_page2(url):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows) Gecko/20080201 Firefox/2.0.0.12',
      'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
      'Connection': 'keep-alive'
    }
    try:
      req = urllib2.Request(url, headers=headers)
      response = urllib2.urlopen(req)
      return response
    except  urllib2.HTTPError as error:
      print "Exception in retrieve(). Error code: %d" %error.code
      print '-'*60
      print response
      traceback.print_exc(file=sys.stdout)
      print '-'*60
      raw_input("ENTER TO CONTINUE")
      return 'ERROR'
    except:
      # Catch any unicode errors while printing to console
      # and just ignore them to avoid breaking application.
      print "Exception in retrieve()"
      print '-'*60
      traceback.print_exc(file=sys.stdout)
      print '-'*60
      raw_input("ENTER TO CONTINUE")
      return 'ERROR'

def get_page_use_request(url,cookies = None):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows) Gecko/20080201 Firefox/2.0.0.12',
      'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
      'Connection': 'keep-alive'
    }
    try:
      if cookies is not None:
        response = requests.get(url,headers=headers, cookies = cookie,allow_redirects = False)
      else:
        response = requests.get(url,headers=headers)
      if response.status_code == requests.codes.ok:
        return response.text
      #elif 300<=response.status_code<400: #check whether it is a redirect
        #cookies = response.header["set-cookie"]
        #url = response.header['location']
        #return get_page_use_request(url,cookies = cookies)
    
    except  requests.exceptions.HTTPError as error:
      print "Exception in retrieve(). Error code: %d" %error.code
      print url
      print '-'*60
      print response
      traceback.print_exc(file=sys.stdout)
      print '-'*60
      #raw_input("ENTER TO CONTINUE")
      return 'ERROR'
    except:
      print url
      # Catch any unicode errors while printing to console
      # and just ignore them to avoid breaking application.
      print "Exception in retrieve()"
      print '-'*60
      traceback.print_exc(file=sys.stdout)
      print '-'*60
      #raw_input("ENTER TO CONTINUE")
      return 'ERROR'


def get_error_info(data_dir):
    error_info = []
    p = subprocess.Popen(["find", data_dir,"-type","f","-name",'error'],  stdout=subprocess.PIPE)
    output = p.communicate()[0]
    lines = output.split("\n")
    for line in lines:
        m = re.search("^(data.+)/error$",line)
        if m is not None:
            error_info.append(m.group(1))
        else:
            print line

    return error_info


def retrieve_error(error_info):
    for file_dir in error_info:
        print "for",file_dir
        missing_files = {}
        file_ids = {}
        next_id = -1000
        with open( os.path.join(file_dir,"map") ) as f:
            for line in f:
                m = re.search("^(\d+) (.+)$",line )
                if m is not None:
                    file_ids[m.group(2)] = m.group(1)
                    next_id = int(m.group(1)) + 1
                else:
                    pass

        with open( os.path.join(file_dir,"error") ) as f:
            for line in f:
                line = line.rstrip()
                m = re.match("^\s+$",line)
                if m is None:
                    #missing_files[line] = file_ids[line]
                    if line in file_ids:
                        dest =   os.path.join(file_dir,file_ids[line]+".html")
                        #rm = "rm %s" %(os.path.join(file_dir,file_ids[line]+".html"))
                    else:
                        dest = os.path.join(file_dir,str(next_id)+".html") 
                        #rm = "rm %s" %(os.path.join(file_dir,str(next_id)+".html"))

                        next_id += 1
                    
                    content = get_page_use_request(line)
                    if content=="ERROR":
                        print "error occur for",line
                        with open("ERROR_TOTAL", "a") as f:
                          f.write(line+"\n")
                    else:
                        
                        
                        if not os.path.exists(dest):
                          # save the crawled document
                          fn = codecs.open(dest, 'wb', 'utf-8')
                          fn.write(content)
                          fn.close
                          # save the mapping between the index and original URL
                          map_file_path = os.path.join(file_dir,'map')
                          print "write %s" %map_file_path
                          fn = codecs.open(map_file_path, 'ab', 'utf-8')
                          fn.write('%s %s\n' %(str(next_id), line))
                        else:
                          print "Skip %s already exists" %(dest)






def main():
    parser = argparse.ArgumentParser(usage = __doc__)
    parser.add_argument("--data_dir", "-d", default = "data")
    args = parser.parse_args()

    error_info = get_error_info(args.data_dir)
    retrieve_error(error_info)


if __name__ == '__main__':
    main()