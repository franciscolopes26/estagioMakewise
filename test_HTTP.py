import requests

url = 'http://127.0.0.1:5000/form/sensor1'
myobj = {'enter': '1',"exit":"3"}

x = requests.post(url, data = myobj)

print(x.text)
