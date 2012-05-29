#sessionizer
#at the end I can discard the complex queries
# Author: Niranjan Kamat, kamatn@cse.ohio-state.edu

from sets import Set
from sqlparser import ParsedQuery
import matplotlib.pyplot as plt
import operator
import re

def padWithZero(a):
    if int(a)<10:
        a='0' + str(a)
        return a
    else:
        return str(a)

def isQueryValid(query):
    query=query.lower()
    
    badWords=['0x','between','inner','join','href','http','left','outer']
    for b in badWords:
        if b in query:
            return 0
    return 1

def getDateAsValue(theTime):
    theTime=theTime.strip()
    delimiters='[/|:| ]'
    tokens=re.split(delimiters,theTime)
    if '' in tokens:
        tokens=tokens.remove('')
    tokens[0]=padWithZero(tokens[0])
    tokens[1]=padWithZero(tokens[1])
    tokens[2]=padWithZero(tokens[2])
    tokens[3]=padWithZero(tokens[3])
    tokens[4]=padWithZero(tokens[4])
    tokens[5]=padWithZero(tokens[5])
    if tokens[6]=='PM':
        tokens[3]=str(int(tokens[3])+12)
    removeAMPM=tokens[0:6]
    timeValue=''.join(removeAMPM)
    return timeValue
    
    

fileName="2006Lines400000ModifiedCleanBugRemoved.txt"
fileHandle=open(fileName,"r")

queryDict=dict()

tok=';;'

jaccardThreshold=0.5

fileNameSessionized="OutputFile1.txt"
fileHandleSessionized=open(fileNameSessionized,"w")

while 1:
    line=fileHandle.readline()
    #print line
    if not line:
        break
        
    tokens=line.split(";;")
    
    theTime=tokens[0]
    logID=tokens[1]
    clientIP=tokens[2]
    query=tokens[3]
    
    value= str(theTime) + tok +str(clientIP) + tok + str(query)
    
    if clientIP in queryDict:
        oldValue=queryDict[clientIP]
        oldValue.append(value)
        queryDict[clientIP]=oldValue
    else:
        emptyList=[]
        emptyList.append(value)
        queryDict[clientIP]=emptyList

print 'Done queryDict'
raw_input()

#ClientIP is the key.     
for key in queryDict:
    print 'key= ' + key
    if key=='143.210.37.169':
        continue
	
    valueList=queryDict[key]
    """for v in valueList:
        print v
    raw_input()"""
    tempDict=dict()#used to sort. create one big key    
    for val in valueList:
        tokens=val.split(';;')
        theTime=tokens[0]
        clientIP=str(tokens[1])
        query=tokens[2]        
        dateValue=getDateAsValue(theTime)    
        tempDict[query]=dateValue
        """print 'query= ' + query 
        print 'dateValue= ' + dateValue
        raw_input()"""
    if len(tempDict)>0:
        tempDict=sorted(tempDict.iteritems(), key=operator.itemgetter(1))     
       # queryFeatureMap=dict()
        lentempDict=len(tempDict)
        
        #for i99 in range(lentempDict):
            #print tempDict[i99]
            #print tempDict[i99][0]
        #raw_input()
        for i in range(lentempDict):
            queryToParseQuery=tempDict[i][0]
         #   print 'i= '+ str(i) + 'q= ' + queryToParseQuery			
            queryFeatures=ParsedQuery(queryToParseQuery)
            if i==lentempDict-1:           
                fileHandleSessionized.write(queryToParseQuery)
            else:
                print1=1
          #      print range(i+1,lentempDict)
                for j in range(i+1,lentempDict):
           #         print 'j= ' + str(j) 
                    nextQuery=tempDict[j][0]
            #        print  'n= ' + nextQuery					
                    nextQueryFeatures=ParsedQuery(nextQuery)
                    """print  queryFeatures.features
                    print  nextQueryFeatures.features
                    """
                    #print 'queryFeatures.features= ' + str(queryFeatures.features)
                    #print 'nextQueryFeatures.features= ' + str(nextQueryFeatures.features) 
                    Numerator=set(queryFeatures.features) & set (nextQueryFeatures.features)
                    Denominator=set(queryFeatures.features) | set (nextQueryFeatures.features)
                    
                    #print 'Numerator= ' + str(Numerator)
                    #print 'Denominator= ' + str(Denominator)
                    #raw_input() 
                            
                    jaccard=float(len(Numerator))/len(Denominator)
                    
             #       print jaccard
              #      raw_input()
                    if jaccard>jaccardThreshold :
                        print1 =0
                        break
                if print1==1:
                    fileHandleSessionized.write(queryToParseQuery)
       # raw_input()
					
                                                
#print arrayOfNumberOfCharacters    
print 'reached here'
       
