import pymel.all as pm
import MARS.MarsUtilities as mu
reload(mu)

class MarsNode():
    def __init__(self,name,type):
        if name != '': node_name = name + '_' + type
        else: node_name = type
        
        self.node = pm.createNode('network',n=node_name)
        self.node.setAttr('node_type',type,f = True)
        self.node.setAttr('version','MARS',f = True)
        self.node.node_type.lock()
        self.node.version.lock()
        
    def __str__(self):
        return self.node.name()
        
    def __repr__(self):
        return pm.PyNode(self.__str__())
        
    def exist_check(self,type,obj,attribute):
        current_node = None
        obj = pm.PyNode(obj)
        if obj.hasAttr('connected_to'):
            for node in pm.listConnections(obj.connected_to):
                if node.node_type.get() == type:
                    if pm.listConnections(node.name() + '.' + attribute)[0] == obj:
                        current_node = node
                        break
        return current_node
        
    def component_group_setup(self, name, hidden_grp = True, anim_grp = True, other_grps = None):
        items = []
        comp_grp = pm.group(n = name + '_component_grp', em = True)
        items.append(comp_grp)
    
        if hidden_grp == True:
            hidden_grp = pm.group(n = 'DO_NOT_TOUCH', em = True, p = comp_grp)
            items.append(hidden_grp)
            hidden_grp.v.set(0)
        if anim_grp == True:
            anim_grp = pm.group(n = 'anim_grp', em = True, p = comp_grp)
            items.append(anim_grp)
        if other_grps != None:
            others = []
            for og in other_grps:
                grp = pm.group(n = og + '_grp', em = True, p = comp_grp)
                others.append(grp)
            items.append(others)
        return items