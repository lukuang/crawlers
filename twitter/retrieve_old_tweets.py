"""
retrieve old tweets for a query
"""
import tweepy
import json
import argparse
import re

def set_value(input_value):
  if (input_value==None):
    return "null"
  else:
    return str(input_value)


    
consumer_key="v4Z0ZQvBFDLcZuGQH2UmVO5hl"
consumer_secret="KUj4eXi36md0cUR2dYFbWq4CZX8vJQHwShLBak14xdgU7G0i6z"
access_token="612441285-1dUojcAcqw6CCu2nOnjB8TfGBCuToLqu0m2tTfqc"
access_token_secret="1QodEQ9CKFCn6VxcD5gsOxrbal9K3zcOSz1AKIoArBzG1"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.secure = True
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
count = 0
i_count = 0
results = {}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("query_string")
args = parser.parse_args()
query = " OR ".join(re.findall("\w+", args.query_string.lower()))
print "got query"
print query



for page in tweepy.Cursor(api.search,
                           q=query.lower(),
                           count=100,
                           result_type="mixed",
                           include_entities=True,
                           lang="en").pages():
    count += 1
    for tweet in page:
        #print tweet.created_at
        #print type(tweet.created_at)
        #print tweet.created_at.year
        #m = re.search(" (\d+)$", str(tweet.created_at))
      doc_id = tweet.created_at.strftime('%Y-%m-%d-%H')
      if doc_id not in results:
        results[doc_id] = []
      single_result = {}
      single_result["created_at"] = tweet.created_at.strftime("%a %b %d %H:%M:%S +0000 %Y")
      single_result["id"] = tweet.id_str
      single_result["text"] = tweet.text
      single_result["in_reply_to_status_id"] = set_value(tweet.in_reply_to_status_id)
      single_result["in_reply_to_status_id_str"] = set_value(tweet.in_reply_to_status_id_str)
      single_result["in_reply_to_user_id"] = set_value(tweet.in_reply_to_user_id)
      single_result["in_reply_to_user_id_str"]  = set_value(tweet.in_reply_to_user_id_str)
      single_result["in_reply_to_screen_name"] = set_value(tweet.in_reply_to_screen_name)
      single_result["usr"] = tweet.user._json
      single_result["geo"] = set_value(tweet.geo)
      single_result["coordinates"] = set_value(tweet.coordinates)
      single_result["place"] = set_value(tweet.place)
      single_result["contributors"] = set_value(tweet.contributors)
      single_result["retweet_count"] = set_value(tweet.retweet_count)
      single_result["favorite_count"] = set_value(tweet.favorite_count)
      single_result["entities"] = tweet.entities
      single_result["favorited"] = set_value(tweet.favorited)
      single_result["retweeted"] = set_value(tweet.retweeted)
            #print tweet.filter_level
      single_result["lang"] = set_value(tweet.lang)
            #print tweet.timestamp_ms
      results[doc_id].append(single_result)
        #print tweet.created_at, tweet.text
      i_count += 1

print "there are",count," pages in total,",i_count,"tweets in total\n" 

print "store_result"
for docid in results:
  with open(docid,"w") as f:
    j_str = json.dumps(results[docid])
    f.write(j_str)

def set_value(input_value):
  if (input_value==None):
    return "null"
  else:
    return str(input_value)

