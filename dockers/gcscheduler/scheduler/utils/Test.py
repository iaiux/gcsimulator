import csv
import numpy as np
from scipy.optimize import minimize

ts=[]
EPV=[]
PmaxEV=[]
PmaxBV=[]


def function(x,y):
    deltat=(float(ts[1])-float(ts[0]))/3600
    PmEV=np.array(PmaxEV)
    PmBV=np.array(PmaxBV)
    
    x=np.array(x)
    y=np.array(y)
    PmEV=np.append(PmEV,0)
    print(PmEV,PmBV,EPV)
    return sum(abs(deltat*(x*PmEV+y*PmBV))-EPV)
    
    
def ReadEnergyPV(PVfilename):
    with open("../csv/"+PVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            ts.append(riga[0])
            EPV.append(float(riga[2]))
        #print(ts,EPV)

def ReadPmax(EVfilename,BVfilename):
    with open("../csv/"+EVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            PmaxEV.append(float(riga[0]))
    with open("../csv/"+BVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            PmaxBV.append(float(riga[0]))

def main(EVfilename,BVfilename,PVfilename):
    ReadEnergyPV(PVfilename)
    ReadPmax(EVfilename,BVfilename)
    #minimize(function,x0)
    print(function([ 3.3 , 7.2 ,16.5 ,22. , 22. ],[12.,12., 12., 12. ,10. ,10.]))
    #x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
    #y0=np.array([1.3, 0.7, 0.8, 1.9, 1.2,1.2])
    #res = minimize(function, x0,y0, method='nelder-mead', options={'xatol': 1e-8, 'disp': True})
    #A_, E_, m_, n_ = res.x
    

if __name__ == '__main__':
    main("EVPmax.csv","BVPmax.csv","2021-09-26_PVenergy.csv")

