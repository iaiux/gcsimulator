import csv
from scipy.optimize import minimize
import numpy as np
ts=[]
EPV=[]
PmaxEV=[]
PmaxBV=[]

def function(x,y):
    #altimenti ho un EV in meno di una batteria PmaxEV.append(PmaxEV[-1])
    deltat=(float(ts[1])-float(ts[0]))/3600
    sum=0
    for i in range(0,int(len(ts))-1):
        for j in range(0,int(len(PmaxEV))):
            sum=sum+deltat*abs(x[i+j]*PmaxEV[j]+y[i+j]*PmaxBV[j])-EPV[i]
    return sum


def ReadEnergyPV(PVfilename):
    with open("../csv/"+PVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            ts.append(riga[0])
            EPV.append(riga[2])
        #print(ts,EPV)

def ReadPmax(EVfilename,BVfilename):
    with open("../csv/"+EVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            PmaxEV.append(riga[0])
    with open("../csv/"+BVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            PmaxBV.append(riga[0])

def main(EVfilename,BVfilename,PVfilename):
    ReadEnergyPV(PVfilename)
    ReadPmax(EVfilename,BVfilename)
    #minimize(function,x0)
    #function()



if __name__ == '__main__':
    main("EVPmax.csv","BVPmax.csv","2021-09-26_PVenergy.csv")
