#!/usr/bin/env python3
"""Drive the CAD-based robot A -> B, attach a payload, return and release it.

Teaching model: ideal planar base motion, three articulated pitch joints and
parallel jaws. Attach/detach is an ideal grasp, not a force-controlled grasp.
SLAM runs independently and does not plan the waypoint path.
"""
import csv,json,math,time
from pathlib import Path
import numpy as np
import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist,PoseStamped
from nav_msgs.msg import Odometry,Path as PathMsg,OccupancyGrid
from sensor_msgs.msg import LaserScan,Imu,Image,JointState
from std_msgs.msg import String
from std_srvs.srv import Empty
from gazebo_msgs.msg import ModelStates,LinkStates,ContactsState
from gazebo_model_attachment_plugin_msgs.srv import Attach,Detach
from robot_kinematics import ik,CARRY,PICK,HOVER,JAW_CLOSED

def angle(a):return math.atan2(math.sin(a),math.cos(a))
def yaw(q):return math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
def smooth(u):
    u=max(0,min(1,u));return 10*u**3-15*u**4+6*u**5

class MobilePickupExperiment(Node):
    def __init__(self):
        super().__init__('mobile_pickup_experiment')
        defaults={'output_dir':'results/test','waypoints_flat':[0.,0.,.9,.25,1.8,.35,.9,.25,0.,0.],
                  'max_linear_speed':.16,'max_linear_accel':.12,'max_angular_speed':.7,
                  'position_tolerance':.004,'return_position_tolerance':.01,'obstacle_stop_distance':.18,'camera_sample_period':1.,'max_duration_sec':180.}
        for k,v in defaults.items():self.declare_parameter(k,v)
        self.cfg={k:self.get_parameter(k).value for k in defaults}
        self.out=Path(self.cfg['output_dir']);self.out.mkdir(parents=True,exist_ok=True);(self.out/'camera').mkdir(exist_ok=True)
        wp=self.cfg['waypoints_flat']
        if len(wp)!=10 or not all(math.isfinite(float(v)) for v in wp):
            raise ValueError('Use exactly five x,y pairs: A, middle, B, middle, A.')
        if list(wp[:2])!=[0.,0.] or list(wp[4:6])!=[1.8,.35] or list(wp[8:])!=[0.,0.]:
            raise ValueError('This lesson keeps stations at A=(0,0) and B=(1.8,0.35). Edit only the two middle pairs.')
        self.wp=list(zip(wp[::2],wp[1::2]))
        self.pose=None;self.object=None;self.grasp=None;self.front=float('inf');self.last_scan=-1e9
        self.stage='WAITING';self.stage_t=0.;self.start=None;self.done=False;self.reason=None;self.future=None
        self.tool=CARRY.copy();self.arm=ik(self.tool);self.jaw=0.;self.tool_from=self.tool.copy();self.jaw_from=self.jaw;self.wheels=[0.]*4
        self.cmd=np.zeros(3);self.prev_acc=np.zeros(3);self.last_t=None;self.last_camera=-1e9
        self.last_odom_log=-1e9;self.last_path=-1e9
        self.rows=[];self.lidar=[];self.imu=[];self.objects=[];self.events=[];self.frames=[];self.maps=[];self.joints=[]
        self.latest_map=None;self.path=PathMsg();self.path.header.frame_id='odom';self.bridge=CvBridge()
        self.hold_pose=None;self.video=None;self.overview_count=0;self.overview_stage=None
        self.close_video=None;self.close_stage=None;self.contact_rows=[];self.contact_messages=0;self.unexpected_contacts=0;self.last_contact=None
        self.jaw_contacts={'left':-1e9,'right':-1e9}
        self.velocity_pub=self.create_publisher(Twist,'/cmd_vel',10)
        self.joint_pub=self.create_publisher(JointState,'/arm_wheel_commands',10)
        self.event_pub=self.create_publisher(String,'/experiment/events',10)
        self.path_pub=self.create_publisher(PathMsg,'/experiment/path',10)
        self.sample_pub=self.create_publisher(Image,'/experiment/camera_sample',10)
        self.create_subscription(Odometry,'/odom',self.on_odom,1)
        self.create_subscription(LaserScan,'/scan',self.on_scan,qos_profile_sensor_data)
        self.create_subscription(Imu,'/imu',self.on_imu,qos_profile_sensor_data)
        self.create_subscription(Image,'/camera/image_raw',self.on_camera,qos_profile_sensor_data)
        self.create_subscription(Image,'/overview/image_raw',self.on_overview,qos_profile_sensor_data)
        self.create_subscription(Image,'/pickup_view/image_raw',self.on_closeup,qos_profile_sensor_data)
        self.create_subscription(ContactsState,'/experiment/contacts',self.on_contacts,10)
        self.create_subscription(ModelStates,'/gazebo/model_states',self.on_models,1)
        self.create_subscription(LinkStates,'/gazebo/link_states',self.on_links,1)
        self.create_subscription(OccupancyGrid,'/map',self.on_map,10)
        self.create_subscription(JointState,'/joint_states',self.on_joints,10)
        self.attach=self.create_client(Attach,'/gazebo/attach');self.detach=self.create_client(Detach,'/gazebo/detach')
        self.pause=self.create_client(Empty,'/pause_physics');self.unpause=self.create_client(Empty,'/unpause_physics')
        self.service_action=None;self.service_phase=None;self.service_deadline=0.
        self.wall_start=time.monotonic();self.timer=self.create_timer(.05,self.step)
    def begin_attachment(self,action):
        # Change constraints only while physics is paused. Service polling uses
        # wall time because the ROS simulation clock stops during this pause.
        self.service_action=action;self.service_phase='pause'
        self.future=self.pause.call_async(Empty.Request())
        self.service_deadline=time.monotonic()+5.
        self.transition('ATTACHING' if action=='attach' else 'DETACHING')
    def poll_attachment(self):
        if self.service_action is None or self.done:return
        if not self.future.done():
            if time.monotonic()>self.service_deadline:
                self.unpause.call_async(Empty.Request());self.finish('FAILED_ATTACHMENT_SERVICE_TIMEOUT')
            return
        result=self.future.result()
        if result is None or (self.service_phase=='constraint' and not result.success):
            self.unpause.call_async(Empty.Request());self.finish('FAILED_ATTACHMENT_SERVICE');return
        if self.service_phase=='pause':
            if self.service_action=='attach':
                req=Attach.Request(joint_name='payload_grip',model_name_1='mobile_robot',link_name_1='grasp_link',model_name_2='payload',link_name_2='link')
                self.future=self.attach.call_async(req)
            else:
                self.future=self.detach.call_async(Detach.Request(joint_name='payload_grip',model_name_1='mobile_robot',model_name_2='payload'))
            self.service_phase='constraint'
        elif self.service_phase=='constraint':
            self.future=self.unpause.call_async(Empty.Request());self.service_phase='resume'
        else:
            action=self.service_action;self.service_action=None
            self.event('PAYLOAD_ATTACHED' if action=='attach' else 'PAYLOAD_RELEASED')
            self.transition('LIFT_B' if action=='attach' else 'RETRACT_A')
        self.service_deadline=time.monotonic()+5.
    def now(self):return self.get_clock().now().nanoseconds*1e-9
    def elapsed(self):return self.now()-(self.start if self.start is not None else self.now())
    def event(self,name,**data):
        e={'time_s':self.elapsed(),'event':name,**data};self.events.append(e)
        self.event_pub.publish(String(data=json.dumps(e)));self.get_logger().info(json.dumps(e))
    def transition(self,stage):
        self.stage=stage;self.stage_t=self.now();self.tool_from=self.tool.copy();self.jaw_from=self.jaw
        if stage=='APPROACH_B':self.hold_pose=(*self.wp[2],0.)
        if stage=='APPROACH_A':self.hold_pose=(*self.wp[4],math.pi)
        self.event(stage,robot_pose=self.pose,object_xyz=self.object)
    def on_odom(self,msg):
        p=msg.pose.pose;self.pose=(p.position.x,p.position.y,yaw(p.orientation))
        if self.start is None:return
        t=self.elapsed()
        if t-self.last_odom_log<.049:return
        self.last_odom_log=t
        self.rows.append([t,*self.pose,msg.twist.twist.linear.x,msg.twist.twist.linear.y,msg.twist.twist.angular.z,*self.cmd,self.stage])
        ps=PoseStamped();ps.header=msg.header;ps.pose=p;self.path.poses.append(ps)
        self.path.header.stamp=msg.header.stamp
        if t-self.last_path>.2:self.path_pub.publish(self.path);self.last_path=t
    def on_scan(self,msg):
        a=msg.angle_min+np.arange(len(msg.ranges))*msg.angle_increment;r=np.asarray(msg.ranges)
        valid=np.isfinite(r)&(r>=msg.range_min)&(r<=msg.range_max)
        forward=valid&(np.abs(a)<math.radians(25));self.front=float(r[forward].min()) if forward.any() else float('inf')
        self.last_scan=self.now()
        if self.start is not None:self.lidar.append([self.elapsed(),self.front,float(r[valid].min()) if valid.any() else float('nan'),float(r[valid].mean()) if valid.any() else float('nan'),int(valid.sum())])
    def on_imu(self,msg):
        if self.start is not None:self.imu.append([self.elapsed(),msg.angular_velocity.x,msg.angular_velocity.y,msg.angular_velocity.z,msg.linear_acceleration.x,msg.linear_acceleration.y,msg.linear_acceleration.z])
    def on_camera(self,msg):
        if self.start is None or self.now()-self.last_camera<self.cfg['camera_sample_period']:return
        self.last_camera=self.now();name=f'frame_{len(self.frames):04d}.jpg'
        try:
            im=self.bridge.imgmsg_to_cv2(msg,'bgr8');cv2.imwrite(str(self.out/'camera'/name),im,[cv2.IMWRITE_JPEG_QUALITY,90])
            self.frames.append([self.elapsed(),name,self.stage]);self.sample_pub.publish(msg)
        except Exception as exc:self.get_logger().warning(str(exc))
    def on_models(self,msg):
        if 'payload' in msg.name:
            p=msg.pose[msg.name.index('payload')].position;self.object=[p.x,p.y,p.z]
            if self.start is not None:self.objects.append([self.elapsed(),p.x,p.y,p.z,self.stage])
    def on_overview(self,msg):
        if self.start is None or self.done:return
        im=self.bridge.imgmsg_to_cv2(msg,'bgr8')
        if self.video is None:
            self.video=cv2.VideoWriter(str(self.out/'overview.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),10.,(im.shape[1],im.shape[0]))
            if not self.video.isOpened():self.get_logger().error('Overview video writer could not open')
        self.video.write(im);self.overview_count+=1
        if self.overview_stage!=self.stage:
            (self.out/'stage_images').mkdir(exist_ok=True)
            cv2.imwrite(str(self.out/'stage_images'/f'{len(self.events):02d}_{self.stage}.png'),im)
            self.overview_stage=self.stage
    def on_links(self,msg):
        if 'mobile_robot::grasp_link' in msg.name:
            p=msg.pose[msg.name.index('mobile_robot::grasp_link')].position;self.grasp=[p.x,p.y,p.z]
    def on_closeup(self,msg):
        if self.start is None or self.done:return
        im=self.bridge.imgmsg_to_cv2(msg,'bgr8')
        if self.close_video is None:self.close_video=cv2.VideoWriter(str(self.out/'pickup_closeup.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),10.,(im.shape[1],im.shape[0]))
        if not self.stage.startswith('RETURN') and self.stage not in ['APPROACH_A','LOWER_A','RELEASE','DETACHING','RETRACT_A','VERIFY']:self.close_video.write(im)
        if self.close_stage!=self.stage:
            (self.out/'closeup_images').mkdir(exist_ok=True);cv2.imwrite(str(self.out/'closeup_images'/f'{len(self.events):02d}_{self.stage}.png'),im);self.close_stage=self.stage
    def on_contacts(self,msg):
        if self.start is None or self.done:return
        self.contact_messages+=1
        for state in msg.states:
            names=(state.collision1_name,state.collision2_name)
            intentional=any('payload' in n for n in names) and any('_jaw' in n for n in names)
            depth=max(state.depths,default=0.)
            self.contact_rows.append([self.elapsed(),*names,depth,intentional,self.stage])
            if intentional:
                for side in ['left','right']:
                    if any(side+'_jaw' in n for n in names):self.jaw_contacts[side]=self.now()
            if not intentional and depth>.0001:
                self.unexpected_contacts+=1;self.last_contact=names
    def on_map(self,msg):
        self.latest_map=msg
        if self.start is not None:self.maps.append([self.elapsed(),msg.info.width,msg.info.height,sum(v>=0 for v in msg.data)])
    def on_joints(self,msg):
        if self.start is not None:self.joints.append([self.elapsed(),json.dumps(dict(zip(msg.name,msg.position)))])
    def move(self,target,heading,dt):
        x,y,h=self.pose;dx,dy=target[0]-x,target[1]-y;dist=math.hypot(dx,dy);err=angle(heading-h)
        tol=self.cfg['return_position_tolerance'] if self.stage.startswith('RETURN') else self.cfg['position_tolerance']
        if dist<tol and abs(err)<.015 and np.linalg.norm(self.cmd)<.015:return True
        speed=min(self.cfg['max_linear_speed'],.8*dist)
        vx,vy=(speed*dx/dist,speed*dy/dist) if dist>1e-6 else (0.,0.)
        # World desired motion is rotated into the mecanum body's axes.
        desired=np.array([math.cos(h)*vx+math.sin(h)*vy,-math.sin(h)*vx+math.cos(h)*vy,np.clip(1.5*err,-self.cfg['max_angular_speed'],self.cfg['max_angular_speed'])])
        if abs(err)>.12:desired[:2]=0
        if self.now()-self.last_scan>.5:desired[:]=0
        elif desired[0]>0:
            # Teaching guard: slow early enough for the configured deceleration.
            # Range is measured from the rearward laser, not from the bumper.
            # This front-cone check is NOT all-direction obstacle avoidance.
            clearance=max(0.,self.front-self.cfg['obstacle_stop_distance'])
            braking_speed=math.sqrt(2*self.cfg['max_linear_accel']*.7*clearance)
            requested=float(np.linalg.norm(desired[:2]))
            if requested>braking_speed:desired[:2]*=braking_speed/requested
        self.command(desired,dt);return False
    def command(self,desired,dt):
        old=self.cmd.copy();diff=desired-self.cmd
        n=np.linalg.norm(diff[:2]);bound=self.cfg['max_linear_accel']*dt
        if n>bound:diff[:2]*=bound/n
        diff[2]=np.clip(diff[2],-1.2*dt,1.2*dt);self.cmd+=diff
        msg=Twist();msg.linear.x=float(self.cmd[0]);msg.linear.y=float(self.cmd[1]);msg.angular.z=float(self.cmd[2]);self.velocity_pub.publish(msg)
    def joints_command(self,dt):
        # Wheels are visual only; roller traction/slip is not modeled.
        vx,vy,w=self.cmd;wheel_rates=[(vx-vy-.16*w)/.042,(vx+vy+.16*w)/.042,(vx+vy-.16*w)/.042,(vx-vy+.16*w)/.042]
        self.wheels=[q+v*dt for q,v in zip(self.wheels,wheel_rates)]
        m=JointState();m.header.stamp=self.get_clock().now().to_msg()
        m.name=['upper_arm_joint','forearm_joint','wrist_joint','left_jaw_slide','right_jaw_slide','front_left_wheel_joint','front_right_wheel_joint','rear_left_wheel_joint','rear_right_wheel_joint'];m.position=[*map(float,self.arm),float(self.jaw),float(self.jaw),*self.wheels]
        self.joint_pub.publish(m)
    def step(self):
        now=self.now();dt=.05 if self.last_t is None else max(.001,min(.2,now-self.last_t));self.last_t=now
        if self.done:self.velocity_pub.publish(Twist());return
        self.joints_command(dt)
        if self.stage=='WAITING':
            if self.pose is not None and self.object is not None and self.grasp is not None and self.latest_map is not None and self.attach.service_is_ready() and self.now()-self.last_scan<.5:
                self.start=now;self.transition('OUTBOUND_MID')
            elif time.monotonic()-self.wall_start>80:self.finish('FAILED_STARTUP')
            return
        if self.elapsed()>self.cfg['max_duration_sec']:self.finish('TIMEOUT');return
        if self.unexpected_contacts:
            self.event('UNEXPECTED_CONTACT',collision_names=self.last_contact);self.finish('FAILED_COLLISION');return
        moves={'OUTBOUND_MID':(self.wp[1],0.,'OUTBOUND_B'),'OUTBOUND_B':(self.wp[2],0.,'APPROACH_B'),'RETURN_MID':(self.wp[3],math.pi,'RETURN_A'),'RETURN_A':(self.wp[4],math.pi,'APPROACH_A')}
        if self.stage in moves:
            target,heading,nxt=moves[self.stage]
            if self.move(target,heading,dt):self.event('WAYPOINT_REACHED',target=target,error_m=math.hypot(self.pose[0]-target[0],self.pose[1]-target[1]));self.transition(nxt)
            return
        # Hold the base still while the ideal joint setter and attachment
        # constraint move the arm. Zero velocity alone permits small drift.
        if self.hold_pose is not None:
            x,y,h=self.pose;hx,hy,hh=self.hold_pose
            wx,wy=np.clip(3*np.array([hx-x,hy-y]),-.04,.04)
            self.command(np.array([math.cos(h)*wx+math.sin(h)*wy,-math.sin(h)*wx+math.cos(h)*wy,np.clip(2*angle(hh-h),-.15,.15)]),dt)
        else:self.command(np.zeros(3),dt)
        age=now-self.stage_t;u=smooth(age/2.5)
        arm_stages={'APPROACH_B':('LOWER_B','hover'),'LOWER_B':('CLOSE','pick'),'LIFT_B':('STOW_B','hover'),'STOW_B':('RETURN_MID','carry'),
                    'APPROACH_A':('LOWER_A','hover'),'LOWER_A':('RELEASE','pick'),'RETRACT_A':('STOW_A','hover'),'STOW_A':('VERIFY','carry')}
        if self.stage in arm_stages:
            nxt,kind=arm_stages[self.stage]
            if kind=='carry':target=CARRY.copy()
            else:
                # Express the fixed station target in the current base frame.
                world=np.array([2.07,.35,.2755]) if self.stage.endswith('B') else np.array([-.27,0,.2755])
                if kind=='hover':world[2]+=.055
                x,y,h=self.pose;dx,dy=world[0]-x,world[1]-y
                target=np.array([math.cos(h)*dx+math.sin(h)*dy,0.,world[2]])
            self.tool=self.tool_from+(target-self.tool_from)*u;self.arm=ik(self.tool)
            if age>=3.2:self.transition(nxt)
        elif self.stage=='CLOSE':
            self.jaw=JAW_CLOSED*smooth(age/1.5)
            if age>=2.0:
                # Contact callbacks and the control timer are asynchronous.
                # Keep the jaws still for up to one extra second while waiting
                # for fresh evidence; do not attach on stale or missing contact.
                both=all(now-stamp<=.3+1e-9 for stamp in self.jaw_contacts.values())
                if not both and age<3.0:return
                gap=float(np.linalg.norm(np.array(self.grasp)-self.object))
                self.event('GRASP_DISTANCE_CHECK',distance_m=gap,grasp_xyz=self.grasp)
                if gap>.001:self.finish('FAILED_GRASP_ALIGNMENT');return
                self.event('FINGER_CONTACT_CHECK',both_fingers_touching=both,contact_age_s={k:now-v for k,v in self.jaw_contacts.items()})
                if not both:self.finish('FAILED_FINGER_CONTACT');return
                self.begin_attachment('attach')
        elif self.stage=='ATTACHING':
            return  # poll_attachment runs even while the simulation is paused.
        elif self.stage=='RELEASE':
            self.jaw=self.jaw_from*(1-smooth(age))
            if age>=1.2:
                self.begin_attachment('detach')
        elif self.stage=='DETACHING':
            return
        elif self.stage=='VERIFY' and age>3:
            err=math.hypot(self.object[0]+.27,self.object[1]);height_error=abs(self.object[2]-.2755)
            self.event('PLACEMENT_CHECK',xy_error_m=err,height_error_m=height_error)
            self.finish('COMPLETED' if err<.005 and height_error<.002 else 'FAILED_PLACEMENT')
    def finish(self,reason):
        self.reason=reason;self.event(reason);self.velocity_pub.publish(Twist());self.done=True
        if self.video is not None:self.video.release()
        if self.close_video is not None:self.close_video.release()
        data={
            'trajectory.csv':(['time_s','x_m','y_m','yaw_rad','odom_vx','odom_vy','odom_w','cmd_vx','cmd_vy','cmd_w','stage'],self.rows),
            'lidar.csv':(['time_s','front_min_m','scan_min_m','scan_mean_m','valid_count'],self.lidar),
            'imu.csv':(['time_s','wx','wy','wz','ax','ay','az'],self.imu),
            'payload.csv':(['time_s','x_m','y_m','z_m','stage'],self.objects),
            'camera_frames.csv':(['time_s','filename','stage'],self.frames),
            'map_updates.csv':(['time_s','width','height','known_cells'],self.maps),
            'joints.csv':(['time_s','positions_json'],self.joints),
            'contacts.csv':(['time_s','collision_1','collision_2','penetration_m','intentional_grip','stage'],self.contact_rows),
        }
        for name,(header,rows) in data.items():
            with (self.out/name).open('w',newline='') as f:w=csv.writer(f);w.writerow(header);w.writerows(rows)
        path=sum(math.hypot(b[1]-a[1],b[2]-a[2]) for a,b in zip(self.rows,self.rows[1:]))
        summary={'status':reason,'duration_sim_s':self.elapsed(),'planned_waypoints_xy_m':self.wp,'path_length_m':path,'final_robot_pose':self.pose,'final_payload_xyz':self.object,'sample_counts':{k:len(v[1]) for k,v in data.items()},'events':self.events,'settings':self.cfg,'model':'User SolidWorks mobile_robot geometry; ideal planar base, three pitch joints and parallel gripper, ideal attachment after 1 mm alignment check','navigation':'odom waypoint control; Cartographer builds a map separately','contact_messages':self.contact_messages,'unexpected_contacts':self.unexpected_contacts,'contact_model':'box and cylinder proxies; intended jaw-payload contact allowed; other contacts deeper than 0.1 mm stop the experiment'}
        summary['overview_video_frames']=self.overview_count
        (self.out/'summary.json').write_text(json.dumps(summary,indent=2));(self.out/'EXPERIMENT_FINISHED.txt').write_text(reason+'\n')

def main():
    rclpy.init();node=MobilePickupExperiment()
    try:
        last_clock=node.now();last_change=time.monotonic()
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node,timeout_sec=.1)
            node.poll_attachment()
            if node.now()!=last_clock:last_clock=node.now();last_change=time.monotonic()
            elif node.start is not None and time.monotonic()-last_change>30:
                node.finish('FAILED_CLOCK_STALLED')
    except KeyboardInterrupt:
        if not node.done:node.finish('INTERRUPTED')
    finally:node.velocity_pub.publish(Twist());node.destroy_node();rclpy.shutdown()
    raise SystemExit(0 if node.reason=='COMPLETED' else 2)
if __name__=='__main__':main()
