import os.path

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
codec = "utf-8"
with open('trainingDataset.tsv','r') as f:
    trainingsetAttributes=[x.strip().split('\t') for x in f][1:]

for row in trainingsetAttributes:
    URI = row[1]
    ID = row[0]
    reviewURL = 'http://www.metacritic.com/music/'
    reviewPATH1 = re.sub('[^0-9a-zA-Z-!+()]+', '-',row[2].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
    reviewPATH2 = re.sub('[^0-9a-zA-Z-!+()]+', '-',row[3].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
    if reviewPATH1.startswith("-"):
        reviewPATH1 = reviewPATH1[1:len(reviewPATH1)]
    if reviewPATH1.endswith("-"):
        reviewPATH1 = reviewPATH1[0:len(reviewPATH1)-1]
    if reviewPATH2.startswith("-"):
        reviewPATH2 = reviewPATH2[1:len(reviewPATH2)]
    if reviewPATH2.endswith("-"):
        reviewPATH2 = reviewPATH2[0:len(reviewPATH2)-1]
    reviewURLPath = reviewURL+ reviewPATH1.lower()+"/"+reviewPATH2.lower()+"/"+"critic-reviews"

    try:
        import os.path
        if not os.path.isfile('MetacriticReviews/'+ID+'.txt'):

            try:
                req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                soup = BeautifulSoup(webpage)
                with open('MetacriticReviews/'+ID+'.txt', 'wb') as f:
                    for souprow in soup('ol', {'class': 'reviews critic_reviews'}):
                        for souprowin in souprow('div', {'class': 'review_body'}):
                            try:
                                f.write((souprowin.text.strip()+"\n\t").encode('utf-8'))
                            except BaseException as b:
                                print(b)

            except BaseException as b:
                reviewURLPath = reviewURL+ reviewPATH1.lower()+"/"+"critic-reviews"
                req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                soup = BeautifulSoup(webpage)
                with open('MetacriticReviews/'+ID+'.txt', 'wb') as f:
                    for souprow in soup('div', {'class': 'review_body'}):
                        try:
                            f.write((souprow.text.strip()+"\n\t").encode('utf-8'))
                        except BaseException as b:
                            print(b)




    except BaseException as b:
        print(ID +"-"+ reviewPATH1 +"-"+reviewPATH2)



print("test")
with open('testDatasetLabeled.tsv','r') as f:
    testsetAttributes=[x.strip().split('\t') for x in f][1:]

import re
for row in testsetAttributes:
    URI = row[1]
    ID = row[0]
    reviewURL = 'http://www.metacritic.com/music/'
    reviewPATH1 = re.sub('[^0-9a-zA-Z-!+()]+', '-',row[2].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
    reviewPATH2 = re.sub('[^0-9a-zA-Z-!+()]+', '-',row[3].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
    if reviewPATH1.startswith("-"):
        reviewPATH1 = reviewPATH1[1:len(reviewPATH1)]
    if reviewPATH1.endswith("-"):
        reviewPATH1 = reviewPATH1[0:len(reviewPATH1)-1]
    if reviewPATH2.startswith("-"):
        reviewPATH2 = reviewPATH2[1:len(reviewPATH2)]
    if reviewPATH2.endswith("-"):
        reviewPATH2 = reviewPATH2[0:len(reviewPATH2)-1]
    reviewURLPath = reviewURL+ reviewPATH1.lower()[0:100]+"/"+reviewPATH2.lower()+"/"+"critic-reviews"

    try:
        import os.path
        if not os.path.isfile('MetacriticReviewsTest/'+ID+'.txt'):

            try:
                req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                soup = BeautifulSoup(webpage)
                with open('MetacriticReviewsTest/'+ID+'.txt', 'wb') as f:
                    for souprow in soup('ol', {'class': 'reviews critic_reviews'}):
                        for souprow in soup('div', {'class': 'review_body'}):
                            try:
                                f.write((souprow.text.strip()+"\n\t").encode('utf-8'))
                            except BaseException as b:
                                print(b)

            except BaseException as b:
                reviewURLPath = reviewURL+ reviewPATH1.lower()[0:100]+"/"+"critic-reviews"
                req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                soup = BeautifulSoup(webpage)
                with open('MetacriticReviewsTest/'+ID+'.txt', 'wb') as f:
                    for souprow in soup('div', {'class': 'review_body'}):
                        try:
                            f.write((souprow.text.strip()+"\n\t").encode('utf-8'))
                        except BaseException as b:
                            print(b)


    except BaseException as b:
        print(ID +"-"+ reviewPATH1 +"-"+reviewPATH2)


with open('TrainReviews.nt', 'w',encoding='utf-8') as reviewsFile:
    with open('trainingDataset.tsv','r') as f:
        trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
    with open('trainingDataset.tsv','r') as f:
        trainingsetAttributes=[x.strip().split('\t') for x in f][1:]
    with open('testDataset.tsv','r') as f:
        testsetAttributes=[x.strip().split('\t') for x in f][1:]
    for row in trainingsetAttributes:
        try:
            ID = row[0]
            URI = row[1]
            if os.path.isfile('MetacriticReviews/'+ID+'.txt'):
                with open('MetacriticReviews/'+ID+'.txt', 'rb') as f:
                    lines = f.readlines()
                    for line in lines:
                        reviewsFile.write("<"+URI+"> "+"<http://dbpedia.org/property/rev> "+ '"'+line.decode("utf-8").strip()+'"'+"@en .\n ")

        except BaseException as b:
            print(b)
with open('TestReviews.nt', 'w',encoding='utf-8') as reviewsFile:
    with open('trainingDataset.tsv','r') as f:
        trainingsetAttributes=[x.strip().split('\t') for x in f][1:]

    for row in testsetAttributes:
        try:
            ID = row[0]
            URI = row[1]
            if os.path.isfile('MetacriticReviewsTest/'+ID+'.txt'):
                with open('MetacriticReviewsTest/'+ID+'.txt', 'rb') as f:
                    lines = f.readlines()
                    for line in lines:
                        reviewsFile.write("<"+URI+"> "+"<http://dbpedia.org/property/rev> "+ '"'+line.decode("utf-8").strip()+'"'+"@en .\n ")

        except BaseException as b:
            print(b)

