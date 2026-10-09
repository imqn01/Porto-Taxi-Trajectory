import json
import pandas as pd

df = pd.read_csv('porto/porto.csv')

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

def count_points(polyline):
  if not isinstance(polyline, str):
    return 0
  try:
    data = json.loads(polyline)
    return len(data) if isinstance(data, list) else 0
  except json.JSONDecodeError:
    return 0

print(f'The dataset has {df.shape[0]} rows and {df.shape[1]} columns')
print('Number of missing values for each column:\n', df.isna().sum())
print('\nData types for each column:\n', df.dtypes)
print(df.head())

print(df['CALL_TYPE'].value_counts(dropna=False)) 
print(df['DAY_TYPE'].value_counts(dropna=False))

print(df['ORIGIN_CALL'].nunique())
print(df['ORIGIN_CALL'].value_counts(dropna=False))
print(df['ORIGIN_STAND'].nunique())
print(df['ORIGIN_STAND'].value_counts(dropna=False))

# checks if original call and origin stand are set correctly
#ORIGIN_CALL: ID of the client who initiated the call (only set when CALL_TYPE = ‘A’). Otherwise NULL
print(f"Number of rows with ORIGIN_CALL set but CALL_TYPE is not 'A': {(df['ORIGIN_CALL'].notna() & (df['CALL_TYPE'] != 'A')).sum()}")
print(f"Number of rows with ORIGIN_CALL not set but CALL_TYPE is 'A': {(df['ORIGIN_CALL'].isna() & (df['CALL_TYPE'] == 'A')).sum()}")
# ORIGIN_STAND: Taxi stand ID where the trip started (only set when CALL_TYPE = ‘B’). Otherwise NULL.
print(f"Number of rows with ORIGIN_STAND set but CALL_TYPE is not'B'': {(df['ORIGIN_STAND'].notna() & (df['CALL_TYPE'] != 'B')).sum()}")
print(f"Number of rows with ORIGIN_STAND not set but CALL_TYPE is 'B': {(df['ORIGIN_STAND'].isna() & (df['CALL_TYPE'] == 'B')).sum()}")

print(f'Identical rows: {df.duplicated().sum()}')
print(f"Number of duplicated TRIP_ID rows: {df['TRIP_ID'].duplicated().sum()}")
duplicate_trip_ids = df[df['TRIP_ID'].duplicated(keep=False)]
duplicate_trip_counts = duplicate_trip_ids.groupby('TRIP_ID').size().sort_values(ascending=False)
print('Duplicated TRIP_IDs and frequence:\n', duplicate_trip_counts)

df['POINT_COUNT'] = df['POLYLINE'].apply(count_points)
duplicates = df[df['TRIP_ID'].duplicated(keep=False)]
print(f"Number of distinct TRIP_IDs that appear more than once: {duplicates['TRIP_ID'].nunique()}")

print(df['TAXI_ID'].nunique())
print(df['TAXI_ID'].value_counts(dropna=False))

print(df['TRIP_ID'].nunique())

# print columns that have different values for the same TRIP_ID
for column in df.columns:
  if column == 'TRIP_ID':
    continue
  diff_values = (duplicates.groupby('TRIP_ID')[column].nunique(dropna=False) > 1).sum()
  print(column, diff_values)

print(duplicates.drop(columns='POLYLINE').head())

most_pts = duplicates.loc[duplicates.groupby('TRIP_ID')['POINT_COUNT'].idxmax()]
print(f"CALL_TYPE with the most GPS points: \n{most_pts['CALL_TYPE'].value_counts()}")

# prints number of invalid trips
print(f"Number of empty trajectories: {(df['POINT_COUNT'] == 0).sum()}")
print(f"Number of points less than 3: {(df['POINT_COUNT'] < 3).sum()}")
print("Minimum GPS points:", df['POINT_COUNT'].min(), "Maximum GPS points:", df['POINT_COUNT'].max())

print(df['MISSING_DATA'].value_counts())
print(df.loc[df['MISSING_DATA'] == True, ['TRIP_ID', 'CALL_TYPE', 'POINT_COUNT']].head(10))
print("Number of MISSING_DATA = True that have less than 3 points: ", (df[df['MISSING_DATA']]['POINT_COUNT'] < 3).sum())

print(df.groupby('MISSING_DATA')['POINT_COUNT'].describe())
print(df.groupby('CALL_TYPE')['MISSING_DATA'].sum()) # returns count of MISSING_DATA = True for every CALL_TYPE
