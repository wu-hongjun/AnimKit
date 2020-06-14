import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class BasicAnim(MarsRigComponent):
    def __init__(self, side, limb, anim = None, translate = False, rotate = False,connect_to = None, area = None, rig = None, node = None):
        if node != None: self.node = node
        else:
            if anim != None: self.node = self.exist_check('BasicAnim',anim,'anim')
            else: self.node = None
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'BasicAnim', side, limb, start = '', end = '')
            
            #Variables
            name = side + '_' + limb
            if anim == None: anim = pm.joint(n = name + '_anim',p = (0,0,0))
            anim_null = mu.stack_chain(anim,'_anim','_null')[0]
            mu.default_anim_shape([anim])
            
            #Group Setup
            component_grp = pm.group(n = name + '_component_grp',em = True)
            anim_grp = pm.group(anim_null,n = name + '_anim_grp',p = component_grp)
            grps = [component_grp,anim_grp]
            
            ##Lock Attributes
            lock = ['scale','visibility']
            if translate == False: lock += ['translate']
            if rotate == False: lock += ['rotate']
            mu.lock_and_hide_attrs(anim, lock)
            mu.lock_and_hide_attrs(anim_null,'all')
            mu.lock_and_hide_attrs(anim_grp,'all')
            pm.select(cl=True)
            
            ##Assign To Node
            mu.con_link(anim,self.node,'anims')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            
            ##Finish
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)