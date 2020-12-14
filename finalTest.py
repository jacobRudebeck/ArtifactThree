#!/usr/bin/python
import json
from bson import json_util
from bson.json_util import dumps
import bottle
from bottle import route, run, request, abort
#imports for database
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection['market']
collection = db['stocks']
collection_comp = db['company']




@route('/createStock/<ticker>', method='POST')
def createStock(ticker):
  data = request.json
  data.update( {'Ticker' : ticker} ) 
  print(data)
  for item in data:
    print(data[item])
  record_created = collection.insert(data) 
  added_doc = collection.find_one({"_id":record_created})
  stars = "*" * 50+"\n"
  return stars+ "Created Document \n "+dumps(added_doc)+"\n\n "+stars 



@route('/updateStock/<ticker>', method='PUT')
def createStock(ticker):
  data = request.json 
  print(data) 
  query = { "Ticker" :ticker} 
  
  for item in data:
    print(data[item])
    new_update =  { "$set":{item:data[item]}}
    collection.update(query,new_update)
  updated_doc = collection.find({"Ticker":ticker})
  stars = "*" * 50+"\n" 
  result = dumps(updated_doc) #
  return stars+"\n"+str(result)+"\n"+stars
  



@route('/getStock/<Ticker>', method='GET')
def get_data(Ticker):
  found_doc = collection.find({"Ticker":Ticker}) 

  return dumps(found_doc)


@route('/deleteStock/<Ticker>', method='GET')
def get_update(Ticker):
  query = {"Ticker" :Ticker}
  print(query) 
  result = collection.delete_many(query) 
  return "document with Ticker "+Ticker+" Has beed deleted from the stocks Collection" 

@route('/stockReport', method='POST')
def run_create(): 
  mylist = request.json.get('list') 
  mylist = mylist.replace("[","") #removes [
  mylist = mylist.replace("]","") #removes ]
  mylist = list(mylist.split(",")) #create a list 
  items = list()
  print(mylist)
  
  for name in mylist:
    print(name)
    item = getReport(name)
    print(item)
    items.append("Report For Ticker "+name+" \n"+item+"\n\n")
  return items #return a lit of items


@route('/industryReport/<industry>', method='GET')
def run_create(industry):
  industry = industry.replace("_"," ")
  print(industry)

  stage_one = { '$project': {'Industry':1, 'Ticker':1,'Performance (YTD)':1,'Performance (Week)':1,'Shares Outstanding':1,'Volume':1 } }
  stage_two = { '$match': { "Industry": industry } }
  stage_three = { '$group': { '_id': "$Industry", 'Total Shares Outstanding': {'$sum': "$Shares Outstanding" },
                           'Average Performance (YTD)':{'$avg':"$Performance (YTD)"},
                           'Average Performance (Week)':{'$avg':'$Performance (Week)'},
                           'Max Shares Outstanding':{'$max':'$Shares Outstanding'},
                           'Total Volume':{'$sum':'$Volume'} } }
  
  stage_four = { '$limit' : 5 }
  query = [stage_one,stage_two,stage_three,stage_four]
  result=collection.aggregate(query)
  result = dumps(result)
  return "-------- \n Portfolio Report For The First Five "+industry+" Industries \n\n "+result+" \n-------- \n\n"


@route('/portfolio/<company>', method='GET')
def run_create(company):
  company = company.replace("_"," ") 
  print(company)
  query = {"Company":company} 
  result=collection.find(query) 
  result = dumps(result)
  return "-------- \n Portfolio Report For "+company+" Company \n\n "+result+" \n-------- \n\n"
    
    

def getReport(ticker):
  
  stage_one = { '$project': { 'Ticker':1,'Performance (YTD)':1,'Performance (Week)':1,'Shares Outstanding':1,'Volume':1 } }
  stage_two = { '$match': { "Ticker": ticker } }
  stage_three = { '$group': { '_id': "$Ticker", 'Total Shares Outstanding': {'$sum': "$Shares Outstanding" },
                           'Average Performance (YTD)':{'$avg':"$Performance (YTD)"},
                           'Average Performance (Week)':{'$avg':'$Performance (Week)'},
                           'Max Shares Outstanding':{'$max':'$Shares Outstanding'},
                           'Total Volume':{'$sum':'$Volume'} } }
  query = [stage_one,stage_two,stage_three] 
  result=collection.aggregate(query) 
  result = dumps(result)
  return result
  
if __name__ == '__main__':
  run(debug=True,reloader = True)
  #run(host='localhost', port=8080)
  