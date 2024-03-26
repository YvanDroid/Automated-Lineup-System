import cv2
import pytesseract
from PIL import Image
import os
import numpy

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

file = r"D:\git\Automated-Lineup-System\Automated-Lineup-System\lib\table_reader\example.jpg"

img = Image.open(file)

text = pytesseract.image_to_string(img, config="--oem 3 --psm 12")

print(text[:-1])
