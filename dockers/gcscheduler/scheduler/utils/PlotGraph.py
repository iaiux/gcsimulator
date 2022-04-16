import csv
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
import matplotlib.dates as md
import datetime as dt
from datetime import datetime as datx
from datetime import timedelta
import time
import numpy as np

def name_of_file():
    today = datx.today()
    d1 = today.strftime("%d-%m-%Y")
    #now = dt.datetime.now()+timedelta(hours=2)
    now = dt.datetime.now()
    current_time = now.strftime("%H-%M-%S")
    date_today = d1 + "_" + current_time
    return date_today

def ReadProduction(filename):
    x=[]
    y=[]
    with open("../csv/"+filename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader=csv.reader(inputcsv)
        for riga in reader:
            x.append(riga[0])
            y.append(float(riga[2]))
    return  x,y

def SingleDraw(ts,Values,lab,ylab,tit):
    plt.figure()
    dtime=[]
    for i in ts:
        dtime.append(datx.fromtimestamp(int(float(i))))
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dtime,Values,label=lab)
    plt.title(tit)
    plt.ylabel(ylab)
    plt.legend()
    filename=name_of_file()
    plt.savefig("../csv/output/figures/"+filename+"_"+tit+".png")
    #plt.show()
def DoubleDrawFill(ts,y1,label1,y2,label2,ylab,tit):
    plt.figure()
    dtime=[]
    for i in ts:
        dtime.append(datx.fromtimestamp(int(float(i))))
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    labels = [label1,label2]
    plt.plot(dtime,y1)
    plt.plot(dtime,y2)
    plt.title(tit)
    plt.ylabel(ylab)
    plt.legend(labels)
    plt.fill_between(dtime,y1,y2,color="green",label='Self-Consumption')
    filename=name_of_file()
    plt.savefig("./csv/output/figures/"+filename+"_"+tit+".png")

def DoubleDraw(ts,y1,label1,y2,label2,ylab,tit):
    plt.figure()
    dtime=[]
    for i in ts:
        dtime.append(datx.fromtimestamp(int(float(i))))
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    labels = [label1,label2]
    plt.plot(dtime,y1)
    plt.plot(dtime,y2)
    plt.title(tit)
    plt.ylabel(ylab)
    plt.legend(labels)
    filename=name_of_file()
    plt.savefig("../csv/output/figures/"+filename+"_"+tit+".png")

def TripleDraw(x,y1,y2,bar3,label1,label2,label3,ylab1,ylab2,tit):
    dtime=[]
    for i in x:
        dtime.append(datx.fromtimestamp(int(float(i))))
    plt.figure()
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    labels = [label1,label2]
    plt.plot(dtime,y1,label=label1)
    plt.plot(dtime,y2,label=label2)
    plt.legend(loc="lower right")
    ax2 = ax.twinx()
    ax.set_ylabel(ylab1)
    ax2.set_ylabel(ylab2)
    # plot bar chart on axis #2
    plt.title(tit)
    ax2.bar(dtime, bar3[:-1], width=0.01, alpha=0.5, color='orange',label=label3)
    ax2.grid(False) # turn off grid #2
    plt.legend(loc="upper left")
    filename=name_of_file()
    plt.savefig("../csv/output/figures/"+filename+"_"+tit+".png")

def TripleDrawEnergies(x,y1,y2,bar3,label1,label2,label3,ylab1,ylab2,tit):
    dtime=[]
    for i in x:
        dtime.append(datx.fromtimestamp(int(float(i))))
    plt.figure()
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    labels = [label1,label2]
    plt.plot(dtime,y1,label=label1)
    plt.plot(dtime,y2,label=label2)
    plt.legend(loc="lower right")
    ax2 = ax.twinx()
    ax.set_ylabel(ylab1)
    ax2.set_ylabel(ylab2)
    # plot bar chart on axis #2
    plt.title(tit)
    ax2.bar(dtime, bar3, width=0.01, alpha=0.5, color='orange',label=label3)
    ax2.grid(False) # turn off grid #2
    plt.legend(loc="upper left")
    filename=name_of_file()
    plt.savefig("../csv/output/figures/"+filename+"_"+tit+".png")

'''
if __name__ == '__main__':
    ts,y=ReadProduction("2021-09-25_PVenergy.csv")
'''
