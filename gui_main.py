# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3

"""
#pip install tkinter
#pip install reportlib


import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import customtkinter as ct
from tkinter import filedialog
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Image as im
from reportlab.lib.units import inch
import cv2 
import os
import numpy as np
from matplotlib import pyplot as plt
import traceback
from os.path import join
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import re

global current_directory
current_directory = os.getcwd()
global x
x = ""


def plot_image(image, title=''):
    plt.title(title, size=20)
    if len(image.shape) < 3:
        plt.imshow(image, cmap='gray')
    else:
        plt.imshow(image)
        
def increase_saturation(image, saturation_factor):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    s = np.clip(s * saturation_factor, 0, 255).astype(np.uint8)
    hsv_image = cv2.merge((h, s, v))
    result_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    return result_image
  
  
base_path = os.getcwd()
saturation_factor=1.5
color_thresholds_glob = {
    'pink/(-)': [(145, 50, 100), (190, 200, 255)],
    'yellow/(+)': [(9, 150, 100), (45, 255, 255)],
    'red/(-)': [(0, 175, 100), (7, 255, 255)],
    'blue/(+)': [(100, 20, 105), (130, 200, 255)]}

global clabel
global sign
clabel = []
sign = []


def chemical_reaction_occurence(image_path,saturation_factor=1.5,color_thresholds=color_thresholds_glob):
    """
    Performs color segmentation to detect chemical reactions in an image.

    Args:
        image_path (str): The path to the image file.
        saturation_factor (float, optional): The factor by which to increase the saturation of the image.
            Higher values result in more vivid colors. Default is 1.5.
        color_thresholds (dict, optional): A dictionary containing color labels as keys and corresponding
            color ranges as values. The color ranges define the lower and upper bounds for detecting specific
            colors in the image. Default is `color_thresholds_glob`.

    Returns:
        numpy.ndarray: The modified image with highlighted chemical reactions.

    Note:
        The `color_thresholds_glob` is a global variable that should be defined prior to calling this function.
        It should be a dictionary with color labels as keys and corresponding color ranges as values.
        Example: {'red': ([0, 50, 50], [10, 255, 255]), 'blue': ([100, 50, 50], [130, 255, 255])}

    Working of the code :
    
        1. The function reads the image from the specified file path and converts it from BGR to RGB color space.
        2. The image's saturation is enhanced using the provided saturation factor.
        3. The RGB image is then converted to the HSV color space, which separates color information into
           hue, saturation, and value components.
        4. The function iterates over the color thresholds dictionary, which contains color labels and ranges.
        5. For each color label and range, a binary mask is created by thresholding the HSV image based on
           the lower and upper color bounds.
        6. Contours are found in the binary mask using the findContours function.
        7. Each contour's area and aspect ratio (width/height) are evaluated to filter out small and
           non-rectangular contours.
        8. Contours that meet the area and aspect ratio criteria are highlighted by drawing rectangles
           around them and adding the corresponding color label near the rectangle.
        9. The modified image, with the highlighted chemical reactions, is returned as the output of the function.
    """
    
    global clabel #
    global sign #
    clabel = [] #
    sign = [] #
    
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image=increase_saturation(image, saturation_factor)

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    max_area = -1
    for color_label, color_range in color_thresholds.items():
        lower_color = np.array(color_range[0])
        upper_color = np.array(color_range[1])

        mask = cv2.inRange(hsv, lower_color, upper_color)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 90 :
                x, y, width, height = cv2.boundingRect(contour)
                aspect_ratio=width/height
                if 1.3>= aspect_ratio>=0.6:
                    cv2.rectangle(image, (x, y), (x + width, y + height), (0, 0, 0), 2)               
                    cv2.putText(image, color_label, (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6,(255, 255, 0), 2)
                    
                    print(color_label) # you can comment it #
                    clabel.append(color_label) #
                    z = ((color_label.split("/"))[1])[1] #
                    print(z) #
                    sign.append(z) #
    clabel.reverse() #
    sign.reverse() #
    print(clabel) #
    print(sign) #

    return image
  

def input_image():
    global  serial_num
    serial_num = get_serial_number()
    print("Select input image")
    
    filetypes = (
        ("Image files", "*.jpg *.jpeg *.png "),
        ("All files", "*.*")
    )
    
    filepath = filedialog.askopenfilename(
        initialdir="/", title="Select Image File",
        filetypes=filetypes
    )
    
    return filepath
    
  
def build_pdf():
    
    global current_directory1
    global clabel
    global serial_num
    
    print("Build PDF")
    print(current_directory1)
    print()
    
    try:
        
        graphs = os.listdir(current_directory1)
        graphs = [join(current_directory1, x) for x in graphs]

        
        doc = SimpleDocTemplate(join(current_directory1, f"{serial_num}-result.pdf"), pagesize=(1500, 5000))
        parts = []
        
        # Adding text before the images
        styles = getSampleStyleSheet()
        title = Paragraph("<b>LAMP Reaction Analysis</b>", styles['Title'])
        parts.append(title)
        
        for image in graphs:
            try:
              
              f = open(image, 'rb')
              parts.append(im(f))
            except:
              pass
            
        title = Paragraph("<b>Analysis Results: </b>", styles['Title'])
        parts.append(title)
        
        for i in clabel:
          title = Paragraph(f"<b>{i}</b>", styles['Title'])
          parts.append(title)
        
        doc.build(parts)
    except Exception as e:
        print(e)
        error = str(e) + "\n\n" + str(traceback.format_exc())
        print(error)
  

def get_serial_number():
    try:
      global current_directory
      global current_directory1
      current_directory1 = str(current_directory)+'/result'
      print(current_directory1)
      if not os.path.exists(current_directory1):
          os.makedirs(current_directory1)
          
      files = [f for f in os.listdir(current_directory1) if os.path.isdir(os.path.join(current_directory1, f))]
      print("files available", str(files))
      
      
      serial_numbers = []
      for file in files:
          match = re.search(r'^(\d+)-.*', file)
          print(f"match = {match}")
          if match:
              serial_numbers.append(int(match.group(1)))
      if serial_numbers:
          serial_number = max(serial_numbers) + 1
      else:
          serial_number = 1
      result = str(serial_number).zfill(3)
      #print(f"get_serial_number() returned {result}")
    except Exception as e:
      print(e)
      error = str(e) + "\n\n" + str(traceback.format_exc())
      print(error)
      result="000"
      
    current_directory1 = str(current_directory1)+f'/{result}-result'
    print(current_directory1)
    if not os.path.exists(current_directory1):
        os.makedirs(current_directory1)
        
    return result


def save_picture(img, i):
    try:
        global current_directory
        global current_directory1
        global serial_num
        
        
        print(current_directory)
        print(serial_num)
      
        if i == 1:
            # img = ImageTk.PhotoImage(img)
            img.save(f"{current_directory1}//{serial_num}-output.png")
        else:
            img.save(f"{current_directory1}//{serial_num}-input.png")
    except Exception as e:
        print(e)
        error = str(e) + "\n\n" + str(traceback.format_exc())
        print(error)
    

def analyze_image():
    print("Image Analysis")
    global x
    global clabel
    global sign
    
    try:
        if not x == "":
            
            image_path = x
            detection=chemical_reaction_occurence(image_path)
            
          
            e1.delete(0, END)
            s = ""
            for i in sign:
              s=s+i
            e1.insert(0, f"{s}")
            
            # Load the background image
            
            # Get the actual width and height of the label
            label_width = image_label2.winfo_width()
            label_height = image_label2.winfo_height()
            
            
            # Convert the frame to a PIL Image
            img = Image.fromarray(detection)
            save_picture(img, 1)
            img = img.resize((label_width, label_height))
            img = ImageTk.PhotoImage(img)

            # Create a label with the background image
            image_label2.configure(image=img, text="")
            
            
        else:
          # Create a label with the background image
          image_label2.configure(image=img, text="Input Image")
          raise ValueError("Input image file not imported!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        error = str(e) + "\n\n" + str(traceback.format_exc())
        print(error)
        
    
def save_result():
    global serial_num
    print("Save results")
    
    try:
        
        build_pdf()
        # filepath = join(f"./result/{serial_num}-result", f"{serial_num}-result.pdf")
        # import subprocess, os, platform
        # if not os.path.exists(filepath):
        #     return False

        # if platform.system() == 'Darwin':  # macOS
        #     subprocess.call(('open', filepath))
        # elif platform.system() == 'Windows':  # Windows
        #     os.startfile(filepath)
        # else:  # linux variants
        #     subprocess.call(('xdg-open', filepath))
        # return True
    except Exception as e:
        print(e)
        error = str(e) + "\n\n" + str(traceback.format_exc())
        print(error)


root = tk.Tk()
# root.state('zoomed')
green = "#6fc276"
lgreen = "#ACFB88"
root.title("Amplification Detection through Color Segmentation")
root.geometry("900x700+50+50")
# Disable window resizing
root.resizable(False, False)
font0=("Arial bold", 14)
font1=("Arial bold", 20)
font2=("Arial", 14)
font3=("Arial bold", 24)

# Load the background image
background_image = Image.open("bg1.jpg")
background_photo = ImageTk.PhotoImage(background_image)

# Create a label with the background image
background_label = Label(root, image=background_photo)
background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

frame0 = ct.CTkFrame(root, fg_color="white", bg_color="white",)
frame0.place(relx=0.5, rely=0.1, relwidth=1, relheight=0.1, anchor=CENTER)

# Create the title label
title_label = ct.CTkLabel(frame0, text="LAMP Reaction Analysis", 
                          font=font3, fg_color="transparent", bg_color="transparent",
                          text_color=green,
                          )
title_label.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.8, anchor=CENTER)


frame1 = ct.CTkFrame(root, border_width=5, border_color=green, bg_color="transparent", fg_color="white")
frame1.place(relx=0.05, rely=0.2, relwidth=0.425, relheight=0.5)

# Create the left image label
image_label1 = ct.CTkLabel(frame1, text="Input Image", 
                          font=("Arial bold", 20), fg_color="white", bg_color="white",
                          text_color=green,
                          )
image_label1.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

frame2 = ct.CTkFrame(root, border_width=5, border_color=green, bg_color="transparent", fg_color="white")
frame2.place(relx=0.5, rely=0.2, relwidth=0.425, relheight=0.5)

# Create the left image label
image_label2 = ct.CTkLabel(frame2, text="Result", 
                          font=("Arial bold", 20), fg_color="white", bg_color="white",
                          text_color=green,
                          )
image_label2.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

e1 = ct.CTkEntry(root,
  # text_color=green,
  font=font2,

)

e1.insert(0, "Program output...")
e1.place(relx=0.55, rely=0.72, relwidth=0.35, relheight=0.07)

e2 = ct.CTkEntry(root,
  # text_color=green,
  font=font2,

)

e2.insert(0, "Input image path...")
e2.place(relx=0.1, rely=0.72, relwidth=0.35, relheight=0.07)

def handle_button_click():
    global x
    x = input_image()
    print(x)
    e2.delete(0, END)
    e2.insert(0, f"{x}")
    
    # Load the background image
    
    # Get the actual width and height of the label
    label_width = image_label1.winfo_width()
    label_height = image_label1.winfo_height()
    
    img = Image.open(x)
    save_picture(img, 0)
    img = img.resize((label_width, label_height))
    img = ImageTk.PhotoImage(img)

    # Create a label with the background image
    image_label1.configure(image=img, text="")
    

button1 = ct.CTkButton(root, text="Upload the image", fg_color=green, text_color="white",
                       font = font0, border_width=5, border_color="white",
                       corner_radius=20, command = handle_button_click)
button1.place(relx=0.1, rely=0.85, relwidth=0.2, relheight=0.1)

button2 = ct.CTkButton(root, text="Analyze", fg_color=green, text_color="white",
                       font = font0, border_width=5, border_color="white",
                       corner_radius=20, command = analyze_image)
button2.place(relx=0.4, rely=0.85, relwidth=0.2, relheight=0.1)


button3 = ct.CTkButton(root, text="Save the result", fg_color=green, bg_color="transparent",
                       text_color="white",
                       font = font0, border_width=5, border_color="white",
                       corner_radius=20, command = save_result,
                       )
button3.place(relx=0.7, rely=0.85, relwidth=0.2, relheight=0.1)


root.mainloop()
