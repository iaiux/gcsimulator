import csv
from scipy.optimize import minimize
import random
import numpy as np
ts=[]
EPV=[]
PmaxEV=[]
PmaxBV=[]

def function(x):
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    N=len(ts)-1
    y=[]
    y=x[N*Mev+1:]
    x=x[:N*Mev]
    somma=0
    for i in range(0,N):
        for j in range (0,Mbv):
            somma=somma+(abs(deltat*(x[i+j]*PmaxEV[j])+(y[i+j]*PmaxBV[j]))-EPV[i])
    return somma

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

def AdjustLen():

    while(len(PmaxEV)>len(PmaxBV)):
        PmaxBV.append(0)
    while(len(PmaxBV)>len(PmaxEV)):
        PmaxEV.append(0)

def xijcons(x):
    Mev=len(PmaxEV)
    N=len(ts)
    return x[:Mev*N] #maggiore di 0
def xijcons2(x):
    Mev=len(PmaxEV)
    N=len(ts)
    return  -1*(x[:Mev*N])-1 #minore di 1

def xijcons3(x):
    Mev=len(PmaxEV)
    N=len(ts)
    return  (x[Mev*N+1:])+1 #minore di 1


def main(EVfilename,BVfilename,PVfilename):
    ReadEnergyPV(PVfilename)
    ReadPmax(EVfilename,BVfilename)
    AdjustLen()
    N=len(ts)-1
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    xij=[]
    for i in range(0,N*Mev+N*Mbv):
        #xij.append(round(random.uniform(0,1), 2))
        xij=np.append(xij,0)
    cons = ({'type': 'ineq','fun' : xijcons},
            {'type': 'ineq','fun' : xijcons2},
            {'type': 'ineq','fun' : xijcons3})
    b1 = [(0,1) for i in range(N*Mev)]
    b2 = [(-1,1) for i in range(N*Mbv)]
    bnds=b1+b2
    print(bnds)
    print(len(bnds))
    res=minimize(function,xij,method='SLSQP',bounds=bnds, options={'maxiter': 50, 'disp': True})
    #function(xij)
    for i in res.x:
        print(i)

if __name__ == '__main__':
    main("EVPmax.csv","BVPmax.csv","2021-09-26_PVenergy.csv")
