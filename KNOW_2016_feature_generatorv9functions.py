import time
import re
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET, SELECT, CONSTRUCT, ASK, DESCRIBE
def populateFeatureAll (featDict, queryCache, cacheFile):
    URI = featDict['uri']
    #1- Baseline
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://purl.org/dc/terms/subject> ?o}",featDict, queryCache, cacheFile)
    #2- ARTIST
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/ontology/artist> ?o}",featDict, queryCache, cacheFile)
    #3- Artist types
    getAttributeWithCaching("SELECT  ?o where { <"+URI+"> <http://dbpedia.org/ontology/artist> ?o1. ?o1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o.}",featDict, queryCache, cacheFile)
    #4- GENRES
    getAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/ontology/genre> ?o}",featDict, queryCache, cacheFile)
    #5-LANGUAGE
    getAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/ontology/language> ?o}",featDict, queryCache, cacheFile)
    #6- How many other albums producer have?
    getNumericAttributeWithCaching( "SELECT count(?s) as ?o WHERE {  <"+URI+"> <http://dbpedia.org/ontology/producer> ?o1. ?s  <http://dbpedia.org/ontology/producer> ?o1}", featDict, 40, 40, "Producer",featDict['uri'] , queryCache, cacheFile)
    #7- Who recorded this album?
    getAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/ontology/recordLabel> ?o}",featDict, queryCache, cacheFile)
    #8- Are long albums more popular than others?
    getNumericAttributeWithCaching( "SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/ontology/runtime> ?o}", featDict, 2800, 2800, "Runtime" ,featDict['uri'] , queryCache, cacheFile)
    #9-Number of awards of an artist
    getNumericAttributeWithCaching("SELECT  count(?o1) as ?o WHERE { <"+URI+">  <http://dbpedia.org/ontology/artist> ?artist. ?artist <http://dbpedia.org/property/award> ?o1}", featDict, 3, 3, "ArtistAward" ,featDict['uri'] , queryCache, cacheFile)
    #10-Who is the director of the album?
    getAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/property/director> ?o}",featDict, queryCache, cacheFile)
    #11-Region
    getAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/property/region> ?o}",featDict, queryCache, cacheFile)
    #12-studio
    getAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/property/studio> ?o}",featDict, queryCache, cacheFile)
    #13-totalLength
    getNumericAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/property/totalLength> ?o}", featDict, 2900, 2900, "TotalLength" ,featDict['uri'] , queryCache, cacheFile)
    #14-song writer
    getAttributeWithCaching("SELECT ?o WHERE { <"+URI+"> <http://dbpedia.org/property/writer> ?o}",featDict, queryCache, cacheFile)
    #15-Reviewers
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/rev> ?o}",featDict, queryCache, cacheFile)
    #16- Topics related to the artist of the album
    getAttributeWithCaching("select ?o where {<"+featDict['uri']+"> <http://dbpedia.org/ontology/artist> ?o1. ?o1 <http://purl.org/dc/terms/subject> ?o}",featDict, queryCache, cacheFile)

    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/collapsed> ?o}",featDict, queryCache, cacheFile)
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/award> ?o}",featDict, queryCache, cacheFile)
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/source> ?o}",featDict, queryCache, cacheFile)
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/extraColumn> ?o}",featDict, queryCache, cacheFile)
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/extra> ?o}",featDict, queryCache, cacheFile)
    getAttributeWithCaching("SELECT ?o WHERE { <"+featDict['uri']+"> <http://dbpedia.org/property/type> ?o}",featDict, queryCache, cacheFile)

def getAttributeWithCaching( sparqlquery, featDict,queryCache, cacheFile):
    sparqlqueryBase = sparqlquery[sparqlquery.index("{") + 1:sparqlquery.rindex("}")]
    sparqlqueryConstruct = "CONSTRUCT {"+sparqlqueryBase+"} WHERE {"+sparqlqueryBase+"}"
    sparqlqueryAsk = "ASK {"+sparqlqueryBase+"}"

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlqueryAsk)
    sparql.setReturnFormat(JSON)
    resultAsk = sparql.query().convert()

    if resultAsk["boolean"] or sparqlquery in queryCache:
        getAttributeLocal(sparqlquery, featDict, "http://localhost:3030/know2/query")
    else:
        try:
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setQuery(sparqlqueryConstruct)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        except BaseException as b:
            print (b)
            time.sleep(1)
        try:
            for result in results["results"]["bindings"]:
                sparql = SPARQLWrapper("http://localhost:3030/know2/update")
                if (str(result["o"]["value"])).startswith("http"):
                    updateQuery = "INSERT DATA {<%s> <%s> <%s>.}" % (str(result["s"]["value"]),str(result["p"]["value"]),str(result["o"]["value"]))
                else:
                    if str(result["o"]["value"]).isnumeric() :
                        updateQuery = "INSERT DATA {<%s> <%s> %s.}" % (str(result["s"]["value"]),str(result["p"]["value"]),str(result["o"]["value"]))
                    else:
                        updateQuery = "INSERT DATA {<%s> <%s> '%s'.}" % (str(result["s"]["value"]),str(result["p"]["value"]),re.sub('[^0-9a-zA-Z_-]+', '',result["o"]["value"]))
                sparql.setQuery(updateQuery)
                sparql.query()
        except BaseException as b:
            print (b)#+" "+"INSERT DATA "+ result["s"]["value"]+result["p"]["value"]+result["o"]["value"])
        getAttributeLocal(sparqlquery, featDict, "http://localhost:3030/know2/query")
    if sparqlquery not in queryCache:
        queryCache.add(sparqlquery)
        cacheFile.write(sparqlquery+"\n")


def getAttributeLocal (sparqlquery, featDict, localuri ):
    onerror = 1
    while onerror:
        try:
            sparql2 = SPARQLWrapper(localuri)
            sparql2.setQuery(sparqlquery)
            sparql2.setReturnFormat(JSON)
            results = sparql2.query().convert()

            for result in results["results"]["bindings"]:
                featDict.update({result["o"]["value"]:1})

            onerror = 0
        except BaseException as b:
            print (b)
            time.sleep(1)



def getNumericAttributeLocal  (sparqlquery, featDict, high, low, name ):

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlquery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    onerror=1
    while onerror:
        try:
            for result in results["results"]["bindings"]:
                try:
                    if int(float(result["o"]["value"].split("/")[4]))>= high:
                        featDict.update({name:"High"})
                    if int(float(result["o"]["value"].split("/")[4]))< high and int(float(result["o"]["value"].split("/")[4]))>low :
                        featDict.update({name:"Mid"})
                    if int(float(result["o"]["value"].split("/")[4]))<=low :
                        featDict.update({name:"Low"})
                except BaseException as b:
                    print (b)
            onerror=0
        except BaseException as b:
            print (b)
            time.sleep(1)
def getNumericAttributeLocalValue  (sparqlquery, featDict, high, low, name ):

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlquery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    onerror=1
    while onerror:
        try:
            for result in results["results"]["bindings"]:
                try:
                    featDict.update({name:int(float(result["o"]["value"].split('/')[4]))})
                except BaseException as b:
                    print (b)
            onerror=0
        except BaseException as b:
            print (b)
            time.sleep(1)

def getNumericAttributeWithCaching( sparqlquery, featDict, high, low, name, URI ,queryCache, cacheFile):

    predicateName = URI+name
    sparqlqueryBase = sparqlquery[sparqlquery.index("{") + 1:sparqlquery.rindex("}")]
    sparqlqueryConstruct = "CONSTRUCT {"+sparqlqueryBase+"} WHERE {"+sparqlqueryBase+"}"
    sparqlqueryAsk = "ASK {<%s> <%s> ?o.}"%(URI,predicateName)

    sparql = SPARQLWrapper("http://localhost:3030/know2/query")
    sparql.setQuery(sparqlqueryAsk)
    sparql.setReturnFormat(JSON)
    resultAsk = sparql.query().convert()

    numericSparqlQuery = "SELECT ?o WHERE { <%s> <%s> ?o}"%(URI,URI+name)
    if resultAsk["boolean"] or sparqlquery in queryCache:
        getNumericAttributeLocal( numericSparqlQuery, featDict, high, low, name )
    else:
        try:
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setQuery(sparqlquery)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        except BaseException as b:
            print (b)
            time.sleep(1)

        for result in results["results"]["bindings"]:
            sparql = SPARQLWrapper("http://localhost:3030/know2/update")
            updateQuery = "INSERT DATA {<%s> <%s> <%s>.}" % (URI,URI+name,str(result["o"]["value"]))
            sparql.setQuery(updateQuery)
            sparql.query()

    getNumericAttributeLocal( numericSparqlQuery, featDict, high, low, name )
    if sparqlquery not in queryCache:
        queryCache.add(sparqlquery)
        cacheFile.write(sparqlquery+"\n")

def k_fold_generator(X, y, k_fold):
    subset_size = int(len(X) / k_fold)
    for k in range(k_fold):
        X_train = X[:k * subset_size] + X[(k + 1) * subset_size:]
        X_valid = X[k * subset_size:][:subset_size]
        y_train = y[:k * subset_size] + y[(k + 1) * subset_size:]
        y_valid = y[k * subset_size:][:subset_size]

        yield X_train, y_train, X_valid, y_valid

