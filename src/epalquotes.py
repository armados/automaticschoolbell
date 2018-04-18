import os
import random
from pathlib import Path 


def fetchQuotesFromFile():

    quotefile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'quotes.txt')

    if Path(quotefile).is_file() == False:
        return None

    fd = open(quotefile, 'r')
    
    quotes = fd.readlines()

    fd.close()

    quotes = [line.strip() for line in quotes if line.strip()]

    return quotes



def getRandomQuote():
    quotes = fetchQuotesFromFile()
    
    if quotes == None:
        return None

    return random.choice(quotes)

