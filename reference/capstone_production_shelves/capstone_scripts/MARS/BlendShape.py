import pymel.all as pm
import MARS.MarsUtilities as mu
from MARS.MarsRigComponent import MarsRigComponent
reload(mu)

class BlendShape(MarsRigComponent):
    def __init__(self, side, limb, mesh, blend_meshes = None, blend_node = None,anim = None, attributes = None,mins = None,maxs = None,dvs = None,rig = None,node = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('BlendShape',mesh,'mesh')
        
        if self.node == None:
            MarsRigComponent.__init__(self,'BlendShape', side, limb, start = '', end = '')
            
            #Variables
            name = side + '_' + limb
            if blend_meshes != None and blend_node == None:
                if isinstance(blend_meshes,str): blend_meshes = [blend_meshes]
                targets = blend_meshes
                targets.append(mesh)
                blend_node = pm.blendShape(targets,n = (mesh + '_blend'),frontOfChain = True,o = 'local')[0]
            component_grp = self.component_group_setup(name, hidden_grp = False,anim_grp = False)[0]
        
            ##Anim##
            if anim != None:
                anim = pm.joint(n=(name + '_blend_anim'),p=(0,0,0))
                pm.parent(anim,component_grp)
                mu.lock_and_hide_attrs(anim,'all')
                mu.con_link(anim,self.node,'anim')
            else: anim = pm.PyNode(anim)
            
            #Attributes
            if attributes != None:
                for i, at in enuemrate(attributes):
                    attribute = anim + '.' + attrs
                    if mins != None: pm.addAttr(attribute,e=True,min = mins[i])
                    if maxs != None: pm.addAttr(attribute,e=True,max = maxs[i])
                    if dvs != None:
                        pm.addAttr(attribute,e=True,dv = dvs[i])
                        anim.attr(attrs).set(dvs[i])
                    else:
                        try: v = 0
                        except: v = mins[i]
                        pm.addAttr(attribute,e=True,dv = v)
                        anim.attr(attrs).set(v)
            else:
                for target in targets[:-1]:
                    anim.addAttr(target,min = 0, max = 1, dv = 0, k=True)
                    anim.attr(target) >> blend_node.attr(target)
    
            #Connections
            mu.con_link(anim,self.node,'blend_anim')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(mesh,self.node,'mesh')
            mu.con_link(blend_node,self.node,'blend_node')

    def connect_components(self,component,connection): pass