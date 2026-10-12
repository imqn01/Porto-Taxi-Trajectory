from DbConnector import DbConnector
from tabulate import tabulate


class PortoTaxiQueries:

    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor
    
    def show_table(self, query):
      self.cursor.execute(query)
      rows = self.cursor.fetchall()
      print(tabulate(rows, headers=self.cursor.column_names))

    # How many taxis, trips, and total GPS points are there?
    def task1(self):
      self.show_table("SELECT COUNT(*) FROM Taxis")
      self.show_table("SELECT COUNT(*) FROM Trips")
      self.show_table("SELECT COUNT(*) FROM GPS_Points")


def main():
    program = None
    try:
        program = PortoTaxiQueries()
        program.task1()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == '__main__':
    main()
