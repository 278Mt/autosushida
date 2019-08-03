#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  15 12:01:20 2018
speed_sishida.py
automatically resolving sushida version 2.0
@author: 278mt
"""

from re import sub as resub
from io import BytesIO
from traceback import format_exc
#from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL.Image import open as image_open
from PIL.Image import fromarray
from pyocr import get_available_tools
from pyocr.builders import TextBuilder
from numpy import asarray


class AutoSushida(object):

    def __init__(self, level=2, input_sth=True):
        # if input_sth mode is false, input sth is off set
        self.__input_sth = input_sth

        # alias
        course_index = level

        # pyocr's tool
        self.__image_to_string = get_available_tools()[0].image_to_string
        self.__image_to_string.__defaults__ = ('eng', TextBuilder())

        # easy, normal, hard courses
        courses = {0:{"coord" : -60,
                      "xs"    : [ 76,  88, 100, 112, 124, 136],
                      "costs" : [100, 100, 100, 180, 180, 240]},
                   1:{"coord" : 0,
                      "xs"    : [112, 124, 136, 150, 162, 174],
                      "costs" : [180, 180, 240, 240, 240, 380]},
                   2:{"coord" : 60,
                      "xs"    : [162, 174, 186, 198, 210, 222],
                      "costs" : [240, 380, 380, 380, 500, 500]}}

        # set technical avoidant speed and coodination for identification of cost of dish flowing
        self.__y = 256

        try:
            course = courses[int(course_index)]
        except ValueError:
            print("PLEASE INPUT ARGUMENT level BY TYPE OF int")
            print("START HARD MODE")
        except IndexError:
            print("PLEASE INPUT ARGUMENT level 0, 1, OR 2")
            print("START HARD MODE")
            course = courses[2]

        self.__coord = course["coord"]
        self.__xs    = course["xs"]
        self.__costs = course["costs"]


    def __open_chrome(self):
        # you use chrome driver.
        # here you can download,
        # "http://chromedriver.chromium.org/downloads"

        # open driver
        driver_path = '../chromedriver'
        self.__driver = webdriver.Chrome(driver_path)
        self.__get_screenshot_as_png = self.__driver.get_screenshot_as_png

        # window size
        window = (500, 420+123)

        # coodination of center of page
        self.__center_x = window[0]//2
        self.__center_y = 256

        # set window size
        self.__driver.set_window_size(*window)

        # move to target url
        target_url = 'http://typingx0.net/sushida/play.html'
        self.__driver.get(target_url)

        target_xpath = '//*[@id="game"]/div'
        self.__webgl_element = self.__driver.find_element_by_xpath(target_xpath)
        actions = ActionChains(self.__driver)
        actions.move_to_element(self.__webgl_element)
        actions.perform()

        target_xpath = '/html/body'
        self.__send_keys = self.__driver.find_element_by_xpath(target_xpath).send_keys

        return


    def __start_action(self):
        # before start action
        k = 0
        while k == 0:
            # save iostream image and clip an image
            im = image_open(BytesIO(self.__get_screenshot_as_png())).convert('L')

            k = im.getpixel((self.__center_x, self.__center_y))

        # click start action
        actions = ActionChains(self.__driver)
        actions.move_to_element_with_offset(self.__webgl_element, self.__center_x, self.__center_y).click().perform()
        print("CLICKED START BUTTON")

        return


    def __course_action(self):
        # before course action
        k = 0
        while k != 255:
            # save iostream image and clip an image
            im = image_open(BytesIO(self.__get_screenshot_as_png())).convert('L')

            k = im.getpixel((self.__center_x, self.__center_y))

        # click course action
        actions = ActionChains(self.__driver)
        actions.move_by_offset(0, self.__coord).click().perform()
        print("CLICKED COURSE BUTTON")

        return


    def __start_game(self):
        # input SPACE for starting game
        self.__send_keys(" ")

        # before displaying question
        k = 0
        while k != 255:
            # save iostream image and clip an image
            im = image_open(BytesIO(self.__get_screenshot_as_png())).convert('L')

            k = im.getpixel((self.__center_x+self.__xs[0], self.__y))

        return


    def __identify_cost_and_resave_im(self, im):

        xs = self.__xs
        for x in xs:
            if im.getpixel((self.__center_x+x, self.__y)) == 255:

                # resave an image to bicolor: white or black, not gradation
                im = asarray(im.crop((self.__center_x-x+32, 230, self.__center_x+x-32, 254)))
                # when convering PIL image into numpy array, the array is immutable
                im.flags.writeable = True

                # if just middle gray and lighter which is font collor, it will black
                # else which is background collor, it will white
                # -1 of uint8 is 255. eg 136 >> 7 == 1, 1-1 == 0(black). 94 >> 7 == 0, 0-1 == -1 == 255(white)
                return self.__costs[xs.index(x)], fromarray((im>>7)-1)


    def auto_game(self):
        # initialize pre text
        pre_text = ""

        self.__open_chrome()
        self.__start_action()
        self.__course_action()
        self.__start_game()

        send_keys = self.__send_keys

        # if you fail technical avoidance, break
        try:
            while True:
                # save iostream image and clip an image
                im = image_open(BytesIO(self.__get_screenshot_as_png())).convert('L')

                # identify cost of dish
                # and resave an image to bicolor: white or black, not gradation
                cost, im = self.__identify_cost_and_resave_im(im)

                # analyze text
                text = resub("[^a-z,\-\!\?]", "", self.__image_to_string(im))

                # send text
                send_keys(text)

                # print text on terminal
                print(cost, "YEN DISH:", text.upper())

                # if failing reading string, bruteforcing spell
                if pre_text == text or text == "":
                    send_keys("-,!?abcdefghijklmnopqrstuvwxyz")
                    im.save("corpus/error_"+pre_text+"_.png")
                else:
                    # save pre_text for failing image analysis
                    pre_text = text

        # end the game
        except TypeError:
            print("======== END THE GAME ========")

        # if you fail technical avoidance, break
        except Exception:
            print(format_exc())

        return


    def __del__(self):
        # if input sth, exit
        if self.__input_sth:
            input("IF YOU EXIT, PLEASE INPUT STH")



if __name__ == "__main__":
    for i in range(1):
        atsushi = AutoSushida(level=0, input_sth=True)
        atsushi.auto_game()
        del atsushi
