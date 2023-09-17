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

class User( BaseModel ):
    userID: str
    email: str
    firstName: str
    lastName: str
    password_hash: str
    salt: str
    event: List[str]
    telephoneNumber: str

class User_Signup( BaseModel ):
    email: str
    password: str
    firstName: str
    lastName: str

class User_Signin( BaseModel ):
    email: str
    password: str

class EventOrganizer( BaseModel ):
    organizerID: str
    email: str
    organizerName: str
    organizerPhone: str
    password_hash: str
    salt: str

class EO_Signup( BaseModel ):
    email: str
    password: str
    organizerName: str
    organizerPhone: str

class EO_Signin( BaseModel ):
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

def generate_userID( email ):
    '''
        Generate userID from email
        Input: email (str)
        Output: userID (str)
    '''
    userID = email.split( '@' )[0]
    
    #   Check if userID already exists
    collection = db['User']
    number = 1
    while collection.find_one( { 'userID' : userID }, { '_id' : 0 } ):
        userID = userID + str( number )
        number += 1

    return userID

def generate_organizerID( email ):
    '''
        Generate organizerID from email
        Input: email (str)
        Output: organizerID (str)
    '''
    organizerID = email.split( '@' )[0]
    
    #   Check if organizerID already exists
    collection = db['EventOrganizer']
    number = 1
    while collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } ):
        organizerID = organizerID + str( number )
        number += 1

    return organizerID

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
    ''' 
        Get event details by eventID
        Input: eventID (str)
        Output: event (dict)
    '''

    #   Connect to MongoDB
    collection = db['Events']

    #   Get event details
    event = collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } )
    return event

#   Normal User Sign Up
@app.post('/signup', tags=['Users'])
def user_signup( user_signup: User_Signup ):
    ''' 
        Normal User Sign up
        Input: user_signup (User_Signup)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if email already exists
    if collection.find_one( { 'email' : user_signup.email }, { '_id' : 0 } ):
        raise HTTPException( status_code = 400, detail = 'Email already exists.' )
    
    #   Generate userID
    genUserID = generate_userID( user_signup.email )

    #   Hash password
    password_hash, password_salt = hash_password( user_signup.password )
    
    #   Insert user to database
    newUser = User(
        userID = genUserID,
        email = user_signup.email,
        firstName = user_signup.firstName,
        lastName = user_signup.lastName,
        password_hash = password_hash,
        salt = password_salt,
        event = [],
        telephoneNumber = '',
    )
    collection.insert_one( newUser.dict() )
    
    return { 'result' : 'success' }

#   Normal User Signin
@app.post('/signin', tags=['Users'])
def user_signin( user_signin: User_Signin ):
    '''
        Normal User Signin
        Input: user_signin (User_Signin)
        Output: userInfo (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if email exists
    user = collection.find_one( { 'email' : user_signin.email }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'Email or Password incorrect' )
    
    #   Hash password
    password_hash, _ = hash_password( user_signin.password, user['salt'] )

    #   Check if password is correct
    if password_hash != user['password_hash']:
        raise HTTPException( status_code = 400, detail = 'Email or Password incorrect' )
    
    userInfo = {
        'email' : user['email'],
        'firstName' : user['firstName']
    }
    
    return userInfo

#   Event Organizer Sign Up
@app.post('/eo_signup', tags=['Event Organizer'])
def eo_signup( eo_signup: EO_Signup ):
    ''' 
        Event Organizer Sign up
        Input: eo_signup (EO_Signup)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    collection = db['EventOrganizer']

    #   Check if email already exists
    if collection.find_one( { 'email' : eo_signup.email }, { '_id' : 0 } ):
        raise HTTPException( status_code = 400, detail = 'Email already exists.' )
    
    #   Generate organizerID
    genOrganizerID = generate_organizerID( eo_signup.email )

    #   Hash password
    password_hash, password_salt = hash_password( eo_signup.password )
    
    #   Insert user to database
    newEO = EventOrganizer(
        organizerID = genOrganizerID,
        email = eo_signup.email,
        organizerName = eo_signup.organizerName,
        organizerPhone = eo_signup.organizerPhone,
        password_hash = password_hash,
        salt = password_salt,
    )
    collection.insert_one( newEO.dict() )
    
    return { 'result' : 'success' }

#   Event Organizer Signin
@app.post('/eo_signin', tags=['Event Organizer'])
def eo_signin( eo_signin: EO_Signin ):
    '''
        Event Organizer Signin
        Input: eo_signin (EO_Signin)
        Output: eoInfo (dict)
    '''

    #   Connect to MongoDB
    collection = db['EventOrganizer']

    #   Check if email exists
    eo = collection.find_one( { 'email' : eo_signin.email }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Email or Password incorrect' )
    
    #   Hash password
    password_hash, _ = hash_password( eo_signin.password, eo['salt'] )

    #   Check if password is correct
    if password_hash != eo['password_hash']:
        raise HTTPException( status_code = 400, detail = 'Email or Password incorrect' )
    
    eoInfo = {
        'email' : eo['email'],
        'organizerName' : eo['organizerName'],
    }
    
    return eoInfo

#   Get Schedule
@app.get('/staff_event/{userID}', tags=['Staff'])
def get_staff_event( userID: str ):
    '''
        Get staff events
        Input: userID (str)
        Output: events (list)
    '''

    #   Connect to MongoDB
    userCollection = db['User']
    eventCollection = db['Events']

    #   Get user events
    user = userCollection.find_one( { 'userID' : userID }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'User not found' )
    
    eventID = user['event']

    events = []
    for event in eventID:
        events.append( eventCollection.find_one( { 'eventID' : event }, { '_id' : 0 } ) )

    sortedEvents = sorted( events, key = lambda i: i['startDateTime'] )

    return sortedEvents