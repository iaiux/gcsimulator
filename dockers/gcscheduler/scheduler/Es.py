import os
import sys
import time
import array
import random
import json
import numpy
import numpy as np
from numpy import *
from math import acos
from math import sin
from math import cos
import datetime

from math import sqrt
from deap import *
from deap import algorithms
from deap import base
from deap import benchmarks
from deap.benchmarks.tools import diversity, convergence
from deap import creator
from deap import tools
from geopy.distance import geodesic

csv = np.genfromtxt("data/values.csv", delimiter=",")
n_cars = int(csv[0, 1])#legge il numero di EV
n_stations = int(csv[1, 1]) #legge il numero di CS
csv = np.genfromtxt("data/ind_pos2.csv", delimiter=",")
stations = np.zeros(n_stations)
#legge le posizioni di EV
lat_ecars = csv[:3,3]
long_ecars  = csv[:3,4]
lat_stations =  csv[:n_stations,0]
long_stations = csv[:n_stations,1]
m_dist = zeros((n_cars, n_stations))

creator.create("FitnessMax", base.Fitness, weights=(-1.0, -1.0,)) #minimizza entrambi gli obiettivi con -1 e -1
creator.create("Individual", list, fitness=creator.FitnessMax) #crea l'oggetto l'individuo che ha come attrib
for i in range(0, n_cars):
    for j in range(0, n_stations):
        #m_dist[i][j] =  distance_cim((lat_ecars[i],long_ecars[i]),(lat_stations[j],long_stations[j]))
        m_dist[i][j] = geodesic((lat_ecars[i],long_ecars[i]), (lat_stations[j],long_stations[j])).km      
#print(m_dist)

toolbox = base.Toolbox()
toolbox.register("attr_bool", random.randint, 1, n_stations)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_bool, n_cars)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#print(toolbox.population(10))

toolbox.register("mate", tools.cxTwoPoint) #registro il crossover
toolbox.register("mutate", tools.mutUniformInt,indpb=0.05) #registro la mutazione
toolbox.register("select", tools.selNSGA2) #registro la selezione


def evalOneMax(individual):
    total_distance = 0
    stations = np.zeros(n_stations)
    for i in range(0, len(individual)):
        total_distance += m_dist[i][individual[i]]
        stations[individual[i]] += 1

    #print(stations)	
    return total_distance,  np.var(stations)



def main(seed=None):
	random.seed(seed)
	NGEN = 100
	MU =8
	CXPB = 0.9
	stats = tools.Statistics(lambda ind: ind.fitness.values) #crea valori utili per le statistiche
	stats.register("avg", numpy.mean, axis=0) #crea valori utili per le statistiche approfondire
	stats.register("std", numpy.std, axis=0)
	stats.register("min", numpy.min, axis=0)
	stats.register("max", numpy.max, axis=0)

	logbook = tools.Logbook()
	logbook.header = "gen", "evals", "std", "min", "avg", "max"
	
	
	pop = toolbox.population(n=MU)
	    
	toolbox.register("evaluate", evalOneMax)
	
	invalid_ind = [ind for ind in pop if not ind.fitness.valid] #prendo gli individui della popolazione
                                                                #che sono invalidi ovvero che non hanno
                                                                #nessun valore di fitness
	fitnesses = toolbox.map(toolbox.evaluate, invalid_ind) #faccio la valutazione di tutti gli individui
	for ind, fit in zip(invalid_ind, fitnesses):
		ind.fitness.values = fit
		print(ind,fit)
		
	pop = toolbox.select(pop, MU)
	record = stats.compile(pop)
	logbook.record(gen=0, evals=len(invalid_ind), **record)
	#print(logbook.stream)	
	f = open('data/out_evolution.csv', 'w')
	for gen in range(1, NGEN):
        # Vary the population
		offspring = tools.selTournamentDCD(pop, len(pop))
		offspring = [toolbox.clone(ind) for ind in offspring]
		#print(offspring)
		#print(offspring[::2])
		#print(offspring[1::2])
		for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
			#print("Individui senza crossover:")
			#print(ind1,ind2)
			if random.random()<=CXPB:
				toolbox.mate(ind1, ind2)
				#print("Individui con crossover:")
				#print(ind1,ind2)
			
			toolbox.mutate(ind1,0,n_stations-1) 
			toolbox.mutate(ind2,0,n_stations-1)
			#print("Individui mutati:")
			#print(ind1,ind2, ind1.fitness.values,ind2.fitness.values)
			del ind1.fitness.values, ind2.fitness.values
			
		invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
		fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
		for ind, fit in zip(invalid_ind, fitnesses):
			ind.fitness.values = fit
		print(pop+offspring)    
		pop = toolbox.select(pop + offspring, MU)
		print(pop)
		record = stats.compile(pop)
		logbook.record(gen=gen, evals=len(invalid_ind), **record)
		print (gen,record["min"][0],",",record["min"][1]) #scrive la generazione nel file con i valori minimi delle f obiettivo
		f.close()
		pop.sort(key=lambda x: x.fitness.values)
		for ind in pop:
			print(ind, ind.fitness.values)
	return pop, logbook, NGEN, m_dist 


if __name__ == "__main__":
	
	
	pop, stats, NGEN, m_dist = main()
	pop.sort(key=lambda x: x.fitness.values)
	
	best_ind1 = tools.selBest(pop, 1)[0]
	best_ind2 = tools.selWorst(pop, 1)[0]
    
    
	print(best_ind1,best_ind2)
	
	
	stations_closest = zeros(n_stations) #crea due vettori di n_stations elementi
	stations_var = zeros(n_stations)

	for i in range(0, n_cars):
		stations_closest[best_ind1[i]] += 1 #carica questi due vettori inserendo quante auto in quale stazione
		stations_var[best_ind2[i]] += 1
	print(stations_closest,stations_var)
