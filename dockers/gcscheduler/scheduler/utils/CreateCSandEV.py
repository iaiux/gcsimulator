from geopy.distance import geodesic
import random
import csv



def main():
	N_stations=0
	N_cars=0
	print("Creo ind_distance_opendata e values_opendata")
	with open("./csv/national-charge-point-registry.csv", newline="", encoding="ISO-8859-1") as inputcsv:
		reader = csv.reader(inputcsv,delimiter=",")
		header = next(reader)
		with open("./data/ind_distance_opendata.csv", 'w+', newline='') as outputcsv:
			writer = csv.writer(outputcsv)
			for riga in reader:
				if(N_stations<200):
					N_stations=N_stations+1
					N_cars=N_cars+1
					#print(riga[3],riga[4])
					latEV=float(riga[3])+round(random.uniform(-0.20, 0.20), 9)
					longEV=float(riga[4])+round(random.uniform(-0.20, 0.20), 9)
					writer.writerow([str(riga[3]),str(riga[4]), 0, str(latEV), str(longEV)])
	with open("./csv/national-charge-point-registry.csv", newline="", encoding="ISO-8859-1") as inputcsv:
		reader = csv.reader(inputcsv,delimiter=",")
		header = next(reader)
		with open("./data/ind_distance_opendata.csv", 'a', newline='') as outputcsv:
			writer = csv.writer(outputcsv)
			for riga in reader:
				if (N_cars<350):
					N_cars=N_cars+1
					print(riga[3],riga[4])
					latEV=float(riga[3])+round(random.uniform(-0.20, 0.20), 9)
					longEV=float(riga[4])+round(random.uniform(-0.20, 0.20), 9)
					writer.writerow([0,0,0, str(latEV), str(longEV)])
	with open("./data/values_opendata.csv", 'w+', newline='') as outputcsv:
		writer = csv.writer(outputcsv)
		writer.writerow(["NCARS:",N_cars])
		writer.writerow(["NSTATIONS:", N_stations])
