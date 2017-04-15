# Picon-Zero
Python3 library for 4Tronix Picon Zero motor controller based on sample code from [4Tronix](https://4tronix.co.uk/store/index.php?rt=product/product&product_id=552)

To use this library you will need a 4Tronix Pricon Zero motor controller

Copy ```piconzero.py``` into your working directory

Enable I2C with ```sudo raspi-config``` 

* Select option 5 "Interfacing Options"
* Select option P5 "I2C" and enable
* reboot your Pi 

Install some tools

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python3-smbus python3-dev
    
Plug on the Picon Zero board and check you can communicate with it.

```i2cdetect -y 1```

if all goes well you should see the following

	pi@raspberrypi:~/piconzero $ i2cdetect -y 1
	     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
	00:          -- -- -- -- -- -- -- -- -- -- -- -- --
	10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	20: -- -- 22 -- -- -- -- -- -- -- -- -- -- -- -- --
	30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	70: -- -- -- -- -- -- -- --
	
Confirming the Picon Zero board has been found at i2C address 0x22


##Testing the library
The library must be in the same directory as your python3 file.

To check everything is running, ensure at least one motor is connected to the Picon Zero motor controller, the library has a basic check script which runs if it is called directly.

Ensure you are in the same directory as ```piconzero.py``` and run

	python3 piconzero.py
	
This should bring up a simple menu, 

	pi@raspberrypi:~/piconzero $ python3 piconzero.py
	Tesing picon Zero motor conotrller
	Test options are:
	1 - test Motor A
	2 - test Motor B
	3 - test Robot, i.e. both motors
	Select option, x = Exit -

If you have one motor connected, select either 1 or 2 and press enter, this should go through a sequence of spinning the motor forwards and backwards and different speeds.  If on first try your motor does not spin, try the other motor.

If you have two motors connected you can try option 3 to spin both motors at the same time.

If you want to see what is going on, open up ```piconzero.py``` and review the code towards the bottom, below the line ```if __name__ == '__main__':```

##Creating your own python3 code
If you want to create your own python3 code you need to import the piconzero library, add this import statement to the top of your script.

	import piconzero

###Using the Motor object
	
Then create a couple of motor objects

	leftmotor  = 0
	rightmotor = 1
	motorA = piconzero.Motor(motor = leftmotor, debug = True)
	motorB = piconzero.Motor(motor = rightmotor, debug = True)
	
We then have a few methods we can use to control the motors, these are

* ```motorA.forward(speed)``` where speed is from ```0``` to ```1```
* ```motorA.reverse(speed)``` where speed is from ```0``` to ```1```

or we can use a single method to control both forwards and reverse

* ```motorA.set_motor(speed)``` where speed is between ```-1``` and ```1```, ```-1``` being full speed reverse, ```0``` being stop and ```1``` being full speed forward.  You can of course use floats between ```-1``` and ```1```, for example, for 1/2 speed reverse set speed to ```-0.5```

###using the Robot object

Crete a robot object

	robot = piconzero.Robot()
	
The methods to control the robot are as follows:

* ```robot.forward(speed)```, in this method and all those that follow, speed works the same as for the motor objects
* ```robot.reverse(speed)```
* ```robot.stop()```
* ```robot.spin_left(speed)``` Spin on the spot, motors turn in opposite directions
* ```robot.spin_right(speed)```
* ```robot.turn_left(speed)``` A slower turn, one motor is stoped whilst the other turns forward
*  ```robot.turn_right(speed)```
*  ```robot.set_motors(left_speed, right_speed)``` As per ```set_motor(speed)``` this is good for controlling your robot with an analogue joypad