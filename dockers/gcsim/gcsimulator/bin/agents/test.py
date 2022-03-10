import requests
import json
info = {
    'sim_id' : '1',
    'time'  : '2',
    'subject' : '3',
    'id'  :  '3',
}
data = json.dumps({
    'response'  : info,
})

files = {
    'response' : json.dumps(info),
    'csvfile': open("test.py", 'rb')
}


payload = {"param_1": "value_1", "param_2": "value_2"}
files = {
     'response': (None, json.dumps(info), 'application/json'),
     'csvfile': ("test.py", open("test.py", 'rb'), 'application/octet-stream')
}



headers = {'Content-type': 'multipart/form-data'}
#files = {'csvfile': open("test.py", 'rb')}
r = requests.post("http://parsec2.unicampania.it:10021/postanswer", files=files)