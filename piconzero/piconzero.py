#!/usr/bin/python3

#MIT License

#Copyright (c) 2017 Keith Ellis

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.



# Python library for 4tronix Picon Zero
# https://4tronix.co.uk/store/index.php?rt=product/product&product_id=552
# This code is based on the samplw code provided by 4Tronix but it has been
# built into a number of classes.

# Currently there is a base class 'Motor_Controller', this handles all the 
# I2C communication

# Two other classes are 'Motor' and 'Robot', both inherrit from 'Motor_Controller'
# Motor provides a number of methods for controlling a single motor, i.e.
# forward(speed), reverse(speed) etc.  Speeds are floats from 1 for forwards,
# 0 for stop and -1 for reverse, this is akin to GPIOZero. 
#


# robot class to drive motors using the 4Tronix picon zero motor driver

import smbus
import time


class Motor_Controller(object):
	def __init__(self, addr = None, debug = None):
		''' base class which handles the communications with the 
		4Tronix Picon Zero motor controller
		The motor controller is hard coded to I2C address 0x22, but
		add allows this to be changed if needed.

		debug should be set to True to get more debuggin info, if None
		debug info will be limited
		'''
		if addr == None:
			self.addr = 0x22
		else:
			self.addr = addr
		self.retries = 4
		self.bus = smbus.SMBus(1)
		self.motorA = 0
		self.motorB = 1
		if debug == None:
			self.debug = False
		else:
			self.debug = debug	
		self.reset = 20
		self.reset_board()

	def reset_board(self):
		''' call to reset the board, altomatically called upon
		initilisation
		'''
		self.send_command(self.reset, 0)

	def cleanup(self):
		self.reset()

	def read_command(self, command):
		''' Method to read info from the Picon Zero board
		'''
		for i in range(self.retries):
			try:
				rval = bus.read_word_data(self.addr, command)
				return [rval/256, rval%256]
			except:
				if self.debug:
					print("Error in reading command")

	def send_command(self, command, value):
		''' Method to send commands and values to the Picon Zero board
		'''
		value = int(value)
		for i in range(self.retries):
			try:
				self.bus.write_byte_data(self.addr, command, value)
				break
			except:
				if self.debug:
					print("Error in sending command")
					raise

	def get_revision(self):
		''' Method to return the revision information from the 
		Picon Zero board
		'''
		return read_command(0)
		
class Motor(Motor_Controller):
	''' Super class of Motor_Controller to control motors, two motors
	can be driven with the Picon Zero board so it is possible to have
	two instances of this class.

	addr is the I2C address of the Picon Zero motor controller
	debug if set to True enables debug messages
	motor is either 0 or 1, depending upon which motor you want
	to drive
	'''
	def __init__(self, motor, addr= None, debug = None):
		if addr == None:
			self.addr = 0x22
		else:
			self.addr = addr
		if debug == None:
			self.debug = False
		else:
			self.debug = debug
		self.motor = motor

		super(Motor, self).__init__(self.addr, self.debug)

		self.speed = 0
		self.stop()

	def scale_speed(self, speed):
		''' Scales the speed from the 1 to -1 used to the 127 to -127
		s used by the Piconzero board.
		Used internally, should not need to be called externally.
		'''
		return speed * 127


	def forward(self, speed):
		''' Drive motor forward 
		Speed range is 0 for stop
		through to 1 for full speed forwards.
		Speed is a float, so intermediate speeds can be fractions
		of 1, for example, 50% speed would be 0.5
		'''
		if speed > 1:
			self.speed = 1
		elif speed < 0:
			self.speed = 0
		else:
			self.speed = speed
		self.send_command(self.motor, self.scale_speed(self.speed))

	def reverse(self, speed):
                ''' Drive motor backwards
                Speed range is 0 for stop
                through to 1 for full speed reverse.
                Speed is a float, so intermediate speeds can be fractions
                of 1, for example, 50% speed would be 0.5
		'''
		speed *= -1		
		if speed < -1:
			self.speed = -1
		elif speed  > 0:
			self.speed = 0
		else:
			self.speed = speed
		self.send_command(self.motor, self.scale_speed(self.speed))
	
	def set_motor(self, speed):
		''' Speed range is 1 through to -1
		Allows motors to be set anywhere from full speed
		forwards to full speed reverse with a single
		command, this is good if using an analogue stick to control
		motor speed
		'''
		if speed > 1:
			self.speed = 1
		elif speed < -1:
			self.speed = -1
		else: 
			self.speed = speed
		self.send_command(self.motor, self.scale_speed(self.speed))

	def stop(self):
		''' Stops motor
		'''
		self.speed = 0
		self.send_command(self.motor, 0)

	def get_speed(self):
		''' Read the current speed back
		'''
		return self.speed


class Robot(Motor_Controller):
	''' 
	Class representing a two wheel drive robot or a 4 wheel
	drive skid/steer robot.  It expands on the Motor_Controller class
	and assmes motor 0 is the left motor and motor 1 is the
	right motor
	'''	

	def __init__(self, addr = None, debug = False):
		if addr == None:
			self.addr = 0x22		
		else:
			self.addr = addr
		self.debug = debug
		super(Robot, self).__init__(self.addr, self.debug)

		self.left_motor = Motor(self.motorA)
		self.right_motor = Motor(self.motorB)
		self.stop()


	def forward(self, speed):
		self.left_motor.forward(speed)
		self.right_motor.forward(speed)

	def reverse(self, speed):
		self.left_motor.reverse(speed)
		self.right_motor.reverse(speed)

	def stop(self):
		self.left_motor.stop()
		self.right_motor.stop()

	def spin_left(self, speed):
		self.left_motor.reverse(speed)
		self.right_motor.forward(speed)

	def spin_right(self, speed):
		self.left_motor.forward(speed)
		self.right_motor.reverse(speed)

	def turn_left(self, speed):
		self.left_motor.stop()
		self.right_motor.forward(speed)

	def turn_right(speed):
		self.left_motor.forward(speed)
		self.right_motor.stop()
		
	def set_motors(self, left_speed, right_speed):
		self.left_motor.set_motor(left_speed)
		self.right_motor.set_motor(right_speed)

	def get_speed(self):
		return[self.left_motor.speed, self.right_motor.speed]


if __name__ == '__main__':
	import sys
	import time

	print("Tesing picon Zero motor conotrller")
	print("Test options are: ")
	print("1 - test Motor A")
	print("2 - test Motor B")
	print("3 - test Robot, i.e. both motors")
	response = input("Select option, x = Exit - ")


	
	def test_motor(motor):
		#Create mote instance
		print("Testing motor {0}".format(motor))
		print("Creating motor instance")
		motor =Motor(motor = motor, debug = True)
		print("Motor speed is {0}".format(motor.get_speed()))
		time.sleep(5)

		print("1/2 speed forward")
		motor.forward(0.5)
		print("Motor speed is {0}".format(motor.get_speed()))
		time.sleep(5)

		print("Full speed forward") 
		motor.forward(1)
		print("Motor speed is {0}".format(motor.get_speed()))
		time.sleep(5)

		print("Motor stop")
		motor.stop()
		print("Motor speed is {0}".format(motor.get_speed()))
		time.sleep(5)

		print("1/2 speed reverse")
		motor.reverse(0.5)
		print("Motor speed is {0}".format(motor.get_speed()))
		time.sleep(5)

		print("Full speed reverse") 
		motor.reverse(1)
		print("Motor speed is {0}".format(motor.get_speed()))
		time.sleep(5)

		print("Motors stoped")
		motor.stop()

	def motorA():
		test_motor(0)

	def motorB():
		test_motor(1)

	def robot():
		robot = Robot(debug = True)
		print("Robot speed = {0}".format(robot.get_speed()))
		robot.stop()
		time.sleep(5)

		print("1/2 speed forward")
		robot.forward(0.5)
		print("Robot speed is {0}".format(robot.get_speed()))
		time.sleep(5)

		print("Full speed forward")
		robot.forward(1)
		print("Robot speed is {0}".format(robot.get_speed()))
		time.sleep(5)

		print("Robot Stop")
		robot.stop()
		print("Robot speed is {0}".format(robot.get_speed()))
		time.sleep(5)

		print("1/2 speed reverse")
		robot.reverse(0.5)
		print("Robot speed is {0}".format(robot.get_speed()))
		time.sleep(5)

		print("Full speed reverse")
		robot.reverse(1)
		print("Robot speed is {0}".format(robot.get_speed()))
		time.sleep(5)

		print("Robot stop")
		robot.stop()
		print("Robot speed is {0}".format(robot.get_speed()))



	while True:
		if response == "1":
			motorA()
			break
		elif response == "2":
			motorB()
			break
		elif response == "3":
			robot()
			break
		elif response.lower() =="x":
			sys.exit 