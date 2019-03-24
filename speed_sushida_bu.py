#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  15 12:01:20 2018

speed_sishida.py
automatically resolving sushida version 2.0
@author: 278mt
"""

import os
import sys
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
from PIL import Image
import pyocr
import pyocr.builders

# pyocr's tool
tool = pyocr.get_available_tools()[0]

# easy, normal, hard courses
courses = (-60, 0, 60)
try:
    course = courses[int(sys.argv[1])]
except IndexError:
    course = courses[-1]

# you use chrome driver.
# here you can download,
# "http://chromedriver.chromium.org/downloads"
driver_path = './chromedriver'
target_url = 'http://typingx0.net/sushida/play.html'

# open driver
driver = webdriver.Chrome(driver_path)
# move to target url
driver.get(target_url)

# filename of sampling png
fname = "./corpus/sample.png"

# coodination of center of page
center = (600,384)

# befor start action
while True:
    driver.save_screenshot(fname)

    # clip an image
    im = Image.open(fname).convert('L')
    k = im.getpixel(center)
    if k == 52:
        break

# click start action
actions = ActionChains(driver)
actions.move_by_offset(*center).click().perform()
print("CLICKED START BUTTON")

# before course action
while True:
    driver.save_screenshot(fname)

    # clip an image
    im = Image.open(fname).convert('L')
    k = im.getpixel(center)
    if k == 252:
        break

# click course action
actions = ActionChains(driver)
actions.move_by_offset(0,course).click().perform()
print("CLICKED COURSE BUTTON")

# input SPACE for starting game
target_xpath = '/html/body'
element = driver.find_element_by_xpath(target_xpath)
element.send_keys(" ")

# set technical avoidant speed and coodination for identification of cost of dish flowing
y = 324
if   course == courses[0]:
    xs = (518,506,494,482,470,458)
    costs = (100,100,100,180,180,240)
    technical_avoidant_speed = 0.0
elif course == courses[1]:
    xs = (482,470,458,432,422)
    costs = (180,180,240,240,380)
    technical_avoidant_speed = 0.0
elif course == courses[2]:
    xs = (432,422,410,398,386,374)
    costs = (240,380,380,380,500,500)
    technical_avoidant_speed = 0.0

# before displaying question
while True:
    driver.save_screenshot(fname)

    # clip an image
    im = Image.open(fname).convert('L')

    for i in range(len(xs)):
        k = im.getpixel((xs[i],y))
        if k == 255:
            break
    else:
        continue
    break

# initialize pre text
pre_text = ""
fname_i = 0
while True:
    # if you fail technical avoidance, break
    try:
        driver.save_screenshot(fname)
    except UnexpectedAlertPresentException:
        break

    # clip an image
    im = Image.open(fname).convert('L')

    # if finish the game, break
    if im.getpixel((640,420)) == 131:
        break

    # identify cost of dish
    for i in range(len(xs)):
        k = im.getpixel((xs[i],y))
        if k == 255:

            # resave an image to bicolor: white or black, not gradation
            for imx in range(xs[i]+16,1200-xs[i]-10-16):
                for imy in range(356,380):
                    if im.getpixel((imx, imy)) >= 128:
                        im.putpixel((imx, imy), 0)
                    else:
                        im.putpixel((imx, imy), 255)

            im.crop((xs[i]+16, 356, 1200-xs[i]-10-16, 380)).save(fname)
            break

    # read string from an image
    im = Image.open(fname)
    text = tool.image_to_string(
        im,
        lang='eng',
        builder=pyocr.builders.TextBuilder()
    )
    # substate correct string from uncorrect one
    text = re.sub('[^-,\!\?a-z]', '', text)

    # send text
    element.send_keys(text)

    # print text on terminal
    print(costs[i], "YEN DISH:", text.upper())

    # if failing reading string, bruteforcing spell
    if pre_text == text or text == "":
        element.send_keys("-,!?abcdefghijklmnopqrstuvwxyz")
    else:
        # make corpus
        # os.rename(fname, "corpus/"+text+".png")

        # save pre_text for failing image analysis
        pre_text = text
        fname_i += 1

        # technical avoidant speed
        sleep(technical_avoidant_speed)

# if input sth, exit
print()
input("IF YOU EXIT, PLEASE INPUT STH")

# close driver
driver.close()
driver.quit()

