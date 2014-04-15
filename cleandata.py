import json
import pymysql
import model
import numpy as np

# List of fields that will occur in the database of cleaned data
fields = ['id', 'authorrep', 'calculus', 'colons', 'commands', 'commas', 
    'dollars', 'doubledollars', 'effort', 'emoticons', 'homework', 'numtags', 
    'paragraphs', 'periods', 'pleas', 'politeness', 'postlength', 'precalc', 
    'questionmarks', 'questions', 'quotes', 'spaces', 'titlelength',
    'txtspeak', 'closed']

def extract_data_dict(item):
    """Given item (a dict extracted from StackExchange JSON data), extract 
    metrics and return a dict of the results.
    """
    
    # Define some word groups to search for as part of data measurement.
    demands = ['prove', 'Prove', 'show', 'Show', 'compute', 'Compute', 
            'calculate', 'Calculate', 'find', 'Find', 'Explain', 'explain']
    effort = ['I tried', "I've tried", "My attempt", 'my attempt', 
            'work so far']
    emoticons = [':)', ':-)', ':(', ':-(', ':D', ':-D', ';-)', ';)', '(:', '):',
            ':$', ':-$']
    pleas = ['help', 'Help', "don't understand", "don't get it", 
            "don't see how", 'show me', 'Show me', 'stuck', 'Stuck']
    polite = ['please', 'Please', 'thanks', 'Thanks', 'Thank you', 'thank you']
    questions = ['where', 'Where', 'what', 'What', 'when', 'When', 'why', 
            'Why', 'how', 'How', 'who', 'Who']
    txtspeak = [' u ', 'pls', 'Pls', 'Thx', 'thx']

    stats = dict()
    

    # Handle the fact that posts are occasionally anonymous by declaring such
    # users to have the minimum possible reputation (1)
    if 'owner' in item and 'reputation' in item['owner']:
        stats['authorrep'] = item['owner']['reputation']
    else:
        stats['authorrep'] = 1
    
    # If question has been closed, check to see if it is for the desired reason
    if 'closed_details' in item:
        desc = item['closed_details']['description']
        stats['closed'] = int('context' in desc)
    else:
        stats['closed'] = 0
    
    stats['calculus'] = int('calculus' in item['tags'] or 
            'multivariable-calculus' in item['tags'])
    stats['colons'] = item['body'].count(':')
    stats['commands'] = sum([item['body'].count(word) for word in demands])
    stats['commas'] = item['body'].count(',')
    stats['dollars'] = item['body'].count('$')
    stats['doubledollars'] = item['body'].count('$$')
    stats['effort'] = sum([item['body'].count(word) for word in effort])
    stats['emoticons'] = sum([item['body'].count(word) for word in emoticons])
    stats['homework'] = int('homework' in item['tags'])
    stats['id'] = item['question_id']
    stats['numtags'] = len(item['tags'])
    stats['paragraphs'] = item['body'].count('<p>')
    stats['periods'] = item['body'].count('.')
    stats['pleas'] = sum([item['body'].count(word) for word in pleas])
    stats['politeness'] = sum([item['body'].count(word) for word in polite])
    stats['postlength'] = len(item['body'])
    stats['precalc'] = int('algebra-precalculus' in item['tags'])
    stats['questionmarks'] = item['body'].count('?')
    stats['questions'] = sum([item['body'].count(word) for word in questions])
    stats['quotes'] = item['body'].count('"') + item['body'].count("'")
    stats['spaces'] = item['body'].count(' ')
    stats['titlelength'] = len(item['title'])
    stats['txtspeak'] = sum([item['body'].count(word) for word in txtspeak])

    return stats

def extract_data_vector(item, include_closed=False, include_id=False):
    """Given item (a dict extracted from StackExchange JSON data), return
    a list of the extracted data, in the order desired by the database.

    include_closed: Do you want the closed status of the post?
    include_id:     Do you want the question ID of the post? (Key for dbase)
    """

    stats = extract_data_dict(item)
   
    if include_closed:
        end = len(fields)
    else:
        end = len(fields) - 1

    if include_id:
        start = 0
    else:
        start = 1
    vec = tuple(stats[field] for field in fields[start:end])
    return vec

def add_to_training_data(posts):
    """ Given posts (a list of dicts extracted from StackExchange JSON data), 
    add posts to the training data stored in the database.

    Note: If a post ID is already in the training database, it is updated with
    the newly-extracted measurements.
    """

    query = "INSERT INTO trainingdata ("
    query += ', '.join(fields) + ") VALUES "
    
    datavecs = [str(tuple(extract_data_vector(item, True, True))) for item in posts]
    
    query += ",\n".join(datavecs)
    query += " ON DUPLICATE KEY UPDATE "
    query += ','.join(["{0}=VALUES({0})".format(field) for field in fields[1:]])
    query += ';\n'

    f = open('dbase.conf', 'r')
    dbase, user, passwd = f.readline().rstrip().split(',')
    f.close()
    conn = pymysql.connect(user=user, passwd=passwd, db=dbase)
    cur = conn.cursor()
    count = cur.execute(query)
    conn.commit()
    print("Successfully merged {} entries!".format(count))

    cur.close()
    conn.close()

    model.build_model()

def update_live_data(posts):
    """ Given posts (a list of dicts extracted from StackExchange JSON data),
    replace the current live data with the information in posts.
    """

    query = '''INSERT INTO livedata (id, postlink, title, body, prediction, '''
    query += '''prob) VALUES ("%s", "%s", "%s", "%s", "%s", "%s") '''
    

    predictions = model.predictions(posts)
    probabilities = model.probabilities(posts)
    queryvals = []
    for post, pred, prob in zip(posts, predictions, probabilities):
        queryvals.append((post['question_id'], post['link'], post['title'], 
            post['body'],float(pred), float(prob)))
    
    f = open('dbase.conf', 'r')
    dbase, user, passwd = f.readline().rstrip().split(',')
    f.close()
    conn = pymysql.connect(user=user, passwd=passwd, db=dbase, charset='utf8')
    cur = conn.cursor()
    cur.execute("DELETE FROM livedata WHERE 1")
    count = cur.executemany(query, queryvals)
    conn.commit()
    print("Successfully merged {} entries!".format(count))

    cur.close()
    conn.close()
# If the script is called directly, process the file 'rawtrainingdata.json' to 
# extract metric information in to database
if __name__ == "__main__":
    rawdatafile = open('rawtrainingdata.json', 'r')
    rawdata = json.load(rawdatafile)

    add_to_training_data(rawdata)
