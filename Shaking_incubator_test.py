from PIL import Image
import numpy as np
import os
import glob
import matplotlib.pyplot as plt

speed_list = ["Static",
              "30 RPM",
              "60 RPM",
              "90 RPM",
              "120 RPM",
              "150 RPM",
              "180 RPM"]

image_list = []
image_names = []
for filename in sorted(glob.glob("Images_60ss/*.jpg")):
    im = Image.open(filename).convert('L')
    image_list.append(im)
    image_names.append(filename)

sharp_list = []
for im in image_list:
    array = np.asarray(im, dtype=np.int32)
    gy, gx = np.gradient(array)
    gnorm = np.sqrt(gx**2 + gy**2)
    sharp_list.append(np.average(gnorm))

plt.bar(speed_list,sharp_list)
plt.title("Sharpness of Images at Various RPM")
plt.xlabel("Speed")
plt.ylabel("Sharpness (Average Gradient Magnitude)")
ss_list = ["1/60s",
           "1/80s",
           "1/100s"]

image_list = []
image_names = []
for filename in sorted(glob.glob("Images_180rpm/*.jpg")):
    im = Image.open(filename).convert('L')
    image_list.append(im)
    image_names.append(filename)

sharp_list = []
for im in image_list:
    array = np.asarray(im, dtype=np.int32)
    gy, gx = np.gradient(array)
    gnorm = np.sqrt(gx**2 + gy**2)
    sharp_list.append(np.average(gnorm))

plt.bar(ss_list,sharp_list)
plt.title("Sharpness of Images at Various Shutter Speeds (180 RPM)")
plt.xlabel("Shutter Speed")
plt.ylabel("Sharpness (Average Gradient Magnitude)")
