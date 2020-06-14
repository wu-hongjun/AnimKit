import pymel.all as pm
from  MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class COGChain(MarsRigComponent):
    '''
    MANDATORY VARIABLES
        side = Use the string center, left, or right.
        limb = Use a string to describe what body part of the rig this applies to.
        start = String of the first bone in the chain.
        end = String of the last bone in the chain.
    
    OPTIONAL VARIABLES
        orient_to_world = Default to True. Changes priority of the anim's default rotation to the world axis.
    
    SPECIALTY VARIABLES
        connect_to = Default to None. Requires a class listed as a variable to parent the current node to.
                     Needs the 'area' variable to work
        area = Default to None. Uses 'start', 'end', or a specific bone string connected to the 
               variable in the 'connected_to' variable.
               
        rig = Default to None. Requires the class of a CharacterRig node.
              Adds node to the component_grp of the CharacterRig node.
              
        node = Default to None. Used for the Marking Menu. Used for reacquiring the class functionality.
    '''
    def __init__(self,side,limb,start,end,orient_to_world = True, connect_to = None, area = None, rig = None, node = None):
        self.node = node
        if node != None: self.node = node
        else: self.node = self.exist_check('COGChain',start,'start')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'COGChain', side, limb, start = start, end = end)
            
            #Variables
            name = self.node.side.get() + '_' + self.node.limb.get()

            #Setup
            bones = mu.get_chain(start,end)
            mu.check_for_constraints(bones)
            controls = mu.duplicate_chain(bones,name,'control_joint')
            COG = mu.duplicate_chain(controls,name,'anim',show = False,orient_to_world = orient_to_world)
            COG_nulls = mu.stack_chain(COG[:-1],'_anim','_null')
            mu.default_anim_shape(COG[:-1],r = 2.00)
            
            #Constraints
            for i, bone in enumerate(bones[:-1]):
                pm.parentConstraint(controls[i], bone, mo = True)
                pm.parentConstraint(COG[i], controls[i], mo = True)
                
            #Group Setup
            component_grp, hidden_grp, anim_grp = self.component_grp_setup(name,start)
            pm.parent(COG_nulls[0],anim_grp)
            pm.parent(controls[0],hidden_grp)
            
            ##Lock Attributes
            mu.lock_and_hide_attrs(COG_nulls,'all')
            mu.lock_and_hide_attrs(COG,['scale','v','radius'])
            
            ##Assign To Node
            mu.con_link(bones,self.node,'bones')
            mu.con_link(COG[:-1],self.node,'anims')
            mu.con_link(controls,self.node,'control_joints')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            
            ##Finish
            self.finalize_anims()
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)