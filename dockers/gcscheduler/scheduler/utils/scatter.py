"""
Demo of the `streamplot` function.

A streamplot, or streamline plot, is used to display 2D vector fields. This
example shows a few features of the stream plot function:

    * Varying the color along a streamline.
    * Varying the density of streamlines.
    * Varying the line width along a stream line.
"""

from geopy.distance import geodesic
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib.pyplot import cm


from  math import acos,sin,cos
import random
import utils.scatter_close


def scatter_random(file1,file2,prob):
	csv = np.genfromtxt(file1, delimiter=",")
	csv2 = np.genfromtxt(file2, delimiter=",")
	random.seed(None)
	distance = np.zeros(len(csv))
	stations_lat = np.zeros(len(csv))
	stations_long = np.zeros(len(csv))
	stations = np.zeros(len(csv))
	n_stations = 0
	for i in range(0,len(csv)):
		start = (csv[i][0], csv[i][1])
		if random.random()<prob:
			end = (csv[i][2], csv[i][3])
		else:
			end = (csv2[i][2], csv[i][3])
		distance[i]=geodesic(start, end).km
		found = 0
		k = 0
		while k < n_stations and not found:
			if end[0] == stations_lat[k] and end[1] == stations_long[k]:
				found = 1
				stations[k] += 1
			else:
				k += 1

		if found == 0:
			stations_lat[n_stations] = csv[i][2]
			stations_long[n_stations] = csv[i][3]
			stations[n_stations]=1
			n_stations += 1



	return distance,stations[:n_stations]



def draw_scatter(filename, n_stations,figname,distvar,case):

	csv = np.genfromtxt(filename, delimiter=",")
	minx = csv[:,0].min()
	maxx = csv[:,0].max()
	miny = csv[:,1].min()
	maxy = csv[:,1].max()

	X, Y = np.mgrid[minx:maxx:0.01j, miny:maxy:0.01j] #Row:all; Column:1

	U= csv[:,2]-csv[:,0]
	V= csv[:,3]-csv[:,1]

	distance =np.zeros(len(U));
	total_distance = 0


	for i in range(0,len(U)):
		start = (csv[i][0], csv[i][1])
		end = (csv[i][2], csv[i][3])
		distance[i] = geodesic(start, end).km


		total_distance += distance[i]



	fig0, ax0 = plt.subplots()

	strm = ax0.quiver(csv[:, 0], csv[:, 1],U,V,distance,scale_units='xy', angles='xy', scale=1)
	ax0.scatter(csv[:,0],csv[:,1])


	plt.xlabel('longitude')
	plt.ylabel('latitude')
	cb1=plt.colorbar(strm)
	cb1.set_label('covered distance')

	car2stations = np.genfromtxt("./data/out_car2stations_"+case+".csv", delimiter=",")
	stations = np.genfromtxt("./data/ind_distance_"+case+".csv", delimiter=",")
	sc2 = ax0.scatter(stations[:n_stations, 0], stations[:n_stations, 1], s=car2stations[:n_stations,distvar] * 50, c=car2stations[:n_stations,distvar],
					  alpha=0.5)
	cb2=plt.colorbar(sc2)
	cb2.set_label('#of ecars per station')



	D = distance

	fig0.savefig(figname)
	stations = csv[:n_stations, 2]
	print ("total distance:",total_distance,",",np.var(D),",",np.average(D),",",np.min(D),",",np.max(D))
	print ("e-cars:,",np.var(car2stations[:n_stations,distvar]),",",np.average(car2stations[:n_stations,distvar]),",",np.min(car2stations[:n_stations,distvar]),",",np.max(car2stations[:n_stations,distvar]))


	return  distance,car2stations[:n_stations,distvar]




def main(n_stations,case):


	distance1,ec2st1 = draw_scatter("./data/out_closest_path_"+case+".csv",n_stations,"./figures/closest_ga_"+case+".png",0,case)
	distance2, ec2st2 =  draw_scatter("./data/out_variance_path_"+case+".csv",n_stations,"./figures/variance_ga_"+case+".png",1,case)
	distance3, ec2st3 = utils.scatter_close.main(case)
	distance4,ec2st4 = scatter_random("./data/out_closest_path_"+case+".csv", "./data/out_variance_path_"+case+".csv", 0.6)
	print (np.var(ec2st4),",vvvv,",np.sum(distance4))

	min =0;
	max =30

	f = open("./data/out_propabilityst_"+case+".csv","w")
	for i in range(0,max):
		prob1 = np.zeros(max)
		for j in range(0,len(ec2st1)):
			prob1[int(ec2st1[j])] += 1
		prob2 = np.zeros(max)
		for j in range(0, len(ec2st2)):
			prob2[int(ec2st2[j])] += 1
		prob3 = np.zeros(max)
		for j in range(0, len(ec2st3)):
			prob3[int(ec2st3[j])] += 1
		prob4 = np.zeros(max)
		for j in range(0, len(ec2st4)):
			prob4[int(ec2st4[j])] += 1


		prob1=prob1/sum(prob1)
		prob2 = prob2 / sum(prob2)
		prob3 = prob3 / sum(prob3)
		prob4 = prob4 / sum(prob4)
		print (i,",",prob1[i],",",prob2[i],",",prob3[i],",",prob4[i],file=f)
	f.close()







	fig0, (ax0, ax1) = plt.subplots(ncols=2)
	ax0.boxplot([distance3, distance1,distance2,distance4], ["closest","distance", "variance","choice"])
	ax1.boxplot([ec2st3,ec2st1,ec2st2,ec2st4], ["closest","distance", "variance","choice"])
	ax0.set_title('Box Plot')
	ax0.set_ylabel('Distance of ecar from station')
	ax1.set_title('Box Plot')
	ax1.set_ylabel('#of ecars per station')
	ax0.set_xlabel('closest,distance, variance, Choice')
	ax1.set_xlabel('closest,distance, variance, Choice')
	fig0.savefig("./figures/boxplots_"+case+".png")


