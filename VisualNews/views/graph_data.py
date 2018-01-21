from flask import Flask, Blueprint, request
import datetime

mod = Blueprint('data', __name__)

@mod.route('/request-data/', methods=['GET', 'POST'])
def get_clusters():
    num_clusters = request.num_clusters
    start_time = request.start_time
    end_time = request.end_time
    x_axis = request.x_axis
    y_axis = request.y_axis
    value = request.value

    clusters = []

    curr = datetime.date.now().hour

    start_time = curr - start_time
    if start_time < 0:
        start_time = 24 + start_time

    end_time = curr - end_time
    if end_time < 0:
        end_time = 24 + end_time

    from pymongo import MongoClient

    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client['VisualNews']

    cluster_collection = db['clusters_{}'.format(start_time)]

    cursor = cluster_collection.find({})
    for doc in cursor:
        clusters.append({
            "y": doc[y_axis],
            "x": doc[x_axis],
            "value": doc[value]
        })

    while start_time != end_time:
        start_time = (start_time + 1) % 24
        cluster_collection = db['clusters_{}'.format(start_time)]
        cursor = cluster_collection.find({})
        for doc in cursor:
            clusters.append({
                "y": doc[y_axis],
                "x": doc[x_axis],
                "value": doc[value]
            })
        

    
    