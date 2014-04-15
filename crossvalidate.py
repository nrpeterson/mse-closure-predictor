import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import svm, preprocessing, tree, cross_validation
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

import pymysql

# Read in the data
f = open('dbase.conf', 'r')
dbase, user, passwd = f.readline().rstrip().split(',')
f.close()
conn = pymysql.connect(user=user, passwd=passwd, db=dbase)
cur = conn.cursor()

count = cur.execute("SELECT * FROM trainingdata")
print("Fetched {} records!".format(count))

data = np.array([row for row in cur], dtype=np.float64)
cur.close()
conn.close()

# Split the data up in to our inputs (X) and outputs (y)
X = data[:, :-1]
X_scaled = preprocessing.scale(X)
y = data[:, -1]

# Initialize several learners, to be compared momentarily
logistic1 = LogisticRegression(C=.1)
logistic2 = LogisticRegression(C=.3)
logistic3 = LogisticRegression(C=1)
logistic4 = LogisticRegression(C=5)
logistic5 = LogisticRegression(C=10)
linsvc = svm.LinearSVC()
knn = KNeighborsClassifier(4, weights='distance')
mytree = tree.DecisionTreeClassifier()
myforest = RandomForestClassifier()

for clf,name in [(logistic1, "Logistic Regression C=.1"), (logistic2, "Logistic Regression C=.3"), (logistic3, "Logistic Regression C=1"), (logistic4, "Logistic Regression C=5"), (logistic5, "Logistic Regression C=10"), (linsvc, "Linear SVC"), (knn, "K-nearest Neighbors"), (mytree, "Decision Tree"), (myforest, "Random Forest")]:

    scores = cross_validation.cross_val_score(clf, X_scaled, y, scoring='recall', cv=400)
    print(name + ":")
    print("Accuracy: {:0.4f} - {:0.4f}".format(scores.mean()-scores.std()/2, scores.mean()+scores.std()/2))
    print()
