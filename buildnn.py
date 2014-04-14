import numpy as np
from scipy.special import expit as sigmoid
from scipy.optimize import fmin_cg
import csv
import json

lmbda = .1
hidden_layer_size = 30

def sigmoid_gradient(z):
    return sigmoid(z) * (1 - sigmoid(z))

def cost_function(nn_params, X, y):
    n = X.shape[1]
    s = hidden_layer_size
    m = X.shape[1]

    X = X.copy()
    nn_params = nn_params.copy()
    nn_params = nn_params.flatten()

    Theta1 = nn_params[0:s*(n+1)]
    Theta1 = Theta1.reshape([s, n+1])
    Theta2 = nn_params[s*(n+1):]
    Theta2 = Theta2.reshape([1, s+1])

    J = 0

    for i in range(m):
        v = X[i].reshape((n,1))
        a1 = np.vstack((np.ones((1,1)), v))
        z2 = np.dot(Theta1, a1)
        a2 = np.concatenate((np.ones((1,1)), sigmoid(z2)))
        z3 = np.dot(Theta2, a2)
        a3 = sigmoid(z3)
        
        J += (-y[i] * np.log(a3) - (1-y[i]) * np.log(1 - a3)) / m
    
    J += (lmbda / (2*m)) * np.sum((Theta1 * Theta1)[:,1:])
    J += (lmbda / (2*m)) * np.sum((Theta2 * Theta2)[:,1:])
    return J

def approx_grad(nn_params, X, y):
    eps = .00001
    grad = np.zeros(nn_params.shape)
    for i in range(nn_params.size):
        nudge = np.zeros(nn_params.shape)
        nudge[i] = eps
        above = cost_function(nn_params + nudge, X, y)
        below = cost_function(nn_params - nudge, X, y)
        grad[i] = (above - below) / (2*eps)
    return grad


def cost_grad(nn_params, X, y):
    n = X.shape[1]
    s = hidden_layer_size
    m = X.shape[0]

    X = X.copy()
    nn_params = nn_params.flatten()

    Theta1 = nn_params[0:s*(n+1)].reshape((s, n+1))
    Theta2 = nn_params[s*(n+1):].reshape((1, s+1))

    Theta1_grad = np.zeros(Theta1.shape)
    Theta2_grad = np.zeros(Theta2.shape)
    D1 = np.zeros(Theta1.shape)
    D2 = np.zeros(Theta2.shape)

    for i in range(m):
        v = X[i].reshape((n,1))
        a1 = np.vstack((np.ones((1,1)), v))
        z2 = np.dot(Theta1, a1)
        a2 = sigmoid(z2)
        a2 = np.vstack((np.ones((1,1)), a2))
        z3 = np.dot(Theta2, a2)
        a3 = sigmoid(z3)
        
        delta3 = a3 - y[i]
        delta2 = np.dot(Theta2.transpose(), delta3)[1:] * sigmoid_gradient(z2)
        delta2 = delta2.reshape((s,1))
        
        a1 = a1.reshape((n+1,1))
        D1 = D1 + np.dot(delta2, a1.transpose())
        
        delta3 = delta3.reshape((1,1))
        a2 = a2.reshape((s+1,1))
        D2 = D2 + np.dot(delta3, a2.transpose())

    Theta1_grad = D1 / m
    Theta2_grad = D2 / m
    
    reg1 = (lmbda / m) * Theta1
    reg1[:,0] = 0
    reg2 = (lmbda / m) * Theta2
    reg2[:,0] = 0
    
    Theta1_grad += reg1
    Theta2_grad += reg2
    
    grad = np.concatenate((Theta1_grad.flatten(), Theta2_grad.flatten()))
    approx = approx_grad(nn_params, X, y)
    print("Difference in computed norms: {0}".format(np.linalg.norm(grad-approx)))
    return grad


Nfeval = 1
def callback(nn_params, X, y):
    global Nfeval
    print(Nfeval, cost_function(nn_params, X, y))
    Nfeval += 1


def build_nn_model():
    csvfile = open('cleandata.csv', newline='')
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    next(reader)
    data = np.array([row for row in reader])
    
    X = data[:, :-1]
    y = data[:, -1]

    print("TOTAL Y: ", np.sum(y))

    n = X.shape[1]
    m = X.shape[0]
    s = hidden_layer_size

    mean = np.mean(X, axis=0)
    mean.reshape((1, mean.size))
    std = np.std(X, axis=0)
    std.reshape((1, std.size))
    X = (X - mean) / std
    # Random initialization
    eps = .12
    nn_params0 = np.random.random((s*(n+1) + 1*(s+1))) * 2 * eps - eps
    
    cost = lambda t: cost_function(t, X, y)
    grad = lambda t: cost_grad(t, X, y)
    cb = lambda t: callback(t, X, y)

    nn_params = fmin_cg(cost, nn_params0, callback=cb, maxiter=30 )
    Theta1 = nn_params[0:s*(n+1)]
    Theta1 = Theta1.reshape((s, n+1))
    Theta2 = nn_params[s*(n+1):].reshape((1, s+1))
   
    print("Done training network!")
    print("Total cost at termination: " + str(cost_function(nn_params, X, y)))
    f = open('parameters.json', 'w')
    json.dump((mean.tolist(), std.tolist(), s, Theta1.tolist(), Theta2.tolist()), f)

if __name__ == "__main__":
    build_nn_model()
