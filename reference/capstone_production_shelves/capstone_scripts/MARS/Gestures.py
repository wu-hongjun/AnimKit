import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class Gestures(MarsRigComponent):
    def __init__(self,side,limb, controlled_anims, root = None, attrs = [], mins = [], maxs = [], dvs = [], tx = [],ty = [],rz = [], anim = None, node = None,rig = None):
        self.node = node
        
        if node != None: self.node = node
        else:
            try: self.node = self.exist_check('Gestures',anim,'anim')
            except: self.node = None
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'Gestures', side, limb, start = '', end = '')
            
            #Variables
            name = side + '_' + limb
            sdk_joints = []
            ui = None
            i = 1
            
            for i , c_anim in enumerate(controlled_anims):
                attributes = pm.listAttr(c_anim, l = True, st = ['translate*','rotate*'])
                for at in attributes: c_anim.attr(at).unlock()
                new_bone = pm.joint(n=(c_anim + '_' + limb +'_SDK_null'),p=(0,0,0),rad = 0.25)
                new_bone.jointOrient.set(0,0,0)
                sdk_joints.append(new_bone)
                if attrs:
                    mu.aligner(new_bone,c_anim)
                    pm.makeIdentity(new_bone, t = True, r = True, s = True, jo = False, a = True)
                    pm.parent(new_bone,c_anim.getParent())
                else:
                    pm.select(cl = True)
                    orienter = pm.group(n=(c_anim + '_' + limb +'_SDK_orient'),em = True)
                    mu.aligner([orienter,new_bone],c_anim,rotation = False)
                    pm.parent(new_bone,orienter)
                    pm.parent(orienter,c_anim.getParent())
                 
                pm.parent(c_anim,new_bone)
                for at in attributes:
                    c_anim.attr(at).lock()
                    new_bone.attr(at).lock()
                pm.select(cl = True)
                   
            ##Anim##
            if anim == None:
                if attrs:
                    anim = pm.joint(n=(name + '_anim'),p=(0,0,0))
                    mu.default_anim_shape([anim],r=0.75)
                    anim.drawStyle.set(2)
                    if root != None:
                        mu.aligner(anim,root)
                        pm.parentConstraint(root,anim,mo=True)
                    mu.lock_and_hide_attrs(anim,['translate','rotate','scale','v','radius'])
            
                #else: anim, ui = ui_anim(name + '_gesture',tx = tx,ty = ty,rz = rz)
                
                #Component Grp Organization
                component_grp = pm.group(n=(name + '_component_grp'),em=True)
                if attrs:
                    anim_grp = pm.group(anim,n=(name + '_anim_grp'),p=component_grp)
                    mu.aligner([anim,component_grp],root)
                    
                #Newer Connections
                mu.con_link(component_grp,self.node,'component_grp')
                
            else: anim = pm.PyNode(anim)
            
            if attrs:
                for i,at in enumerate(attrs):
                    anim.addAttr(at, at='double', k=True)
                    attribute = anim + '.' + at
                    if mins: pm.addAttr(attribute,e=True,min = mins[i])
                    if maxs: pm.addAttr(attribute,e=True,max = maxs[i])
                    if dvs:
                        pm.addAttr(attribute,e=True,dv = dvs[i])
                        anim.attr(at).set(dvs[i])
                    else:
                        try: v = 0
                        except: v = mins[i]
                        pm.addAttr(attribute,e=True,dv = v)
                        anim.attr(at).set(v)
            pm.select(cl=True)
            
            mu.con_link(anim,self.node,'anims')
            mu.con_link(sdk_joints,self.node,'sdk_joints')
            
            if rig != None: rig.add_to_rig(self)
            
    def pre_infinity(self):
        for sdk in pm.listConnections(self.node.sdk_joints):
            attrs = pm.listAttr(sdk,w=True,u=True,v=True,k=True)
            nodes = []
            for all in attrs:
                items = pm.listConnections(sdk.attr(all),c = True,d = True)
                for item in items:
                    sdk_node = item[-1]
                    sdk_node.preInfinity.set(3)
    
    def post_infinity(self):
        for sdk in pm.listConnections(self.node.sdk_joints):
            attrs = pm.listAttr(sdk,w=True,u=True,v=True,k=True)
            nodes = []
            for all in attrs:
                items = pm.listConnections(sdk.attr(all),c = True,d = True)
                for item in items:
                    sdk_node = item[-1]
                    sdk_node.postInfinity.set(3)
        
    def linear(self):
        for sdk in pm.listConnections(self.node.sdk_joints):
            attrs = pm.listAttr(sdk,w=True,u=True,v=True,k=True)
            nodes = []
            for all in attrs:
                items = pm.listConnections(sdk.attr(all),c = True,d = True)
                for item in items:
                    sdk_node = item[-1]
                    pm.selectKey(sdk_node,add = True,k=True)
                    pm.keyTangent(itt = 'linear',ott = 'linear',e = True)
            pm.select(cl = True)
    
    def get_ui(self):
        return pm.listConnections(self.node.ui)[0]
    
    def get_sdk_joints(self):
        return pm.listConnections(self.node.sdk_joints)
    
    def hide_joints(self):
        sdk_joints = pm.listConnections(self.node.sdk_joints)
        [x.drawStyle.set(2) for x in sdk_joints]
        
    def show_joints(self):
        sdk_joints = pm.listConnections(self.node.sdk_joints)
        [x.drawStyle.set(0) for x in sdk_joints]
        