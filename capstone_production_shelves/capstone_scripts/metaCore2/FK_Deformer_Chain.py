from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class FK_Deformer_Chain(Network_Node):
    def __init__(self,side,limb,start,end,type = 'sine',stretch = True):
        Network_Node.__init__(self,'FK_Deformer_Chain',side = side,limb = limb,start = start,end = end,stretch = stretch)
        
        network = side.title() + '_' + limb.title() + '_FK_Deformer_Chain'
        name = side + '_' + limb
        bones = get_chain(start,end);
        
        con = check_constraint_connections(bones[0])
        if con:
            delete(con)
        
        #Control Chain
        Control = duplicate_chain(start,end,rep='_bind',wi='control')
        
        #FK Chain
        FK_chain = stacked_chain(start ,end, amnt = 1, rep = 'bind_joint', wi = 'FK_anim',reverse = False)
        nulls = FK_chain[0::2]
        FK = FK_chain[1::2]
        anim_shape_generator(FK[:-1], r=1.50)
        j = 0
        
        for i in range(len(FK_chain)):
            FK_chain[i].drawStyle.set(2)
            if i % 2 == 0:
                FK_chain[i].rename(FK_chain[i].replace('null1','null'))
            else:
                parentConstraint(FK_chain[i],Control[j])
                parentConstraint(Control[j],bones[j])
                j += 1
        
        if stretch == True:
            FK_stretch(FK)
        
        #Deformer Chain
        deformer_chain = duplicate_chain(start,end,rep = '_bind_', wi = '_deformer_')
        deformer_curve = make_spline(name + '_deformer',start = start,end = end)
        deformer_handle = ikHandle(n=(name + '_deformer_IK'),sol='ikSplineSolver',c=deformer_curve,sj=deformer_chain[0],ee=deformer_chain[-1],ccv=False,pcv=False)[0]
        for i in range(len(nulls)-1):
            deformer_chain[i].rotate >> nulls[i].rotate
        
        length = []
        for all in nulls:
            length.append(all.tx.get())   
        dist = (sum(length)/2.00)
        
        select(deformer_curve)
        deform = nonLinear(type = type)
        placer = group(n=('deform_place'),em=True)
        parent(deform[1],placer)
        PyNode(deform[1]).scale.set(dist,dist,dist)
        PyNode(deform[1]).translate.set(PyNode(deform[1]).sx.get(),0,0)
        PyNode(deform[1]).rz.set(-90)
        aligner([placer],bones[0])
        
        #Switch
        switch = group(n=(name + '_switch'),em=True)
        lock_and_hide_attrs([switch],['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility'])
        
        if type == 'sine':
            switch.addAttr('amplitude',min = -5,max = 5,dv=0,k=True)
            switch.addAttr('wavelength',min = 0.1,max = 10,dv=2,k=True)
            switch.addAttr('offset',dv=0,k=True)
            
            switch.amplitude >> PyNode(deform[0]).amplitude
            switch.wavelength >> PyNode(deform[0]).wavelength
            switch.offset >> PyNode(deform[0]).offset
            
        elif type == 'bend':
            switch.addAttr('curvature',dv=0,k=True)
            
        #Component Grp Organization
        component_grp = group(switch,n=(name + '_component_grp'))
        anim_grp = group(nulls[0],n=(name + '_anim_grp'),p=component_grp)
        hidden_grp = group(deformer_curve,deformer_handle,deformer_chain[0],deform[1],Control[0],n=('DO_NOT_TOUCH'),p=component_grp)
        hidden_grp.visibility.set(0)
        network_grp_lock(name,bones[0])
        delete(placer)
        select(cl=True)
        
        #Connections
        connect_objs_to_node(FK,network,'anims')
        connect_objs_to_node(FK,network,'FK_anims')
        connect_objs_to_node(Control,network,'control_joints')
        connect_objs_to_node(switch,network,'switch')
        connect_objs_to_node(component_grp,network,'component_grp')
        connect_objs_to_node(hidden_grp,network,'hidden_grp')
        
        for anim in listConnections(PyNode(network).anims):
            anim.addAttr('animNode',at='message')