import csv

from matplotlib import pyplot as plt
from scipy.optimize import minimize
import numpy as np
import random
import PlotGraph
ts=[]
EPV=[]
PmaxEV=[]
PmaxBV=[]
CapsEV=[]
EnInitEV=[]
EVdemand=[]
CapsBV=[]
EnInitBV=[]
BVdemand=[]

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
        temp=0
        for j in range (0,Mev):
            temp=temp+ deltat*(x[i+j]*PmaxEV[j])
        for j in range (0,Mbv):
            temp=temp+ (y[i+j]*PmaxBV[j])
        temp = temp-EPV[i]
        somma =somma+abs(temp)
    print(somma)
    return somma

def CalculateConsumption(x,y):
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    N=len(ts)-1
    Consumption=[]
    for i in range(0,len(ts)):
        temp=0
        for j in range (0,Mev):
            temp=temp+ deltat*(x[i+j]*PmaxEV[j])
        for j in range (0,Mbv):
            temp=temp+ deltat*(y[i+j]*PmaxBV[j])
        Consumption.append(temp)

    return Consumption



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
            PmaxEV.append(float(riga[5]))
    with open("../csv/"+BVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            PmaxBV.append(float(riga[5]))

def ReadEnergyEV(EVfilename):
    with open("../csv/"+EVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            CapsEV.append(float(riga[1]))
            EnInitEV.append(float(riga[3]))
            EVdemand.append(float(riga[4]))
    #print(CapsEV,EnInitEV,EVdemand)
def ReadEnergyBV(BVfilename):
    with open("../csv/"+BVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            CapsBV.append(float(riga[1]))
            EnInitBV.append(float(riga[3]))
            BVdemand.append(float(riga[4]))


'''L’energia assorbita dalle auto  sommata all’energia iniziale 
non può superare la  capacità della batteria'''
def consCapEV(x):
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    cons=0
    N=len(ts)-1
    Mev=len(PmaxEV)
    EVen=0
    y=[]
    y=x[:N*Mev]
    for i in range(0,N+1):
        for j in range(0,Mev):
            cons=cons+ (deltat*y[i+j]*PmaxEV[j])+EnInitEV[j]
    for j in range(0,Mev):
        EVen=EVen+EnInitEV[j]

    return -cons+EVen
'''L’energia assorbita deve essere almeno uguale a quella richiesta.'''
def consEVdemand(x):
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    cons=0
    demand=0
    N=len(ts)-1
    Mev=len(PmaxEV)
    y=[]
    y=x[:N*Mev]
    for i in range(0,N):
        for j in range(0,Mev):
            cons=cons+ (deltat*y[i+j]*PmaxEV[j])
    for j in range(0,Mev):
        demand=demand+EVdemand[j]
    return cons-demand


'''L’energia accumulata dalla batteria deve essere sempre maggiore o uguale a 0'''
def consBVaccumulate(x):
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    cons=0
    BVStart=0
    N=len(ts)-1
    Mbv=len(PmaxBV)
    Mev=len(PmaxEV)
    y=x[N*Mev+1:]
    for i in range(0,N):
        for j in range(0,Mbv):
            cons=cons+ (deltat*y[i+j]*PmaxBV[j])
    for j in range(0,Mbv):
        BVStart=BVStart+EnInitBV[j]

    return cons+BVStart
'''L’energia accumulata dalla batteria deve essere sempre minore della capacità'''
def consBVaccumulate2(x):
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    cons=0
    BVStart=0
    BVCap=0
    N=len(ts)-1
    Mbv=len(PmaxBV)
    Mev=len(PmaxEV)
    y=x[N*Mev+1:]
    for i in range(0,N):
        for j in range(0,Mbv):
            cons=cons+ (deltat*y[i+j]*PmaxBV[j])
    for j in range(0,Mbv):
        BVStart=BVStart+EnInitBV[j]
        BVCap=BVCap+ CapsBV[j]
    return -cons-BVStart+BVCap

def main(PVfilename,EVfilename,BVfilename):
    Consumption=[]
    ReadEnergyPV(PVfilename)
    ReadPmax(EVfilename,BVfilename)
    #AdjustLen()
    ReadEnergyEV(EVfilename)
    ReadEnergyBV(BVfilename)
    N=len(ts)-1
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    xij=[]
    for i in range(0,N*Mev+N*Mbv):
        #xij.append(round(random.uniform(0,1), 2))
        xij=np.append(xij,0)
    b1 = [(0,1) for i in range(N*Mev)]
    b2 = [(-1,1) for i in range(N*Mbv)]
    bnds=b1+b2
    cons = ({'type': 'ineq','fun' : consCapEV},
            {'type': 'ineq','fun' : consEVdemand},
            {'type': 'ineq','fun' : consBVaccumulate},
            {'type': 'ineq','fun' : consBVaccumulate2})
    res=minimize(function,xij,method='L-BFGS-B',bounds=bnds,constraints=cons,options={'disp': True, 'maxls': 20, 'iprint': -1, 'gtol': 1e-05, 'eps': 1e-08, 'maxiter': 15000, 'ftol': 2.220446049250313e-09, 'maxcor': 10, 'maxfun': 15000})
    print(res.x)
    for i in res.x:
       print(i,end=',')

    xr=res.x[0:Mev*N]
    yr=res.x[Mev*N+1:]
    Consumption=CalculateConsumption(xr,yr)
    PlotGraph.SingleDraw(ts,EPV,"Production (kWh)")
    PlotGraph.SingleDraw(ts,Consumption,"Consumption (kWh)")


if __name__ == '__main__':
    main("2021-09-26_PVenergy.csv","EVenergyandPmax.csv","BVenergyandPmax.csv")
