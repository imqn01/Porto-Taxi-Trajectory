import pandas as pd

df = pd.read_csv('porto/porto.csv')

#convert TIMESTAMP to a standard datetime format
df['TIMESTAMPp'] = pd.to_datetime(df['TIMESTAMP'], unit='s')
print(df[['TIMESTAMP', 'TIMESTAMPp']].head())