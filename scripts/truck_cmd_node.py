#!/usr/bin/env python
import signal
import dictionaries
import atexit
import time
import rospy
from driving import Truck
from hw_api_ackermann.msg import AckermannDrive


class TruckNode:
    def __init__(self):

        dictionaries.generateDictionaries()

        self.last_message_time = 0
        self.last_speed = 0
		
        self.truck = Truck()
        self.truck.reset()
        self.truck.update()

        rospy.init_node('truck_cmd_node', anonymous=True)
        rospy.Subscriber("truck_cmd", AckermannDrive, self.callback)



    def callback(self, data):
        phi = data.steering_angle
        v = data.speed


        self.last_message_time = rospy.get_time()
        self.last_speed = v

        steering_cmd = dictionaries.getSteeringCmd(phi)
        speed_cmd = dictionaries.getSpeedCmd(v)


        self.truck.setSteering(steering_cmd)
        self.truck.setSpeed(speed_cmd)
        self.truck.update()
			

    def spin(self): 

        #rospy.spin()    
        while not rospy.is_shutdown():
            #if truck is moving and last message was a long time ago, stop truck
            if self.last_speed >= 0:
                if rospy.get_time() - self.last_message_time > 1:
                    print "didnt receive a message in 1 sec, resetting"
                    self.truck.reset()
                    self.truck.update()
            
            rospy.sleep(0.1)

def interruptHandler(sig, frame):
	signal.signal(signal.SIGINT, signal.SIG_IGN)
	print("Interrupted, reset servo...")
	# Return to neutral
	truck = TruckNode()
	truck.truck.reset()
	truck.truck.update()
	time.sleep(0.4)
	exit(0)

def exit_handler():
    truck = TruckNode()
    truck.truck.reset()
    truck.truck.update()
    exit(0)

signal.signal(signal.SIGINT, interruptHandler)
atexit.register(exit_handler)

if __name__ == '__main__':
	t = TruckNode()
    t.spin()


