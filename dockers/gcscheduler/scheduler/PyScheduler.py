# coding=utf-8
import requests
import json
import threading
import utils.CreateCSV
import utils.pareto
import subprocess

EVlat = []
EVlong = []
CSlat = []
CSlong = []
dict_EV = {}



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


def sendResponse(jsonRequest):
    jsonResponse = {}
    jsonResponse["sim_id"] = jsonRequest["message"]["id"]
    jsonResponse["time"] = float(jsonRequest["time"]) + 10
    jsonResponse["id"] = jsonRequest["message"]["id"]
    switchsubject = jsonRequest["message"]["subject"]
    if switchsubject == "LOAD":
        jsonResponse["subject"] = "ASSIGNED_START_TIME"
        jsonResponse["ast"] = jsonRequest["message"]["est"].strip()
        jsonResponse["producer"] = "[0]:[0]"
        req = requests.post("http://greencharge.simulator:10021/postanswer", jsonResponse)
        # req=requests.post("http://parsec2.unicampania.it:10021/postanswer",jsonResponse)
        print("Req: ", req.text)
    # per ora gli hc non ci interessano quindi commento questo codice
    # elif switchsubject=="HC":
    #	jsonResponse["csvfile"]=jsonRequest["message"]["id"]+".csv"
    # jsonResponse["subject"]="HC_PROFILE"
    # incompleto
    # req=requests.post("http://parsec2.unicampania.it:10020/postmessage",jsonResponse)
    elif switchsubject == "EV":
        jsonResponse["subject"] = "EV_PROFILE"
        dict_EV_message_id = dict_EV[jsonRequest["message"]["id"]]
        dict_EV_message_id_capacity = dict_EV_message_id["capacity"]
        booked_charge = float(dict_EV_message_id_capacity) * float(jsonRequest["message"]["target_soc"]) - float(
            jsonRequest["message"]["soc_at_arrival"]) / 100
        available_energy = float(dict_EV_message_id["max_ch_pow_ac"]) * (
                int(jsonRequest["message"]["departure_time"]) - (int(jsonRequest["message"]["arrival_time"])))
        charged_energy = available_energy
        charged_0 = float(dict_EV_message_id_capacity) * float(jsonRequest["message"]["soc_at_arrival"]) / 100
        if available_energy >= booked_charge:
            charging_time = 3600 * charged_energy / float(dict_EV_message_id["max_ch_pow_ac"])
        csvstr = (str(jsonRequest["message"]["arrival_time"])) + "," + str(charged_0) + "\n"
        csvstr += str(charging_time + float(jsonRequest["message"]["arrival_time"])) + "," + str(
            charged_energy + charged_0) + "\n"
        with open("test.csv", 'w') as f:
            f.write(csvstr)
    # r = requests.post("http://parsec2.unicampania.it:10021/postanswer", files={'file': open('test.csv','r')})
    # r = requests.post("http://greencharge.simulator:10021/postanswer", files={'file': open('test.csv','r')})
    # print("Req: ", r.text)

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
    if subject == "LOAD" or subject == "HC" or subject == "CREATE_EV" or subject == "CREATE_ENERGY_GROUP":
        lat, long, type = getLatLon(json_object)
        if type == "EV":
            EVlat.append(lat)
            EVlong.append(long)
        elif type == "CS":
            CSlat.append(lat)
            CSlong.append(long)
        sendResponse(json_object)
    if subject == "SIMULATION_END" and count == 0:
        utils.CreateCSV.createCSVFile(CSlat, CSlong, EVlat, EVlong)
        utils.CreateCSV.CreateValuesFile(len(EVlat), len(CSlat))
        print("EVLats: ", EVlat)
        print("EVLongs: ", EVlong)
        print("CSlat: ", CSlat)
        print("CSLongs: ", CSlong)
        count += 1
        subprocess.call("python3 utils/multi_obiettivo.py", shell=True)
        #exec(open("utils/multi_obiettivo.py").read())
        utils.pareto.draw_pareto("out_pareto.csv","pareto.png")
    threading.Timer(2.0, getRequest,args=(count,)).start()


if __name__ == '__main__':
    getRequest(0)
