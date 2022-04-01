import csv
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
import matplotlib.dates as md
import datetime as dt
from datetime import datetime as date
import time
import numpy as np

def ReadProduction(filename):
    x=[]
    y=[]
    with open("../csv/"+filename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader=csv.reader(inputcsv)
        for riga in reader:
            x.append(riga[0])
            y.append(float(riga[2]))
    return  x,y

def SingleDraw(ts,Values,lab):
    dtime=[]
    for i in ts:
        dtime.append(date.fromtimestamp(int(float(i))))
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dtime,Values,label=lab)
    #plt.xlabel("TEST")
    plt.legend()

    plt.show()


if __name__ == '__main__':
    ts,y=ReadProduction("2021-09-25_PVenergy.csv")
