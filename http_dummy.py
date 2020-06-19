
from flask import Flask, request #import main Flask class and request object
from flask import json


http_dummy_server = Flask(__name__) #create the Flask app

# Global variables to store info
TOTAL_ENTER = 0
TOTAL_EXIT = 0


# Recives post in json with countings
# format o json:
#  {"enter":"1","exit":"2"}
# Can be teste using curl with
#  curl --header "Conteuest POST   --data '{"enter":"1","exit":"2"}'  http://127.0.0.1:5000/upload/sensor1
#
@http_dummy_server.route('/json/<sensor_id>', methods=['POST'])
def counting_json(sensor_id):
    global TOTAL_ENTER
    global TOTAL_EXIT
    req_data = request.get_json()
    if req_data:
        if(req_data['enter']):
            TOTAL_ENTER += int(req_data['enter'])
        if (req_data['exit']):
            TOTAL_EXIT += int(req_data['exit'])
    print("Revice counting from sensor %s = %s" % (sensor_id,req_data))
    return countings()

# Recives post
#
@http_dummy_server.route('/form/<sensor_id>', methods=['POST'])
def counting_post(sensor_id):
    global TOTAL_ENTER
    global TOTAL_EXIT
    req_data = request.values
    if req_data:
        if (req_data['enter']):
            TOTAL_ENTER += int(req_data['enter'])
        if (req_data['exit']):
            TOTAL_EXIT += int(req_data['exit'])
    print("Revice counting from sensor %s = %s" % (sensor_id,(req_data['enter'],req_data['exit'])))
    return countings()


# Return current counting
@http_dummy_server.route('/', methods=['GET'])
def countings():
    global TOTAL_ENTER
    global TOTAL_EXIT
    data = { 'total' : { 'enter':TOTAL_ENTER, 'exit':TOTAL_EXIT }}
    print("Current %s" % (data))
    response = http_dummy_server.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response



if __name__ == '__main__':
    http_dummy_server.run(debug=True, port=5000) #run app in debug mode on port 5000

