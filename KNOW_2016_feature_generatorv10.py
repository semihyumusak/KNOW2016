import os.path
import pickle
import numpy as np
from sklearn.svm import LinearSVC
import re
from KNOW_2016_feature_generatorv9functions import *
from KNOW_2016_feature_generatorv9functions import populateFeaturesAggregated
from KNOW_2016_feature_generatorv9functions import k_fold_generator

from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC
import matplotlib.pyplot as plt
def plot_coefficients(classifier, feature_names, top_features=10000):
 coef = classifier.coef_.ravel()
 top_positive_coefficients = np.argsort(coef)[-top_features:]
 top_negative_coefficients = np.argsort(coef)[:top_features]
 top_coefficients = np.hstack([top_negative_coefficients, top_positive_coefficients])
 top_coefficients =  np.argsort(coef)
 # create plot
 # plt.figure(figsize=(15, 5))
 #
 #
 # colors = ['red' if c < 0 else 'blue' for c in coef[top_coefficients]]
 # plt.bar(np.arange(2 * top_features), coef[top_coefficients], color=colors)
 feature_names = np.array(feature_names)
 # plt.xticks(np.arange(1, 1 + 2 * top_features), feature_names[top_coefficients], rotation=60, ha='right')
 for a in feature_names[top_coefficients]:
     print(a)
 for b in coef[top_coefficients]:
     print (b)
 plt.show()

def plotFeatures(featureListTrain,trainingsetLabels):
    cv = DictVectorizer()
    cv.fit(featureListTrain)
    print (len(cv.vocabulary_))
    print (cv.get_feature_names())
    X_train = cv.transform(featureListTrain)
    svm = LinearSVC()
    svm.fit(X_train, trainingsetLabels)
    plot_coefficients(svm, cv.get_feature_names())

def LoadDumps(name,featureListTest,featureListTrain):
    if os.path.isfile('train'+name) and os.path.isfile('test'+name):
        with open('train'+name,'rb') as f:
            featureListTrain = pickle.load(f)
        with open('test'+name,'rb') as f:
            featureListTest = pickle.load(f)
        return 1,featureListTest,featureListTrain
    else:
        return 0,featureListTest,featureListTrain
def SaveDump(name,featureListTest,featureListTrain):
    with open('train'+name,'wb') as f:
        pickle.dump(featureListTrain, f)
    with open('test'+name,'wb') as f:
        pickle.dump(featureListTest, f)

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
def TextFeatures ():
    import nltk
    from nltk.corpus import stopwords
    stemmer = nltk.stem.snowball.EnglishStemmer(ignore_stopwords=False)
    stop = stopwords.words('english')

    import nltk

    def get_words_in_reviews(reviews):
        all_words = []
        for (words, sentiment) in reviews:
            all_words.extend(words)
        return all_words

    def get_word_features(wordlist):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    # ------ ADDING TEXT FEATURES
    with open('trainingDataset.tsv','r') as f:
        trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
    import re
    uncleanedreviews = []
    reviews = []
    for row in trainingsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
                    uncleanedreviews.append((revs,str(row[6])))
        except BaseException as b:
            print(b)

    for (words,sentiment) in uncleanedreviews:
        words_filtered = [stemmer.stem(e.lower()) for e in words.split() if len(e) >= 3 and stemmer.stem(e.lower()) not in stop]
        reviews.append((words_filtered, sentiment))
    word_features = get_word_features(get_words_in_reviews(reviews))

    for row in trainingsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))

                    for featDict in featureListTrain:
                        if featDict['ID']==row[0].replace('"',''):
                            for word in revs.split():
                                root = stemmer.stem(word)
                                if root in word_features and root not in stop:
                                    featDict.update({root: 1})
            # else:
            #     print("dosya yok")
        except BaseException as b:
            print(b)

    for row in testsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviewsTest/'+ID+'.txt'):
                with open('MetacriticReviewsTest/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
                    for featDict in featureListTest:
                        if featDict['ID']==row[0].replace('"',''):
                            for word in revs.split():
                                root = stemmer.stem(word)
                                if root in word_features and root not in stop:
                                    featDict.update({root: 1})
            else:
                print(ID+"dosya yok")
        except BaseException as b:
            print(b)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
def KFoldPredictionScore (X,y,k,header):

    from sklearn.svm import SVC
    from sklearn.feature_extraction import DictVectorizer
    vec = DictVectorizer()


    names = ["Linear SVC", "Linear SVM","Nearest Neighbors",  "RBF SVM", "Decision Tree",
     "Random Forest", "AdaBoost", "Naive Bayes"]
    # names = ["Linear SVM","Linear SVM","Linear SVM","Linear SVM"]

    classifiers = [
    LinearSVC(),
    SVC(kernel="linear", C=0.025),
    KNeighborsClassifier(3),
    SVC(gamma=2, C=1),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GaussianNB()]
    # classifiers = [
    # SVC(kernel="linear", C=0.025),
    # SVC(kernel="linear", C=0.02),
    # SVC(kernel="linear", C=0.01)
    # ]

    for name, clf in zip(names, classifiers):
        try:
            accuracy = 0.0
            for X_train, y_train, X_test, y_test in k_fold_generator(X, y, k):

                vec = DictVectorizer()
                fit = vec.fit(X_train)

                X_train_counts = fit.transform(X_train)
                X_test_counts = fit.transform(X_test)
                # clf = SVC(kernel="linear", C=0.025)
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
            print (name+"\t"+header+"\t"+str(accuracy))
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

loaded, featureListTest,featureListTrain = LoadDumps("LCA",featureListTest,featureListTrain)
if not loaded:
    # Populate Linked Data Aggregated Features
    for featDict in featureListTrain:
        populateFeaturesAggregated(featDict, queryCache, cacheFile)
    for featDict in featureListTest:
        populateFeaturesAggregated(featDict, queryCache, cacheFile)
    SaveDump("LCA",featureListTest,featureListTrain)
#
# plotFeatures(featureListTrain,trainingsetLabels)
# KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"LCA ")

initLists(featureListTest,featureListTrain)

loaded, featureListTest,featureListTrain = LoadDumps("LC",featureListTest,featureListTrain)
if not loaded:    # Populate Linked Data Features
    for featDict in featureListTrain:
        populateFeatureAll(featDict, queryCache, cacheFile)
    for featDict in featureListTest:
        populateFeatureAll(featDict, queryCache, cacheFile)
    SaveDump("LC",featureListTest,featureListTrain)

# KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"LC ")

loaded, featureListTest,featureListTrain = LoadDumps("LCA.LC",featureListTest,featureListTrain)
if not loaded:    # Populate Linked Data Features
    # Populate Linked Data Aggregated Features
    for featDict in featureListTrain:
        populateFeaturesAggregated(featDict, queryCache, cacheFile)
    for featDict in featureListTest:
        populateFeaturesAggregated(featDict, queryCache, cacheFile)
    SaveDump("LCA.LC",featureListTest,featureListTrain)

plotFeatures(featureListTrain,trainingsetLabels)
# KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"LC+LCA ")

cacheFile.close()

# ------ ADDING TEXT FEATURES
loaded, featureListTest,featureListTrain = LoadDumps("LCA.LC.TEXT",featureListTest,featureListTrain)
if not loaded:    # Populate Linked Data Features
    TextFeatures()
    SaveDump("LCA.LC.TEXT",featureListTest,featureListTrain)

# ----- ENG TEXT FEATURES

KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"LC+LCA+TEXT ")

initLists(featureListTest,featureListTrain)
loaded, featureListTest,featureListTrain = LoadDumps("TEXT",featureListTest,featureListTrain)
if not loaded:    # Populate Linked Data Features
    TextFeatures()
    SaveDump("TEXT",featureListTrain,featureListTest)

# KFoldPredictionScore(featureListTrain,trainingsetLabels,10,"TEXT ")

from sklearn.svm import SVC
from sklearn.feature_extraction import DictVectorizer
vec = DictVectorizer()

fit = vec.fit(featureListTrain)
X_train_counts = fit.transform(featureListTrain)
X_test_counts = fit.transform(featureListTest)
clf = SVC(kernel="linear", C=0.025)
clf.fit(X_train_counts.toarray(), y)
predict = clf.predict(X_test_counts.toarray())
print ("TEST SET PREDICTION")
for v in predict:
    print(v)
