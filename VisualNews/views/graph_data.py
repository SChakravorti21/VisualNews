from flask import Flask, Blueprint, request

mod = Blueprint('data', __name__)

@mod.route('/request-data/', methods=['GET', 'POST'])
def get_clusters():
    num_clusters = request.num_clusters
    start_time = request.start_time
    end_time = request.end_time
    x_axis = request.x_axis
    y_axis = request.y_axis
    value = request.value
    