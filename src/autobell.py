import logging
from threading import Thread
from datetime import datetime
import time
import configparser

import epalaudio
import epalspeech


config = configparser.ConfigParser()
config.read('config.ini')

varBellAutoMode = config.getboolean('autobell', 'autobell_enabled')
varPlayMusicAtBreak = config.getboolean('autobell', 'music_on_brake')

varSayTimeBeforeAfterBell = config.getboolean('autobell', 'saytime_enabled')

varSoundEffectAnnouncement = config.get('autobell', 'saytime_audio_file')

bellSoundFilename = config.get('autobell', 'autobell_audio_file')





def bellRingNow():
    logging.debug('Ring now...')
    
    epalaudio.stopAllAudio()
    
    epalaudio.play(src=bellSoundFilename, volume=100)
    bellRing('period-2', 'end')


def bellRing(msg1=None, msg2=None):
    logging.debug('Action: Its time to ring the bell. Start ringing...')
    logging.debug('Message is: %s and %s' % (msg1, msg2))

    timefilename = None
    
    if varSayTimeBeforeAfterBell == True:
                    
        if msg2 == "start":
            if msg1 == "period-1":
                str="Η ώρα είναι " + time.strftime("%H:%M") +". Καλή σας μέρα και καλό μάθημα."                
            elif msg1 == "period-7":
                str="Η ώρα είναι " + time.strftime("%H:%M") +". Αλλαγή διδακτικής ώρας χωρίς διάλειμμα. Καλό μάθημα."
            else:
                str="Η ώρα είναι " + time.strftime("%H:%M") +". Καλό μάθημα."
        elif msg2 == "end":
            if msg1 != "period-7":
                str="Η ώρα είναι " + time.strftime("%H:%M") +". Καλό διάλειμμα."
            else:
                str="Η ώρα είναι " + time.strftime("%H:%M") +". Τέλος μαθημάτων. Σας εύχομαι καλό μεσημέρι και καλό διάβασμα."
        
        timefilename = epalspeech.say('el', str)

    epalaudio.stopAllAudio()

    epalaudio.play(src=bellSoundFilename, volume=100)
        
    if varSayTimeBeforeAfterBell == True:
        epalaudio.play(src=varSoundEffectAnnouncement, volume=60)
        epalaudio.play(src=timefilename, volume=60)
        
    if varPlayMusicAtBreak == True:
        if msg2 == "end" and msg1 in ['period-2', 'period-3','period-4', 'period-5']:
            epalaudio.playMusicDirRandom(dir='../music2', volume=30)

        
        
        
        

def bellAutoRingDefaultSchedule():
        
    schoolBellDaysList = (0,1,2,3,4)
    
    while True:
        # sleep until the next minute
        t = datetime.now()
        sleeptime = 60 - (t.second + t.microsecond/1000000.0)
        time.sleep(sleeptime)

        timeCurrentHHMM = datetime.now().strftime('%H:%M')
        timeCurrentWeekday = datetime.today().weekday()
                
        logging.debug('Time: %s | AutoBellMode: %s | PlayMusicAtBreak: %s' % (timeCurrentHHMM, varBellAutoMode, varPlayMusicAtBreak))

        if (varBellAutoMode == True) and (timeCurrentWeekday in schoolBellDaysList):
        
            if   (timeCurrentHHMM == '08:30'):
                bellRing('period-1', 'start')
            elif (timeCurrentHHMM == '09:10'):
                bellRing('period-1', 'end')
            elif (timeCurrentHHMM == '09:15'):
                bellRing('period-2', 'start')
            elif (timeCurrentHHMM == '09:55'):
                bellRing('period-2', 'end')
            elif (timeCurrentHHMM == '10:05'):
                bellRing('period-3', 'start')
            elif (timeCurrentHHMM == '10:45'):
                bellRing('period-3', 'end')
            elif (timeCurrentHHMM == '10:50'):
                bellRing('period-4', 'start')
            elif (timeCurrentHHMM == '11:30'):
                bellRing('period-4', 'end')
            elif (timeCurrentHHMM == '11:35'):
                bellRing('period-5', 'start')
            elif (timeCurrentHHMM == '12:15'):
                bellRing('period-5', 'end')
            elif (timeCurrentHHMM == '12:20'):
                bellRing('period-6', 'start')
            elif (timeCurrentHHMM == '13:00'):
                bellRing('period-7', 'start')
            elif (timeCurrentHHMM == '13:40'):
                bellRing('period-7', 'end')



def setBellAutoMode(status):
    global varBellAutoMode
    varBellAutoMode = status 


def getBellAutoMode():
    return varBellAutoMode 


def setPlayMusicAtBreak(status):
    global varPlayMusicAtBreak
    varPlayMusicAtBreak = status 


def getPlayMusicAtBreak():
    return varPlayMusicAtBreak 
    

def setSayTimeBeforeAfterBell(status):
    global varSayTimeBeforeAfterBell
    varSayTimeBeforeAfterBell = status 


def getSayTimeBeforeAfterBell():
    return varSayTimeBeforeAfterBell 
    
    

def startAutoBellThread():
        
    try:
        t = Thread(target=bellAutoRingDefaultSchedule, args=())
        t.start()
     
    except KeyboardInterrupt:
        pass
