import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class RollBoneChain(MarsRigComponent):
    def __init__(self, side, limb, driver, end, roll_bones, rig = None, node = None):
        if node != None: self.node = node
        else:
            if isinstance(roll_bones,str): roll_bones = [pm.PyNode(roll_bones)]
            self.node = self.exist_check('RollBoneChain',roll_bones[0],'bones')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'RollBoneChain', side, limb, start = driver, end = end)
            
            #Variables
            name = side + '_' + limb
            driver = pm.PyNode(driver)
            end = pm.PyNode(end)
            bones = [driver, end]
            chain = [driver, end]
            reverse = True
            if driver.getParent() == end:
                chain.reverse()
                reverse = False
                roll_bones.reverse()
            
            #Setup
            twist = mu.duplicate_chain(bones,name,'control_joint',reverse = True)
            twist_null = pm.group(n=(name+'_twist_null'),em=True)
            mu.aligner(twist_null,driver)
            pm.parent(twist[0],twist_null)
            twist_IK, twist_ef = pm.ikHandle(n=(name + '_twist_IK'),sol='ikSCsolver',sj=twist[0],ee=twist[1],ccv=False,pcv=False)
            
            stretch_md = mu.create_node('multiplyDivide')
            chain[1].tx >> stretch_md.input1X
            stretch_md.input2X.set(chain[1].tx.get())
            stretch_md.operation.set(2)
        
            if reverse == True:
                pm.parentConstraint(bones[0].getParent(), twist_IK, mo=True)
                pm.parentConstraint(bones[0], twist_null, mo=True)
            else:
                pm.parentConstraint(bones[0], twist_IK, mo=True)
                pm.parentConstraint(bones[1], twist_null, mo=True)
        
            for roll_bone in roll_bones:
                md = mu.create_node('multiplyDivide')
                distance_md = mu.create_node('multiplyDivide')
                value = float(roll_bone.tx.get()/chain[1].tx.get())
                twist[0].rx >> md.input1X
                md.outputX >> roll_bone.rx
                if reverse == True: md.input2X.set(1.00 - value)
                else: md.input2X.set(value)
            
                stretch_md.outputX >> distance_md.input2X
                distance_md.input1X.set(roll_bone.tx.get())
                distance_md.outputX >> roll_bone.tx
            
            #Component Grp Organization
            component_grp = pm.group(n=(name + '_component_grp'),em = True)
            hidden_grp = pm.group(twist_null,twist_IK,n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            pm.select(cl=True)
            
            ##Assign To Node
            mu.con_link(roll_bones,self.node,'bones')
            mu.con_link(twist,self.node,'control_joints')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')

            #Finalize
            if rig != None: rig.add_to_rig(self)