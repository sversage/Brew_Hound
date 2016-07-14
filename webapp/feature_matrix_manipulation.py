from collections import defaultdict
import pandas as pd
from read_write_to_sql import BrewHoundDatabase

psql_db_connection = BrewHoundDatabase()

def query_sql(sql_statement):
    return psql_db_connection.query_sql(sql_statement)

def data_types_to_numeric(df, fields):
    for col in fields:
        df[col] = pd.to_numeric(df[col])
    return df

#determined categorial variables aren't helpful due to sparse data availability
def categorial_dummy(df, fields):
    for col in fields:
        temp_df = pd.concat([df, pd.get_dummies(df[col])], axis=1)
        temp_df.drop(col, axis=1, inplace=True)
    return temp_df

def style_avg_call():
    try:
        psql_db_connection.engine.execute("""CREATE TABLE mod_style as SELECT *, ("abvMax" + "abvMin")/2 as AVG_ABV, \
             ("fgMax" + "fgMin")/2 as FG_AVG, \
             ("ibuMax" + "ibuMin")/2 as IBU_AVG, \
             ("srmMax" + "srmMin")/2 as srm_AVG \
             FROM style_info;""")
    except:
        psql_db_connection.engine.execute("""DROP TABLE mod_style""")
        style_avg_call()
def feature_maxtrix_to_numeric_dummy_categorial():
    """base feature matrix to get all variables in the correct data types
        and categorial variables into the appropriate format."""

    num_fields = ['abv','abvMax','abvMin','fgMax','fgMin','ibu','ibuMax','ibuMin','ogMax','ogMin','originalgravity','srmMax','srmMin']
    #cat_fields = ['isorganic','servingtemperature']

    df1 = query_sql("SELECT * FROM full_features")
    df2 = data_types_to_numeric(df1,num_fields)
    #df3 = categorial_dummy(df2, cat_fields)
    df2.drop(['servingtemperature','originalgravity','ogMax', 'isorganic','glasswareId'], axis =1, inplace = True)
    psql_db_connection.write_to_sql(df2,'feature_matrix_base')


    #SQL queries to insert the average IBU rating per the style of the beer
    ibu_mod_query = """CREATE TABLE temp_feats AS
    SELECT ff.*, ms.ibu_avg
    FROM feature_matrix_base AS ff
    LEFT JOIN mod_style as ms ON ms.id = ff."styleId";

    CREATE TABLE feature_matrix_2 AS
    SELECT *,
    CASE WHEN ibu IS NULL THEN IBU_AVG
         ELSE ibu
         END as ibus
    FROM temp_feats;

    ALTER TABLE feature_matrix_2 DROP COLUMN ibu;
    ALTER TABLE feature_matrix_2 DROP COLUMN ibu_avg;
    ALTER TABLE feature_matrix_2 DROP COLUMN "ibuMax";
    ALTER TABLE feature_matrix_2 DROP COLUMN "ibuMin";
    ALTER TABLE feature_matrix_2 DROP COLUMN "level_0";
    DROP TABLE temp_feats;"""

    try:
        psql_db_connection.engine.execute(ibu_mod_query)
    except:
        psql_db_connection.engine.execute('DROP TABLE feature_matrix_2')
        psql_db_connection.engine.execute(ibu_mod_query)

if __name__ == '__main__':
    feature_maxtrix_to_numeric_dummy_categorial()
    #style_avg_call()SE
