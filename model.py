"""A collection of methods for training a classifier to predict whether posts
    from Mathematics.StackExchange will be closed due to 'lack of context', and
    for using that model to make predictions.
"""

import numpy as np
from scipy.special import expit as sigmoid
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import pickle
import json
import pymysql

import cleandata

def build_model():
    """Fit a classifier to the data stored in our trainingdata database table.
    Store the model using pickle, for later use in predictions.
    """
    
    # Read in the data
    f = open('dbase.conf', 'r')
    dbase, user, passwd = f.readline().rstrip().split(',')
    f.close()
    conn = pymysql.connect(user=user, passwd=passwd, db=dbase)
    cur = conn.cursor()
   
    print("Fetching training data...")
    count = cur.execute("SELECT * FROM trainingdata")
    print("Done! Fetched {} training records.\n".format(count))
    data = np.array([row for row in cur], dtype=np.float64)
    cur.close()
    conn.close()
    
    # Split the data up in to our inputs (X) and outputs (y)
    X = data[:, 1:-1]
    y = data[:, -1]
    # Set up the scaler, and transform the data
    print("Scaling data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("Done.\n")

    # Initialize the classifier:
    print("Training the classifier...")
    classifier =  SVC(probability=True) #LogisticRegression(C=20.)
    classifier.fit(X_scaled, y)
    print("Done. Classifier score: {:04f}".format(classifier.score(X_scaled, y)))

    print("Storing model parameters...")
    with open('model.pickle', 'wb') as f:
        pickle.dump((scaler, classifier), f)
    print("Done!")


def probabilities(posts):
    """Given a collection of posts (in StackExchange JSON format), return our
    model's estimated probabilities that the posts will be closed.
    """
    
    # Read in Model
    with open('model.pickle', 'rb') as f:
        scaler, classifier = pickle.load(f)
    
    data = [cleandata.extract_data_vector(post) for post in posts]
    X = np.array(data, dtype=np.float64)

    X_scaled = scaler.transform(X)
    probs = classifier.predict_proba(X_scaled)[:,1]
    return probs


def predictions(posts):
    """Given a collection of posts (in StackExchange JSON format), return our
    model's predictions for whether or not each post will be closed.
    """

    # Read in Model
    with open('model.pickle', 'rb') as f:
        scaler, classifier = pickle.load(f)
    data = [cleandata.extract_data_vector(post) for post in posts]
    X = np.array(data, dtype=np.float64)
    X_scaled = scaler.transform(X)
    preds = classifier.predict(X_scaled)
    return preds


# If called as a script: rebuild the model.
if __name__ == '__main__':
    build_model()

