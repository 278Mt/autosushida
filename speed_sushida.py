#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  15 12:01:20 2018

speed_sishida.py
automatically resolving sushida
@author: 278mt
"""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import os
import sys
import re
from PIL import ImageGrab
from PIL import Image
import pyocr
import pyocr.builders

tools = pyocr.get_available_tools()
tool = tools[0]

# if you use short technical avoidant speed, technical probrems will be raised.
technical_avoidant_speed = 0 #[sec]

# easy, normal, hard courses
courses = [-70, 0, 70]
course = courses[2]

# you use chrome driver.
# here you can download,
# "http://chromedriver.chromium.org/downloads"
driver_path = './chromedriver'
target_url = 'http://typingx0.net/sushida/play.html'

# open driver
driver = webdriver.Chrome(driver_path)
driver.get(target_url)

# technical avoidant sleep.
# underconstruction
# future, here will be made by pyorc
sleep(10)

# click start action
actions = ActionChains(driver)
actions.move_by_offset(604,366).click().perform()
print("GO")

# technical avoidant sleep.
sleep(2)

# click cource action
actions = ActionChains(driver)
actions.move_by_offset(0,course).click().perform()
print("GO")

# input SPACE for starting game
target_xpath = '/html/body'
element = driver.find_element_by_xpath(target_xpath)
element.send_keys(" ")

# technical avoidant sleep.
sleep(2)

# underconstruction
# tweak is a very borring for me, hummm....
if course == courses[0]:
    xs = [162,137,126,114,102,90]
elif course == courses[1]:
    xs = [114,102,90,78,66,53]
elif course == courses[2]:
    xs = [78,66,53,42,30,18]

i = 0
pre_text = ""

while True:
    #fname = "corpus/sample{:06}".format(i)+".png"
    fname = "corpus/sample.png"
    # clip an image
    ImageGrab.grab(bbox=(378, 525, 856, 551)).save(fname)

    # read as a monocolor mode
    im = Image.open(fname).convert('L')
    for x in xs:
        k = im.getpixel((x,0))
        if k == 255:
            print(x, i)
            # rewrite an image to bicolor: white or black, not gradation
            for imx in range(478):
                for imy in range(22):
                    if im.getpixel((imx, imy)) >= 128:
                        im.putpixel((imx, imy), 0)
                    else:
                        im.putpixel((imx, imy), 255)

            im.crop((x+16, 0, 478-x-16, 24)).save(fname)
            break

    # read string from an image
    im = Image.open(fname)
    text = tool.image_to_string(
        im,
        lang='eng',
        builder=pyocr.builders.TextBuilder()
    )
    text = re.sub('[^-,\!\?abcdefghijklmnopqrstuvwxyz]', '', text)
    element.send_keys(text)
    print(text)

    # underconstruction
    # if failing reading string, bruteforcing spell
    if pre_text == text or text == "":
        element.send_keys("-,!?abcdefghijklmnopqrstuvwxyz")

    else:
        pre_text = text
        i += 1
        # technical avoidant speed
        sleep(technical_avoidant_speed)

# if input sth, exit
input()

driver.close()
driver.quit()

