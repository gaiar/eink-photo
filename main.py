from PIL import Image, ImageDraw
from PIL import Image
import hitherdither
from hitherdither.palette import rgb2hex
import numpy as np
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

WHITE = 0
BLACK = 1
RED = 2

w = rgb2hex(255, 255, 255)
b = rgb2hex(0, 0, 0)
r = rgb2hex(255, 0, 0)

palette = hitherdither.palette.Palette(
		[w, b, r]
)


def print_message(im, string):
	draw = ImageDraw.Draw(im)
	font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
	draw.text((im.size[0] - 80, im.size[1] - 20), string, font=font, fill=0)
	return im


def get_dith_image(im):
	#return hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering(im, palette, order=8)
	return hitherdither.diffusion.error_diffusion_dithering(im, palette, method='floyd-steinberg')


def get_red_buf(im):
	img_np = np.asarray(im, dtype=np.uint8)
	return np.packbits(np.where(img_np == RED, 1, 0)).tolist()


def get_black_buf(im):
	img_np = np.asarray(im, dtype=np.uint8)
	return np.packbits(np.where(img_np == BLACK, 0, 1)).tolist()


def get_buffers(im):
	img_np = np.asarray(im, dtype=np.uint8)
	return np.packbits(np.where(img_np == BLACK, 1, 0)).tolist(), np.packbits(np.where(img_np == RED, 1, 0)).tolist()


def make_photo():
	print('Making photo!')
	print('Smile!')
	camera.start_preview()
	# Camera warm-up time
	sleep(5)
	camera.capture(IMAGE_PATH)


def get_image(image='/home/pi/developer/eink-photo/image.jpg'):
	im = Image.open(image)
	im.thumbnail((epd.height, epd.width), Image.LANCZOS)
	im = im.resize((epd.height, epd.width), resample=Image.LANCZOS)
	im = print_message(im, 'Smile!')
	return im.transpose(Image.ROTATE_90)


def update_display(im, fr_black=None, fr_red=None):
	if (fr_black is None):
		frame_black = epd.get_frame_buffer(im)
	else:
		frame_black = fr_black

	if (fr_red is not None):
		#print()
		frame_red = fr_red

	#print(frame_black,frame_red)

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
			print('Showing color picture of nice lady')
			im = get_image(KATYA_PATH)
			im_dith = get_dith_image(im)
			fr_black, fr_red = get_buffers(im_dith)
			#print(fr_black, fr_red)
			update_display(im, fr_black, fr_red)
			del im
			time.sleep(0.2)

		if key4state == False:
			print('Key4 Pressed')
			make_photo()
			print('Photo done!')
			im = get_image()
			fr_black, fr_red = get_buffers(get_dith_image(im))
			update_display(im,fr_black, fr_red)
			del im
			# updateDisplay('Key4 pressed')
			time.sleep(0.2)


if __name__ == '__main__':
	get_keys()
