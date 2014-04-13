import json
import csv

# List of fields that will occur in the CSV file of cleaned date, so that
# this list can be imported by other code rather than inferred.
fields = ['id', 'author_rep', 'calculus', 'closed', 'colons', 'commands', 'commas', 'dollars', 'doubledollars', 'effort', 'homework', 'num_tags', 'paragraphs', 'periods', 'pleas', 'politeness', 'post_length', 'precalc', 'questionmarks', 'questions', 'quotes', 'spaces', 'title_length', 'txtspeak']


def extract_data(item):
    """Given item (a dict extracted from StackExchange JSON data), extract 
    metrics and return a dict of the results.
    """
    
    # Define some word groups to search for as part of data measurement.
    demands = ['prove', 'Prove', 'show', 'Show', 'compute', 'Compute', 
            'calculate', 'Calculate', 'find', 'Find', 'Explain', 'explain']
    txtspeak = [' i ', ' u ']
    pleas = ['help', 'Help', "don't understand", "don't get it", 
            "don't see how", 'show me', 'Show me', 'stuck', 'Stuck']
    polite = ['please', 'Please', 'thanks', 'Thanks', 'Thank you', 'thank you']
    effort = ['I tried', "I've tried", "My attempt", 'my attempt', 
            'work so far']
    questions = ['where', 'Where', 'what', 'What', 'when', 'When', 'why', 
            'Why', 'how', 'How', 'who', 'Who']

    stats = dict()
    
    stats['id'] = item['question_id']
    
    if 'owner' in item and 'reputation' in item['owner']:
        stats['author_rep'] = item['owner']['reputation']
    else:
        stats['author_rep'] = 1
    
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
    stats['homework'] = int('homework' in item['tags'])
    stats['num_tags'] = len(item['tags'])
    stats['paragraphs'] = item['body'].count('<p>')
    stats['periods'] = item['body'].count('.')
    stats['pleas'] = sum([item['body'].count(word) for word in pleas])
    stats['politeness'] = sum([item['body'].count(word) for word in polite])
    stats['post_length'] = len(item['body'])
    stats['precalc'] = int('algebra-precalculus' in item['tags'])
    stats['questionmarks'] = item['body'].count('?')
    stats['questions'] = sum([item['body'].count(word) for word in questions])
    stats['quotes'] = item['body'].count('"') + item['body'].count("'")
    stats['spaces'] = item['body'].count(' ')
    stats['title_length'] = len(item['title'])
    stats['txtspeak'] = sum([item['body'].count(word) for word in txtspeak])

    return stats

# If the script is called directly, process the file 'rawdata.json' to extract
# metric information in to cleandata.csv
if __name__ == "__main__":
    rawdatafile = open('rawdata.json', 'r')
    rawdata = json.load(rawdatafile)
    
    cleandatafile = open('cleandata.csv', 'w')
    writer = csv.DictWriter(cleandatafile, fields)
    writer.writeheader()

    for item in rawdata:
        writer.writerow(extract_data(item))

    print("Wrote data to cleandata.csv, with {0} columns".format(len(fields)))
