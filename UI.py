import math

import os, subprocess

from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter import filedialog
from tkinter import messagebox as mb

import sched, time
scheduler = sched.scheduler(time.time, time.sleep)
pic_event = scheduler.enter(1,1,print("Startup..."))
scheduler.cancel(pic_event)
import threading
is_running = False

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)

import email_notification

import pyrebase
firebaseConfig = {
    'apiKey': "Removed due to security reasons",
    'authDomain': "piculturecam.firebaseapp.com",
    'databaseURL': "https://piculturecam-default-rtdb.firebaseio.com",
    'projectId': "piculturecam",
    'storageBucket': "piculturecam.appspot.com",
    'messagingSenderId': "902194219220",
    'appId': "1:902194219220:web:9d6cd77416bddaa3ea5341"
}
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

unit_options = [
    "Seconds",
    "Minutes",
    "Hours",
    "Days"
]

shutter_options = [
    "1/2",
    "1/4",
    "1/8",
    "1/15",
    "1/30",
    "1/60",
    "1/80",
    "1/100",
    "1/125",
    "1/250",
    "1/500"
]

def preview():
    
    settings = get_settings()
    GPIO.output(18, GPIO.HIGH)
    subprocess.run(["libcamera-still", "-o", "preview.jpg"] + settings)
    GPIO.output(18, GPIO.LOW)
    preview_image = Image.open("preview.jpg")
    width, height = preview_image.size
    preview_image = preview_image.resize((width // 5, height // 5))
    tkimage = ImageTk.PhotoImage(preview_image)
    panel1.configure(image=tkimage)
    panel1.image = tkimage

def dur_iit_error_check(input):
    
    max_digits = 9;
    
    if(len(input) <= max_digits):
        if(input.isdigit() and float(input) > 0):
            return True            
        elif(input == ""):
            return True
        else:
            return False
    else:
        return False
    
def exp_name_error_check(input):
    
    max_length = 40;
    
    if(len(input) <= max_length):
        if(input.find(".") == -1 and
           input.find("\\") == -1 and
           input.find("/") == -1):
            return True            
        elif(input == ""):
            return True
        else:
            return False
    else:
        return False

def get_folder_path():
    
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)
    
def update_progress_label_percent():
    
    return f"Current Progress: {round(pb['value'],3)}%"

def update_progress_label_frac():
    
    total = total_pics.get()
    num = math.ceil(total*(pb['value']/100))
    return f"({num}/{total})"

def update_message():
    
    return message_text.get()

def warn_change(_):

    message_text.set("A setting has been modified. Please press Preview to see changes.")
    
def start_button_pressed():
    
    if(folder_path.get() != "" and
       duration.get() != "" and
       inter_image_time.get() != ""):
        open_run_window()
        t = threading.Thread(target=start)
        t.start()
    else:
        print("Missing Inputs")

def start():
    
    dur = float(duration.get())
    iit = float(inter_image_time.get())
    dur_units = duration_units.get()
    iit_units = inter_image_time_units.get()
    
    path = folder_path.get() + "/" + exp_name.get()
    if (not os.path.exists(path)):
        os.makedirs(path)
    
    settings = get_settings()
    
    if(dur_units == unit_options[1]):
        dur = dur * 60
    elif(dur_units == unit_options[2]):
        dur = dur * 60 * 60
    elif(dur_units == unit_options[3]):
        dur = dur * 60 * 60 * 24
    
    if(iit_units == unit_options[1]):
        iit = iit * 60
    elif(iit_units == unit_options[2]):
        iit = iit * 60 * 60
    elif(iit_units == unit_options[3]):
        iit = iit * 60 * 60 * 24
        
    total_images = calculator(dur, iit)
    total_pics.set(total_images)
    pb_label_frac['text'] = update_progress_label_frac()
    
    global is_running
    is_running = True
    periodic(scheduler, iit, take_pic, total_images, actionargs=(settings,path))
    scheduler.run()
    is_running = False
    time.sleep(3)
    cancel()
    
def open_run_window():
    
    root.withdraw()
    run_window.deiconify()

def cancel():
    
    if(is_running):
        res = mb.askquestion('Cancel Run', 'Do you really want to cancel?') 
        if(res == 'yes'): 
            return_to_settings()
        else: 
            mb.showinfo('Return', 'Press OK')
    else:
        return_to_settings()
        
def return_to_settings():
    
    global is_running
    is_running = False
    if(not scheduler.empty()):
        scheduler.cancel(pic_event)
    pb['value'] = 0
    pb_label_percent['text'] = update_progress_label_percent()
    pb_label_frac['text'] = update_progress_label_frac()
    root.deiconify()
    run_window.withdraw() 

def get_roi_params():
    
    N = 2*max_zoom_level + 1
    z = zoom_level.get()
    x = z/N
    y = x
    w = 1-2*x
    h = w
    return str(x)+","+str(y)+","+str(w)+","+str(h)

def get_settings():
    
    timeout_time = "500"
    
    ss = shutter_speed.get()
    num, den = ss.split('/')
    shutter = (float(num)/float(den))*(10e5)
    
    settings = ["-n",
                "-t",timeout_time,
                "--roi",get_roi_params(),
                "--sharpness",str(sharpness_level.get()),
                "--contrast",str(contrast_level.get()),
                "--brightness",str(brightness_level.get()),
                "--shutter",str(shutter)]
    
    if(v_flip.get()):
        settings.append("--vflip")
    if(h_flip.get()):
        settings.append("--hflip")
    
    print(settings)
    return settings

def calculator(duration, inter_image_time):

    total_images = math.floor(duration/inter_image_time)
        
    print("Commencing to capture " + str(total_images) + " Images")
    return total_images

def periodic(scheduler, interval, action, reps, rep_num = 0, actionargs=()):
        
    rep_num += 1
    if(rep_num <= reps and is_running):
        global pic_event
        pic_event = scheduler.enter(interval, 1, periodic,
                                    (scheduler, interval, action, reps, rep_num, actionargs))
    if(rep_num > 1): 
        action(*actionargs)
        pb['value'] += (1/reps)*100
        pb_label_percent['text'] = update_progress_label_percent()
        pb_label_frac['text'] = update_progress_label_frac()
   
def take_pic(settings,path):
    
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = path + f"/{timestamp}.jpg"
    GPIO.output(18, GPIO.HIGH)
    subprocess.run(["libcamera-still", "-o", filename] + settings)
    GPIO.output(18, GPIO.LOW)
    if(use_firebase.get()):
        fb_path = exp_name.get() + f"/{timestamp}.jpg"
        storage.child(fb_path).put(filename)
    email_notification.notify(timestamp,exp_name.get())

#######################################################################
# Settings Window Setup

root = Tk()
root.title("Imaging Settings")
root.minsize(1400, 500)
setting_frame = ttk.Frame(root, padding="3 3 12 12")
setting_frame.grid(column=0, row=0, sticky=(N, W, E, S))
preview_frame = ttk.Frame(root, padding="3 3 12 12")
preview_frame.grid(column=1, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

s_frame_entry = ttk.Frame(setting_frame, padding="3 3 12 12")
s_frame_entry.grid(column=0, row=0, sticky=(N, W, E, S))
s_frame_sliders = ttk.Frame(setting_frame, padding="3 3 12 12")
s_frame_sliders.grid(column=0, row=1, sticky=(N, W, E, S))
s_frame_toggles = ttk.Frame(setting_frame, padding="3 3 12 12")
s_frame_toggles.grid(column=0, row=2, sticky=(N, W, E, S))
s_frame_message = ttk.Frame(setting_frame, padding="3 3 12 12")
s_frame_message.grid(column=0, row=3, sticky=(N, W, E, S))
s_frame_buttons = ttk.Frame(setting_frame, padding="3 3 12 12")
s_frame_buttons.grid(column=0, row=4, sticky=(N, E, S))

#######################################################################
# Naming Experiment and Firebase Toggle

exp_name = StringVar()
exp_name.set("My New Experiment")

ttk.Label(s_frame_entry, text="Experiment Name: ").grid(column=1, row=1, sticky=W, pady=5)

exp_name_reg = s_frame_entry.register(exp_name_error_check)
exp_name_entry = ttk.Entry(s_frame_entry, textvariable=exp_name, validate="key", validatecommand=(exp_name_reg, '%P'))
exp_name_entry.grid(column=2, row=1, sticky=(W, E), pady=5)

use_firebase = BooleanVar()
firebase_button = Checkbutton(s_frame_entry,
                              text = "Use Firebase",
                              variable = use_firebase,
                              onvalue = True,
                              offvalue = False)
firebase_button.grid(column=3, row=1, sticky=W, pady=5)

#######################################################################
# Select Path

folder_path = StringVar()
folder_path.set("/home/pi/Desktop")
ttk.Label(s_frame_entry, text="Path to Store Images: ").grid(column=1, row=2, sticky=W)
path_entry = Entry(s_frame_entry, textvariable=folder_path, state= "disabled").grid(column=2, row=2, sticky=(E, W))
path_button = ttk.Button(s_frame_entry, text="Browse Folder",command=get_folder_path)
path_button.grid(column=3, row=2, sticky=E)

#######################################################################
# Duration Settings

duration = StringVar()
duration_units = StringVar()
duration.set("")
duration_units.set(unit_options[0])

ttk.Label(s_frame_entry, text="Duration: ").grid(column=1, row=3, sticky=W)

duration_reg = s_frame_entry.register(dur_iit_error_check)
duration_entry = ttk.Entry(s_frame_entry, textvariable=duration, validate="key", validatecommand=(duration_reg, '%P'))
duration_entry.grid(column=2, row=3, sticky=(W, E))

duration_drop = OptionMenu(s_frame_entry, duration_units, *unit_options)
duration_drop.grid(column=3, row=3, sticky=E)

#######################################################################
# Inter-Image Time Settings

inter_image_time = StringVar()
inter_image_time_units = StringVar()
inter_image_time.set("")
inter_image_time_units.set(unit_options[0])

ttk.Label(s_frame_entry, text="Inter-Image Time: ").grid(column=1, row=4, sticky=W)

iit_reg = s_frame_entry.register(dur_iit_error_check)
iit_entry = ttk.Entry(s_frame_entry, textvariable=inter_image_time, validate="key", validatecommand=(duration_reg, '%P'))
iit_entry.grid(column=2, row=4, sticky=(W, E))

iit_drop = OptionMenu(s_frame_entry, inter_image_time_units, *unit_options)
iit_drop.grid(column=3, row=4, sticky=E)

#######################################################################
# Message Label

message_text = StringVar()
message_text.set("")
message_label = Label(s_frame_message, text = update_message(), fg="#FF0000", font='Arial 14 bold')
message_label.grid(column=1, row=1, sticky=(W,E))

#######################################################################
# Shutter Settings

shutter_speed = StringVar()
shutter_speed.set("1/125")

ttk.Label(s_frame_entry, text="Shutter Speed: ").grid(column=1, row=5, sticky=W)
shutter_drop = OptionMenu(s_frame_entry, shutter_speed, *shutter_options)
shutter_drop.grid(column=2, row=5, columnspan=2, sticky=(E,W))

#######################################################################
# Zoom Settings

max_zoom_level = 10
zoom_level = DoubleVar()

zoom_label = Label(s_frame_sliders, text = "Zoom: ")
zoom_label.grid(column=1, row=1, sticky=(S,W))

zoom_slider = Scale(s_frame_sliders,
                    length = 330,
                    variable = zoom_level,
                    from_ = 0,
                    to = max_zoom_level,
                    command = warn_change,
                    orient = HORIZONTAL)
zoom_slider.grid(column=2, row=1, columnspan=2, sticky=(E,W))

#######################################################################
# Sharpness Settings

max_sharpness_level = 10
sharpness_level = DoubleVar()
# sharpness_level.trace('w',update_message(1))

sharpness_label = Label(s_frame_sliders, text = "Sharpness: ")
sharpness_label.grid(column=1, row=2, sticky=(S,W))

sharpness_slider = Scale(s_frame_sliders,
                         length = 330,
                         variable = sharpness_level,
                         from_ = 0,
                         to = max_sharpness_level,
                         orient = HORIZONTAL)
sharpness_slider.grid(column=2, row=2, columnspan=2, sticky=(E,W))

#######################################################################
# Contrast Settings

max_contrast_level = 10
contrast_level = DoubleVar()
# contrast_level.trace('w',update_message(1))

contrast_label = Label(s_frame_sliders, text = "Contrast: ")
contrast_label.grid(column=1, row=3, sticky=(S,W))

contrast_slider = Scale(s_frame_sliders,
                        length = 330,
                        variable = contrast_level,
                        from_ = 1,
                        to = max_contrast_level,
                        orient = HORIZONTAL)
contrast_slider.grid(column=2, row=3, columnspan=2, sticky=(E,W))

#######################################################################
# Brightness Settings

brightness_level = DoubleVar()
brightness_level.set(0.0)
# brightness_level.trace('w',update_message(1))

brightness_label = Label(s_frame_sliders, text = "Brightness: ")
brightness_label.grid(column=1, row=4, sticky=(S,W))

brightness_slider = Scale(s_frame_sliders,
                          length = 330,
                          variable = brightness_level,
                          from_ = -1,
                          to = 1,
                          resolution = 0.01,
                          orient = HORIZONTAL)
brightness_slider.grid(column=2, row=4, columnspan=2, sticky=(E,W))

#######################################################################
# Vert/Horz Flip Settings

v_flip = BooleanVar()
# v_flip.trace('w',update_message(1))
v_flip_button = Checkbutton(s_frame_toggles,
                            text = "Vertical Flip",
                            variable = v_flip,
                            onvalue = True,
                            offvalue = False)
v_flip_button.grid(column=1, row=1, sticky=W)

h_flip = BooleanVar()
# h_flip.trace('w',update_message(1))
h_flip_button = Checkbutton(s_frame_toggles,
                            text = "Horizontal Flip",
                            variable = h_flip,
                            onvalue = True,
                            offvalue = False)
h_flip_button.grid(column=2, row=1, sticky=W)

#######################################################################
# Preview Button

start_button = ttk.Button(s_frame_buttons, text="Preview", width=7, command=preview)
start_button.grid(column=1, row=1, sticky=E)

#######################################################################
# Start Button

start_button = ttk.Button(s_frame_buttons, text="Start", width=7, command=start_button_pressed)
start_button.grid(column=2, row=1, sticky=E)

#######################################################################
# Preview Frame

preview_image = Image.open("preview.jpg")
width, height = preview_image.size
preview_image = preview_image.resize((width // 10, height // 10))
tkimage = ImageTk.PhotoImage(preview_image)
panel1 = Label(preview_frame, image=tkimage)
panel1.grid(sticky=(W,E))

#######################################################################
# Run Window Setup

run_window = Toplevel(root)
run_window.title("Running...")
run_window.protocol("WM_DELETE_WINDOW", cancel)

run_frame = ttk.Frame(run_window, padding="3 3 12 12")
run_frame.grid(column=0, row=0, sticky=(N, W, E, S))

pb = ttk.Progressbar(run_frame, orient='horizontal', mode='determinate', length=280)
pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
pb_label_percent = ttk.Label(run_frame, text=update_progress_label_percent())
pb_label_percent.grid(column=0, row=1, columnspan=2)
total_pics = IntVar()
total_pics.set(0)
pb_label_frac = ttk.Label(run_frame, text=update_progress_label_frac())
pb_label_frac.grid(column=0, row=2, columnspan=2)

stop_button = ttk.Button(run_frame, text="Cancel", command=cancel)
stop_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10, sticky=(W, E))

run_window.withdraw()
preview()

root.mainloop()
