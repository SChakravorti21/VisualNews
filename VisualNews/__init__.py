from flask import Flask, render_template
from VisualNews.views import graph_data

app = Flask(__name__)

app.register_blueprint(graph_data.mod)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
