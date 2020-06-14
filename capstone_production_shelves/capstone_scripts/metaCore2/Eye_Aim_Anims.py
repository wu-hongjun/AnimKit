from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Eye_Aim_Anims(Network_Node):
    def __init__(self,side,limb,eye_anim_list,main_anim = True,dist = 5.00):
        exists = False

        eye_anim = PyNode(eye_anim_list[0])
        if eye_anim.hasAttr('connected_to') and len(listConnections(eye_anim.connected_to)) > 0:
            for node in listConnections(eye_anim.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Eye_Aim_Anims':
                    if listConnections(node.eyes)[0] == eye_anim:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'Eye_Aim_Anims',side = side,limb = limb)
            
            network = side.title() + '_' + limb.title() + '_Eye_Aim_Anims'
            name = side + '_' + limb
            
            nulls = []
            anims = []
            
            #Component Grp Organization
            component_grp = group(n=(name + '_component_grp'),em=True)
            anim_grp = group(n=(name + '_anim_grp'),em=True,p=component_grp)
            
            #Eye Aim Anim Setup
            for anim in eye_anim_list:
                anim = PyNode(anim)
                anim_grp = anim.getParent()
                rotation_null = group(n=(anim + '_rotation_null'),em=True,p=anim_grp)
                aligner([rotation_null],anim_grp)
                makeIdentity(rotation_null,a=True,t=True,r=True,s=True)
                parent(anim,rotation_null)
                select(cl=True)
                bone = anim.replace('_FK_anim','')
                
                select(cl=True)
                aim_anim = joint(n=(bone+'_aim_anim'),p=(0,0,0), r= 2)
                aim_null = group(aim_anim,n=(bone+'_aim_null'))
                aligner([aim_null],anim)
                
                loc = spaceLocator(anim + '_wuo',p = (0,0,0))
                aligner([loc],anim,rotation = False)
                loc.ty.set(loc.ty.get() + 2.00)
                loc.visibility.set(0)
                parent(loc,component_grp)
                
                aim_null.tz.set(abs(aim_null.tz.get() * dist))
                aimConstraint(aim_anim,rotation_null,mo=True,wut = 'object', wuo = loc.name())
                nulls.append(aim_null)
                anims.append(aim_anim)
                
            select(cl=True)
            
            #Main Eye Aim Anim Setup
            if main_anim == True:
                main_anim = joint(n=(side + '_main_eye_aim_anim'),p=(0,0,0), r= 2)
                main_null = group(main_anim,n=(side + '_main_eye_aim_anim_null'))
                anims.append(main_anim)
                anim_shape_generator(anims,r=1.00)
                
                for all in nulls:
                    con = pointConstraint(all,main_null,mo=False)
                aligner([main_null],anims[0],position = False)
                delete(con)
                
                shape = main_anim.getChildren(s=True)[0]+'.cv[:]'
                scale(shape,1,1.5,2.75,r=True)
                
                [parent(all,main_anim) for all in nulls]
                parent(main_null,component_grp)
                select(cl=True)
            
            else:
                anim_shape_generator(anims,r=1.00)
                parent(nulls,component_grp)
    
            lock_and_hide_attrs(anims,['sx','sy','sz','v','radius'])
            for all in anims:
                all.drawStyle.set(2)
    
            #Connections
            connect_objs_to_node(anims,network,'anims')
            connect_objs_to_node(eye_anim_list,network,'eyes')
            connect_objs_to_node([component_grp],network,'component_grp')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')