import pandas as pd
from collections import Counter
import csv

Source_data = "data/porto.csv"
Output_data = "data/porto_no_duplicates.csv"
REMOVED = "data/removed_duplicates.csv"

seen = set()
rows_in = 0
rows_out = 0 
next_id = 1
first = True #TODO

for chunk in pd.read_csv(Source_data, dtype=str, keep_default_na=False, chunksize=200_000):
    hashes = pd.util.hash_pandas_object(chunk, index=False)
    seen_before = hashes.isin(seen)
    duplicate_in_chunk = hashes.duplicated(keep="first")
    
    keep = ~(seen_before | duplicate_in_chunk)
    seen.update(hashes[keep])
    
    
    kept = chunk[keep].copy()
    kept["TRIP_ID"] = pd.RangeIndex(next_id, next_id + len(kept)).astype(str)
    next_id += len(kept)
    
    kept.to_csv(Output_data, mode="w" if first else "a", header=first, index=False, quoting=csv.QUOTE_ALL)    
    chunk[~keep].to_csv(REMOVED, mode="w" if first else "a", header=first, index=False, quoting=csv.QUOTE_ALL)   # TODO

    
    rows_in += len(chunk)
    rows_out += keep.sum()
    first = False
print(f"Rows read: {rows_in}")
print(f"Duplicate rows removed: {rows_in - rows_out}")
print(f"Rows kept: {rows_out}")
print(f"Siste ID tildelt: {next_id-1}")


