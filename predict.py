import csv
import numpy as np
from scipy.special import expit as sigmoid
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
import pickle
import json

from cleandata import extract_data, fields


def build_model():
    # Read in the data
    csvfile = open('cleandata.csv', newline='')
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    next(reader)
    data = np.array([row for row in reader])

    # Split the data up in to our inputs (X) and outputs (y)
    X = data[:, :-1]
    y = data[:, -1]

    # Set up the scaler, and transform the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Initialize the Linear SVC:
    classifier = LinearSVC()
    classifier.fit(X, y)

    with open('model.pickle', 'wb') as f:
        pickle.dump((scaler, classifier), f)

def probabilities(posts):
    # Read in Model
    with open('model.pickle', 'rb') as f:
        scaler, classifier = pickle.load(f)
    
    jsondata = [extract_data(post) for post in posts]

    data = []
    for post in jsondata:
        data.append([post[key] for key in fields])
    data = np.matrix(data)

    X = data[:,:-1]
    X_scaled = scaler.transform(X)
    probs = sigmoid(classifier.decision_function(X))
    return probs


if __name__ == '__main__':
    with open('rawdata.json', 'r') as f:
        posts = json.load(f)

    probs = probabilities(posts)

    print('Max: {}'.format(max(probs)))
