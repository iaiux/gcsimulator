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




def draw_convergence():
	csv = np.genfromtxt("data/out_evolution_mod.csv", delimiter=",")
	minx = csv[:, 0].min() #prende il minimo valore della prima f obiettivo
	maxx = csv[:, 0].max() #prende il max valore della prima f obiettivo
	miny = csv[:, 1].min() #prende il min valore della seconda f obiettivo
	maxy = csv[:, 1].max() #prende il max valore della seconda f obiettivo
	X, Y = np.mgrid[minx:maxx:0.01j, miny:maxy:0.01j]  # Row:all; Column:1


	fig0, ax0 = plt.subplots()
	ax0.set_xticks(np.arange(minx,maxx,1000))
	ax0.set_yticks(np.arange(miny, maxy, 20))
	plt.plot(csv[:, 0], csv[:, 1], label='distance')

	xy= (csv[3, 1], csv[3, 2])  # <--
	ax0.annotate('(%s, %s)' % xy, xy=xy, textcoords='data')

	xy = (csv[-3, 1], csv[-3, 2])  # <--
	ax0.annotate('(%s, %s)' % xy, xy=xy, textcoords='data')

	plt.xlabel('evolution')
	plt.ylabel('distance')
	plt.grid()
	plt.show()

def draw_pareto(filename,outputname):

	csv = np.genfromtxt("data/"+filename, delimiter=",")
	minx = csv[:, 0].min()
	maxx = csv[:, 0].max()
	miny = csv[:, 1].min()
	maxy = csv[:, 1].max()

	X, Y = np.mgrid[minx:maxx:0.01j, miny:maxy:0.01j] #Row:all; Column:1




	fig0, ax0 = plt.subplots()

	plt.scatter(csv[:,0],csv[:,1])
	plt.xlabel('distance')
	plt.ylabel('variance')
	fig0.savefig("figures/"+outputname)
	print("Produco il plot delle soluzioni in figures: ", outputname)



