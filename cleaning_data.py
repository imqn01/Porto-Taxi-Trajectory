import json
import pandas as pd

def count_points(polyline):
  if not isinstance(polyline, str):
    return 0
  try:
    data = json.loads(polyline)
    return len(data) if isinstance(data, list) else 0
  except json.JSONDecodeError:
    return 0
  
df = pd.read_csv('porto/porto.csv')

print("Original rows:", df.shape[0])
exact_duplicates = df[df.duplicated(keep=False)].groupby('TRIP_ID').size().sort_values(ascending=False)
print('Number of TRIP_IDs that are duplicated:', len(exact_duplicates))
print(exact_duplicates)

removed_exact_duplicates = df[df.duplicated(keep='first')].copy()
print('Identical rows removed:', len(removed_exact_duplicates))
removed_exact_duplicates.to_csv('porto/removed_exact_duplicates.csv', index=False)

df = df.drop_duplicates().copy()
print('Rows after removing exact duplicates:', df.shape[0])

# Remove duplicated TRIP_IDs
df['POINT_COUNT'] = df['POLYLINE'].apply(count_points)
repeated_trip_ids = df[df['TRIP_ID'].duplicated(keep=False)].copy()
repeated_trips = repeated_trip_ids.groupby('TRIP_ID').size().sort_values(ascending=False)

print("Repeated TRIP_IDs:\n", repeated_trip_ids['TRIP_ID'].nunique())
print('Rows with repeated TRIP_IDs:', len(repeated_trip_ids))
print("Rows to remove:", df['TRIP_ID'].duplicated(keep='first').sum())
print(repeated_trips)

df = df.sort_values(['TRIP_ID', 'POINT_COUNT'], ascending=[True, False], kind='stable')
removed_repeated_trip_ids = df[df.duplicated('TRIP_ID', keep='first')].copy()
print('Duplicated TRIP_ID rows removed:', len(removed_repeated_trip_ids))

removed_repeated_trip_ids.to_csv('porto/removed_repeated_trip_ids.csv', index=False)
df = df.drop_duplicates('TRIP_ID', keep='first').copy()

print('Total rows after removing duplicates:', df.shape[0])
df.to_csv('porto/porto_cleaned.csv', index=False)