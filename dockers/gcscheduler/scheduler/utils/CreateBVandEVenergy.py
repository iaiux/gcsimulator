import csv

def SoCCapsEVCreator(CapsEV,EVid1,SoCsEV,EVid2,filename):
    x_s,y_s=map(list,zip(*sorted(zip(EVid1,CapsEV)))) #ordina le due liste in modo che abbiano
    a_s, b_s= map(list, zip(*sorted(zip(EVid2, SoCsEV))))#gli id in ordine numerico crescente e
                                                        #le Capacità e le SoC associate.
    with open("../csv/"+filename, 'w+', newline='') as outputcsv:
        writer=csv.writer(outputcsv)
        for id,cap,soc in zip(x_s,y_s,b_s):
            writer.writerow([id, cap,soc,cap*soc,cap-(cap*soc)]) #cap*soc è l'energia ancora nella EV
                                                                #cap-(cap*soc) è l'energia richiesta
def BVeneryCreator(BVid,CapsBV,SoCsBV,filename):
    with open("../csv/"+filename, 'w+', newline='') as outputcsv:
        writer=csv.writer(outputcsv)
        for id,cap,soc in zip(BVid,CapsBV,SoCsBV):
            writer.writerow([id, cap,soc,cap*soc,cap-(cap*soc)])


if __name__ == '__main__':
    SoCCapsEVCreator([10.5, 31.5, 75.0, 52.0, 52.0],
                    ['[99]:[292]', '[99]:[293]', '[99]:[299]', '[99]:[302]', '[99]:[303]'],
                    [0.12,0.5,0.5,0.5,0.5],['[99]:[292]', '[99]:[299]', '[99]:[302]', '[99]:[303]', '[99]:[293]'],"EVenergy.csv")
    BVeneryCreator(['[99]:[18]:[3]', '[99]:[18]:[4]', '[99]:[18]:[6]', '[99]:[18]:[7]', '[99]:[19]:[2]', '[99]:[19]:[5]'],
                   [27.0, 27.0, 27.0, 27.0, 100.0, 100.0],[0.12,0.5,0.5,0.5,0.5,0.7],"BVenergy.csv")
