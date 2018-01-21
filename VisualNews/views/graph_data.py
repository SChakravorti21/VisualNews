from flask import Flask, Blueprint, request, json
import datetime
from pprint import pprint
from faker import Factory

from pymongo import MongoClient
from bson.objectid import ObjectId

mod = Blueprint('data', __name__)

fake = Factory.create()

@mod.route('/request-data/', methods=['GET', 'POST'])
def get_clusters():
    args = request.args
    num_clusters = int(args.get('num_clusters'))
    start_time = int(args.get('start_time'))
    end_time = int(args.get('end_time'))
    x_axis = args.get('x-axis')
    y_axis = args.get('y-axis')
    value = args.get('value')

    clusters = []

    curr = datetime.datetime.now().hour

    start_time = curr + start_time
    if start_time < 0:
        start_time = 24 + start_time
    print("\n\n\n\n\n\n")
    print("start_time: {}".format(start_time))

    end_time = curr + end_time
    if end_time < 0:
        end_time = 24 + end_time

    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client['VisualNews']

    cluster_name = 'clusters_{}'.format(start_time)
    cluster_collection = db[cluster_name]

    cursor = cluster_collection.find({})
    for doc in cursor:
        
        pprint(doc)
        clusters.append({
            "cluster_name": cluster_name,
            "cluster_size": doc["cluster_size"],
            "cluster_labels": doc["labels"],
            "_id": str(doc["_id"]),
            "y": doc[y_axis],
            "x": doc[x_axis],
            "value": doc[value],
            "color": str(fake.hex_color())
        })

    while start_time != end_time:
        start_time = (start_time + 1) % 24
        cluster_name = 'clusters_{}'.format(start_time)
        cluster_collection = db[cluster_name]
        cursor = cluster_collection.find({})
        for doc in cursor:
            pprint(doc)
            clusters.append({
                "cluster_name": cluster_name,
                "cluster_size": doc["cluster_size"],
                "cluster_labels": doc["labels"],
                "_id": str(doc["_id"]),
                "y": doc[y_axis],
                "x": doc[x_axis],
                "value": doc[value],
                "color": str(fake.hex_color())
            })

    def sort_key(d):
        return d['cluster_size']

    print(num_clusters)
    new_clusters = sorted(clusters, key=sort_key, reverse=True)

    return json.dumps(new_clusters[:num_clusters])

@mod.route('/get-cluster-data/', methods=['GET'])
def get_cluster_data():
    args = request.args;
    _id = args.get('_id');
    cluster_name = args.get('cluster_name')

    print(_id)
    print(cluster_name)

    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client['VisualNews']

    collection = db[cluster_name]

    doc = collection.find_one({'_id': ObjectId(str(_id))}, {'_id': 0})

    pprint(doc)
    doc = json.dumps(doc)

    return doc
