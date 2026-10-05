#Identify duplicate values 
#Idetnify duplicate rows
#Remove duplicate rows
#New indexes to remove duplicated TRIP_IDs

import pandas as pd

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

