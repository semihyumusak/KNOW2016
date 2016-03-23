import os.path
import pickle

from KNOW2016_feature_generatorv8functions import populateFeatureAll
from KNOW2016_feature_generatorv8functions import k_fold_generator

# Load of attribute and test values
with open('trainingDataset.tsv','r') as f:
    trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
with open('testDataset.tsv','r') as f:
    testsetAttributes=[x.strip().split('\t') for x in f][1:]

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

# Populate Features
for featDict in featureListTrain:
    populateFeatureAll(featDict,queryCache)
for featDict in featureListTest:
    populateFeatureAll(featDict,queryCache)

cacheFile.close()

import nltk
from nltk.corpus import stopwords
stemmer = nltk.stem.snowball.EnglishStemmer(ignore_stopwords=False)
stop = stopwords.words('english')
# ------ ADDING TEXT FEATURES

if os.path.isfile('traindumpv8text') and os.path.isfile('testdumpv8text'):
    with open('traindumpv8text','rb') as f:
        featureListTrain = pickle.load(f)
    with open('testdumpv8text','rb') as f:
        featureListTest = pickle.load(f)

else:
    import nltk

    def get_words_in_tweets(tweets):
        all_words = []
        for (words, sentiment) in tweets:
            all_words.extend(words)
        return all_words

    def get_word_features(wordlist):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    def extract_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    # ------ ADDING TEXT FEATURES
    with open('trainingDataset.tsv','r') as f:
        trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
    import re
    uncleanedtweets = []
    tweets = []
    for row in trainingsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))
                    uncleanedtweets.append((revs,str(row[6])))
        except BaseException as b:
            print(b)

    for (words,sentiment) in uncleanedtweets:
        words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
        tweets.append((words_filtered, sentiment))
    word_features = get_word_features(get_words_in_tweets(tweets))

    for row in trainingsetAttributes:
        try:
            import os.path
            ID = row[0]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    revs = re.sub('[^0-9a-zA-Z ]+',"",f.read().decode("utf-8").replace("\n"," "))

                    for featDict in featureListTrain:
                        if featDict['ID']==row[0].replace('"',''):
                            for word in word_features:
                                if word in revs:
                                    featDict.update({word: 1})
            else:
                print("dosya yok")
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
                            for word in word_features:
                                if word in revs:
                                    featDict.update({word: 1})
            else:
                print(ID+"dosya yok")
        except BaseException as b:
            print(b)

    import re

    with open('traindumpv8text','wb') as f:
        pickle.dump(featureListTrain, f)
    with open('testdumpv8text','wb') as f:
        pickle.dump(featureListTest, f)

# ----- ENG TEXT FEATURES
with open('trainingDataset.tsv','r') as f:
    trainingsetLabels=[x.strip().split('\t')[6] for x in f][1:]

X=featureListTrain
y= trainingsetLabels

from sklearn.svm import SVC
from sklearn.feature_extraction import DictVectorizer
vec = DictVectorizer()


try:
        accuracy = 0.0
        for X_train, y_train, X_test, y_test in k_fold_generator(X, y, 10):

            vec = DictVectorizer()
            fit = vec.fit(X_train)

            X_train_counts = fit.transform(X_train)
            X_test_counts = fit.transform(X_test)
            clf = SVC(kernel="linear", C=0.025)
            try:
                clf.fit(X_train_counts.toarray(), y_train)
                predict = clf.predict(X_test_counts.toarray())
                for i in range(0,len(X_test)):
                    print (X_test[i]['ID']+"\t"+y_test[i]+"\t"+predict[i])
            except BaseException as b:
                    print (b)
except BaseException as b:
    print (b)


fit = vec.fit(X)
X_train_counts = fit.transform(X)
X_test_counts = fit.transform(featureListTest)
clf = SVC(kernel="linear", C=0.025)
clf.fit(X_train_counts.toarray(), y)
predict = clf.predict(X_test_counts.toarray())

for v in predict:
    print(v)
