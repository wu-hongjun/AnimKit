import pymel.all as pm
import MARS as mars
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class StackedComponent(MarsRigComponent):
    
    def __init__(self, side, limb, start, end, components = None,connect_to = None, area = None, rig = None, node = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('StackedComponent',start,'start')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'StackedComponent', side, limb, start = start, end = end)
            
            #Variables
            name = self.node.side.get() + '_' + self.node.limb.get()
            bones = mu.get_chain(start,end)
            mu.check_for_constraints(bones)
            controls = mu.duplicate_chain(bones,name,'control_joint')
            switch = self.switch_setup(name,components)
            component_grp, hidden_grp = self.component_group_setup(name,anim_grp = False)
            
            #Constraints
            constraints = self.stack_constraints(switch,bones,controls,components)
            
            #Set Driven Keys
            self.stack_sdks(switch,constraints)
            
            #Visibility
            self.stack_visibility(name,switch,components)
            
            #Parent
            pm.parent(switch,component_grp)
            pm.parent(controls[0],hidden_grp)
            
            ##Lock Attributes
            mu.lock_and_hide_attrs(switch,['translate','rotate','scale','v'])
            pm.select(cl=True)
            
            ##Assign To Node
            mu.con_link(bones,self.node,'bones')
            mu.con_link(switch,self.node,'switch')
            mu.con_link(controls,self.node,'control_joints')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            
    def switch_setup(self,name,components):
        switch = pm.group(n = name + '_switch',em = True)
        enum_string = ''
        for x in components: enum_string += pm.PyNode(x).name() + ':'
        switch.addAttr('type_switch',at = 'enum',en = enum_string,k = True)
        return switch
        
    def stack_constraints(self,switch,bones,controls,components):
        for i, b in enumerate(bones): pm.parentConstraint(controls[i],b,mo = True) 
        if components != None:
            for component in components:
                comp_controls = component.get_control_joints()
                for i, c in enumerate(controls): pm.parentConstraint(comp_controls[i],c,mo = True)
        constraints = [pm.listConnections(c,type = pm.nt.Constraint)[-1] for c in controls]
        return constraints
    
    def stack_sdks(self,switch,constraints):
        print constraints
        for con in constraints:
            ats = pm.listAttr(con,st = ['*jointW*'])
            for i, at in enumerate(ats):
                pm.setDrivenKeyframe(con.attr(at),cd = switch.type_switch,dv = i,v = 1)
                for x in ats:
                    if x != at: pm.setDrivenKeyframe(con.attr(x),cd = switch.type_switch,dv = i,v = 0)
    
    def stack_visibility(self,name,switch,components):
        for i, comp in enumerate(components):
            grp = comp.get_component_grp()
            pm.setDrivenKeyframe(grp.visibility,cd = switch.type_switch,dv = i,v = 1)
            for x in components:
                x_grp = x.get_component_grp()
                if x != comp: pm.setDrivenKeyframe(x_grp.visibility,cd = switch.type_switch,dv = i,v = 0)