import speech_recognition as sr
import os
import telebot
import requests
import subprocess
import datetime

logfile = str(datetime.date.today()) + '.log'
token = 'TOKEN_BOT'
bot = telebot.TeleBot(token)


def audio_to_text(dest_name: str):
    r = sr.Recognizer()
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    try:
        print("Started recognition...")
        file_info = bot.get_file(message.voice.file_id)
        path = os.path.splitext(file_info.file_path)[0]
        file_name = os.path.basename(path)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
        
        with open(file_name + '.oga', 'wb') as f:
            f.write(doc.content)  # save audio message
        process = subprocess.run(['ffmpeg', '-i', file_name + '.oga', file_name + '.wav'])
        result = audio_to_text(file_name + '.wav')
        bot.send_message(message.chat.id, format(result))
        
    except sr.UnknownValueError as e:
        bot.send_message(message.chat.id, "Не разобрал сообщение...")
        
        with open(logfile, 'a', encoding='utf-8') as f:  # save audio
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':Message is empty.\n')
            
    except Exception as e:  # wrong, if speech was don't understand
        bot.send_message(message.chat.id, "Упс, ошибка")
        
        with open(logfile, 'a', encoding='utf-8') as f:  # if any other problem
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':' + str(e) + '\n')
            
    finally:  # deleting temporary files
        os.remove(file_name + '.wav')
        os.remove(file_name + '.oga')


bot.polling(none_stop=True, interval=0)
