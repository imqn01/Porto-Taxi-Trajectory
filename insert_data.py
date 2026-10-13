from DbConnector import DbConnector
from tabulate import tabulate
import json
import pandas as pd
from haversine import haversine

MAX_SPEED_KMH = 200
MAX_SEGMENT_KM = MAX_SPEED_KMH / 3600 * 15


def calc_distance_km(gps_points):
    total_distance = 0.0
    for p1, p2 in zip(gps_points, gps_points[1:]):
        segment = haversine((p1[1], p1[0]), (p2[1], p2[0]))
        if segment <= MAX_SEGMENT_KM:
            total_distance += segment
    return total_distance


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
                   distance_km DOUBLE NOT NULL,
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

    def insert_taxi_data(self, csv_file):
        df = pd.read_csv(csv_file, usecols=["TAXI_ID"])
        taxi_ids = [(int(taxi_id),) for taxi_id in df["TAXI_ID"].unique()]
        query = "INSERT INTO Taxis (taxi_id) VALUES (%s)"
        self.cursor.executemany(query, taxi_ids)
        self.db_connection.commit()
        print(f"Inserted {len(taxi_ids)} unique taxi IDs into Taxis table")

    def insert_trip_data(self, csv_file, limit=None):
        columns = [
            "TRIP_ID",
            "TAXI_ID",
            "CALL_TYPE",
            "ORIGIN_CALL",
            "ORIGIN_STAND",
            "DAY_TYPE",
            "MISSING_DATA",
            "TIMESTAMP",
            "POINT_COUNT",
            "POLYLINE",
        ]
        query = """INSERT INTO Trips (trip_id, taxi_id, call_type, origin_call, origin_stand, day_type, missing_data, start_time, point_count, distance_km)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        df = pd.read_csv(csv_file, usecols=columns, chunksize=20000, nrows=limit)
        for chunk in df:
            rows = []
            chunk["start_time"] = pd.to_datetime(chunk["TIMESTAMP"], unit="s")
            for row in chunk.itertuples(index=False):
                gps_points = json.loads(row.POLYLINE) if pd.notna(row.POLYLINE) else []
                rows.append(
                    (
                        int(row.TRIP_ID),
                        int(row.TAXI_ID),
                        row.CALL_TYPE,
                        int(row.ORIGIN_CALL) if pd.notna(row.ORIGIN_CALL) else None,
                        int(row.ORIGIN_STAND) if pd.notna(row.ORIGIN_STAND) else None,
                        row.DAY_TYPE,
                        bool(row.MISSING_DATA),
                        row.start_time.to_pydatetime(),
                        int(row.POINT_COUNT),
                        calc_distance_km(gps_points),
                    )
                )
            self.cursor.executemany(query, rows)
            self.db_connection.commit()
            print(f"Inserted {len(rows)} rows into Trips table")

    def insert_gps_data(self, csv_file, limit=None):
        query = """INSERT INTO GPS_Points (trip_id, latitude, longitude, sequence)
              VALUES (%s, %s, %s, %s)"""
        df = pd.read_csv(
            csv_file, usecols=["TRIP_ID", "POLYLINE"], chunksize=20000, nrows=limit
        )
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
        program.insert_taxi_data(csv_file="porto/porto_cleaned.csv")
        program.insert_trip_data(csv_file="porto/porto_cleaned.csv")
        program.insert_gps_data(csv_file="porto/porto_cleaned.csv")
        program.show_tables()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
