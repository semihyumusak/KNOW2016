import os.path
import pickle
import numpy as np
from sklearn.svm import LinearSVC
import re
from KNOW_2016_feature_generatorv9functions import *
from KNOW_2016_feature_generatorv9functions import populateFeaturesAggregated
from KNOW_2016_feature_generatorv9functions import k_fold_generator

def initLists(featureListTest,featureListTrain):
    featureListTrain.clear()
    featureListTest.clear()
        # Initialize Feature Sets
    for row in trainingsetAttributes:
        URI = row[1].replace('"','')
        featureDictTrain = {"uri":URI}
        ID = row[0].replace('"','')
        featureDictTrain.update({"ID":ID})
        featureListTrain.append(featureDictTrain)
    for row in testsetAttributes:
        URI = row[1].replace('"','')
        featureDictTest = {"uri":URI}
        ID = row[0].replace('"','')
        featureDictTest.update({"ID":ID})
        featureListTest.append(featureDictTest)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
def KFoldPredictionScore (X,y,k,header):

    from sklearn.svm import SVC
    from sklearn.feature_extraction import DictVectorizer
    vec = DictVectorizer()

    try:
        accuracy = 0.0
        for X_train, y_train, X_test, y_test in k_fold_generator(X, y, k):

            vec = DictVectorizer()
            fit = vec.fit(X_train)

            X_train_counts = fit.transform(X_train)
            X_test_counts = fit.transform(X_test)
            clf = SVC(kernel="linear", C=0.025)
            try:
                clf.fit(X_train_counts.toarray(), y_train)
                #predict = clf.predict(X_test_counts.toarray())
                accuracy += clf.score(X_test_counts.toarray(),y_test)
                # coef = clf._get_coef()
               # print(np.argsort(coef)[-20:])
                #for i in range(0,len(X_test)):
                    #print (X_test[i]['ID']+"\t"+y_test[i]+"\t"+predict[i])
            except BaseException as b:
                    print (b)
        print (header+"\t"+str(accuracy))
    except BaseException as b:
        print (b)


# Load of attribute and test values
with open('trainingDataset.tsv','r') as f:
    trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
with open('testDataset.tsv','r') as f:
    testsetAttributes=[x.strip().split('\t') for x in f][1:]
with open('trainingDataset.tsv','r') as f:
    trainingsetLabels=[x.strip().split('\t')[6] for x in f][1:]

# Query caching prevents the algorithm to send DBpedia requests if it is already in the local storage
queryCache = set()
with open('querycache.txt','r') as f:
    lines = f.readlines()
    for line in lines:
        queryCache.add(line.replace("\n",""))
cacheFile = open('querycache.txt', 'a',encoding='utf-8')

i = 0
featureListTest = []
featureListTrain = []

# Initialize Feature Sets
initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #1- Baseline
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://purl.org/dc/terms/subject> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"1:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #2- ARTIST
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/ontology/artist> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"2:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #3- Artist types
    getAttributeWithCaching("SELECT  ?o where { <"+featDict['uri']+"> <http://dbpedia.org/ontology/artist> ?o1. ?o1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o.}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"3:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #4- GENRES
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/ontology/genre> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"4:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #5-LANGUAGE
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/ontology/language> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"5:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #6- How many other albums producer have?
    getNumericAttributeWithCaching( "SELECT count(?s) as ?o WHERE {  <"+featDict['uri']+"> <http://dbpedia.org/ontology/producer> ?o1. ?s  <http://dbpedia.org/ontology/producer> ?o1}", featDict, 40, 40, "Producer",featDict['uri'] , queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"6:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #7- Who recorded this album?
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/ontology/recordLabel> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"7:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #8- Are long albums more popular than others?
    getNumericAttributeWithCaching( "SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/ontology/runtime> ?o}", featDict, 2800, 2800, "Runtime" ,featDict['uri'] , queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"8:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #9-Number of awards of an artist
    getNumericAttributeWithCaching("SELECT  count(?o1) as ?o WHERE { <"+featDict['uri']+">  <http://dbpedia.org/ontology/artist> ?artist. ?artist <http://dbpedia.org/property/award> ?o1}", featDict, 3, 3, "ArtistAward" ,featDict['uri'] , queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"9:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #10-Who is the director of the album?
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/director> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"10:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #11-Region
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/region> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"11:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #12-studio
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/studio> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"12:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #13-totalLength
    getNumericAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/totalLength> ?o}", featDict, 2900, 2900, "TotalLength" ,featDict['uri'] , queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"13:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #14-song writer
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/writer> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"14:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #15-Reviewers
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/rev> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"15:")

initLists(featureListTest,featureListTrain)
for featDict in featureListTrain:
    #16- Topics related to the artist of the album
    getAttributeWithCaching("select ?o where {<"+featDict['uri']+"> <http://dbpedia.org/ontology/artist> ?o1. ?o1 <http://purl.org/dc/terms/subject> ?o}",featDict, queryCache, cacheFile)
KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"16:")
