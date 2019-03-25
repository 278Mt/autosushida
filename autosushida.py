#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  15 12:01:20 2018
speed_sishida.py
automatically resolving sushida version 2.0
@author: 278mt
"""

import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import pyocr
import pyocr.builders

class SpeedSushida(object):

    def __init__(self, course_index=2):
        # pyocr's tool
        self.tool = pyocr.get_available_tools()[0]

        # easy, normal, hard courses
        self.courses = {0:{"coord" : -60,
                           "xs"    : ( 76,  88, 100, 112, 124, 136),
                           "costs" : (100, 100, 100, 180, 180, 240),
                           "tas"   : 10.0},
                        1:{"coord" : 0,
                           "xs"    : (112, 124, 136, 150, 162, 174),
                           "costs" : (180, 180, 240, 240, 240, 380),
                           "tas"   : 0.0},
                        2:{"coord" : 60,
                           "xs"    : (162, 174, 186, 198, 210, 222),
                           "costs" : (240, 380, 380, 380, 500, 500),
                           "tas"   : 0.0}}

        # image size
        self.window = (752, 720)
        # set technical avoidant speed and coodination for identification of cost of dish flowing
        self.y = 324

        # you use chrome driver.
        # here you can download,
        # "http://chromedriver.chromium.org/downloads"
        driver_path = './chromedriver'
        target_url = 'http://typingx0.net/sushida/play.html'

        # open driver
        self.driver = webdriver.Chrome(driver_path)
        # set window size
        self.driver.set_window_size(*self.window)
        # move to target url
        self.driver.get(target_url)

        # filename of sampling png
        self.fname = "./corpus/sample.png"

        # coodination of center of page
        self.center = (self.window[0]//2, 386)
        try:
            course = self.courses[int(course_index)]
        except IndexError:
            course = self.courses[2]

        self.coord = course["coord"]
        self.xs    = course["xs"]
        self.costs = course["costs"]
        self.tas   = course["tas"]

        self.target_xpath = '/html/body'
        self.element = self.driver.find_element_by_xpath(self.target_xpath)

    def _start_action(self):
        # before start action
        while True:
            self.driver.save_screenshot(self.fname)

            # clip an image
            im = Image.open(self.fname).convert('L')
            k = im.getpixel(self.center)
            if k != 0:
                break

        # click start action
        actions = ActionChains(self.driver)
        actions.move_by_offset(*self.center).click().perform()
        print("CLICKED START BUTTON")

    def _course_action(self):
        # before course action
        while True:
            self.driver.save_screenshot(self.fname)

            # clip an image
            im = Image.open(self.fname).convert('L')
            k = im.getpixel(self.center)
            if k == 255:
                break

        # click course action
        actions = ActionChains(self.driver)
        actions.move_by_offset(0, self.coord).click().perform()
        print("CLICKED COURSE BUTTON")

    def _start_game(self):
        # input SPACE for starting game
        self.element.send_keys(" ")

        # before displaying question
        while True:
            self.driver.save_screenshot(self.fname)

            # clip an image
            im = Image.open(self.fname).convert('L')

            for i in range(len(self.xs)):
                k = im.getpixel((self.center[0]+self.xs[i], self.y))
                if k == 255:
                    return

    def _identify_cost_and_resave_im(self, im, xs):
        for i in range(len(xs)):
            k = im.getpixel((self.center[0]+xs[i], self.y))
            if k == 255:

                # resave an image to bicolor: white or black, not gradation
                for imx in range(self.center[0]-xs[i]+8, self.center[0]+xs[i]-8):
                    for imy in range(356, 380):
                        if im.getpixel((imx, imy)) >= 128:
                            im.putpixel((imx, imy), 0)
                        else:
                            im.putpixel((imx, imy), 255)

                return i, im.crop((self.center[0]-xs[i]+8, 356, self.center[0]+xs[i]-8, 380))

    def _analyze_text(self, im):
        text = self.tool.image_to_string(
            im,
            lang='eng',
            builder=pyocr.builders.TextBuilder()
        )
        # substate correct string from uncorrect one
        text = re.sub('[^-,\!\?a-z]', '', text)

        return text

    def auto_game(self):

        self._start_action()
        self._course_action()
        self._start_game()

        # initialize pre text
        pre_text = ""
        fname_i = 0
        while True:
            # if you fail technical avoidance, break
            try:
                self.driver.save_screenshot(self.fname)

                # clip an image
                im = Image.open(self.fname).convert('L')

                # if finish the game, break
                # identify twitter logo
                if im.getpixel((self.center[0]+48, self.center[1]+48)) == 132:
                    break

                # identify cost of dish
                # and resave an image to bicolor: white or black, not gradation
                i, im = self._identify_cost_and_resave_im(im, self.xs)
                # analyze text
                text = self._analyze_text(im)

                # send text
                self.element.send_keys(text)

                # print text on terminal
                print(self.costs[i], "YEN DISH:", text.upper())

                # if failing reading string, bruteforcing spell
                if pre_text == text or text == "":
                    self.element.send_keys("-,!?abcdefghijklmnopqrstuvwxyz")
                    im.save("corpus/error_"+pre_text+"_.png")
                else:
                    # make corpus
                    # os.rename(fname, "corpus/"+text+".png")

                    # save pre_text for failing image analysis
                    pre_text = text
                    fname_i += 1

                    # technical avoidant speed
                    sleep(self.tas)

            # if you fail technical avoidance, break
            except Exception as ex:
                assert ex
                break

    def __del__(self):
        # if input sth, exit
        print()
        input("IF YOU EXIT, PLEASE INPUT STH")

        # close driver
        self.driver.close()
        self.driver.quit()

def main():
    spisushi = SpeedSushida(1)
    spisushi.auto_game()
    del spisushi

if __name__ == "__main__":
    main()
