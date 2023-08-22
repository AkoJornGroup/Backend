from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import os
import hashlib, uuid

app = FastAPI()

#   Load .env
load_dotenv( '.env' )
user = os.getenv( 'user' )
password = os.getenv( 'password' )
MY_VARIABLE = os.getenv('MY_VARIABLE')

#   Connect to MongoDB
client = MongoClient(f"mongodb+srv://{user}:{password}@cluster0.dpx3ndy.mongodb.net/")
db = client['EventBud']
# collection = db['Events']

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

class Event( BaseModel ):
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

class Register( BaseModel ):
    email: str
    password: str
    firstName: str
    lastName: str

class User( BaseModel ):
    email: str
    firstName: str
    lastName: str
    password_hash: str
    salt: str
    

##############################################################
#
#   Helper Functions
#

def hash_password( password ):
    '''
        Hash password with salt
        Input: password (str)
        Output: password_hash (str), password_salt (str)
    '''
    salt = uuid.uuid4().hex
    password_salt = ( password + salt ).encode( 'utf-8' )
    password_hash = hashlib.sha512( password_salt ).hexdigest()
    return password_hash, password_salt

##############################################################
#
#   API
#

#   Root
@app.get('/')
def read_root():
    return { 'details' : f'Hello, this is EventBud API. Please go to {MY_VARIABLE} {user} for more details.' }

#   Get Event Details
@app.get('/event/{eventId}')
def get_event( eventId: str ):
    ''' Get event details by eventId
        Input: eventId (str)
        Output: event (dict)
    '''

    #   Connect to MongoDB
    collection = db['Events']

    #   Get event details
    event = collection.find_one( { 'eventId' : eventId }, { '_id' : 0 } )
    return event

#   Sign Up
@app.post('/signup')
def signup( register: Register ):
    ''' Sign up
        Input: register (Register)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if email already exists
    if collection.find_one( { 'email' : register.email } ):
        raise HTTPException( status_code = 400, detail = 'Email already exists.' )
    
    #   Hash password
    password_hash, password_salt = hash_password( register.password )
    
    #   Insert user to database
    newUser = User(
        email = register.email,
        firstName = register.firstName,
        lastName = register.lastName,
        password_hash = password_hash,
        salt = password_salt
    )
    collection.insert_one( newUser.dict() )
    
    return { 'result' : 'success' }