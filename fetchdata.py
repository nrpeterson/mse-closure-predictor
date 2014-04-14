import json
import gzip
import urllib
from urllib.request import urlopen
from urllib.parse import urlencode, unquote
import datetime as dt
from io import BytesIO

# Set up timestamps to grab results from 28 to 14 days ago.
today = dt.datetime.today()
end = today - dt.timedelta(days=14)
end = int(end.timestamp())

items = list()

# Then, fetch posts which ARE closed.
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
    except:
        print("Error!  Moving along.")
        continue
    
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
    else:
        page += 1

# First, fetch questions which were NOT closed.
for page in range(1,21):
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
    while True:
        try:
            response = urlopen(fullurl)
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            text = f.read().decode()
        except:
            print("Error!  Retrying...")
            continue
        break

    data = json.loads(text)
    print("Done! {0} queries remaining for today.".format(
        data['quota_remaining']))

    for item in data['items']:
        items.append(item)

    if not data['has_more']:
        break

print("Fetched a total of {0} items.".format(len(items)))

f = open('rawdata.json', 'w')
json.dump(items, f)
