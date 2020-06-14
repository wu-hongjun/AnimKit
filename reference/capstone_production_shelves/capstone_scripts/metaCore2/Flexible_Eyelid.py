from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
class Flexible_Eyelid(Network_Node):
    def __init__(self,side,limb,upper_lid,lower_lid,inner_corner,outer_corner,eye_bone,nurb = None):
        exists = False

        inner_corner = PyNode(inner_corner)
        if inner_corner.hasAttr('connected_to') and len(listConnections(inner_corner.connected_to)) > 0:
            for node in listConnections(inner_corner.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Flexible_Eyelid':
                    if listConnections(node.corner_lid_bones)[0] == inner_corner:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'Flexible_Eyelid',side = side,limb = limb)
            
            network = side.title() + '_' + limb.title() + '_Flexible_Eyelid'
            name = side + '_' + limb
            upper_lids = [PyNode(x) for x in upper_lid]
            lower_lids = [PyNode(x) for x in lower_lid]
            outer_corner = PyNode(outer_corner)
            inner_corner = PyNode(inner_corner)
            Controls = []
            anims = []
            bind_locs = []
            splines = []
            nurb_locs = []
            lid_nurbs = []
            all_anims = []
            
            bones = list(set([inner_corner] + upper_lids + [outer_corner] + lower_lids))
            if nurb != None:
                nurb = PyNode(nurb)
                rename(nurb,name + '_nurb_surface')
            for lid in ['upper_lid','lower_lid']:
                if lid == 'upper_lid':
                    lid_chain = [PyNode(x) for x in upper_lid]
                    r = [0,len(lid_chain)+2]
                else:
                    lid_chain = [PyNode(x) for x in lower_lid]
                    r = [1,(len(lid_chain)+1)]
                lid_chain.insert(0,inner_corner)
                lid_chain.append(outer_corner)
                lid_nurb = make_spline((name + '_' + lid),chain = lid_chain,smooth = False)
                lid_wire= make_spline((name + '_' + lid + '_wire'),chain = lid_chain)
                lid_nurbs.append(lid_wire)
                wire_deform = wire(lid_nurb, gw=False,en=1.00,ce=0.00, li = 0.00, w = lid_wire)[0]
                wire_deform.dropoffDistance[0].set(1000)
                deform = PyNode(name + '_' + lid + '_wire_cvBaseWire')
                splines.append(lid_nurb)
                splines.append(lid_wire)
                splines.append(deform)
                for i in range(r[0],r[1]):
                    u =  float(i * (1.00/(len(lid_chain)-1)))
                    loc = spaceLocator(n=(lid_chain[i].replace('_joint','_loc')),p=(0,0,0))
                    curve_constraint(lid_nurb,loc,u)
                    bind_locs.append(loc)
            
            #Aim Joints
            aim_joint_starts = []
            aim_joint_ends = []
            aim_IKs = []
            Control_Nulls = []
            nurb_locs = []
            start = xform(eye_bone, q= True, ws=True, rp=True)
            for bone in bones:
                end = xform(bone, q= True, ws=True, rp=True)
                aim_start = joint(n = bone.replace('_bind','_control'),p = start)
                aim_end = joint(n = bone.replace('_bind','_control_end'),p = end)
                aim_end.jointOrient.set(0,0,0)
                aim_joint_starts.append(aim_start)
                aim_joint_ends.append(aim_end)
                IK = ikHandle(n=(name + '_IK'),sol='ikSCsolver',sj=aim_start,ee=aim_end,ccv=False,pcv=False)[0]
                aim_IKs.append(IK)
                pointConstraint(bone.replace('_joint','_loc'),IK,mo=True)
                if nurb != None:
                    n_loc = spaceLocator(n=(bone.replace('_bind_joint','_nurb_loc')),p=(0,0,0))
                    nurb_locs.append(n_loc)
                    geometryConstraint(nurb,n_loc)
                    aligner([n_loc],bone,rotation = False)
                    parentConstraint(aim_end,n_loc, mo = True)
                    parentConstraint(n_loc,bone,mo = True)
                else:
                    parentConstraint(aim_end,bone,mo=True)
                select(cl=True)
    
            middle_spline = self.make_middle_spline(name,lid_nurbs[0],lid_nurbs[1])
            splines.append(middle_spline)
            more_splines, blends = self.create_blend_shapes(lid_nurbs[0],lid_nurbs[1],middle_spline)
            splines += more_splines
                  
            #Make Anims and Control Joints
            anims, anim_nulls = self.make_anims(name,lid_nurbs[0],lid_nurbs[1])
            all_anims += anims
            nulls = [PyNode(name + '_inner_anim').getParent(),PyNode(name + '_outer_anim').getParent()]
            for anim in anims:
                anim_shape_generator([anim], r=0.35)
                anim.drawStyle.set(2)
    
            i = 0
            for side in ['_upper_','_lower_']: 
                for s in ['inner','outer']:
                    anim = PyNode(name + side + s + '_anim')
                    mid = PyNode(name + side + 'mid_' + s + '_anim')
                    corner = PyNode(name + '_' + s + '_anim')
                    if corner.hasAttr('secondary_anim_vis') == False:
                        corner.addAttr('secondary_anim_vis',at='double',min=0,max=1,k=True)
                    parentConstraint(mid,anim.getParent(), mo = True)
                    parentConstraint(corner,anim.getParent(), mo = True)
                    corner.secondary_anim_vis >> anim.visibility
                
                sub_anims = ls(name + side + '*_anim')
                influences = [(name + '_inner_anim')] + sub_anims + [(name + '_outer_anim')]
                #skinCluster(influences,lid_nurbs[i],tsb=True)
                skinCluster(influences,more_splines[i],tsb=True)
                
                main_anim_null = group(n = (name + side + 'main_anim_zero_grp'),em=True)
                main_anim = joint(n = (name + side + 'main_anim'),p=(0,0,0))
                all_anims += [main_anim]
                main_anim.addAttr('blink', min = 0, max = 1, dv = 0, k = True)
                main_anim.blink >> blends[i + 1].attr(middle_spline.name())
                blink_rev = create_node('reverse',n = (name + side + 'main_anim_rev_blink'))
                main_anim.blink >> blink_rev.inputX
                blink_rev.outputX >> blends[i + 1].attr(more_splines[i])
                
                
                if side == '_upper_':
                    main_anim.addAttr('blink_height', min = 0, max = 1, dv = 0.5, k = True)
                    rev = create_node('reverse',n=(name + '_blink_height_reverse'))
                    main_anim.blink_height >> rev.inputX
                    main_anim.blink_height >> blends[0].attr(more_splines[0].name())
                    rev.outputX >> blends[0].attr(more_splines[1].name())
                parent(main_anim,main_anim_null)
                aligner([main_anim_null],(name + side + 'mid_anim'))
                parent(main_anim_null, w=True)
                for sub_anims in sub_anims:
                    parent(sub_anims.getParent(),main_anim)
                anims.append(main_anim)
                nulls.append(main_anim_null)
                anim_shape_generator([main_anim], r=0.7)
                main_anim.drawStyle.set(2)
                select(cl=True)
                i += 1
            
            lock_and_hide_attrs(anims,['sx','sy','sz','radius','visibility'])
    
            #Component Grp Organization
            component_grp = group(n=(name + '_component_grp'),em=True)
            anim_grp = group(nulls,n=(name + '_anim_grp'),p=component_grp)
            hidden_grp = group(n=('DO_NOT_TOUCH'),p=component_grp,em=True)
            if nurb != None:
                n_loc_grp = group(nurb_locs,n = (name + '_nurb_loc_grp'),p = hidden_grp)
                parent(nurb,hidden_grp)
            control_grp = group(aim_joint_starts,n=(name + '_control_grp'),p=hidden_grp)
            aim_IK_grp = group(aim_IKs,n=(name + '_control_IK_grp'),p = hidden_grp)
            spline_grp = group(splines,n = (name + '_spline_grp'),p=hidden_grp)
            bind_loc_grp = group(bind_locs,n=(name + '_bind_loc_grp'),p = hidden_grp)
            hidden_grp.visibility.set(0)
            bind_loc_grp.inheritsTransform.set(0)
            spline_grp.inheritsTransform.set(0)
            select(cl=True)
            
            #Connections
            connect_objs_to_node(bones,network,'bones')
            connect_objs_to_node(all_anims,network,'anims')
            connect_objs_to_node(aim_joint_ends,network,'control_joints')
            connect_objs_to_node(upper_lids,network,'upper_lid_bones')
            connect_objs_to_node(lower_lids,network,'lower_lid_bones')
            connect_objs_to_node([inner_corner,outer_corner],network,'corner_lid_bones')
            connect_objs_to_node([component_grp],network,'component_grp')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')
    
    def make_middle_spline(self,name,upper_cv,lower_cv,smooth = True):
        #Make Locators representing the splines
        mid_locs = []
        for cv in [upper_cv,lower_cv]:
            for i in range(0,8):
                u =  float(i * (1.00/7.00))
                loc = spaceLocator(n = (cv + '_temp_loc_'+str(i)),p=(0,0,0))
                curve_constraint(cv,loc,u)
        
        #Create Mid Locators
        for i in range(0,8):
            mid_loc = spaceLocator(n = ('mid_loc_'+str(i)),p=(0,0,0))
            up_loc = xform((upper_cv + '_temp_loc_'+str(i)), q= True, ws=True, rp=True);
            down_loc = xform((lower_cv + '_temp_loc_'+str(i)), q= True, ws=True, rp=True);
            translate = [((up_loc[0] + down_loc[0])/2.00),((up_loc[1] + down_loc[1])/2.00),((up_loc[2] + down_loc[2])/2.00)]
            move(translate[0],translate[1],translate[2], mid_loc, rpr = True);
            delete((upper_cv + '_temp_loc_'+str(i)),(lower_cv + '_temp_loc_'+str(i)))
            mid_locs.append(mid_loc)
            select(cl=True)
        
        #Make Spline
        spline = make_spline(name + '_mid_spline',chain = mid_locs)
        delete(mid_locs)
        return spline
    
    def create_blend_shapes(self,upper_cv,lower_cv,mid_cv):
        og_upper_cv = duplicate(upper_cv)[0].rename(upper_cv + '_original')
        og_lower_cv = duplicate(lower_cv)[0].rename(lower_cv + '_original')

        blends = []
        blends += blendShape(og_upper_cv,og_lower_cv,mid_cv,n=(mid_cv + '_blend'))
        
        blends += blendShape(og_upper_cv,mid_cv,upper_cv,n=(upper_cv + '_blend'))
        blends += blendShape(og_lower_cv,mid_cv,lower_cv,n=(lower_cv + '_blend'))
        select(cl=True)
        
        return [[og_upper_cv, og_lower_cv],blends]

    def make_anims(self,name,upper_lid,lower_lid):
        anims = []
        nulls = []
        i = 0
        select(cl=True)
        #Corner Anims
        for s in ['_inner','_outer']:
            n = name + s + '_anim'
            anim = self.oriented_anim(n,upper_lid,i)
            anims.append(anim)
            i += 1
        #Mid Anims
        for lid in [upper_lid,lower_lid]:
            if lid == upper_lid:
                l = '_upper'
            else:
                l = '_lower'
            value = [0.125,0.25,0.5,0.75,0.875]
            i = 0
            for s in ['_inner','_mid_inner','_mid','_mid_outer','_outer']:
                n = name + l + s + '_anim'
                anim = self.oriented_anim(n,lid,value[i])
                anims.append(anim)
                i += 1
        
        #Create Nulls
        for anim in anims:
            null = group(n = anim + '_zero_grp',em=True)
            aligner([null],anim)
            parent(anim,null)
            nulls.append(null)
            
        return [anims,nulls]

    def oriented_anim(self,n,cv,value):
        anim = joint(n = n,p=(0,0,0),r=4.00)
        curve_constraint(cv,anim,value)
        translation = anim.translate.get()
        rotation = anim.rotate.get()
        delete(listConnections(anim))
        anim.translate.set(translation)
        anim.rotate.set(0,0,0)
        anim.jointOrient.set(rotation)
        select(cl=True)
        return anim