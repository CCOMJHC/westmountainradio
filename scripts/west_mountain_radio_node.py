#!/usr/bin/env python
#
# Val Schmidt
# Centeer for Coastal and Ocean Mapping
# University of New Hamsphire

import _mypath
import sys
import rospy
import rosbag
#from time import sleep
from westmountainradio.msg import Circuit
import westmountainradio.westmountainradio as wmr
import datetime
import sys

verbose = False
if sys.argv[1] == "verbose":
    verbose = True 
wmr12_address = "192.168.100.212"
wmr24_address = "192.168.100.224"

def create_ros_bag_for_node(node):
    dts = datetime.datetime.utcnow()
    bag_filename = "nodes/" +  node.name[1:] + "-" + dts.isoformat().replace(':','-') + ".bag"
    rospy.loginfo("Opening BAG: " + bag_filename)
    try:
        bag = rosbag.Bag(bag_filename,'w')
    except:
        rospy.loginfo("Error Opening bag file for " + node.name[1:])
    
    return bag

def publisher():
    
    pub = rospy.Publisher('westmountainradio',Circuit,queue_size = 1000)
    rospy.init_node('publisher',anonymous=True)
    rate = rospy.Rate(1)

    #bag = create_ros_bag_for_node(pub)

    while not rospy.is_shutdown():
        circuits = get_circuit_data()
        
        for c in circuits:
            C = Circuit()
            #C.header.timestamp = rospy.get_time()
            C.header.stamp.secs = int(c.updatetime)
            C.header.stamp.nsecs = c.updatetime - int(c.updatetime)
            C.name = c.cktname
            C.status = c.status == "1"
            C.voltage= float(c.voltage)
            C.current = float(c.current)

            rospy.loginfo(C)
            pub.publish(C)
            #bag.write(pub.name[1:],C)

        rate.sleep()        

    #bag.flush() 
    #bag.close()
 
def get_circuit_data():
    wmr12 = wmr.west_mountain_radio(wmr12_address)        
    wmr24 = wmr.west_mountain_radio(wmr24_address)

    if verbose:
        print wmr24.url
    wmr24.get_names()
    wmr24.get_status()
    #wmr24.print_status()
    #wmr24.print_log(logfile)
    #sleep(1)
    if verbose:
        print wmr12.url
 
    wmr12.get_names()
    wmr12.get_status()
    #wmr12.print_status()
    #wmr12.print_log(logfile)

    return wmr24.circuits + wmr12.circuits
        
if __name__ == '__main__':
    
    try: 
        publisher()
    except rospy.ROSInterruptException:
        pass
    
