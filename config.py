# config.py
import urllib.parse

class Config:
    SECRET_KEY = "secret-key-thay-sau"
    
    DRIVER = "ODBC Driver 18 for SQL Server"
    SERVER = "MSI"            # hoặc IP máy thật #MSI
    DATABASE = "project1"
    USERNAME = "sa"
    PASSWORD = "Minh_26102005" #Minh_26102005

    CONNECTION_STRING = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )

    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(CONNECTION_STRING)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

