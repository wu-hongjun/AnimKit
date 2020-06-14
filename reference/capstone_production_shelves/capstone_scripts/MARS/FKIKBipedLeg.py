import pymel.all as pm
from MARS.FKIKLimb import FKIKLimb
import MARS.MarsUtilities as mu
reload(mu)

class FKIKBipedLeg(FKIKLimb):
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
    
    def __init__(self, side, limb, start, end, front_piv ,back_piv, inner_piv, outer_piv, soft_IK = True,
                 stretch = True, stretch_type = 'position', dv = 0, connect_to = None, area = None, rig = None, node = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('FKIKBipedLeg',start,'start')
        
        if self.node == None:
            #Run Function
            FKIKLimb.__init__(self,'FKIKBipedLeg', side, limb, start = start, end = end)
            
            #Variables
            name = self.node.side.get() + '_' + self.node.limb.get()
            bones = mu.get_chain(start,end)
            mu.check_for_constraints(bones)
            pivots = [pm.PyNode(x) for x in [back_piv ,inner_piv, outer_piv, front_piv ,bones[-2], bones[-3], bones[-2], bones[-1]]]
            controls = mu.duplicate_chain(bones,name,'control_joint')
            IKs = mu.duplicate_chain(bones,name,'IK_joint')
            FK_anims, FK_nulls = mu.create_anims(bones, name, suffix = 'FK_anim')
            IK_anim, IK_null = mu.create_anims(bones[2], name, suffix = 'IK_anim', end = False, type = 'sphere')
            PV_anim, PV_null = mu.create_anims(bones[1], name, suffix = 'PV_anim', end = False, type = 'sphere')
            IKH, eff = pm.ikHandle(n = name + '_IKH',sj = IKs[0], ee = IKs[2], sol = 'ikRPsolver')
            foot_IKH, eff = pm.ikHandle(n = name + '_foot_IKH',sj = IKs[2], ee = IKs[3], sol = 'ikSCsolver')
            toe_IKH, eff = pm.ikHandle(n = name + '_toe_IKH',sj = IKs[3], ee = IKs[4], sol = 'ikSCsolver')
            IK_pos = pm.group(n = name + '_IKH_pos',em = True)
            mu.aligner(IK_pos,IKH)
            all_IKHs = [IKH,foot_IKH,toe_IKH]
            IK_roll, roll_anims, foot_null = self.IK_pivot_setup(name,bones,IK_anim,pivots)
            constraints = self.FKIK_constraint_setup(bones,controls,FK_anims,IKs,stretch_type)
            switch, revs = mu.switch_setup(name,bones[0],constraints, dv = dv)
            component_grp, hidden_grp, anim_grp, other_grps = self.component_group_setup(name, other_grps = ['FK_anim','IK_anim','distance'])
            FK_grp, IK_grp, dist_grp = other_grps
            grps = [component_grp, hidden_grp, anim_grp, FK_grp, IK_grp, dist_grp]
            anims = FK_anims[:-1] + [IK_anim] + [PV_anim] + roll_anims
            self.IK_roll_attribute_setup(name,IK_anim,IK_roll)
            
            #PV Placement
            PV_pos = mu.stack_chain(PV_anim,'_anim','_position_null')[0]
            if side == 'left': PV_pos.translateY.set(-1.50 * mu.get_bone_length(bones[1],bones[2]))
            else: PV_pos.translateY.set(1.50 * mu.get_bone_length(bones[1],bones[2]))
            
            ##IK Setup
            pm.parentConstraint(IK_pos,IKH,mo = True)
            pm.parentConstraint(IK_roll[-3],IK_pos,mo = True)
            pm.parentConstraint(IK_roll[-2],foot_IKH,mo = True)
            pm.parentConstraint(IK_roll[-1],toe_IKH,mo = True)
            pm.poleVectorConstraint(PV_anim,IKH)
            
            #Stretch Setup
            locs, dists, dist_cons = self.set_distance_nodes(name,IKH, IKs, IK_roll[-3], PV_anim)
            pm.parent(locs,[x.getParent() for x in dists],dist_grp)
            if stretch == True:
                FK_mds = mu.FK_stretch_setup(FK_anims[:3],FK_nulls,controls,stretch_type)
                IK_mds = self.IK_limb_stretch_setup(name,dists,IKs[:-2],IK_anim,stretch_type)
                self.FKIK_stretch_blend(switch, controls[:-2], FK_mds, IK_mds, stretch_type)
                bls = self.pole_vector_stretch(IKs,PV_anim,IK_mds,dists[1:-2],stretch_type)
                PV_FK_anims = self.PV_FK_setup(name,all_IKHs,IK_anim,PV_anim,IKs[1:],[locs[-3]],bls)
                anims += PV_FK_anims
                mu.con_link(dists,self.node,'distances')
                self.node.setAttr('stretch_type',stretch_type,f = True)
                self.node.stretch_type.lock()
                
            if soft_IK == True:
                soft_IKs, soft_IKH = self.setup_soft_IK(name,bones,IK_anim,PV_anim,dists[0],IK_pos,area = IK_roll[-3],stretch = stretch)
            IK_snaps = self.IK_anim_snaps(FK_anims[1:3], [PV_anim, IK_anim], 2, stretch)
            [pm.parent(x.getParent(),hidden_grp) for x in IK_snaps]
            
            #Parent Setup
            pm.parent(controls[0], IKs[0], IKH, foot_IKH, toe_IKH, dist_grp, IK_pos, hidden_grp)
            pm.parent(switch, FK_grp, IK_grp, anim_grp)
            #pm.parent(foot_null,IK_grp)
            pm.parent(FK_nulls[0],FK_grp)
            pm.parent(IK_null, PV_null, IK_grp)
            if soft_IK == True: pm.parent(soft_IKs[0],soft_IKH,hidden_grp)
            mu.aligner(grps, bones[0], position = False, rotation = False, pivot = True)
            
            ##Lock Attributes
            mu.lock_and_hide_attrs(switch,['translate','rotate','scale','v'])
            mu.lock_and_hide_attrs(FK_anims,['translate','scale','v','radius'])
            mu.lock_and_hide_attrs([FK_anims[1],FK_anims[3]],['rx','ry'])
            mu.lock_and_hide_attrs(FK_nulls,'all')
            mu.lock_and_hide_attrs([IK_null, PV_null],'all')
            mu.lock_and_hide_attrs([IK_anim,PV_anim],['scale','v','radius'])
            mu.lock_and_hide_attrs(IK_snaps,'all')
            pm.select(cl=True)
            
            ##Assign To Node
            mu.con_link(bones,self.node,'bones')
            mu.con_link(anims,self.node,'anims')
            mu.con_link([PV_anim,IK_anim],self.node,'IK_anims')
            mu.con_link(FK_anims[:-1],self.node,'FK_anims')
            mu.con_link(IK_roll,self.node,'IK_pivots')
            mu.con_link(IKs,self.node,'IK_joints')
            mu.con_link(all_IKHs,self.node,'IK_handles')
            mu.con_link(switch,self.node,'switch')
            mu.con_link(controls,self.node,'control_joints')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            mu.con_link(FK_grp,self.node,'FK_anim_grp')
            mu.con_link(IK_grp,self.node,'IK_anim_grp')
            #mu.con_link(IK_snaps,self.node,'IK_snaps')
            mu.con_link(foot_null,self.node,'foot_null')
            
            self.node.addAttr('stretch',at = 'bool', dv = stretch)
            self.node.stretch.lock()

            #Finalize
            self.FKIK_group_vis_setup(switch,FK_grp,IK_grp)
            self.finalize_anims()
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)
            pm.select(cl = True)