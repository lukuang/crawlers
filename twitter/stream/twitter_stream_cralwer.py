"""
retrieve tweets from ongoing tweet stream
"""
from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
#import tweepy
import json
import argparse
import time
from time import gmtime, strftime 
import os,re

previous = strftime("%Y-%m-%d-%H", gmtime())
all_data = []
# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after

#print (para)
print ("start time",previous)
class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        #print (data)
        #return True
        global all_data,previous
        now = strftime("%Y-%m-%d-%H", gmtime())
        #print (now, len(all_data))
        if now > previous:
            print ("write data to",previous, "with len",len(all_data))
            with open(os.path.join("data",previous), "a") as f:
                j_str = json.dumps(all_data)
                f.write(j_str)
                all_data = []
                
                previous = now
                
        all_data.append(data)

        return True
        

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    para = json.load(open("auth.json"))
    consumer_key=str(para["consumer_key"])
    consumer_secret=str(para["consumer_secret"])
    access_token=str(para["access_token"])
    access_token_secret=str(para["access_token_secret"])

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query_string")
    args = parser.parse_args()
    query = re.findall("\w+", args.query_string.lower())
    print (query)
    #api = tweepy.API(auth)

    # If the authentication was successful, you should
    # see the name of the account print out
    #print(api.me().name)

    # If the application settings are set for "Read and Write" then
    # this line should tweet out the message to your account's
    # timeline. The "Read and Write" setting is on https://dev.twitter.com/apps
    #api.update_status(status='Updating using OAuth authentication via Tweepy!')
    stream = Stream(auth, l)
    stream.filter(track=query,languages = ["en"]) 
    #stream.filter(track=["Nepal","earthquake"], languages = ["English"])