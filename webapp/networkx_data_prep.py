from collections import defaultdict
import pandas as pd
from read_write_to_sql import BrewHoundDatabase
from sqlalchemy import create_engine
import networkx as nx


psql_db_connection = BrewHoundDatabase()

def query_sql_write_to_csv(sql_statement, filepath):
    temp_df = psql_db_connection.query_sql(sql_statement)
    temp_df.to_csv(filepath,sep='\t', index=False)

def create_graph(filepath):
    G = nx.read_edgelist(filepath, delimiter='\t')

if __name__ == '__main__':
    #create .csv for beer to brewrey mapping
    query_sql_write_to_csv("""
                            SELECT brew_location_id, beer_id
                            FROM beer_brew_loc
                            """)
    #create csv for beer to location graph
    query_sql_write_to_csv("""
                            SELECT zip_code, beer_id
                            FROM beer_brew_loc
                            """)
    #create csv for brewery to zip code mapping
    query_sql_write_to_csv("""
                            SELECT brew_location_id, zip_code
                            FROM beer_brew_loc
                            """)
