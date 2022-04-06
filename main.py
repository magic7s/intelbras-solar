import requests
import json
from login import LOGIN

BASE_URL = 'http://solar-monitoramento.intelbras.com.br/'

s = requests.Session()

# POST /login
# {"result":1}
r = s.post(BASE_URL + "login", data=LOGIN)
if r.json().get("result") == 1:
    print("Login Success")
else:
    print("ERROR: ", r.text)

# POST /index/getPlantListTitle
# [{"id":"25404","timezone":"-3","plantName":"Ana Paula "}]
r = s.post(BASE_URL + "index/getPlantListTitle")
plants = r.json()
plant_id = plants[0].get("id")
print(plant_id)

# POST panel/getDevicesByPlantList
# {"result":1,"obj":{"currPage":1,"pages":1,"pageSize":4,"count":1,"ind":1,"datas":[{"pac":"0.7","sn":"ASF4K61A2147066A","plantName":"Ana Paula ","location":"","alias":"ASF4K61A2147066A","status":"1","eToday":"27.6","lastUpdateTime":"2022-04-06 18:14:22","datalogSn":"HPEXXX0421450935","datalogTypeTest":"EPWU 2000","deviceModel":"EGT 4600 PRO","bdcStatus":"0","deviceTypeName":"tlx","eTotal":"699.5","eMonth":"144.7","nominalPower":"4600","accountName":"Ana Paula Julidori","timezone":"-3","timeServer":"2022-04-07 05:14:22","plantId":"25404","deviceType":"0"}],"notPager":false}}
get_plan_data = {'plantId': plant_id, 'currPage': 1}
r = s.post(BASE_URL + "panel/getDevicesByPlantList", data=get_plan_data)
all_devices = json.loads(r.text)
print(all_devices)
