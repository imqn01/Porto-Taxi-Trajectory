#Identify duplicate values 
#Idetnify duplicate rows
#Remove duplicate rows
#New indexes to remove duplicated TRIP_IDs

import pandas as pd
from collections import Counter

Source_data = "data/prto.csv"
Output_data = "data/porto_no_duplicates"

#Lese gjennom fil chunk for chunk for å spare minne
#Lager oversikt over hvilken som er sett for å fikse ulempe med at to like rader ikke er i samme chunk
#Lager en ny fil med resultatene slik at orginal dataen aldri endres


#Duplicatd IDs 
ids = pd.read_csv("data/porto.csv", usecols=["TRIP_ID"])
dupes = ids["TRIP_ID"].duplicated().sum()
print(f"Amount of reused TRIP_IDs{dupes}")
#Duplicated row
df = pd.read_csv("data/porto.csv")
if (df.duplicated().sum() == 0):
    print("No duplicated rows")
else: 
    newdf = df.drop_duplicates() #Removes duplicated rows from the dataset wihtout modifying the origional datafile. 
    #print(f"Duplicated rows:{df[df.duplicated()]}")
    #print(f"HEI{newdf[newdf.duplicated()]}")

