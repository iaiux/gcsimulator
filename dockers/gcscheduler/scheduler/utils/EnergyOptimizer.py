import csv
import datetime
import os

import pandas as pd
from matplotlib import pyplot as plt
from numpy import diff
from scipy.interpolate import PchipInterpolator
from scipy.optimize import minimize, Bounds, LinearConstraint
import numpy as np
import random
from datetime import datetime as date
from datetime import datetime
from datetime import timedelta
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
EnergyProd=[]
def function(x):
    global EnergyProd
    deltat=float((float(ts[1])-float(ts[0])))/3600
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    N=len(ts)-1
    y=x[N*Mev:]
    x=x[:N*Mev]
    somma=0

    for i in range(0, N-1):
        temp=0
        for j in range (0,Mev):
            temp=temp+ deltat*(x[i*Mev+j]*PmaxEV[j])
        for j in range (0,Mbv):
            temp=temp+ deltat * (y[i*Mbv+j]*PmaxBV[j])
        if i==0:
            temp = temp
        else:
            temp = temp-EnergyProd[i-1]
        somma =somma+abs(temp)
    print("Evaluating function: " ,somma)

    return somma


def CalculateConsumption(x,y):
    deltat=float((float(ts[1])-float(ts[0])))/3600
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    N=len(ts)
    Consumption=[]
    temp=0
    ConsBV=[]
    temp2=0
    for i in range(0,N):
        for j in range (0,Mev):
            temp=temp+ deltat*(x[i*Mev+j]*PmaxEV[j])
            temp2=temp2+ deltat*(x[i*Mev+j]*PmaxEV[j])
        for j in range (0,Mbv):
            temp=temp+ deltat*(y[i*Mbv+j]*PmaxBV[j])
            temp2=temp2+ deltat*(y[i*Mbv+j]*PmaxBV[j])
        Consumption.append(temp)
        if temp2<0:
            ConsBV.append(0)
        else:
            ConsBV.append(temp2)
    return Consumption, ConsBV

def ReadEnergyPV(PVfilename):
    with open("../csv/"+PVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            ts.append(riga[0])
            EPV.append(float(riga[2]))


def ReadPmax(EVfilename,BVfilename,Mev=None,Mbv=None):
    with open("../csv/"+EVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            if Mev is None or len(PmaxEV)<Mev:
                PmaxEV.append(float(riga[5]))
            else:
                break
    with open("../csv/"+BVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            if Mbv is None or len(PmaxBV)<Mbv:
                PmaxBV.append(float(riga[5]))
            else:
                break

def ReadEnergyEV(EVfilename,Mev=None):
    with open("../csv/"+EVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            if Mev is None or len(CapsEV)<Mev:
                CapsEV.append(float(riga[1]))
                EnInitEV.append(float(riga[3]))
                EVdemand.append(float(riga[4]))
            else:
                break
    #print(CapsEV,EnInitEV,EVdemand)
def ReadEnergyBV(BVfilename,Mbv=None):
    with open("../csv/"+BVfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            if Mbv is None or len(CapsBV)<Mbv:
                CapsBV.append(float(riga[1]))
                EnInitBV.append(float(riga[3]))
                BVdemand.append(float(riga[4]))
            else:
                break
'''L’energia assorbita dalle auto  sommata all’energia iniziale 
non può superare la  capacità della batteria'''
def consCapEV(x):
    deltat=float((float(ts[1])-float(ts[0])))/3600
    N=len(ts)-1
    Mev=len(PmaxEV)
    y=x[:N*Mev]
    for j in range(0, Mev):
        energy = EnInitEV[j]
        for i in range(0, N):
            energy += (deltat * y[i + j] * PmaxEV[j])
            if energy > CapsEV[j]:
                return -1
    return 1
'''L’energia assorbita deve essere almeno uguale a quella richiesta.'''
def consEVdemand(x):
    deltat=float((float(ts[1])-float(ts[0])))/3600
    N=len(ts)
    Mev=len(PmaxEV)
    y=x[:N*Mev]
    for j in range(0, Mev):
        energy = 0
        for i in range(0, N):
            energy += ((deltat)*y[i*Mev+j]*PmaxEV[j])
            if energy >= EVdemand[j]:
                break
        if energy < EVdemand[j]:
            return -1
    return 1



'''L’energia accumulata dalla batteria deve essere sempre maggiore o uguale a 0'''

def consBVaccumulate(x):
    deltat=float((float(ts[1])-float(ts[0])))/3600
    N=len(ts)
    Mbv=len(PmaxBV)
    Mev=len(PmaxEV)
    y=x[N*Mev:]
    for j in range(0, Mbv):
        energy = 0
        for i in range(0, N):
            energy += (deltat*y[i*Mbv+j]*PmaxBV[j])
            if energy < 0:
                return -1
    return 1
'''L’energia accumulata dalla batteria deve essere sempre minore della capacità'''

def consBVaccumulate2(x):
    deltat=float((float(ts[1])-float(ts[0])))/3600
    N=len(ts)
    Mbv=len(PmaxBV)
    Mev=len(PmaxEV)
    y=x[N*Mev:]
    for j in range(0, Mbv):
        energy = EnInitBV[j]
        for i in range(0, N):
            energy += (deltat*y[i*Mbv+j]*PmaxBV[j])
            if energy > CapsBV[j]:
                return -1
    return 1

def Deriva(x, y):
    x = np.array(x)
    y= np.array(y)
    dy=diff(y)/diff(x)
    return dy


def WriteRes(xr, yr,max,ft,Mev,N):
    today = date.today()
    d1 = today.strftime("%d-%m-%Y")
    #now = datetime.now()+timedelta(hours=2)
    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")
    date_today = d1 + "_" + current_time

    with open("../csv/output/XIJ_"+date_today+".csv","w+",newline='')as file:
        writer=csv.writer(file)
        writer.writerow([max,ft,Mev,N])
        for x in xr:
            writer.writerow([x])
        for y in yr:
            writer.writerow([y])
    return "XIJ_"+date_today

def CreateResults(resfile,num):
    global EnergyProd
    ts1=[]
    for t in ts:
        ts1.append(float(t)/3600)
    xnew,ynew=ReadRes(resfile)
    Consumption,ConsBV=CalculateConsumption(xnew,ynew)
    PowerProduction=Deriva(ts1,EPV)
    PowerConsumption=Deriva(ts1,Consumption)
    PlotGraph.SingleDraw(ts[:-1],EnergyProd,"Energy production","kWh","Energy Production Plot")
    PlotGraph.TripleDraw(ts[:-1],PowerProduction,PowerConsumption,Consumption,"PowerProduction","PowerConsumption","Consumption","kW","kWh","Power and Consumption Plot")
    PlotGraph.SingleDraw(ts[:-1],PowerProduction,"PowerProduction","kW","Power Production Plot")
    PlotGraph.SingleDraw(ts[:-1],PowerConsumption,"PowerConsumption","kW", "Power Consumption Plot")
    PlotGraph.DoubleDraw(ts[:-1],PowerProduction,"PowerProduction",PowerConsumption,"PowerConsumption","kW","Power Plot")
    PlotGraph.SingleDraw(ts,EPV,"Production","kWh","Cumulative Energy Production Plot")
    PlotGraph.SingleDraw(ts,Consumption,"Consumption","kWh","Cumulative Energy Consumption Plot")
    PVEnergyCons=calculateEnergyConPV(ConsBV)
    #PlotGraph.TripleDrawEnergies(ts,EPV,Consumption,PVEnergyCons,"Cumulative Energy Production","Cumulative Energy Consumption","Consumption from PV","kWh","kWh","Energy Plot")
    SelfC=sum(PVEnergyCons)/sum(EnergyProd)
    print("Autoconsumo con ",num," iterazioni: ", SelfC)
    plt.show()

def ReadRes(filename):
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    N=len(ts)
    xij=[]
    yij=[]
    i=0
    with open("../csv/output/"+filename+".csv", newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        next(reader)
        for riga in reader:
            if i<N*Mev:
                xij.append(float(riga[0]))
            else:
                yij.append(float(riga[0]))
            i=i+1
    return xij,yij

def calculateEnergyConPV(Consumption):
    res=[]
    global EnergyProd
    for i in range(0,len(EnergyProd)):
        if EnergyProd[i]>Consumption[i]:
            res.append(Consumption[i])
        else:
            res.append(EnergyProd[i])
    return res


def main(PVfilename,EVfilename,BVfilename,max):
    global EnergyProd
    ReadEnergyPV(PVfilename)
    ReadPmax(EVfilename,BVfilename,5,1)
    ReadEnergyEV(EVfilename,5)
    ReadEnergyBV(BVfilename,1)
    EnergyProd=diff(EPV)
    print(len(EPV),len(EnergyProd))
    N=len(ts)
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    xij=[]
    for i in range(0,N*Mev+N*Mbv):
        #xij.append(round(random.uniform(0,1), 2))
        xij=np.append(xij,0)
    b1 = [(0,1) for i in range(0,N*Mev)]
    b2 = [(-1,1) for i in range(0,N*Mbv)]
    bnds=b1+b2

    cons = ({'type': 'ineq','fun' : consCapEV},
            {'type': 'ineq','fun' : consEVdemand},
            {'type': 'ineq','fun' : consBVaccumulate},
            {'type': 'ineq','fun' : consBVaccumulate2})

    ft=1e-3

    res=minimize(function,xij,method='SLSQP',bounds=bnds,constraints=cons,options={'disp': True, 'ftol':ft})
    print(res)
    #for i in res.x:
       #print(i,end=',')
    xr=res.x[0:Mev*N]
    yr=res.x[Mev*N:]

    resfile=WriteRes(xr,yr,max,ft,Mev,N)
    CreateResults(resfile,max)



if __name__ == '__main__':
    main("2021-09-26_PVcumulativeenergy.csv","EVenergyandPmax.csv","BVenergyandPmax.csv",170)
'''
    ReadEnergyPV("2021-09-26_PVcumulativeenergy.csv")
    EnergyProd=diff(EPV)
    ReadPmax("EVenergyandPmax.csv","BVenergyandPmax.csv",5,0)
    ReadEnergyEV("EVenergyandPmax.csv",5)
    ReadEnergyBV("BVenergyandPmax.csv",0)
    CreateResults("XIJ_15-04-2022_11-19-34",170)
'''
