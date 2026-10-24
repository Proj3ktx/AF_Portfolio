"""Small, testable planar arm model using hinge centres from the CAD surface.

Coordinates are meters, ROS X forward and Z up. Joint angles are offsets from
the imported pose. Positive rotation about Y tips an X-facing link downward.
"""
import math
import numpy as np
S=np.array([.0226,0.,.218905])
E=np.array([-.035984,0.,.277489])
W=np.array([.00544,0.,.34924])
G=np.array([.148,0.,.271])
ORIGINS={'base':np.zeros(3),'upper_arm':S,'forearm':E,'wrist':W,'left_jaw':G,'right_jaw':G}
TOOL_PITCH=math.atan2((G-W)[2],(G-W)[0])
CARRY=np.array([.205,0.,.37])
PICK=np.array([.27,0.,.2755])
HOVER=PICK+np.array([0,0,.055])
JAW_CLOSED=.0102
def ry(a):
    c,s=math.cos(a),math.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def ik(target):
    """Solve two arm links, then keep the fingers level with a wrist offset."""
    target=np.asarray(target);v1=E-S;v2=W-E
    wrist=target-ry(TOOL_PITCH)@(G-W)
    dx,dz=(wrist-S)[[0,2]];l1=np.linalg.norm(v1);l2=np.linalg.norm(v2)
    c=(dx*dx+dz*dz-l1*l1-l2*l2)/(2*l1*l2)
    if not -1<=c<=1:raise ValueError(f'Tool target outside reach: {target}')
    elbow=-math.acos(c)
    a1=math.atan2(dz,dx)-math.atan2(l2*math.sin(elbow),l1+l2*math.cos(elbow))
    a2=a1+elbow
    q1=math.atan2(v1[2],v1[0])-a1
    q2=math.atan2(v2[2],v2[0])-a2-q1
    q3=TOOL_PITCH-q1-q2
    return np.array([q1,q2,q3])
def fk(q,jaw=0):
    q1,q2,q3=q;r1=ry(q1);r2=ry(q1+q2);r3=ry(sum(q))
    ep=S+r1@(E-S);wp=ep+r2@(W-E);gp=wp+r3@(G-W)
    return {'base':(np.zeros(3),np.eye(3)),'upper_arm':(S,r1),'forearm':(ep,r2),'wrist':(wp,r3),
            'left_jaw':(gp+r3@np.array([0,-jaw,0]),r3),'right_jaw':(gp+r3@np.array([0,jaw,0]),r3),'grasp_link':(gp,r3)}
if __name__=='__main__':
    for name,target in [('carry',CARRY),('hover',HOVER),('pick',PICK)]:
        q=ik(target);actual=fk(q)['grasp_link'][0]
        print(name,'joint angles rad',q,'tool XYZ',actual,'error',np.linalg.norm(actual-target))
