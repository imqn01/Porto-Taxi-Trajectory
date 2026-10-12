from DbConnector import DbConnector
from tabulate import tabulate
import json
import pandas as pd

class PortoTaxiProgram:

    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor

    def create_tables(self):
        query1 = """CREATE TABLE IF NOT EXISTS Taxis (
                   taxi_id INT NOT NULL PRIMARY KEY
                )"""
        self.cursor.execute(query1)
        
        query2 = """CREATE TABLE IF NOT EXISTS Trips (
                   trip_id BIGINT NOT NULL PRIMARY KEY,
                   taxi_id INT NOT NULL,
                   call_type ENUM('A', 'B', 'C') NOT NULL,
                   origin_call INT NULL,
                   origin_stand INT NULL,
                   day_type ENUM('A', 'B', 'C') NOT NULL,
                   missing_data BOOLEAN NOT NULL,
                   start_time DATETIME NOT NULL,
                   point_count INT NOT NULL,
                   FOREIGN KEY (taxi_id) REFERENCES Taxis(taxi_id) ON DELETE CASCADE
                )"""
        self.cursor.execute(query2)
        
        query3 = """CREATE TABLE IF NOT EXISTS GPS_Points (
                   trip_id BIGINT NOT NULL,
                   latitude DECIMAL(11,8) NOT NULL,
                   longitude DECIMAL(11,8) NOT NULL,
                   sequence INT NOT NULL,
                   FOREIGN KEY (trip_id) REFERENCES Trips(trip_id) ON DELETE CASCADE,
                   PRIMARY KEY (trip_id, sequence)
                )"""
        self.cursor.execute(query3)
        self.db_connection.commit()

    def insert_data(self, table_name):
        names = ['Bobby', 'Mc', 'McSmack', 'Board']
        for name in names:
            # Take note that the name is wrapped in '' --> '%s' because it is a string,
            # while an int would be %s etc
            query = "INSERT INTO %s (name) VALUES ('%s')"
            self.cursor.execute(query % (table_name, name))
        self.db_connection.commit()
        
    def insert_taxi_data(self, csv_file):
      df = pd.read_csv('porto/porto_cleaned.csv', usecols=['TAXI_ID'])
      taxi_ids = [(int(taxi_id),) for taxi_id in df['TAXI_ID'].unique()]
      query = "INSERT INTO Taxis (taxi_id) VALUES (%s)"
      self.cursor.executemany(query, taxi_ids)
      self.db_connection.commit()
      print(f"Inserted {len(taxi_ids)} unique taxi IDs into Taxis table")
      
    def insert_trip_data(self, csv_file, limit=None):
      columns = ['TRIP_ID', 'TAXI_ID', 'CALL_TYPE', 'ORIGIN_CALL', 'ORIGIN_STAND', 'DAY_TYPE', 'MISSING_DATA', 'TIMESTAMP', 'POINT_COUNT']
      df = pd.read_csv(csv_file, usecols=columns, nrows=limit)
      df['start_time'] = pd.to_datetime(df['TIMESTAMP'], unit='s')
      rows = []
      for row in df.itertuples(index=False):
        rows.append((int(row.TRIP_ID), int(row.TAXI_ID), row.CALL_TYPE,
                     int(row.ORIGIN_CALL) if pd.notna(row.ORIGIN_CALL) else None,
                     int(row.ORIGIN_STAND) if pd.notna(row.ORIGIN_STAND) else None,
                     row.DAY_TYPE, bool(row.MISSING_DATA), row.start_time.to_pydatetime(), int(row.POINT_COUNT)))
      query = """INSERT INTO Trips (trip_id, taxi_id, call_type, origin_call, origin_stand, day_type, missing_data, start_time, point_count)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
      BATCH_SIZE = 50000
      for i in range(0, len(rows), BATCH_SIZE):
          batch = rows[i:i+BATCH_SIZE]
          self.cursor.executemany(query, batch)
          self.db_connection.commit()
      print(f"Inserted {len(rows)} rows into Trips table")
      
    def insert_gps_data(self, csv_file, limit=None):
      query = """INSERT INTO GPS_Points (trip_id, latitude, longitude, sequence)
              VALUES (%s, %s, %s, %s)"""
      df = pd.read_csv(csv_file, usecols=['TRIP_ID', 'POLYLINE'], chunksize=20000, nrows=limit)
      for chunk in df:
        rows = []
        for row in chunk.itertuples(index=False):
          trip_id = int(row.TRIP_ID)
          polyline = json.loads(row.POLYLINE) if pd.notna(row.POLYLINE) else []
          for sequence, point in enumerate(polyline):
            longitude, latitude = point
            rows.append((trip_id, latitude, longitude, sequence))
        if rows:
          self.cursor.executemany(query, rows)
          self.db_connection.commit()
        print(f"Inserted {len(rows)} rows into GPS_Points table")
          

    def fetch_data(self, table_name):
        query = "SELECT * FROM %s"
        self.cursor.execute(query % table_name)
        rows = self.cursor.fetchall()
        print("Data from table %s, raw format:" % table_name)
        print(rows)
        # Using tabulate to show the table in a nice way
        print("Data from table %s, tabulated:" % table_name)
        print(tabulate(rows, headers=self.cursor.column_names))
        return rows

    def drop_table(self, table_name):
        print("Dropping table %s..." % table_name)
        query = "DROP TABLE IF EXISTS %s"
        self.cursor.execute(query % table_name)

    def show_tables(self):
        self.cursor.execute("SHOW TABLES")
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))


def main():
    program = None
    try:
        program = PortoTaxiProgram()
        program.drop_table(table_name="GPS_Points")
        program.drop_table(table_name="Trips")
        program.drop_table(table_name="Taxis")
        program.create_tables()
        program.show_tables()
        program.insert_taxi_data(csv_file='porto/porto_cleaned.csv')
        program.insert_trip_data(csv_file='porto/porto_cleaned.csv')
        program.insert_gps_data(csv_file='porto/porto_cleaned.csv')
        program.show_tables()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == '__main__':
    main()
