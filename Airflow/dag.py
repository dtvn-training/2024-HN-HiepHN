from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor

dag = DAG(
    'project',
    default_args = {
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
    },
    description = 'A simple DAG sample by HiepHN',
    schedule_interval = "@daily",
    start_date = datetime(2024, 11, 25), # Start date
    tags = ['hiep'],
)

# -O ./output/tiki_url.csv
crawl_url = BashOperator(
    task_id = 'crawl_url',
    bash_command = 'cmd.exe /c "cd C:/Hiep/DataKiban/2024-HiepHN/Crawl_data/tiki && scrapy crawl tiki_url"',
    dag = dag
)

filter_url = BashOperator(
    task_id = 'filter_url',
    bash_command = 'cmd.exe /c "cd C:/Hiep/DataKiban/2024-HiepHN/Crawl_data/tiki && py filter.py"',
    dag = dag
)

#-O ../../Data_ETL/Data/tiki_product.csv
crawl_product = BashOperator(
    task_id = 'crawl_product',
    bash_command = 'cmd.exe /c "cd C:/Hiep/DataKiban/2024-HiepHN/Crawl_data/tiki && scrapy crawl tiki_product -O ../../Data_ETL/Data/tiki_product.csv"',
    dag = dag
)

etl = BashOperator(
    task_id = 'etl',
    bash_command = 'cmd.exe /c "C:/Hiep/pdi-ce-6.1.0.1-196/data-integration/kitchen.bat /file C:/Hiep/DataKiban/2024-HiepHN/Data_ETL/Job/Main.kjb"'
)

wait_for_url = FileSensor(
    task_id = 'wait_for_url',
    filepath = '/mnt/c/hiep/datakiban/2024-hiephn/crawl-data/tiki/output/tiki_url.csv', 
    fs_conn_id = 'fs_default', 
    poke_interval = 5,
    timeout = 300
)

wait_for_product = FileSensor( 
    task_id = 'wait_for_product',
    filepath = '/mnt/c/hiep/datakiban/2024-hiephn/data_etl/data/tiki_product.csv', 
    fs_conn_id = 'fs_default', 
    poke_interval = 5,
    timeout = 300)


crawl_url >> wait_for_url >> filter_url >> crawl_product >> wait_for_product >> etl