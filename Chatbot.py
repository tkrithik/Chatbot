# weather
import requests
import json

# for speech-to-text
import speech_recognition as sr

# for spelling check
from textblob import Word
import re

# for grammer check
import language_tool_python

# for text-to-speech
from gtts import gTTS

# for language model
import transformers

import os
import time

# for data
import os
import datetime
import numpy as np

# fetch a weather forecast from a city
def getweather():
    # get the hyperlink for corrosponding grid from Latitude and longitude
    r1 = requests.get('https://api.weather.gov/points/37.7022,-121.9358')
    r1_j = r1.json()
    link = r1_j['properties']['forecastHourly']
    r = requests.get(link)
    r_j = r.json()
    temperature = r_j['properties']['periods'][0]['temperature']
    shortForecast = r_j['properties']['periods'][0]['shortForecast']
    return shortForecast, temperature



weather_type, temperature = getweather()
#print(weather_type, temperature)


tool = language_tool_python.LanguageTool('en-US')
def check_word_spelling(word):
    word = Word(word)

    result = word.spellcheck()

    if word == result[0][0]:
        # print(f'Spelling of "{word}" is correct!')
        return 0
    else:
        # print(f'Spelling of "{word}" is not correct!')
        # print(f'Correct spelling of "{word}": "{result[0][0]}" (with {result[0][1]} confidence).')
        return 1

def check_sentence_spelling(sentence):
    words = sentence.split()

    words = [word.lower() for word in words]

    words = [re.sub(r'[^A-Za-z0-9]+', '', word) for word in words]
    result = 0
    questionable_word = ''
    for word in words:
        if check_word_spelling(word) != 0:
            result = 1
            questionable_word = word

    return result, questionable_word

# Creating chatbot class
class ChatBot:
    rewrite = 0
    counter = 1
    def __init__(self):
        print("----- Starting up bot -----")

    def conversation(self):
        if self.counter % 8 == 0:
            self.text_to_speech("It is fun talking about movies!")
            self.counter = 0
        elif self.counter % 6 == 0:
            self.text_to_speech("Movie questions are fun!")
        elif self.counter % 3 == 0:
            self.text_to_speech("I am really interested in movies. Let's talk about movies!")

        self.text = input("Me  --> ")
        # check spelling. If there is an error
        # ask user for clarification
        self.rewrite = 0
        if self.rewrite == 0:
            result, questionable_word = check_sentence_spelling(self.text)
            if result == 1:
                while True:
                    print("Dev  --> Could you tell me a little bit about what you mean by \'" + questionable_word + "\'?")
                    self.text = input("Me  --> ")
                    result, questionable_word = check_sentence_spelling(self.text)
                    if result == 0:
                        self.rewrite = 1
                        break
            
        else:
            matches = tool.check(self.text)
            #print(matches)
            while True:
                if len(matches) != 0:
                    print(matches)
                    corrected = language_tool_python.utils.correct(self.text, matches)
                    print("Dev  -> Do you mean \'" + corrected + "\'?")
                    answer = input("Me  --> ")
                    answer = answer.lower()
                    if (answer.find('yes') != -1):
                        self.text = corrected
                        print("Dev  -> Thanks for clarifying")
                        self.rewrite = 0
                        break
                    else:
                        print("Dev  -> Sorry, my mistake. Could you rephrase it again?")
                        self.text = input("Me  --> ")
                        matches = tool.check(self.text)
                        if len(matches) == 0:
                            print("Dev  -> Thanks a lot!")
                            break
                else:
                    break

        self.counter += 1
    def text_to_speech(self, text):
        print("Dev --> ", text)
        speaker = gTTS(text=text, lang="en", slow=False)
        
        speaker.save("res.mp3")
        statbuf = os.stat("res.mp3")
        mbytes = statbuf.st_size / 1024
        duration = mbytes / 200
        os.system('afplay res.mp3')
        os.remove("res.mp3")

    def action_time(self):
        return datetime.datetime.now().time().strftime('%H:%M')


# Running the AI
if __name__ == "__main__":

    ai = ChatBot()
    nlp = transformers.pipeline("conversational", model="facebook/blenderbot-400M-distill")
    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    ex =True
    res = np.random.choice(["Hi, how are you? My name is Chatter." ,"Hello! My name is Chatter." ,"Hello, what do you want to talk about? My name is Chatter." ,"Good afternoon, how can I help you? My name is Chatter."])
    ai.text_to_speech(res)
    while ex:
            
        ai.conversation()

        #time
        if "time" in ai.text:
            res = ai.action_time()
        elif "weather" in ai.text:
            res = "The weather is " + weather_type + " and " + str(temperature) + " degrees."
        # polite responses
        elif any(i in ai.text for i in ["thank" ,"thanks"]):
            res = np.random.choice(["you're welcome!" ,"anytime!" ,"no problem!" ,"cool!" ,"I'm here if you need me!" ,"mention not"])

        elif any(i in ai.text for i in ["exit" ,"close"]):
            res = np.random.choice(["Tata" ,"Have a good day" ,"Bye" ,"Goodbye" ,"Hope to meet soon" ,"peace out!"])

            ex =False
        # conversation
        else:
            if ai.text == "ERROR":
                res ="Sorry, come again?"
            else:
                #print('input to chatbot', ai.text)
                chat = nlp(transformers.Conversation(ai.text))
                res = str(chat)
                #print("Without stripped" + res)
                res = res[res.find("bot >> " ) + 6:].strip()

        ai.text_to_speech(res)
    print("----- Closing down chatbot -----")

