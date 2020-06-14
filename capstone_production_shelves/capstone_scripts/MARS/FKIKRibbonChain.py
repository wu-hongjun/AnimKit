import pymel.all as pm
from  MARS.FKIKLimb import FKIKLimb
import MARS.MarsUtilities as mu
reload(mu)

class FKIKRibbonChain(FKIKLimb):
    '''
    MANDATORY VARIABLES
        side = Use the string center, left, or right.
        limb = Use a string to describe what body part of the rig this applies to.
        start = String of the first bone in the chain.
        end = String of the last bone in the chain.
    
    OPTIONAL VARIABLES
        stretch = Default to True. Uses to determine if the FKIK anims have a stretch attribute.
        stretch_type = Default to 'position.' Used to determine if the scale is driven by translation attributes
                       or by the scale attributes.
        IK_anim_num = Default to 5. Determines the amount of IK anims for the spline chain.
        dv = Default value set to 0. Determines if the component starts in FK or IK mode.
             0 is FK. 1 is IK.
    
    SPECIALTY VARIABLES
        connect_to = Default to None. Requires a class listed as a variable to parent the current node to.
                     Needs the 'area' variable to work
        area = Default to None. Uses 'start', 'end', or a specific bone string connected to the 
               variable in the 'connected_to' variable.
               
        rig = Default to None. Requires the class of a CharacterRig node.
              Adds node to the component_grp of the CharacterRig node.
              
        node = Default to None. Used for the Marking Menu. Used for reacquiring the class functionality.
    '''
    
    def __init__(self, side, limb, start, end, stretch = True, stretch_type = 'position', IK_anim_num = 5, dv = 0, connect_to = None, area = None, rig = None, node = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('FKIKRibbonChain',start,'start')
        
        if self.node == None:
            FKIKLimb.__init__(self,'FKIKRibbonChain', side, limb, start = start, end = end)
            
            #Variables
            name = side + '_' + limb
            bones = mu.get_chain(start,end)
            mu.check_for_constraints(bones)
            controls = mu.duplicate_chain(bones,name,'control_joint')
            IKs = mu.duplicate_chain(bones,name,'IK_joint')
            FK_anims, nulls = mu.create_anims(bones, name, suffix = 'FK_anim')
            IK_anims, IK_nulls, nurb = mu.create_nurb_anims(name,'IK_anim',IKs,amnt = IK_anim_num)
            skin_joints = mu.duplicate_chain(IK_anims,name,'skin_joint')
            constraints = self.FKIK_constraint_setup(bones,controls,FK_anims,IKs,stretch_type)
            rots, rot_nulls = self.IK_ribbon_setup(IKs, nurb)
            switch, revs = mu.switch_setup(name,bones[0],constraints, dv = dv)
            component_grp, hidden_grp, anim_grp, other_grps = self.component_group_setup(name, other_grps = ['FK_anim','IK_anim','nurb','distance','rotation'])
            FK_grp, IK_grp, nurb_grp, dist_grp, rotation_grp = other_grps
            grps = [component_grp, hidden_grp, anim_grp, FK_grp, IK_grp, nurb_grp, dist_grp, rotation_grp]
            anims = FK_anims[:-1] + IK_anims

            #Group Setup    
            pm.parent(other_grps,switch,anim_grp)
            pm.parent(IKs[0], controls[0], nurb_grp, dist_grp, rotation_grp, hidden_grp)
            pm.parent(nulls[0],FK_grp)
            pm.parent(IK_nulls, IK_grp)
            pm.parent(rots, rot_nulls, rotation_grp)
            pm.parent(skin_joints,hidden_grp)
            nurb_grp.inheritsTransform.set(0)
            dist_grp.inheritsTransform.set(0)
            rotation_grp.inheritsTransform.set(0)
            
            #Skin Curve
            for i, sj in enumerate(skin_joints): pm.parentConstraint(IK_anims[i],sj,mo = True)
            pm.skinCluster(skin_joints,nurb,n = nurb + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
        
            #Attribute Locks
            FK_anims[-1].v.set(0)
            mu.aligner(grps,bones[0],position = False, rotation = False, pivot = True)
            mu.lock_and_hide_attrs(FK_anims[0],['scale','visibility','radius'])
            mu.lock_and_hide_attrs(FK_anims[1:],['translate','scale','visibility','radius'])
            mu.lock_and_hide_attrs(IK_anims,['scale','visibility','radius'])
            mu.lock_and_hide_attrs(nulls,['translate','rotate','scale','visibility','radius'])
            mu.lock_and_hide_attrs(IK_nulls,['translate','rotate','scale','visibility','radius'])
            mu.lock_and_hide_attrs(other_grps,['translate','rotate','scale'])
            mu.lock_and_hide_attrs([anim_grp,hidden_grp],['translate','rotate','scale'])
    
            ##Assign To Node
            mu.con_link(bones,self.node,'bones')
            mu.con_link(anims,self.node,'anims')
            mu.con_link(FK_anims[:-1],self.node,'FK_anims')
            mu.con_link(IK_anims,self.node,'IK_anims')
            mu.con_link(switch, self.node, 'switch')
            mu.con_link(controls,self.node,'control_joints')
            mu.con_link(IKs,self.node,'IK_joints')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            mu.con_link(FK_grp,self.node,'FK_anim_grp')
            mu.con_link(IK_grp,self.node,'IK_anim_grp')
            self.node.addAttr('stretch',at = 'bool', dv = stretch)
            self.node.stretch.lock()
        
            #Stretch Setup
            if stretch == True:
                FK_mds = mu.FK_stretch_setup(FK_anims,nulls,controls,stretch_type)
                IK_mds, locs, dists, nurb_nulls = self.IK_spline_stretch_setup(IKs, nurb, stretch_type)
                self.FKIK_stretch_blend(switch, controls, FK_mds, IK_mds, stretch_type)
                
                pm.parent(locs, [x.getParent() for x in dists], dist_grp)
                pm.parent(nurb, nurb_nulls ,nurb_grp)
                
                mu.con_link(dists,self.node,'distances')
                self.node.setAttr('stretch_type',stretch_type,f = True)
                self.node.stretch_type.lock()
    
            IK_snaps = self.IK_anim_snaps(FK_anims, IK_anims, IK_anim_num, False)
            
            #Finalize
            self.FKIK_group_vis_setup(switch,FK_grp,IK_grp)
            self.finalize_anims()
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)
            pm.select(cl = True)
            
    def IK_ribbon_setup(self, IKs, nurb):
        locators = []
        positions = []
        rotations = []
        nulls = []
        amnt = 0.00
        length = mu.get_bone_length(IKs[0],IKs[-1])
        
        for i, IK in enumerate(IKs):
            if i > 0 and i != len(IKs) - 1: amnt += mu.get_bone_length(IKs[i-1],IKs[i])/length
            elif i == len(IKs) - 1: amnt = 1.00
            pm.select(cl = True)
            pos = pm.joint(n = IK + '_rot_null', p = (0,0,0))
            rot = pm.joint(n = IK + '_rot', p = (0,0,0))
            loc = pm.group(n = IK + '_rot_wuo', em = True)
            pm.parent(loc, rot)
            nulls.append(mu.nurbs_constraint(nurb, pos, u = 0.5, v = amnt))
            mu.aligner(rot,IK)
            pm.makeIdentity(rot,t = True, r = True, s = True, jo = False, a = True)
            loc.ty.set(10)
            pm.parent(loc,pos)
            rot.translate.set(0,0,0)
            locators.append(loc)
            rotations.append(rot)
            positions.append(pos)
            
        for i, IK in enumerate(IKs[:-1]):
            pm.aimConstraint(rotations[i + 1], IK, mo = True, wut = 'object', wuo = locators[i])
        pm.pointConstraint(rotations[0],IKs[0],mo = True)    
        pm.parentConstraint(rotations[-1],IKs[-1],mo = True, st = ['x','y','z'])
        
        return positions, nulls