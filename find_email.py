from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson import BSON
from bson import json_util
import json ,re

elastic_array=[]
elastic_company=[]
elastic_indices=[]
email_elastic = {}
tmpindices=[]
email_elastic['Elastic_getMail'] = []
array_mongo=[]
company_mongo=[]
email_mongo = {}
email_mongo['MongoDb_getMail'] = []

def read_elastic():
    with open('open_DB.json') as f:
        data = json.load(f)
    datas=(data["ElasticSearch"])
    for i in range(len(datas)):
        elastic_array.append(datas[i]['ip'])
        elastic_company.append(datas[i]['company'])
def read_mongodb():
    with open('open_DB.json') as f:
        data = json.load(f)
    datas=(data["MongoDb"])
    for i in range(len(datas)):
        array_mongo.append(datas[i]['ip'])
        company_mongo.append(datas[i]['company'])

def search_elastic():
    len_indices=1
    for i in range(len(elastic_array)):
        host="http://"+elastic_array[i]+":9200"
        es = Elasticsearch(host,timeout=5)
        try:
            for index in es.indices.get_alias("*"):
                tmpindices.append(index)
            elastic_indices.append(tmpindices)
            len_indices=1
        except:
            elastic_indices.append("")
            len_indices=0
        if len_indices==1:
            for j in range(len(elastic_indices[i])):
                    indices=elastic_indices[i][j]
                    try:
                        es = Elasticsearch(host,timeout=5)
                        data=es.search(index=indices,size=10000,body={
                            "query": {
                                "match_all": {}
                            }
                        })
                        datas = json.dumps(data , indent=4)
                        emails = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", datas)
                        unique_list = list()
                        unique_list.clear()
                        for x in emails:
                            if x not in unique_list:
                                unique_list.append(x)
                        if len(unique_list)>0:
                            write_elastic(unique_list,i,j)
                    except:
                        datas=""

def search_mongo():
    flow=1
    for i in range(len(array_mongo)):
        client = MongoClient(array_mongo[i], 27017)
        try:
            databases=client.database_names()
            flow=1
        except:
            databases=""
            flow=0
        if flow==1:
            for j in range(len(databases)):
                db = client[databases[j]]
                collectionarray=db.collection_names()
                for x in range(len(collectionarray)):
                    collection= db[collectionarray[x]]
                    post=collection.find()
                    lpost = list(post)
                    posts = json.dumps(lpost , indent=4, default=json_util.default)
                    emails = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", posts)
                    unique_list = list()
                    unique_list.clear()
                    for x in emails:
                        if x not in unique_list:
                            unique_list.append(x)
                    if len(unique_list)>0:
                        databaseslist = databases[j].split('*!~')
                        collectionarraylist = databases[j].split('*!~')
                        write_mongo(unique_list,i,databaseslist,collectionarraylist)

def write_mongo(emails,array_index,database_names,collection_names):
    email_mongo['MongoDb_getMail'].append({
        'ip': array_mongo[array_index],
        'company': company_mongo[array_index],
        'database_names': database_names[0],
        'collection_names':collection_names[0],
        'mail' : emails
    })
    with open('mongodb_mail.json', 'w') as outfile:
        json.dump(email_mongo, outfile, indent=4)

def write_elastic(emails,array_index,indices_index):
    email_elastic['Elastic_getMail'].append({
        'ip': elastic_array[array_index],
        'company': elastic_company[array_index],
        'indices': elastic_indices[array_index][indices_index],
        'mail' : emails
    })
    with open('elastic_mail.json', 'w') as outfile:
        json.dump(email_elastic, outfile, indent=4)

def main():
    read_elastic()
    search_elastic()
    read_mongodb()
    search_mongo()
if __name__ == '__main__':
    main()
