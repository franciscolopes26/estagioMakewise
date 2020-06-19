import requests
from people_counter import *
url = 'http://127.0.0.1:5000/form/sensor1'
myobj = {'enter': total_left_AB,"exit": total_right_AB}

x = requests.post(url, data = myobj)

print(x.text)
