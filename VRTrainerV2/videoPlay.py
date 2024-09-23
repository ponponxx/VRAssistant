import cv2
import time
from threading import Thread, Event

class VideoPlay:
    def __init__(self):
        self.video_path = None
        self.cap = None
        self.playing_thread = None
        self.start_time = None
        self.end_time = None
        self.stop_event = Event()

    def convert_to_milliseconds(self, time_str):
        h, m, s, ms = map(int, time_str.split(':'))
        return ((h * 3600 + m * 60 + s) * 1000 + ms)

    def set_function(self,video_path, start_time_str, end_time_str):
        self.video_path = 'video/'+video_path
        self.start_time = self.convert_to_milliseconds(start_time_str)
        self.end_time = self.convert_to_milliseconds(end_time_str)

    def play_video(self):
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            self.cap.set(cv2.CAP_PROP_POS_MSEC, self.start_time)

            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                print("Error: Unable to get FPS of the video.")
                return

            frame_duration = 1 / fps
            cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('Video', cv2.WND_PROP_TOPMOST, 1.0)
            cv2.resizeWindow('Video',1440,810)
            cv2.moveWindow('Video',50,150)

            while self.cap.isOpened() and not self.stop_event.is_set():
                ret, frame = self.cap.read()
                if not ret or self.cap.get(cv2.CAP_PROP_POS_MSEC) >= self.end_time:
                    break
                cv2.imshow('Video', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                if cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
                    break

                time.sleep(frame_duration)

        finally:
            self.release_resources()

    def start(self,video_path, start_time_str, end_time_str):
        self.stop()  # Ensure any previous playback is stopped
        self.set_function(video_path ,start_time_str, end_time_str)
        self.stop_event.clear()  # Reset the stop event for new playback
        self.playing_thread = Thread(target=self.play_video)
        self.playing_thread.start()

    def stop(self):
        self.stop_event.set()  # Signal the thread to stop
        if self.playing_thread and self.playing_thread.is_alive():
            self.playing_thread.join()  # Wait for the thread to finish
        self.release_resources()

    def release_resources(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
