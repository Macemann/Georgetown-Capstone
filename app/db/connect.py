import pymongo


def connect ():
    '''
    Create the connection to the MongoDB and create 3 collections needed
    '''
    try:
        # Create the connection to the local host 
        conn = pymongo.MongoClient()
        print 'MongoDB Connection Successful'
    except pymongo.errors.ConnectionFailure, err:
        print 'MongoDB Connection Unsuccessful'
        return False
    
    # This is the name of the database  -'GtownTwitter'
    db = conn['GtownTwitter_PROD']
    return db