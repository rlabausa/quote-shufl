#!/path/to/python/virtual/env

# standard libs
import os
import getpass
import random
import textwrap
import configparser
import logging

# third-party libs
import psycopg2
import pyfiglet

def load_ini(filename):
    '''
    Parses INI file to a dictionary. This function assumes that there are one or more sections in the INI file with unique parameter names.

    Args:
        filename (str): INI configuration file path
    
    Returns:
        ini_params (dict): dictionary containing INI configuration parameters
    '''
    # initialize dict to store config params
    ini_params ={}

    # read contents of the config file
    parser = configparser.ConfigParser()
    parser.read(filename)
    
    # get list of sections stored in INI file and iterate through each
    sections = parser.sections()

    for section in sections:
        # get list of params stored in the section
        params = parser.items(section)

        # store params as key-value pairs
        for param in params:
            ini_params[param[0]] = param[1]
    
    return ini_params

def greet_user(quote, source):
    '''
    Greets the current user with a welcome message and a quote

    Args:
        quote (str): desired quote or message to display
        source (str): author of the quote
    
    Returns:
        None
    '''
    # print greeting message for current user (with some additional formatting)
    username = getpass.getuser()
    terminal = os.get_terminal_size()

    message = f'hello, {username}!'

    print('-' * terminal.columns)
    print('+' * terminal.columns)
    print('-' * terminal.columns)
    print()

    print(pyfiglet.figlet_format(message, font='slant', justify='center', width=terminal.columns))

    print()
    print('-' * terminal.columns)
    print('+' * terminal.columns)
    print('-' * terminal.columns)
    print('\n' * 3)

    # print selected quote line-by-line
    quote_wrap = textwrap.wrap(quote)

    for i in range(len(quote_wrap)):
        print(quote_wrap[i].center(terminal.columns))
    
    print(f'\n{source.center(terminal.columns)}')

    # terminate program after keypress
    input('')


def main():
    # set variable for db conn and cursor
    conn = None
    cur = None

    try:
        # set up logging
        logging.basicConfig(
            filename='quote_shufl.log',
            level=logging.DEBUG,
            format='%(levelname)s: %(asctime)s %(message)s',
            datefmt='%m/%d/%Y %H:%M:%S'
        )

        # load db config params
        args = load_ini('conf/db.ini')

        # open connection to db
        conn = psycopg2.connect(**args)

        # open cursor to perform db ops
        cur = conn.cursor()

        # execute query on db to pull a random record from the quote table
        cur.execute(
            """
            SELECT
                body,
                source
            FROM
                quote
            OFFSET
                floor(random() * (SELECT COUNT(id) FROM quote))
            LIMIT 1;
            """
        )

        # fetch the result of the above query
        record = cur.fetchone()
        logging.debug('query result = ' + str(record))

        # display welcome message
        greet_user(record[0], record[1])

    except(Exception) as e:
        # TODO clean up error handling and logging
        logging.error(e)
        print(e)
        
    finally:
        # close existing cursor
        if(cur):
            cur.close()
            logging.debug('cursor closed.')

        # close existing db connection
        if(conn):
            conn.close()
            logging.debug('connection closed.')

if __name__ == '__main__':
    main()