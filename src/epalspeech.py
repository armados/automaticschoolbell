from gtts import gTTS
import tempfile
import time
import logging


def createAudioFileFromText(language, message):

    logging.info('Generate TTS audio file with text [%s]' % message)

    namePrefix = time.strftime("tts-%Y-%m-%d-%H-%M-%S-")
    nameSuffix = '.mp3'
    
    tmpfile = tempfile.NamedTemporaryFile(prefix=namePrefix, suffix=nameSuffix, delete=False)
    
    tts = gTTS(text=message, lang=language)
    
    tts.write_to_fp(tmpfile)

    tmpfile.close()
    
    return tmpfile.name

