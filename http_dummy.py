

from flask import Flask, request,json #import main Flask class and request object



http_dummy_server = Flask(__name__, static_url_path="",static_folder="./webapp",) #create the Flask app

# Global variables to store info


TOTAL_EXIT = 0
TOTAL_ENTER = 0



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
@http_dummy_server.route('/counting', methods=['GET'])
def countings():
    global TOTAL_ENTER
    global TOTAL_EXIT

    data = {'total': {'enter': TOTAL_ENTER, 'exit': TOTAL_EXIT, 'dentro': TOTAL_ENTER-TOTAL_EXIT}}
    print("Current %s" % (data))
    response = http_dummy_server.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@http_dummy_server.route('/')
def root():
    return http_dummy_server.send_static_file("index.html")


@http_dummy_server.route('/reset', methods=['POST'])
def reset():
    global TOTAL_ENTER
    global TOTAL_EXIT

    TOTAL_EXIT = 0
    TOTAL_ENTER = 0

    data = {'msg': 'RESET has been executed'}
    response = http_dummy_server.response_class(
        status=200,
        response=json.dumps(data),
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    http_dummy_server.run(debug=True, port=5000) #run app in debug mode on port 5000

