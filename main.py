from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Dict
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

class TicketClass( BaseModel ):
    classID: str
    className: str
    amountOfSeat: int
    pricePerSeat: int

class Event( BaseModel ):
    eventID: str
    eventName: str
    startDateTime: str
    endDateTime: str
    onSaleDateTime: str
    endSaleDateTime: str
    location: str
    info: str
    featured: bool
    eventStatus: str
    tagName: List[str]
    posterImage: str
    seatImage: List[str]
    organizationName: str
    staff: List[str]
    ticket: Dict[str, bool]
    ticketType: str
    ticketClass: List[TicketClass]

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

class Signin( BaseModel ):
    email: str
    password: str
    

##############################################################
#
#   Helper Functions
#

def hash_password( password, salt = None ):
    '''
        Hash password with salt
        Input: password (str)
        Output: password_hash (str), password_salt (str)
    '''
    if not salt:
        salt = uuid.uuid4().hex
    password_salt = ( password + salt ).encode( 'utf-8' )
    password_hash = hashlib.sha512( password_salt ).hexdigest()
    return password_hash, salt

##############################################################
#
#   API
#

#   Root
@app.get('/')
def read_root():
    return { 'details' : f'Hello, this is EventBud API. Please go to {MY_VARIABLE} {user} for more details.' }

#   Get All Events
@app.get('/event', tags=['Events'])
def get_all_event():
    '''
        Get all events
        Input: None
        Output: events (list)
    '''

    #   Connect to MongoDB
    collection = db['Events']

    #   Get all events
    events = list( collection.find( {}, { '_id' : 0 } ) )

    return events

#   Get Event Details
@app.get('/event/{eventID}', tags=['Events'])
def get_event( eventID: str ):
    ''' Get event details by eventID
        Input: eventID (str)
        Output: event (dict)
    '''

    #   Connect to MongoDB
    collection = db['Events']

    #   Get event details
    event = collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } )
    return event

#   Sign Up
@app.post('/signup', tags=['Users'])
def signup( register: Register ):
    ''' Sign up
        Input: register (Register)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if email already exists
    if collection.find_one( { 'email' : register.email }, { '_id' : 0 } ):
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

#   Signin
@app.post('/signin', tags=['Users'])
def signin( signin: Signin ):
    '''
        Signin
        Input: signin (Signin)
        Output: userInfo (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if email exists
    user = collection.find_one( { 'email' : signin.email }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'Email or Password incorrect' )
    
    #   Hash password
    password_hash, _ = hash_password( signin.password, user['salt'] )

    #   Check if password is correct
    if password_hash != user['password_hash']:
        raise HTTPException( status_code = 400, detail = 'Email or Password incorrect' )
    
    userInfo = {
        # 'id' : user['_id'],
        'email' : user['email'],
        'firstName' : user['firstName']
    }
    
    return userInfo