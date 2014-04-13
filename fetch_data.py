import json
import gzip
from urllib.request import urlopen
from urllib.parse import urlencode, unquote
import datetime as dt
from io import BytesIO

# Set up timestamps to grab results from 28 to 14 days ago.
today = dt.datetime.today()
end = today - dt.timedelta(days=14)
start = end - dt.timedelta(days=14)
end = int(end.timestamp())
start = int(start.timestamp())

items = list()

# First, fetch questions which were NOT closed.
for page in range(1,11):
    url = "http://api.stackexchange.com/2.2/search/advanced"
    params = dict()
    params['key'] = 'dWDGnVFUsu2Nu11MiamE4A(('
    params['closed'] = 'True'
    params['page'] = page
    params['pagesize'] = 100
    params['fromdate'] = start
    params['enddate'] = end
    params['order'] = 'desc'
    params['sort'] = 'creation'
    params['site'] = 'math'
    params['filter'] = '!17vXHhjmWmlII1BEL6*HftL(DcATBEDTrqcUJjFMt.70ga'

    fullurl = url + '?' + urlencode(params)
    print("Fetching page {0}...".format(page))
    response = urlopen(fullurl)
    buf = BytesIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    text = f.read().decode()

    data = json.loads(text)
    print("Done!")
    for item in data['items']:
        items.append(item)

    if not data['has_more']:
        break

# Then, fetch posts which ARE closed.
for page in range(1,11):
    url = "http://api.stackexchange.com/2.2/search/advanced"
    params = dict()
    params['key'] = 'dWDGnVFUsu2Nu11MiamE4A(('
    params['closed'] = 'False'
    params['page'] = page
    params['pagesize'] = 100
    params['fromdate'] = start
    params['enddate'] = end
    params['order'] = 'desc'
    params['sort'] = 'creation'
    params['site'] = 'math'
    params['filter'] = '!17vXHhjmWmlII1BEL6*HftL(DcATBEDTrqcUJjFMt.70ga'

    fullurl = url + '?' + urlencode(params)
    print("Fetching page {0}...".format(page))
    response = urlopen(fullurl)
    buf = BytesIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    text = f.read().decode()

    data = json.loads(text)
    print("Done!")
    for item in data['items']:
        items.append(item)

    if not data['has_more']:
        break

print("Fetched a total of {0} items.".format(len(items)))

f = open('rawdata.json', 'w')
json.dump(items, f)
