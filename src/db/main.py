import os
import pymongo

client = pymongo.MongoClient(os.environ["DB_CONN_STRING"])
db = client['snwl-portal']

usersCollection = db['users']
firewallsCollection = db['firewalls']
companiesCollection = db['companies']
