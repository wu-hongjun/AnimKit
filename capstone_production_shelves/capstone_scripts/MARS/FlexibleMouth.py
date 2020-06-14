import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class FlexibleMouth(MarsRigComponent):
    '''
    MANDATORY VARIABLES
        side = Use the string center, left, or right.
        limb = Use a string to describe what body part of the rig this applies to.
        upper_lips = Use a list of the joints for the upper lip from the character's right to left.
                     Does not include corner joints.
        lower_lips = Use a list of the joints for the lower lip from the character's right to left.
                     Does not include corner joints.
        right_corner = Use a string for the name of the right corner bone.
        left_corner = Use a string for the name of the left corner bone.
        
    OPTIONAL VARIABLES
        nurb = Requires the string of a nurbSurface. This surface should map out where the teeth are.
        secondary_anims = Defaults to True. Creates a second layer of anims for added fine movement.
        jaw = Default to None. Requires a string of a jaw bone. Connects the lower lip to the jaw bone.
    
    SPECIALTY VARIABLES
        connect_to = Default to None. Requires a class listed as a variable to parent the current node to.
                     Needs the 'area' variable to work
        area = Default to None. Uses 'start', 'end', or a specific bone string connected to the 
               variable in the 'connected_to' variable.
               
        rig = Default to None. Requires the class of a CharacterRig node.
              Adds node to the component_grp of the CharacterRig node.
              
        node = Default to None. Used for the Marking Menu. Used for reacquiring the class functionality.
        '''
    def __init__(self, side, limb, upper_lips, lower_lips, left_corner, right_corner, nurb = None,
                 secondary_anims = True, jaw = None, node = None, connect_to = None, area = None, rig = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('FlexibleMouth',upper_lips[0],'upper_lip_bones')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'FlexibleMouth', side, limb, start = '', end = '')
            
            #Variables
            name = side + '_' + limb
            upper_lips = [pm.PyNode(x) for x in upper_lips]
            lower_lips = [pm.PyNode(x) for x in lower_lips]
            left_corner = pm.PyNode(left_corner)
            right_corner = pm.PyNode(right_corner)
            full_upper_lip = [right_corner] + upper_lips + [left_corner]
            full_lower_lip = [right_corner] + lower_lips + [left_corner]
            bones = [right_corner] + upper_lips + [left_corner ]+ lower_lips
            
            #Control Setups
            upper_controls = mu.duplicate_chain(upper_lips,name + '_upper','control_joint',separate = True)
            lower_controls = mu.duplicate_chain(lower_lips,name + '_lower','control_joint',separate = True)
            right_control = mu.duplicate_chain([right_corner],name + '_right','control_joint',separate = True)[0]
            left_control = mu.duplicate_chain([left_corner],name + '_left','control_joint',separate = True)[0]
            controls = [right_control] + upper_controls + [left_control] + lower_controls
            
            ##Primary Lip Anims
            upper_anims, upper_nulls, upper_nurb = self.create_lip_anims(name + '_upper',full_upper_lip)
            lower_anims, lower_nulls, lower_nurb = self.create_lip_anims(name + '_lower',full_lower_lip)
            left_anim, left_null = mu.create_anims(left_corner,name + '_left',end = False,type = 'sphere')
            right_anim, right_null = mu.create_anims(right_corner,name + '_right',end = False,type = 'sphere')
            primary_anims = [right_anim] + upper_anims + [left_anim] + lower_anims 
            anims = [right_anim] + upper_anims + [left_anim] + lower_anims 
            
            if secondary_anims == True: 
                u_sec_anims, u_sec_nulls = mu.create_anims(upper_lips, name + '_upper', suffix = 'secondary_anim', separate = True, end = False)
                l_sec_anims, l_sec_nulls = mu.create_anims(lower_lips, name + '_lower', suffix = 'secondary_anim', separate = True, end = False)
                right_sec_anim, right_sec_null = mu.create_anims(right_corner, name + '_right', suffix = 'secondary_anim', separate = True, end = False)
                left_sec_anim, left_sec_null = mu.create_anims(left_corner, name + '_left', suffix = 'secondary_anim', separate = True, end = False)
                sec_anims = [right_sec_anim] + u_sec_anims + [left_sec_anim] + l_sec_anims
                sec_anim_nulls = [right_sec_null] + u_sec_nulls + [left_sec_null] + l_sec_nulls
                anims += sec_anims
            
            #Skin Jnts
            upper_skin_jnts = mu.duplicate_chain(upper_anims,name + '_upper','skin_joint',separate = True)
            lower_skin_jnts = mu.duplicate_chain(lower_anims,name + '_lower','skin_joint',separate = True)
            right_skin_jnt = mu.duplicate_chain(right_anim,name + '_right','skin_joint',separate = True)[0]
            left_skin_jnt = mu.duplicate_chain(left_anim,name + '_left','skin_joint',separate = True)[0]
            full_upper_lip_skin = [right_skin_jnt] + upper_skin_jnts + [left_skin_jnt]
            full_lower_lip_skin = [right_skin_jnt] + lower_skin_jnts + [left_skin_jnt]
            skin_jnts = [right_skin_jnt] + upper_skin_jnts + [left_skin_jnt] + lower_skin_jnts
            
            #Constraint Setup
            pm.pointConstraint(upper_anims[1],right_anim,upper_anims[0].getParent(),mo = True)
            pm.pointConstraint(upper_anims[-2],left_anim,upper_anims[-1].getParent(),mo = True)
            pm.pointConstraint(lower_anims[1],right_anim,lower_anims[0].getParent(),mo = True)
            pm.pointConstraint(lower_anims[-2],left_anim,lower_anims[-1].getParent(),mo = True)
            
            if nurb == None:
                for i, sj in enumerate(skin_jnts): pm.parentConstraint(primary_anims[i],sj)
            else:
                nurb = pm.PyNode(nurb)
                skin_locs, skin_pos, top_nurb, bottom_nurb = self.nurb_constraint_setup(name,primary_anims,skin_jnts,nurb)
                
            #Attach to Lip Nurbs    
            if secondary_anims == True:
                zero_nulls = self.lip_nurb_constraint_setup(u_sec_nulls,right_sec_null,left_sec_null,upper_nurb)
                zero_nulls += self.lip_nurb_constraint_setup(l_sec_nulls,right_sec_null,left_sec_null,lower_nurb, sides = False)
            else:
                zero_nulls = self.lip_nurb_constraint_setup(upper_controls,right_control,left_control,upper_nurb)
                zero_nulls += self.lip_nurb_constraint_setup(lower_controls,right_control,left_control,lower_nurb,sides = False)
            
            for i, b in enumerate(bones):
                if nurb != None:
                    if secondary_anims == True:
                        pm.pointConstraint(sec_anims[i],controls[i],mo = True)
                        pm.parentConstraint(controls[i],b,mo = True)
                    else: pm.pointConstraint(controls[i],b,mo = True)
                else:
                    if secondary_anims == True: pm.parentConstraint(sec_anims[i],controls[i],mo = True)
                    pm.parentConstraint(controls[i],b,mo = True)
            
            #Skinning
            pm.skinCluster(full_upper_lip_skin,upper_nurb,n = upper_nurb + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
            pm.skinCluster(full_lower_lip_skin,lower_nurb,n = lower_nurb + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
            upper_nurb.inheritsTransform.set(0)
            lower_nurb.inheritsTransform.set(0)
                
            #Group Setup
            extra_grps = ['primary_anim','secondary_anim','nurbs','control','skin','nurb_zero','jaw_anim','jaw_skin']
            component_grp, hidden_grp, anim_grp, other_grps = self.component_group_setup(name, other_grps = extra_grps)
            prim_grp, sec_grp, nurb_grp, control_grp, skin_grp, nurb_zero_grp, jaw_anim_grp, jaw_skin_grp = other_grps
            sec_grp.visibility.set(0)
            
            pm.parent(lower_nulls, jaw_anim_grp)
            pm.parent(upper_nulls, right_null, left_null, jaw_anim_grp, prim_grp)
            pm.parent(prim_grp, sec_grp, anim_grp)
            if secondary_anims == True:
                pm.parent(sec_anim_nulls, sec_grp)
                sec_grp.inheritsTransform.set(0)
            else:
                pm.delete(sec_grp)
                control_grp.inheritsTransform.set(0)
            pm.parent(nurb_grp, nurb_zero_grp, control_grp, skin_grp, hidden_grp)
            pm.parent(controls,control_grp)
            pm.parent(upper_nurb,lower_nurb,nurb_grp)
            if nurb:
                pm.parent(skin_pos,skin_grp)
                pm.parent(top_nurb,bottom_nurb,nurb_grp)
                pm.parent([x for x in skin_pos if 'lower' in x.name()], jaw_skin_grp)
            pm.parent(zero_nulls, nurb_zero_grp)
            pm.parent(skin_jnts, jaw_skin_grp, skin_grp)
            nurb_zero_grp.inheritsTransform.set(0)
            
            #Lock And Hide Attrs
            mu.lock_and_hide_attrs(anims,['scale','radius','visibility'])
            mu.lock_and_hide_attrs(other_grps,'all')
            mu.lock_and_hide_attrs(hidden_grp,'all')
            
            #Connections
            mu.con_link(bones,self.node,'bones')
            mu.con_link(controls,self.node,'controls')
            mu.con_link(upper_anims,self.node,'upper_anims')
            mu.con_link(lower_anims,self.node,'lower_anims')
            mu.con_link(upper_lips,self.node,'upper_lip_bones')
            mu.con_link(lower_lips,self.node,'lower_lip_bones')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            mu.con_link(primary_anims,self.node,'primary_anims')
            mu.con_link([jaw_anim_grp, jaw_skin_grp],self.node,'jaw_grps')
            mu.con_link(anims,self.node,'anims')
            mu.con_link([right_anim,left_anim],self.node,'corner_anims')
            mu.con_link([right_corner,left_corner],self.node,'corner_bones')
            if secondary_anims == True: mu.con_link(sec_anims,self.node,'secondary_anims')
            if nurb != None:
                mu.con_link(top_nurb,self.node,'upper_nurb')
                mu.con_link(bottom_nurb,self.node,'lower_nurb')

            ##Finish
            if jaw != None: self.add_jaw(jaw)
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)
        
    def get_distance_between(self,bones):
        value = 0
        for bone in bones[1:]: value += abs(pow(pow(bone.tx.get(),2) + pow(bone.ty.get(),2) + pow(bone.tz.get(),2),0.5))
        return value
    
    def get_jaw_grps(self):
        return pm.listConnections(self.node.jaw_grps)
    
    def lip_nurb_constraint_setup(self,objs,right,left,nurb,sides = True):
        nulls = []
        all_objs = [right] + objs + [left]
        length = self.get_distance_between(all_objs)
        prct = 1.00/(len(all_objs) - 1.00)
        for i, ob in enumerate(objs):
            amnt = prct * (i + 1.00)
            nulls += [mu.nurbs_constraint(nurb, ob, u = 0.5, v = amnt)]
        if sides == True:
            nulls += [mu.nurbs_constraint(nurb, right, u = 0.5, v = 0.0)]
            nulls += [mu.nurbs_constraint(nurb, left, u = 0.5, v = 1.0)]
        return nulls
    
    def nurb_constraint_setup(self,name,anims,skin_jnts,nurb):
        locators  = []
        positions = []
        top_nurb = nurb
        top_nurb.rename(name + '_upper_nurb')
        bottom_nurb = pm.duplicate(top_nurb)[0]
        bottom_nurb.rename(name + '_lower_nurb')
        
        for i, anim in enumerate(anims):
            pos = pm.group(n = anim + '_skin_pos', em = True)
            loc = pm.spaceLocator(n = anim + '_skin_loc',p = (0,0,0))
            pm.parent(loc,pos)
            locators += [loc] 
            positions += [pos]
            mu.aligner(pos,anim,rotation = False)
            if '_lower_' in anim.name():
                pm.normalConstraint(bottom_nurb,loc)
                bottom_nurb.worldSpace >> loc.geometry
            else:
                pm.normalConstraint(top_nurb,loc)
                top_nurb.worldSpace >> loc.geometry
            pm.pointConstraint(anim,loc,mo = True)
            anim.rotate >> skin_jnts[i].rotate
            anim.addAttr('pull',at = 'double',min = 0, max = 1, dv = 0,k = True)
            
            rev = mu.create_node('reverse',n = anim + '_rev')
            con = pm.pointConstraint(loc,skin_jnts[i],mo = True,w = 1)
            pm.pointConstraint(anim,skin_jnts[i], mo = True, w=0)
            con_ats = pm.listAttr(con,st = ['*W0','*W1'])
            
            anim.pull >> rev.inputX
            rev.outputX >> con.attr(con_ats[0])
            anim.pull >> con.attr(con_ats[1])
            
        return locators, positions, top_nurb, bottom_nurb
    
    def create_lip_anims(self,name,bones):
        areas = [0.1,0.25,0.5,0.75,0.9]
        anims, nulls, nurb = mu.create_nurb_anims(name,'anim',bones,amnt = 5, smooth = False, spots = areas)
        ns = ['right_corner','right','middle','left','left_corner']
        for i, anim in enumerate(anims):
            anim.rename(name + '_' + ns[i] + '_anim')
            nulls[i].rename(name + '_' + ns[i] + '_null')
            nulls[i].jointOrient.set(0,0,0)
        pm.rebuildSurface(nurb, ch = False,rpo = True, rt = 0, end = 1,du = 3, dv = 3, su = 0, sv = 0, fr = True)
        nurb.rename(name + '_lip_nurb')
        return anims, nulls, nurb
    
    def get_primary_anims(self):
        return pm.listConnections(self.node.primary_anims)
        
    def get_secondary_anims(self):
        if self.node.hasAttr('secondary_anims') == True: return pm.listConnections(self.node.secondary_anims)
        else: return None
        
    def add_jaw(self,bone):
        name = self.node.side.get() + '_' + self.node.limb.get()
        bone = pm.PyNode(bone)
        jaw_grps = pm.listConnections(self.node.jaw_grps)
        #mu.aligner(jaw_grps,bone,pivot = True)
        for jg in jaw_grps:
            for x in ['X','Y','Z']:
                jg.attr('translate' + x).unlock()
                jg.attr('rotate' + x).unlock()
            pm.parentConstraint(bone, jg, mo = True)
        if self.node.hasAttr('lower_nurb'): pm.parentConstraint(bone,pm.listConnections(self.node.lower_nurb)[0], mo = True)
        mu.con_link(bone,self.node,'jaw')
        pm.select(cl = True)