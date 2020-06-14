import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class FlexibleEyelid(MarsRigComponent):
    '''
    #MANDATORY VARIABLES
        side = Use the string center, outer, or inner.
        limb = Use a string to describe what body part of the rig this applies to.
        upper_lids = Use a list of the joints for the upper lip from the character's inner to outer.
                     Does not include corner joints.
        lower_lids = Use a list of the joints for the lower lip from the character's inner to outer.
                     Does not include corner joints.
        inner_corner = Use a string for the name of the inner corner bone.
        outer_corner = Use a string for the name of the outer corner bone.
        
    #OPTIONAL VARIABLES
        nurb = Requires the string of a nurbSurface. This surface should map out where the teeth are.
        secondary_anims = Defaults to True. Creates a second layer of anims for added fine movement.
        jaw = Default to None. Requires a string of a jaw bone. Connects the lower lip to the jaw bone.
    
    #SPECIALTY VARIABLES
        connect_to = Default to None. Requires a class listed as a variable to parent the current node to.
                     Needs the 'area' variable to work
        area = Default to None. Uses 'start', 'end', or a specific bone string connected to the 
               variable in the 'connected_to' variable.
               
        rig = Default to None. Requires the class of a CharacterRig node.
              Adds node to the component_grp of the CharacterRig node.
              
        node = Default to None. Used for the Marking Menu. Used for reacquiring the class functionality.
    '''
    def __init__(self, side, limb, upper_lids, lower_lids, inner_corner, outer_corner, eye_joint,
                 secondary_anims = True, node = None, connect_to = None, area = None, rig = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('FlexibleEyelid',upper_lids[0],'upper_lid_bones')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'FlexibleEyelid', side, limb, start = '', end = '')
            
            #Variables
            name = side + '_' + limb
            upper_lids = [pm.PyNode(x) for x in upper_lids]
            lower_lids = [pm.PyNode(x) for x in lower_lids]
            outer_corner = pm.PyNode(outer_corner)
            inner_corner = pm.PyNode(inner_corner)
            eye_joint = pm.PyNode(eye_joint)
            full_upper_lid = [inner_corner] + upper_lids + [outer_corner]
            full_lower_lid = [inner_corner] + lower_lids + [outer_corner]
            bones = [inner_corner] + upper_lids + [outer_corner ]+ lower_lids
            
            #Control Setups
            upper_controls, upper_control_IKs, upper_IKHs = self.control_setup(name + '_upper',upper_lids,eye_joint)
            lower_controls, lower_control_IKs, lower_IKHs = self.control_setup(name + '_lower',lower_lids,eye_joint)
            inner_control, inner_control_IK, inner_IKH = self.control_setup(name + '_inner',inner_corner,eye_joint)
            outer_control, outer_control_IK, outer_IKH = self.control_setup(name + '_outer',outer_corner,eye_joint)
            controls = [inner_control] + upper_controls + [outer_control] + lower_controls
            control_IKs = [inner_control_IK] + upper_control_IKs + [outer_control_IK] + lower_control_IKs
            IKHs = [inner_IKH] + upper_IKHs + [outer_IKH] + lower_IKHs
            
            ##Primary Lip Anims
            upper_anims, upper_nulls, upper_nurb = self.create_lid_anims(name + '_upper',full_upper_lid)
            lower_anims, lower_nulls, lower_nurb = self.create_lid_anims(name + '_lower',full_lower_lid)
            outer_anim, outer_null = mu.create_anims(outer_corner,name + '_outer',end = False,type = 'sphere')
            inner_anim, inner_null = mu.create_anims(inner_corner,name + '_inner',end = False,type = 'sphere')
            top_anim, top_null = mu.create_anims(eye_joint,name + '_upper_eyelid',end = False)
            bottom_anim, bottom_null = mu.create_anims(eye_joint,name + '_lower_eyelid',end = False)
            primary_anims = [inner_anim] + upper_anims + [outer_anim] + lower_anims 
            anims = [inner_anim] + upper_anims + [outer_anim] + lower_anims
            anims += [top_anim,bottom_anim]
            
            #Secondary Anim Setup
            if secondary_anims == True: 
                u_sec_anims, u_sec_nulls = mu.create_anims(upper_lids, name + '_upper', suffix = 'secondary_anim', separate = True, end = False)
                l_sec_anims, l_sec_nulls = mu.create_anims(lower_lids, name + '_lower', suffix = 'secondary_anim', separate = True, end = False)
                inner_sec_anim, inner_sec_null = mu.create_anims(inner_corner, name + '_inner', suffix = 'secondary_anim', separate = True, end = False)
                outer_sec_anim, outer_sec_null = mu.create_anims(outer_corner, name + '_outer', suffix = 'secondary_anim', separate = True, end = False)
                sec_anims = [inner_sec_anim] + u_sec_anims + [outer_sec_anim] + l_sec_anims
                sec_anim_nulls = [inner_sec_null] + u_sec_nulls + [outer_sec_null] + l_sec_nulls
                anims += sec_anims
            
            #Nurb Setup
            mid_nurb, s_upper_nurb, s_lower_nurb = self.middle_blend_setup(name,top_anim, bottom_anim, upper_nurb, lower_nurb)
            
            #Parent_Anim Setup
            pm.parent(upper_nulls,top_anim)
            pm.parent(lower_nulls,bottom_anim)
            
            #Constraint Setup
            pm.pointConstraint(upper_anims[1],inner_anim,upper_anims[0].getParent(),mo = True)
            pm.pointConstraint(upper_anims[-2],outer_anim,upper_anims[-1].getParent(),mo = True)
            pm.pointConstraint(lower_anims[1],inner_anim,lower_anims[0].getParent(),mo = True)
            pm.pointConstraint(lower_anims[-2],outer_anim,lower_anims[-1].getParent(),mo = True)
            for i, b in enumerate(bones): pm.parentConstraint(controls[i],b,mo = True)
            
            #Constrain To Controls
            zero_nulls = self.lip_nurb_constraint_setup(upper_IKHs,inner_IKH,outer_IKH,upper_nurb,sides = True)
            zero_nulls += self.lip_nurb_constraint_setup(lower_IKHs,inner_IKH,outer_IKH,lower_nurb)
            
            #Skinning
            full_upper_anims = [inner_anim] + upper_anims + [outer_anim]
            full_lower_anims = [inner_anim] + lower_anims + [outer_anim]
            pm.skinCluster(full_upper_anims,s_upper_nurb,n = upper_nurb + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
            pm.skinCluster(full_lower_anims,s_lower_nurb,n = lower_nurb + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
            
            #Group Setup
            extra_grps = ['primary_anim','secondary_anim','control','IK_handle','nurbs']
            component_grp, hidden_grp, anim_grp, other_grps = self.component_group_setup(name, other_grps = extra_grps)
            prim_grp, sec_grp, control_grp, IK_handle_grp, nurb_grp = other_grps
            sec_grp.visibility.set(0)
            
            pm.parent(inner_null, outer_null, top_null, bottom_null, prim_grp)
            pm.parent(prim_grp, sec_grp, anim_grp)
            if secondary_anims == True: pm.parent(sec_anim_nulls, sec_grp)
            else: pm.delete(sec_grp)
            nurb_grp.inheritsTransform.set(0)
            IK_handle_grp.inheritsTransform.set(0)
            pm.parent(IKHs,IK_handle_grp)
            pm.parent(control_IKs,control_grp)
            pm.parent(upper_nurb,lower_nurb,mid_nurb, s_upper_nurb, s_lower_nurb,nurb_grp)
            pm.parent(nurb_grp, IK_handle_grp, control_grp, hidden_grp)
            
            #Lock And Hide Attrs
            mu.lock_and_hide_attrs(anims,['scale','radius','visibility'])
            mu.lock_and_hide_attrs(other_grps,'all')
            mu.lock_and_hide_attrs(hidden_grp,'all')
            
            #Connections
            mu.con_link(anims,self.node,'anims')
            mu.con_link(bones,self.node,'bones')
            mu.con_link(controls,self.node,'controls')
            mu.con_link(upper_anims,self.node,'upper_anims')
            mu.con_link(lower_anims,self.node,'lower_anims')
            mu.con_link(upper_lids,self.node,'upper_lid_bones')
            mu.con_link(lower_lids,self.node,'lower_lid_bones')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            mu.con_link(primary_anims,self.node,'primary_anims')
            mu.con_link([inner_anim,outer_anim],self.node,'corner_anims')
            mu.con_link([inner_corner,outer_corner],self.node,'corner_bones')
            if secondary_anims == True: mu.con_link(sec_anims,self.node,'secondary_anims') 

            ##Finish
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)
        
    def middle_blend_setup(self,name,top_anim,bottom_anim,upper_nurb,lower_nurb):
        start_upper_nurb = pm.duplicate(upper_nurb,n = upper_nurb + '_start')[0]
        start_lower_nurb = pm.duplicate(lower_nurb,n = lower_nurb + '_start')[0]
        new_nurbs = [start_upper_nurb,start_lower_nurb]
        mid_nurb = pm.duplicate(upper_nurb,n = name + '_center_nurb')[0]
        mid_nurb.inheritsTransform.set(1)
        temp_blend = pm.blendShape(upper_nurb, lower_nurb, mid_nurb,n = 'temp', tc = True)[0]
        temp_blend.attr(upper_nurb).set(0.5)
        temp_blend.attr(lower_nurb).set(0.5)
        pm.delete(mid_nurb,ch = True)
        
        upper_blend = pm.blendShape(start_upper_nurb,mid_nurb,upper_nurb,n = upper_nurb + '_blend',tc = True)[0]
        lower_blend = pm.blendShape(start_lower_nurb,mid_nurb,lower_nurb,n = lower_nurb + '_blend',tc = True)[0]
        middle_blend = pm.blendShape(start_upper_nurb, start_lower_nurb, mid_nurb, n = lower_nurb + '_blend',tc = True)[0]
        blends = [upper_blend,lower_blend]
        
        for i, anim in enumerate([top_anim,bottom_anim]):
            anim.addAttr('blink',at = 'double', dv = 0, min = 0, max = 1, k = True)
            anim.blink >> blends[i].attr(mid_nurb)
            rev = mu.create_node('reverse',n = anim + '_blink_rev')
            anim.blink >> rev.inputX
            rev.outputX >> blends[i].attr(new_nurbs[i])
            
        top_anim.addAttr('blink_height',at = 'double', dv = 0.5 ,min = 0,max = 1,k = True)
        rev = mu.create_node('reverse',n = name + '_blink_height_reverse')
        top_anim.blink_height >> rev.inputX
        top_anim.blink_height >> middle_blend.attr(start_upper_nurb)
        rev.outputX >> middle_blend.attr(start_lower_nurb)
        
        return mid_nurb, start_upper_nurb, start_lower_nurb
        
    def get_distance_between(self,bones):
        value = 0
        for bone in bones[1:]: value += abs(pow(pow(bone.tx.get(),2) + pow(bone.ty.get(),2) + pow(bone.tz.get(),2),0.5))
        return value
    
    def control_setup(self,name,bones,eye_joint):
        if not isinstance(bones,list): bones = [bones]
        controls = mu.duplicate_chain(bones,name,'control_joint',separate = True)
        IK_jnts = []
        IK_handles = []
        for c in controls:
            pm.select(cl = True)
            IK_jnt = pm.joint(n = c.replace('_joint','_IK'),p = (0,0,0))
            mu.aligner(IK_jnt,eye_joint)
            pm.parent(c,IK_jnt)
            IKH, eff = pm.ikHandle(n = c.replace('_joint','_IKH'),sj = IK_jnt, ee = c, sol = 'ikSCsolver')
            IK_jnts.append(IK_jnt)
            IK_handles.append(IKH)
        if len(bones) > 1: return controls, IK_jnts, IK_handles
        else: return controls[0], IK_jnts[0], IK_handles[0]

    def lip_nurb_constraint_setup(self,objs,inner,outer,nurb,sides = False):
        nulls = []
        all_objs = [inner] + objs + [outer]
        length = self.get_distance_between(all_objs)
        prct = 1.00/(len(all_objs) - 1.00)
        for i, ob in enumerate(objs):
            amnt = prct * (i + 1.00)
            nulls += [mu.curve_constraint(nurb, ob, amnt)]
        if sides == True:
            nulls += [mu.curve_constraint(nurb, inner, 0.0)]
            nulls += [mu.curve_constraint(nurb, outer, 1.0)]
        return nulls
    
    def create_lid_anims(self,name,bones):
        areas = [0.1,0.25,0.5,0.75,0.9]
        anims, nulls, nurb = mu.create_spline_anims(name,'anim',bones,amnt = 5, spots = areas)
        for n in nulls: n.jointOrient.set(0,0,0)
        ns = ['inner_corner','inner','middle','outer','outer_corner']
        for i, anim in enumerate(anims):
            anim.rename(name + '_' + ns[i] + '_anim')
            nulls[i].rename(name + '_' + ns[i] + '_null')
        nurb.rename(name + '_lid_nurb')
        return anims, nulls, nurb
    
    def get_primary_anims(self):
        return pm.listConnections(self.node.primary_anims)
        
    def get_secondary_anims(self):
        if self.node.hasAttr('secondary_anims') == True: return pm.listConnections(self.node.secondary_anims)
        else: return None