import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class EyeAimComponent(MarsRigComponent):
    def __init__(self, side, limb, eye_anims, main_anim = True, connect_to = None, area = None, rig = None, node = None, dist = 5.00):
        if node != None: self.node = node
        else: self.node = self.exist_check('EyeAimComponent',eye_anims[0],'eyes')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self, 'EyeAimComponent', side, limb, start = '', end = '')
            
            #Variables
            name = side + '_' + limb
            eye_anims = [pm.PyNode(x) for x in eye_anims]
            aim_anims = []
            locs = []
            for ea in eye_anims:
                suffix = 'center_anim'
                if 'right' in ea.name(): suffix = 'right_anim'
                elif 'left' in ea.name(): suffix = 'left_anim'
                aim_anims += mu.duplicate_chain(ea,name,suffix)
            
            mu.default_anim_shape(aim_anims,r = 0.25)
            anim_nulls = mu.stack_chain(aim_anims,'_anim','_null')
            aim_nulls = mu.stack_chain(eye_anims,'_anim','_aim_null')
            mu.lock_and_hide_attrs(aim_anims,['rotate','scale','v','radius'])
            nulls_to_parent = anim_nulls
            
            #Functions
            for i, anim in enumerate(aim_anims):
                loc = pm.spaceLocator(anim + '_wuo',p = (0,0,0))
                locs.append(loc)
                mu.aligner(loc,aim_nulls[i])
                loc.ty.set(abs(loc.ty.get() * 2.00))
                anim_nulls[i].tz.set(anim_nulls[i].tz.get() * dist)
                anim_nulls[i].jointOrient.set(0,0,0)
                pm.aimConstraint(anim,aim_nulls[i],mo=True,wut = 'object', wuo = loc.name(),u = (0,1,0),aim = (0,0,1))
            
            pm.select(cl = True)
            
            #Creating a main anim setup
            if main_anim == True:
                main_anim = pm.joint(n = name + '_main_anim',p = (0,0,0))
                main_anim.jointOrient.set(0,0,0)
                main_anim.rotate.set(0,0,0)
                main_null = mu.stack_chain(main_anim,'_anim','_null')[0]
                mu.align_between(main_null,anim_nulls,rotation = False)
                pm.parent(anim_nulls,main_anim)
                nulls_to_parent = main_null
                mu.default_anim_shape(main_anim)
                anim_nulls.append(main_null)
                aim_anims.append(main_anim)
                mu.lock_and_hide_attrs(main_anim,['scale','v','radius'])
                
            #Component Grp Organization
            pm.select(cl = True)
            component_grp = pm.group(n=(name + '_component_grp'))
            anim_grp = pm.group(nulls_to_parent,n = (name + '_anim_grp'),p = component_grp)
            hidden_grp = pm.group(locs,n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            pm.select(cl=True)

            #Connections
            mu.con_link(aim_anims,self.node,'anims')
            mu.con_link(eye_anims,self.node,'eyes')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            
            ##Finish
            if connect_to != None and area != None: self.connect_component_to(connect_to,area)
            if rig != None: rig.add_to_rig(self)
            self.finalize_anims()