# weather
import python_weather
import asyncio

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
async def getweather():
    async with python_weather.Client(format=python_weather.IMPERIAL) as client:
        weather = await client.get("Dublin")

        # returns the current day's forecast temperature (int)
        return (weather.current.type), (weather.current.temperature)



if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

weather_type, temp = asyncio.run(getweather())
print(weather_type, temp)
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

    def speech_to_text(self):
        # recognizer = sr.Recognizer()
        # with sr.Microphone() as mic:
        #    print("Listening...")
        #    audio = recognizer.listen(mic)
        #    self.text="ERROR"
        # try:
        #    self.text = recognizer.recognize_google(audio)
        #    print("Me  --> ", self.text)
        # except:
        #    print("Me  -->  ERROR")
        
        if self.counter % 8 == 0:
            print("dev  --> It is fun talking about movies!")
        elif self.counter % 6 == 0:
            print("dev  --> Movie questions are fun!")
        elif self.counter % 3 == 0:
            print("dev  --> I am really interested in movies. Let's talk about movies!")

        self.text = input("Me  --> ")
        # check spelling. If there is an error
        # ask user for clarification
        if self.rewrite == 0:
            result, questionable_word = check_sentence_spelling(self.text)
            if result == 1:
                while True:
                    print("Dev  --> Could you tell me a little bit about what do you mean by \'" + questionable_word + "\'?")
                    self.text = input("Me  --> ")
                    result, questionable_word = check_sentence_spelling(self.text)
                    if result == 0:
                        self.rewrite = 1
                        break
        else:
            matches = tool.check(self.text)
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

    @staticmethod
    def text_to_speech(text):
        print("Dev --> ", text)
        speaker = gTTS(text=text, lang="en", slow=False)
        
        # speaker.save("res.mp3")
        # statbuf = os.stat("res.mp3")
        # mbytes = statbuf.st_size / 1024
        # duration = mbytes / 200
        # os.system('start res.mp3')  #if you are using mac->afplay or else for windows->start
        # os.system("close res.mp3")
        # time.sleep(int(50*duration))
        # os.remove("res.mp3")



    def wake_up(self, text):
        return True if self.name in text.lower() else False

    @staticmethod
    def action_time():
        return datetime.datetime.now().time().strftime('%H:%M')


# Running the AI
if __name__ == "__main__":

    ai = ChatBot()
    nlp = transformers.pipeline("conversational", model="facebook/blenderbot-400M-distill")
    os.environ["TOKENIZERS_PARALLELISM"] = "true"

    ex =True
    while ex:
        ai.speech_to_text()

        ## action time
        if "time" in ai.text:
            res = ai.action_time()

        ## respond politely
        elif any(i in ai.text for i in ["thank" ,"thanks"]):
            res = np.random.choice \
                (["you're welcome!" ,"anytime!" ,"no problem!" ,"cool!" ,"I'm here if you need me!" ,"mention not"])

        elif any(i in ai.text for i in ["exit" ,"close"]):
            res = np.random.choice(["Tata" ,"Have a good day" ,"Bye" ,"Goodbye" ,"Hope to meet soon" ,"peace out!"])

            ex =False
        ## conversation
        else:
            if ai.text == "ERROR":
                res ="Sorry, come again?"
            else:
                #print('input to chatbot', ai.text)
                #chat = nlp(transformers.Conversation(ai.text), pad_token_id=50256)
                chat = nlp(transformers.Conversation(ai.text))
                res = str(chat)
                res = res[res.find("bot >> " ) +6:].strip()

        ai.text_to_speech(res)
    print("----- Closing down chatbot -----")

