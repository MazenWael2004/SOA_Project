import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    # MYSQL_USER = os.getenv('MYSQL_USER')
    # MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    # MYSQL_HOST = os.getenv('MYSQL_HOST')
    # MYSQL_DB = os.getenv('MYSQL_DB')

    # SQLALCHEMY_DATABASE_URI = (
    #     f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
    #     f"@{MYSQL_HOST}/{MYSQL_DB}"
    # )
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'pricing.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False