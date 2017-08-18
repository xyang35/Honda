import os
import numpy as np
import time
import pdb
import pickle as pkl

from sklearn.svm import LinearSVC
from scipy.stats import mode
from sklearn.decomposition import PCA

class SVMModel():

    def __init__(self, PCA=-1):
        self.PCA = PCA
        self.svm_model = None
        self.pca_model = None
        self.feasibility = False    # flag for whether model is trained
        self.old2new = None
        self.new2old = None

    def train(self, X, label):

        if self.PCA > 0:
            print ("PCA to %d dims ..." % self.PCA)
            self.pca_model = PCA(n_components = self.PCA)
            X = self.pca_model.fit_transform(X)
            print ("Explained variance ratio: ",
                    np.sum(self.pca_model.explained_variance_ratio_))

        # deal with missing label cases
        old2new = {}
        new2old = {}
        for i in range(len(label)):
            l = label[i]
            if l not in old2new:
                old2new[l] = len(new2old.keys())
                new2old[len(new2old.keys())] = l
            label[i] = old2new[l]

        self.old2new = old2new
        self.new2old = new2old
        C = len(new2old.keys())
        print ("Linear SVM: %d data samples with dim=%d and %d distinct labels" % 
                (X.shape[0], X.shape[1], C))

        self.svm_model = LinearSVC()
        self.svm_model.fit(X, label)
        print ("Training done!")
        print ("Training accuracy: %f" % self.svm_model.score(X, label))

        self.feasibility = True


    def save_model(self, output_path):

        # save the model
        pkl.dump({'svm': self.svm_model,
                'pca': self.pca_model,
                'new2old': self.new2old,
                'old2new': self.old2new},
                open(output_path+'svm_model.pkl', 'w'))


    def load_model(self, input_path):

        # load the model
        fin = pkl.load(open(input_path+'svm_model.pkl', 'r'))

        self.kmeans_model = fin['svm']
        self.pca_model = fin['pca']
        self.new2old = fin['new2old']
        self.old2new = fin['old2new']
        self.feasibility = True


    def predict(self, X):
        
        if self.svm_model is None:
            print "Error! You need to load a logistic regression model!"
            raise

        if self.PCA > 0 and self.pca_model is None:
            print "Error! We cannot find the PCA model!"
            raise

        if self.PCA > 0:
            X = self.pca_model.transform(X)

        result = self.svm_model.predict(X)
        for i in range(len(result)):
            result[i] = self.new2old[result[i]]
            
        return result

    def train_and_predict(self, X, label):

        self.train(X, label)
        return self.predict(X)

