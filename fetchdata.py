import json
import gzip
import urllib
from urllib.request import urlopen
from urllib.parse import urlencode, unquote
from urllib.error import URLError
import datetime as dt
from io import BytesIO

import cleandata

def fetch_training_data():
    # Set up timestamps to grab results from 28 to 14 days ago.
    today = dt.datetime.today()
    end = today - dt.timedelta(days=14)
    end = int(end.timestamp())

    items = list()

    # Fetch closed questions
    found_closed = 0
    page = 1
    while True:
        url = "http://api.stackexchange.com/2.2/search/advanced"
        params = dict()
        params['key'] = 'dWDGnVFUsu2Nu11MiamE4A(('
        params['closed'] = 'True'
        params['page'] = page
        params['pagesize'] = 100
        params['todate'] = end
        params['order'] = 'desc'
        params['sort'] = 'creation'
        params['site'] = 'math'
        params['filter'] = '!17vXHhjmWmlII1BEL6*HftL(DcATBEDTrqcUJjFMt.70ga'

        fullurl = url + '?' + urlencode(params)
        print("Fetching page {0}...".format(page))
        try:
            response = urlopen(fullurl)
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            text = f.read().decode()
            data = json.loads(text)
            print("Done! {0} queries remaining for today.".format(
                data['quota_remaining']))
            
            for item in data['items']:
                if 'closed_details' in item:
                    if 'context' in item['closed_details']['description']:
                        items.append(item)
                        found_closed += 1

            if not data['has_more'] or found_closed >= 2000:
                break
        except URLError:
            print("Error!  Moving along.")
        page += 1 

    # Fetch questions which were NOT closed.
    page = 1
    fetched = 0
    while fetched <= 20:
        url = "http://api.stackexchange.com/2.2/search/advanced"
        params = dict()
        params['key'] = 'dWDGnVFUsu2Nu11MiamE4A(('
        params['closed'] = 'False'
        params['page'] = page
        params['pagesize'] = 100
        params['todate'] = end
        params['order'] = 'desc'
        params['sort'] = 'creation'
        params['site'] = 'math'
        params['filter'] = '!17vXHhjmWmlII1BEL6*HftL(DcATBEDTrqcUJjFMt.70ga'

        fullurl = url + '?' + urlencode(params)
        print("Fetching page {0}...".format(page))
        try:
            response = urlopen(fullurl)
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            text = f.read().decode()
            fetched += 1
            data = json.loads(text)
            print("Done! {0} queries remaining for today.".format(
                data['quota_remaining']))

            for item in data['items']:
                items.append(item)

            if not data['has_more']:
                break
        
        except URLError:
            print("Error!  Moving along...")
            continue
        page += 1

    print("Fetched a total of {0} items.".format(len(items)))

    with open('rawtrainingdata.json', 'w') as f:
        json.dump(items, f)

    cleandata.add_to_training_data(items)

def fetch_live_data():
    url = "http://api.stackexchange.com/2.2/questions"
    params = dict()
    params['key'] = 'dWDGnVFUsu2Nu11MiamE4A(('
    params['page'] = 1
    params['pagesize'] = 30
    params['order'] = 'desc'
    params['sort'] = 'creation'
    params['site'] = 'math'
    params['filter'] = '!OfY_RfJwZ9)ZZHfPph2)A*5mrJRnBrLuNr0R6QQWH8X'

    fullurl = url + '?' + urlencode(params)
    
    print("Fetching data...")
    try:
        response = urlopen(fullurl)
        buf = BytesIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        text = f.read().decode()
        data = json.loads(text)
        print("Done! {0} queries remaining for today.".format(
            data['quota_remaining']))
        
        items = []
        for item in data['items']:
            if 'closed_details' not in item:
                items.append(item)

        with open('rawlivedata.json', 'w') as f:
            json.dump(items, f)
        
        print("Successfully grabbed {} unclosed questions!".format(len(items)))
        cleandata.update_live_data(items)

    except URLError:
        print("Error!  Try again in a couple of minutes.")

if __name__ == '__main__':
    fetch_live_data()
