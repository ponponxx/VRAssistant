import pyttsx3
import pygame
import threading
import os
import time

    

class TTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ZH-TW_HANHAN_11.0')
        self.engine.setProperty('rate', 125)
        pygame.mixer.init()
        self.playing_thread = None
        self.filename = 'temp'

    def save_to_mp3(self, text):
        if os.path.exists(self.filename):
            self.stop()
        self.engine.save_to_file(text,self.filename)
        self.engine.runAndWait()

    def play(self):
        if self.playing_thread and self.playing_thread.is_alive():
            self.stop(self.filename)
        self.playing_thread = threading.Thread(target=self._play)
        self.playing_thread.start()

    def _play(self):
        pygame.mixer.music.load(self.filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        try:
            os.remove(self.filename)
        except:
            pass
        if self.playing_thread:
            self.playing_thread.join()

    def generate_and_play(self, text):
        self.save_to_mp3(text)
        self.play()

