#!/usr/bin/env python

import json
import colorsys
import os
import threading
import math
import colorsys
from time import sleep
from datetime import datetime
from gpiozero import CPUTemperature
import blinkt
from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS
from random import randint
from jsmin import jsmin

blinkThread = None
crntColors = None
globalRed = 0
globalGreen = 0
globalBlue = 0
globalBrightness = 0
globalLastCalled = None
globalLastCalledApi = None
globalStatus = None
globalStatusOverwrite = False

# get the width and height of the hardware and set it to portrait if its not
width = 8

class MyFlaskApp(Flask):
	def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
		if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
			with self.app_context():
				startupRainbow()
		super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__, static_folder='frontend/build', static_url_path='/')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def setColor(r, g, b, brightness=0.5, speed=None):
	global crntColors
	setPixels(r, g, b, brightness)
	blinkt.show()

	if speed is not None and speed != '':
		crntT = threading.currentThread()
		blinkt.clear()
		while getattr(crntT, "do_run", True):
			setPixels(r, g, b, brightness)
			blinkt.show()
			sleep(speed)
			blinkt.clear()
			blinkt.show()
			sleep(speed)


def setPixels(r, g, b, brightness=0.5):
	global globalBrightness, globalBlue, globalGreen, globalRed

	globalRed = r
	globalGreen = g
	globalBlue = b

	if brightness is not None:
		globalBrightness = brightness
		blinkt.setBrightness(brightness)

	blinkt.set_colour(r, g, b)


def switchOn():
	rgb = colorsys.hsv_to_rgb(randint(0, 360), 100, 100)
	blinkThread = threading.Thread(target=setColor, args=(rgb[0], rgb[1], rgb[2]))
	blinkThread.do_run = True
	blinkThread.start()


def switchOff():
	global blinkThread, globalBlue, globalGreen, globalRed
	globalRed = 0
	globalGreen = 0
	globalBlue = 0
	if blinkThread is not None:
		blinkThread.do_run = False
	blinkt.clear()
	blinkt.off()


def halfBlink():
	blinkt.show()
	sleep(0.8)
	blinkt.clear()
	blinkt.show()
	sleep(0.2)



def displayRainbow(brightness, speed, run=None):
	global crntColors
	if speed is None:
		speed = 0.01
	if brightness is None:
		brightness = 0.5
	crntT = threading.currentThread()
	i = 0.0
	offset = 30
	while getattr(crntT, "do_run", True):
		i = i + 0.3
		blinkt.setBrightness(brightness)
		for x in range(0, width):
            #ddd

		blinkt.show()
		sleep(speed)


def setTimestamp():
	global globalLastCalled
	globalLastCalled = datetime.now()


# API Initialization
@app.route('/', methods=['GET'])
def root():
	print(app.static_folder)
	return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/on', methods=['GET', 'POST'])
def apiOn():
	global globalStatusOverwrite, globalStatus, globalLastCalledApi
	globalStatusOverwrite = False
	globalStatus = 'on'
	globalLastCalledApi = '/api/on'
	switchOff()
	switchOn()
	setTimestamp()
	return make_response(jsonify({}))


@app.route('/api/off', methods=['GET', 'POST'])
def apiOff():
	global crntColors, globalStatusOverwrite, globalStatus, globalLastCalledApi
	globalStatusOverwrite = False
	globalStatus = 'off'
	globalLastCalledApi = '/api/off'
	crntColors = None
	switchOff()
	setTimestamp()
	return make_response(jsonify({}))


@app.route('/api/switch', methods=['POST'])
def apiSwitch():
	global blinkthread, globalStatusOverwrite, globalStatus, globalLastCalledApi

	if globalStatusOverwrite:
		return make_response(jsonify({}))

	globalLastCalledApi = '/api/switch'
	switchOff()
	content = json.loads(jsmin(request.get_data(as_text=True)))
	red = content.get('red', None)
	green = content.get('green', None)
	blue = content.get('blue', None)
	if red is None or green is None or blue is None:
		return make_response(jsonify({'error': 'red, green and blue must be present and can\' be empty'}), 500)

	if red == 0 and green == 144 and blue == 0:
		globalStatus = 'Available'
	elif red == 255 and green == 191 and blue == 0:
		globalStatus = 'Away'
	elif red == 179 and green == 0 and blue == 0:
		globalStatus = 'Busy'
	else:
		globalStatus = None

	brightness = content.get('brightness', None)
	speed = content.get('speed', None)
	blinkThread = threading.Thread(target=setColor, args=(red, green, blue, brightness, speed))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/available', methods=['GET', 'POST'])
def availableCall():
	global globalStatusOverwrite, globalStatus, globalLastCalledApi, blinkThread
	globalStatusOverwrite = True
	globalStatus = 'Available'
	globalLastCalledApi = '/api/available'
	switchOff()
	blinkThread = threading.Thread(target=setColor, args=(0, 144, 0))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/busy', methods=['GET', 'POST'])
def busyCall():
	global globalStatusOverwrite, globalStatus, globalLastCalledApi, blinkThread
	globalStatusOverwrite = True
	globalStatus = 'Busy'
	globalLastCalledApi = '/api/busy'
	switchOff()
	blinkThread = threading.Thread(target=setColor, args=(179, 0, 0))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/away', methods=['GET', 'POST'])
def awayCall():
	global globalStatusOverwrite, globalStatus, globalLastCalledApi, blinkThread
	globalStatusOverwrite = True
	globalStatus = 'Away'
	globalLastCalledApi = '/api/away'
	switchOff()
	blinkThread = threading.Thread(target=setColor, args=(255, 191, 0))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/reset', methods=['GET', 'POST'])
def resetCall():
	global globalStatusOverwrite, globalStatus, globalLastCalledApi, blinkThread
	globalStatusOverwrite = False
	return make_response(jsonify())


@app.route('/api/rainbow', methods=['POST'])
def apiDisplayRainbow():
	global blinkThread, globalStatus, globalLastCalledApi
	globalStatus = 'rainbow'
	globalLastCalledApi = '/api/rainbow'
	switchOff()
	data = request.get_data(as_text=True)
	content = json.loads(jsmin(request.get_data(as_text=True)))
	brightness = content.get('brightness', None)
	speed = content.get('speed', None)
	blinkThread = threading.Thread(target=displayRainbow, args=(brightness, speed, None))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())


@app.route('/api/status', methods=['GET'])
def apiStatus():
	global globalStatusOverwrite, globalStatus, globalBlue, globalGreen, globalRed, globalBrightness, \
		globalLastCalled, globalLastCalledApi, width, height, blinkt

	cpu = CPUTemperature()
	return jsonify({
		'red': globalRed, 
		'green': globalGreen,
		'blue': globalBlue,
		'brightness': globalBrightness,
		'lastCalled': globalLastCalled,
		'cpuTemp': cpu.temperature,
		'lastCalledApi': globalLastCalledApi, 
		'height': height,
		'width': width,
		'blinkt': blinkt.getType(),
		'status': globalStatus,
		'statusOverwritten': globalStatusOverwrite
	})


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)


def startupRainbow():
	global blinkThread
	blinkThread = threading.Thread(target=displayRainbow, args=(1, 0.1, 1))
	blinkThread.do_run = True
	blinkThread.start()


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)