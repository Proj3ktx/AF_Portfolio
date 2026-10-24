#!/usr/bin/env python3
"""Optional SIMULATION-ONLY timed-motion comparison; no pickup controller.

Only use in the baseline scene started with launch_demo.sh. It commands
0.05 m/s for 2 simulation seconds without reading odometry, then sends zero.
This is open-loop with respect to position. The displacement is not verified.
"""
import os,time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TimedMove(Node):
    def __init__(self):
        super().__init__('open_loop_timed_demo')
        self.declare_parameter('confirm_simulation',False)
        if not self.get_parameter('confirm_simulation').value or not self.get_parameter('use_sim_time').value:
            raise RuntimeError('Requires confirm_simulation:=true and use_sim_time:=true. Simulation only.')
        if os.environ.get('ROS_LOCALHOST_ONLY')!='1':raise RuntimeError('Set ROS_LOCALHOST_ONLY=1 first.')
        self.pub=self.create_publisher(Twist,'/cmd_vel',10)
        self.start=None;self.done=False;self.timer=self.create_timer(.05,self.tick)
    def tick(self):
        if self.done:return
        if self.count_publishers('/cmd_vel')>1:
            self.get_logger().error('Another velocity publisher is active. Stop the automatic controller first.')
            self.done=True;self.pub.publish(Twist());return
        now=self.get_clock().now().nanoseconds*1e-9
        if self.start is None:self.start=now
        msg=Twist()
        if now-self.start<2.:msg.linear.x=.05
        else:self.done=True
        self.pub.publish(msg)

def main():
    rclpy.init();node=TimedMove();wall=time.monotonic()
    try:
        while rclpy.ok() and not node.done and time.monotonic()-wall<15:
            rclpy.spin_once(node,timeout_sec=.1)
    finally:
        for _ in range(5):node.pub.publish(Twist());time.sleep(.05)
        node.destroy_node();rclpy.shutdown()
if __name__=='__main__':main()
