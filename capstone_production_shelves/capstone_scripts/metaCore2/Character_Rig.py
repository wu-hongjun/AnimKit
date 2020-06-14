from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Character_Rig(Network_Node):
    def __init__(self, character_name, root):
        exists = False

        root = PyNode(root)
        if root.hasAttr('connected_to') and len(listConnections(root.connected_to)) > 0:
            for node in listConnections(root.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Character_Rig':
                    if listConnections(node.root)[0] == root:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            network = character_name.title() + '_Character_Rig'
            Network_Node.__init__(self,'Character_Rig',character_name = character_name,root = root)
            self.network = network
            
            self.topCon = joint(n=(character_name + '_topCon'),p=(0,0,0))
            self.topCon.drawStyle.set(2)
            self.topCon.addAttr('animNode', at = 'message')
            
            mesh_grp = group(n='mesh_grp',em=True)
            mesh_grp.inheritsTransform.set(0)
            bind_joint_grp = group(n = 'bind_joint_grp',em=True)
            component_grp = group(n='component_grp',em=True)
            
            if not PyNode(root).getParent():
                parent(root,bind_joint_grp)
            parent(mesh_grp,bind_joint_grp,component_grp,self.topCon)
            
            self.topCon.addAttr('global_scale',at='double',min=0,dv=1,k=True)
            self.topCon.global_scale >> PyNode(self.network).global_scale
            
            mesh_grp.inheritsTransform.set(0)
            bind_joint_grp.visibility.set(0)
            
            for s in ['sx','sy','sz']:
                self.topCon.setAttr(s,k=False,cb=False)
                self.topCon.global_scale >> self.topCon.attr(s)
            
            lock_and_hide_attrs([self.topCon],['radius'])
            select(cl=True)
            
            #Connections
            connect_objs_to_node([self.topCon],self.network,'topCon')
            connect_objs_to_node([mesh_grp],self.network,'mesh_grp')
            connect_objs_to_node([bind_joint_grp],self.network,'bind_joint_grp')
            connect_objs_to_node([component_grp],self.network,'component_grp')

    def get_topCon(self):
        return listConnections(PyNode(self.network).topCon)[0]
    
    def connect_rigs(self,node,bone = None):
        node = PyNode(node)
        network = self.network
        
        topCon = self.get_topCon()
        node_topCon = listConnections(node.topCon)[0]
        
        parent(topCon,node_topCon)
        node_topCon.global_scale >> topCon.global_scale
        connect_objs_to_node([network],node,'connected_rigs')
        
        if bone:
            parentConstraint(bone,topCon,mo=True)
            
        lock_and_hide_attrs([topCon],['tx','ty','tz','rx','ry','rz','global_scale'])

    def add_to_rig(self,node):
        node = PyNode(node)
        network = PyNode(self.network)
        type = node.network_type.get()
        topCon = self.get_topCon()
        if type.startswith('FKIK') == True:
            if type not in ['FKIK_Spline_Chain','FKIK_Ribbon_Chain']:
                IK_grp = PyNode(node.side.get() + '_' + node.limb.get() + '_IK_anim_grp')
                IK_grp.tx.unlock()
                IK_grp.ty.unlock()
                IK_grp.tz.unlock()
                IK_grp.rx.unlock()
                IK_grp.ry.unlock()
                IK_grp.rz.unlock()
                parentConstraint(topCon,IK_grp,mo=True)
        
        rig_comp_grp = listConnections(network.component_grp)[0]
        bind_joint_grp = listConnections(network.bind_joint_grp)[0]
        
        if node.hasAttr('start'):
            node_start = listConnections(node.start)[0]
            if node_start.getParent() == None:
                parent(node_start,bind_joint_grp)
        
        if node.hasAttr('component_grp'):
            node_comp_grp = listConnections(node.component_grp)[0]
            parent(node_comp_grp, rig_comp_grp)
        select(cl=True)
        
        v = len(listConnections(network.connected_networks))
        network.global_scale >> node.global_scale
        node.rig >> network.connected_networks[v]
        
    def get_all_anims(self):
        network = PyNode(self.network)
        anim_list = []
        if network.hasAttr('connected_networks'):
            nodes = listConnections(network.connected_networks)
            for node in nodes:
                if node.hasAttr('anims'):
                    anim_list += listConnections(node.anims)
                if node.hasAttr('switch'):
                    anim_list += listConnections(node.switch)
        return anim_list
    
    def get_switch(self):
        network = PyNode(self.network)
        switch_list = []
        if network.hasAttr('connected_networks'):
            nodes = listConnections(network.connected_networks)
            for node in nodes:
                if node.hasAttr('switch'):
                    switch = listConnections(node.switch)[0]
                    switch_list.append(switch)
        return switch_list
                    
    def default_pose(self):
        self.rig_default_pose()
    
    def get_meshes(self):
        network = PyNode(self.network)
        mesh_grps = [self.get_mesh_grp()]
        meshes = []
        geo = []
        if network.hasAttr('connected_rigs'):
            for rig in listConnections(network.connected_rigs):
                mesh_grps += listConnections(rig.mesh_grp)
        for grp in mesh_grps:
            meshes += listRelatives(grp,ad = True)
        for mesh in meshes:
            if listRelatives(mesh,s = True): geo.append(mesh)
        return geo

    def get_mesh_grp(self):
        network = PyNode(self.network)
        if network.hasAttr('mesh_grp'):
            mesh_grp = listConnections(network.mesh_grp)[0]
            return mesh_grp
        else:
            print 'No mesh grp'
            

    def get_all_bind_joints(self):
        network = PyNode(self.network)
        bones = [listConnections(network.root)[0]]
        for bone in listRelatives(listConnections(network.root)[0],ad = True):
            if bone.nodeType() == 'joint': bones.append(bone)
        return bones

    def get_bind_joint_grp(self):
        network = PyNode(self.network)
        if network.hasAttr('bind_joint_grp'):
            bind_joint_grp = listConnections(network.bind_joint_grp)[0]
            return bind_joint_grp
        else: print 'No bind joint grp'

    def topCon_shape(self,r=5.00):
        main = circle(nr = (0,1,0),r=r)
        circle_parts = detachCurve(main,p=(0.325,1.675,2.325,3.675,4.325,5.675,6.325,7.675))
        parts = circle_parts[::2]
        delete(circle_parts[1::2],main)
        topCon = self.get_topCon()
        for i in range(1,5):
            shape = curve(d = 1,
                          p = [((0.9 * r),0,(0.25 * r)),
                               ((1.5 * r),0,(0.25 * r)),
                               ((1.5 * r),0,(0.5 * r)),
                               ((2.00 * r),0,0),
                               ((1.5 * r),0,-(0.5 * r)),
                               ((1.5 * r),0,-(0.25 * r)),
                               ((0.9 * r),0,-(0.25 * r))],
                           k = (0,1,2,3,4,5,6));
            shape.ry.set(90 * (i - 1))
            pieces = detachCurve(shape,p=(0.110,5.890))
            parts.append(PyNode(pieces[1]))
            delete(shape,pieces[::2])
        finished = attachCurve(parts,ch=False,rpo=True)[0]
        finished_shape = finished.getChildren(s=True)
        finished_shape[0].rename('topCon_shape')
        
        parent(finished_shape,topCon,r=True,s=True)
        
        delete(parts[1:],finished)
        select(cl=True)
    
    def get_all_rig_anims(self):
        network = PyNode(self.network)
        anims = []
        connected_nodes = listConnections(network.connected_networks)
        for node in connected_nodes:
            if node.hasAttr('anims'):
                anims += listConnections(node.anims)
            if node.hasAttr('switch'):
                anims += listConnections(node.switch)
        return anims

    def get_complete_rig_anims(self):
        network = PyNode(self.network)
        anims = []
        rigs = []
        anims += self.get_all_rig_anims()
        if network.hasAttr('connected_rigs'):
            rigs += listConnections(network.connected_rigs)
        if network.hasAttr('connected_to'):
            rigs += listConnections(network.connected_to)
        for rig in rigs:
            root = listConnections(rig.root)[0]
            component = Character_Rig('',root.name())
            anims += component.get_all_rig_anims()
        return anims

    def rig_default_pose(self):
        network = PyNode(self.network)
        anims = self.get_all_rig_anims()
        for anim in anims:
            anim_default_pose(anim)
        #anim_default_pose(self.get_topCon())
        
    def complete_rig_default_pose(self):
        network = PyNode(self.network)
        self.rig_default_pose()
        rigs = []
        if network.hasAttr('connected_rigs'):
            rigs += listConnections(network.connected_rigs)
        if network.hasAttr('connected_to'):
            rigs += listConnections(network.connected_to)
        for rig in rigs:
            root = listConnections(rig.root)[0]
            component = Character_Rig('',root.name())
            component.rig_default_pose()

    def select_rig_anims(self):
        network = PyNode(self.network)
        anims = self.get_all_anims()
        select(anims, add = True)
        
    def select_complete_rig_anims(self):
        network = PyNode(self.network)
        anims = self.get_all_anims()
        rigs = []
        if network.hasAttr('connected_rigs'):
            rigs += listConnections(network.connected_rigs)
        if network.hasAttr('connected_to'):
            rigs += listConnections(network.connected_to)
        for rig in rigs:
            name = rig.character_name.get()
            root = listConnections(rig.root)[0]
            component = Character_Rig(name,root)
            anims += component.get_all_anims()
        select(anims, add = True)

    def get_complete_rig_components(self):
        network = PyNode(self.network)
        components = []
        rigs = []
        if network.hasAttr('connected_rigs'):
            rigs += listConnections(network.connected_rigs)
        if network.hasAttr('connected_to'):
            rigs += listConnections(network.connected_to)
        for rig in rigs:
            components += listConnections(rig.connected_networks)
        return components
    
    def key_all_rig_anims(self):
        anims = self.get_all_rig_anims()
        for anim in anims:
            for attr in anim.listAttr(w=True,u=True,v=True,k=True):
                attribute = attr.split('.')[-1]
                setKeyframe(anim,at = attribute)
    
    def key_complete_rig_anims(self):
        network = PyNode(self.network)
        rigs = [network]
        if network.hasAttr('connected_rigs'):
            rigs += listConnections(network.connected_rigs)
        if network.hasAttr('connected_to'):
            rigs += listConnections(network.connected_to)
        for rig in rigs:
            name = rig.character_name.get()
            root = listConnections(rig.root)[0]
            component = Character_Rig(name,root)
            component.key_all_rig_anims()
    
    def add_anim_visibility_attr(self,attribute,anims,dv = 1):
        topCon = self.get_topCon()
        if topCon.hasAttr(attribute) == False:
            topCon.addAttr(attribute,at='double',min=0,max=1,dv=dv,k=True)
            
        for anim in anims:
            shapes = PyNode(anim).getChildren(s=True)
            for shape in shapes:
                shape.visibility.set(1)
            obj = anim.getParent()
            vis_null = group(n = (anim + '_vis_null'),em = True)
            parent(vis_null,obj)
            vis_null.translate.set(0,0,0)
            vis_null.rotate.set(0,0,0)
            attrs = listAttr(anim,l = True)
            for at in attrs:
                anim.attr(at).unlock()
            parent(anim,vis_null)
            for at in attrs:
                anim.attr(at).lock()
            topCon.attr(attribute) >> vis_null.visibility
            lock_and_hide_attrs([vis_null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility'])
        select(cl=True)

    def finalize_rig(self):
        network = PyNode(self.network)
        nodes = listConnections(network.connected_networks)
        mesh_grps = listConnections(network.mesh_grp)

        if network.hasAttr('connected_rigs'):
            for rig in listConnections(network.connected_rigs):
                nodes += listConnections(rig.connected_networks)
                mesh_grps += listConnections(rig.mesh_grp)
        
        redo_nulls = []
        redo_cons = []
        
        for node in nodes:
            if node.network_type.get() == 'Multi_Constraint':
                if node.side.get() == 'left':
                    influences = listConnections(node.influences)
                    nulls = listConnections(node.influence_nulls)
                    for i in range(0,len(nulls)):
                        if influences[i].startswith('left'):
                            delete(nulls[i].getChildren()[0])
                            redo_nulls.append(nulls[i])
                            redo_cons.append(influences[i])
        
        for node in nodes:
            if 'FKIK' in node.name():
                IK_anims = listConnections(node.IK_anims)
                IK_aligners = listConnections(node.IK_aligners)
                FK_anims = listConnections(node.FK_anims)
                for i in range(len(IK_anims)):
                    null = IK_anims[i].getParent()
                    delete(IK_aligners[i] + '_parentConstraint1')
                    parent(IK_aligners[i],null)
                    aligner([IK_aligners[i]],FK_anims[i + 1])
                    parentConstraint(FK_anims[i + 1],IK_aligners[i],mo = True)
                    if node.side.get() == 'left':
                        null.sx.unlock()
                        null.sy.unlock()
                        null.sz.unlock()
                        null.scale.set(-1,-1,-1)
                        lock_and_hide_attrs([null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility'])
            if 'Face_Component' in node.name():
                anims = listConnections(node.anims)
                for anim in anims:
                    null = anim.getParent()
                    if node.side.get() == 'left':
                        null.sx.unlock()
                        null.sy.unlock()
                        null.sz.unlock()
                        null.scale.set(-1,-1,-1)
                        lock_and_hide_attrs([null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility'])
            if '_FK_Chain' in node.name() and node.translate.get() == True:
                anims = listConnections(node.anims)
                for anim in anims:
                    null = anim.getParent()
                    if node.side.get() == 'left':
                        null.sx.unlock()
                        null.sy.unlock()
                        null.sz.unlock()
                        null.scale.set(-1,-1,-1)
                        lock_and_hide_attrs([null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','visibility'])
        
        for j in range(0,len(redo_cons)): parentConstraint(redo_cons[j],redo_nulls[j],mo = True)
        
        self.complete_rig_default_pose()
        geo_lyr = createDisplayLayer(mesh_grps, n = 'geo_lyr', nr = True);
        geo_lyr.displayType.set(2)
        select(cl=True)