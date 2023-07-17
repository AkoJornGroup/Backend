from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# CORS
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

##############################################################
#
#   Class OOP
#

##############################################################
#
#   API
#

@app.get('/')
def read_root():
    return {'Hello': 'World'}