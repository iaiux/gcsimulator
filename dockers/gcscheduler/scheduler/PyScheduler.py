# coding=utf-8
import numpy as np
import requests
import json
import threading
import utils.CreateCSV
import utils.CreateCSandEV
import utils.CreatePmax
import utils.pareto
import utils.scatter
import subprocess

EVlat = []
EVlong = []
CSlat = []
CSlong = []
dict_EV = {}
EVmaxpow=[]
BVmaxpow=[]
PVid=[]
profiles=[]
def getLatLon(jsonRequest):
    switchsubject = jsonRequest["message"]["subject"]
    if switchsubject == "CREATE_EV":
        print("arrivata un EV")
        lat = float(jsonRequest["message"]["lat"])
        long = float(jsonRequest["message"]["long"])
        # print("Latitude: ", lat, "Longitude: ", long)
        return lat, long, "EV"
    if switchsubject == "CREATE_ENERGY_GROUP" and jsonRequest["message"].get("lat") and jsonRequest["message"].get(
            "long"):
        print("arrivata un CS")
        lat = float(jsonRequest["message"]["lat"])
        long = float(jsonRequest["message"]["long"])
        # print("Latitude: ", lat, "Longitude: ", long)
        return lat, long, "CS"
    else:
        return None, None, None

def getRequest(count):
    # r =requests.get("http://parsec2.unicampania.it:10021/getmessage")
    # r =requests.get("http://127.0.0.1:10021/getmessage")
    r = requests.get("http://greencharge.simulator:10021/getmessage")
    json_object = json.loads(r.text)
    # pairs = json_object.items()
    message = json_object['message']
    subject = ""
    print(json_object)
    if message != "no new message":  # ho dovuto mettere questo if perché se non lo mettessi
        subject = message['subject']  # quando il messaggio è no new message non ha subject e quindi
    # mi va in errore perché non è un dict
    if subject == "CREATE_EV":
        dict_EV[message['id']] = message
        EVmaxpow.append(float(message["max_ch_pow_ac"]))
    if subject== "CREATE_BATTERY":
        BVmaxpow.append(float(message["max_ch_pow_ac"]))
    if subject=="PREDICTION_UPDATE" and message["id"] not in PVid:
        PVid.append(message["id"])
        profiles.append(message["profile"])
    if subject == "LOAD" or subject == "HC" or subject == "CREATE_EV" or subject == "CREATE_ENERGY_GROUP":
        lat, long, type = getLatLon(json_object)

        if type == "EV":
            EVlat.append(lat)
            EVlong.append(long)
        elif type == "CS":
            CSlat.append(lat)
            CSlong.append(long)
    if subject == "SIMULATION_END" and count == 0:
        ind_dist = utils.CreateCSV.createCSVFile(CSlat, CSlong, EVlat, EVlong)
        values = utils.CreateCSV.CreateValuesFile(len(EVlat), len(CSlat))
        print("EVLats: ", EVlat)
        print("EVLongs: ", EVlong)
        print("CSlat: ", CSlat)
        print("CSLongs: ", CSlong)
        count += 1
        print("Avvio con simulator data " + values + " " + ind_dist)
        subprocess.call("python3 utils/multi_obiettivo.py " + values + " " + ind_dist + " " + "simulator", shell=True)
        print("Avvio con opendata")
        utils.CreateCSandEV.main()
        utils.CreatePmax.PmaxCreator(EVmaxpow,"EVPmax.csv")
        utils.CreatePmax.PmaxCreator(BVmaxpow,"BVPmax.csv")
        #subprocess.call("python3 utils/multi_obiettivo.py values_opendata.csv ind_distance_opendata.csv opendata",shell=True)
        #utils.pareto.draw_pareto("out_pareto_simulator.csv", "pareto_simulator.png")
        #utils.pareto.draw_pareto("out_pareto_opendata.csv", "pareto_opendata.png")
        #utils.scatter.main(len(CSlat), "simulator")
        #csv = np.genfromtxt("data/values_opendata.csv", delimiter=",")
        #n_stations = int(csv[1, 1])  # legge il numero di CS
        #utils.scatter.main(n_stations, "opendata")
    threading.Timer(2.0, getRequest, args=(count,)).start()


if __name__ == '__main__':
    getRequest(0)
