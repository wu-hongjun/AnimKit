import pymel.all as pm
from MARS.MarsNode import MarsNode
import MARS.MarsUtilities as mu
reload(mu)

class MarsRigComponent(MarsNode):
    def __init__(self, node_type, side, limb, start = '', end = '', connect_to = None):
       #Run Function
       name = side + '_' + limb 
       MarsNode.__init__(self,name,node_type)
       
       #Global Scale
       self.node.addAttr('global_scale',at='double',min=0,dv=1)
       
       #Assign To Node
       mu.con_link(side,self.node,'side')
       mu.con_link(limb,self.node,'limb')
       if start != '': mu.con_link(start,self.node,'start')
       if end != '': mu.con_link(end,self.node,'end')
    
    def finalize_anims(self):
        side = self.node.side.get()
        limb = self.node.limb.get()
        anims = pm.listConnections(self.node.anims)
        s = 0
        if side == 'left': s = 1
        elif side == 'right': s = 2
        for i, anim in enumerate(anims):
            anim.setAttr('side',s)
            anim.setAttr('type',18)
            anim.setAttr('otherType', limb, type = 'string')
            anim.addAttr('number', at = 'byte',dv = (i + 1))
            anim.setAttr('side',lock = True)
            anim.setAttr('type',lock = True)
            anim.setAttr('otherType',lock = True)
            anim.number.lock()
    
    def get_bind_joints(self):
        if self.node.hasAttr('bones'): return pm.listConnections(self.node.bones)
        
    def get_IK_anims(self):
        if self.node.hasAttr('IK_anims'): return pm.listConnections(self.node.IK_anims)
    
    def get_FK_anims(self):
        if self.node.hasAttr('FK_anims'): return pm.listConnections(self.node.FK_anims)
        
    def get_IK_joints(self):
        if self.node.hasAttr('IK_joints'): return pm.listConnections(self.node.IK_joints)
    
    def get_all_anims(self):
        anims = []
        if self.node.hasAttr('switch'): anims += pm.listConnections(self.node.switch)
        if self.node.hasAttr('anims'): anims += pm.listConnections(self.node.anims)
        return anims
        
    def get_anim_grp(self):
        if self.node.hasAttr('anim_grp'): return pm.listConnections(self.node.anim_grp)[0]
    
    def get_hierarchy_anims(self):
        components = [self.node]
        anims = []
        for component in components:
            if component.hasAttr('child_nodes'): components += pm.listConnections(component.child_nodes)
        for component in components:
            anims += pm.listConnections(component.anims)
            if component.hasAttr('switch'): anims += pm.listConnections(component.switch)
        return anims
    
    def default_pose(self):
        for anim in self.get_all_anims(): mu.set_to_default_pose(anim)
    
    def hierarchy_default_pose(self):
        for anim in self.get_hierarchy_anims(): mu.set_to_default_pose(anim)
    
    def mirror(self):
        mu.mirror_selection(self.get_all_anims())
        
    def mirror_hierarchy(self):
        mu.mirror_selection(self.get_hierarchy_anims())
    
    def select_all_anims(self):
        pm.select(self.get_all_anims(),add = True)
        
    def select_hierarchy_anims(self):
        pm.select(self.get_hierarchy_anims(),add = True)
    
    def key_anim(self,anim):
        for attr in anim.listAttr(w=True,u=True,v=True,k=True):
            attribute = attr.split('.')[-1]
            pm.setKeyframe(anim,at = attribute)
    
    def key_all_anims(self):
        anims = self.get_all_anims()
        for anim in anims: self.key_anim(anim)
        
    def key_hierarchy(self):
        anims = self.get_hierarchy_anims()
        for anim in anims: self.key_anim(anim)
    
    def get_hidden_grp(self):
        if self.node.hasAttr('hidden_grp'): return pm.listConnections(self.node.hidden_grp)[0]
        
    def get_component_grp(self):
        if self.node.hasAttr('component_grp'): return pm.listConnections(self.node.component_grp)[0]
    
    def get_control_joints(self):
        if self.node.hasAttr('control_joints'): return pm.listConnections(self.node.control_joints)
    
    def component_grp_setup(self,name,start):
        pm.select(cl = True)
        component_grp = pm.group(n = name + '_component_grp',em = True)
        anim_grp = pm.group(n = name + '_anim_grp',em = True, p = component_grp)
        hidden_grp = pm.group(n = 'DO_NOT_TOUCH', em = True, p = component_grp)
        hidden_grp.v.set(0)
        grps = [component_grp,hidden_grp,anim_grp]
        mu.aligner(grps,start,position = False,rotation = False,pivot = True)
        pm.select(cl = True)
        return grps
    
    def connect_component_to(self,parent_node,area):
        parent_node = pm.PyNode(parent_node)
        bones = pm.listConnections(parent_node.bones)
        if area == 'start': num = 0
        elif area == 'end': num = -1
        else: num = bones.index(area)
        ctrl_jnt = pm.listConnections(parent_node.control_joints)[num]
        
        comp_grp = pm.listConnections(self.node.component_grp)[0]
        [comp_grp.attr('translate' + x).unlock() for x in ['X','Y','Z']]
        [comp_grp.attr('rotate' + x).unlock() for x in ['X','Y','Z']]
        pm.parentConstraint(ctrl_jnt, comp_grp, mo = True)
        mu.lock_and_hide_attrs(comp_grp,['translate','rotate','scale'])
        
        #Link
        mu.con_link(self.node,parent_node,'child_nodes')