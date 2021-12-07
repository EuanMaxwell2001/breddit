class config(object):
    DEBUG = False
    TESTING = False

    db_username = 'b3322b067b460c'
    db_password = '225bfff4'
    db_host     = 'us-cdbr-east-04.cleardb.com'
    db_db       = 'heroku_6ac55aa9e840c72'

    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(db_username,
                                                           db_password,
                                                           db_host,
                                                           db_db)

class productionconfig(config):
    pass

class developmentconfig(config):
    DEBUG = True