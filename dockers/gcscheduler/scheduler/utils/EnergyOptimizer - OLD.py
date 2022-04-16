import csv
import datetime
import os

from matplotlib import pyplot as plt
from numpy import diff
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

def function(x):
    deltat=float((float(ts[1])-float(ts[0])))
    Mev=len(PmaxEV)
    Mbv=len(PmaxBV)
    N=len(ts)-1
    y=[]
    y=x[N*Mev:]
    x=x[:N*Mev]
    somma=0
    for i in range(0, N-1):
        temp=0
        for j in range (0,Mev):
            temp=temp+ deltat*(x[i+j]*PmaxEV[j])
        for j in range (0,Mbv):
            temp=temp+ deltat * (y[i+j]*PmaxBV[j])
        if i==0:
            temp = temp/3600-EPV[i]
        else:
            temp = temp / 3600 - (EPV[i]-EPV[i-1])
        somma =somma+abs(temp)
    print("Evaluating function: " ,somma)

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
    deltat=float((float(ts[1])-float(ts[0]))/3600)
    cons=0
    N=len(ts)-1
    Mev=len(PmaxEV)
    Capstot=0
    temp=0
    y=[]
    y=x[:N*Mev]
    for k in range(0,N+1):
        for i in range(0,k): #for i in range(0,N)
            for j in range(0,Mev):
                cons=cons+ (deltat*y[i+j]*PmaxEV[j])
        for j in range(0,Mev):
            Capstot=Capstot+CapsEV[j]
            temp=temp+EnInitEV[j]

    return -cons-temp+Capstot
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
    for k in range(0,N+1):
        for i in range(0,k): #for i in range(0,N):
            for j in range(0,Mbv):
             cons=cons+ (deltat*y[i+j]*PmaxBV[j])
    for j in range(0,Mbv):
            BVStart=BVStart+EnInitBV[j]
            BVCap=BVCap+ CapsBV[j]
    return -cons-BVStart+BVCap


def Deriva(x, y):
    x = np.array(x)
    y= np.array(y)
    dy=diff(y)/diff(x)
    return dy


def WriteRes(xr, yr,max,ft):
    today = date.today()
    d1 = today.strftime("%d-%m-%Y")
    #now = datetime.now()+timedelta(hours=2)
    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")
    date_today = d1 + "_" + current_time

    with open("../csv/output/XIJ_"+date_today+".csv","w+",newline='')as file:
        writer=csv.writer(file)
        writer.writerow([max,ft])
        for x in xr:
            writer.writerow([x])
        for y in yr:
            writer.writerow([y])
    return "XIJ_"+date_today

def CreateResults(resfile,num):
    ts1=[]
    for t in ts:
        ts1.append(float(t)/3600)
    xnew,ynew=ReadRes(resfile)
    Consumption=CalculateConsumption(xnew,ynew)
    PowerProduction=Deriva(ts1,EPV)
    PowerConsumption=Deriva(ts1,Consumption)
    PlotGraph.TripleDraw(ts[:-1],PowerProduction,PowerConsumption,Consumption,"PowerProduction","PowerConsumption","Consumption","kW","kWh","Power and Consumption Plot")
    PlotGraph.SingleDraw(ts[:-1],PowerProduction,"PowerProduction","kW","Power Production Plot")
    PlotGraph.SingleDraw(ts[:-1],PowerConsumption,"PowerConsumption","kW", "Power Consumption Plot")
    PlotGraph.DoubleDraw(ts[:-1],PowerProduction,"PowerProduction",PowerConsumption,"PowerConsumption","kW","Power Plot")
    PlotGraph.SingleDraw(ts,EPV,"Production","kWh","Energy Production Plot")
    PlotGraph.SingleDraw(ts,Consumption,"Consumption","kWh","Energy Consumption Plot")
    PlotGraph.DoubleDraw(ts,EPV,"Production",Consumption,"Consumption","kWh", "Energy Production and Consmuption Plot")
    PVEnergyCons=calculateEnergyConPV(Consumption,EPV)
    PVPowerCons=Deriva(ts1,PVEnergyCons)
    #PlotGraph.DoubleDrawFill(ts[:-1],PowerProduction,"Power Production",PVPowerCons,"PV Power Consumption","kW","Power Consumed from PV")
    PlotGraph.TripleDrawEnergies(ts,EPV,Consumption,PVEnergyCons,"Energy Production","Energy Consumption","Consumption from PV","kWh","kWh","Energy Plot")
    SelfC=sum(PVEnergyCons)/sum(EPV)
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
            if i<=N*Mev:
                xij.append(float(riga[0]))
            else:
                yij.append(float(riga[0]))
            i=i+1
    return xij,yij

def calculateEnergyConPV(Consumption,EPV):
    res=[]
    for i in range(0,len(EPV)):
        if EPV[i]>=Consumption[i]:
            res.append(Consumption[i])
        else:
            res.append(EPV[i])
    return res


def main(PVfilename,EVfilename,BVfilename,max):
    ReadEnergyPV(PVfilename)
    ReadPmax(EVfilename,BVfilename,1,1)
    ReadEnergyEV(EVfilename,1)
    ReadEnergyBV(BVfilename,1)
    N=len(ts)-1
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
    res=minimize(function,xij,method='SLSQP',bounds=bnds,constraints=cons,options={'disp': True, 'maxiter': max, 'ftol':ft})
    print(res)
    #for i in res.x:
       #print(i,end=',')
    xr=res.x[0:Mev*N]
    yr=res.x[Mev*N:]
    resfile=WriteRes(xr,yr,max,ft)
    CreateResults(resfile,max)



if __name__ == '__main__':
    main("2021-09-26_PVenergy.csv","EVenergyandPmax.csv","BVenergyandPmax.csv",170)
    '''
    ReadEnergyPV("2021-09-25_PVenergy.csv")
    ReadPmax("EVenergyandPmax.csv","BVenergyandPmax.csv")
    ReadEnergyEV("EVenergyandPmax.csv")
    ReadEnergyBV("BVenergyandPmax.csv")
    CreateResults("XIJ_09-04-2022_16-14-24",30)
    '''
