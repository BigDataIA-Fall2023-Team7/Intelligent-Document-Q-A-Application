from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from airflow.models.param import Param
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import re
import sys
import requests
import mysql.connector
import os
from datetime import datetime
import secrets
import string
import io
import pypdf

from airflow.providers.google.cloud.operators.gcs import (
    GCSCreateBucketOperator,
    GCSDeleteBucketOperator,
    GCSDeleteObjectsOperator,
    GCSListObjectsOperator,
)

from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator


# To solve the stuck requests problem
from _scproxy import _get_proxy_settings
_get_proxy_settings()



# Sql statements
SQL_INSERT_APPLICATION_LOG="INSERT INTO ApplicationLog (Application_LogCorrelationID, Application_Component, Application_LogStatus, Application_LogDetails) VALUES (%s, %s, %s, %s)"

# Getting config parameters
MYSQL_HOST = Variable.get("airflow_var_mysqlhost")
MYSQL_USER = Variable.get("airflow_var_mysqluser")
MYSQL_PASSWORD = Variable.get("airflow_var_mysqlpassword")
MYSQL_DATABASE = Variable.get("airflow_var_mysqldatabase")
GCS_BUCKET = Variable.get("airflow_var_gcsbucket")


# Utility Functions
def generate_random_string(length=6):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string

# Global Variables
PIPELINE_NAME='pipeline1'
FILE_CACHE = Variable.get("airflow_var_filecache")



def create_connection():
    config = {
        "host": MYSQL_HOST,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": MYSQL_DATABASE,
    }
    print(f"Creating connection to database: {MYSQL_DATABASE}")
    conn = mysql.connector.connect(**config)
    print("Database Connectivity Successful!")
    return conn

def execute_query(query, params=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

def close_cursor(cursor):
    cursor.close()

def close_connection(connection):
    connection.close()

def applicationLogger(applicationlog_correlationid, application_component, log_status, log_details):
    execute_query(SQL_INSERT_APPLICATION_LOG, (applicationlog_correlationid, application_component, log_status, log_details))
    print("Logging Record inserted successfully.")

#
#  DAG task functions
# 



def task_inititatePipeline(**context):
    ti = context['ti']
    PDF_PROCESSOR = context['params']['pdfProcessor'].lower()
    APPLICATION_LOG_CORRELATION_ID = datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + '-' + generate_random_string()
    ti.xcom_push(key='APPLICATION_LOG_CORRELATION_ID', value=APPLICATION_LOG_CORRELATION_ID)
    ti.xcom_push(key='PDF_PROCESSOR', value=PDF_PROCESSOR)

    print(f'Application Log Correlation ID : {APPLICATION_LOG_CORRELATION_ID}')
    inputPDFLinksArray = context["params"]["inputPDFLinksArray"]
    pdfProcessor = context["params"]["pdfProcessor"]
    nougatAPIServerURL = context["params"]["nougatAPIServerURL"]
    print(f'Initiating the pipeline {PIPELINE_NAME}')
    print("Inputs")
    print(f'Input Configuration Param: inputPDFLinksArray -> {inputPDFLinksArray}')
    print(f'Input Configuration Param: pdfProcessor -> {pdfProcessor}')
    print(f'Input Configuration Param: nougatAPIServerURL -> {nougatAPIServerURL}')

    if PDF_PROCESSOR == "nougat" or PDF_PROCESSOR == "pypdf":
        pass
    else:
        raise Exception("*** Incorrect PDF Processor (Only 'nougat' or 'pypdf' allowed ) ***")
    
    print('Testing the connectivity to MySQL database')
    log_details = f'Started the pipeline {PIPELINE_NAME} with inputPDFLinksArray->{inputPDFLinksArray} & pdfProcessor->{pdfProcessor}'
    applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)
    

def task_validateInputPDFLinks(**context):
    ti = context['ti']
    APPLICATION_LOG_CORRELATION_ID = ti.xcom_pull(key='APPLICATION_LOG_CORRELATION_ID')

    print('Validating Input PDF Links')
    inputPDFLinksArray = context["params"]["inputPDFLinksArray"]
    if len(inputPDFLinksArray)<=0:
        log_details = '***Empty inputPDFLinksArray while validating urls!***'
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Error', log_details=log_details)
        raise Exception(log_details)
    
    print(f"Validating URLs -> {inputPDFLinksArray}")
    inputPDFLinksValidationIssues = []
    for i in inputPDFLinksArray:
        try:
            print(f"Validating URL -> {i}")
            response = requests.head(i)
            content_type = response.headers.get("Content-Type")
            print("Got HTTP Response")
            if response.status_code==200 and ('application/pdf' in content_type.lower()):
                a = f"Validation PDF Link Successful : {i}"
                print(a)
            else:
                a = f"Validation PDF Link Unsuccessful : {i}, Reason: {str(response.status_code) + ' ' + response.reason}"
                print(a)
                inputPDFLinksValidationIssues.append(a)
        except Exception as e:
            a = f"Validation PDF Link Unsuccessful : {i}, Reason: {str(e)}"
            print(a)
            inputPDFLinksValidationIssues.append(a)

    if len(inputPDFLinksValidationIssues)>=1:
        log_details = '*** Multiple InputPDF Link Validation Issues ***' + str(inputPDFLinksValidationIssues)
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Error', log_details=log_details)
        raise Exception(log_details)
    else:
        log_details =  'All InputPDF Links Valid'
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)


def task_downloadPDFs(**context):
    ti = context['ti']
    APPLICATION_LOG_CORRELATION_ID = ti.xcom_pull(key='APPLICATION_LOG_CORRELATION_ID')

    print('Downloading All PDFs via submitted links')
    inputPDFLinksArray = context["params"]["inputPDFLinksArray"]

    downloadIssues = []
    downloadedFileLocations = []
    for i, link in enumerate(inputPDFLinksArray):

        # extract the pdf name from the link
        match = re.search(r'\/([^/]+\.pdf)$', link)
        if match:
            pdf_filename =  match.group(1)
        else:
            fileid = APPLICATION_LOG_CORRELATION_ID + '-' +str(i)
            pdf_filename =  "InputPDF_" + fileid +  ".pdf"

        try:
            response = requests.get(link)
            content_type = response.headers.get("Content-Type")
            if response.status_code==200 and ('application/pdf' in content_type.lower()):
                with open(FILE_CACHE + pdf_filename, 'wb') as file:
                    file.write(response.content)
                
                downloadedFileLocations.append(FILE_CACHE + pdf_filename)
                log_details =  f"Download PDF Successful : {link} -> {pdf_filename}"
                print(log_details)
                applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)
            else:
                log_details = f"Download PDF Unsuccessful : {link} -> {pdf_filename}, Reason: {str(response.status_code) + ' ' + response.reason}"
                downloadIssues.append(log_details)
                print(log_details)
                applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Error', log_details=log_details)
        except Exception as e:
            log_details = f"Problem downloading PDF : {link} -> {pdf_filename}, Reason: {str(e)}"
            downloadIssues.append(log_details)
            print(log_details)
            applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Error', log_details=log_details)
    
    if len(downloadIssues)>=1:
        log_details = '*** Multiple pdf download failures ***' + str(downloadIssues)
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Error', log_details=log_details)
        raise Exception(log_details)
    else:
        log_details =  'All PDF Downloads Complete'
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

        #Send the downloaded PDFs to GCS
        gcsSavedPDFLocations = []
        gcs_bucket = GCS_BUCKET
        gcs_prefix = APPLICATION_LOG_CORRELATION_ID + "/pdfs"
        log_details =  f'Using {gcs_bucket} to upload the downloaded PDFs'
        print(log_details)
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

        for location in downloadedFileLocations:
            filename = location.split('/')[-1]
            gcs_object_name = f"{gcs_prefix}/{filename}"
            upload_task = LocalFilesystemToGCSOperator(
                    task_id=f'{filename}',
                    src=location,
                    dst=gcs_object_name,
                    bucket=gcs_bucket,
                    mime_type="application/octet-stream",
                    gcp_conn_id="google_cloud_default",
                    dag=dag,
            )
            upload_task.execute(context=context)
            gcsSavedPDFLocations.append(gcs_object_name)
            log_details =  f'Uploaded {filename} to {gcs_object_name}'
            print(log_details)
            applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

        context['ti'].xcom_push(key='gcsSavedPDFLocations', value=gcsSavedPDFLocations)
        log_details =  f'Uploaded All PDFs to {gcs_bucket}/{gcs_prefix}'
        print(log_details)
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

        

def task_selectPDFProcessor(**context):
    ti = context['ti']
    APPLICATION_LOG_CORRELATION_ID = ti.xcom_pull(key='APPLICATION_LOG_CORRELATION_ID')

    pdfProcessor = ti.xcom_pull(key='PDF_PROCESSOR')
    if pdfProcessor == 'nougat':
        return 'task_processPDFViaNougat'
    elif pdfProcessor == 'pypdf':
        return 'task_processPDFViaPyPDF'
    else:
        raise Exception("*** Selecting PDF Processor Branch Failed ***")
    
def task_processPDFViaNougat(**context):
    ti = context['ti']
    APPLICATION_LOG_CORRELATION_ID = ti.xcom_pull(key='APPLICATION_LOG_CORRELATION_ID')
    pass

def task_processPDFViaPyPDF(**context):
    ti = context['ti']
    gcsSavedPDFLocations = context['ti'].xcom_pull(key='gcsSavedPDFLocations')
    APPLICATION_LOG_CORRELATION_ID = ti.xcom_pull(key='APPLICATION_LOG_CORRELATION_ID')

    gcs_bucket = GCS_BUCKET
    gcs_prefix = APPLICATION_LOG_CORRELATION_ID + "/pdfs/"
    log_details =  f'Redownloading PDFs from {gcs_bucket}/{gcs_prefix} to process using PyPDF'
    print(log_details)
    applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

    # Redownload the PDFs from GCS to FILECACHE for PyPDF Processing
    # Download each PDF one by one and process using PyPDF to get MMD file
    # Send that MMD file from FILECACHE to GCS
    gcsSavedMMDLocations = []
    for i, gcsObject in enumerate(gcsSavedPDFLocations):
        filename = gcsObject.replace('/', '_')
        download_file = GCSToLocalFilesystemOperator(
            task_id=f"download_file_{filename}",
            object_name=gcsObject,
            bucket=gcs_bucket,
            filename=FILE_CACHE + filename
        )
        download_file.execute(context=context)
        log_details =  f'Redownloaded file {gcs_bucket}/{gcsObject} to process using PyPDF'
        print(log_details)
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

        with open(FILE_CACHE + filename, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            pages = pdf_reader.pages[:]
            contents = "".join([page.extract_text() for page in pages])

        mmdFileName = f'{FILE_CACHE + filename}'[:-3] + "mmd"
        with open(mmdFileName, 'w') as file:
            file.write(contents)

        #Send the processed MMD to GCS
        
        gcs_bucket = GCS_BUCKET
        gcs_prefix = APPLICATION_LOG_CORRELATION_ID + "/pypdf-mmds"
        log_details =  f'Using {gcs_bucket} to upload the processed PyPDF MMDs'
        print(log_details)
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

        filename = mmdFileName.split('/')[-1]
        gcs_object_name = f"{gcs_prefix}/{filename}"
        upload_task = LocalFilesystemToGCSOperator(
                task_id=f'{filename}',
                src=mmdFileName,
                dst=gcs_object_name,
                bucket=gcs_bucket,
                mime_type="application/octet-stream",
                gcp_conn_id="google_cloud_default",
                dag=dag,
        )
        upload_task.execute(context=context)
        gcsSavedMMDLocations.append(gcs_object_name)
        log_details =  f'Uploaded {filename} to {gcs_object_name}'
        print(log_details)
        applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

    context['ti'].xcom_push(key='gcsSavedMMDLocations', value=gcsSavedMMDLocations)
    log_details =  f'Uploaded All MMDs to {gcs_bucket}/{gcs_prefix}'
    print(log_details)
    applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)


    log_details =  f'PyPDF Processed all PDFs from {gcs_bucket}/{gcs_prefix}'
    print(log_details)
    applicationLogger(applicationlog_correlationid=APPLICATION_LOG_CORRELATION_ID, application_component=PIPELINE_NAME, log_status='Info', log_details=log_details)

    




with DAG(
    dag_id=PIPELINE_NAME,
    description=PIPELINE_NAME,
    start_date=days_ago(1),
    schedule_interval=None,
    params={
    "inputPDFLinksArray": Param(["https://www.sec.gov/files/formadv.pdf", "https://www.sec.gov/files/forms-1.pdf"], type="array"),
    "pdfProcessor": Param("pypdf", type="string"),
    "nougatAPIServerURL": Param("", type="string"),
    },
) as dag:

    task_inititatePipeline = PythonOperator(
        task_id='task_inititatePipeline',
        python_callable=task_inititatePipeline,
        provide_context=True
    )

    task_validateInputPDFLinks = PythonOperator(
        task_id='task_validateInputPDFLinks',
        python_callable=task_validateInputPDFLinks
    )

    task_downloadPDFs = PythonOperator(
        task_id='task_downloadPDFs',
        python_callable=task_downloadPDFs
    )

    task_selectPDFProcessor = BranchPythonOperator(
        task_id='task_selectPDFProcessor',
        python_callable=task_selectPDFProcessor
    )

    task_processPDFViaNougat = PythonOperator(
        task_id='task_processPDFViaNougat',
        python_callable=task_processPDFViaNougat
    )

    task_processPDFViaPyPDF = PythonOperator(
        task_id='task_processPDFViaPyPDF',
        python_callable=task_processPDFViaPyPDF
    )

task_inititatePipeline >> \
    task_validateInputPDFLinks >> \
        task_downloadPDFs >> \
            task_selectPDFProcessor >> \
                [task_processPDFViaNougat, task_processPDFViaPyPDF]