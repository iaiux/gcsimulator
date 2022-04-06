import csv

def PmaxCreator(Pmax,filename):

    with open("./csv/"+filename, 'w+', newline='') as outputcsv:
        writer=csv.writer(outputcsv)
        for p in Pmax:
            writer.writerow([p])



