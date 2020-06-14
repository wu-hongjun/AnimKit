from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Multi_Constraint(Network_Node):
    def __init__(self, anim, constraint_objs,translation = True,rotation = True):
        if anim.startswith('left'): side = 'left'
        elif anim.startswith('right'): side = 'right'
        else: side = 'center'
        
        Network_Node.__init__(self,'Multi_Constraint',side = side, root = anim)
        
        network = anim.title() + '_Multi_Constraint'
        name = anim
        anim = PyNode(anim)
        objects = [PyNode(x) for x in constraint_objs] 
        
        #Add Anim Constraint Null
        anim.tx.unlock()
        anim.ty.unlock()
        anim.tz.unlock()
        null = joint(n=(anim + '_multi_constraint_null'),p=(0,0,0))
        null.drawStyle.set(2)
        aligner([null],anim.getParent())
        joint_orient(null)
        parent(null,anim.getParent())
        for at in ['tx','ty','tz']:
            con = listConnections(anim.attr(at),p=True,d=False)
            if con:
                try:
                    Attribute(con[0]) // anim.attr(at)
                    Attribute(con[0]) >> null.attr(at)
                except:
                    pass
        parent(anim,null)
        if anim.endswith('FK_anim') == True:
            anim.tx.lock()
            anim.ty.lock()
            anim.tz.lock()
            
        #Connect Multi_Constraint To Anim Component
        component = PyNode(listConnections(anim.connected_to)[0])
        val = len(listConnections(component.connected_networks))
        PyNode(network).parent_network >> component.connected_networks[val]
        
        rig = listConnections(component.rig)[0]
        amnt = len(listConnections(rig.connected_networks))
        PyNode(network).rig >> rig.connected_networks[amnt]
        
        #Create Attribute Enum
        enum_name = str(constraint_objs).replace('[','').replace(']','').replace("'","").replace(', ',':') + ':'
        anim.addAttr('parent_to',at='enum',en=enum_name,k=True)
        
        cd = anim + '.parent_to'
        attrs = []
        i = 0;
        
        pma = shadingNode('plusMinusAverage',au=True)
        pma.output3D >> null.rotate
        
        influence_nulls = []
        
        for obj in constraint_objs:
            con_obj = group(n = (name + '_' + obj + '_null'),em=True)
            influence_nulls.append(con_obj)
            if component.hasAttr('hidden_grp') == True:
                parent(con_obj,listConnections(component.hidden_grp)[0])
            else:
                parent(con_obj,listConnections(component.component_grp)[0])
            aligner([con_obj],anim)
            if translation == True:
                trans_con = pointConstraint(con_obj, null, mo=True)
            if rotation == True:
                rot_con = orientConstraint(con_obj, null, mo=True)
            parentConstraint(obj,con_obj,mo=True)
            attrs.append(con_obj + 'W' + str(i))
            i += 1;
        
        for i in range(len(attrs)):
            cond = create_node('condition',n=(anim + '_multi_con_condition_' + str(i + 1)))
            anim.parent_to >> cond.firstTerm
            cond.secondTerm.set(i)
            cond.colorIfTrue.set(1,1,1)
            cond.colorIfFalse.set(0,0,0)
            if translation == True:
                cond.outColorR >> trans_con.attr(attrs[i])
            if rotation == True:
                cond.outColorR >> rot_con.attr(attrs[i])
        for at in ['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility','radius']:
            null.setAttr(at,l=True,cb=False,k=False)

        anim.attr('parent_to').set(0)
        select(cl=True)
            
        #Connections
        connect_objs_to_node([anim],network,'anim')
        connect_objs_to_node([null],network,'constraint_null')
        connect_objs_to_node(influence_nulls,network,'influence_nulls')
        connect_objs_to_node(objects,network,'influences')
        
    def connect_components(self,component,connection):
        pass;