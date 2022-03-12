##################################
#           MINIMIZER            #
##################################


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

from deap import algorithms
from deap import base
from deap import benchmarks
from deap.benchmarks.tools import diversity, convergence
from deap import creator
from deap import tools
from geopy.distance import geodesic

filename = "values2.csv"
csv = np.genfromtxt("data/" + filename, delimiter=",")
print("Avvio algoritmo con: ", filename)
n_cars = int(csv[0, 1])  # legge il numero di EV
n_stations = int(csv[1, 1])  # legge il numero di CS

m_dist = zeros((n_cars, n_stations))  # crea la matrice delle distanze
average = n_cars / n_stations  # indica la media di macchine per stazione

filename = "ind_pos2.csv"
csv = np.genfromtxt("data/" + filename, delimiter=",")
print("Avvio algoritmo con: ", filename)
stations = np.zeros(n_stations)
# legge le posizioni di EV
lat_ecars = csv[:n_cars, 3]
long_ecars = csv[:n_cars, 4]
# legge le posizioni di CS
lat_stations = csv[:n_stations, 0]
long_stations = csv[:n_stations, 1]

creator.create("FitnessMax", base.Fitness, weights=(-1.0, -1.0,))  # minimizza entrambi gli obiettivi con -1 e -1
creator.create("Individual", list,
               fitness=creator.FitnessMax)  # crea l'oggetto l'individuo che ha come attributo la fitness
# crea la matrice delle distanze nella posizione i j c'è la distanza tra la EV i e la stazione j (in km)
for i in range(0, n_cars):
    for j in range(0, n_stations):
         m_dist[i][j] = geodesic((lat_ecars[i], long_ecars[i]), (lat_stations[j], long_stations[j])).km

toolbox = base.Toolbox()

# Attribute generator: define 'attr_bool' to be an attribute ('gene')
#                      which corresponds to integers sampled uniformly
#                      from the range [0,1] (i.e. 0 or 1 with equal
#                      probability)
toolbox.register("attr_bool", random.randint, 1, n_stations)  # crea una shortcut a randint e gli passa 1 e n_stations
# quindi fornisce un valore che va da 1 a n_stations
# in questo modo creo un individuo che va da 1 a n_station in maniera casuale cioè mi dice quella EV in che CS sarà situata
# Structure initializers: define 'individual' to be an individual
#consisting of n_cars 'attr_bool' elements ('genes')
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_bool, n_cars)  # crea shortcut initRepeat che chiama n volte la stessa funzione
# initRepeat gli passa Individual ovvero dove salvare il ris, la funzione
# da ripetere che è attr_bool (vedi sopra) e quante volte ripeterlo n_cars, perché deve
# creare un vettore di n_cars elementi, ogni elemento mi dice quella EV in che CS va

 # define the population to be a list of 'individual's
toolbox.register("population", tools.initRepeat, list,
                 toolbox.individual)  # creo shortcut a initRepeat che come sappiamo


# ripete Individual (cioè quello che crea l'array che mi dice ogni car in che CP va)
# e genera una lista di questi individui, una lista di array
# non ci metto quante volte li deve generare perché lo passo dopo come parametro variabile
# the goal ('fitness') function to be minimazed
# a questa funzione gli passo l'individuo (array di n_cars elementi)
# definisco distanza totale e la setto a 0
# definisco un vettore lungo quanto il numero di stazioni
# dico che la distanza totale è la somma delle distanze tra la EV i-esima e la CS di quella EV che
# si indica come individual[i] perché individual è il vettore che ha per ogni EV in che stazione si trova
# quindi accedo alla matrice delle distanze e di volta in volta mi prendo la distanza che mi serve
# e vado poi a sommare alla distanza totale
# alla fine incremento per ogni stazione il numero di auto che ci sono a caricare in tale stazione
def evalOneMax(individual):
    total_distance = 0
    stations = np.zeros(n_stations)
    for i in range(0, len(individual)):
        total_distance += m_dist[i][individual[i]]
        stations[individual[i]] += 1

    return total_distance, np.var(stations)  # var = mean(x), where x = abs(a - a.mean())^2

# ----------
# Operator registration
# ----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)  # registro la funzione fitness da minimizzae

# register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)  # registro il crossover

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutUniformInt, indpb=0.05)  # registro la mutazione

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of three individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selNSGA2)  # registro la selezione



'''
leggere e inizializzare tutte le info di macchine e stazioni
'''


def main(seed=None):

    random.seed(seed)

    NGEN = 1000
    MU = 100
    CXPB = 0.9

    stats = tools.Statistics(lambda ind: ind.fitness.values)  # crea valori utili per le statistiche
    stats.register("avg", numpy.mean, axis=0)  # crea valori utili per le statistiche (vedi stats.compile(pop))
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    pop = toolbox.population(n=MU)  # crea la popolazione (crea MU individui)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]  # prendo gli individui della popolazione
    # che sono invalidi ovvero che non hanno
    # nessun valore di fitness
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)  # faccio la valutazione di tutti gli individui
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    # record=stats.compile(pop) mi da un dict con tutte le info su media, dev standard, minimo e massimo di fitness
    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))  # effettuo una selezione dei pop individui, len(pop) è la lunghezza, in
    # realtà selezionare len(pop) individui significa prenderli di nuovo tutti

    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(invalid_ind),
                   **record)  # serve per creare un log di tutti i parametri piu importanti della generazione 0

    f = open('data/out_evolution.csv', 'w')  # apro file in scrittura per salvare dati
    # print >>f,logbook.stream

    # Begin the generational process
    for gen in range(1, NGEN):  # effettua NGEN volte le seguenti operazioni, fa queste cose per ogni generazione
        # Vary the population
        print("Generazione: ", gen, " - ", end="")
        offspring = tools.selTournamentDCD(pop,
                                           len(pop))  # effettua una selezione di tutti gli individui http://gpbib.cs.ucl.ac.uk/gecco2005/docs/p257.pdf
        offspring = [toolbox.clone(ind) for ind in
                     offspring]  # clona questi individui quindi fa una riproduzione (non cambia offspring)

        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):  # divide gli individui in due liste separate
            if random.random() <= CXPB:  # se il valore di un numero casuale è minore di 0,9 probabilità
                # assegnata al crossover, effettua il crossover tra gli individui

                toolbox.mate(ind1,
                             ind2)  # a partire da due genitori ind1 e ind2 mi produce due figli che sovrascrivono ind1 e ind2

            toolbox.mutate(ind1, 0, n_stations - 1)  # effettua una mutazione di ind1 ed ind2
            # ind1 diverrà ind1 mutato con valori dell'array
            # che saranno interi (mutUniformInt) da 0 a nstation-1
            # stessa cosa per ind2

            toolbox.mutate(ind2, 0, n_stations - 1)
            del ind1.fitness.values, ind2.fitness.values  # elimino le fitness per invalidare gli individui e ricalcolare le fitness

        # Evaluate the individuals with an invalid fitness
        # rivaluto sui nuovi individui la funzione obiettivo
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population
        pop = toolbox.select(pop + offspring, MU)  # a partire da vecchi individui e nuovi individui ne seleziona MU
        record = stats.compile(pop)  # crea le stats riguardanti media, dev std, min e max

        logbook.record(gen=gen, evals=len(invalid_ind), **record)  # per la generazione gen crea le stats
        print(gen, ",", record["min"][0], ",", record["min"][1],
              file=f)  # scrive la generazione nel file con i valori minimi delle f obiettivo
    f.close()
    return pop, logbook, NGEN, m_dist  # restituisce la popolazione, il logbook il numero di generazioni e la matrice delle distanze


if __name__ == "__main__":
    # with open("pareto_front/zdt1_front.json") as optimal_front_data:
    #    optimal_front = json.load(optimal_front_data)
    # Use 500 of the 1000 points in the json file
    # optimal_front = sorted(optimal_front[i] for i in range(0, len(optimal_front), 2))
    pop, stats, NGEN, m_dist = main()  # chiama il main
    pop.sort(key=lambda x: x.fitness.values)

    # print(stats)
    # print("Convergence: ", convergence(pop, optimal_front))
    # print("Diversity: ", diversity(pop, optimal_front[0], optimal_front[-1]))

    # print("\n")
    print("-- End of (successful) evolution --")
    best_ind1 = tools.selBest(pop, 1)[0]  # seleziona un individuo che ottimizza la prima f obiettivo
    best_ind2 = tools.selWorst(pop, 1)[0]  # seleziona un individuo che ottimizza la seconda f obiettivo
    print("Seleziono due individui:")
    print("Ind1:", best_ind1, "Fit1:", best_ind1.fitness.values[0], "Fit2: ", best_ind1.fitness.values[1])
    print("Ind2:", best_ind2, "Fit2:", best_ind2.fitness.values[0], "Fit2: ", best_ind2.fitness.values[1])

    f = open('data/out_pareto.csv', 'w')  # stampa nel file out_pareto i valori delle fitness di tutti gli individui
    # della popolazione finale che sono quelli che ottimizzano
    print("Scrivo gli individui che ottimizzano in data/out_pareto.csv")
    for ind in pop:
        print(ind.fitness.values[0], ",", ind.fitness.values[1], file=f)
    f.close()

    print("Scrivo ogni EV a che CS viene associata se scelgo il percorso con meno km in data/out_closest_path.csv")
    # print("Stazione preferita di ogni auto nel caso a minor distanza %s, %s" % (best_ind1, best_ind1.fitness.values))
    f = open('data/out_closest_path.csv',
             'w')  # stampa nel file out_closest_path la posizione dell'auto e la posizione della stazione
    # con minore distanza per ogni CS
    for i in range(0, len(best_ind1)):
        print(lat_ecars[i], ",", long_ecars[i], ",", lat_stations[best_ind1[i]], ",", long_stations[best_ind1[i]],
              file=f)
    f.close()
    print("Scrivo ogni EV a che CS viene associata se scelgo varianza bassa in data/out_variance_path.csv")
    # print("Stazione preferita da ogni auto nel caso a minor varianza %s, %s" % (best_ind2, best_ind2.fitness.values))
    f = open('data/out_variance_path.csv', 'w')  # stampa nel file out_variance_path la posizione dell'auto e
    # della stazione con varianza (tempo di attesa medio più basso possibile)
    for i in range(0, len(best_ind2)):
        print(lat_ecars[i], ",", long_ecars[i], ",", lat_stations[best_ind2[i]], ",", long_stations[best_ind2[i]],
              file=f)
    f.close()

    stations_closest = zeros(n_stations)  # crea due vettori di n_stations elementi
    stations_var = zeros(n_stations)

    for i in range(0, n_cars):
        stations_closest[best_ind1[i]] += 1  # carica questi due vettori inserendo quante auto in quale stazione
        stations_var[best_ind2[i]] += 1

    f = open('data/out_objectives.csv', 'w')
    print(best_ind1.fitness.values[0], best_ind1.fitness.values[1], np.var(stations_closest), file=f)
    print(best_ind2.fitness.values[0], best_ind2.fitness.values[1], np.var(stations_var), file=f)
    f.close()

    print("Salvo in data/out_inds.csv il file con due individui ottimi")
    f = open("data/out_inds.csv", "w")
    print(best_ind1, ",", best_ind1.fitness.values[0], ",", best_ind1.fitness.values[1], file=f)
    print(best_ind2, ",", best_ind2.fitness.values[0], ",", best_ind2.fitness.values[1], file=f)
    f.close()
