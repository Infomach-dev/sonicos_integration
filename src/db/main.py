import pymongo

client = pymongo.MongoClient("<InsertConnectionString>")
db = client['snwl-portal']

usersCollection = db['users']
firewallsCollection = db['firewalls']
companiesCollection = db['companies']