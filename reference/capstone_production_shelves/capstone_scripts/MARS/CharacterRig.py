import pymel.all as pm
from MARS.MarsNode import MarsNode
import MARS.MarsUtilities as mu
reload(mu)

class CharacterRig(MarsNode):
    '''
    MANDATORY VARIABLES
        character_name = The name of the character itself written as a string.
        root = Provide a string of the starting joint of the CharacterRig hierarchy.
               Note: if root joint not at (0,0,0), it will create a new root joint at that position for VR.
        
    OPTIONAL VARIABLES
        tcr = Top Con Radius. Creates a topCon anim and sized when written as a float or int.
              Default value 0 does not create a TopCon
        
    SPECIALTY VARIABLES
        node = used for the Marking Menu. Used for reacquiring the class functionality.
    '''
    def __init__(self,character_name,root,tcr = 0,node = None):
        self.node = None
        if node != None: self.node = node
        else: self.node = self.exist_check('CharacterRig',root,'root')
        
        if self.node == None:
            #Run Function
            MarsNode.__init__(self,character_name,'CharacterRig')
            
            #Variables
            self.root = pm.PyNode(root)
            
            #Setup
            topCon = pm.joint(n = character_name + '_topCon', p = (0,0,0))
            topCon.addAttr('global_scale',at = 'double',dv = 1,min = 0.00001,k = True)
            topCon.drawStyle.set(2)
            for at in ['sx','sy','sz']: topCon.global_scale >> topCon.attr(at)
            mu.lock_and_hide_attrs(topCon,['scale','radius'])
            self.node.addAttr('global_scale',at='double',min=0,dv=1)
            topCon.global_scale >> self.node.global_scale
            
            #Group Setup
            component_grp = pm.group(n = 'component_grp',em = True,p = topCon)
            bind_joint_grp = pm.group(n = 'bind_joint_grp',p = topCon,em = True)
            mesh_grp = pm.group(n = 'mesh_grp',em = True, p =topCon)
            mu.lock_and_hide_attrs([bind_joint_grp,component_grp,mesh_grp],['translate','rotate','scale'])
            bind_joint_grp.v.set(0)
            mesh_grp.inheritsTransform.set(0)
            mesh_grp.overrideEnabled.set(1)
            bind_joint_grp.overrideEnabled.set(1)
            bind_joint_grp.overrideDisplayType.set(2)
            
            #Root at (0,0,0)
            if self.root.getParent() == None:
                old_root = self.root
                self.root = pm.joint(n = character_name + '_root_bind_joint',p = (0,0,0),rad = old_root.radius.get())
                pm.parent(old_root,self.root)
                pm.parent(self.root,bind_joint_grp)

            #Attrs
            self.node.addAttr('rig_components',dt = 'string',m=True)
            mu.bone_labeling(pm.listRelatives(root,ad = True))
            
            #Setup
            mu.con_link(character_name,self.node,'character_name')
            mu.con_link(topCon,self.node,'topCon')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(mesh_grp,self.node,'mesh_grp')
            mu.con_link(bind_joint_grp,self.node,'bind_joint_grp')
            mu.con_link(self.root,self.node,'root')
            
            #topCon Finalize
            topCon.addAttr('mesh_display',at='enum',en = 'normal:template:reference:',dv = 2,k = True)
            topCon.addAttr('bind_joint_display',at='bool',dv = 0, k = True)
            topCon.mesh_display >> mesh_grp.overrideDisplayType
            topCon.bind_joint_display >> bind_joint_grp.visibility
            if tcr > 0: self.topCon_shape(r = tcr)
    
    def center_of_mass(self,root,chest = None, pelvis = None, head = None, feet = None, hands = None, r = 1.00):
        #Variables
        items = []
        data = []
    
        #Variable Data Collection
        if chest != None:
            items.append(chest)
            data.append(0.37)
        if pelvis != None:
            items.append(pelvis)
            data.append(0.25)
        if head != None:
            items.append(head)
            data.append(0.08)
        if feet != None:
            if not isinstance(feet,list): feet = [feet]
            for f in feet:
                items.append(f)
                data.append(0.08)
        if hands != None:
            if not isinstance(hands,list): hands = [hands]
            for h in hands:
                items.append(h)
                data.append(0.07)
            
        items = [pm.PyNode(item) for item in items]
    
        #Setup
        center_of_mass = pm.circle(n = self.node.character_name.get() + '_center_of_mass',r = r,nr = (0,1,0),ch = False)[0]
        topCon = self.get_topCon()
        topCon.addAttr('show_center_of_mass',at = 'bool',dv = 0,k = True)
        mu.con_link(center_of_mass,self.node,'center_of_mass')
        mu.aligner(center_of_mass,root,rotation = False)
        center_of_mass.ty.set(0)
        pm.parent(center_of_mass,topCon)
        con = pm.pointConstraint(items,center_of_mass,sk='y')
        for i, item in enumerate(items): con.attr('{0}W{1}'.format(item,i)).set(data[i])
        topCon.show_center_of_mass >> center_of_mass.visibility
    
    def proxy_rig_setup(self,meshes):
        #Variables
        topCon = self.get_topCon()
        pm.select(cl = True)
        proxy_grp = pm.group(n = 'proxy_rig_grp',em = True,p = topCon)
        
        #Setup
        pm.parent(proxy_grp,topCon)
        pm.parent(meshes,proxy_grp)
        
        #Setup
        topCon.addAttr('proxy_geo',at = 'bool', dv = 0, k = True)
        rev = mu.create_node('reverse', n = 'proxy_rev')
        topCon.proxy_geo >> proxy_grp.visibility
        topCon.proxy_geo >> rev.inputX
        rev.outputX >> self.get_mesh_grp().visibility
        proxy_grp.overrideEnabled.set(1)
        topCon.mesh_display >> proxy_grp.overrideDisplayType
        
        mu.con_link(proxy_grp,self.node,'proxy_grp')
    
    def add_to_rig(self,child_node):
        child_node = pm.PyNode(child_node)
        child_node.addAttr('rig',at = 'message')
        num = len(pm.listConnections(self.node.rig_components))
        child_node.rig >> self.node.attr('rig_components[' + str(num) + ']')
        child_grp = pm.listConnections(child_node.component_grp)[0]
        comp_grp = pm.listConnections(self.node.component_grp)[0]
        self.get_topCon().global_scale >> child_node.global_scale
        
        pm.parent(child_grp,comp_grp)
        pm.select(cl = True)
        
    def connect_rigs(self,rig,bone = None):
        topCon = self.get_topCon()
        node_topCon = rig.get_topCon()
        
        pm.parent(topCon,node_topCon)
        node_topCon.global_scale >> topCon.global_scale
        node_topCon.mesh_display >> topCon.mesh_display
        mu.con_link(self.node, pm.PyNode(rig), 'connected_rigs')
        
        if bone != None:
            for at in ['X','Y','Z']:
                topCon.attr('translate' + at).unlock()
                topCon.attr('rotate' + at).unlock()
            pm.parentConstraint(bone,topCon,mo=False)
        mu.lock_and_hide_attrs(topCon,['global_scale','mesh_display'])
    
    def get_proxy_grp(self):
        if self.node.hasAttr('proxy_grp'): return pm.listConnections(self.node.proxy_grp)[0]
    
    def get_topCon(self):
        return pm.listConnections(self.node.topCon)[0]
    
    def get_mesh_grp(self):
        return pm.listConnections(self.node.mesh_grp)[0]
        
    def get_bind_joint_grp(self):
        return pm.listConnections(self.node.bind_joint_grp)[0]
    
    def get_rig_components(self):
        return pm.listConnections(self.node.rig_components)
    
    def get_complete_rig_components(self):
        components = []
        root = self.get_root_rig()
        if root == None: rigs = [self.node]
        else: rigs = [root]
        if self.node.hasAttr('connected_rigs'): rigs += pm.listConnections(rigs[0].connected_rigs)
        for rig in rigs:
            mars_rig = CharacterRig('','',node = rig)
            components += mars_rig.get_rig_components() 
        return components
    
    def finalize(self):
        #Delete MultiCon Mirrored Anim Influences
        multicons = [x for x in pm.ls(type = pm.nt.Network) if x.node_type.get() == 'MultiConstraint']
        influences_to_fix = []
        multicon_anim_fix = []
        for m in multicons: 
            for x in pm.listConnections(m.influence_nulls):
                anim = pm.PyNode(x.replace(x.name().split('_')[0] + '_','').replace('_null',''))
                if 'left' in x.name() and pm.getAttr(anim.translateX,l = True) == False:
                    influences_to_fix += [x]
                    multicon_anim_fix += [anim]
        for x in influences_to_fix: pm.delete(pm.listConnections(x, t = pm.nt.ParentConstraint))
        
        #Mirror Anims
        components = self.get_complete_rig_components()
        for component in components:
            anims = []
            foot_null = None
            prime_IK_anim = None
            comp_type = component.node_type.get()
            #Snaps
            if 'FKIK' in comp_type:
                snaps = pm.listConnections(component.IK_snaps)
                if comp_type in ['FKIKArm','FKIKBipedLeg','FKIKQuadLeg','FKIKBendyArm','FKIKBendyBipedLeg']:
                    for i, anim in enumerate(pm.listConnections(component.IK_anims)):
                        pm.parent(snaps[i].getParent(),anim.getParent())
                        mu.aligner([snaps[i]],anim)
                else:
                    if component.side.get() == 'left':
                        for snap in snaps:
                            for x in ['X','Y','Z']:
                                snap.getParent().attr('scale' + x).unlock()
                                snap.getParent().attr('scale' + x).set(-1)
                                snap.getParent().attr('scale' + x).lock()
            
            quad_null = None
            if component.side.get() == 'left':
                if comp_type == 'FKChain' and component.translate.get() == True: anims += pm.listConnections(component.anims)
                elif comp_type == 'FaceComponent' or 'FKIK' in comp_type:
                    if comp_type == 'FaceComponent': anims += pm.listConnections(component.anims)
                    else:
                        anims += pm.listConnections(component.IK_anims)
                        if component.hasAttr('bendy_anims'): anims += pm.listConnections(component.bendy_anims)
                    if comp_type in ['FKIKBipedLeg','FKIKBendyBipedLeg','FKIKQuadLeg']:
                        foot_null = pm.listConnections(component.foot_null)[0]
                        prime_IK_anim = pm.listConnections(component.IK_anims)[-1]
                        pm.parent(foot_null,w = True)
                        
                for anim in anims: mu.mirror_object(anim.getParent())
                if prime_IK_anim != None and foot_null != None: pm.parent(foot_null,prime_IK_anim)
                
        #Fix MultiConstraints
        for i, inf in enumerate(influences_to_fix): pm.parentConstraint(multicon_anim_fix[i], inf, mo = True)
        
        #Length Width Height
        r = pm.exactWorldBoundingBox(pm.ls('*mesh_grp'),ii = True)
        self.node.addAttr('width',at = 'double',dv = abs(r[3] - r[0]))
        self.node.addAttr('height',at = 'double',dv = abs(r[4] - r[1]))
        self.node.addAttr('length',at = 'double',dv = abs(r[5] - r[2]))
        self.node.length.lock()
        self.node.width.lock()
        self.node.height.lock()
                    
    def get_root_joint(self):
        return pm.listConnections(self.node.root)[0]
    
    def get_root_rig(self):
        if self.node.hasAttr('connected_rigs'): return self.node
        else:
            rigs = []
            if self.node.hasAttr('connected_to'): 
                rigs += pm.listConnections(self.node.connected_to)
                for rig in rigs:
                    while rig.hasAttr('connected_to'): continue
                return rig
    
    def get_complete_rig_anims(self):
        anims = []
        root = self.get_root_rig()
        if root == None: rigs = [self.node]
        else: rigs = [root]
        if rigs[0].hasAttr('connected_rigs'): rigs += pm.listConnections(rigs[0].connected_rigs)
        for rig in rigs:
            mars_rig = CharacterRig('','',node = rig)
            anims += mars_rig.get_rig_anims() 
        return anims
        
    def get_rig_anims(self):
        #Variables
        anims = []
        components = pm.listConnections(self.node.rig_components)
        for component in components:
            if component.hasAttr('anims'): anims += pm.listConnections(component.anims)
            if component.hasAttr('switch'): anims += pm.listConnections(component.switch)
        return anims
    
    def key_anim(self,anim):
        for attr in anim.listAttr(w=True,u=True,v=True,k=True):
            attribute = attr.split('.')[-1]
            pm.setKeyframe(anim,at = attribute)
    
    def key_all_rig_anims(self):
        for anim in self.get_rig_anims(): self.key_anim(anim)
    
    def key_complete_rig_anims(self):
        for anim in self.get_complete_rig_anims(): self.key_anim(anim)
    
    def rig_default_pose(self):
        for anim in self.get_rig_anims(): mu.set_to_default_pose(anim)
    
    def mirror_rig(self):
        mu.mirror_selection(self.get_rig_anims())
        
    def mirror_complete_rig(self):
        mu.mirror_selection(self.get_complete_rig_anims())
    
    def complete_rig_default_pose(self):
        for anim in self.get_complete_rig_anims(): mu.set_to_default_pose(anim)
    
    def select_complete_rig_anims(self):
        mars_rig = CharacterRig('','',node = self.node)
        pm.select(mars_rig.get_complete_rig_anims(),add = True)
        
    def select_rig_anims(self):
        mars_rig = CharacterRig('','',node = self.node)
        pm.select(mars_rig.get_rig_anims())
        
    def select_all_anims(self): pass
    
    def select_hierarchy_anims(self): pass
    
    def topCon_shape(self,r = 5.00):
        topCon = self.get_topCon()
        
        #Make the Shape
        main = pm.circle(nr = (0,1,0),r=r)
        circle_parts = pm.detachCurve(main,p=(0.325,1.675,2.325,3.675,4.325,5.675,6.325,7.675))
        parts = circle_parts[::2]
        pm.delete(circle_parts[1::2],main)
        for i in range(1,5):
            pos = [((0.9 * r),0,(0.25 * r)), ((1.5 * r),0,(0.25 * r)), ((1.5 * r),0,(0.5 * r)), ((2.00 * r),0,0),
                   ((1.5 * r),0,-(0.5 * r)), ((1.5 * r),0,-(0.25 * r)),((0.9 * r),0,-(0.25 * r))]
            shape = pm.curve(d = 1, p = pos, k = (0,1,2,3,4,5,6));
            shape.ry.set(90 * (i - 1))
            pieces = pm.detachCurve(shape,p=(0.110,5.890))
            parts.append(pm.PyNode(pieces[1]))
            pm.delete(shape,pieces[::2])
        finished = pm.attachCurve(parts,ch=False,rpo=True)[0]
        finished_shape = finished.getChildren(s=True)
        finished_shape[0].rename('topCon_shape')
        
        #Add The Shape
        pm.parent(finished_shape,topCon,r=True,s=True)
        pm.delete(parts[1:],finished)
        pm.select(cl=True)
        
        #Visibility Attribute
        topCon.addAttr('shape_visibility',at = 'bool',dv = 1,k = True)
        topCon.shape_visibility >> finished_shape[0].visibility
    
    def add_anim_visibility_attr(self,attribute,anims,dv = 1):
        topCon = self.get_topCon()
        if topCon.hasAttr(attribute) == False: topCon.addAttr(attribute,at='bool',dv=dv,k=True)
        for anim in anims:
            shapes = pm.PyNode(anim).getChildren(s=True)
            for shape in shapes: shape.visibility.set(1)
            obj = anim.getParent()
            pm.select(cl = True)
            vis_null = pm.group(n = anim.name().replace('_anim','_vis_null'),em = True)
            #vis_null = pm.joint(n = anim.name().replace('_anim','_vis_null'),p = (0,0,0))
            #vis_null.drawStyle.set(2)
            mu.aligner(vis_null,anim)
            pm.parent(vis_null,obj)
            pm.parent(anim,vis_null)
            topCon.attr(attribute) >> vis_null.visibility
            mu.lock_and_hide_attrs(vis_null,['translate','rotate','scale','visibility'])
            
        pm.select(cl=True)