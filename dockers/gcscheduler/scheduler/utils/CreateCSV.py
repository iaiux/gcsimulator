import csv
import itertools
import os


def createCSVFile(CSlat, CSlong, EVlat, EVlong):
    #print(CSlat, CSlong, EVlat, EVlong)
    with open("./data/ind_pos2.csv", 'w+', newline='') as file:
        writer = csv.writer(file)
        for latC, longC, latE, longE in itertools.zip_longest(CSlat, CSlong, EVlat, EVlong):
            if (latC != None and longC != None and latE != None and longE != None):
                writer.writerow([str(latC), str(longC), 0, str(latE), str(longE)])
            elif (latC != None and longC != None and latE == None and longE == None):
                writer.writerow([str(latC), str(longC), 0])
            elif (latC == None and longC == None and latE != None and longE != None):
                writer.writerow([0, 0, 0, str(latE), str(longE)])

def CreateValuesFile(N_cars,N_stations):
    with open("./data/values2.csv","w+",newline='')as file:
        writer=csv.writer(file)
        writer.writerow(["NCARS:",N_cars])
        writer.writerow(["NSTATIONS:", N_stations])


if __name__ == '__main__':
    print("HELLO")
    '''
    EVlat=[40.9801261315, 40.9801261315, 40.9801261315,40.9615476411, 40.9622413607, 40.9615292093, 40.9615332603]
    EVlong=[14.2112648752, 14.2112648752, 14.2112648752, 14.2631077766, 14.2500896752, 14.2631399632, 14.2631292343]
    CSlat=[40.9615476411, 40.9622413607, 40.9615292093, 40.9615332603]
    CSlong=[14.2631077766, 14.2500896752, 14.2631399632, 14.2631292343]
    createCSVFile(CSlat,CSlong,EVlat,EVlong)
    '''
