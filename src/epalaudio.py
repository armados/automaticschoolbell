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


playerBusy = False


class State:
    PLAYING = 1
    PAUSED = 2
    STOPPED = 3


maxPlayTime = 0



queuePlaylist = queue.Queue()

#define VLC instance
vlcInstance = vlc.Instance('--no-xlib') #--quiet --verbose 3

#Define VLC player
player = vlcInstance.media_player_new()
#player.stop()

thread2start = threading.Event()
thread2stop = threading.Event()
    
queuePlayEvent = threading.Event()




def threadPlayMaxTime():
    global maxPlayTime
    global thread2stop
    global thread2start
    
    while True:
        
        thread2start.clear()
        thread2start.wait()
        #print ("maxtime startted now | max time: %d" % maxPlayTime)
        thread2start.clear()
        
        countsec = 0
        thread2stop.clear()
        while(not thread2stop.is_set()):
            print ("%d %d" % (countsec, maxPlayTime))
          
            if countsec >= maxPlayTime:
                maxPlayTime = 0
                player.stop()
                thread2stop.set()
              
            thread2stop.wait(1)
            countsec = countsec + 1


    
def findmp3files(path, recursive=True):
    
    mp3list = []

    if recursive == True:
            
        for root, folders, files in os.walk(path):
            for filename in files:
                if not (filename.endswith('.mp3') or filename.endswith('.MP3')):
                    continue
                basename = os.path.basename(root)
                filepath = os.path.join(root, filename)
                mp3list.append(filepath)

    else:
        
        for filename in os.listdir(path):
            if not (filename.endswith('.mp3') or filename.endswith('.MP3')):
                continue
            filepath = os.path.join(path, filename)
            mp3list.append(filepath)
        
    return mp3list
    
    
    
def playMusicDirRandom(dir, randomplay=True, volume=100):

    list = findmp3files(dir,recursive=True)
    
    if randomplay:
        random.shuffle(list)
        
    for filepath in list:
        addToPlayQueue(filepath, volume=volume)
        #logging.info("Audio clip in list [%s]" % filepath)
        
    
    
def stopAllAudio():
    logging.info('Stop player and clear media queue')
    
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
 
    curVolume = player.audio_get_volume()
    
    newVolume = curVolume + 5
    
    if newVolume > 100:
        newVolume = 100
 
    logging.info('Increase volume level from [%d] to [%d]' % (curVolume, newVolume))
 
    player.audio_set_volume(newVolume)
 

def stepDecreaseVolume():
 
    curVolume = player.audio_get_volume()
    
    newVolume = curVolume - 5
    
    if newVolume < 0:
        newVolume = 0
 
    logging.info('Decrease volume level from [%d] to [%d]' % (curVolume, newVolume))
 
    player.audio_set_volume(newVolume)
   
    
    
def addToPlayQueue(src, volume = 100, maxtime = 0):

    logging.debug('Added audio [%s] to queue with volume [%d]' % (src, volume))

    clip = dict(src=src, volume=volume, maxtime=maxtime)    

    queuePlaylist.put(clip)
    

    
def playQueue():

    if queuePlaylist.empty():
        logging.info('Cannot play queue, queue is empty')
    else:

        logging.debug('Playing queue now')

        queuePlayEvent.set()
 


    
def execQueueListToPlay():
    global playerBusy

    playing = set([1,2,3,4])
    #playing = set([State.PAUSED, State.PLAYING, State.STOPPED])

    while True:
    
        #while True:
        #    time.sleep(2)
        #    state = playerBell.get_state()
        #    if state not in playing:
        #        break
        
        
        queuePlayEvent.wait()
        queuePlayEvent.clear()

        #logging.debug('execQueueListToPlay() received ThreadEvent to play queue')

        time.sleep(0.2)
        
        state = player.get_state()
        
        if (state not in playing) and (not queuePlaylist.empty()):
            
            playerBusy = True

            clip = queuePlaylist.get()
            
            media = vlcInstance.media_new(clip.get('src'))
            media.get_mrl()
            media.parse()
                             
            player.set_media(media)
            
            player.play()
                                                            
            logging.debug('Now playing audio [%s]'  % clip.get('src'))

            if media.get_duration() == -1:
                logging.debug('Media duration: [unknown]')
            else:
                seconds = media.get_duration() / 1000
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                logging.debug('Media duration: [%d:%02d:%02d]' % (h, m, s))
            
            # required to set player volume
            # time.sleep(0.1)
            
            #logging.debug('Setting volume to [%d]' % clip.get('volume'))
            
            while player.get_state() in playing and player.audio_get_volume() != clip.get('volume'):
                player.audio_set_volume(clip.get('volume'))
            player.audio_set_volume(clip.get('volume'))
            logging.debug('Volume has been set to [%d]' % clip.get('volume'))


            global maxPlayTime
            maxPlayTime = clip.get('maxtime')
            
            if maxPlayTime > 0:
                logging.debug('Setting max play time [%d] seconds' % maxPlayTime)
                thread2start.set()


def cbMediaPlayerPlaying(event):
    #logging.debug('CB: MediaPlayerPlaying')
    
    global playerBusy
    playerBusy = True
    

def cbMediaPlayerStopped(event):
    #logging.debug('CB: MediaPlayerStopped')
    
    thread2stop.set()
    queuePlayEvent.set()

    global playerBusy
    playerBusy = False
    

def cbMediaPlayerEndReached(event):
    #logging.debug('CB: MediaPlayerEndReached')
    
    thread2stop.set()
    queuePlayEvent.set()

    global playerBusy
    playerBusy = False
    

def cbMediaPlayerError(event):
    #logging.debug('CB: cbMediaPlayerError detected')
    
    thread2stop.set()
    queuePlayEvent.set()

    global playerBusy
    playerBusy = False

   
    
def startAudioThread():

    event_manager = player.event_manager()
    
    event_manager.event_attach(EventType.MediaPlayerPlaying, cbMediaPlayerPlaying)    
    event_manager.event_attach(EventType.MediaPlayerStopped, cbMediaPlayerStopped)    
    event_manager.event_attach(EventType.MediaPlayerEndReached, cbMediaPlayerEndReached)    
    event_manager.event_attach(EventType.MediaPlayerEncounteredError , cbMediaPlayerError)    
    
    try:
        thread1 = Thread(target = execQueueListToPlay, args=())
        thread1.start()
     
        thread2 = threading.Thread(target=threadPlayMaxTime, args=())
        thread2.start()
        
    except KeyboardInterrupt:
        pass
