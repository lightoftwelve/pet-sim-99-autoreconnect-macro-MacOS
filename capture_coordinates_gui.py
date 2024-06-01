import tkinter as tk
import pyautogui
import configparser
import os
import subprocess
from PIL import Image, ImageTk
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

config_file = os.path.join(os.path.dirname(__file__), "ReconnectionMacroSettings.ini")

# Load existing configuration
config = configparser.ConfigParser()
if os.path.exists(config_file):
    config.read(config_file)
else:
    config['PositionMap'] = {}

class CaptureGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Capture Game Coordinates")

        # Set fixed size for the window
        self.master.geometry("600x1100")
        self.master.resizable(False, False)

        # Set the background color
        self.master.configure(bg='#f5f5f5')

        # Create a frame for the banner and text
        self.top_frame = tk.Frame(self.master, bg='#f5f5f5')
        self.top_frame.pack(fill="x")

        # Create a canvas for the banner and text
        self.canvas = tk.Canvas(self.top_frame, bg='#f5f5f5', highlightthickness=0, height=375)
        self.canvas.pack(fill="x", expand=False)

        # Load the banner image
        self.banner_img = Image.open("images/banner_image.png")
        self.banner_img_resized = self.banner_img.resize((600, 300), Image.LANCZOS)
        self.banner_photo = ImageTk.PhotoImage(self.banner_img_resized)

        # Add the banner image to the canvas
        self.banner_item = self.canvas.create_image(0, 0, anchor="nw", image=self.banner_photo)

        # Add the large FMLY text
        self.fmly_text_bg = self.canvas.create_text(325, 203, anchor="n", text="FMLY", font=("Helvetica", 174), fill="#D8BFD8")
        self.fmly_text = self.canvas.create_text(315, 200, anchor="n", text="FMLY", font=("Helvetica", 172), fill="#734375")

        # Create a frame for the scrollable area
        self.scrollable_frame_container = tk.Frame(self.master, bg='#f5f5f5')
        self.scrollable_frame_container.pack(fill="both", expand=True, padx=75, pady=0)

        # Create a canvas within the frame to enable scrolling
        self.inner_canvas = tk.Canvas(self.scrollable_frame_container, bg='#f5f5f5', highlightthickness=0)
        self.inner_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.scrollable_frame_container, orient="vertical", command=self.inner_canvas.yview, bg='#f5f5f5')
        self.scrollbar.pack(side="right", fill="y")

        self.inner_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create another frame within the inner canvas to hold the actual content
        self.scrollable_frame = tk.Frame(self.inner_canvas, bg='#f5f5f5')
        self.inner_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.inner_canvas.configure(
                scrollregion=self.inner_canvas.bbox("all")
            )
        )

        self.label = tk.Label(self.scrollable_frame, text="Click on the buttons below to capture coordinates:", bg='#f5f5f5', anchor='w')
        self.label.grid(row=0, column=0, columnspan=5, pady=10, sticky='ew')

        # Adding X and Y headers
        tk.Label(self.scrollable_frame, text="X", bg='#f5f5f5').grid(row=1, column=1)
        tk.Label(self.scrollable_frame, text="Y", bg='#f5f5f5').grid(row=1, column=2)

        self.coord_entries_x = {}
        self.coord_entries_y = {}

        self.create_button("Autofarm (Top-Left)", "autofarmtl", "images/autofarm_topleft.png", 2)
        self.create_button("Autofarm (Bottom-Right)", "autofarmbr", "images/autofarm_bottomright.png", 3)
        self.create_button("Disconnect Box (Left Side)", "disconnectedbackgroundleftside", "images/disconnected_left.png", 4)
        self.create_button("Disconnect Box (Right Side)", "disconnectedbackgroundrightside", "images/disconnected_right.png", 5)
        self.create_button("Reconnect Button", "reconnectbutton", "images/reconnect.png", 6)
        self.create_button("Teleport Button", "tpbutton", "images/teleport_button.png", 7)
        self.create_button("Teleport (Top-Left)", "tpbuttontl", "images/teleport_topleft.png", 8)
        self.create_button("Teleport (Bottom-Right)", "tpbuttonbr", "images/teleport_bottomright.png", 9)
        self.create_button("Search Bar", "searchbar", "images/search_bar.png", 10)
        self.create_button("Teleport Button (Middle)", "tpuimiddle", "images/teleport_ui_middle.png", 11)
        self.create_button("X Button", "x", "images/x.png", 12)
        self.create_button("X Button (Bottom-Right)", "xbr", "images/xbr.png", 13)
        self.create_button("X Button (Top Left)", "xtl", "images/xtl.png", 14)

        self.status = tk.Label(self.scrollable_frame, text="", fg="#734375", bg='#f5f5f5', anchor='w')
        self.status.grid(row=15, column=0, columnspan=5, pady=10, sticky='ew')

        self.start_button = tk.Button(self.scrollable_frame, text="Start", command=self.start_script, bg='#f5f5f5')
        self.start_button.grid(row=16, column=0, pady=5, sticky='e')
        
        self.stop_button = tk.Button(self.scrollable_frame, text="Stop", command=self.stop_script, state=tk.DISABLED, bg='#f5f5f5')
        self.stop_button.grid(row=16, column=1, pady=5, sticky='w')

        self.master.bind('<space>', self.toggle_script)

        self.process = None
        self.running = False
        self.paused = False

        # Variable to keep track of the label currently being captured
        self.current_label = None

        self.master.bind_all('<Shift_L>', self.capture_key_press)

    def create_button(self, text, label, icon_path, row):
        frame = tk.Frame(self.scrollable_frame, bg='#f5f5f5')
        frame.grid(row=row, column=0, padx=5, pady=5, sticky='ew')

        button = tk.Button(frame, text=text, command=lambda: self.capture_position(label), bg='#AFEEEE')
        button.pack(side="left")

        coord_entry_x = tk.Entry(self.scrollable_frame, width=5)
        coord_entry_x.grid(row=row, column=1, sticky='w')
        self.coord_entries_x[label] = coord_entry_x

        coord_entry_y = tk.Entry(self.scrollable_frame, width=5)
        coord_entry_y.grid(row=row, column=2, sticky='w')
        self.coord_entries_y[label] = coord_entry_y

        self.show_info_button = tk.Button(frame, text="i", command=lambda: self.show_image(icon_path), bg='#AFEEEE')
        self.show_info_button.pack(side="right")

        # Set default values from the INI file
        if label in config['PositionMap']:
            x, y = map(int, config['PositionMap'][label].split('|'))
            coord_entry_x.insert(0, x)
            coord_entry_y.insert(0, y)

    def show_image(self, icon_path):
        # Create a new window
        popup = tk.Toplevel(self.master)
        popup.title("Image")

        # Load the image
        img = Image.open(icon_path)
        img = ImageTk.PhotoImage(img)

        # Create a label with the image
        img_label = tk.Label(popup, image=img)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack()

    def capture_position(self, label):
        logging.debug(f"Preparing to capture position for {label}")
        self.status.config(text=f"Move mouse to {label} position and press 'Shift' to capture.")
        self.current_label = label  # Set the current label being captured

    def capture_key_press(self, event):
        if self.current_label is not None and event.keysym == 'Shift_L':
            self.save_position()

    def save_position(self):
        if self.current_label is not None:
            x, y = pyautogui.position()
            logging.debug(f"Captured position for {self.current_label}: ({x}, {y})")
            config['PositionMap'][self.current_label] = f"{x}|{y}"
            with open(config_file, 'w') as configfile:
                config.write(configfile)
            logging.info(f"Saved position for {self.current_label} to INI file: ({x}, {y})")
            self.status.config(text=f"Successfully captured {self.current_label} position: ({x}, {y})")
            self.update_coord_entry(self.current_label, x, y)
            self.current_label = None  # Reset the current label

    def update_coord_entry(self, label, x, y):
        self.coord_entries_x[label].delete(0, tk.END)
        self.coord_entries_x[label].insert(0, x)
        self.coord_entries_y[label].delete(0, tk.END)
        self.coord_entries_y[label].insert(0, y)
        logging.debug(f"Updated entry for {label} with position: ({x}, {y})")

    def start_script(self):
        if not self.running:
            self.running = True
            self.process = subprocess.Popen(["python3", "AutoReconnect-Main.py"])
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status.config(text="Script started.")
            logging.info("Script started.")

    def stop_script(self):
        if self.running:
            self.running = False
            self.process.terminate()
            self.process.wait()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status.config(text="Script stopped.")
            logging.info("Script stopped.")

    def toggle_script(self, event=None):
        if self.running:
            if self.paused:
                self.process.send_signal(subprocess.signal.SIGCONT)
                self.paused = False
                self.status.config(text="Script resumed.")
                logging.info("Script resumed.")
            else:
                self.process.send_signal(subprocess.signal.SIGSTOP)
                self.paused = True
                self.status.config(text="Script paused. Press spacebar to resume.")
                logging.info("Script paused.")
        else:
            self.start_script()

def run_gui():
    root = tk.Tk()
    gui = CaptureGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
