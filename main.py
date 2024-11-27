import os
import connection
import sqlparse
import pandas as pd

if __name__ == '__main__':
    # connection data source
    conf = connection.config('marketplace_prod')
    conn, engine = connection.get_conn(conf, 'DataSource')

    # connection dwh
    name_source_dwh = 'dwh'
    conf_dwh = connection.config(name_source_dwh)
    conn_dwh, engine_dwh = connection.get_conn(conf_dwh, name_source_dwh)
    cursor_dwh = conn_dwh.cursor()

    # get ququery string
    path_query = os.path.join(os.getcwd(), 'query')
    query = sqlparse.format(
        open(os.path.join(path_query, 'query.sql'), 'r').read(), strip_comments=True
    ).strip()
    dwh_design = sqlparse.format(
        open(os.path.join(path_query, 'dwh_design.sql'), 'r').read(), strip_comments=True
    ).strip()

    print(query)
    print(dwh_design)

    try:
        # get data
        print('[INFO] service etl is running..')
        df = pd.read_sql(query, engine)
        print(df)
        
        # create schema dwh
        cursor_dwh.execute(dwh_design)
        conn_dwh.commit()

        # ingest data to dwh
        df.to_sql(
            'dim_orders',
            engine_dwh,
            schema='public',
            if_exists='replace',
            index=False
        )
        print('[INFO] service etl is success..')
    
    except Exception as e:
        print('[ERROR] service etl is failed')
        print(str(e))

        pass