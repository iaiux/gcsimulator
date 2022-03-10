import csv
import os


def createCSVFile(CSlat, CSlong, EVlat, EVlong):
    print(CSlat, CSlong, EVlat, EVlong)
    with open("../data/CS_pos.csv", 'w+', newline='') as CSf:
        CSwriter = csv.writer(CSf)
        for lat, long in zip(CSlat, CSlong):
            CSwriter.writerow([str(lat), str(long)])
    with open("../data/EV_pos.csv", 'w+', newline='') as EVf:
        EVwriter = csv.writer(EVf)
        for lat, long in zip(EVlat, EVlong):
            EVwriter.writerow([str(lat), str(long)])


if __name__ == '__main__':
    print("HELLO")
    '''
    EVlat=[40.9801261315, 40.9801261315, 40.9801261315]
    EVlong=[14.2112648752, 14.2112648752, 14.2112648752]
    CSlat=[40.9615476411, 40.9622413607, 40.9615292093, 40.9615332603]
    CSlong=[14.2631077766, 14.2500896752, 14.2631399632, 14.2631292343]
    createCSVFile(CSlat,CSlong,EVlat,EVlong)
    '''
