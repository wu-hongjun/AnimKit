import pymel.all as pm
from  MARS.FKIKLimb import FKIKLimb
import MARS.MarsUtilities as mu
reload(mu)

class FKIKSplineChain(FKIKLimb):
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
        else: self.node = self.exist_check('FKIKSplineChain',start,'start')
        
        if self.node == None:
            FKIKLimb.__init__(self,'FKIKSplineChain', side, limb, start = start, end = end)
            
            #Variables
            name = side + '_' + limb
            bones = mu.get_chain(start,end)
            mu.check_for_constraints(bones)
            controls = mu.duplicate_chain(bones,name,'control_joint')
            IKs = mu.duplicate_chain(bones,name,'IK_joint')
            FK_anims, nulls = mu.create_anims(bones, name, suffix = 'FK_anim')
            IK_anims, IK_nulls, cv = mu.create_spline_anims(name,'IK_anim',bones,amnt = IK_anim_num)
            skin_joints = mu.duplicate_chain(IK_anims,name,'skin_joint')
            IKH, eff = pm.ikHandle(n = name + '_IKH',sj = IKs[0], ee = IKs[-1], sol = 'ikSplineSolver', ccv = False, c = cv)
            constraints = self.FKIK_constraint_setup(bones,controls,FK_anims,IKs,stretch_type)
            switch, revs = mu.switch_setup(name,bones[0],constraints, dv = dv)
            component_grp, hidden_grp, anim_grp, other_grps = self.component_group_setup(name, other_grps = ['FK_anim','IK_anim','cv','distance'])
            FK_grp, IK_grp, cv_grp, dist_grp = other_grps
            grps = [component_grp, hidden_grp, anim_grp, FK_grp, IK_grp, cv_grp, dist_grp]
            anims = FK_anims[:-1] + IK_anims

            #Group Setup    
            pm.parent(other_grps,switch,anim_grp)
            pm.parent(IKs[0],IKH, controls[0], cv_grp, dist_grp, hidden_grp)
            pm.parent(nulls[0],FK_grp)
            pm.parent(IK_nulls, IK_grp)
            pm.parent(cv,cv_grp)
            pm.parent(skin_joints,hidden_grp)
            
            #Skin Curve
            for i, sj in enumerate(skin_joints): pm.parentConstraint(IK_anims[i],sj,mo = True)
            pm.skinCluster(skin_joints,cv,n = cv + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
            
            #Attribute Locks
            FK_anims[-1].v.set(0)
            mu.aligner(grps,bones[0],position = False, rotation = False, pivot = True)
            mu.lock_and_hide_attrs(FK_anims[0],['scale','visibility','radius'])
            mu.lock_and_hide_attrs(IK_anims,['scale','visibility','radius'])
            mu.lock_and_hide_attrs(FK_anims[1:],['translate','scale','visibility','radius'])
            mu.lock_and_hide_attrs(nulls,['translate','rotate','scale','visibility','radius'])
            mu.lock_and_hide_attrs(IK_nulls,['translate','rotate','scale','visibility','radius'])
            mu.lock_and_hide_attrs(grps,['translate','rotate','scale'])
            mu.lock_and_hide_attrs([anim_grp,hidden_grp],['translate','rotate','scale'])
            dist_grp.inheritsTransform.set(0)
    
            ##Assign To Node
            mu.con_link(bones,self.node,'bones')
            mu.con_link(anims,self.node,'anims')
            mu.con_link(FK_anims[:-1],self.node,'FK_anims')
            mu.con_link(IK_anims,self.node,'IK_anims')
            mu.con_link(IKH,self.node,'IK_handle')
            mu.con_link(switch, self.node, 'switch')
            mu.con_link(controls,self.node,'control_joints')
            mu.con_link(IKs,self.node,'IK_joints')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            mu.con_link(FK_grp,self.node,'FK_anim_grp')
            mu.con_link(IK_grp,self.node,'IK_anim_grp')
            mu.con_link(skin_joints,self.node,'skin_joints')
            
            self.node.addAttr('stretch',at = 'bool', dv = stretch)
            self.node.stretch.lock()
            
            #IK Twist
            self.IK_twist()
            
            #Stretch Setup
            if stretch == True:
                FK_mds = mu.FK_stretch_setup(FK_anims,nulls,controls,stretch_type)
                IK_mds, locs, dists = self.IK_spline_stretch_setup(IKs, cv, stretch_type)
                pm.parent(locs,[x.getParent() for x in dists],dist_grp)
                self.FKIK_stretch_blend(switch, controls, FK_mds, IK_mds, stretch_type)
                
                mu.con_link(dists,self.node,'distances')
                self.node.setAttr('stretch_type',stretch_type,f = True)
                self.node.stretch_type.lock()
                
            IK_snaps = self.IK_anim_snaps(FK_anims, IK_anims, IK_anim_num, stretch)

            #Finalize
            self.FKIK_group_vis_setup(switch,FK_grp,IK_grp)
            self.finalize_anims()
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)
            pm.select(cl = True)
            
    def IK_twist(self):
        IK_handle = pm.listConnections(self.node.IK_handle)[0]
        IK_anims = pm.listConnections(self.node.IK_anims)
        
        twist_md = mu.create_node('multiplyDivide')
        twist_pma = pm.shadingNode('plusMinusAverage',au=True)
        roll_pma = pm.shadingNode('plusMinusAverage',au=True)
            
        twist_md.input2X.set(-1)
        IK_anims[0].rotateX >> roll_pma.input1D[0]
        roll_pma.output1D >> IK_handle.roll
        roll_pma.output1D >> twist_md.input1X
            
        IK_anims[-1].rotateX >> twist_pma.input1D[0]
        twist_md.outputX >> twist_pma.input1D[1]
        twist_pma.output1D >> IK_handle.twist