import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import svm, preprocessing, tree, cross_validation
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

# Read in the data
csvfile = open('cleandata.csv', newline='')
reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
next(reader)
data = np.array([row for row in reader])

# Split the data up in to our inputs (X) and outputs (y)
X = data[:, :-1]
X_scaled = preprocessing.scale(X)
y = data[:, -1]

# Initialize several learners, to be compared momentarily
logistic = LogisticRegression(C=.3)
mysvc = svm.SVC()
linsvc = svm.LinearSVC()
knn = KNeighborsClassifier(4, weights='distance')
mytree = tree.DecisionTreeClassifier()
myforest = RandomForestClassifier()

for clf,name in [(logistic, "Logistic Regression"), (mysvc, "SVC"), (linsvc, "Linear SVC"), (knn, "K-nearest Neighbors"), (mytree, "Decision Tree"), (myforest, "Random Forest")]:

    scores = cross_validation.cross_val_score(clf, X_scaled, y, cv=400)
    print(name + ":")
    print("Accuracy: {:0.4f} - {:0.4f}".format(scores.mean()-scores.std(), scores.mean()+scores.std()))
    print()
