import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import time
from threading import Thread
from TTS import TTS
from videoPlay import VideoPlay
from threading import Thread, Event

class VRAApp:
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.title("VRA Program")
        self.root.attributes('-topmost', True)  # Keep window on top
        self.root.geometry("500x400")

        self.videoplaytime_path = 'videoplaytime.csv'
        self.df = pd.read_csv(self.videoplaytime_path)
        self.unique_categories = self.df['Type'].unique()  # Extract unique categories
        self.subcategories = self.df.groupby('Type')['Cat'].unique().to_dict()

        self.TTS = TTS()
        self.video_play = VideoPlay()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Initialize pages based on unique categories
        self.initialize_pages()

        #self.create_buttons()
        #self.step_index = 0
        self.paused = False

    def initialize_pages(self):
        for category in self.unique_categories:
            # Create a CategoryPage frame for each main category
            category_page = CategoryPage(self.notebook, category, self.df, self.TTS, self.video_play)
            
            # Add the CategoryPage to the main notebook
            self.notebook.add(category_page, text=category)
    
    def initialize_sub_page(self, frame, category, subcat):
        # Example content: You can customize this as needed
        label = ttk.Label(frame, text=f"Content for {category} - {subcat}")
        label.pack(padx=20, pady=20)
        


    def create_instruction_square(self):
        self.square_frame = tk.Frame(self.root, width=200, height=200, bg="lightblue", bd=5, relief="sunken")
        self.square_frame.pack(side=tk.RIGHT, padx=10, pady=10)

class CategoryPage(tk.Frame):
    def __init__(self, parent, category, df, tts, video_play):
        super().__init__(parent)
        self.category = category
        self.df = df
        self.TTS = tts
        self.video_play = video_play

        # Create the sub-notebook within this category page
        self.sub_notebook = ttk.Notebook(self)
        self.sub_notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Get subcategories for this main category
        subs = self.df[self.df['Type'] == self.category]['Cat'].unique()

        for subcat in subs:
            sub_page = SubCategoryPage(self.sub_notebook, self.category, subcat, self.df, self.TTS, self.video_play)
            self.sub_notebook.add(sub_page, text=subcat)


class SubCategoryPage(tk.Frame):
    def __init__(self, parent, category, subcategory, df, tts, video_play):
        super().__init__(parent)
        self.category = category
        self.subcategory = subcategory
        self.df = df
        self.TTS = tts
        self.video_play = video_play

        # Create sections and buttons within the subcategory page
        self.create_sections()

    def create_sections(self):
        # Create two separate frames for sections
        section1_frame = tk.LabelFrame(self, text="操作流程", bd=2, relief="groove")
        section1_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

        section2_frame = tk.LabelFrame(self, text="功能細節", bd=2, relief="groove")
        section2_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

        # Filter functions by category, subcategory, and section
        section1_df = self.df[(self.df['Type'] == self.category) & 
                               (self.df['Cat'] == self.subcategory) & 
                               (self.df['Sec'] == 1)]
        section2_df = self.df[(self.df['Type'] == self.category) & 
                               (self.df['Cat'] == self.subcategory) & 
                               (self.df['Sec'] == 2)]

        # Create buttons for Section 1
        self.create_buttons(section1_frame, section1_df)

        # Create buttons for Section 2
        self.create_buttons(section2_frame, section2_df)


    def create_buttons(self, frame, filtered_df):
        functions = filtered_df['function_name'].tolist()

        num_columns = 4

        for col in range(num_columns):
            frame.grid_columnconfigure(col, weight=1)

        for idx, func in enumerate(functions):
            row = idx // num_columns  # Adjust this number for more/less buttons per row
            col = idx % num_columns
            btn = tk.Button(frame, text=func, command=lambda f=func: self.activate_function(f), width=15, height=2, wraplength=100, anchor='center')
            btn.grid(row=row, column=col, padx=5, pady=5 , sticky = 'n')

        frame.grid_rowconfigure(len(functions) // num_columns + 1, weight=1)

    def activate_function(self, function_name):
        #messagebox.showinfo("Function Activated", f"{function_name} is activated.")
        self.stop_function()
        # Retrieve the corresponding data from the dataframe
        row = self.df[self.df['function_name'] == function_name].iloc[0]
        text = row['TTScontent']
        start_time = row['start_time']
        end_time = row['end_time']
        video_path = row['video_path']
        
        # Play the TTS content and video
        self.TTS.generate_and_play(text)
        self.video_play.start(video_path, start_time, end_time)
        monitor_thread = Thread(target=self.monitor_video)
        monitor_thread.start()

    def monitor_video(self):
        # Monitor video thread and stop audio if video is done
        self.video_play.playing_thread.join()  # Wait until video thread finishes
        self.TTS.stop()  # Stop audio if it is still playing

    def stop_function(self):
        self.TTS.stop()
        self.video_play.stop()
        print("Stopping function")


if __name__ == "__main__":
    root = tk.Tk()
    app = VRAApp(root)
    root.mainloop()
