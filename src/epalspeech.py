from gtts import gTTS
import epalaudio
import tempfile
import logging


def say(language, message):

    logging.info('Generate TTS audio file with text [%s]' % message)

    tmpfile = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    
    tts = gTTS(text=message, lang=language)
    
    tts.write_to_fp(tmpfile)

    tmpfile.close()
    
    return tmpfile.name

