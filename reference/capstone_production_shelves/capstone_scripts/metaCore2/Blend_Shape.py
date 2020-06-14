from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *

class Blend_Shape(Network_Node):

    def __init__(self, side, limb, root, mesh, blend_meshes, anim = None):
        Network_Node.__init__(self,'Blend_Shape',side = side,limb = limb, root = root)
        
        network = side.title() + '_' + limb.title() + '_Blend_Shape'
        name = side + '_' + limb
        
        targets = blend_meshes
        targets.append(mesh)
        
        blend_node = blendShape(targets,n = (mesh + '_blend'),frontOfChain = True,o = 'local')[0]
    
        ##Anim##
        if not anim:
            anim = joint(n=(name + '_blend_anim'),p=(0,0,0))
            anim.addAttr('animNode',at='message')
            aligner([anim],root)
            anim_shape_generator([anim],r=0.75)
            anim.drawStyle.set(2)
            joint_orient(anim)
            parentConstraint(root,anim,mo=True)
            lock_and_hide_attrs([anim],['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius'])
        
        else: anim = PyNode(anim)
        
        for target in targets[:-1]:
            anim.addAttr(target,min = 0, max = 1, dv = 0, k=True)
            anim.attr(target) >> blend_node.attr(target)

        #Component Grp Organization
        component_grp = group(n=(name + '_component_grp'),em=True)
        anim_grp = group(n=(name + '_anim_grp'),p=component_grp,em = True)
        if anim.endswith('_blend_anim'): parent(anim,anim_grp)
        network_grp_lock(name,root)
        select(cl=True)

        #Connections
        connect_objs_to_node([anim],network,'anims')
        connect_objs_to_node([component_grp],network,'component_grp')
        
        self.network = PyNode(network)

    def connect_components(self,component,connection):
        pass