from DbConnector import DbConnector
from tabulate import tabulate


class PortoTaxiQueries:

    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor

    def show_table(self, query, title=None):
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.print_table(rows, self.cursor.column_names, title=title)

    def print_table(self, rows, headers, title=None):
        table = tabulate(rows, headers=headers)
        if title:
            table_width = len(table.split("\n")[0])
            centered_title = f"\033[1m{title.upper().center(table_width)}\033[0m"
            print(centered_title)
        print(table)

    def task1(self):
        """1. How many taxis, trips, and total GPS points are there?"""
        self.show_table("SELECT COUNT(*) AS total_taxis FROM Taxis")
        self.show_table("SELECT COUNT(*) AS total_trips FROM Trips")
        self.show_table("SELECT COUNT(*) AS total_GPS_points FROM GPS_Points")

    def task2(self):
        """2. What is the average number of trips per taxi?"""
        query = """
        	SELECT 
         		AVG(num_trips) AS avg_trips_per_taxi
            FROM (SELECT COUNT(*) AS num_trips
            FROM Trips
            GROUP BY taxi_id) AS per_taxi
            """
        self.show_table(query)

    def task3(self):
        """3. List the top 20 taxis with the most trips."""
        query = """
        	SELECT 
         		taxi_id, 
           		COUNT(*) AS num_trips
            FROM Trips
            GROUP BY taxi_id
            ORDER BY num_trips DESC
            LIMIT 20
            """
        self.show_table(query)

    def task4a(self):
        """4. a) What is the most used call type per taxi?"""
        self.cursor.execute("""
            SELECT 
            	taxi_id, 
             	call_type
            FROM Trips
            GROUP BY taxi_id, call_type
            ORDER BY taxi_id, COUNT(*) DESC, call_type
            """)
        rows = self.cursor.fetchall()
        most_used_call_type_per_taxi = {}
        for taxi_id, call_type in rows:
            if taxi_id not in most_used_call_type_per_taxi:
                most_used_call_type_per_taxi[taxi_id] = call_type
        table = [
            (taxi_id, call_type)
            for taxi_id, call_type in most_used_call_type_per_taxi.items()
        ]
        self.print_table(table, headers=["Taxi ID", "Most used call type"])

    def task4b(self):
        """4. b) For each call type, compute the average trip duration and distance,
        and also report the share of trips starting in four time bands: 00_06, 06_12, 12_18, and 18_24.
        """
        query = """
        	SELECT 
				call_type,
				COUNT(*) AS trips,
				SUM(point_count > 2) AS valid_trips,
				ROUND(AVG(CASE WHEN point_count > 2 THEN (point_count - 1) * 15 END), 1) AS avg_trip_dur_sec,
				ROUND(AVG(CASE WHEN point_count > 2 THEN distance_km END), 2) AS avg_distance_km,
    			ROUND(100 * SUM(HOUR(start_time) BETWEEN 0 AND 5) / COUNT(*), 1) AS band_00_06,
				ROUND(100 * SUM(HOUR(start_time) BETWEEN 6 AND 11) / COUNT(*), 1) AS band_06_12,
				ROUND(100 * SUM(HOUR(start_time) BETWEEN 12 AND 17) / COUNT(*), 1) AS band_12_18,
				ROUND(100 * SUM(HOUR(start_time) BETWEEN 18 AND 23) / COUNT(*), 1) AS band_18_24
			FROM Trips
			GROUP BY call_type
			ORDER BY call_type
			"""
        self.show_table(query)

    def task5(self):
        """5. Find the taxis with the most total hours driven as well as total distance driven.
        List them in order of total hours."""
        query = """
        	SELECT 
         		taxi_id,
                SUM((point_count - 1) * 15) / 3600 AS total_hours,
                SUM(distance_km) AS total_distance_km
            FROM Trips
            WHERE point_count > 2
            GROUP BY taxi_id
            ORDER BY total_hours DESC
            """
        self.show_table(query)

    def task6(self):
        """6. Find the trips that passed within 100 m of Porto City Hall. (longitude, latitude) = (-8.62911, 41.15794)"""
        longitude, latitude = -8.62911, 41.15794
        radius_m = 100
        self.cursor.execute(
            "SET @city_lon = %s, @city_lat = %s, @radius_m = %s",
            (longitude, latitude, radius_m),
        )
        self.cursor.execute("""
            SELECT DISTINCT trip_id
            FROM GPS_Points
            WHERE ST_Distance_Sphere(
            	POINT(longitude, latitude), 
                POINT(@city_lon, @city_lat)) <= @radius_m
            """)
        trips = self.cursor.fetchall()
        print(f"{len(trips)} passed within 100 m of Porto City Hall")
        self.print_table(trips[:20], ["Trip ID"])

    def task7(self):
        """7. Identify the number of invalid trips. An invalid trip is defined as a trip with fewer than 3 GPS points."""
        query = """
            SELECT COUNT(*) AS invalid_trips
            FROM Trips
            WHERE point_count < 3
            """
        self.show_table(query)

    def task8(self):
        """8. Find the trips that started on one calendar day and ended on the next (midnight crossers)."""
        self.cursor.execute("""
            WITH times AS (
            	SELECT 
            		trip_id, 
             		start_time, 
              		DATE_ADD(start_time, INTERVAL (point_count - 1) * 15 SECOND) AS end_time
            	FROM Trips
            	WHERE point_count > 2
            )
            SELECT
				trip_id,
				start_time,
				end_time
			FROM times
			WHERE DATE(end_time) > DATE(start_time)
            """)
        midnight_crossers = self.cursor.fetchall()
        print(f"{len(midnight_crossers)} midnight crossers")
        self.print_table(midnight_crossers[:10], self.cursor.column_names)

    def task9(self):
        """9. Find the trips whose start and end points are within 50 m of each other (circular trips)."""
        self.cursor.execute("""
			WITH start_end AS (
            	SELECT 
            		trip.trip_id,
                	ST_Distance_Sphere(
                     	POINT(start_point.longitude, start_point.latitude),
                		POINT(end_point.longitude, end_point.latitude)
            ) AS start_end_distance_m
            FROM Trips AS trip
            JOIN GPS_Points AS start_point ON trip.trip_id = start_point.trip_id AND start_point.sequence = 0
            JOIN GPS_Points AS end_point ON trip.trip_id = end_point.trip_id AND end_point.sequence = trip.point_count - 1
            WHERE trip.point_count > 2
            )
			SELECT
				trip_id,
				start_end_distance_m
			FROM start_end
			WHERE start_end_distance_m <= 50
            """)
        circular_trips = self.cursor.fetchall()
        print(f"{len(circular_trips)} circular trips")
        self.print_table(circular_trips[:20], self.cursor.column_names)

    def task10(self):
        """10. For each taxi, compute the average idle time between consecutive trips.
        List the top 20 taxis with the highest average idle time."""
        idle_time_between_trips = """
        	WITH times AS (
             	SELECT 
              		taxi_id, 
                	trip_id, 
                 	start_time, 
                  	DATE_ADD(start_time, INTERVAL GREATEST(point_count - 1, 0) * 15 SECOND) AS end_time
              	FROM Trips
            ),
            prev_trips AS (
				SELECT 
					taxi_id,
					start_time,
					LAG(end_time) OVER (PARTITION BY taxi_id ORDER BY start_time, trip_id) AS prev_end_time
				FROM times
			),
            idle_times AS (
            	SELECT 
             		taxi_id, 
              		TIMESTAMPDIFF(SECOND, prev_end_time, start_time) AS idle_seconds
             	FROM prev_trips
				WHERE prev_end_time IS NOT NULL
            )
            """
        query = idle_time_between_trips + """
            SELECT 
            	taxi_id, 
            	ROUND(AVG(idle_seconds) / 3600, 2) AS avg_idle_hours
            FROM idle_times
            WHERE idle_seconds >= 0
            GROUP BY taxi_id
            ORDER BY AVG(idle_seconds) DESC
            LIMIT 20
            """
        self.show_table(query)


def main():
    program = None
    try:
        program = PortoTaxiQueries()
        program.task1()
        program.task2()
        program.task3()
        program.task4a()
        program.task4b()
        program.task5()
        program.task6()
        program.task7()
        program.task8()
        program.task9()
        program.task10()

    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
