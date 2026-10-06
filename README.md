# Porto-Taxi-Trajectory
Exercise 2: Group project in TDT4225 Very Large, Distributed Data Volumes

### Duplicates 
To run the Duplicates.py, be sure to first use "Developer: Reload window" so that no stale or old data is showing up. 

#### What Duplicates.py does
1. Instead of working with the whole file at once, it is split into chuncks to make it easier to work with. 
2. To avoid damaging or changing the original data, the duplicated rows and the "cleand" data are moved into different csv files. 
3. 200 000 rows = 1 chunk
4. Every row is hashed into a number, acting sor of like a fingerprint. Identical rows therefor gets identical fingerprints. 
5. Duplicated rows are found when a fingerprint that was already seen is discorvered. 
6. The rows that are kept are those with "keep" = True, those that are removed and moved have "keep" = False. These are the duplicates. 
7. Several rows have the same TRIP_ID. TRIP_ID servers as a great possible key in the database, so to utilize this while also fixing the problem with the TRIP_ID, new IDs are distributed. They are given based on the counter (from 1 to 1710667, the last row after duplicate rows are removed)