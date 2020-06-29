#CODIGO INCOMPLETO NA LINHA 73

from json.decoder import JSONDecodeError
from logging import DEBUG
import logging
from flask import Flask, request, json  # import main Flask class and request object

http_dummy_server = Flask(__name__, static_url_path="", static_folder="./webapp", )  # create the Flask app
logging.basicConfig()
LOG_APP = logging.getLogger('app')
logging.getLogger().setLevel(logging.INFO)

# Global variables to store info

LABEL = None
TOTAL_EXIT = 0
TOTAL_ENTER = 0
MAX_PEOPLE = 0

valueList = []
configList = []

try:
    with open('output.json', 'r') as f:
        valueList = json.load(f)
except Exception as ex:
    LOG_APP.info('output.json not found')
LOG_APP.info('History: %s' % str(valueList))

#try:
#    for item in valueList:



def what_color():
    if (TOTAL_ENTER - TOTAL_EXIT) >= MAX_PEOPLE:
        return "red"
    if (TOTAL_ENTER - TOTAL_EXIT) > (MAX_PEOPLE * 3 / 4):  # 75%
        return "orange"
    if (TOTAL_ENTER - TOTAL_EXIT) > (MAX_PEOPLE / 2):  # 50%
        return "yellow"
    return "white"


# Recives post in json with countings
# format o json:
#  {"enter":"1","exit":"2"}
# Can be teste using curl with
#  curl --header "Conteuest POST   --data '{"enter":"1","exit":"2"}'  http://127.0.0.1:5000/upload/sensor1
#
@http_dummy_server.route('/json/<sensor_id>', methods=['POST'])
def counting_json(sensor_id):
    global valueList
    req_data = request.get_json()

    print(req_data)

    if req_data:
        print("HELPME")
        # for item in values.items():
        #     if item['label'] == req_data['label']:
        #         valueData = {"label": None, "enter": None, "exit": None}
        #         valueData['enter'] += item['enter']
        #         valueData['exit'] += item['exit']
        #         valueList.update(valueData)
        #         print('AAAAA' + valueList)

    print("Revice counting from sensor %s = %s" % (sensor_id, req_data))
    return countings()


# Recives post
#
@http_dummy_server.route('/form/<sensor_id>', methods=['POST'])
def counting_post(sensor_id):
    global valueList
    LOG_APP.info('New counting received for device %s' % str(sensor_id))
    req_data = request.values
    found = False
    for item in valueList:
        if req_data["label"] == item["label"]:
            found = True
            LOG_APP.info('Label %s already exists! updating values...' % str(req_data["label"]))
            item["enter"] = int(item["enter"]) + int(req_data["enter"])
            item["exit"] = int(item["exit"]) + int(req_data["exit"])
    if not found:
        LOG_APP.info('Label %s does not exist! appending new value...' % str(req_data["label"]))
        valueList.append(req_data)
    save_data()
    response = http_dummy_server.response_class(
        response=json.dumps(valueList),
        status=200,
        mimetype='application/json'
    )
    return response


def save_data():
    global valueList

    try:
        with open('output.json', 'w') as f:  # PLANO > append da informação
            json.dump(valueList, f)
    except Exception as ex:
        LOG_APP.exception("Error saving history file", ex)
    try:
        with open('output.json', 'r') as f:
            valueList = json.load(f)
    except:
        print("bufixing")

# Return current counting
@http_dummy_server.route('/counting', methods=['GET'])
def countings():
    global valueList

    data = valueList

    LOG_APP.info("Current %s" % data)

    return http_dummy_server.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )


@http_dummy_server.route('/')
def root():
    return http_dummy_server.send_static_file("index.html")


@http_dummy_server.route('/reset', methods=['POST'])
def reset():
    global valueList
    req_data = request.get_json()

    for item in valueList:
        if req_data["label"] == item["label"]:
            item["enter"] = 0
            item["exit"] = 0


    data = {'msg': 'RESET has been executed'}
    response = http_dummy_server.response_class(
        status=200,
        response=json.dumps(data),
        mimetype='application/json'
    )


    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@http_dummy_server.route('/change', methods=['POST'])
def getMaxValue():
    global configList
    req_data = request.get_json()
    MAX_PEOPLE = int(req_data["maxx"])

    data = {'msg': 'RESET has been executed'}
    response = http_dummy_server.response_class(
        status=200,
        response=json.dumps(data),
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    http_dummy_server.run(debug=True, port=5000)  # run app in debug mode on port 5000
