import pymongo
import keys

client = pymongo.MongoClient(
    "mongodb+srv://" + keys.mongodb_user + "-j6nsa.mongodb.net/test?retryWrites=true&w=majority")
db = client['Bot']
coll = db['user_id']


# Create new user in DB
def writer(id_u, lang='eng', origin='Krakow'):
    doc = {'id': id_u, 'language': lang, 'origin': origin}
    coll.save(doc)


# Looking for user in DB
def reader(id_u):
    return coll.find_one({'id': id_u})


# Update user language information
def lang_updater(id_u, lang='eng'):
    coll.update({'id': id_u}, {'$set': {'language': lang}})


# Update user origin city information
def origin_updater(id_u, origin='Krakow'):
    coll.update({'id': id_u}, {'$set': {'origin': origin}})
