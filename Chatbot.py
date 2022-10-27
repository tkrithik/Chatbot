

# for speech-to-text
from lib2to3.pgen2.tokenize import tokenize
import speech_recognition as sr

# for text-to-speech
from gtts import gTTS

# for language model
import transformers

import os
import time

# for da
import datetime
import numpy as np

# Building the AI
class ChatBot():
    def __init__(self, name):
        print("----- Starting up", name, "-----")
        self.name = name

    def speech_to_text(self):
        # recognizer = sr.Recognizer()
        # with sr.Microphone() as mic:
        #     print("Listening...")
        #     audio = recognizer.listen(mic)
        #     self.text="ERROR"
        # try:
        #     self.text = recognizer.recognize_google(audio)
        #     print("Me  --> ", self.text)
        # except:
        #     print("Me  -->  ERROR")
        self.text = input("Me -->")
        
            

    @staticmethod
    def text_to_speech(text):
        print("Dev --> ", text)
        speaker = gTTS(text=text, lang="en", slow=False)
        speaker.save("res.mp3")
        statbuf = os.stat("res.mp3")
        mbytes = statbuf.st_size / 1024
        duration = mbytes / 200
        os.system('afplay res.mp3')  #if you are using mac->afplay or else for windows->start
        #os.system("close res.mp3")
        time.sleep(int(50*duration))
        os.remove("res.mp3")
        
        

    def wake_up(self, text):
        return True if self.name in text.lower() else False

    @staticmethod
    def action_time():
        return datetime.datetime.now().time().strftime('%H:%M')
    @staticmethod
    def action_date():
        return datetime.datetime.now().today().strftime("%m/%d/%y")


# Running the AI
if __name__ == "__main__":
    
    ai = ChatBot(name="dev")
    print("Step 2")
    #nlp = transformers.pipeline("conversational", model="microsoft/DialoGPT-medium")
    nlp = transformers.pipeline("conversational", model="facebook/blenderbot-400M-distill")
    print("Step 1")
    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    
    ex = True
    while ex:
        ai.speech_to_text()

        ## wake up
        
        if ai.wake_up(ai.text) is True:
            res = "Hello I am Dave the AI, what can I do for you?"
        
        ## action time
        elif "time" in ai.text:
            res = ai.action_time()

        elif "date" in ai.text:
            res = ai.action_date()
        
        ## respond politely
        elif any(i in ai.text for i in ["thank","thanks"]):
            res = np.random.choice(["you're welcome!","anytime!","no problem!","cool!","I'm here if you need me!","mention not"])
        
        elif any(i in ai.text for i in ["exit","close"]):
            res = np.random.choice(["Have a good day","Bye","Goodbye","Hope to meet soon","peace out!"])
            
            ex = False
        ## conversation
        else:   
            if ai.text=="ERROR":
                res="Sorry, come again?"
            else:
                chat = nlp(transformers.Conversation(ai.text))
                res = str(chat)
                res = res[res.find("bot >> ")+6:].strip()

        ai.text_to_speech(res)
    print("----- Closing down Dev -----")
