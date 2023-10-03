from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Dict
import requests
import os
import hashlib, uuid
import datetime

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
    ticketID : str
    validDatetime : datetime.datetime
    expiredDatetime : datetime.datetime
    status : str
    seatNo : str
    className : str
    eventID : str
    userID : str
    eventName : str
    eventImage : str
    location : str

class TicketClass( BaseModel ):
    className: str
    amountOfSeat: int
    pricePerSeat: int
    rowNo: int
    columnNo: int
    seatNo: Dict[str, str]    #   Dict of seatNo and status

class NewTicket( BaseModel ):
    eventID: str
    userID: str
    className: str
    seatNo: List[str]   #   List of blank string if no seat

class ZoneRevenue( BaseModel ):
    className: str
    price: int
    ticketSold: int
    quota: int

class BankAccount( BaseModel ):
    bank: str
    accountName: str
    accountType: str
    accountNo: str
    branch: str

class Event( BaseModel ):
    eventID: str
    eventName: str
    startDateTime: datetime.datetime
    endDateTime: datetime.datetime
    onSaleDateTime: datetime.datetime
    endSaleDateTime: datetime.datetime
    location: str
    info: str
    featured: bool
    eventStatus: str
    tagName: List[str]
    posterImage: str
    seatImage: List[str]
    staff: List[str]
    ticketType: str
    ticketClass: List[TicketClass]
    organizerName: str
    timeStamp: datetime.datetime
    totalTicket: int
    soldTicket: int
    totalTicketValue: int
    totalRevenue: int
    zoneRevenue: List[ZoneRevenue]
    bankAccount: BankAccount

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

class User_Edit_Profile( BaseModel ):
    userID: str
    newEmail: str
    newFirstName: str
    newLastName: str
    newTelephoneNumber: str

class User_Reset_Password( BaseModel ):
    userID: str
    oldPassword: str
    newPassword: str

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

def generate_ticketID( eventID, userID, classID, seatNo ):
    '''
        Generate ticketID from eventID, userID, classID, and seatNo
        Input: eventID (str), userID (str), classID (str), seatNo (str)
        Output: ticketID (str)
    '''
    ticketID = eventID + userID + classID + seatNo
    
    #   Check if ticketID already exists
    collection = db['Ticket']
    number = 1
    copyTicketID = ticketID
    while collection.find_one( { 'ticketID' : ticketID }, { '_id' : 0 } ):
        ticketID = copyTicketID + str( number )
        number += 1

    return ticketID

def generate_eventID():
    '''
        Generate eventID
        Input: None
        Output: eventID (str)
    '''
    #   Connect to MongoDB
    collection = db['Events']

    #   Generate eventID
    eventID = 'EV' + str( collection.count_documents( {} ) + 1 ).zfill( 5 )

    number = 2
    #   Check if eventID already exists
    while collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } ):
        eventID = 'EV' + str( collection.count_documents( {} ) + number ).zfill( 5 )
        number += 1

    return eventID

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
        'userID' : user['userID'],
        'email' : user['email'],
        'name' : user['firstName'] + ' ' + user['lastName'],
    }
    
    return userInfo

#   Get User Ticket
@app.get('/user_ticket/{userID}', tags=['Users'])
def get_user_ticket( userID: str ):
    '''
        Get user ticket
        Input: userID (str)
        Output: tickets (list)
    '''

    #   Connect to MongoDB
    user_collection = db['User']
    ticket_collection = db['Ticket']

    #   Check if userID exists
    user = user_collection.find_one( { 'userID' : userID }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'User not found' )
    
    #   Get user ticket
    tickets = list( ticket_collection.find( { 'userID' : userID }, { '_id' : 0 } ) )

    #   Sort tickets by ticket status
    status_order = { 'available' : 0, 'scanned' : 1, 'expired' : 2, 'transferred' : 3 }
    sortedTickets = sorted( tickets, key = lambda i: (status_order[i['status']], i['validDatetime']) )

    return sortedTickets

#   User Edit Profile
@app.post('/update_profile', tags=['Users'])
def user_edit_profile( user_edit_profile: User_Edit_Profile ):
    '''
        User Edit Profile
        Input: user_edit_profile (User_Edit_Profile)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if userID exists
    user = collection.find_one( { 'userID' : user_edit_profile.userID }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'User not found' )
    
    #   Check if email already exists
    if user_edit_profile.newEmail != user['email']:
        if collection.find_one( { 'email' : user_edit_profile.newEmail }, { '_id' : 0 } ):
            raise HTTPException( status_code = 400, detail = 'Email already exists.' )
    
    #   Update user profile
    collection.update_one( { 'userID' : user_edit_profile.userID }, { '$set' : {
        'email' : user_edit_profile.newEmail,
        'firstName' : user_edit_profile.newFirstName,
        'lastName' : user_edit_profile.newLastName,
        'telephoneNumber' : user_edit_profile.newTelephoneNumber,
    } } )

    return { 'result' : 'success' }

#   Get User Profile
@app.get('/profile/{userID}', tags=['Users'])
def get_user_profile( userID: str ):
    '''
        Get user profile
        Input: userID (str)
        Output: userInfo (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if userID exists
    user = collection.find_one( { 'userID' : userID }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'User not found' )
    
    userInfo = {
        'email' : user['email'],
        'firstName' : user['firstName'],
        'lastName' : user['lastName'],
        'telephoneNumber' : user['telephoneNumber'],
    }

    return userInfo

#   Reset Password
@app.post('/reset_password', tags=['Users'])
def user_reset_password( user_reset_password: User_Reset_Password ):
    '''
        User Reset Password
        Input: user_reset_password (User_Reset_Password)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    collection = db['User']

    #   Check if userID exists
    user = collection.find_one( { 'userID' : user_reset_password.userID }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'User not found' )
    
    #   Check if old password is incorrect
    password_hash, _ = hash_password( user_reset_password.oldPassword, user['salt'] )
    if password_hash != user['password_hash']:
        raise HTTPException( status_code = 400, detail = 'Old password is incorrect' )

    #   Hash password
    password_hash, password_salt = hash_password( user_reset_password.newPassword )
    
    #   Update password
    collection.update_one( { 'userID' : user_reset_password.userID }, { '$set' : {
        'password_hash' : password_hash,
        'salt' : password_salt,
    } } )

    return { 'result' : 'success' }

#   Post New Ticket
@app.post('/post_ticket', tags=['Users'])
def post_new_ticket( new_ticket: NewTicket ):
    '''
        Post new ticket
        Input: new_ticket (NewTicket)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    user_collection = db['User']
    event_collection = db['Events']
    ticket_collection = db['Ticket']

    #   Check if userID exists
    user = user_collection.find_one( { 'userID' : new_ticket.userID }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'User not found' )
    
    #   Check if eventID exists
    event = event_collection.find_one( { 'eventID' : new_ticket.eventID }, { '_id' : 0 } )
    if not event:
        raise HTTPException( status_code = 400, detail = 'Event not found' )

    #   Check if wrong ticket class
    for i in range( len( event['ticketClass'] ) ):
        if event['ticketClass'][i]['className'] == new_ticket.className:
            break
        if i == len( event['ticketClass'] ) - 1:
            raise HTTPException( status_code = 400, detail = 'Wrong ticket class' )
        
    #   Check if no seatNo
    if len( new_ticket.seatNo ) == 0:
        raise HTTPException( status_code = 400, detail = 'Please select seat' )
    
    #   Check if ticket amount is enough
    #       Loop find ticketClass
    for ticketClass in event['zoneRevenue']:
        if ticketClass['className'] == new_ticket.className:
            if ticketClass['ticketSold'] + len( new_ticket.seatNo ) > ticketClass['quota']:
                raise HTTPException( status_code = 400, detail = 'Ticket amount is not enough' )
            break

    #   Check if seatNo is already taken or wrong seatNo
    #       Loop find ticketClass
    if new_ticket.seatNo[0] != '':
        for ticketClass in event['ticketClass']:
            if ticketClass['className'] == new_ticket.className:
                for seatNo in new_ticket.seatNo:
                    if seatNo not in ticketClass['seatNo']:
                        raise HTTPException( status_code = 400, detail = f'{seatNo} Seat not found' )
                    if ticketClass['seatNo'][seatNo] != 'vacant':
                        raise HTTPException( status_code = 400, detail = f'{seatNo} Seat already taken' )
                break
    
    #   Loop for each seatNo
    for seatNo in new_ticket.seatNo:

        #   Generate ticketID
        ticketID = generate_ticketID( new_ticket.eventID, new_ticket.userID, new_ticket.className, seatNo )

        #   Insert ticket to database
        newTicket = Ticket(
            ticketID = ticketID,
            validDatetime = event['startDateTime'],
            expiredDatetime = event['endDateTime'],
            status = 'available',
            seatNo = seatNo,
            className = new_ticket.className,
            eventID = new_ticket.eventID,
            userID = new_ticket.userID,
            eventName = event['eventName'],
            eventImage = event['posterImage'],
            location = event['location']
        )
        ticket_collection.insert_one( newTicket.dict() )

    #   Update Event ticketClass
    #       Loop find ticketClass
    for i in range( len( event['ticketClass'] ) ):
        ticketClass = event['ticketClass'][i]
        if ticketClass['className'] == new_ticket.className and new_ticket.seatNo[0] != '':
            for seatNo in new_ticket.seatNo:
                event_collection.update_one( { 'eventID' : new_ticket.eventID }, { '$set' : {
                    f'ticketClass.{i}.seatNo.{seatNo}' : 'available'
                } } )
            break

    #   Update ticket amount
    #       Loop find ticketClass
    totalPrice = 0
    for i in range( len( event['zoneRevenue'] ) ):
        ticketClass = event['zoneRevenue'][i]
        if ticketClass['className'] == new_ticket.className:
            event['zoneRevenue'][i]['ticketSold'] += len( new_ticket.seatNo )
            totalPrice = len( new_ticket.seatNo ) * ticketClass['price']
            break

    #   Update event ticket
    event_collection.update_one( { 'eventID' : new_ticket.eventID }, { '$set' : {
        'soldTicket' : event['soldTicket'] + len( new_ticket.seatNo ),
        'zoneRevenue' : event['zoneRevenue'],
        'totalRevenue' : event['totalRevenue'] + totalPrice
    } } )

    return { 'result' : 'success' }

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

#   Get All Events by Event Organizer
@app.get('/eo_event/{organizerID}', tags=['Event Organizer'])
def get_eo_event( organizerID: str ):
    '''
        Get all events by event organizer
        Input: organizerID (str)
        Output: events (list)
    '''

    #   Connect to MongoDB
    eo_collection = db['EventOrganizer']
    event_collection = db['Events']

    #   Check if organizerID exists
    eo = eo_collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Organizer not found' )
    
    eoName = eo['organizerName']

    #   Get all events
    events = list( event_collection.find( { 'organizerName' : eoName }, { '_id' : 0 } ) )

    status_order = { 'Draft' : 0, 'On-going' : 1, 'Expired' : 2 }

    #   Sort events by status
    sortedEvents = sorted( events, key = lambda i: (status_order[i['eventStatus']], i['startDateTime']) )

    return sortedEvents

#   Get All Ticket Sold by Event Organizer and Event ID
@app.get('/eo_get_all_ticket_sold/{organizerID}/{eventID}', tags=['Event Organizer'])
def get_all_ticket_sold( organizerID: str, eventID: str ):
    '''
        Get all tickets sold by event organizer and eventID
        Input: organizerID (str), eventID (str)
        Output: tickets (list)
    '''

    #   Connect to MongoDB
    eo_collection = db['EventOrganizer']
    event_collection = db['Events']

    #   Check if organizerID exists
    eo = eo_collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Organizer not found' )
    
    #   Check if eventID exists
    event = event_collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } )
    if not event or event['organizerName'] != eo['organizerName']:
        raise HTTPException( status_code = 400, detail = 'Event not found' )
    
    returnDict = {
        'totalRevenue' : event['totalRevenue'],
        'ticketSold' : event['soldTicket'],
        'ticketLeft' : event['totalTicket'] - event['soldTicket'],
    }

    return returnDict

#   Post Create Event by Event Organizer
@app.post('/eo_create_event/{organizerID}', tags=['Event Organizer'])
def post_create_event( organizerID: str ):
    '''
        Post create event by event organizer
        Input: organizerID (str)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    eo_collection = db['EventOrganizer']
    event_collection = db['Events']

    #   Check if organizerID exists
    eo = eo_collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Organizer not found' )

    #   Generate eventID
    eventID = generate_eventID()

    #   Insert event to database
    newEvent = Event(
        eventID = eventID,
        eventName = '',
        startDateTime = datetime.datetime.now(),
        endDateTime = datetime.datetime.now(),
        onSaleDateTime = datetime.datetime.now(),
        endSaleDateTime = datetime.datetime.now(),
        location = '',
        info = '',
        featured = False,
        eventStatus = 'Draft',
        tagName = [],
        posterImage = '',
        seatImage = [],
        organizationName = eo['organizerName'],
        staff = [],
        ticketType = '',
        ticketClass = [],
        organizerName = eo['organizerName'],
        timeStamp = datetime.datetime.now(),
        totalTicket = 0,
        soldTicket = 0,
        totalTicketValue = 0,
        totalRevenue = 0,
        zoneRevenue = [],
        bankAccount = BankAccount(
            bank = '',
            accountName = '',
            accountType = '',
            accountNo = '',
            branch = ''
        )
    )
    event_collection.insert_one( newEvent.dict() )

    return { 'result' : 'success' }

#   Delete Event by Event Organizer and Event ID
@app.delete('/eo_delete_event/{organizerID}/{eventID}', tags=['Event Organizer'])
def delete_event( organizerID: str, eventID: str ):
    '''
        Delete event by event organizer and eventID
        Input: organizerID (str), eventID (str)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    eo_collection = db['EventOrganizer']
    event_collection = db['Events']

    #   Check if organizerID exists
    eo = eo_collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Organizer not found' )
    
    #   Check if eventID exists
    event = event_collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } )
    if not event or event['organizerName'] != eo['organizerName']:
        raise HTTPException( status_code = 400, detail = 'Event not found' )
    
    #   Delete event
    event_collection.delete_one( { 'eventID' : eventID } )

    return { 'result' : 'success' }

#   Get All Staff by Event Organizer and Event ID
@app.get('/eo_get_all_staff/{organizerID}/{eventID}', tags=['Event Organizer'])
def get_all_staff( organizerID: str, eventID: str ):
    '''
        Get all staff by event organizer and eventID
        Input: organizerID (str), eventID (str)
        Output: staffs (list)
    '''

    #   Connect to MongoDB
    eo_collection = db['EventOrganizer']
    event_collection = db['Events']
    user_collection = db['User']

    #   Check if organizerID exists
    eo = eo_collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Organizer not found' )
    
    #   Check if eventID exists
    event = event_collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } )
    if not event or event['organizerName'] != eo['organizerName']:
        raise HTTPException( status_code = 400, detail = 'Event not found' )
    
    staffs = []
    for staff in event['staff']:
        user = user_collection.find_one( { 'userID' : staff }, { '_id' : 0 } )
        staffs.append( user )

    return staffs

#   Add Staff to Event by Event Organizer and Event ID
@app.post('/eo_add_staff/{organizerID}/{eventID}/{staffEmail}', tags=['Event Organizer'])
def add_staff( organizerID: str, eventID: str, staffEmail: str ):
    '''
        Add staff to event by event organizer and eventID
        Input: organizerID (str), eventID (str), staffEmail (str)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    eo_collection = db['EventOrganizer']
    event_collection = db['Events']
    user_collection = db['User']

    #   Check if organizerID exists
    eo = eo_collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Organizer not found' )
    
    #   Check if eventID exists
    event = event_collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } )
    if not event or event['organizerName'] != eo['organizerName']:
        raise HTTPException( status_code = 400, detail = 'Event not found' )
    
    #   Check if staffEmail exists
    user = user_collection.find_one( { 'email' : staffEmail }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'Staff not found' )
    
    #   Check if staff already in event
    if user['userID'] in event['staff']:
        raise HTTPException( status_code = 400, detail = 'Staff already in event' )
    
    #   Add staff to event
    event_collection.update_one( { 'eventID' : eventID }, { '$push' : { 'staff' : user['userID'] } } )

    #   Add event to staff
    user_collection.update_one( { 'email' : staffEmail }, { '$push' : { 'event' : eventID } } )

    return { 'result' : 'success' }

#   Remove Staff from Event by Event Organizer and Event ID
@app.post('/eo_remove_staff/{organizerID}/{eventID}/{staffEmail}', tags=['Event Organizer'])
def remove_staff( organizerID: str, eventID: str, staffEmail: str ):
    '''
        Remove staff from event by event organizer and eventID
        Input: organizerID (str), eventID (str), staffEmail (str)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    eo_collection = db['EventOrganizer']
    event_collection = db['Events']
    user_collection = db['User']

    #   Check if organizerID exists
    eo = eo_collection.find_one( { 'organizerID' : organizerID }, { '_id' : 0 } )
    if not eo:
        raise HTTPException( status_code = 400, detail = 'Organizer not found' )
    
    #   Check if eventID exists
    event = event_collection.find_one( { 'eventID' : eventID }, { '_id' : 0 } )
    if not event or event['organizerName'] != eo['organizerName']:
        raise HTTPException( status_code = 400, detail = 'Event not found' )
    
    #   Check if staffID exists
    user = user_collection.find_one( { 'email' : staffEmail }, { '_id' : 0 } )
    if not user:
        raise HTTPException( status_code = 400, detail = 'Staff not found' )
    
    #   Check if staff not in event
    if user['userID'] not in event['staff']:
        raise HTTPException( status_code = 400, detail = 'Staff not in event' )
    
    #   Remove staff from event
    event_collection.update_one( { 'eventID' : eventID }, { '$pull' : { 'staff' : user['userID'] } } )

    #   Remove event from staff
    user_collection.update_one( { 'email' : staffEmail }, { '$pull' : { 'event' : eventID } } )

    return { 'result' : 'success' }

#   Scan Ticket
@app.post('/scanner/{eventID}/{ticketID}', tags=['Staff'])
def scan_ticket( eventID: str, ticketID: str ):
    '''
        Scan ticket
        Input: eventID (str), ticketID (str)
        Output: result (dict)
    '''

    #   Connect to MongoDB
    collection = db['Ticket']

    #   Check if ticketID exists
    ticket = collection.find_one( { 'ticketID' : ticketID }, { '_id' : 0 } )
    if not ticket:
        raise HTTPException( status_code = 400, detail = 'Ticket not found' )
    
    #   Check if wrong event
    if ticket['eventID'] != eventID:
        raise HTTPException( status_code = 400, detail = 'Wrong event' )
    
    #   Check if ticket is already scanned
    if ticket['status'] == 'scanned':
        raise HTTPException( status_code = 400, detail = 'Ticket already scanned' )
    
    #   Check if ticket is expired
    if ticket['status'] == 'expired':
        raise HTTPException( status_code = 400, detail = 'Ticket expired' )
    
    #   Check if ticket is transferred
    if ticket['status'] == 'transferred':
        raise HTTPException( status_code = 400, detail = 'Ticket transferred' )
    
    #   Update ticket status
    if ticket['status'] == 'available':
        collection.update_one( { 'ticketID' : ticketID }, { '$set' : { 'status' : 'scanned' } } )

    return ticket

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