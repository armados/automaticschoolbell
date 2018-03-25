from gtts import gTTS
import epalaudio
import tempfile
import logging


def say(language, message):

    logging.info('Say message [%s]' % message)

    file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    
    tts = gTTS(text=message, lang=language)
    
    tts.write_to_fp(file)

    file.close()
    
    return file.name

