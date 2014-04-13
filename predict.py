import numpy as np
from scipy.special import expit as sigmoid
from scipy.optimize import minimize
import json
import csv

def predict(X):
    f = open('parameters.json', 'r')
    (mean, std, s, Theta1, Theta2) = json.load(f)
    f.close()

    if X.ndim == 1:
        n = X.size
        m = 1
        X = X.reshape((1, n))
    else:
        m, n = X.shape
    
    mean = np.array(mean)
    std = np.array(std)
    Theta1 = np.array(Theta1)
    Theta2 = np.array(Theta2)

    X = X.copy()
    X = (X - mean) / std

    v1 = np.dot(np.hstack((np.ones((m, 1)), X)), Theta1.transpose())
    h1 = sigmoid(v1)
    v2 = np.dot(np.hstack((np.ones((m, 1)), h1)), Theta2.transpose())
    p = sigmoid(v2)
    return p

if __name__ == '__main__':
    f = open('cleandata.csv', newline='')
    reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
    next(reader)
    data = np.array([row for row in reader])
    X = data[:,:-1]
    y = data[:,-1]
    probs = predict(X)
    y = y.reshape(probs.shape)
    error = np.sum(np.abs(y - np.around(probs)))
    print("Correctly predicted {:.2%}".format(1-error/X.shape[0]))
