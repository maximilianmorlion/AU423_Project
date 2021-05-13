#!/usr/bin/env python

from __future__ import print_function

import threading

import roslib; roslib.load_manifest('custom_control')
import rospy

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import sys, select, termios, tty

msg = """
Reading from the keyboard  and Publishing to Twist and Joint Velocity Controller!
----------------------------------
Move robot : 
forward = z
backward = s
turn right = d
turn left = q

a : increase speed by x1.1
e : decrease speed by x0.9


Move arms :
Arm1 : t and g
Arm2 : y and h
Arm3 first axis : u and j 
Arm3 second axis : i and k
End effector prismatic : o and l

---------------------------

"""

moveBindings = {
        'z':(1,0,0,0,0,0,0),
        'q':(0,1,0,0,0,0,0),
        's':(-1,0,0,0,0,0,0),
        'd':(0,-1,0,0,0,0,0),

        't':(0,0,0.01,0,0,0,0),
        'g':(0,0,-0.01,0,0,0,0),

        'y':(0,0,0,0.01,0,0,0),
        'h':(0,0,0,-0.01,0,0,0),

        'u':(0,0,0,0,0.01,0,0),
        'j':(0,0,0,0,-0.01,0,0),

        'i':(0,0,0,0,0,0.01,0),
        'k':(0,0,0,0,0,-0.01,0),

        'o':(0,0,0,0,0,0,100),
        'l':(0,0,0,0,0,0,-100),

    }
    
speedBindings={
        'a':(1.1,1.1),
        'e':(0.9,0.9),
    }

limit = [-1.3,1.3,-1.57,1.57,-0.785,0.785,-0.785,0.785,-50,50]
#position limit end efffector = -0.02,0.03

class PublishThread(threading.Thread):
    def __init__(self, rate):
        super(PublishThread, self).__init__()
        self.publisher = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        self.cmdArm1Pub = rospy.Publisher("robot_project/arm1_position_controller/command",Float64 ,queue_size=1)
        self.cmdArm2Pub = rospy.Publisher("robot_project/arm2_position_controller/command",Float64 ,queue_size=1)
        self.cmdArm2bisPub = rospy.Publisher("robot_project/arm2bis_position_controller/command",Float64 ,queue_size=1)
        self.cmdArm3Pub = rospy.Publisher("robot_project/arm3_position_controller/command",Float64 ,queue_size=1)
        self.cmdEndeffectorPub = rospy.Publisher("robot_project/end_effector_effort_controller/command",Float64 ,queue_size=1)

        self.x = 0.0
        self.th = 0.0
        self.t1= 0.0
        self.t2= 0.0
        self.t3= 0.0
        self.t4 = 0.0
        self.l = 50.0
        self.speed = 0
        self.turn = 0
        self.joint_speed = 10
        self.condition = threading.Condition()
        self.done = False

        # Set timeout to None if rate is 0 (causes new_message to wait forever
        # for new data to publish)
        if rate != 0.0:
            self.timeout = 1.0 / rate
        else:
            self.timeout = None

        self.start()

    def wait_for_subscribers(self):
        i = 0
        while not rospy.is_shutdown() and self.publisher.get_num_connections() == 0:
            if i == 4:
                print("Waiting for subscriber to connect to {}".format(self.publisher.name))
            rospy.sleep(0.5)
            i += 1
            i = i % 5
        if rospy.is_shutdown():
            raise Exception("Got shutdown request before subscribers connected")

    def update(self,x,th,t1,t2,t3,t4,l):
        self.condition.acquire()
        self.x = x
        self.th = th
        
        if self.t1 >= limit[0] and self.t1 <= limit[1]:
        	if (self.t1 == limit[1] and t1 == 0.01) or (self.t1 == limit[0] and t1 == -0.01):
        		print("Limit reached")
        	else :
        		self.t1 += t1
        		
        elif self.t1 < limit[0]:
        	self.t1= limit[0]
        elif self.t1 > limit[1]:
        	self.t1 = limit[1]
        	
        if self.t2 >= limit[2] and self.t2 <= limit[3]:
        	if (self.t2 == limit[3] and t2 == 0.01) or (self.t2 == limit[2] and t2 == -0.01):
        		print("Limit reached")
        	else :
        		self.t2 += t2
        elif self.t2 < limit[2]:
        	self.t2 = limit[2]
        elif self.t2 > limit[3]:
        	self.t2 = limit[3]
        	
        if self.t3 >= limit[4] and self.t3 <= limit[5]:
        	if (self.t3 == limit[5] and t3 == 0.01) or (self.t3 == limit[4] and t3 == -0.01):
        		print("Limit reached")
        	else :
        		self.t3 += t3
        elif self.t3 < limit[4]:
        	self.t3 = limit[4]
        elif self.t3 > limit[5]:
        	self.t3 = limit[5]
        if self.t4 >= limit[6] and self.t4 <= limit[7]:
        	if (self.t4 == limit[7] and t4 == 0.01) or (self.t4 == limit[6] and t4 == -0.01):
        		print("Limit reached")
        	else :
        		self.t4 += t4
        elif self.t4 < limit[6]:
        	self.t4 = limit[6]
        elif self.t4 > limit[7]:
        	self.t4 = limit[7]
        if self.l >= limit[8] and self.l <= limit[9]:
        	
        	if (self.l == limit[9] and l == 100) or (self.l == limit[8] and l == -100):
        		print("Limit reached")
        	else :
        		self.l += l	
        elif self.l < limit[8]:
        	self.l = limit[8]
        elif self.l > limit[9]:
        	self.l = limit[9]	

        self.speed = speed
        self.turn = turn
        # Notify publish thread that we have a new message.
        self.condition.notify()
        self.condition.release()

    def stop(self):
        self.done = True
        self.update(0,0,0,0,0,0,0)
        self.join()

    def run(self):
        twist = Twist()
        cmdArm1 = Float64()
        cmdArm2 = Float64()
        cmdArm2bis = Float64()
        cmdArm3 = Float64()
        cmdEndeffector = Float64()
        while not self.done:
            self.condition.acquire()
            # Wait for a new message or timeout.
            self.condition.wait(self.timeout)

            # Copy state into twist message.
            twist.linear.x = self.x * self.speed
            twist.linear.y = 0
            twist.linear.z = 0
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = self.th * self.speed
            cmdArm1.data = self.t1
            cmdArm2.data = self.t2
            cmdArm2bis.data = self.t3
            cmdArm3.data = self.t4
            cmdEndeffector.data = self.l
            self.condition.release()

            # Publish.
            self.publisher.publish(twist)
            self.cmdArm1Pub.publish(cmdArm1)
            self.cmdArm2Pub.publish(cmdArm2)
            self.cmdArm2bisPub.publish(cmdArm2bis)
            self.cmdArm3Pub.publish(cmdArm3)
            self.cmdEndeffectorPub.publish(cmdEndeffector)

        # Publish stop message when thread exits.
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        cmdArm1.data = 0
        cmdArm2.data = 0
        cmdArm2bis.data = 0
        cmdArm3.data = 0
        cmdEndeffector.data = 0
        self.publisher.publish(twist)
        self.cmdArm1Pub.publish(cmdArm1)
        self.cmdArm2Pub.publish(cmdArm2)
        self.cmdArm2bisPub.publish(cmdArm2bis)
        self.cmdArm3Pub.publish(cmdArm3)
        self.cmdEndeffectorPub.publish(cmdEndeffector)

def getKey(key_timeout):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def vels(speed, turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('teleop_twist_keyboard')

    speed = rospy.get_param("~speed", 1.0)
    turn = rospy.get_param("~turn", 1.0)
    repeat = rospy.get_param("~repeat_rate", 10)
    key_timeout = rospy.get_param("~key_timeout", 0.6)
    if key_timeout == 0.0:
        key_timeout = None

    pub_thread = PublishThread(repeat)

    x = 0
    th = 0
    t1=0
    t2=0
    t3=0
    t4=0
    l=50.0
    status = 0

    try:
        pub_thread.wait_for_subscribers()
        pub_thread.update(x, th, t1,t2,t3,t4,l)

        print(msg)
        # print(vels(speed,turn))
        while(1):
            key = getKey(key_timeout)
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                th = moveBindings[key][1]
                t1 = moveBindings[key][2]
                t2 =  moveBindings[key][3]
                t3 =  moveBindings[key][4]
                t4 =  moveBindings[key][5]
                l = moveBindings[key][6]

            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][0]
                print(vels(speed,turn))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            else:
                # Skip updating cmd_vel if key timeout and robot already
                # stopped.
                if key == '' and x == 0 and th == 0  and t1 == 0 and t2 == 0 and t3 == 0 and t4 ==0 and l == 0:
                    continue
                x = 0
                th = 0
                t1=0
                t2=0
                t3=0
                t4 = 0
                l=0
                if (key == '\x03'):
                    break
 
            pub_thread.update(x, th, t1,t2,t3,t4,l)

    except Exception as e:
        print(e)

    finally:
        pub_thread.stop()

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
