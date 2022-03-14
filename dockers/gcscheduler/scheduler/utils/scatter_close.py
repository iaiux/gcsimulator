"""
Demo of the `streamplot` function.

A streamplot, or streamline plot, is used to display 2D vector fields. This
example shows a few features of the stream plot function:

    * Varying the color along a streamline.
    * Varying the density of streamlines.
    * Varying the line width along a stream line.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib.pyplot import cm
import math
from geopy.distance import geodesic


#This file containes in first 2 column position of station (76 rows).
#In 3,4 colums initial car position (300 rows).
def main():
	csv = np.genfromtxt("./data/out_closest_path.csv", delimiter=",")


	n_cars =len(csv[:,2])

	stations_lat = np.zeros(n_cars )
	stations_long = np.zeros(n_cars )

	n_stations = 0
	for i in range(0,n_cars):
		found = 0
		k = 0
		while k<n_stations and not found:
			if csv[i][2] == stations_lat[k] and csv[i][3] == stations_long[k]:
				found = 1
			k +=1

		if found == 0:
			stations_lat[n_stations] = csv[i][2]
			stations_long[n_stations] = csv[i][3]
			n_stations += 1

	stations_lat =stations_lat[:n_stations]
	stations_long = stations_long[:n_stations]
	stations = np.zeros(n_stations)


	C = np.zeros(len(csv[:,2])) #C[i] tells the closest station to car i
	U=np.zeros(len(csv[:,2]))
	V=np.zeros(len(csv[:,2]))
	D = np.zeros(len(csv[:,2])) #distance covered by car i

	total_distance = 0
	for i in range(0,len(csv[:,2])):
		#minimum distance between i-car and its final destination
		start = (csv[i][0], csv[i][1])
		end = (stations_lat[0], stations_long[0])
		dmin= geodesic(start, end).km
		U[i] = end[0] - start[0]
		V[i] = end[1] - start[1]
		C[i]= 0

		#find the minimum distance between i-car and each station
		for j in range(1,n_stations):
			end = (stations_lat[j], stations_long[j])
			d= geodesic(start, end).km

			if d<dmin:
				C[i]= j
				U[i]=end[0]-start[0] #This is the y distance between start and destination of car i
				V[i]=end[1]-start[1] #This is the y distance between start and destination of car i
				dmin=d
		D[i] = dmin
		total_distance +=D[i]
		#station j is also chosen by car i
		stations[int(C[i])]=stations[int(C[i])]+1



	'''
	print C[:temp]
	print csv[:temp, 2]
	print csv[:temp, 3]
	print U[:temp]
	print V[:temp]
	'''

	minx = csv[:, 0].min()
	maxx = csv[:, 0].max()
	miny = csv[:, 1].min()
	maxy = csv[:, 1].max()
	X, Y = np.mgrid[minx:maxx:0.01j, miny:maxy:0.01j] #Row:all; Column:1



	colors = stations
	fig0, ax0 = plt.subplots()

	strm = ax0.quiver(csv[:, 0], csv[:, 1],U,V,D,scale_units='xy', angles='xy', scale=1)
	sc=ax0.scatter(csv[:, 0],csv[:, 1])
	sc=ax0.scatter(stations_lat,stations_long,s=stations*50,c=colors,alpha=0.5)

	cb1=plt.colorbar(sc)
	cb2=plt.colorbar(strm)
	plt.xlabel('longitude')
	plt.ylabel('latitude')
	cb1.set_label('#of ecars per station')
	cb2.set_label('covered distance')

	'''
	strm = ax0.quiver(csv[:, 0], csv[:, 1],U,V ,color=speed,
				   cmap=cm.cool,        # colour map
				   headlength=7)
	#fig0.colorbar(cm.cool)
	#strm = ax0.streamplot(X, Y,  U,V,color=U, linewidth=2, cmap=plt.cm.autumn)
	#fig0.colorbar(strm.lines)

	fig1, (ax1, ax2) = plt.subplots(ncols=2)
	ax1.streamplot(X, Y, csv[:, 2], csv[:, 2], density=[0.5, 1])

	lw = 5*speed / speed.max()
	ax2.streamplot(X, Y, csv[:, 2], csv[:, 2], density=0.6, color='k', linewidth=lw)
	'''


	print ("total distance:",total_distance,",",np.var(D),",",np.average(D),",",np.min(D),",",np.max(D))
	print ("e-cars:,",np.var(stations),",",np.average(stations),",",np.min(stations),",",np.max(stations))
	fig0.savefig("./figures/closest_opt.png")

	return D,stations


