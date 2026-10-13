# Porto-Taxi-Trajectory

Exercise 2: Group project in TDT4225 Very Large, Distributed Data Volumes

## Requirements

      - Python and Docker
      - `pip install -r requirements.txt`

## Running the code

      1. Add porto.csv to a folder `porto`
      2. Create a `.env` file and choose passwords:
      ```
      DB_ROOT_PASSWORD=<choose password>
      DB_PASSWORD=<choose password>
      ```
      1. Run 
      ```
      docker compose up -d
      ```
      1. Run `EDA.ipynb` for exploratory data analysis
      2. Run `cleaning_data.py` to clean the dataset
      3. Run `insert_data.py` to create tables and insert data
      4. Run `queries.py` to execute the queries
