from PIL import Image, ImageDraw

from PIL import ImageFont

from time import sleep
from picamera import PiCamera


import epd2in7b
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

key1 = 5
key2 = 6
key3 = 13
key4 = 19

GPIO.setup(key1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

COLORED = 1
UNCOLORED = 0

IMAGE_PATH = '/home/pi/developer/eink-photo/image.jpg'
KATYA_PATH = '/home/pi/developer/eink-photo/katya.jpg'

epd = epd2in7b.EPD()
epd.init()

camera = PiCamera()
camera.resolution = (1024, 800)

frame_black = [0] * int((epd.width * epd.height / 8))
frame_red = [0] * int((epd.width * epd.height / 8))


def print_message(im, string):
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
    draw.text((im.size[0]-80, im.size[1]-20), string, font=font, fill=0)
    return im


def make_photo():
    print ('Making photo!')
    print ('Smile!')
    camera.start_preview()
    # Camera warm-up time
    sleep(2)
    camera.capture(IMAGE_PATH)

def get_image(image='/home/pi/developer/eink-photo/image.jpg'):
    im = Image.open(image)
    im.thumbnail((epd.height,epd.width),Image.LANCZOS)
    im = im.resize((epd.height, epd.width),resample=Image.LANCZOS)
    im = print_message(im,'Smile!')
    return im.transpose(Image.ROTATE_90)

def update_display(im):
    frame_black = epd.get_frame_buffer(im)
    #frame_red= epd.get_frame_buffer(im)
    epd.display_frame(frame_black, frame_red)

def get_keys():
    while True:
        key1state = GPIO.input(key1)
        key2state = GPIO.input(key2)
        key3state = GPIO.input(key3)
        key4state = GPIO.input(key4)

        if key1state == False:
            print('Key1 Pressed')
            make_photo()
            im = get_image()
            update_display(im)
            del im
            time.sleep(0.2)
        if key2state == False:
            print('Key2 Pressed')
            im = get_image(KATYA_PATH)
            update_display(im)
            time.sleep(0.2)
        if key3state == False:
            print('Key3 Pressed')
            print('Showing picture of nice lady')
            im = get_image(KATYA_PATH)
            update_display(im)
            del im
            time.sleep(0.2)
        if key4state == False:
            print('Key4 Pressed')
            make_photo()
            im = get_image()
            update_display(im)
            del im
            #updateDisplay('Key4 pressed')
            time.sleep(0.2)

if __name__ == '__main__':
    get_keys()
