import csv
from scipy.optimize import minimize
import numpy as np
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
    production=0
    for i in range(0,N):
        for j in range (0,Mbv):
            #somma=somma+(abs(deltat*(x[i+j]*PmaxEV[j])+(y[i+j]*PmaxBV[j])-EPV[i]))
            somma=somma+ (deltat*(x[i+j]*PmaxEV[j]+y[i+j]*PmaxBV[j]))
        production=sum(EPV)
    print(abs(somma-production))
    return abs(somma-production)

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

def ReadEnergyEV(EVenfilename):
    with open("../csv/"+EVenfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            CapsEV.append(float(riga[1]))
            EnInitEV.append(float(riga[3]))
            EVdemand.append(float(riga[4]))
    #print(CapsEV,EnInitEV,EVdemand)
def ReadEnergyBV(BVenfilename):
    with open("../csv/"+BVenfilename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader = csv.reader(inputcsv,delimiter=",")
        for riga in reader:
            CapsBV.append(float(riga[1]))
            EnInitBV.append(float(riga[3]))
            BVdemand.append(float(riga[4]))

def AdjustLen():
    while(len(PmaxEV)>len(PmaxBV)):
        PmaxBV.append(0)
        CapsBV.append(0)
        EnInitBV.append(0)
        BVdemand.append(0)

    while(len(PmaxBV)>len(PmaxEV)):
        PmaxEV.append(0)
        EnInitEV.append(0)
        EVdemand.append(0)
        CapsEV.append(0)

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
    for i in range(0,N):
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

def main(EVPmaxfilename,BVpmaxfilename,PVfilename,EVenfilename,BVenfilename):
    ReadEnergyPV(PVfilename)
    ReadPmax(EVPmaxfilename,BVpmaxfilename)
    AdjustLen()
    ReadEnergyEV(EVenfilename)
    ReadEnergyBV(BVenfilename)
    N=len(ts)-1
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
            {'type': 'ineq','fun' : consBVaccumulate2},)
    res=minimize(function,xij,method='SLSQP',bounds=bnds,constraints=cons, options={'maxiter': 1000, 'disp': True,})
    print(res.x)
    for i in res.x:
       print(i,end=' ')

if __name__ == '__main__':
    main("EVPmax.csv","BVPmax.csv","2021-09-26_PVenergy.csv","EVenergy.csv","BVenergy.csv")
