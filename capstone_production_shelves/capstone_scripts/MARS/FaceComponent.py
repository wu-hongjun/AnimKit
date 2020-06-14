import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class FaceComponent(MarsRigComponent):
    def __init__(self, side, limb, bones, connect_to = None, area = None, rig = None, node = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('FaceComponent',bones[0],'bones')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'FaceComponent', side, limb, start = '', end = '')
            
            #Variables
            name = side + '_' + limb
            if isinstance(bones,str): bones = [bones]
            bones = [pm.PyNode(x) for x in bones]
            controls = mu.duplicate_chain(bones,name,'control_joint',separate = True)
            anims, nulls = mu.create_anims(bones,name,suffix = 'anim',separate = True,end = False)
            if len(bones) == 1:
                nulls.rename(nulls.replace('1_',''))
                anims.rename(anims.replace('1_',''))
                anims = [anims]
                nulls = [nulls]
            
            for i, bone in enumerate(bones):
                pm.parentConstraint(anims[i],controls[i],mo = True)
                pm.parentConstraint(controls[i],bone)
            
            mu.lock_and_hide_attrs(anims,['scale','v','radius'])
            mu.lock_and_hide_attrs(nulls,['translate','rotate','scale','v','radius'])

            #Group Setup
            component_grp = pm.group(n = name + '_component_grp',em = True)
            anim_grp = pm.group(nulls,n = name + '_anim_grp',p = component_grp)
            hidden_grp = pm.group(controls,n = 'DO_NOT_TOUCH',p = component_grp)
            hidden_grp.v.set(0)

            ##Assign To Node
            mu.con_link(bones,self.node,'bones')
            mu.con_link(anims,self.node,'anims')
            mu.con_link(controls,self.node,'control_jnts')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            mu.con_link(anim_grp,self.node,'anim_grp')
            
            ##Finish
            self.finalize_anims()
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)