from flask import Flask, jsonify, request
from bson.json_util import dumps
import os, yaml, requests, time
from internals import * 

app = Flask(__name__)

config = getConfig()
ROOT_PATH = os.getcwd()

@app.route("/getData", methods=['GET'])
def getData():
  parameter = request.args.get('url')
  searchQuery = {}
  if parameter:
    searchQuery = {
      "url": parameter
    }
  jsonData = dumps(MongoFind("response_times", searchQuery))
  response = app.response_class(
    response=jsonData,
    status=200,
    mimetype='application/json'
  )
  return response
    

if __name__ == "__main__":
  print("🚀 Starting the server.")
  app.run(port=5000, debug=True)