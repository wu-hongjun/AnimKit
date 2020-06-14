from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Flexible_Mouth(Network_Node):
    def __init__(self,side,limb,upper_lip,lower_lip,left_corner,right_corner,nurb_surface,secondaries = False):
        exists = False

        left_corner = PyNode(left_corner)
        if left_corner.hasAttr('connected_to') and len(listConnections(left_corner.connected_to)) > 0:
            for node in listConnections(left_corner.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Flexible_Mouth':
                    if listConnections(node.corner_lip_bones)[0] == left_corner:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'Flexible_Mouth',side = side,limb = limb)
            
            network = side.title() + '_' + limb.title() + '_Flexible_Mouth'
            name = side + '_' + limb
            upper_lips = [PyNode(x) for x in upper_lip]
            lower_lips = [PyNode(x) for x in lower_lip]
            left_corner = PyNode(left_corner)
            right_corner = PyNode(right_corner)
            nurb_surface = PyNode(nurb_surface)
            Controls = []
            Control_Nulls = []
            anims = []
            bind_locs = []
            splines = []
            nurb_locs = []
            lip_nurbs = []
            secondary_nulls = []
            secondary_anims = []
    
            bones = list(set([right_corner] + upper_lips + [left_corner ]+ lower_lips))
            wuo = spaceLocator(n = name + '_wuo',p=(0,0,0))  
            for lip in ['upper_lip','lower_lip']:
                if lip == 'upper_lip':
                    lip_chain = [PyNode(x) for x in upper_lip]
                    r = [0,len(lip_chain)+2]
                else:
                    lip_chain = [PyNode(x) for x in lower_lip]
                    r = [1,(len(lip_chain)+1)]
                lip_chain.insert(0,right_corner)
                lip_chain.append(left_corner)
                lip_nurb = make_spline((name + '_' + lip),chain = lip_chain,smooth = False)
                lip_wire= make_spline((name + '_' + lip + '_wire'),chain = lip_chain)
                lip_nurbs.append(lip_wire)
                wire_deform = wire(lip_nurb, gw=False,en=1.00,ce=0.00, li = 0.00, w = lip_wire)[0]
                wire_deform.dropoffDistance[0].set(1000)
                deform = PyNode(name + '_' + lip + '_wire_cvBaseWire')
                splines.append(lip_nurb)
                splines.append(lip_wire)
                splines.append(deform)
                for i in range(r[0],r[1]):
                    u =  float(i * (1.00/(len(lip_chain)-1)))
                    loc = spaceLocator(n=(lip_chain[i].replace('_joint','_loc')),p=(0,0,0))
                    bind_locs.append(loc)
                    curve_constraint(lip_nurb,loc,u)
                    normalConstraint(nurb_surface,loc, wut = 'objectrotation', wuo = wuo)
                    if secondaries == True:
                        secondary_anim = joint(n = (name + '_' + lip_chain[i].replace('_bind_joint','_anim')),p=(0,0,0))
                        secondary_null = group(n=(name + '_' + lip_chain[i].replace('_bind_joint','_zero_grp')),em=True)
                        anim_shape_generator([secondary_anim],r=0.1)
                        secondary_anim.drawStyle.set(2)
                        parent(secondary_anim,secondary_null)
                        aligner([secondary_null,secondary_anim],lip_chain[i])
                        makeIdentity(secondary_anim,a = True,t = True,r = True,s = True,jo = False)
                        parentConstraint(loc,secondary_null,mo=True)
                        parentConstraint(secondary_anim,lip_chain[i],mo=True)
                        secondary_nulls.append(secondary_null)
                        secondary_anims.append(secondary_anim)
                        lock_and_hide_attrs([secondary_null],['sx','sy','sz','visibility'])
                        lock_and_hide_attrs([secondary_anim],['sx','sy','sz','visibility','radius'])
                    else:
                        parentConstraint(loc,lip_chain[i],mo=True)
                    
            #Make Anims and Control Joints
            anims, anim_nulls = self.make_anims(name,lip_nurbs[0],lip_nurbs[1],nurb_surface)
            upper_nulls = [x.getParent() for x in anims if '_upper_' in x.name()]
            lower_nulls = [x.getParent() for x in anims if '_lower_' in x.name()]
            corner_nulls = [PyNode(name + '_left_anim').getParent(),PyNode(name + '_right_anim').getParent()]
            upper_anims = [x for x in anims if '_upper_' in x.name()]
            lower_anims = [x for x in anims if '_lower_' in x.name()]
            corner_anims = [PyNode(name + '_left_anim'),PyNode(name + '_right_anim')]
            upper_nurb = nurb_surface.rename(name + '_upper_nurb')
            lower_nurb = duplicate(nurb_surface)[0].rename(name + '_lower_nurb')
            nurb = upper_nurb
    
            for anim in anims:
                anim_shape_generator([anim], r=0.35)
                anim.drawStyle.set(2)
                Control = joint(n=(anim.replace('_anim','_control_joint')),rad = 0.5)
                Control_Null = group(n =(anim.replace('_anim','_control_null')))
                Controls.append(Control)
                Control_Nulls.append(Control_Null)
                aligner([Control],anim)
                joint_orient(Control)
                aligner([Control_Null],Control)
                parent(Control,Control_Null)
                
                #Create nurbLocators
                n_loc = spaceLocator(n=(anim.replace('_anim','_nurb_loc')),p=(0,0,0))
                aligner([n_loc],anim,rotation = False)
                if 'lower' in anim.name():
                    nurb = lower_nurb
                normalConstraint(nurb,n_loc)
                parentConstraint(n_loc,Control_Null,mo=True)
                pointConstraint(anim,n_loc,mo=True)
                nurb.worldSpace >> n_loc.geometry
                nurb_locs.append(n_loc)
                select(cl=True)
                
                #Push Attr
                anim.addAttr('push',at = 'double',dv = 0,k=True)
                anim.push >> Control.tx
            
            #Finish Anim Setup
            i = 0
            for side in ['_upper_','_lower_']:
                for s in ['left','right']:
                    anim = PyNode(name + side + s + '_anim')
                    mid = PyNode(name + side + 'mid_' + s + '_anim')
                    corner = PyNode(name + '_' + s + '_anim')
                    if corner.hasAttr('secondary_anim_vis') == False:
                        corner.addAttr('secondary_anim_vis',at='double',min=0,max=1,k=True)
                    parentConstraint(mid,anim.getParent(), mo = True)
                    parentConstraint(corner,anim.getParent(), mo = True)
                    corner.secondary_anim_vis >> anim.getParent().visibility
    
                influences = [(name + '_right_control_joint')] + ls(name + side + '*_control_joint') + [(name + '_left_control_joint')]
                skinCluster(influences,lip_nurbs[i],tsb=True)
                i += 1
    
            lock_and_hide_attrs(anims,['rx','ry','rz','sx','sy','sz','radius','visibility'])
            lock_and_hide_attrs(anim_nulls,['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility'])
            
            #Component Grp Organization
            component_grp = group(n=(name + '_component_grp'),em=True)
            control_grp = group(Control_Nulls,n=(name + '_control_grp'))
            upper_anim_grp = group(upper_nulls,upper_nurb,n=(name + '_upper_anim_grp'))
            lower_anim_grp = group(lower_nulls,lower_nurb,n=(name + '_lower_anim_grp'))
            anim_grp = group(corner_nulls,upper_anim_grp,lower_anim_grp,n=(name + '_anim_grp'),p=component_grp)
            if secondaries == True:
                secondary_anim_grp = group(secondary_nulls,n=(name + '_secondary_anim_grp'),p=anim_grp)
            hidden_grp = group(wuo,control_grp,nurb_surface,n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            spline_grp = group(splines,n = (name + '_spline_grp'),p=hidden_grp)
            nurb_loc_grp = group(nurb_locs,n=(name + '_nurb_loc_grp'),p=hidden_grp)
            bind_loc_grp = group(bind_locs,n=(name + '_bind_loc_grp'),p = hidden_grp)
            nurb_loc_grp.inheritsTransform.set(0)
            bind_loc_grp.inheritsTransform.set(0)
            spline_grp.inheritsTransform.set(0)
            select(cl=True)
            
            #Connections
            connect_objs_to_node(bones,network,'bones')
            connect_objs_to_node(anims,network,'primary_anims')
            connect_objs_to_node(anims,network,'anims')
            if secondaries == True:
                connect_objs_to_node(secondary_anims,network,'anims')
                connect_objs_to_node(secondary_anims,network,'secondary_anims')
                
            connect_objs_to_node(upper_anims,network,'upper_anims')
            connect_objs_to_node(lower_anims,network,'lower_anims')
            connect_objs_to_node(corner_anims,network,'corner_anims')
            connect_objs_to_node(Controls,network,'control_joints')
            connect_objs_to_node(upper_lips,network,'upper_lip_bones')
            connect_objs_to_node(lower_lips,network,'lower_lip_bones')
            connect_objs_to_node([left_corner,right_corner],network,'corner_lip_bones')
            connect_objs_to_node([component_grp],network,'component_grp')
            connect_objs_to_node([hidden_grp],network,'hidden_grp')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')
        
            self.network = PyNode(network)
    
    def get_primary_anims(self):
        return listConnections(self.network.primary_anims)
        
    def get_secondary_anims(self):
        if self.network.hasAttr('secondary_anims') == True:
            return listConnections(self.network.secondary_anims)
        else:
            return [None]
    
    def add_jaw(self,bone):
        nulls = [x.getParent() for x in listConnections(self.network.lower_anims)]
        lower_anim_grp = nulls[0].getParent()
        aligner([lower_anim_grp],bone,position = False,rotation = False,pivot = True)
        con = parentConstraint(bone,lower_anim_grp,mo=True)
        select(cl=True)
        
    def make_anims(self,name,upper_lip,lower_lip,nurb_surface):
        anims = []
        nulls = []
        i = 0
        select(cl=True)
        #Corner Anims
        for s in ['_right','_left']:
            n = name + s + '_anim'
            anim = self.oriented_anim(n,upper_lip,nurb_surface,i)
            anims.append(anim)
            i += 1
        #Mid Anims
        for lip in [upper_lip,lower_lip]:
            if lip == upper_lip:
                l = '_upper'
            else:
                l = '_lower'
            value = [0.125,0.25,0.5,0.75,0.875]
            i = 0
            for s in ['_right','_mid_right','_mid','_mid_left','_left']:
                n = name + l + s + '_anim'
                anim = self.oriented_anim(n,lip,nurb_surface,value[i])
                anims.append(anim)
                i += 1
        
        #Create Nulls
        for anim in anims:
            null = group(n = anim + '_zero_grp',em=True)
            aligner([null],anim)
            parent(anim,null)
            nulls.append(null)
            
        return [anims,nulls]

    def oriented_anim(self,n,cv,nurb_surface,value):
        anim = joint(n = n,p=(0,0,0),r=4.00)
        curve_constraint(cv,anim,value)
        normalConstraint(nurb_surface,anim)
        translation = anim.translate.get()
        rotation = anim.rotate.get()
        delete(listConnections(anim))
        anim.translate.set(translation)
        anim.rotate.set(0,0,0)
        anim.jointOrient.set(rotation)
        select(cl=True)
        return anim