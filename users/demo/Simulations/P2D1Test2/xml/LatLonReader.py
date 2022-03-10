import xml.etree.ElementTree as ET


f = open("neighborhood.xml", "r")
fileIntero = f.read()
root = ET.fromstring(fileIntero)

for house in root.findall('chargingStation'):  # READ XML FILE
        # inserisci qui il codice per la creazione di una cs
        houseId = house.get('id')
        CSlat=house.find('lat').text
        #CSlat=house[0].text
        #CSlong=house[1].text
        CSlong=house.find('long').text
        print("HouseID:", houseId, "Lat: ",CSlat,"Long: ", CSlong)
