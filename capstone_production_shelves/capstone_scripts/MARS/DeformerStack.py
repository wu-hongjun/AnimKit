import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class DeformerStack(MarsRigComponent):
    def __init__(self,side, limb, start, end, controlled_anims, deformer_type = 'sine', translation = True, rotation = None,dv = 5.00, anim = None, rig = None, node = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('DeformerStack',start,'start')
        
        if self.node == None:
            #Run Function
            MarsRigComponent.__init__(self,'DeformerStack', side, limb, start = start, end = end)
            
            ##Variables
            name = side + '_' + limb
            controlled_anims = [pm.PyNode(x) for x in controlled_anims]
            def_chain = mu.duplicate_chain(mu.get_chain(start,end),name,'deformer_joint')
            deformer_nulls = mu.stack_chain(controlled_anims,rep = '_anim',wi = '_deformer_null')
            def_chain_zero = mu.stack_chain(def_chain[0],rep = '_joint',wi = '_zero_joint')[0]
            mu.lock_and_hide_attrs(deformer_nulls,['translate','rotate','v','radius'])
            if anim == None: anim = controlled_anims[0]
            
            ##Setup
            for c in def_chain[1:]: c.jointOrient.set(0,0,0)
            IKH,ef,cv = pm.ikHandle(n = name + '_IK', sj = def_chain[0], ee = def_chain[-1], sol = 'ikSplineSolver',ccv=True)
            cv.rename(name + '_IK_curve')
            pm.rebuildCurve(cv,ch = False,s = 10)
            deform, handle = pm.nonLinear(cv,type = deformer_type)
            deform.rename(name + '_deformer_' + deformer_type)
            handle.rename(name + '_deformer_' + deformer_type +'_handle')
            deformer_null = pm.group(n = name + '_deformer_' + deformer_type + '_null', em = True)
            if rotation != None: handle.rotate.set(rotation)
            mu.aligner(deformer_null, handle)
            pm.parent(handle,deformer_null)
            
            ##Attribute Setup
            if deformer_type == 'sine':
                anim.addAttr(limb + '_offset',at = 'double',dv = 0,k = True)
                anim.addAttr(limb + '_height',at = 'double',min = 0, max = 1, dv = 0,k = True)
                anim.addAttr(limb + '_length',at = 'double',min = 0.0001, dv = dv, k = True)
                
                anim.attr(limb + '_offset') >> deform.offset
                anim.attr(limb + '_height') >> deform.amplitude
                anim.attr(limb + '_length') >> deform.wavelength
                
            #Influence Switch
            for i, dn in enumerate(deformer_nulls):
                current_anim = controlled_anims[i]
                current_anim.addAttr(name + '_influence',min = 0, max = 1, dv = 1,k = True)
                bc = mu.create_node('blendColors',n = name + '_' + str(i + 1) + '_influence_blend')
                bc.color2.set(0,0,0)
                current_anim.attr(name + '_influence') >> bc.blender
                def_chain[i].rotate >> bc.color1
                bc.output >> dn.rotate
           
            #Translation Blend
            if translation == True:
                [deformer_nulls[0].attr('translate' + x).unlock() for x in ['X','Y','Z']] 
                bc = mu.create_node('blendColors',n = name + '_translate_influence_blend')
                bc.color2.set(0,0,0)
                controlled_anims[0].attr(name + '_influence') >> bc.blender
                def_chain[0].translate >> bc.color1
                bc.output >> deformer_nulls[0].translate
               
            #Component Grp Organization
            pm.select(cl = True)
            component_grp = pm.group(n=(name + '_component_grp'),em = True)
            hidden_grp = pm.group(IKH,def_chain_zero,cv,deformer_null,n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            pm.select(cl=True)
            
            #Finalize
            mu.lock_and_hide_attrs([hidden_grp,component_grp],['translate','rotate','scale'])
            
            #Connections
            mu.con_link(anim,self.node,'driver_anim')
            mu.con_link(IKH,self.node,'ik_handle')
            mu.con_link(handle,self.node,'deformer_handle')
            mu.con_link(deform,self.node,'deformer')
            mu.con_link(controlled_anims,self.node,'controlled_anims')
            mu.con_link(deformer_type,self.node,'deformer_type')
            mu.con_link(def_chain,self.node,'deformer_chain')
            mu.con_link(component_grp,self.node,'component_grp')
            mu.con_link(hidden_grp,self.node,'hidden_grp')
            
            ##Finish
            if rig != None: rig.add_to_rig(self)
            
    def connect_component_to(self,parent_node,area): pass
    
    def get_deformer(self):
        return pm.listConnections(self.node.deformer)[0]
    
    def display_handle(self,translate = None,rotate = None):
        #Variables
        deformer = pm.listConnections(self.node.deformer)[0]
        handle = pm.listConnections(self.node.deformer_handle)[0]
        driver_anim = pm.listConnections(self.node.driver_anim)[0]
        deformer_type = self.node.deformer_type.get()
        anim = pm.listConnections(self.node.driver_anim)[0]
        
        new_handle =  pm.duplicate(handle)[0]
        new_deformer =  new_handle.listConnections(s = True)[0]
        name = self.node.side.get() + '_' + self.node.limb.get()
        new_deformer.rename(name + '_display_' + deformer_type)
        new_handle.rename(name + '_display_' + deformer_type + '_handle')
        
        #Setup
        deformer_null = pm.group(n = name + '_display_' + deformer_type + '_null', em = True)
        mu.aligner(deformer_null, anim, rotation = False)
        pm.parent(new_handle,deformer_null)
        pm.pointConstraint(anim,deformer_null,mo = True)
        pm.parent(deformer_null,pm.listConnections(self.node.component_grp)[0])
        driver_anim.addAttr('display_deformer',at = 'double',min = 0, max = 1, dv = 0,k = True)
        driver_anim.display_deformer >> new_handle.visibility
        if translate != None: new_handle.translate.set(translate)
        if rotate != None: new_handle.rotate.set(rotate)
        
        ##Deformer Setup
        attributes = ['amplitude','wavelength','offset']
        for at in attributes: deformer.attr(at) >> new_deformer.attr(at)
        mu.lock_and_hide_attrs(new_handle,['translate','rotate','scale'])
        new_handle.overrideEnabled.set(1)
        new_handle.overrideDisplayType.set(2)