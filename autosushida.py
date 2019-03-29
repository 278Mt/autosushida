#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  15 12:01:20 2018
speed_sishida.py
automatically resolving sushida version 2.0
@author: 278mt
"""

import re
import io
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import pyocr
import pyocr.builders

class AutoSushida(object):

    def __init__(self, level=2, input_sth=True):
        # if input_sth mode is false, input sth is off set
        self.input_sth = input_sth

        # alias
        course_index = level

        # pyocr's tool
        self.tool = pyocr.get_available_tools()[0]

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
        self.y = 256

        # filename of sampling png
        self.fname = "./sample.png"

        try:
            course = courses[int(course_index)]
        except ValueError:
            print("PLEASE INPUT ARGUMENT level BY TYPE OF int")
            print("START HARD MODE")
        except IndexError:
            print("PLEASE INPUT ARGUMENT level 0, 1, OR 2")
            print("START HARD MODE")
            course = courses[2]

        self.coord = course["coord"]
        self.xs    = course["xs"]
        self.costs = course["costs"]

        # input technical avoidant speed
        self.max_dishes = 700-1

    def _open_chrome(self):
        # you use chrome driver.
        # here you can download,
        # "http://chromedriver.chromium.org/downloads"

        # open driver
        driver_path = './chromedriver'
        self.driver = webdriver.Chrome(driver_path)

        # window size
        window = (500, 420+123)

        # coodination of center of page
        self.center_x = window[0]//2
        self.center_y = 256

        # set window size
        self.driver.set_window_size(*window)

        # move to target url
        target_url = 'http://typingx0.net/sushida/play.html'
        self.driver.get(target_url)

        target_xpath = '//*[@id="game"]/div'
        self.webgl_element = self.driver.find_element_by_xpath(target_xpath)
        actions = ActionChains(self.driver)
        actions.move_to_element(self.webgl_element)
        actions.perform()

        target_xpath = '/html/body'
        self.body_element = self.driver.find_element_by_xpath(target_xpath)

    def _start_action(self):
        # before start action
        while True:
            self.driver.save_screenshot(self.fname)

            # clip an image
            im = Image.open(self.fname).convert('L')
            k = im.getpixel((self.center_x, self.center_y))
            if k!= 0:
                break

        # click start action
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(self.webgl_element, self.center_x, self.center_y).click().perform()
        print("CLICKED START BUTTON")

    def _course_action(self):
        # before course action
        while True:
            # save iostream image
            im_bin = self.driver.get_screenshot_as_png()
            im_bin_stream = io.BytesIO(im_bin)

            # clip an image
            im = Image.open(im_bin_stream).convert('L')

            k = im.getpixel((self.center_x, self.center_y))
            if k == 255:
                break

        # click course action
        actions = ActionChains(self.driver)
        actions.move_by_offset(0, self.coord).click().perform()
        print("CLICKED COURSE BUTTON")

    def _start_game(self):
        # input SPACE for starting game
        self.body_element.send_keys(" ")

        # before displaying question
        while True:
            # save iostream image
            im_bin = self.driver.get_screenshot_as_png()
            im_bin_stream = io.BytesIO(im_bin)

            # clip an image
            im = Image.open(im_bin_stream).convert('L')

            k = im.getpixel((self.center_x+self.xs[0], self.y))
            if k == 255:
                return

    def _identify_cost_and_resave_im(self, im, xs):

        for i in range(len(xs)):
            k = im.getpixel((self.center_x+xs[i], self.y))
            if k == 255:

                # resave an image to bicolor: white or black, not gradation
                im = im.crop((self.center_x-xs[i]+32, 230, self.center_x+xs[i]-32, 254))
                for imx in range(im.width):
                    for imy in range(im.height):
                        k = im.getpixel((imx, imy))
                        # if just middle gray and lighter which is font collor, it will black
                        if k >= 128:
                            im.putpixel((imx, imy), 0)
                        # else which is background collor, it will white
                        else:
                            im.putpixel((imx, imy), 255)

                return self.costs[i], im

    def _predict_text(self, im):

        text = self.tool.image_to_string(im, lang='eng', builder=pyocr.builders.TextBuilder())

        return re.sub("[^a-z,\-\!\?]", "", text)

    def auto_game(self):
        # initialize pre text
        pre_text = ""
        predict_dishes = 0

        self._open_chrome()
        self._start_action()
        self._course_action()
        self._start_game()

        while True:
            # if you fail technical avoidance, break
            try:
                # save iostream image
                im_bin = self.driver.get_screenshot_as_png()
                im_bin_stream = io.BytesIO(im_bin)

                # clip an image
                im = Image.open(im_bin_stream).convert('L')

                # if finish the game, break
                # identify twitter logo
                k = im.getpixel((self.center_x+48, self.center_y+48))
                if k == 132:
                    break

                # identify cost of dish
                # and resave an image to bicolor: white or black, not gradation
                cost, im = self._identify_cost_and_resave_im(im, self.xs)

                # save file for corpus
                # im.save("./corpus/__corpus_{:03}.png".format(predict_dishes))

                # analyze text
                text = self._predict_text(im)

                # send text
                self.body_element.send_keys(text)

                # print text on terminal
                print(cost, "YEN DISH:", text.upper())

                # if failing reading string, bruteforcing spell
                if pre_text == text or text == "":
                    self.body_element.send_keys("-,!?abcdefghijklmnopqrstuvwxyz")
                    im.save("corpus/error_"+pre_text+"_.png")
                else:
                    # save pre_text for failing image analysis
                    pre_text = text
                    predict_dishes += 1
                    if predict_dishes == self.max_dishes:
                        break

            # if you fail technical avoidance, break
            except Exception:
                break

    def __del__(self):
        # if input sth, exit
        print("======== END THE GAME ========")
        if self.input_sth:
            input("IF YOU EXIT, PLEASE INPUT STH")

        # close driver
        self.driver.close()
        self.driver.quit()

def main():
    for i in range(1):
        atsushi = AutoSushida(level=0, input_sth=True)
        atsushi.auto_game()
        del atsushi

if __name__ == "__main__":
    main()
