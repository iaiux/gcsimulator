import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import interp1d
import matplotlib.dates as md
import datetime as dt
from datetime import datetime
import random
import time
import numpy as np


def substring_after(s, delim):
    return s.partition(delim)[2]

def ReadProfile(filepath):
    x=[]
    y=[]
    empty_lines=0
    filename=substring_after(filepath,"2021")
    filename="2021"+filename
    with open("../csv/"+filename, newline="", encoding="ISO-8859-1") as inputcsv:
        reader=csv.reader(inputcsv)
        for riga in reader:
            if not riga:
                empty_lines += 1
                continue
            x.append(riga[0])
            y.append(riga[1])
    #print(x,y)
    return x,y

def interp(x,y,filepath):
    dtime=[]
    tm=[]
    date=substring_after(filepath,"2021")
    date="2021"+date
    date=date[0:10]
    ts=time.mktime(dt.datetime.strptime(date, "%Y-%m-%d").timetuple())
    for i in x:
        tm.append(time.mktime(dt.datetime.strptime(i, "%Y-%m-%d %H:%M:%S").timetuple()))
    f=interp1d(tm, y,fill_value="extrapolate")
    timestamps=np.linspace(ts,ts+86400,24*4)
    ynew=f(timestamps)
    for i in timestamps:
        dtime.append(datetime.fromtimestamp(i))
    plt.subplots_adjust(bottom=0.2)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dtime,ynew)
    #plt.show()
    return timestamps,dtime,ynew

def main(filepath):
    x,y=ReadProfile(filepath)
    timestamps,date,PVenergy=interp(x,y,filepath)
    return timestamps,date,PVenergy

if __name__ == '__main__':
    timestamps,date,PVenergy=main("http://localhost/demo/12_12_15_145/2021-09-26-b734beb8-cd3a-4e19-a0b7-e9ef1d0e4275.csv")

