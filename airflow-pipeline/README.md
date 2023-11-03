# Assignment3-QAChatApplication-VectorEmbeddings
End-user facing question-answering chatbot application built using microservices architecture. Stack: Streamline, FastAPI, Airflow, Pinecone, Docker

Refer this to install airflow locally
https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

###  Pre-requisites:
1. You must have docker desktop installed -> https://docs.docker.com/get-docker/
2. You must clone this repository
3. You must have a mysql database installed -> https://dev.mysql.com/downloads/mysql/
4. Login as mysql root user and run azure-mysql-database/1_application_user_db_setup.sql (Change the passwords as per your choice)
5. Login as application_dba user and run azure-mysql-database/azure-mysql-database/2_application_table_setup.sql (Change the passwords as per your choice)

### Steps to setup up airflow pipelines and UI:
1. cd into airflow-pipeline/
2. open terminal and run `export AIRFLOW_HOME=$PWD`
3. `curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.7.2/docker-compose.yaml'`
4. `mkdir -p ./logs ./plugins ./config`
5. `echo -e "AIRFLOW_UID=$(id -u)" > .env`
6. `docker compose up airflow-init`
7. `docker compose up`