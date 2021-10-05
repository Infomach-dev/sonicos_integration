import pymongo

client = pymongo.MongoClient("mongodb+srv://api-admin:Infomach%402021@cluster0.b94hv.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client['snwl-portal']

usersCollection = db['users']
firewallsCollection = db['firewalls']
companiesCollection = db['companies']