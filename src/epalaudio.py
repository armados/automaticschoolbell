import os
import queue
import time
import random
import configparser

from threading import Thread
import threading

import vlc
from vlc import EventType

import logging
import requests


config = configparser.ConfigParser()
config.read('config.ini')

varInitialVolume = config.getint('epalaudio', 'initial_volume')


queuePlaylist = None

vlcInstance = None

player = None

playerBusy = False


queuePlayEvent = threading.Event()





class State:
    PLAYING = 1
    PAUSED = 2
    STOPPED = 3


thread2 = None
thread2start = None
thread2stop = None
maxPlayTime = 0

ueueCurMediaPlay = None


def threadPlayMaxTime(start_event, stop_event):
    global maxPlayTime
    global thread2stop
    global thread2start
    
    while True:
        
        #start_event.wait()
        thread2start.clear()
        thread2start.wait()
        print ("maxtime startted now | max time: %d" % maxPlayTime)
        thread2start.clear()
        #start_event.clear()
        
        countsec = 0
        thread2stop.clear()
        while(not thread2stop.is_set()):
            print ("%d %d" % (countsec, maxPlayTime))
          
            if countsec >= maxPlayTime:
                maxPlayTime = 0
                player.stop()
                #stop_event.set()
                thread2stop.set()
              
            #stop_event.wait(1)
            thread2stop.wait(1)
            countsec = countsec + 1

        print ("end of max thread | max time: %d" % maxPlayTime)


 
def initEpalAudio():

    global queuePlaylist
    queuePlaylist = queue.Queue()

    global vlcInstance
    vlcInstance = vlc.Instance('--no-video')
    
    global player
    player = vlcInstance.media_player_new()
    player.audio_set_volume(varInitialVolume)
    
    global thread2start
    thread2start = threading.Event()
    
    global thread2stop
    thread2stop = threading.Event()
    
    global thread2
    thread2 = threading.Thread(target=threadPlayMaxTime, args=(thread2start, thread2stop))


    
def findmp3files(basepath):
    
    mp3list = []
    
    for root, folders, files in os.walk(basepath):
        if folders:
            continue
        for filename in files:
            if not (filename.endswith('.mp3') or filename.endswith('.MP3')):
                continue
            basename = os.path.basename(root)
            filepath = os.path.join(root, filename)
            mp3list.append(filepath)
            
    return mp3list
    
    
def playMusicDirRandom(dir, randomplay=True, volume=100):

    list = findmp3files(dir)
    
    if randomplay:
        random.shuffle(list)
        
    for filepath in list:
        logging.info("%s" % filepath)
        
        addToPlayQueue(filepath, volume=volume)
    
    
def stopAllAudio():
    logging.info('Stop all audio and clear media queue')
    
    audioQueueClear()
    
    player.stop()


    
def audioQueueClear():
    
    if queuePlaylist.empty():
        logging.info('Queue is empty')
    else:
        logging.info('Clearing current queue')
        
        queuePlaylist.queue.clear()

    
def audioQueuePlayNext():
    
    if queuePlaylist.empty():
        logging.info('Queue is empty')
    else:
        logging.info('Skipping current media from queue')
        
        player.stop()
    


def stepIncreaseVolume():
    logging.info('Increase volume')
 
    curVolume = player.audio_get_volume()
    
    newVolume = curVolume + 5
    
    if newVolume > 100:
        newVolume = 100
 
    logging.info('Change volume level from [%d] to [%d]' % (curVolume, newVolume))
 
    player.audio_set_volume(newVolume)
 

def stepDecreaseVolume():
    logging.info('Decrease volume')
 
    curVolume = player.audio_get_volume()
    
    newVolume = curVolume - 5
    
    if newVolume < 0:
        newVolume = 0
 
    logging.info('Change volume level from [%d] to [%d]' % (curVolume, newVolume))
 
    player.audio_set_volume(newVolume)
   
    
    
def addToPlayQueue(src, volume = 100, maxtime = 0):

    logging.debug('Adding audio [%s] to queue with volume [%d]' % (src, volume))

    clip = dict(src=src, volume=volume, maxtime=maxtime)    

    queuePlaylist.put(clip)
    

    
def playQueue():

    if queuePlaylist.empty():
        logging.info('Cannot play queue, queue is empty')
    else:

        logging.debug('Start playing queue')

        queuePlayEvent.set()
 



def MediaStateChanged(event):
    global playerBusy
    
    playing = set([State.PAUSED, State.PLAYING, State.STOPPED])

    state = player.get_state()

    logging.debug('Callback VLC: state %s ' % state)
    
    #if state in playing:
    #    playerBusy = True
    #else:
    #    playerBusy = False

    
def execQueueListToPlay():
    global playerBusy

    #playing = set([1,2,3,4])
    #playing = set([State.PAUSED, State.PLAYING, State.STOPPED])

    while True:
    
        #while True:
        #    time.sleep(2)
        #    state = playerBell.get_state()
        #    if state not in playing:
        #        break
        print ("playEVENT: ", playerBusy)   
        
        queuePlayEvent.wait()
        queuePlayEvent.clear()

        
        if not playerBusy and not queuePlaylist.empty():
            
            playerBusy = True

            clip = queuePlaylist.get()
            
            media = vlcInstance.media_new(clip.get('src'))
            media.get_mrl()
            media.parse()

            player.set_media(media)
            
            global maxPlayTime
            maxPlayTime = clip.get('maxtime')
                                    
            logging.debug('Starting to play audio [%s]'  % clip.get('src'))
            
            player.play()
                        
            curVolume = player.audio_get_volume()
            logging.debug('Setting volume from [%d] to [%d]' % (curVolume, clip.get('volume')))
            player.audio_set_volume(clip.get('volume'))
    


def cbMediaPlayerPlaying(event):
    logging.debug('CB: MediaPlayerPlaying')
    
    global playerBusy
    playerBusy = True
    
    if maxPlayTime > 0:
        logging.debug('Setting max play time [%d] seconds' % maxPlayTime)
        thread2start.set()

    

def cbMediaPlayerStopped(event):
    logging.debug('CB: MediaPlayerStopped')
    
    thread2stop.set()
    queuePlayEvent.set()

    global playerBusy
    playerBusy = False
    

    

def cbMediaPlayerEndReached(event):
    logging.debug('CB: MediaPlayerEndReached')
    
    thread2stop.set()
    queuePlayEvent.set()

    global playerBusy
    playerBusy = False
    
    

def cbMediaPlayerError(event):
    logging.debug('CB: cbMediaPlayerError detected')
    
    thread2stop.set()
    queuePlayEvent.set()

    global playerBusy
    playerBusy = False

    
def startAudioThread():
 
    initEpalAudio()

    event_manager = player.event_manager()
    
    event_manager.event_attach(EventType.MediaPlayerEndReached, cbMediaPlayerEndReached)    
    event_manager.event_attach(EventType.MediaPlayerStopped, cbMediaPlayerStopped)    
    event_manager.event_attach(EventType.MediaPlayerPlaying, cbMediaPlayerPlaying)    
    event_manager.event_attach(EventType.MediaPlayerEncounteredError , cbMediaPlayerError)    
    
    try:
        thread1 = Thread(target = execQueueListToPlay, args=())
        thread1.start()
     
        #FIXME thread2.start()
        
    except KeyboardInterrupt:
        pass
