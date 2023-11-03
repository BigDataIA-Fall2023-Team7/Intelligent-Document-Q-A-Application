from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://application_user:application_user!12345@amkdb.mysql.database.azure.com/db_damg7245team7"
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://INFO6210:NEUHusky!@boyce.coe.neu.edu/DAMG_Assignment3?driver=ODBC+Driver+18+for+SQL+Server&encrypt=no"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()