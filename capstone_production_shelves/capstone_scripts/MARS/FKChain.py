import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class FKChain(MarsRigComponent):
    '''
    MANDATORY VARIABLES
        side = Use the string center, left, or right.
        limb = Use a string to describe what body part of the rig this applies to.
        start = String of the first bone in the chain.
        end = String of the last bone in the chain.
    
    OPTIONAL VARIABLES
        translate = Makes the anims able to move position.
        stretch = Allows the anims the ability to stretch.
        stretch_type = States the type of stretching that occurs. Either use 'position' or 'scale'.
    
    SPECIALTY VARIABLES
        connect_to = Requires a class listed as a variable to parent the current node to.
                     Needs the 'area' variable to work
        area = Uses 'start', 'end', or a specific bone string connected to the 
               variable in the 'connected_to' variable.
                   
        rig = Requires the class of a CharacterRig node. Adds node to the component_grp of the CharacterRig node.
        node = used for the Marking Menu. Used for reacquiring the class functionality.
    '''
    def __init__(self, side, limb, start, end, translate = False, stretch = True, stretch_type = 'position',connect_to = None, area = None, rig = None, node = None):   
        if node != None: self.node = node
        else: self.node = self.exist_check('FKChain',start,'start')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'FKChain', side, limb, start = start, end = end)
            
            #Variables
            name = self.node.side.get() + '_' + self.node.limb.get()
            lock = ['scale','v','radius']
            if translate == False: lock += ['translate']
            
            ##Bones and Anims
            bones = mu.get_chain(start,end)
            mu.check_for_constraints(bones)
            controls = mu.duplicate_chain(bones,name,'control_joint')
            FKs = mu.duplicate_chain(bones,name,'anim',show = False)
            FK_nulls = mu.stack_chain(FKs,'_anim','_null')
            mu.default_anim_shape(FKs[:-1])
            
            ##Setup Bones
            for i, bone in enumerate(bones[:-1]):
                pm.parentConstraint(controls[i], bone, mo = True)
                pm.parentConstraint(FKs[i], controls[i], mo = True)
                
            if stretch == True: mu.FK_stretch_setup(FKs,FK_nulls,controls,stretch_type)
            
            #Group Setup
            component_grp, hidden_grp, anim_grp = self.component_grp_setup(name,start)
            pm.parent(FK_nulls[0],anim_grp)
            pm.parent(controls[0],hidden_grp)
            
            ##Lock Attributes
            mu.lock_and_hide_attrs(FKs,lock)
            mu.lock_and_hide_attrs(FK_nulls,'all')
            pm.select(cl=True)
            
            ##Assign To Node
            mu.con_link(bones,self.node,'bones')
            mu.con_link(FKs[:-1],self.node,'anims')
            mu.con_link(FKs[:-1],self.node,'FK_anims')
            mu.con_link(controls,self.node,'control_joints')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            self.node.addAttr('translate',at = 'bool',dv = translate)
            self.node.setAttr('stretch_type',stretch_type,f = True)
            self.node.translate.lock()
            self.node.stretch_type.lock()
            
            ##Finish
            self.finalize_anims()
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)