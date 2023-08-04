from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import os

app = FastAPI()

#   Load .env
load_dotenv( '.env' )
user = os.getenv( 'user' )
password = os.getenv( 'password' )
MY_VARIABLE = os.getenv('MY_VARIABLE')

#   Connect to MongoDB
client = MongoClient(f"mongodb+srv://{user}:{password}@cluster0.dpx3ndy.mongodb.net/")
db = client['EventBud']
collection = db['Events']

#   CORS
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

class Ticket( BaseModel ):
    ticketName: str
    price: int
    amount: int

class Event(BaseModel):
    eventId: str
    tag: str
    name: str
    startDate: str
    endDate: str
    featured: bool
    info: str
    location: str
    tickets: list[Ticket]
    imageUrl: str

##############################################################
#
#   API
#

#   Root
@app.get('/')
def read_root():
    return { 'details' : f'Hello, this is EventBud API. Please go to {MY_VARIABLE} for more details.' }

#   Get Event Details
@app.get('/event/{eventId}')
def get_event( eventId: str ):
    ''' Get event details by eventId
        Input: eventId (str)
        Output: event (dict)
    '''
    event = collection.find_one( { 'eventId' : eventId }, { '_id' : 0 } )
    return event