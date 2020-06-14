import re
from pymel.core import *
from scene_manager.methods import *
import scene_manager.metaUtil as mu
import pymel.core.runtime as rt
import pymel.core.other as other
import os
import random
import time

#meta methods
def fromNetworkToObject(node):
        '''
            turns the networkNode into the correct MetaNode object
        '''
        metaType = node.metaType.get()
        if metaType == 'FKChain':
            return FKChain('','','','',node = node)
        elif metaType == 'FKIKReverseSplineChain':
		    return FKIKReverseSplineChain('','','','',node = node)
        elif metaType == 'FKDeformerChain':
            return FKDeformerChain('','','','',node = node)
        elif metaType == 'FKFloatChain':
            return FKFloatChain('','','','',node = node)
        elif metaType == 'COGChain':
            return COGChain('','','','',node = node)
        elif metaType == 'SDKComponent':
            return SDKComponent('','','',node = node)
        elif metaType == 'SDK':
            return SDK('','','',node = node)
        elif metaType == 'ReverseChain':
            return ReverseChain('','','','',node = node)
        elif metaType == 'AdditionalTwist':
            return AdditionalTwist('','','','','',node = node)
        elif metaType == 'SingleIKChain':
            return SingleIKChain('','','','',node = node)
        elif metaType == 'FKIKSplineChain':
            return FKIKSplineChain('','','','',node = node)
        elif metaType == 'FKIKSplineTail':
            return FKIKSplineTail('', '', '', '', node = node)
        elif metaType == 'FKIKSplineFollow':
            return FKIKSplineFollow('', '', '', '', node = node)
        elif metaType == 'IKLips':
            return IKLips('','','','','','','','', node = node)
        elif metaType == 'FKIKChain':
            return FKIKChain('','','','',node = node)
        elif metaType == 'AdvancedFoot':
            return AdvancedFoot('','','','','','','','',node = node)
        elif metaType == 'EyeAimComponent':
            return EyeAimComponent('','','','','','',node = node)
        elif metaType == 'DynamicChain':
            return DynamicChain('','','','',node = node)
        elif metaType == 'StretchyJointChain':
            return StretchyJointChain('','','','','','', node = node)
        elif metaType == 'FKIKArm':
            return FKIKArm('','','','', node = node)
        elif metaType == 'FKIKArm2':
            return FKIKArm2('','','','', node = node)
        elif metaType == 'FKIKQuadrupedLeg':
            return FKIKQuadrupedLeg('','','','','','','','', node = node)
        elif metaType == 'FKIKLeg':
            return FKIKLeg('','','','','','','','', node = node)
        elif metaType == 'FKIKSpine':
            return FKIKSpine('','','','', node = node)
        elif metaType == 'Manager':
            return Manager(node = node)
        elif metaType == 'LightGroup':
            return LightGroup('', node = node)
        elif metaType == 'GeometryGroup':
            return GeometryGroup('', node = node)
        elif metaType == 'GeometryResGroup':
            return GeometryResGroup('', node = node)
        elif metaType == 'AnimGroup':
            return AnimGroup('', node = node)
        elif metaType == 'CharacterRig':
            return CharacterRig('','','', node = node)
        elif metaType == 'MultiConstraint':
            return MultiConstraint('','','','', node = node)
        elif metaType == 'ReversePelvis':
            return ReversePelvis('', '', '', '', node = node)
        elif metaType == 'RFKChain':
            return RFKChain('', '', '', '', node = node)
        elif metaType == 'FKIKHair':
            return FKIKHair('', '', '', '', '', node = node)
        elif metaType == 'ElasticComponent':
            return ElasticComponent('', '', '', '', node = node)
        elif metaType == 'TwistChainComponent':
            return TwistChainComponent('', '', '', '', '', '', node = node)
        elif metaType == 'FeatherComponent':
            return FeatherComponent('', '', '', '', node = node)
        elif metaType == 'BlendShapeController':
            return BlendShapeController('', '', '', '', node = node)
        elif metaType == 'FlexibleEyelid':
            return FlexibleEyelid('', '', '', '', '', '', '', '', '', node = node)
        elif metaType == 'FlexibleMouth':
            return FlexibleMouth('', '', '', '', '', '', '', node = node)
        elif metaType == 'FKIKLimb':
            return FKIKLimb('', '', '', '', node = node)
        elif metaType == 'FKIKBipedLeg':
            return FKIKBipedLeg('','','','','','','','', node = node)
		# From Jason's short
        elif metaType == 'Evil':
            return Evil('', node = node)
        else:
            raise Exception("fromNetworkToObject:metaNode of metaType, %s, either isn't a metaNode or not added to the fromNetworkToObject method"%metaType)

			
			
def alignPR(obj,target):
    alPos = xform(target, q= True, ws=True, rp=True);
    alRot = xform(target, q=True, ws = True, ro = True);
    move(alPos[0],alPos[1],alPos[2], obj, rpr = True);
    xform(obj, ws=True,ro=(alRot[0],alRot[1],alRot[2]))
    
def alignP(obj,target):
    alPos = xform(target, q= True, ws=True, rp=True);
    move(alPos[0],alPos[1],alPos[2], obj, rpr = True);

def get_chain(start,end):
    rn = len(PyNode(start).longName()[1:].split('|'))-1
    list = PyNode(end).longName()[1:].split('|')[rn:]
    return list

def duplicate_chain(start ,end, rep = '', wi = '',reverse = False):
    bones = get_chain(start,end);
    new_bones = []; i=0
    
    if reverse == True:
        bones.reverse()
    
    for all in bones:
        r = PyNode(all).radius.get()
        nb = joint(n=(all.replace(rep,wi)),rad=(r*2),p=(0,0,0))
        alignPR(nb,all)
        select(cl=True)
        new_bones.append(nb)
        
        rot = nb.rotate.get()
        nb.rotate.set(0,0,0)
        nb.jointOrient.set(rot)
    
    for all in new_bones[1:]:
        parent(all,new_bones[i])
        i=i+1;
    
    select(cl=True)
    return new_bones

def duplicate_chain_double(start ,end, rep = '', wi = '',reverse = False):
    bones = get_chain(start,end);
    new_bones = []; i=2
    
    if reverse == True:
        bones.reverse()
    
    for all in bones:
        r = PyNode(all).radius.get()
        rb = joint(n=(all.replace(rep,wi)+'_rot'),rad=(r*2),p=(0,0,0))
        nb = joint(n=(all.replace(rep,wi)),rad=(r*2),p=(0,0,0))
        alignPR(rb,all)
        select(cl=True)
        new_bones.append(rb)
        new_bones.append(nb)
        
        rot = rb.rotate.get()
        rb.rotate.set(0,0,0)
        rb.jointOrient.set(rot)
    
    for all in bones[1:]:
        parent(new_bones[i],new_bones[i-1])
        i=i+2;
    
    select(cl=True)
    return new_bones

def make_spline(name,start,end):
    bones = get_chain(start,end); i=0
    co = []; k=[];
    
    for all in bones:
        alPos = xform(all, q= True, ws=True, rp=True);
        co.append((alPos[0],alPos[1],alPos[2]))
        k.append(i)
        i=i+1;
    
    cv = curve(n=(name+'_cv'),d=1,p=co,k=k)
    rebuildCurve(cv,rt=0,ch=0,s=8,d=3,tol=0)
    return cv;
    
def reversible_FKIK_spine(side,name,start,end):
	
    bc = shadingNode('blendColors',au=True)
    bc.color1R.set(0)
    bc.color2R.set(1)
    
    #Get starting chain and length
    bones = get_chain(start,end); g=1; h=0; i=0; j=1; k=0; l=0; f=0
    bl = len(bones)-1
    
    #Creates switch component
    switch = group(n=(name+'_FKIK_switch'),em=True)
    addAttr(switch,ln='FKIK_Switch',at='double',min=0,max=1,k=True)
    addAttr(switch,ln='show_FK_anim',at='double',min=0,max=1,k=True)
    addAttr(switch,ln='show_reverse_FK_anim',at='double',min=0,max=1,k=True)
    
    switch.FKIK_Switch.set(1)
    switch.show_FK_anim.set(1)
    switch.show_reverse_FK_anim.set(1)
    switch.FKIK_Switch >> bc.blender
    
    ats = ['translateX','rotateX','scaleX','translateY','rotateY','scaleY','translateZ','rotateZ','scaleZ','visibility']
    ans = ['translateX','translateY','translateZ','scaleX','scaleY','scaleZ','visibility','radius']
    for at in ats:
        setAttr((name+'_FKIK_switch.'+at),k=False,l=True,cb=False)
    
    #Makes IK components
    select(cl=True)
    IK = duplicate_chain(start,end,rep = '_bind',wi = '_IK') 
    IK_curve = make_spline(name,start,end)
    IKH = ikHandle(n=(name+'_ik'),sol='ikSplineSolver',c=IK_curve,sj=IK[0],ee=IK[bl],ccv=False,pcv=False)[0]
    select(cl=True)

    #Makes FK components
    select(cl=True)
    FK = duplicate_chain_double(start,end,rep = '_bind_joint',wi = '_FK_anim')
    rev_FK = duplicate_chain_double(start,end,rep = '_bind_joint',wi = '_reverse_FK_anim',reverse = True)
    
    switch.show_FK_anim >> FK[0].visibility
    switch.show_reverse_FK_anim >> rev_FK[0].visibility
    
    rev_FK.reverse()
    rev_guides = duplicate_chain(start,end,'bind_joint','reverse_FK_guide',reverse=True)
    pointConstraint(FK[len(FK)-1],rev_FK[len(FK)-1])
    select(cl=True)
    
    #Makes Control components
    control = duplicate_chain(start,end,rep = '_bind',wi = '_control'); e=1;
    for all in control:
        all.visibility.set(0)
    parent(control,w=True);
    anims = rev_FK[1::2]
    #anims.reverse()
    #control.reverse()
    for all in control[:-1]:
	print anims[e]
	aimConstraint(control[e],all,mo=True,aim=(1,0,0),u=(0,1,0),wut='object',wuo=anims[e])
        e=e+1;
    select(cl=True); #control.reverse()

    for f in FK:
        if f.endswith('_anim'):
            addBoxToJoint(f)
            lockAndHideAttrs(f, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
            addAnimAttr(f)
        PyNode(f).drawStyle.set(2)
        #PyNode(f).addAttr('animNode',at='message')
    i=0        
    for r in rev_FK:
        if r.endswith('_anim'):
            addBoxToJoint(r)
            lockAndHideAttrs(r, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
            addAnimAttr(r); i=i+1;
        PyNode(r).drawStyle.set(2)
        #PyNode(r).addAttr('animNode',at='message')
    i=0
    #FK Anim Stretch Components
  
    '''select('*_FK_anim')
    select('*_reverse_FK_anim',d=True)
    FK_anims = ls(sl=True)
    select('*_reverse_FK_anim')
    revFK_anims = ls(sl=True)
    select(cl=True)
    FK_anims.reverse()
    num=1;
    
    for all in FK_anims[:-1]:
        revFK = PyNode(revFK_anims[num-1])
        stretch_revFK_rot = PyNode(revFK_anims[num]+'_rot')
        FK_rot = PyNode(FK_anims[num]+'_rot')
        revFK_rot = PyNode(all.replace('_FK','_reverse_FK')+ '_rot')
        
        addAttr(all,ln='stretch',at='double',min = 0,dv=1,k=True)
        addAttr(revFK,ln='stretch',at='double',min = 0,dv=1,k=True)

        stretch = shadingNode('multiplyDivide',au=True)
        rev_stretch = shadingNode('multiplyDivide',au=True)
        #rev_anim_stretch = shadingNode('multiplyDivide',au=True)
        
        stretch.operation.set(2)
        rev_stretch.input2.set(-1,-1,-1)
        stretch.input2.set(getAttr(FK_rot+'.tx'),1,1)
        PyNode(all).stretch >> stretch.input1X
        stretch.outputX >> FK_rot.translateX
        stretch.outputX >> rev_stretch.input1X
        rev_stretch.outputX >> revFK_rot.translateX
        
        num=num+1;'''
 
    #Makes sine components
    select(cl=True)
    sine = duplicate_chain(start,end,rep = '_bind',wi = '_sine')
    select(cl=True)
    pin = duplicate_chain(start,end,rep = '_bind',wi = '_pin')
    sine_curve = make_spline((name+'_sine'),start,end)
    pin_curve = make_spline((name+'_pin'),start,end)
    pin_ik_curve = make_spline((name+'_ik_pin'),start,end)
    pin_curve_shape = listRelatives(pin_curve)
    cl = cluster(pin_curve_shape[0]+'.cv[:]')
    bs = blendShape(pin_curve,pin_ik_curve,sine_curve,n='pin_curve')[0]
    setAttr((bs+'.'+pin_curve),1)
    setAttr((bs+'.'+pin_ik_curve),1)
    
    sine_IKH = ikHandle(n=(name+'_sine_ik'),sol='ikSplineSolver',c=sine_curve,sj=sine[0],ee=sine[bl],ccv=False,pcv=False)[0]
    pin_IKH = ikHandle(n=(name+'_pin_ik'),sol='ikSplineSolver',c=pin_ik_curve,sj=pin[0],ee=pin[bl],ccv=False,pcv=False)[0]
    select(pin_ik_curve)
    sineDef = mc.nonLinear(typ = 'sine')
    PyNode(sineDef[1]).rotateX.set(90)
    select(cl=True)
    
    addAttr(switch,ln='pin_to_segment',at='enum',en='None:',k=True)
    addAttr(switch,ln='amplitude',at='double',min=-5,max=5,dv=0,k=True)
    addAttr(switch,ln='wavelength',at='double',min=0.001,max=10,dv=2,k=True)
    addAttr(switch,ln='offset',at='double',dv=0,k=True)
    
    switch.amplitude >> PyNode(sineDef[1]).amplitude
    switch.wavelength >> PyNode(sineDef[1]).wavelength
    switch.offset >> PyNode(sineDef[1]).offset

    #Creates constraints to original chain
    for all in bones[:-1]:
        parentConstraint(IK[i],all,mo=False,w=0)
        parentConstraint(control[i],all,mo=False,w=0)
        parent(control[i],rev_FK[j])
	parentConstraint(rev_FK[j],control[i],w=1,sr=['x','y','z'])
        pCAttrs = listAttr(all+'_parentConstraint1',s=True,r=True,w=True,c=True,st=['*W0','*W1'])
        
        a1 = Attribute(all+'_parentConstraint1.'+pCAttrs[0])
        a2 = Attribute(all+'_parentConstraint1.'+pCAttrs[1])  
        
        switch.FKIK_Switch >> a1
        bc.outputR >> a2
        
        i=i+1;j=j+2
    parent(control[-1],rev_FK[j])
    parentConstraint(sine[0],FK[0],sr=['x','y','z'],mo=True)
    
    #Creates constraints to original chain
    
    rev_md = {}
    loc_grp = group(n=(name+'_loc_grp'),em=True)
    pin_pma = shadingNode('plusMinusAverage',au=True)
    null_md = shadingNode('multiplyDivide',au=True)
    null_md.input1.set(0,0,0); null_md.input2.set(0,0,0)
    null_md.output >> pin_pma.input3D[0]
    pin_pma.output3Dx >> cl[1].translateX
    pin_pma.output3Dz >> cl[1].translateZ
    string = 'None:'
    select('*_FK_anim_rot')
    select('*reverse*',d=True)
    fk_rots = ls(sl=True)
    sine.reverse(); pin.reverse();
    
    for all in sine:
        select(cl=True)
        addAttr(switch,ln='FK_anim_'+str(g),at='double',min=0,max=1,dv=1,k=True)
        string = string+all.replace('_sine_joint','')+':'
        s = PyNode(all)
        p = PyNode(pin[g-1])
        fk = PyNode(fk_rots[g-1])
        
        at = Attribute(name+'_FKIK_switch.FK_anim_'+str(g))
        loc = spaceLocator(n=all.replace('joint','loc'),p=(0,0,0))
        
        alignPR(loc,all);
        makeIdentity(a=True,t=True,r=True,s=True)
        parent(loc,loc_grp)
        pointConstraint(p,loc)
        
        rev_md[all] = shadingNode('multiplyDivide',au=True)
        rev_md[all].input2.set(-1,0,-1)
        loc.translate >> rev_md[all].input1
        rev_md[all].output >> pin_pma.input3D[g]
        
        fk_blend = shadingNode('blendColors',au=True)
        at >> fk_blend.blender
        s.rotate >> fk_blend.color1
        fk_blend.output >> fk.rotate
        fk_blend.color2.set(0,0,0)
        
        g=g+1;
    
    addAttr(switch+'.pin_to_segment',e=True,en=string)
    list = string.split(':')[0:-1]; r=0;
    
    for a in list:
        r=0;
        for all in rev_md:
            cd = (switch+'.pin_to_segment')
            x = (rev_md[all]+'.input2X')
            y = (rev_md[all]+'.input2Y')
            z = (rev_md[all]+'.input2Z')
            if a == 'None':
                v =0
            else:
                if all == a+'_sine_joint':
                    v=-1
                else:
                    v = 0
            setDrivenKeyframe(x,cd=cd,dv=h,v=v);
            setDrivenKeyframe(y,cd=cd,dv=h,v=v);
            setDrivenKeyframe(z,cd=cd,dv=h,v=v);
            r=r+1;
        h=h+1;
    
    rev_FK.reverse(); FK.reverse(); sine.reverse(); pin.reverse()
    pv_grps = []; rev_IKs = []
    pointConstraint(FK[0],rev_guides[0]) 
    
    for all in rev_guides[:-1]:
        rg_IK = ikHandle(n=(all+'_ik'),sol='ikSCsolver',sj=all,ee=(rev_guides[k+1]))[0]
        parentConstraint(FK[l+2],rg_IK)
        rev_IKs.append(rg_IK);
        PyNode(all).rotate >> rev_FK[l].rotate
        k=k+1; l=l+2;
     
    #Groups all components together
    select(cl=True)
    FK.reverse();
    component_grp = group(n=side+'_'+name+'_component_group')
    
    select(IK[0],IK_curve,IKH)
    IK_grp = group(n=(side+'_'+name+'_IK_group'),em=False,p=component_grp)
    IK_grp.visibility.set(0)
    select(cl=True)
    
    select(pv_grps)
    pvs = group(n=(side+'_'+name+'_FK_rev_guide_pvs'),em=False)
    select(cl=True)
    
    select(rev_IKs)
    rev_IK_grp = group(n=(side+'_'+name+'_FK_rev_guide_iks'),em=False)
    select(cl=True)
    
    select(pvs,rev_guides[0],rev_IK_grp)
    rev_guide_grp = group(n=(side+'_'+name+'_FK_rev_guide_group'),em=False)
    rev_guide_grp.visibility.set(0)
    select(cl=True)
    
    select(FK[0],rev_FK[0],rev_guide_grp)
    FK_grp = group(n=(side+'_'+name+'_FK_group'),em=False,p=component_grp)
    select(cl=True)
    
    select(pin[0],cl[1],loc_grp,pin_curve,pin_ik_curve,pin_IKH,sineDef)
    pin_grp = group(n=(side+'_'+name+'_pin_group'),em=False,p=component_grp)
    pin_grp.visibility.set(0)
    pin_grp.inheritsTransform.set(0)
    select(cl=True)
    
    select(sine_curve,sine[0],sine_IKH)
    sine_grp = group(n=(side+'_'+name+'_sine_group'),em=False,p=component_grp)
    sine_grp.visibility.set(0)
    select(cl=True)
    
    parent(switch,component_grp)
    select(cl=True)
    return [bones,IK,FK,rev_FK,switch,component_grp]
	
def FK_deformer(side,name,start,end,deform = 'bend'):
    n = side+'_'+name; i=0;
    bones = get_chain(start,end)
    FK = duplicate_chain_double(start,end,rep = '_bind_joint',wi = '_FK_anim')
    FK_anims = FK[1::2]
    FK_rots = FK[0::2]
    Deformer = duplicate_chain(start,end,rep = 'bind',wi = 'deformer')
    Deformer_IK_curve = make_spline(n,start,end)
    Deformer_IKH = ikHandle(n=(n+'_deformer_ik'),sol='ikSplineSolver',c=Deformer_IK_curve,sj=Deformer[0],ee=Deformer[-1],ccv=False,pcv=False)[0]
    
    switch = group(n=(n+'_switch'),em=True)
    ats = ['translateX','rotateX','scaleX','translateY','rotateY','scaleY','translateZ','rotateZ','scaleZ','visibility']
    for at in ats:
        setAttr((switch+'.'+at),k=False,l=True,cb=False)
    for f in FK_anims:
        addBoxToJoint(f)
        lockAndHideAttrs(f, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
        addAnimAttr(f)
        #PyNode(f).addAttr('animNode',at='message')

    for all in FK:
        PyNode(all).drawStyle.set(2)
        
    select(Deformer_IK_curve)
    def_handle = nonLinear(type = deform)
    def_handle[1].rotate.set(-90,0,90)
    
    if deform == 'bend':
        def_rot = group(n=(n+'_deform_rot'),em=True)
        def_handle[0].lowBound.set(0)
        def_handle[0].highBound.set(2)
        alignP(def_handle[1],start)
        alignPR(def_rot,start)
        parent(def_handle[1],def_rot)
        addAttr(switch,ln='curvature',at='double',k=True)
	addAttr(switch,ln='protrude',at='double',min=-10,max=20,k=True)
        switch.curvature >> def_handle[0].curvature

    elif deform == 'sine':
        addAttr(switch,ln='amplitude',at='double',min=-5,max=5,dv=0,k=True)
        addAttr(switch,ln='wavelength',at='double',min=0.001,max=10,dv=2,k=True)
        addAttr(switch,ln='offset',at='double',dv=0,k=True)
        
        switch.offset >> def_handle[0].offset
        switch.amplitude >> def_handle[0].amplitude
        switch.wavelength >> def_handle[0].wavelength
    
    for all in FK_anims[:-1]:
        parentConstraint(all,bones[i])
        addAttr(switch,ln=all,at='double',min=0,max=1,dv=1,k=True)
        addAttr(all,ln='stretch',at='double',min=0.01,dv=1,k=True)
        md = shadingNode('multiplyDivide',au=True)
        PyNode(all).stretch >> md.input2X
        val = getAttr(bones[i+1]+'.translateX')
        md.input1X.set(val)
        md.outputX >> PyNode(FK_rots[i+1]).translateX
        switch_at = Attribute(switch+'.'+all)
        bc = shadingNode('blendColors',au=True)
        Deformer[i].rotate >> bc.color1
        bc.color2.set(0,0,0)
        bc.output >> FK_rots[i].rotate
        switch_at >> bc.blender
        i=i+1;
    
    Component_grp = group(n=n+'_component_group',em=True)
    
    FK_grp = group(n=n+'_FK_grp',em=True)
    parent(FK[0],FK_grp)
    
    Deformer_grp = group(n=n+'_deformer_grp',em=True)
    Deformer_grp.visibility.set(0)
    parent(Deformer[0],Deformer_IK_curve,Deformer_IKH,def_handle[1],Deformer_grp)
    if objExists(n+'_deform_rot')==True:
        parent(def_rot,Deformer_grp)

    if deform == 'bend':
        prot_grp = group(n=(n+'_protrude_grp'),em=True)
        alignPR(prot_grp,bones[0])
        parent(FK_rots[0],prot_grp)
        parent(prot_grp,FK_grp)
        switch.protrude >> FK_rots[0].translateX
	
    parent(FK_grp,Deformer_grp,switch,Component_grp)
    select(cl=1)
    
    return [bones,FK_anims,switch,Component_grp,def_handle]	

def connectToMeta(child, parent, attrName):
    '''
    connects parent.attrName to child.metaParent
    
    child:
        child node
        
    parent:
        should be a MetaNode 
        
    attrName:
        the name of the parents attr connecting to, attr that wants reference to child
    '''
    if(not objExists(child)):
        printError("connectToMeta:" + child+ "doesn't exist")
    if(not objExists(parent)):    
        printError("connectToMeta: "+parent+" doesn't exist")
    
    addMetaParentAttr(child)
    parent = PyNode(parent)
    
    
    index = attrName.find('[')
    if not index == -1:
        attrName = attrName.split("[")[0]
            
    if not parent.hasAttr(attrName) and index == -1:
        parent.addAttr(attrName, dt = "string")
        PyNode(child).metaParent >> parent.attr(attrName)
    elif parent.hasAttr(attrName) and index == -1 and not parent.attr(attrName).isMulti():
        PyNode(child).metaParent >> parent.attr(attrName)
    else:
        if not parent.hasAttr(attrName):
            parent.addAttr(attrName, dt = "string", m = 1)
        array = parent.attr(attrName).getArrayIndices()
        done = 0
        inc = -1
        while not done:
            inc +=1
            if not inc in array:
                done = 1
        PyNode(child).metaParent >> parent.attr(attrName).elementByLogicalIndex(inc)

def connectChainToMeta(objList, parent, attrName):
    '''
    connects all the objects to a multi string attr attrName
    
    objList:
        list of child objects to connect to meta
        
    parent:
        parent meta node
        
    attrName:
        name of parents attribute which will have easy access to obj list
    '''
    if(not objExists(parent)):
        printError('connectChainToMeta: ' + parent + "doesn't exist")
    
    parent = PyNode(parent)    
    if not parent.hasAttr(attrName):
        parent.addAttr(attrName, dt = 'string', multi = 1)    
    
    inc = 0
    for obj in objList:
        if(not objExists(obj)):
            printError('connectChainToMeta: ' + obj + "doesn't exists")
        obj = PyNode(obj)
        addMetaParentAttr(obj)
        
        obj.metaParent >> parent.attr(attrName).elementByLogicalIndex(inc) 
        
        inc += 1

def addMetaParentAttr(obj):
    '''    
    add .metaParent attribute to object
    
    obj:
        object to add .metaParent to.
    '''
    if objExists(obj):
        obj = PyNode(obj)
        if not obj.hasAttr('metaParent'):
            obj.addAttr('metaParent', at = 'message')
    else:
        printError("addMetaParentAttr: node given: " + obj + " doesn't exist")
        
def isMetaNode(obj):
    '''
    checks if obj is a meta node
        
    obj:
        object to check
    
    return:
        True if obj is a metaNode
        False if obj is not a metaNode
    '''    
    if not objExists(obj):
        return False
    obj = PyNode(obj)
    if obj.type() == 'network' and obj.hasAttr('metaType'):
        return True
    return False
        
def getMetaNodesOfType(metatype):
    '''
    returns all metaNodes of specified type
    
    metaType:
        the metaType which is wanted
        
    return:
        a list of all the metaNodes of type given in the scene
    '''
    metaList = ls(type = 'network')
    retList = []
    for meta in metaList:
        if isMetaNode(meta) and meta.metaType.get().lower() == metatype.lower():
            retList.append(meta)
    return retList

def getNodeOfTypeForChar(character, metatype):
    '''
    returns all metaNodes of specified type for a specified character
    
    character:
        character in which to search for metatype
    
    metaType:
        the metaType which is wanted
        
    return:
        a list of all the metaNodes of type given for specified character
    '''
    
    metaList = ls(type = 'network')
    retList = []
    for meta in metaList:
        if isMetaNode(meta) and meta.metaType.get().lower() == metatype.lower():
            if getMetaRoot(meta, stopAt= 'CharacterRig') == character:
                retList.append(meta)
    return retList
    
def isMetaNodeOfType(node, metaType):
    '''
    
    node: node tested
    metaType: checks if meta Node is of same type
    return: true if node is metaNode and of type given
            false if node is not metaNode or of type given
    '''
    if isMetaNode(node) and node.metaType.get() == metaType:
        return True
    return False
    
def getMetaRoot(obj, stopAt= 'CharacterRig'):
    '''
    returns the metaRoot of this object
    '''
    try:
        if not (type(stopAt) is list or type(stopAt) is tuple):
            stopAt = [stopAt]
        if obj.metaType.get() in stopAt:
            return fromNetworkToObject(obj)
    except:
        pass
    try:
        for mp in obj.metaParent.listConnections():
            root = getMetaRoot(mp, stopAt)
            if root:
                return root
    except:    
        pass    

def createSingleIKChain(startJoint, endJoint, compName):
    '''
    create a ik chain
    
    startJoint:
        the starting joint for the chain
    endJoint:
        the ending joint for the chain
    compName:
        will give names to the nodes created, example 'center_spine'
    return:
        [anims,         0, a list of the anims created
        animZeroGrp,     1, a list of the groups that makes all transfroms on the anim zero
        anims_grp,        2, the group that hold all the anims
        ik_joints,       3, a list of all the joints used 
        ik_joints_grp]     4, a group that holds all the joints
    '''
    
    # get the joints chain
    chain = chainBetween(startJoint, endJoint)
    origChain = duplicateChain(startJoint, endJoint)
    ik_joints = map(lambda x: PyNode(x), chain)
    ik_joint_grp = group(ik_joints[0], n = '%s_ik_joints'%compName)
    
    #create the ik chain
    anims = []
    zeroGrps = []
    for inc in xrange(len(ik_joints)-1):
        base = ik_joints[inc]
        top = ik_joints[inc+1]
        #create Anim
        select(clear=1)
        anim = joint(n = '%s_%i_anim'%(compName, inc+1))
        alignPointOrient(top, anim, 1,1)
        zeroGrp = createZeroedOutGrp(anim)
        addAnimAttr(anim)
        cube = polyCube()[0]
        appendShape(cube, anim)
        delete(cube)
        parentConstraint(anim, top, w=1)
        lockAndHideAttrs(anim, ['sx','sy','sz','v','radius'])
        zeroGrps.append(zeroGrp)
        anims.append(anim)
        
    #rename if there is only one anim
    if len(ik_joints) == 2:
        anims[0].rename("%s_anim"%(compName))
    
    #group all the anims into one group
    animGrp = group(zeroGrps, n = '%s_anims'%compName)
    
    #delete extra nodes
    delete(origChain)
    
    #return
    return [anims, zeroGrps, animGrp, ik_joints, ik_joint_grp]
        
def createNurbsPlaneIKChain(startJoint, endJoint, compName, useReverseEndAimer=False):

    '''
    create stretchy ik controls for the chain
    startJoint:
        the starting joint for the chain
    endJoint:
        the ending joint for the chain
    useReverseEndAimer:
        If true, make a secondary aimer anim under the final control.  In truth it's always created,
        this just controls whether it's hidden or not.
    return:
        [startAnim,       #0, the ik anim that controls the start of the chain   
        midAnim,        #1  the ik anim that controls the middle of the chain, note: parented contrained between start and end
        endAnim,        #2  the ik anim that controls the end of the chain
        animGrp,        #3  the grp created around the anims and their groups, note: reparent this group instead of the individual anims
        ik_joint_grp,     #4  the group that contains the joints given, note: joints now aren't in a heirarchy
        nurbsPlane,     #5  the plane created to control the joints
        transGrp,         #6  the groups controled by the point on surface nodes
        dummyGrp,         #7  groups which match joints and are nurbConstrained to surface
        ikLocGrp,        #8  locators to help measure distanced of the joints
        distDimGrp,         #9    distance dimension objects for scaling purposes
        reverseEndAimer]        #10  reverse end aimer anim.  Included last because it's a late addition. 
    ''' 
    #get IK joints 
    chain = chainBetween(startJoint, endJoint)
    origChain = duplicateChain(startJoint, endJoint)
    ik_joints = map(lambda x: PyNode(x), chain)
    ik_joint_grp = group(ik_joints[0], n = '%s_ik_joints'%compName)
    
    #create nurbs plane
    leftCurve = createCurveThroughObjects(origChain, offset=(0,0,-1))
    rightCurve = createCurveThroughObjects(origChain, offset=(0,0,1))
    
    """
    # TODO: Should probably be able to specify a "forward" axis for the NURBs plane
    """
    nurbsPlane = loft(leftCurve, rightCurve,ch=0, ss=1, d=3, ar=1, c=0, rn=0, po=0, rsn = 0)[0]
    delete(rightCurve)
    delete(leftCurve)
    
    #connect the joints to the nurbs
        #get lengths
    totalLength = 0
    for ik in origChain[1:]:
        length = ik.translateX.get()
        totalLength += length
    

    #create Control Joints
    zeroGrps = []
    select(cl=1)
    control_start = joint(n = "%s_ik_start_anim"%compName)
    alignPointOrient(origChain[0], control_start,1,1)
    torus = polyTorus()[0]
    appendShape(torus, control_start)
    delete(torus)
    zeroGrps.append(createZeroedOutGrp(control_start))
    lockAndHideAttrs(control_start, [ 'sx', 'sy', 'sz', 'v', 'radius'])
    addAnimAttr(control_start)
    
    select(cl=1)
    control_mid = joint(n = "%s_ik_mid_anim"%compName)
    '''
    alignPointOrient(origChain[len(origChain)/2], control_mid, 1,1)
    '''
    # If there is an even number of joints, center the middle control between the center two
    if len(origChain)%2 == 0:
        delete(pointConstraint(origChain[len(origChain)/2], origChain[len(origChain)/2-1], control_mid, mo=0))
        alignPointOrient(origChain[len(origChain)/2-1], control_mid, 0,1)
    else:
        alignPointOrient(origChain[len(origChain)/2], control_mid, 1,1)

    torus = polyTorus()[0]
    appendShape(torus, control_mid)
    delete(torus)
    zeroGrps.append(createZeroedOutGrp(control_mid))
    lockAndHideAttrs(control_mid, [ 'sx', 'sy', 'sz', 'v', 'radius'])
    addAnimAttr(control_mid)
    
    select(cl=1)
    control_end = joint(n = "%s_ik_end_anim"%compName)
    alignPointOrient(origChain[-1], control_end, 1,1)
    torus = polyTorus()[0]
    appendShape(torus, control_end)
    delete(torus)
    zeroGrps.append(createZeroedOutGrp(control_end))
    lockAndHideAttrs(control_end, [ 'sx', 'sy', 'sz', 'v', 'radius'])
    addAnimAttr(control_end)

    select(cl=1)
    reverseEndAimer = joint(n = "%s_reverse_aim_anim"%compName)
    alignPointOrient(origChain[-1], control_end, 1,1)
    cone = polyCone()[0]
    appendShape(cone, reverseEndAimer)
    delete(cone)
    reverseEndAimerZeroGrp = createZeroedOutGrp(reverseEndAimer)
    zeroGrps.append(reverseEndAimerZeroGrp)
    parentConstraint(control_end, reverseEndAimerZeroGrp, mo=0)
    if not useReverseEndAimer: hide(reverseEndAimer)
    lockAndHideAttrs(reverseEndAimer, [ 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'v', 'radius'])
    addAnimAttr(reverseEndAimer)

    transGroups = []
    dummyGroups = []
    surfacePoints = []

    
    for ij in ik_joints[:1]:
        dummy = group(empty = 1, n = '%s_dummy_group'%ij.name())
        alignPointOrient(ij, dummy, 1, 1)
        rets = nurbsConstraint(nurbsPlane, dummy, u = .5, v=0)
        pointConstraint(dummy, ij, mo=1)
        transGroups.append(rets[1])
        dummyGroups.append(dummy)
        surfacePoints.append(rets[2])
        
    length = 0
    
    for i in xrange(1, len(ik_joints)-1):
        ij = ik_joints[i]
        origj = origChain[i]
        
        dummy = group(empty = 1, n = '%s_dummy_group'%ij.name())
        alignPointOrient(origj, ij, 0, 1)
        alignPointOrient(ij, dummy, 1, 1)
        
        length += ij.translateX.get()
        uvCoord = mu.getClosestPointOnSurface(nurbsPlane.getShape(), mu.getWorldPositionVector(ij))
        
        ratio = length/(totalLength) # TO FIX: THIS VALUE
        rets = nurbsConstraint(nurbsPlane, dummy, u=.5, v =uvCoord[1])
        
        # Instead of parent constraining, aim at the next joint in a similar manner
        # to the original joint chain.  This happens after everything is positioned and set up.
        # parentConstraint(dummy, ij, w=1, mo=1)
        pointConstraint(dummy, ij, mo=1)

        dummyGroups.append(dummy)
        transGroups.append(rets[1])
        surfacePoints.append(rets[2])

    for ij in ik_joints[-1:]:
        dummy = group(empty = 1, n = '%s_dummy_group'%ij.name())
        alignPointOrient(ij, dummy, 1, 1)
        length += ij.translateX.get()
        ratio = length/totalLength
        rets = nurbsConstraint(nurbsPlane, dummy, u= .5, v = ratio)
        parentConstraint(dummy, ij, w=1, mo=1, sr = ['x', 'y', 'z'])
        orientConstraint(control_end, ij, w=1, mo=1)
        dummyGroups.append(dummy)
        transGroups.append(rets[1])
        surfacePoints.append(rets[2])
    
    # Get info of each joint
    dirToNextJntList = []
    for i in xrange(0, len(ik_joints)-1):
        ij = ik_joints[i]
        dummy = dummyGroups[i]
        
        # Direction to the next joint in this joint's local space
        dirToNextJnt = mu.getLocalDir(ij, ik_joints[i+1])
        dirToNextJntList.append(dirToNextJnt)

    # Set up the aim constraints now that all the ik joints are positioned
    for i in xrange(0, len(ik_joints)-1):
        ij = ik_joints[i]
        dummy = dummyGroups[i]
        
        # The 'up' normal of the NURBs plane via the dummy group in this joint's local space
        dirToDummyZAxis = mu.getLocalDirToPos(ij, mu.getWorldForwardVector(dummy)+mu.getWorldPositionVector(ij, (0,0,0)))
        
        # IK joint aimer set up to behave like the old parent constraint
        aimConstraint(ik_joints[i+1], ij, mo=0, aim=dirToNextJntList[i], u=dirToDummyZAxis, wut="objectrotation", wuo=dummy, wu=(0,0,1))

    
    #constraint the middle anim
    #midConstGrp = group(control_mid, n = '%s_start_end_constraint'%control_mid.name())
    
    # Automatic anim movement results in hard to work with behavior - disabling (for now).
    #pointConstraint(control_start, control_end, midConstGrp, mo=1, w=1)
    
    #make the scaleX of the joints controlled by stretch
    #reparent ikjoints
    for ij in ik_joints[1:]:
        ik_joint_grp | ij
        
    ikScaleLocs = []
    distDims = []
    
    #create locators
    for inc in xrange(len(ik_joints)):
        ij = ik_joints[inc]
        loc = PyNode(spaceLocator())
        loc.translate.set(ij.getTranslation(space = 'world'))
        select(loc)
        rt.CenterPivot()
        parentConstraint(dummyGroups[inc], loc, w=1, mo=1)
        ikScaleLocs.append(loc)
        #use locators for distance calcs
    
    for inc in xrange(len(ik_joints)-1):
        ij = ik_joints[inc+1]
        startLoc = ikScaleLocs[inc]
        endLoc = ikScaleLocs[inc+1]
        dist = PyNode(distanceDimension(sp = startLoc.getTranslation(space = 'world'), ep = endLoc.getTranslation(space = 'world')))
        distDims.append(dist)
        ratioMult = createNode('multiplyDivide')# ratio = currentLen/orig
        ratioMult.operation.set(2)
        ratioMult.input2X.set(origChain[inc+1].translateX.get())
        dist.distance >> ratioMult.input1X
        ratioMult.outputX >> ij.scaleX

    #make control Joints control nurbsplane
    select(control_start, control_mid, reverseEndAimer, nurbsPlane)
    rt.SmoothBindSkin()
    
    #grouping
    animGrp = group(zeroGrps, n = '%s_anim_grp'%compName)
    transGrp = group(transGroups, n = '%s_transforms'%compName)
    dummyGrp = group(dummyGroups, n = '%s_dummys'%compName)
    ikLocGrp = group(ikScaleLocs, n = '%s_distance_locators'%compName)
    distDimGrp = group(distDims, n = '%s_distances'%compName)
    
    #turn off inherits transforms
    transGrp.inheritsTransform.set(0)
    dummyGrp.inheritsTransform.set(0)
    nurbsPlane.inheritsTransform.set(0)
    
    #delete
    delete(origChain)

    #return
    return(control_start, control_mid, control_end, animGrp, ik_joint_grp, nurbsPlane, transGrp, dummyGrp, ikLocGrp, distDimGrp, reverseEndAimer)

def createOldNurbsPlaneIKChain(startJoint, endJoint, compName):
    '''
    create stretchy ik controls for the chain
    startJoint:
        the starting joint for the chain
    endJoint:
        the ending joint for the chain
    return:
        [startAnim,       #0, the ik anim that controls the start of the chain   
        midAnim,        #1  the ik anim that controls the middle of the chain, note: parented contrained between start and end
        endAnim,        #2  the ik anim that controls the end of the chain
        animGrp,        #3  the grp created around the anims and their groups, note: reparent this group instead of the individual anims
        ik_joint_grp,     #4  the group that contains the joints given, note: joints now aren't in a heirarchy
        nurbsPlane,     #5  the plane created to control the joints
        transGrp,         #6  the groups controled by the point on surface nodes
        dummyGrp,         #7  groups which match joints and are nurbConstrained to surface
        ikLocGrp,        #8  locators to help measure distanced of the joints
        distDimGrp]        #9    distance dimension objects for scaling purposes
    ''' 
    #get IK joints 
    chain = chainBetween(startJoint, endJoint)
    origChain = duplicateChain(startJoint, endJoint)
    ik_joints = map(lambda x: PyNode(x), chain)
    ik_joint_grp = group(ik_joints[0], n = '%s_ik_joints'%compName)
    
    #create nurbs plane
    leftCurve = createCurveThroughObjects(origChain)
    rightCurve = createCurveThroughObjects(origChain)
    #PROBLEM: assume the characters rightside and leftside are on the relative Y axis
    movingRight = spaceLocator()
    movingLeft = spaceLocator()
    alignPointOrient(origChain[0], movingRight, 1,1)
    alignPointOrient(origChain[0], movingLeft, 1,1)
    parent(rightCurve, movingRight)
    parent(leftCurve, movingLeft)
    move(movingRight,[0,1,0], r=1, os=1,wd=1)
    move(movingLeft, [0,-1,0], r=1, os=1,wd=1)
    parent(rightCurve, w=1)
    parent(leftCurve, w=1)
    delete(movingRight)
    delete(movingLeft)
    nurbsCurveRebuildPref(s=len(chain), rt=0)
    nurbsPlane = loft(leftCurve, rightCurve,ch=0, ss=1, d=3, ar=1, c=0, rn=0, po=0, rsn = 0, rb=1)[0]
    delete(rightCurve)
    delete(leftCurve)
    
    #connect the joints to the nurbs
        #get lengths
    jointLengths = [0]
    totalLength = 0
    for ik in origChain[1:]:
        length = ik.translateX.get()
        totalLength += length
    
    
    #create Control Joints
    zeroGrps = []
    select(cl=1)
    control_start = joint(n = "%s_ik_start_anim"%compName)
    alignPointOrient(origChain[0], control_start,1,1)
    torus = polyTorus()[0]
    appendShape(torus, control_start)
    delete(torus)
    zeroGrps.append(createZeroedOutGrp(control_start))
    lockAndHideAttrs(control_start, [ 'sx', 'sy', 'sz', 'v', 'radius'])
    addAnimAttr(control_start)
    
    select(cl=1)
    control_mid = joint(n = "%s_ik_mid_anim"%compName)
    alignPointOrient(origChain[len(origChain)/2], control_mid, 1,1)
    torus = polyTorus()[0]
    appendShape(torus, control_mid)
    delete(torus)
    zeroGrps.append(createZeroedOutGrp(control_mid))
    lockAndHideAttrs(control_mid, [ 'sx', 'sy', 'sz', 'v', 'radius'])
    addAnimAttr(control_mid)
    
    select(cl=1)
    control_end = joint(n = "%s_ik_end_anim"%compName)
    alignPointOrient(origChain[-1], control_end, 1,1)
    torus = polyTorus()[0]
    appendShape(torus, control_end)
    delete(torus)
    zeroGrps.append(createZeroedOutGrp(control_end))
    lockAndHideAttrs(control_end, [ 'sx', 'sy', 'sz', 'v', 'radius'])
    addAnimAttr(control_end)
    
    transGroups = []
    dummyGroups = []
    surfacePoints = []
    for ij in ik_joints[:1]:
        dummy = group(empty = 1, n = '%s_dummy_group'%ij.name())
        alignPointOrient(ij, dummy, 1, 1)
        rets = nurbsConstraint(nurbsPlane, dummy, u = .5, v=0)
        parentConstraint(dummy, ij, w=1, mo=1)
        transGroups.append(rets[1])
        dummyGroups.append(dummy)
        surfacePoints.append(rets[2])
        #for the rest of the joints
    length = 0
    for ij in ik_joints[1:-1]:#ik_joints[1:]: 
        dummy = group(empty = 1, n = '%s_dummy_group'%ij.name())
        alignPointOrient(ij, dummy, 1, 1)
        length += ij.translateX.get()
        ratio = length/totalLength
        rets = nurbsConstraint(nurbsPlane, dummy, u= .5, v = ratio)
        parentConstraint(dummy, ij, w=1, mo=1)
        dummyGroups.append(dummy)
        transGroups.append(rets[1])
        surfacePoints.append(rets[2])
    for ij in ik_joints[-1:]:
        dummy = group(empty = 1, n = '%s_dummy_group'%ij.name())
        alignPointOrient(ij, dummy, 1, 1)
        length += ij.translateX.get()
        ratio = length/totalLength
        rets = nurbsConstraint(nurbsPlane, dummy, u= .5, v = ratio)
        parentConstraint(dummy, ij, w=1, mo=1, sr = ['x', 'y', 'z'])
        orientConstraint(control_end, ij, w=1, mo=1)
        dummyGroups.append(dummy)
        transGroups.append(rets[1])
        surfacePoints.append(rets[2])
    
    #constraint the middle anim
    midConstGrp = group(control_mid, n = '%s_start_end_constraint'%control_mid.name())
    #parentConstraint(control_start, control_end, midConstGrp, mo=1, w=1)
    pointConstraint(control_start, control_end, midConstGrp, mo=1, w=1)
    
    #make the scalXe the joints controlled by stretch
    #reparent ikjoints
    for ij in ik_joints[1:]:
        ik_joint_grp | ij
        
    ikScaleLocs = []
    distDims = []
    #create locators
    for inc in xrange(len(ik_joints)):
        ij = ik_joints[inc]
        loc = PyNode(spaceLocator())
        loc.translate.set(ij.getTranslation(space = 'world'))
        select(loc)
        runtime.CenterPivot()
        parentConstraint(dummyGroups[inc], loc, w=1, mo=1)
        ikScaleLocs.append(loc)
        #use locators for distance calcs
    for inc in xrange(len(ik_joints)-1):
        ij = ik_joints[inc+1]
        startLoc = ikScaleLocs[inc]
        endLoc = ikScaleLocs[inc+1]
        dist = PyNode(distanceDimension(sp = startLoc.getTranslation(space = 'world'), ep = endLoc.getTranslation(space = 'world')))
        distDims.append(dist)
        ratioMult = createNode('multiplyDivide')# ratio = currentLen/orig
        ratioMult.operation.set(2)
        ratioMult.input2X.set(origChain[inc+1].translateX.get())
        dist.distance >> ratioMult.input1X
        ratioMult.outputX >> ij.scaleX
    
    #make control Joints control nurbsplane
    select(control_start, control_mid, control_end, nurbsPlane)
    rt.SmoothBindSkin()
    
    #grouping
    animGrp = group(zeroGrps, n = '%s_anim_grp'%compName)
    transGrp = group(transGroups, n = '%s_transforms'%compName)
    dummyGrp = group(dummyGroups, n = '%s_dummys'%compName)
    ikLocGrp = group(ikScaleLocs, n = '%s_distance_locators'%compName)
    distDimGrp = group(distDims, n = '%s_distances'%compName)
    
    #turn off inherits transforms
    transGrp.inheritsTransform.set(0)
    dummyGrp.inheritsTransform.set(0)
    nurbsPlane.inheritsTransform.set(0)
    
    #delete
    delete(origChain)
    
    #return
    return(control_start, control_mid, control_end, animGrp, ik_joint_grp, nurbsPlane, transGrp, dummyGrp, ikLocGrp, distDimGrp)
    
def createReverseChain(startJoint, endJoint, compName):
    '''
    return [rev_piv_joint,  #anim
            anim_grp,       #anim_grp
            joint_grp]         #joint_grp
    '''

    chain = chainBetween(startJoint, endJoint)
    chain = map(lambda x: PyNode(x), chain)
    if not len(chain) == 2:
        raise Exception('ReverseChain.__init__: should only have 2 joints ')
    
    #create control chain
    control_joints = duplicateChain(chain[0], chain[-1], '_joint', '_control_joint')
    
    
    #create reverse Joints
    select(cl=1)
    piv_pos = chain[-1].getTranslation(space = 'world')
    rot_pos = chain[0].getTranslation(space = 'world')
    rev_piv_joint = joint(p = piv_pos)
    rev_rot_joint = joint(p = rot_pos, n = "%s_rot_joint"%compName)
    joint(rev_piv_joint, e=1, zso=1, oj='xyz', sao='yup')
    
    #make pivot joint into anim
    addBoxToJoint(rev_piv_joint)
    lockAndHideAttrs(rev_piv_joint, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
    addAnimAttr(rev_piv_joint)
    rev_piv_joint.rename('%s_anim'%compName)        
    
    #parent Constrain to control and bind joints
    parentConstraint(rev_rot_joint, control_joints[0],mo=1,w=1)
    
    for inc in xrange(len(chain)-1):
        parentConstraint(control_joints[inc], chain[inc])
                
    #group
    jointGrp = group(control_joints[0], n = "%s_joint_group")
    animGrp = group(rev_piv_joint, n = "%s_anim_group")
                
    return [rev_piv_joint, animGrp, jointGrp]
    
###################################################################
#              Nebbish Production
###################################################################
def createFaceComponent(char, joints, parentComponent, layer=None):
    components = []
    for j in joints:
        j = PyNode(j)
        side = j.side.get()
        if side == 2:
            side = 'right'
        elif side == 1:
            side = 'left'
        else:
            side = 'center'
        bodyPart = j.otherType.get()
        par = j.getParent()
        component = SingleIKChain(side, bodyPart, par, j)
        if layer!=None:
            map(lambda x: layer.append(x), component.getAllAnims())
        component.connectToComponent(parentComponent, par)
        components.append(component)
        char.addRigComponent(component)
    return components


def setupOptionalMaterials(materials,controller, shader_name, path):
    matAttrs = { 'blinn':['color','specularColor'], \
             'lambert':['color']}
    passAttrs = { 'blinn':['normalCamera'] , \
                  'lambert' : ['normalCamera']}
    if not objExists(controller):
        meta.printError("%s doesn't exist"%controller)
        return None
        
    if not os.path.isdir(path):
        meta.printError("setupOptionalMaterials: %s is not a directory"%path)
        return None
    
    #shader = shadingNode('blinn', asShader=1, n = '%s_mat'%(name));
    shader = None
    first = True
    second = False
    controller.addAttr('material',at='enum',enumName=':'.join(materials),k=1)
    matIdx=0
    matEnum={}
    for mat in materials:
        matEnum[mat]=matIdx
        matIdx = matIdx + 1
    
    lastConditional = None
    prevConditions = {}
    prevMat = None
    prevCondNodes = None
    for name in materials:
        print name
        fileName = path + "/" + name + ".ma"
        if not os.path.exists(fileName):
            print("importing shader: no file matched for %s"%name)
        else:
            newNodes = importFile(fileName, f=1, returnNewNodes =1, defaultNamespace =1)
            matNode = PyNode(name)
            if not matNode:
                printWarning("*+*+*+*+*+ Skipping %s, material node not found"%name)
            
            if shader==None :
                shader = shadingNode(matNode.type(), asShader=1, n =  shader_name)
            
            
            if first:
                first = False
                second = True
                prevMat = matNode
                for attrib in matAttrs[shader.type()]:
                    matNode.attr(attrib)>>shader.attr(attrib)
                for input in matNode.normalCamera.inputs():
                    input.outNormal>>shader.normalCamera
            else:
                if second:
                    second = False
                    condNodes = {}
                    for attrib in matAttrs[shader.type()]:
                        condNodes[attrib] = shadingNode('condition', name="%(n)s_cond_%(a)s"%{'n':name,'a':attrib}, asUtility=1)
                        condNode = condNodes[attrib]
                        prevMat.attr(attrib)//shader.attr(attrib)
                        condNode.outColor >> shader.attr(attrib)
                        prevMat.attr(attrib) >> condNode.colorIfFalse
                        matNode.attr(attrib) >> condNode.colorIfTrue
                        controller.material >> condNode.firstTerm
                        condNode.secondTerm.set(matEnum[name])
                    #Do a bump map if it exists
                    for input in prevMat.normalCamera.inputs():
                        condNodes['bump']=shadingNode('condition', name="%(n)s_cond_%(a)s"%{'n':name,'a':'bump'}, asUtility=1)
                        condNode = condNodes['bump']
                        input.outNormal//shader.normalCamera
                        condNode.outColor >> shader.normalCamera
                        input.outNormal >> condNode.colorIfFalse
                        for input2 in matNode.normalCamera.inputs():
                            input2.outNormal >> condNode.colorIfTrue
                        controller.material >> condNode.firstTerm
                        condNode.secondTerm.set(matEnum[name])
                        
                    prevCondNodes = condNodes
                    prevMat = matNode
                else:
                    condNodes = {}
                    for attrib in matAttrs[shader.type()]:
                        condNodes[attrib] = shadingNode('condition', name="%(n)s_cond_%(a)s"%{'n':name,'a':attrib}, asUtility=1)
                        condNode = condNodes[attrib]
                        prevCond = prevCondNodes[attrib]
                        prevCond.outColor//shader.attr(attrib)
                        prevCond.outColor>>condNode.colorIfFalse
                        matNode.attr(attrib)>>condNode.colorIfTrue
                        condNode.outColor>>shader.attr(attrib)
                        controller.material>>condNode.firstTerm
                        condNode.secondTerm.set(matEnum[name])
                    #Do a bump map if it exists
                    for input in prevMat.normalCamera.inputs():
                        condNodes['bump']=shadingNode('condition', name="%(n)s_cond_%(a)s"%{'n':name,'a':'bump'}, asUtility=1)
                        condNode = condNodes['bump']
                        prevCond = prevCondNodes['bump']
                        prevCond.outColor//shader.normalCamera
                        prevCond.outColor>>condNode.colorIfFalse
                        input.outNormal>>condNode.colorIfTrue
                        condNode.outColor>>shader.normalCamera
                        controller.material>>condNode.firstTerm
                        condNode.secondTerm.set(matEnum[name])
                    prevCondNodes = condNodes
                    prevMat = matNode
        prevName = name
    return shader

def setupOptionalLayeredMaterials(materials,controller, shader_name, path):
    matAttrs = { 'blinn':['color','specularColor'], \
             'lambert':['color']}
    passAttrs = { 'blinn':['normalCamera'] , \
                  'lambert' : ['normalCamera']}
    if not objExists(controller):
        meta.printError("%s doesn't exist"%controller)
        return None
        
    if not os.path.isdir(path):
        meta.printError("setupOptionalLayeredMaterials: %s is not a directory"%path)
        return None
    
    #shader = shadingNode('blinn', asShader=1, n = '%s_mat'%(name));
    shader = None
    first = True
    second = False
    controller.addAttr('material',at='enum',enumName=':'.join(materials),k=1)
    matIdx=0
    matEnum={}
    for mat in materials:
        matEnum[mat]=matIdx
        matIdx = matIdx + 1
    
    lastConditional = None
    prevConditions = {}
    prevMat = None
    prevCondNodes = None
    for name in materials:
        print name
        fileName = path + "/" + name + ".ma"
        if not os.path.exists(fileName):
            print("importing shader: no file matched for %s"%name)
        else:
            newNodes = importFile(fileName, f=1, returnNewNodes =1, defaultNamespace =1)
            matNode = PyNode(name)
            if not matNode:
                printWarning("*+*+*+*+*+ Skipping %s, material node not found"%name)
            
            if shader==None :
                shader = shadingNode('layeredShader', asShader=1, n =  shader_name)
                shader.setCompositingFlag(1)
            
            defaultNavigation(force=1,connectToExisting=1,source=matNode,destination=shader)
            matNode.outColor>>shader.attr('inputs['+str(matEnum[name])+']').color
            matNode.outGlowColor>>shader.attr('inputs['+str(matEnum[name])+']').glowColor
            condNode = shadingNode('condition', name="%(n)s_cond"%{'n':name}, asUtility=1)
            controller.material >> condNode.firstTerm
            condNode.secondTerm.set(matEnum[name])
            condNode.outColor>>shader.attr('inputs['+str(matEnum[name])+']').transparency
            
            
    return shader
    
    
def applyShaderFromFile(name, path, meshes):
    '''
        reads a shader from a file and applies it to the given meshes
    
        name:
            name of the shader -- should be shading node name and file name
        path:
            path to file
        meshes:
            list of meshes to apply shader to
            
    '''
    if not os.path.isdir(path):
        meta.printError("applyShaderFromFile: %s is not a directory"%path)
        return None
    
    print name
    fileName = path + "/" + name + ".ma"
    if not os.path.exists(fileName):
        print("importing shader: no file matched for %s"%name)
    else:
        newNodes = importFile(fileName, f=1, returnNewNodes =1, defaultNamespace =1)
        matNode = PyNode(name)
        if not matNode:
            printWarning("*+*+*+*+*+ Skipping %s, material node not found"%name)
        
        
        select(meshes)
        hyperShade(assign=matNode)
        

def applyWeights(mesh,weightsFile,mode):
    '''
        Uses comet scripts to apply saved weights to a mesh
        
        mesh:
            name of mesh to apply to
            
        weightsFile:
            full path and filename of stored weights
            
        mode:
            1 for point order, 2 for world coord
    '''
    mel.eval('source libSkin')
    mel.eval('source libString')
    mel.eval('source cometSaveWeights')
    skin = mel.libSkin_getSkinFromGeo(mesh);
    print skin
    mesh_obj = PyNode(mesh)
    select(mesh_obj.vtx[:])


    
    tol = -1.0
    mirrorMode = 1 # none
    doPrune = 1
    prunePlaces = 5
    values = [ skin, '[%s]'%','.join(mel.libSkin_getSelComps(skin[0])) ,mode , tol, mirrorMode, '', '', doPrune, prunePlaces]
    print values
    mel.cSaveW_load(skin[0], weightsFile, mel.libSkin_getSelComps(skin[0]) ,mode , tol, mirrorMode, '', '', doPrune, prunePlaces) 

def applyWeightsNative(mesh, weightsFile):
    '''
        Uses native maya weight import to apply saved weights to a mesh
        
        mesh:
            name of mesh to apply to
            
        weightsFile:
            full path and filename of stored weights
    '''
    select(cl=True)
    select(mesh)
    weightsFile = weightsFile.replace('\\', '\\\\')
    mel.eval('source importSkinMap')
    mel.eval('importSkinWeightMap("' + weightsFile + '", "weightMap")')


#meta classes            
class MetaNode():
        def __init__(self, metaType, metaVersion, metaDescription):
            '''
            metaType:
                the type of rig Component
            metaVersion:
                what version is the component in
            metaDescription:
                a brief description of what the metaComponent does            
            '''
            self.networkNode = createNode('network', n = metaType)
            self.networkNode.setAttr('metaType', metaType ,f=1)
            self.networkNode.setAttr('metaVersion', metaVersion ,f=1)
            self.networkNode.setAttr('metaDescription', metaDescription ,f=1)
        
        def metaType(self):
            '''
            returns the metaType of the metaNode
            '''
            return self.networkNode.getAttr('metaType')
        
            
        def metaVersion(self):
            '''    
            returns the version of the metaNode
            '''
            return self.networkNode.getAttr('metaVersison')
        
            
        def metaDescription(self):
            '''
            returns the meta description of the metaNode
            '''
            return self.networkNode.getAttr('metaVersison')
        
        
        def __str__(self):
            '''
            the to string method
            '''
            return '[%s::%s]'%(self.networkNode.metaType.get(),self.networkNode.name())
            
        def __eq__(self, other):
            try:
                return self.networkNode == other.networkNode
            except:
                return False

class Manager(MetaNode):
    def __init__(self, node = None):
        """
        node:
            existing network node of a Manager Meta Node
        """        
        if node:
            pass
        else:
            MetaNode.__init__(self, 'SceneManager', 1.0, 'Contains info about the Scene')
            self.networkNode.addAttr('file_path', dt = 'string')
            mc.file(q=1, l=1)[0]
            self.file_name = self.file_path.split('/')[-1][:-3]
            self.rigs 
            self.lights = []
            self.efx = []

        
    def saveIter(self):
        '''        
        saves an iteration of the scene in the iterations folder, if iterations folder doesnt exist it will create one
        '''
        SaveIterWindow()

        
    def addLightGroup(self, lightGrp):
        '''
        adds a light group to the manager node
        '''
        pass

class LightGroup(MetaNode):
        def __init__(self, groupName ,node = ''):
            '''
            groupName:
                the name of the lightGroup
            node:
                an existing LightGroup meta Node
            '''
            if node:
                if objExists(node):
                    node = PyNode(node)
                    if( isMetaNode(node) and node.metaType.get() == 'LightGroup'):
                        self.networkNode = node
                    else:
                        printError("LightGroup: node %s is not a LightGroup metaNode"%(node))
                else:
                    printError("LightGroup: node %s doesn't exist"%(node))
                    
            else:
                MetaNode.__init__(self, 'LightGroup', 1.0, 'Contains info about lights in Group')
                self.networkNode.setAttr('groupName', groupName ,f=1)
                self.networkNode.addAttr('keys', dt = 'string', m=1)
                self.networkNode.addAttr('fills', dt = 'string', m=1)
                self.networkNode.addAttr('rims', dt = 'string', m=1)
                self.networkNode.addAttr('others', dt = 'string', m=1)
                
        
        def createLightByType(self, lightType):
            '''
            creates a light
            '''
            if lightType.lower() == 'spot':
                return spotLight().getParent()
            elif lightType.lower() == 'directional':
                return directionalLight().getParent()
            elif lightType.lower() == 'point':
                return pointLight().getParent()
            elif lightType.lower() == 'volume':
                return createNode('volumeLight').getParent()
            elif lightType.lower() == 'area':
                return createNode('areaLight').getParent()
            elif lightType.lower() == 'ambient':
                return ambientLight().getParent()
            else:
                print 'WARNING LIGHT NOT CREATED'
                return None

        def addLightToRims(self, light):
            '''
            adds the given light to the rim lights
            light:
                light to add to rims
            '''
            self.addLightToGroup(light, 'rims')
        
        def addLightToKeys(self,light):
            '''
            adds the given light to the key lights
            light:
                light to add to keys
            '''
            self.addLightToGroup(light, 'keys')
            
        def addLightToOthers(self, light):
            '''
            adds the given light to the other lights
            light:
                light to add to other
            '''
            self.addLightToGroup(light, 'others')

        def addLightToFills(self,light):
            '''
            adds the given light to the fill lights
            light:
                light to add to fills
            '''
            self.addLightToGroup(light, 'fills')

        def addLightTypeToRims(self, ltype):
            '''
            creates light of ltype and adds it to rims
            ltype:
                the light type, (point, area, spot, ...)
            '''
            self.addLightToGroup(self.createLightByType(ltype), 'rims')
    
        def addLightTypeToKeys(self, ltype):
            '''
            creates light of ltype and adds it to keys
            ltype:
                the light type, (point, area, spot, ...)
            '''
            self.addLightToGroup(self.createLightByType(ltype), 'keys')
        
        def addLightTypeToOthers(self, ltype):
            '''
            creates light of ltype and adds it to others
            ltype:
                the light type, (point, area, spot, ...)
            '''
            self.addLightToGroup(self.createLightByType(ltype), 'others')
    
        def addLightTypeToFills(self, ltype):
            '''
            creates light of ltype and adds it to fills
            ltype:
                the light type, (point, area, spot, ...)
            '''
            self.addLightToGroup(self.createLightByType(ltype), 'fills')    

        def addSelectedLightsToGroup(self, groupName):
            '''
            adds all the selected lights to the group given
            groupName:
                the group to add the lights to, (keys, rims, fills, others)
            '''
            selection = ls(sl=1)
            allLights = ls(type = 'lights')
            for item in selection:
                shape = item.getShape()
                if shape in allLights:
                    self.addLightToGroup(item, groupName)    
            
        def addLightToGroup(self, light, groupName):
            '''
            adds the given light to the given group
            light:
                the light to add to the group
            groupName:
                the name of the group to add the light to, (keys, fills, rims, others)
            return:
                true if added, else false
            '''
            #see if the group name exists if it doesn't return None
            try:
                self.networkNode.attr(groupName)
            except MayaAttributeError:
                print "LightGroup.addLightToGroup: got MayaAttributeError, group doesn't exist"
    
            #if light already is in group or doesn't exist, don't add light
            
            if (not objExists(light)) or (light in self.networkNode.attr(groupName).get()):
                return None
            number = 0
            groups = ['rims','fills','keys','others']
            groupName = groupName.lower()
            if groupName in groups:
                    number = self.networkNode.attr(groupName).numElements()
                    connectToMeta(light, self.networkNode, '%s[%i]'%(groupName, number) )
            return True

        def RemoveLightFromGroup(self, light, groupName):
            '''
            removes the light grom the group specified
            light:
                the light to remove
            groupName:
                the name of the group to remove from
            return:
                return the light if removed, else false
            '''
            #see if the group name exists if it doesn't return None
            try:
                self.networkNode.attr(groupName)
            except MayaAttributeError:
                print "LightGroup.addLightToGroup: got MayaAttributeError, group doesn't exist"
            #if light already is in group or doesn't exist, don't add light
            
            if (not objExists(light)) or (light in self.networkNode.attr(groupName).get()):
                return None
            
            groups = ['rims','fills', 'keys', 'others']    
            groupName = groupName.lower()
            if groupName in groups:
                for num in xrange(self.networkNode.attr(groupName).numElements()):
                    if listConnections(self.networkNode.attr('%s[%i]'%(groupName,num)))[0] == light:
                        self.networkNode.attr('%s[%i]'%(groupName, num)).remove(b=1)
                        return light
            
                            
        def getAllLights(self):
            '''
            return all the lights in the light group
            '''
            allLights = []
            map((lambda x:allLights.append(x)),self.getRims())
            map((lambda x:allLights.append(x)),self.getKeys())
            map((lambda x:allLights.append(x)),self.getFills())
            map((lambda x:allLights.append(x)),self.getOthers())
            return allLights
    
        def getKeys(self):
            '''
            return all the key lights
            '''
            return self.networkNode.keys.get()
            
        def getFills(self):
            '''
            return all the fill lights
            '''
            return self.networkNode.fills.get()
            
        def getRims(self):
            '''
            return all the rim lights
            '''
            return self.networkNode.rims.get()
            
        def getOthers(self):
            '''
            return all the other lights
            '''
            return self.networkNode.others.get()

        def selectRimLights(self):
            '''
            replace selection with rim lights
            '''
            select(cl=1)
            map((lambda x: select(x, add=1)), self.getRims())
        
        def selectKeyLights(self):
            '''
            replace selection with the key lights
            '''
            select(cl=1)
            map((lambda x: select(x, add=1)), self.getKeys())
        
        
        def selectFillLights(self):
            '''
            replace selection with the fill lights
            '''
            select(cl=1)
            map((lambda x: select(x, add=1)), self.getFills())
        
        def selectOtherLights(self):
            '''
            replace selection with the other lights
            '''
            select(cl=1)
            map((lambda x: select(x, add=1)), self.getOthers())
        
        def selectAllLights(self):
            '''
            replace selection with all the lights in the LightGroup
            '''
            select(cl=1)
            map((lambda x: select(x, add=1)), self.getAllLights())
            
        def getNetworkNode(self):
            '''
            retrun the networkNode of this metaNode
            '''
            return self.networkNode
            
        def getGroupName(self):
            '''
            return the name of this LightGroup
            '''
            return self.networkNode.groupName.get()

        def appendLightGroup(self, other):
            '''
            append all the lights from other group into this group
            
            other:
                the other LightGroup
            '''
            
            for light in other.getKeys():
                self.addLightToKeys(light)
            for light in other.getFills():
                self.addLightToFills(light)
            for light in other.getRims():
                self.addLightToRims(light)
            for light in other.getOthers():
                self.addLightToOthers(light)
                
class GeometryGroup(MetaNode):
    def __init__(self, groupName ,node = ''):
        '''
        groupName:    
            name of the Geometry Group
        node:
            an existing geometry Node
        '''    
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'GeometryGroup'):
                    self.networkNode = node
                else:
                    printError("GeometryGroup: node %s is not a GeometryGroup metaNode"%(node))
            else:
                printError("GeometryGroup: node %s doesn't exist"%(node))
        else:
            MetaNode.__init__(self, 'GeometryGroup', 1.0, 'groups Geometry into sections')
            self.networkNode.setAttr('groupName', groupName ,f=1)
            self.networkNode.addAttr('resGroups', dt = 'string', multi = 1)

                        
    def hideAllGeo(self):
        '''
        hide all geometry in the group
        '''
        ress = self.getResGroups()
        for res in ress:
            res.setVisibility(0)
            
    def showAllGeo(self):
        '''
        unhides all geometry in the group
        '''
        ress = self.getResGroups()
        for res in ress:
            res.setVisibility(1)
            
    def makeHighGeo(self):
        '''
        makes all the geometry in the group highPoly
        '''
        ress = self.getResGroups()
        for res in ress:
            res.setToHigh()
            
    def makeLowGeo(self):
        '''
        makes all the geometry in the group low poly 
        '''
        ress = self.getResGroups()
        for res in ress:
            res.setToLow()
        
    def getGroupName(self):
        '''
        returns the name of the GeometryGroup
        '''
        return self.networkNode.groupName.get()
        
    def getResGroups(self, network = None):
        '''
        returns all the GeoResGroups in the GeometryGroup
        network:
            will return the networkNodes instead of the GeoResGroup object
        '''
        ress = listConnections(self.networkNode.resGroups)
        if network:
            return ress
        
        newlist = []
        
        for obj in ress:
            if obj:
                buff = GeometryResGroup("", node = obj)
                newlist.append(buff)
        return newlist
        
    def addResGroup(self, res):
        '''
        adds the res group to this Geometry Group
        res:
            the GeometryResGroup to add        
        '''
        if( objExists(res) and isMetaNode(res) and res.metaType.get() == 'GeometryResGroup'):
            numElements = self.networkNode.resGroups.numElements()
            attr = 'resGroups[%i]'%numElements
            connectToMeta(res, self.networkNode,attr )
        else:
            printError("addResGroup: node %s is not a GeometryResGroup"%res)
        
class GeometryResGroup(MetaNode):
    def __init__(self, groupName, low = None , high= None, node = ''):
        '''
        groupName:
            name of this resGroup
        low:
            low poly geometry
        high:
            high poly geometry
        node:
            an existing GeometeryResGroup meta node
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'GeometryResGroup'):
                    self.networkNode = node
                    if low:
                        self.setLowPolyGeo(low)
                    if high:
                        self.setHighPolyGeo(high)     
                else:
                    printError("GeometryGroup: node %s is not a GeometryGroup metaNode"%(node))
            else:
                printError("GeometryGroup: node %s doesn't exist"%(node))
        else:
            MetaNode.__init__(self, 'GeometryResGroup', 1.0, 'contains high-res and low-res geos of objects')
            self.networkNode.setAttr('groupName', groupName, f=1)
            self.networkNode.addAttr('highPolyGeo', dt = 'string')
            self.setHighPolyGeo(high)
            self.networkNode.addAttr('lowPolyGeo', dt = 'string')
            self.setLowPolyGeo(low)
            self.networkNode.setAttr('isHighRes', 0, f = 1 )
            self.networkNode.setAttr('isVisible',1,f=1)
            self.setToLow()
            self.setVisibility(1)
    
    def renameGroup(self, newName):
        '''
        renames the GeometryResGroup to the new name
        newName:
            the name to change to
        '''
        if newName:
            self.networkNode.groupName.set(newName)
                    
    def setLowPolyGeo(self, geo):
        '''
        sets the lowPoly geometry for the ResGroup
        '''
        if objExists(geo) and nodeType(geo) == 'transform':
            connectToMeta(geo, self.networkNode, 'lowPolyGeo')
        else:
            printError("GeometryResGroup.SetLowPolyGeo: geo given %s doesn't exist or isn't transform node"%geo)
    
    def getGroupName(self):
        '''
        return the name of the group
        '''
        return self.networkNode.groupName.get()
            
    def setHighPolyGeo(self, geo):
        '''
        sets the the highPoly geometry for the ResGroup
        '''
        if objExists(geo) and nodeType(geo) == 'transform':
            connectToMeta(geo, self.networkNode, 'highPolyGeo')
        else:
            printError("GeometryResGroup.SetHighPolyGeo: geo given %s doesn't exist or isn't transform node"%geo)
            
    def toggleRes(self):
        '''
            if geometry is low poly then turn to high, else turn to low
        '''
        state = self.networkNode.isHighRes.get()
        if state:
            setToLow()
        else:
            setToHigh()

    def setToHigh(self):
        '''
        sets the group to high Poly
        '''
        if listConnections(self.networkNode.lowPolyGeo) and listConnections(self.networkNode.highPolyGeo):
            self.networkNode.isHighRes.set(1)
            if self.networkNode.isVisible.get():
                listConnections(self.networkNode.lowPolyGeo)[0].visibility.set(0)
                listConnections(self.networkNode.highPolyGeo)[0].visibility.set(1)
        else:
            print("setToHigh: doesn't have both high and low geometry")
        
    def setToLow(self):
        '''
        sets the group to lowPoly
        '''
        if listConnections(self.networkNode.lowPolyGeo) and listConnections(self.networkNode.highPolyGeo):
            self.networkNode.isHighRes.set(0)
            if self.networkNode.isVisible.get():
                listConnections(self.networkNode.lowPolyGeo)[0].visibility.set(1)
                listConnections(self.networkNode.highPolyGeo)[0].visibility.set(0)
        else:
            print("setToHigh: doesn't have both high and low geometry")
    
    def isHighRes(self):
        '''
        return True if ResGroup is high Poly
        '''
        return self.networkNode.isHighRes.get()
    
    def setVisibility(self, var):
        '''
        set the visibility of the ResGroup, if 1, then geometry is visible, else: all geometry is hidden
        '''
        self.networkNode.isVisible.set(var)
        listConnections(self.networkNode.lowPolyGeo)[0].visibility.set(bool(var and (1-self.networkNode.isHighRes.get())))
        listConnections(self.networkNode.highPolyGeo)[0].visibility.set(bool(var and self.networkNode.isHighRes.get()))
            
    def isVisible(self):
        '''
        return is the geometry is visible
        '''
        return self.networkNode.isVisible.get()
        
    def toggleVis(self):
        '''
        if geometry is visible then hides them, else: shows geometry
        '''
        self.setVisibility(1 - self.isVisible())

class CharacterRig(MetaNode):
    def __init__(self, characterName, upDirection, forwardDirection, rootJoint = None, node = ''):
        '''
        characterName:
            the name of the character
        upDirection:
            the axis of the charcters up direction
        forwardDirection:
            the axis of the characters forward direction
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'CharacterRig'):
                    self.networkNode = node
                else:
                    printError("CharacterRig: node %s is not a CharacterRig metaNode"%(node))
            else:
                printError("CharacterRig: node %s doesn't exist"%(node))
        else:
            MetaNode.__init__(self, 'CharacterRig', 1.0, 'contains the charcter rig information')
            #error test inputs
            directions = ['x', 'y', 'z', '-x', '-y', '-z']
            if not upDirection in directions:
                raise Exception("CharacterRig.__init__(): upDirection should be one of %s"%directions.__repr__())
            if not forwardDirection in directions:
                raise Exception("CharacterRig.__init__(): forwardDirection should be one of %s"%directions.__repr__())
            if directions.index(upDirection) % 3 == directions.index(forwardDirection)%3:
                raise Exception("CharacterRig__init__(): forwardDirection and upDirection should are on same axis")
            
            if(rootJoint == None):
                rootJoint = getJointsByLabel('center', 'root')
            
            topCon = joint(p = [0,0,0], n = "%s_topCon"%characterName)
            lockAndHideAttrs(topCon, ['radius'])
            topCon.scaleX.set(keyable = 0, cb = 0)
            topCon.scaleY.set(keyable = 0, cb = 0)
            topCon.scaleZ.set(keyable = 0, cb = 0)
            topCon.addAttr('globalScale', dv = 1, min = .000001, keyable = 1)
            topCon.globalScale >> topCon.scaleX
            topCon.globalScale >> topCon.scaleY
            topCon.globalScale >> topCon.scaleZ
            addAnimAttr(topCon)
            
            compGrp = group(empty = 1, n = 'component grp')
            bindGrp = group(rootJoint, n = "bind joint grp")
            meshGrp = group(empty = 1, n = "mesh grp")
            meshGrp.inheritsTransform.set(0)
            parent([compGrp, bindGrp, meshGrp], topCon)
            
            #connectToMeta
            self.networkNode.setAttr('characterName', characterName, f=1)
            self.networkNode.addAttr('rigComponents',dt = 'string', m=1)
            self.networkNode.addAttr('utilComponents',dt = 'string', m=1)
            self.networkNode.addAttr('meshes',dt = 'string', m=1)
            self.networkNode.setAttr('upDirection', upDirection, f=1)
            self.networkNode.addAttr('leftShader', dt = 'string')
            self.networkNode.addAttr('rightShader', dt = 'string')
            self.networkNode.addAttr('centerShader', dt = 'string')
            self.networkNode.setAttr('forwardDirection', forwardDirection, f=1)
            connectToMeta(meshGrp, self.networkNode, 'meshGrp')
            connectToMeta(bindGrp, self.networkNode, 'bindGrp')
            connectToMeta(topCon, self.networkNode, 'topCon')
            connectToMeta(compGrp, self.networkNode, 'compGrp')
    
    def addSmoothToTopCon(self):
        topCon = self.getTopCon()
        topCon.addAttr("smooth", dv = 0, min = 0, max = 1, keyable = 0)
        setAttr(topCon + ".smooth", cb=True)
        meshes = self.getAllMeshes()
        for mesh in meshes:
            connections = mesh.getShape().listConnections(type="polySmoothFace")
            if (len(connections) > 0):
                connectAttr(topCon + ".smooth", connections[0] + ".divisions")
    
    def setRenderAttrs(self):
        for anim in self.getAllAnims():
            shape = anim.getShape()
            if shape:
                setAttr(shape + '.primaryVisibility', 0)
                setAttr(shape + '.castsShadows', 0)
                setAttr(shape + '.receiveShadows', 0)
                setAttr(shape + '.visibleInReflections', 0)
                setAttr(shape + '.visibleInRefractions', 0)
                for attr in ['miTransparencyCast', 'miTransparencyReceive', 'miReflectionReceive', 'miRefractionReceive', 'miFinalGatherCast', 'miFinalGatherReceive']:
                    if objExists(shape + '.' + attr):
                        setAttr(shape + '.' + attr, 0)

    def getAllMeshes(self):
        '''
        returns a list of all connected meshes
        '''
        allMeshes = self.networkNode.meshes.listConnections()
        return allMeshes
        
        
    def getLeftSideDirection(self):
        '''
        get the direction of the characters side
        return: 
            (-)(x,y,z)
        '''
        allOptions = {
        ('x', 'y'): "-z",
        ('x', '-y'): "z",
        ('x', 'z'): "y",
        ('x', '-z'): "z",
        ('-x', 'y'): 'z',
        ('-x', '-y'): '-z',
        ('-x', 'z'): '-y',
        ('-x', '-z'): 'y',
        ('y', 'x'): "z",
        ('y', '-x'): "-z",
        ('y', 'z'): "-x",
        ('y', '-z'): "x",
        ('-y', 'x'): '-z',
        ('-y', '-x'): 'z',
        ('-y', 'z'): 'x',
        ('-y', '-z'): '-x',
        ('z', 'x'): "-y",
        ('z', '-x'): "y",
        ('z', 'y'): "x",
        ('z', '-y'): "-x",
        ('-z', 'x'): 'y',
        ('-z', '-x'): '-y',
        ('-z', 'y'): '-x',
        ('-z', '-y'): 'x'
        }    
        
        return allOptions[(self.getForwardDirection(), self.getUpDirection())]
    
    def addMesh(self, mesh):
        '''
        add a mesh to the character rig, a mesh is a mesh to bind to joints
        mesh:
            mesh to bind at later time
        '''
        if not objExists(mesh):
            raise Exception("CharacterRig.addMesh: mesh obj , %s ,doesn't exist"%mesh)
        parent(mesh, self.networkNode.meshGrp.listConnections()[0])
        # setAttr(mesh + '.overrideEnabled', 1)
        # setAttr(mesh + '.overrideDisplayType', 2)
        connectToMeta(mesh, self.networkNode, 'meshes')
                    
    def addRigComponent(self, rigComponent):
        '''
        connects the rigComponent to the character and parent it under the component group
        rigComponent:
            the rigComponent to connect
        '''
        connectToMeta(rigComponent.networkNode,self.networkNode, 'rigComponents')
        rigComponent.parentUnder(self.networkNode.compGrp.listConnections()[0])
        
    def getCharacterName(self):
        '''
        returns the name of the character
        '''
        return self.networkNode.characterName.get()
    
    def getUpDirection(self):
        '''
        return the axis of the characters up direction
        return:
            string (-)(x,y,z)
        '''
        return self.networkNode.upDirection.get()
        
    def getForwardDirection(self):
        '''
        return the axis of the characters forward direction
        return:
            string (-)(x,y,z)
        '''
        return self.networkNode.forwardDirection.get()
    
    def getOppositeComponent(self, comp):
        '''
        get the opposite component of component given
        '''
        if not comp.getCharacterRig() == self:
            raise Exception("CharacterRig.getOppositeComponent: component, %s, doesn't belong to this character rig")
        side = comp.networkNode.side.get().lower()
        bodyPart = comp.networkNode.bodyPart.get().lower()
        if side == 'center':
            return comp
        else:
            allComps = self.networkNode.rigComponents.listConnections()
            for c in allComps:
                otherSide = c.side.get().lower()
                otherBodyPart = c.bodyPart.get().lower()
                if otherBodyPart == bodyPart:
                    if otherSide == 'left' and side == 'right':
                        return fromNetworkToObject(c)
                    elif otherSide == 'right' and side == 'left':
                        return fromNetworkToObject(c)
        return comp
        
    def getAllRigComponents(self):
        '''
        returns a list of all the rigComponents
        '''
        allComps = self.networkNode.rigComponents.listConnections()
        allComps = map(lambda x: fromNetworkToObject(x), allComps)
        return allComps
                
    def getTopCon(self):
        '''
        returns the topCon anim
        '''
        return self.networkNode.topCon.listConnections()[0]
        
    def getAllAnims(self, side = ""):
        '''
        returns a list of all the anims associate with this rig
        '''
        components = self.networkNode.rigComponents.listConnections()
        components = map(lambda x: fromNetworkToObject(x), components)
        components = filter(lambda x: isinstance(x, RigComponent), components) # Filter out non rig components
        allAnims = []
        if side:
            for comp in components:
                if comp.getSide().lower() == side:
                    anims = comp.getAllAnims()
                    map(lambda x: allAnims.append(x), anims)
            #if side == "center":
            #    allAnims.append(self.getTopCon())
            return allAnims
        else:
            for comp in components:
                compAnims = comp.getAllAnims()
                for anim in compAnims:
                    allAnims.append(anim)
            allAnims.append(self.getTopCon())
            return allAnims
        
    def keyAllAnims(self):
        '''
        keys all the anims in the rig but the topCon
        '''
        anims = self.getAllAnims()
        for anim in anims:
            if not anim == self.getTopCon():
                setKeyframe(anim)
            
    def selectAllAnims(self):
        '''
        selects all the anims of the rig but the topCon
        '''
        select(clear = 1)
        anims = self.getAllAnims()
        for anim in anims:
            if not anim == self.getTopCon():
                select(anim, add=1)
    
    def toDefaultPose(self):
        '''
        moves the character to the placement of initial rig
        '''
        allComps = self.getAllRigComponents()
        for comp in allComps:
            comp.toDefaultPose()
            
    def mirrorPose(self):
        '''
        mirrors the whole character
        '''
        components = self.getAllRigComponents()
        notComps = []
        for comp in components:
            if not comp in notComps:
                try:
                    comps = comp.mirror(bothSides=1)
                    for x in comps:
                        notComps.append(x)
                except:
                    print "Could not mirror"+str(comp)

    def mirrorComponentSide(self, component):
        '''
        mirrors the side that the component argument is on
        '''
        compSide = component.networkNode.side.get().lower()
        components = self.getAllRigComponents()
        notComps = []
        for comp in components:
            if not comp in notComps and compSide == comp.networkNode.side.get().lower():
                try:
                    comps = comp.mirror(bothSides=0)
                    for x in comps:
                        notComps.append(x)
                except:
                    print "Could not mirror"+str(comp)
                    
    def createLayer(self, layerName, objs, template = 0, visible = 1, reference = 0):
        '''
        creates a display layer for the rig, and connects it to the rig for tracking
        '''
        select(objs)
        layer = createDisplayLayer(name = self.networkNode.characterName.get() + "_" + layerName, nr=1)
        layer.visibility.set(visible)
        if reference:
            layer.displayType.set(2) 
        else:
            if template:
                layer.displayType.set(1)
        connectChainToMeta([layer], self.networkNode, 'layers')
        
    def exportAnims(self, folder):
        '''
        exports all the anims to a folder for faster creation later
        '''
        for x in self.getAllAnims():
            if hasAnimAttr(x) or True:
                print "exporting:", x
                name = x.name()
                grp = group(empty=1, name = name)
                alignPointOrient(x, grp,1,1)
                appendShape(x, grp)
                select(grp)
                hyperShade(assign = "lambert1")
                select(grp)
                exportPath = folder + "/" + name + ".ma"
                rt.ConvertInstanceToObject(grp)
                try:
                    exportSelected(exportPath,f=1, typ = "mayaAscii")
                except:
                    print("***ERROR*** exportAnims: unable to save file %s"%exportPath)
                    print("continuing")
                delete(grp)
                select(cl=1)
            
    def importAnims(self, folder):
        '''
        imports all anims from a folder
        '''
        for x in self.getAllAnims():
            name = x.name()
            name = name[name.rfind("|") + 1:]

            if not os.path.isdir(folder):
                printError("rig.importAnims: %s is not a directory"%folder)
            fileName = folder + "/" + name + ".ma"
            if not os.path.exists(fileName):
                print("rig.importAnims: no file matched for %s"%name)
            else:
                newNodes = importFile(fileName, f=1, returnNewNodes =1, defaultNamespace =1)
                goodNodes = []
                
                for y in newNodes:
                    if y.type() == 'transform':
                        if y.getShape():
                            goodNodes.append(y)
                            goodNodes.append(y.getShape())
                
                if len(goodNodes) < 2:
                    continue
                    
                """
                newNodes.remove(goodNodes[0])
                newNodes.remove(goodNodes[1])
                """
                
                newObj = goodNodes[0]
                
                """
                alignPointOrient(x, newObj,1,1)
                addRot = x.rotateAxis.get()
                rotate(newObj, addRot, os =1, r=1)
                makeIdentity(newObj, apply =1, t=1, r=1, s=1)
                """
                
                swapShapes(x, newObj)
                delete(newObj)
                
                
    def importAnimsFromFile(self, filePath, apr=3):
        '''
        Replaces anims of character with shapes from the specified file.
        
        filePath:
            File to seek out shapes from.
            
        apr:
            "Anims Per Refresh", number of anims to generate before doing a screen refresh
        '''

        if not os.path.isfile(filePath):
            raise Exception('importAnimsFromFile: Anims file "'+filePath+'" does not exist.')
        
        try:
            fileRef = createReference(filePath, namespace='')
        except:
            raise Exception('importAnimsFromFile: Error referencing anims file "'+filePath+'"')
        ns = fileRef.namespace
        hide(filter(lambda n: isinstance(n, nt.Transform), fileRef.nodes()))
        
        animCounter = 0
        for a in self.getAllAnims():
            animName = a.name()
            animName = animName[animName.rfind("|") + 1:]
            
            # Search for transform that matches the anim name
            newShapeSearch = ls(ns+':'+animName)
            if (len(newShapeSearch) < 1):
                print('importAnimsFromFile: WARNING: No anim shapes found for '+animName)
                continue
                
            if (len(newShapeSearch) > 1):
                print('importAnimsFromFile: WARNING: Multiple possible new shapes found for '+animName+'. Skipping.')
                continue
            
            # Check for shapes
            newShapeTransform = newShapeSearch[0]
            if (not isinstance(newShapeTransform, nt.Transform) or (len(newShapeTransform.getShapes())  < 1)):
                print('importAnimsFromFile: WARNING: No shapes found under the matching transform for '+animName)
                continue
            
            # Remove old shapes
            delete(a.getShapes())
            
            # Duplicate over new shapes
            for s in newShapeTransform.getShapes():
                ds = duplicate(s, addShape=1)
                parent(ds, a, shape=1, r=1)
                
            # Refresh screen
            animCounter += 1
            if ((animCounter % apr) == 0): refresh()
            
        fileRef.remove()
        refresh()

                
        
    def createShader(self, side, color= [1,0,0], opacity = .5, apply = 0):
        '''
        creates shaders and connects to metaNode
        return the material created
        '''
        side = side.lower()
        topCon = self.getTopCon()
        if not topCon.hasAttr("animOpacity"):
            topCon.addAttr("animOpacity")
            topCon.animOpacity.setMax(1)
            topCon.animOpacity.setMin(0)
        topCon.animOpacity.set(opacity)
        setAttr(topCon.animOpacity, k=0, cb=1)
        if side in ('left', 'right', 'center'):
            shader = shadingNode('lambert', asShader=1, n = '%s_%s_anim_mat'%(self.getCharacterName(), side));
            shader.color.set(color)
            topCon.animOpacity >> shader.transparency.transparencyR
            topCon.animOpacity >> shader.transparency.transparencyG
            topCon.animOpacity >> shader.transparency.transparencyB
            connectToMeta(shader, self.networkNode, '%sShader'%side)
            if apply:
                select(self.getAllAnims(side))
                if side == "center":
                    shp = self.getTopCon().getShape()
                    if shp:
                        select(shp, add=1)
                hyperShade(assign = shader)
                select(cl=1)
        else:
            printError("side given isn't valid")
            
class RigComponent(MetaNode):
    def __init__(self, metaType, metaVersion, metaDescription, side, bodyPart, startJoint = "", endJoint = ""):
        '''
        metaType:
            the type of rig Component
        metaVersion:
            what version is the component in
        metaDescription:
            a brief description of what the metaComponent does
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        MetaNode.__init__( self, metaType, metaVersion, metaDescription)
        self.networkNode.setAttr('side', side, f=1)
        self.networkNode.setAttr('bodyPart', bodyPart, f=1)
        if startJoint:
            connectToMeta(startJoint, self.networkNode, 'startJoint')
        if endJoint:
            connectToMeta(endJoint, self.networkNode, 'endJoint')
        if startJoint == endJoint and startJoint != "" and endJoint != "":
            raise Exception('RigComponent: endJoint == startJoint')
        
    def getSide(self):
        '''
        returns the side of the rigComponent
        '''
        return self.networkNode.side.get()
        
    def getBodyPart(self):
        '''
        returns the body Part of the rigComponent
        '''
        return self.networkNode.bodyPart.get()
    
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        pass
        
    def getCharacterRig(self):
        '''
        Get the character Rig node that this component belongs to
        '''
        metaType = self.networkNode.metaType.get()
        node = self.networkNode
        while metaType != 'CharacterRig':
            if node == None:
                return None
            try:
                newNode = node.metaParent.listConnections()[0]
                node = newNode
            except:
                node = None
            try:
                metaType = node.metaType.get()
            except:
                metaType = "None"
        return CharacterRig('','','',node = node)
                    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        raise Exception("can't connect this component connectToComponent() not implemented, %s"%self.networkNode.metaType.get())
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        raise Exception("can't connect to this component getConnectObj() not implemented, %s"%self.networkNode.metaType.get())
    
    def isIK(self):
        '''
        returns true if component has an IK chain, else false
        '''
        return False
    
    def getIK(self):
        '''
        returns the IK handle
        '''
        return None
        
    def isFK(self):
        '''
        returns true if component has an fk chain
        '''
        return False
    
    def getFK(self):
        '''
        return the jk joints
        '''
        try:
            return self.networkNode.FKJoints.listConnections()    
        except:
            return None
        
    def isSwitch(self):
        '''
        return True if component switches between two types of chains
        '''
        return None
            
    def getBindJoints(self):
        '''
        return the joints which should be bound to
        '''
        try:
            return self.networkNode.bindJoints.listConnections()
        except:
            return None 
    
    def parentUnder(self, obj):
        '''
        parent this rigComponent under the obj
        obj:
            object to parent under
        '''
        if not objExists(obj):
            raise Exception("RigComponent: can't parent under $s, obj doesn't exist"%obj)
        try:
            parent(self.networkNode.componentGrp.listConnections()[0], obj)
        except:
            raise Exception("%s.parentUnder: not implemented"%self.networkNode.metaType.get())
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return None
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        pass
            
    def __str__(self):
        node = self.networkNode
        return "%s:: %s %s, %s"%(node.metaType.get(), node.side.get(), node.bodyPart.get(), node.name())

        
class AnimGroup(RigComponent):

    def __init__(self, animObjects, node = ''):
        '''
        Flags a collection of pre-existing objects as animation controls.
        '''
    
        # REQUISITE META SETUP
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'AnimGroup'):
                    self.networkNode = node
                else:
                    printError("AnimGroup: node %s is not a AnimGroup metaNode"%(node))
            else:
                printError("AnimGroup: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        
        # Initiate the component
        RigComponent.__init__(self, 'AnimGroup', 1.0, 'Flags existing objects as anims', '', '')

        
        # SET UP COMPONENT
        
        # Check for objects
        if (len(animObjects) == 0): raise Exception('AnimGroup: Please specify objects to use as animation controls.')
        
        # Register objects as animation controls
        for obj in animObjects:
            addAnimAttr(obj)
            
        # Register anim list with the meta node
        connectChainToMeta(animObjects, self.networkNode, 'anims')
        
        
    def getAllAnims(self):
        '''
        Returns a list of all the anims
        '''
        return self.networkNode.anims.listConnections()
        
    def parentUnder(self, obj):
        '''
        This component is just organizational and has no transforms available for parenting
        '''
        pass
        
class FKChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = '', stretchy = 0, baseOrient = False, orientTarget = None):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        baseOrient:
            Orient all anims with the base
        orientTarget:
            Use orient of target transform, superseded by baseOrient if True
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKChain'):
                    self.networkNode = node
                else:
                    printError("FKChain: node %s is not a FKChain metaNode"%(node))
            else:
                printError("FKChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKChain', 1.0, 'chain of FK Joints', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            compName = '%s_%s'%(side, bodyPart)
            for item in chain:
                item = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
            0
            fk_joints = duplicateChain(bind_joints[0],bind_joints[-1], 'bind', 'FK')
            
            if(baseOrient):
                for inc in xrange(len(fk_joints)-1):
                    obj = fk_joints[inc]
                    if(inc < len(fk_joints)-1):
                        child = fk_joints[inc+1]
                        parent(child, w = 1, a = True)
                        alignPointOrient(fk_joints[0], obj, point = False, orient = True)
                        makeIdentity(obj, rotate = True, apply = True)
                        parent(child, obj, a = True)
                        
            elif(orientTarget != None and isinstance(orientTarget, nt.Transform)):
                for inc in xrange(len(fk_joints)-1):
                    obj = fk_joints[inc]
                    if(inc < len(fk_joints)-1):
                        child = fk_joints[inc+1]
                        parent(child, w = 1, a = True)
                        alignPointOrient(orientTarget, obj, point = False, orient = True)
                        makeIdentity(obj, rotate = True, apply = True)
                        parent(child, obj, a = True)
                        
            
            for inc in xrange(len(fk_joints)-1):
                obj = fk_joints[inc]
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
                addAnimAttr(obj)
                obj.rename('%s_%i_anim'%(compName, inc+1))
            
            globalMultiplier = createNode('multiplyDivide')
            if stretchy:
                #create stretch attr
                fk_joints[-2].addAttr("stretch", dv = 1, min = .000001, keyable =1)
                for x in fk_joints[:-2]:
                    x.addAttr("stretch", dv = 1, min = .000001, keyable = 1)
                    fk_joints[-2].stretch >> x.stretch
                    x.stretch.lock()
                
                #create basic setup with calc nodes
                    #multipler
                fk_joints[-2].stretch >> globalMultiplier.input1X
                globalMultiplier.input2X.set(1)

                #add stretchy to the FK joints
                for j in fk_joints[1:]:
                    jointMult = createNode('multiplyDivide')
                    orig = j.translateX.get()
                    jointMult.input1X.set(orig)
                    j.translateX.unlock()
                    globalMultiplier.outputX >> jointMult.input2X
                    jointMult.outputX >> j.translateX
                
                
            #rename if there is only one anim
            if len(fk_joints) == 2:
                fk_joints[0].rename("%s_anim"%(compName))
                
            if baseOrient or (orientTarget != None and isinstance(orientTarget, nt.Transform)):
                mo = True
            else:
                mo = False
            for inc in xrange(len(bind_joints)-1):
                parentConstraint(fk_joints[inc], bind_joints[inc], w=1, mo=mo)
                
            #grouping
            select(cl=1)
            animGrp = group(fk_joints[0], n = "%s_anim_grp"%compName)
            mainGrp = group([animGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
                
            #connectToMeta
            self.networkNode.setAttr('stretchy', stretchy,  f=1)
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
            select(cl=1)
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
    
    
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.FKJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.FKJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            for inc in xrange(len(fk_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return fk_joints[inc]
                if location == fk_joints[inc]:
                    return fk_joints[inc]
        raise Exception("FKChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or fk joint ")

    def isFK(self):
        return True
        
    def getAnims(self):
        '''
        returns all the anims associated with the FK chain
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            for anim in self.getAnims():
                rot = anim.rotate.get()
                anim.rotate.set(-rot[0],-rot[1],rot[2])
            return [self]
        else:
            allAnims = self.getAnims()
            allRots = []
            map(lambda x: allRots.append(x.rotate.get()), allAnims)
            if bothSides:
                otherAnims = other.getAnims()
                otherRots = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    inc += 1
                inc = 0
                for anim in otherAnims:
                    anim.rotate.set(allRots[inc])
                    inc+=1
                return [self, other]
            else:
                otherAnims = other.getAnims()
                otherRots = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    inc += 1
                return [self]
                
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return self.getAnims()
    
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        anims = self.getAllAnims()
        for anim in anims:
            resetAttrs(anim)
            
class FKFloatChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = '', stretchy = 0, baseOrient = False):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        baseOrient:
            Orient all anims with the base
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKFloatChain'):
                    self.networkNode = node
                else:
                    printError("FKFloatChain: node %s is not a FKFloatChain metaNode"%(node))
            else:
                printError("FKFloatChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKFloatChain', 1.0, 'chain of FK Joints with a floating end connector', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            compName = '%s_%s'%(side, bodyPart)
            for item in chain:
                item = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
            
            fk_joints = duplicateChain(bind_joints[0],bind_joints[-1], 'bind', 'FK')
            
            if(baseOrient):
                for inc in xrange(len(fk_joints)-1):
                    obj = fk_joints[inc]
                    if(inc < len(fk_joints)-1):
                        child = fk_joints[inc+1]
                        parent(child, w = 1, a = True)
                        alignPointOrient(fk_joints[0], obj, point = False, orient = True)
                        makeIdentity(obj, rotate = True, apply = True)
                        parent(child, obj, a = True)
                        
                        
            
            for inc in xrange(len(fk_joints)-1):
                obj = fk_joints[inc]
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
                addAnimAttr(obj)
                obj.rename('%s_%i_anim'%(compName, inc+1))
            
            globalMultiplier = createNode('multiplyDivide')
            if stretchy:
                #create stretch attr
                fk_joints[-2].addAttr("stretch", dv = 1, min = .000001, keyable =1)
                for x in fk_joints[:-2]:
                    x.addAttr("stretch", dv = 1, min = .000001, keyable = 1)
                    fk_joints[-2].stretch >> x.stretch
                    x.stretch.lock()
                
                #create basic setup with calc nodes
                    #multipler
                fk_joints[-2].stretch >> globalMultiplier.input1X
                globalMultiplier.input2X.set(1)

                #add stretchy to the FK joints
                for j in fk_joints[1:]:
                    jointMult = createNode('multiplyDivide')
                    orig = j.translateX.get()
                    jointMult.input1X.set(orig)
                    j.translateX.unlock()
                    globalMultiplier.outputX >> jointMult.input2X
                    jointMult.outputX >> j.translateX
                
                
            #rename if there is only one anim
            if len(fk_joints) == 2:
                fk_joints[0].rename("%s_anim"%(compName))
                
            for inc in xrange(len(bind_joints)-1):
                parentConstraint(fk_joints[inc], bind_joints[inc], w=1, mo=baseOrient)
                
            #grouping
            select(cl=1)
            animGrp = group(fk_joints[0], n = "%s_anim_grp"%compName)
            mainGrp = group([animGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)

            # Create floating connection point
            fixedEnd = fk_joints[-1]
            floatEnd = duplicateChain(fixedEnd, fixedEnd, 'FK', 'Float')[0]
            parent(floatEnd, fixedEnd.getParent())
            floatEnd.inheritsTransform = False
            orientConstraint(mainGrp, floatEnd, mo=True)
            pointConstraint(fixedEnd,floatEnd,mo=True)

            #connectToMeta
            self.networkNode.setAttr('stretchy', stretchy,  f=1)
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
            connectChainToMeta([floatEnd],self.networkNode,'floatJoint')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
            select(cl=1)
            
            
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
    
    
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.FKJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.FKJoints.listConnections()[-1]
        elif location == 'float':
            return self.networkNode.floatJoint.listConnections()[0]
        else: # an object
            if not objExists(location):
                raise Exception("FKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            if location == self.networkNode.floatJoint.listConnections()[0]:
                return self.networkNode.floatJoint.listConnections()[0]
            bind_joints = self.networkNode.bindJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            for inc in xrange(len(fk_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return fk_joints[inc]
                if location == fk_joints[inc]:
                    return fk_joints[inc]
        raise Exception("FKFloatChain.getConnectObj: location wasn't found, try 'start', 'end', 'float' or name of bind or fk joint ")

    def isFK(self):
        return True
        
    def getAnims(self):
        '''
        returns all the anims associated with the FK chain
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            for anim in self.getAnims():
                rot = anim.rotate.get()
                anim.rotate.set(-rot[0],-rot[1],rot[2])
            return [self]
        else:
            allAnims = self.getAnims()
            allRots = []
            map(lambda x: allRots.append(x.rotate.get()), allAnims)
            if bothSides:
                otherAnims = other.getAnims()
                otherRots = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    inc += 1
                inc = 0
                for anim in otherAnims:
                    anim.rotate.set(allRots[inc])
                    inc+=1
                return [self, other]
            else:
                otherAnims = other.getAnims()
                otherRots = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    inc += 1
                return [self]
                
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return self.getAnims()
    
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        anims = self.getAllAnims()
        for anim in anims:
            resetAttrs(anim)
            
class COGChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = '', worldOrient = 0, stretchy = 0):
        '''
        side:
            The side is this component on, ex. center, left, right.
        bodyPart:
            The body part the component is for, ex. arm, leg, clavicle, foot.
        startJoint:
            The place where the component starts.
        endJoint:
            The place where the component ends.
		stretchy:
			Wasn't documented.  Dunno.
		worldOrient:
			Align all COG chain joints to world space.  Assumes two joint chain, not tested for beyond that.
		
        note, similar to FKChain but doesn't constrain the start joint, and also allows for translation
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'COGChain'):
                    self.networkNode = node
                else:
                    printError("COGChain: node %s is not a COGChain metaNode"%(node))
            else:
                printError("COGChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'COGChain', 1.0, 'center of gravity component', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            compName = '%s_%s'%(side, bodyPart)
            for item in chain:
                item = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
            
            fk_joints = duplicateChain(bind_joints[0],bind_joints[-1], 'bind', 'FK')

            if worldOrient:
                makeIdentity(fk_joints, r=1, jo=1, a=1)

            for inc in xrange(len(fk_joints)-1):
                obj = fk_joints[inc]
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, ['sx', 'sy', 'sz', 'radius'])
                addAnimAttr(obj)
                obj.rename('%s_%i_anim'%(compName, inc+1))
                
            
            
            globalMultiplier = createNode('multiplyDivide')
            if stretchy:
                #create stretch attr
                fk_joints[-2].addAttr("stretch", dv = 1, min = .000001, keyable =1)
                for x in fk_joints[:-2]:
                    x.addAttr("stretch", dv = 1, min = .000001, keyable = 1)
                    fk_joints[-2].stretch >> x.stretch
                    x.stretch.lock()
                
                #create basic setup with calc nodes
                    #multipler
                fk_joints[-2].stretch >> globalMultiplier.input1X
                globalMultiplier.input2X.set(1)

                #add stretchy to the FK joints
                for j in fk_joints[1:]:
                    jointMult = createNode('multiplyDivide')
                    orig = j.translateX.get()
                    jointMult.input1X.set(orig)
                    j.translateX.unlock()
                    globalMultiplier.outputX >> jointMult.input2X
                    jointMult.outputX >> j.translateX
                
                
            #rename if there is only one anim
            if len(fk_joints) == 2:
                fk_joints[0].rename("%s_anim"%(compName))
                
            #for inc in xrange(len(bind_joints)-1):
            #    parentConstraint(fk_joints[inc], bind_joints[inc], w=1)
                
            #grouping
            zeroGrp = createZeroedOutGrp(fk_joints[0])
            select(cl=1)
            animGrp = group(zeroGrp, n = "%s_anim_grp"%compName)
            mainGrp = group([animGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
                
            #connectToMeta
            self.networkNode.setAttr('stretchy', stretchy,  f=1)
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
            select(cl=1)
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
    
    
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.FKJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.FKJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            for inc in xrange(len(fk_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return fk_joints[inc]
                if location == fk_joints[inc]:
                    return fk_joints[inc]
        raise Exception("FKChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or fk joint ")

    def isFK(self):
        return True
        
    def getAnims(self):
        '''
        returns all the anims associated with the FK chain
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            for anim in self.getAnims():
                rot = anim.rotate.get()
                anim.rotate.set(-rot[0],-rot[1],rot[2])
            return [self]
        else:
            allAnims = self.getAnims()
            allRots = []
            map(lambda x: allRots.append(x.rotate.get()), allAnims)
            if bothSides:
                otherAnims = other.getAnims()
                otherRots = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    inc += 1
                inc = 0
                for anim in otherAnims:
                    anim.rotate.set(allRots[inc])
                    inc+=1
                return [self, other]
            else:
                otherAnims = other.getAnims()
                otherRots = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    inc += 1
                return [self]
                
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return self.getAnims()
    
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        anims = self.getAllAnims()
        for anim in anims:
            resetAttrs(anim)
            
class SingleIKChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = ''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'SingleIKChain'):
                    self.networkNode = node
                else:
                    printError("SingleIKChain: node %s is not a SingleIKChain metaNode"%(node))
            else:
                printError("SingleIKChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'SingleIKChain', 1.0, 'singlechain(SC) IK solver chain', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            compName = '%s_%s'%(side, bodyPart)
            for item in chain:
                item = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
                    
            ik_joints = duplicateChain(bind_joints[0],bind_joints[-1], 'bind', 'IK')
            
            anims = []
            zeroGrps = []
            for inc in xrange(len(ik_joints)-1):
                base = ik_joints[inc]
                top = ik_joints[inc+1]
                #create Anim
                select(clear=1)
                anim = joint(n = '%s_%i_anim'%(compName, inc+1))
                alignPointOrient(top, anim, 1,1)
                zeroGrp = createZeroedOutGrp(anim)
                addAnimAttr(anim)
                cube = polyCube()[0]
                appendShape(cube, anim)
                delete(cube)
                parentConstraint(anim, top, w=1)
                lockAndHideAttrs(anim, ['sx','sy','sz','v','radius'])
                zeroGrps.append(zeroGrp)
                anims.append(anim)
                
            #rename if there is only one anim
            if len(ik_joints) == 2:
                anims[0].rename("%s_anim"%(compName))
                
            for inc in xrange(len(bind_joints)-1):#not the first joint
                parentConstraint(ik_joints[inc+1], bind_joints[inc+1], w=1)
                
            #grouping
            select(cl=1)
            animGrp = group(zeroGrps, n="%s_anim_grp"%compName)
            jointGrp = group(ik_joints[0], n = "%s_joint_grp"%compName)
            mainGrp = group([animGrp, jointGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
                
            #connectToMeta
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(ik_joints, self.networkNode, 'IKJoints')
            connectChainToMeta(anims, self.networkNode, 'anims' )
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
            select(cl=1)
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.IKJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.IKJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("SingleIKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            ik_joints = self.networkNode.IKJoints.listConnections()
            for inc in xrange(len(ik_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return ik_joints[inc]
                if location == ik_joints[inc]:
                    return ik_joints[inc]
        raise Exception("FKChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or ik joint ")

    def isIK(self):
        return True
        
    def getAnims(self):
        '''
        returns all the anims associated with the FK chain
        '''
        return self.networkNode.anims.listConnections()
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:  
            for anim in self.getAnims():
                rot = anim.rotate.get()
                anim.rotate.set(-rot[0],-rot[1],rot[2])
                anim.translateX.set(-anim.translateX.get())
            return [self]
        else:
            allAnims = self.getAnims()
            allRots = []
            allTrans = []
            map(lambda x: allRots.append(x.rotate.get()), allAnims)
            map(lambda x: allTrans.append(x.translate.get()), allAnims)
            if bothSides:
                otherAnims = other.getAnims()
                otherRots = []
                otherTrans = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                map(lambda x: otherTrans.append(x.translate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    anim.translate.set(-otherTrans[inc])
                    inc += 1
                inc = 0
                for anim in otherAnims:
                    anim.rotate.set(allRots[inc])
                    anim.translate.set(-allTrans[inc])
                    inc+=1
                return [self, other]
            else:
                otherAnims = other.getAnims()
                otherRots = []
                otherTrans = []
                map(lambda x: otherRots.append(x.rotate.get()), otherAnims)
                map(lambda x: otherTrans.append(x.translate.get()), otherAnims)
                inc = 0
                for anim in allAnims:
                    anim.rotate.set(otherRots[inc])
                    anim.translate.set(-otherTrans[inc])
                    inc += 1
                return [self]
                
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return self.getAnims()
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        anims = self.getAllAnims()
        for anim in anims:
            resetAttrs(anim)

class ReverseChain(RigComponent):
    
    def __init__(self, side, bodyPart, startJoint, endJoint, node = ''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'ReverseChain'):
                    self.networkNode = node
                else:
                    printError("ReverseChain: node %s is not a ReverseChain metaNode"%(node))
            else:
                printError("ReverseChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'ReverseChain', 1.0, 'creates FK Joint that rotates from the Joints child Node', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            bind_joints = []
            for item in chain:
                item = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
            if not len(bind_joints) == 2:
                raise Exception('ReverseChain.__init__: should only have 2 joints ')
            
            #create control chain
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
            
            
            #create reverse Joints
            select(cl=1)
            piv_pos = bind_joints[-1].getTranslation(space = 'world')
            rot_pos = bind_joints[0].getTranslation(space = 'world')
            rev_piv_joint = joint(p = piv_pos)
            rev_rot_joint = joint(p = rot_pos, n = "%s_rot_joint"%compName)
            joint(rev_piv_joint, e=1, zso=1, oj='xyz', sao='yup')
            
            #make pivot joint into anim
            addBoxToJoint(rev_piv_joint)
            lockAndHideAttrs(rev_piv_joint, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
            addAnimAttr(rev_piv_joint)
            rev_piv_joint.rename('%s_anim'%compName)        
            
            #parent Constrain to control and bind joints
            parentConstraint(rev_rot_joint, control_joints[0],mo=1,w=1)
            
            for inc in xrange(len(bind_joints)-1):
                parentConstraint(control_joints[inc], bind_joints[inc])
            
            #grouping
            select(cl=1)
            jointGrp = group([control_joints[0], rev_piv_joint],n='%s_joint_grp'%compName)
            dntGrp = group(empty =1 , n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            #hide extra junk
            dntGrp.hide()
            control_joints[0].hide()
                    
            
            #connect To Meta
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectToMeta(rev_rot_joint, self.networkNode, 'rotateJoint')
            connectToMeta(rev_piv_joint, self.networkNode, 'reverseAnim')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            connectToMeta(dntGrp, self.networkNode, 'doNotTouchGrp')
            
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
        
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("ReverseChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            for inc in xrange(len(fk_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
        raise Exception("ReverseChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or control joint ")
        
    def isFK(self):
        return True
        
    def getAnim(self):
        '''
        returns the reverse anim
        '''
        return self.networkNode.reverseAnim.listConnections()[0]
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            anim = self.getAnim()
            rot = anim.rotate.get()
            anim.rotate.set(-rot[0],-rot[1],rot[2])
            return [self]
        else:
            anim = self.getAnim()
            rot = anim.rotate.get()
            if bothSides:
                otherAnim = other.getAnim()
                otherRot = otherAnim.rotate.get()
                anim.rotate.set(otherRot)
                otherAnim.rotate.set(rot)
                return [self, other]
            else:
                otherAnim = other.getAnim()
                otherRot = otherAnim.rotate.get()
                anim.rotate.set(otherRot)
                return [self]
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return [self.getAnim()]
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        resetAttrs(self.getAnim())

class IKLips(RigComponent):
    def __init__(self,upperLeft, upperRight, lowerLeft, lowerRight, side, bodyPart,startJoint, endJoint, node = ''):
        '''
        upperLeft:
            the joints in the upper Left section of the mouth, starting from upperCenter
        upperRight:
            the joints in the upper Right sectio of the mouth, starting from upper Center
        lowerLeft:
            the joints in the lower left section of the mouth, starting from the lower center
        lowerRight:
            the joints in the lower right section of the mouth, starting from the lower center
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'IKLips'):
                    self.networkNode = node
                else:
                    printError("IKLips: node %s is not a IKLips metaNode"%(node))
            else:
                printError("IKLips: node %s doesn't exist"%(node))
        
        else:
            
            RigComponent.__init__(self, 'IKLips', 1.0, 'a ik component with tweaks for animating around a hole',side, bodyPart, startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            
            #error testing
            upperRight = map(lambda x: PyNode(x), upperRight)
            upperLeft = map(lambda x: PyNode(x), upperLeft)
            lowerRight = map(lambda x: PyNode(x), lowerRight)
            lowerLeft = map(lambda x: PyNode(x), lowerLeft)
            
            #create initial groups
            jointGrp = group(empty = 1, n='%s_joint_grp'%compName)
            animGrp = group(empty = 1, n = "%s_anim_grp"%compName)
            dntGrp = group(empty =1, n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            
            #hide some
            dntGrp.visibility.set(0)
            
            #make single ik chains for each joint
            allJoints = []
            tweakAnims = []
            orig_singleIKZeroGrps = {}
            for x in upperLeft:
                if not x in allJoints:
                    allJoints.append(x)
            for x in upperRight:
                if not x in allJoints:
                    allJoints.append(x)
            for x in lowerLeft:
                if not x in allJoints:
                    allJoints.append(x)
            for x in lowerRight:
                if not x in allJoints:
                    allJoints.append(x)
            for j in allJoints:
                ikChain = duplicateChain(j.getParent(), j)
                ikChainCompName = j.name().split("_bind_joint")[0] + "_tweak"
                ret = createSingleIKChain(ikChain[0],ikChain[-1], ikChainCompName)
                tweakAnims.append(ret[0][0])
                orig_singleIKZeroGrps[j] = ret[1]
                parent(ret[2], animGrp)
                parent(ret[4], jointGrp)
                #connect the bind joints to the ik joints
                parentConstraint(ret[3][-1],j, w=1, mo=1)
            
            #make ik spline chain for each joint section
            URikSplineJoints = []
            orig_nurbsJoint = {}
            for inc in xrange(len(upperRight)):
                select(cl=1)
                j = upperRight[inc]
                ikSplineJoint = joint(n = j.name().replace('bind', 'ik_dummy'))
                orig_nurbsJoint[j] = ikSplineJoint
                alignPointOrient( j, ikSplineJoint, 1,1)
                if URikSplineJoints:
                    parent(ikSplineJoint, URikSplineJoints[inc-1])
                URikSplineJoints.append(ikSplineJoint)
            makeIdentity(URikSplineJoints[0], apply=1, t=0, r=1, s=0, n=0)
            joint(URikSplineJoints[0], e=1,oj= 'xyz', secondaryAxisOrient= 'yup', ch=1, zso=1);
            
            ULikSplineJoints = []
            for inc in xrange(len(upperLeft)):
                select(cl=1)
                j = upperLeft[inc]
                ikSplineJoint = joint(n = j.name().replace('bind', 'ik_dummy'))
                orig_nurbsJoint[j] = ikSplineJoint
                alignPointOrient( j, ikSplineJoint, 1,1)
                if ULikSplineJoints:
                    parent(ikSplineJoint, ULikSplineJoints[inc-1])
                ULikSplineJoints.append(ikSplineJoint)
            makeIdentity(ULikSplineJoints[0], apply=1, t=0, r=1, s=0, n=0)
            joint(ULikSplineJoints[0], e=1,oj= 'xyz', secondaryAxisOrient= 'yup', ch=1, zso=1);
            
            LRikSplineJoints = []
            for inc in xrange(len(lowerRight)):
                select(cl=1)
                j = lowerRight[inc]
                ikSplineJoint = joint(n = j.name().replace('bind', 'ik_dummy'))
                orig_nurbsJoint[j] = ikSplineJoint
                alignPointOrient( j, ikSplineJoint, 1,1)
                if LRikSplineJoints:
                    parent(ikSplineJoint, LRikSplineJoints[inc-1])
                LRikSplineJoints.append(ikSplineJoint)
            makeIdentity(LRikSplineJoints[0], apply=1, t=0, r=1, s=0, n=0)
            joint(LRikSplineJoints[0], e=1,oj= 'xyz', secondaryAxisOrient= 'yup', ch=1, zso=1);
            
            LLikSplineJoints = []
            for inc in xrange(len(lowerLeft)):
                select(cl=1)
                j = lowerLeft[inc]
                ikSplineJoint = joint(n = j.name().replace('bind', 'ik_dummy'))
                orig_nurbsJoint[j] = ikSplineJoint
                alignPointOrient( j, ikSplineJoint, 1,1)
                if LLikSplineJoints:
                    parent(ikSplineJoint, LLikSplineJoints[inc-1])
                LLikSplineJoints.append(ikSplineJoint)
            makeIdentity(LLikSplineJoints[0], apply=1, t=0, r=1, s=0, n=0)
            joint(LLikSplineJoints[0], e=1,oj= 'xyz', secondaryAxisOrient= 'yup', ch=1, zso=1);

            #make the ikNurbs plane chain for the upper left
            ULret = createOldNurbsPlaneIKChain(ULikSplineJoints[0],ULikSplineJoints[-1] , 'upper_left_lips')
            ULstartAnim = ULret[0]       #0, the ik anim that controls the start of the chain   
            ULmidAnim = ULret[1]        #1  the ik anim that controls the middle of the chain, note: parented contrained between start and end
            ULendAnim = ULret[2]        #2  the ik anim that controls the end of the chain
            parent(ULret[3], animGrp) # ret3 #animGrp,        #3  the grp created around the anims and their groups, note: reparent this group instead of the individual anims
            parent(ULret[4], jointGrp)
            parent(ULret[5], ULret[6], ULret[7], ULret[8], ULret[9], dntGrp)
            rename(ULret[5], compName+'_UL_surface')
            
            #make the ikNurbs plane chain for the upper right
            URret = createOldNurbsPlaneIKChain(URikSplineJoints[0],URikSplineJoints[-1] , 'upper_right_lips')
            URstartAnim = URret[0]       #0, the ik anim that controls the start of the chain   
            URmidAnim = URret[1]        #1  the ik anim that controls the middle of the chain, note: parented contrained between start and end
            URendAnim = URret[2]
            parent(URret[3], animGrp) # ret3 #animGrp,        #3  the grp created around the anims and their groups, note: reparent this group instead of the individual anims
            parent(URret[4], jointGrp)
            parent(URret[5], URret[6], URret[7], URret[8], URret[9], dntGrp)
            rename(URret[5], compName+'_UR_surface')
            
            #make the ikNurbs plane chain for the lower left
            LLret = createOldNurbsPlaneIKChain(LLikSplineJoints[0],LLikSplineJoints[-1] , 'lower_left_lips')
            LLstartAnim = LLret[0]       #0, the ik anim that controls the start of the chain   
            LLmidAnim = LLret[1]        #1  the ik anim that controls the middle of the chain, note: parented contrained between start and end
            LLendAnim = LLret[2]
            parent(LLret[3], animGrp) # ret3 #animGrp,        #3  the grp created around the anims and their groups, note: reparent this group instead of the individual anims
            parent(LLret[4], jointGrp)
            parent(LLret[5], LLret[6], LLret[7], LLret[8], LLret[9], dntGrp)
            rename(LLret[5], compName+'_LL_surface')
            
            #make the ikNurbs plane chain for the lower right
            LRret = createOldNurbsPlaneIKChain(LRikSplineJoints[0],LRikSplineJoints[-1] , 'lower_right_lips')
            LRstartAnim = LRret[0]       #0, the ik anim that controls the start of the chain   
            LRmidAnim = LRret[1]        #1  the ik anim that controls the middle of the chain, note: parented contrained between start and end
            LRendAnim = LRret[2]
            parent(LRret[3], animGrp) # ret3 #animGrp,        #3  the grp created around the anims and their groups, note: reparent this group instead of the individual anims
            parent(LRret[4], jointGrp)
            parent(LRret[5], LRret[6], LRret[7], LRret[8], LRret[9], dntGrp)
            rename(LRret[5], compName+'_LR_surface')
            
            #remove .animNode attributes from the ends of the nurbs anims
            URendAnim.animNode.delete()
            LRendAnim.animNode.delete()
            ULendAnim.animNode.delete()
            LLendAnim.animNode.delete()
            URstartAnim.animNode.delete()
            ULstartAnim.animNode.delete()
            LLstartAnim.animNode.delete()
            LRstartAnim.animNode.delete()
            
            #make extra anims for attaching corners and centers
                #right corner
            select(cl=1)
            rightMouthCornerAnim = joint(n = 'right_mouth_corner_anim')
            alignPointOrient(upperRight[-1], rightMouthCornerAnim, 1,1)
            rightMouthCornerZeroGrp = createZeroedOutGrp(rightMouthCornerAnim)
            addAnimAttr(rightMouthCornerAnim)
            cube = polyCube()[0]
            appendShape(cube, rightMouthCornerAnim)
            delete(cube)
            lockAndHideAttrs(rightMouthCornerAnim, [ 'v', 'radius', 'sx', 'sy', 'sz'])
            
                #left corner
            select(cl=1)
            leftMouthCornerAnim = joint(n = 'left_mouth_corner_anim')
            alignPointOrient(upperLeft[-1], leftMouthCornerAnim, 1,1)
            leftMouthCornerZeroGrp = createZeroedOutGrp(leftMouthCornerAnim)
            addAnimAttr(leftMouthCornerAnim)
            cube = polyCube()[0]
            appendShape(cube, leftMouthCornerAnim)
            delete(cube)
            lockAndHideAttrs(leftMouthCornerAnim, [ 'v', 'radius', 'sx', 'sy', 'sz'])
            
                #upper center
            select(cl=1)
            upperCenterAnim = joint(n = 'upper_lip_anim')
            alignPointOrient(upperLeft[0], upperCenterAnim, 1,1)
            upperCenterZeroGrp = createZeroedOutGrp(upperCenterAnim)
            addAnimAttr(upperCenterAnim)
            cube = polyCube()[0]
            appendShape(cube, upperCenterAnim)
            delete(cube)
            lockAndHideAttrs(upperCenterAnim, [ 'v', 'radius', 'sx', 'sy', 'sz'])
            
                #lower center
            select(cl=1)
            lowerCenterAnim = joint(n = 'lower_lip_anim')
            alignPointOrient(lowerLeft[0], lowerCenterAnim, 1,1)
            lowerCenterZeroGrp = createZeroedOutGrp(lowerCenterAnim)
            addAnimAttr(lowerCenterAnim)
            cube = polyCube()[0]
            appendShape(cube, lowerCenterAnim)
            delete(cube)
            lockAndHideAttrs(lowerCenterAnim, [ 'v', 'radius', 'sx', 'sy', 'sz'])
            
            #group main anims
            mainAnimGrp = group(upperCenterZeroGrp, lowerCenterZeroGrp, leftMouthCornerZeroGrp, rightMouthCornerZeroGrp, n= '%s_main_anims')
            parent(mainAnimGrp, animGrp)
            
            #make extra anims control other anims
                #right mouth corner
            parentConstraint(rightMouthCornerAnim, URendAnim, w=1, mo=1)
            parentConstraint(rightMouthCornerAnim, LRendAnim, w=1, mo=1) 
            URendAnim.visibility.unlock()
            LRendAnim.visibility.unlock()
            URendAnim.visibility.set(0)
            LRendAnim.visibility.set(0)
            
                #left mouth corner
            parentConstraint(leftMouthCornerAnim, ULendAnim, w=1, mo=1)
            parentConstraint(leftMouthCornerAnim, LLendAnim, w=1, mo=1)   
            ULendAnim.visibility.unlock()
            LLendAnim.visibility.unlock()
            ULendAnim.visibility.set(0)
            LLendAnim.visibility.set(0)
            
                #upper center
            parentConstraint(upperCenterAnim, URstartAnim, w=1, mo=1)
            parentConstraint(upperCenterAnim, ULstartAnim, w=1, mo=1)
            URstartAnim.visibility.unlock()
            ULstartAnim.visibility.unlock()
            URstartAnim.visibility.set(0)
            ULstartAnim.visibility.set(0)
                
                #lower center
            parentConstraint(lowerCenterAnim, LRstartAnim, w=1, mo=1)
            parentConstraint(lowerCenterAnim, LLstartAnim, w=1, mo=1)
            LLstartAnim.visibility.unlock()
            LRstartAnim.visibility.unlock()
            LLstartAnim.visibility.set(0)
            LRstartAnim.visibility.set(0)
            
            #connect the nurbs to the single IK
            for j in allJoints:
                zeroGrp = orig_singleIKZeroGrps[j]
                nurbsJoint = orig_nurbsJoint[j]
                parentConstraint(nurbsJoint, zeroGrp, w=1, mo=1)
            
            
            #connectToMeta
            connectChainToMeta(allJoints, self.networkNode, 'bindJoints')
            connectToMeta(lowerCenterAnim, self.networkNode, 'lowerLipAnim')
            connectToMeta(upperCenterAnim, self.networkNode, 'upperLipAnim')
            connectToMeta(rightMouthCornerAnim, self.networkNode, 'rightMouthCornerAnim')
            connectToMeta(leftMouthCornerAnim, self.networkNode, 'leftMouthCornerAnim')
            connectToMeta(URmidAnim ,self.networkNode, 'upperRightMidAnim')
            connectToMeta(LRmidAnim ,self.networkNode, 'lowerRightMidAnim')
            connectToMeta(ULmidAnim ,self.networkNode, 'upperLeftMidAnim')
            connectToMeta(LLmidAnim ,self.networkNode, 'lowerLeftMidAnim')
            connectChainToMeta(tweakAnims, self.networkNode, 'tweakAnims')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            connectToMeta(jointGrp, self.networkNode, 'jointGrp')
            connectToMeta(dntGrp, self.networkNode, 'dntGrp')
            connectToMeta(animGrp, self.networkNode, 'animGrp')
        
    def getAllTweakAnims(self):
        allTweaks = self.networkNode.tweakAnims.listConnections()
        return allTweaks
    
    
    def getAllMainAnims(self):
        allMain = []
        allMain.append(self.networkNode.lowerLipAnim.listConnections()[0])
        allMain.append(self.networkNode.upperLipAnim.listConnections()[0])
        allMain.append(self.networkNode.rightMouthCornerAnim.listConnections()[0])
        allMain.append(self.networkNode.leftMouthCornerAnim.listConnections()[0])
        allMain.append(self.networkNode.upperRightMidAnim.listConnections()[0])
        allMain.append(self.networkNode.lowerRightMidAnim.listConnections()[0])
        allMain.append(self.networkNode.upperLeftMidAnim.listConnections()[0])
        allMain.append(self.networkNode.lowerLeftMidAnim.listConnections()[0])
        return allMain
    
    def getAllAnims(self):
        allAnims = []
        map(lambda x: allAnims.append(x), self.getAllTweakAnims() )
        map(lambda x: allAnims.append(x), self.getAllMainAnims() )
        return allAnims
        
    def connectToComponentWithLevel(self, obj, anims):
        '''
        helper method to connectToComponent for only parenting part of the component
        '''
        dntGrp = self.networkNode.dntGrp.listConnections()[0]
        for x in anims:
            zero = createZeroedOutGrp(x)
            parentGrp = group(empty=1)
            parent(parentGrp, dntGrp)
            alignPointOrient(x, parentGrp, 1, 1)
            createZeroedOutGrp(parentGrp)
            parentConstraint(obj, parentGrp, w=1, mo=1)
            if 'mid' in x.name():#NOT THE BEST CHECK FOR MIDDLE NURBS ANIMS
                transMult = createNode('multiplyDivide')
                transMult.input2.set([.5,.5,.5])
                parentGrp.translate >> transMult.input1
                transMult.output >> zero.translate
                rotMult = createNode('multiplyDivide')
                rotMult.input2.set([.5,.5,.5])
                parentGrp.translate >> rotMult.input1
                rotMult.output >> zero.rotate
            else:
                parentGrp.translate >> zero.translate
                parentGrp.rotate >> zero.rotate
        
    def connectToComponent(self, comp, location, point=1, orient =1, level = 'all'):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []
        
        
        if level == 'all':
            mainGrp.setPivots(obj.getTranslation(space= 'world'))
            parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        elif level == 'upper':
            anims = []
            anims.append(self.networkNode.upperRightMidAnim.listConnections()[0])
            anims.append(self.networkNode.upperLipAnim.listConnections()[0])
            anims.append(self.networkNode.upperLeftMidAnim.listConnections()[0])
            self.connectToComponentWithLevel(obj, anims)
        elif level == 'lower':
            anims = []
            anims.append(self.networkNode.lowerRightMidAnim.listConnections()[0])
            anims.append(self.networkNode.lowerLipAnim.listConnections()[0])
            anims.append(self.networkNode.lowerLeftMidAnim.listConnections()[0])
            self.connectToComponentWithLevel(obj, anims)
        elif level == 'mid':#corner
            anims = []
            anims.append(self.networkNode.rightMouthCornerAnim.listConnections()[0])
            anims.append(self.networkNode.rightMouthCornerAnim.listConnections()[0])
            self.connectToComponentWithLevel(obj, anims)
    
    
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.rightMouthCornerAnim.listConnections()[0]
        elif location == 'end':
            return self.networkNode.leftMouthCornerAnim.listConnections()[0]
        else: # an object
            if not objExists(location):
                raise Exception("FKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return bind_joints[inc]
                #if location == fk_joints[inc]:
                #    return bind_joints[inc]
        raise Exception("FKChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or fk joint ")
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''        
        anims = self.getAllAnims()
        for anim in anims:
            resetAttrs(anim)
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        printWarning("IKLips.mirror: not yet implemented")
        
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            anim = self.getAnim()
            anim.rotateX.set(anim.rotateX.get()*-1)
            anim.rotateY.set(anim.rotateY.get()*-1)
            return [self]
        else:
            anim = self.getAnim()
            attrs = anim.listAttr(keyable = 1)
            attrValue = {}
            attrs = map(lambda x: x.name().split(".")[-1], attrs)
            for x in attrs:
                attrValue[x] = anim.attr(x).get()
            otherAnim = other.getAnim()
            otherAttrs = otherAnim.listAttr(keyable = 1)
            otherAttrs = map(lambda x: x.name().split(".")[-1], otherAttrs)
            otherAttrValue = {}    
            for x in otherAttrs:
                otherAttrValue[x] = otherAnim.attr(x).get()
            if bothSides:
                for attr in attrs:
                    otherAnim.attr(attr).set(attrValue[attr])
                for attr in otherAttrs:
                    anim.attr(attr).set(otherAttrValue[attr])
                return [self, other]
            else:
                for attr in otherAttrs:
                    anim.attr(attr).set(otherAttrValue[attr])
            return [self]
        '''


class IKSplineChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        RigComponent.__init__(self, 'IKChain', 1.0, 'chain of IK joints', side, bodyPart, startJoint, endJoint)
        chain = chainBetween(startJoint, endJoint)
        compName = '%s_%s'%(side, bodyPart)
        bind_joints = []
        for item in chain:
            item = PyNode(item)
            if item.type() == 'joint':
                bind_joints.append(item)
        ik_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'ik')
        
        #create ik handle/curve
        ik = ikHandle(sol='ikSplineSolver', ns = len(bind_joints), sj = ik_joints[0], ee = ik_joints[-1])[0]
        ik.rename('%s_ik'%compName)
        ikCurve = PyNode(ikHandle(ik, q=1, c=1)).getParent()
        ikCurve.rename('%s_ik_curve'%compName)
        ikCurve.inheritsTransform.set(0)
        
        #spine curve and anim setup
        select(cl=1)
        cvsJoint = joint(n = '%s_ik_curve_start_joint'%compName)
        select(cl=1)
        cvmJoint = joint(n = '%s_ik_curve_mid_joint'%compName)
        select(cl=1)
        cveJoint = joint(n = '%s_ik_curve_end_joint'%compName)
        
        alignPointOrient(ik_joints[0],cvsJoint,1,1 )
        alignPointOrient(ik_joints[len(ik_joints)/2],cvmJoint,1,1 )
        alignPointOrient(ik_joints[-1],cveJoint,1,1 )
        
        curve_joints = [cvsJoint, cvmJoint, cveJoint]
        anim_joints =[]
        spineLocs = []
        zeroGrps = []
        for obj in [cvsJoint,cveJoint]:            
            select(obj)
            animJoint = joint(n=obj.name().replace('ik_curve_','' ).replace('_joint','_anim'))
            addAnimAttr(animJoint)
            parent(animJoint, w=1)
            parent(obj, animJoint)
            zeroGrps.append(createZeroedOutGrp(animJoint))
            
            s = polySphere()[0]
            appendShape(s, animJoint)
            delete(s)
            anim_joints.append(animJoint)
            
            loc = spaceLocator(n = obj.name().replace('ik_curve_','' ).replace('_joint','_loc'))
            alignPointOrient(curve_joints[1], loc, 1,1)
            spineLocs.append(loc)
            
        midBendJoint = joint(n=cvmJoint.name().replace('ik_curve_','' ).replace('_joint','bend'))
        midBendJoint | cvmJoint     
        
        parentConstraint(anim_joints[0], spineLocs[0], w=1,mo=1)
        parentConstraint(anim_joints[1], spineLocs[1], w=1, mo=1)
        parentConstraint(spineLocs, midBendJoint, w=1, mo=1)
        
        select(cvsJoint, cvmJoint, cveJoint, ikCurve)
        rt.SmoothBindSkin()
        
        #connect to bind joints
        for inc in xrange(len(bind_joints)-1):
            parentConstraint(ik_joints[inc], bind_joints[inc], w=1, mo=1)    
            
        #grouping
        select(cl=1)
        jointGrp = group([ik_joints[0], midBendJoint],n='%s_joint_grp'%compName)
        animGrp = group(zeroGrps, n = "%s_anim_grp"%compName)
        dntGrp = group([ik,ikCurve], n = "%s_DO_NOT_TOUCH_grp"%compName)
        parent(spineLocs, dntGrp)
        mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
        xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
        
        #hide
        dntGrp.hide()
        midBendJoint.hide()
        
        #connect To Meta
        connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
        connectChainToMeta(ik_joints, self.networkNode, 'IKJoints')
        connectToMeta(ikCurve, self.networkNode, 'ikCurve')
        connectToMeta(ik, self.networkNode, 'ikHandle')
        connectToMeta(anim_joints[0], self.networkNode, 'bottomAnim')
        connectToMeta(anim_joints[1], self.networkNode, 'topAnim')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp')

    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
        
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.IKJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.IKJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("IKSpline.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            ik_joints = self.networkNode.IKJoints.listConnections()
            for inc in xrange(len(ik_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return ik_joints[inc]
                if location == ik_joints[inc]:
                    return ik_joints[inc]
        raise Exception("ikSpline.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or ik joint ")
    
    def isIK(self):
        return True
    
    def getIK(self):
        '''
        returns the ikhandle of the component
        '''
        return self.networkNode.ikHandle.listConnections()[0]
        
class AdditionalTwist(RigComponent):
    def __init__(self, twistLoc, side, bodyPart, startJoint, endJoint, node = ''):
        '''
        twistLoc:
            the place where the joints should twist from , start mid end
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'AdditionalTwist'):
                    self.networkNode = node
                else:
                    printError("AdditionalTwist: node %s is not a AdditionalTwist metaNode"%(node))
            else:
                printError("AdditionalTwist: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'AdditionalTwist', 1.0, 'chain that adds extra joints between two joints', side, bodyPart, startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            
            #error test        
            chain =  chainBetween(startJoint, endJoint)
            numAdded = len(chain)-2
            control_joints = map(lambda x: PyNode(x), chain)
            twist_joints = duplicateChain(control_joints[0], control_joints[-1], 'bind', 'twist')
            
            #parent twist joints to world
            #stops inheritance of rotation
            for j in twist_joints:
                try:
                    parent(j, world = 1)
                except:
                    pass
            
            #twist anim
            select(cl=1)
            twistAnim = joint(n = compName + '_twist_anim')
            addAnimAttr(twistAnim)
            
            cube = polyCube()[0]
            appendShape(cube, twistAnim)
            delete(cube)
            zeroGrp = createZeroedOutGrp(twistAnim)
            #create twist grp, 
            twistGrp = group(empty = 1, n = "%s_twist_grp"%compName)
            
            
            
            if twistLoc == 'start':
                #place anim
                const = parentConstraint(twist_joints[0],twistAnim, w=1, mo=0)
                delete(const)
                makeIdentity(twistAnim, apply=1, t=0, r=1, s=1, n=0)
                #add rotation
                inc = numAdded+1
                while inc >= 0:
                    multiplier = 1-(1.0/(numAdded+1))*inc
                    mult = createNode('multiplyDivide')
                    twistGrp.rotate >> mult.input1
                    mult.input2.set([multiplier,multiplier, multiplier])
                    mult.output >> twist_joints[inc].rotate
                    inc -= 1
            elif twistLoc == 'mid':
                
                odd = len(twist_joints) % 2
                
                mid_start = int((len(twist_joints)+1)/2)-1#mid to start joint inc
                mid_end = int((len(twist_joints)+1)/2)-1 #mid to end joint inc
                
                if not odd:
                    mid_end += 1
                
                #place anim
                const = parentConstraint(twist_joints[mid_start],twist_joints[mid_end], twistAnim, w=1, mo=0)
                delete(const)
                makeIdentity(twistAnim, apply=1, t=0, r=1, s=1, n=0)
                
                div = mid_start
                inc = mid_start
                while inc >= 0:
                    multiplier = float(inc)/div
                    
                    mult = createNode('multiplyDivide')
                    twistGrp.rotate >> mult.input1
                    mult.input2.set([multiplier,multiplier, multiplier])
                    mult.output >> twist_joints[mid_start].rotate
                    mult.output >> twist_joints[mid_end].rotate
                    
                    mid_start -=1
                    mid_end += 1
                    inc -= 1
            elif twistLoc == 'end':
                #place anim
                const = parentConstraint(twist_joints[-1],twistAnim, w=1, mo=0)
                delete(const)
                makeIdentity(twistAnim, apply=1, t=0, r=1, s=1, n=0)
                #add rotation
                inc = numAdded+1
                while inc > 0:
                    multiplier = (1.0/(numAdded+1))*inc
                    mult = createNode('multiplyDivide')
                    twistGrp.rotate >> mult.input1
                    mult.input2.set([multiplier,multiplier, multiplier])
                    mult.output >> twist_joints[inc].rotate
                    inc -= 1
                    
            else: #not an option
                raise Exception("AdditionalTwist.__init__: please specify a twist location: 'end', 'mid', 'start'")
                
            #parentConstrain the twist to the control
            for inc in xrange(len(twist_joints)):
                parentConstraint(twist_joints[inc], control_joints[inc], w=1, mo=1)
                
            #lock anim attrs
            lockAndHideAttrs(twistAnim, ['tx', 'ty','tz', 'ry', 'rz','sx','sy','sz','v','radius'])
            
            #grouping
            select(cl=1)
            twistJointGrp = group(twist_joints, n = '%s_twist_joint_grp'%compName)
            jointGrp = group([twistJointGrp, control_joints[0]],n='%s_joint_grp'%compName)
            animGrp = group([zeroGrp], n = "%s_anim_grp"%compName)
            dntGrp = group(twistGrp, n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = control_joints[0].getTranslation(space = 'world'), ws=1)
            
            alignPointOrient(twistAnim, twistGrp, 1,1)
            twistZeroGrp = createZeroedOutGrp(twistGrp)
            parentConstraint(twistAnim, twistGrp, mo=1, w=1)
            
            #hide extra junk
            dntGrp.hide()
            twistJointGrp.hide()
            
            
            #connections to meta
            connectChainToMeta(twist_joints, self.networkNode, 'twistJoints')
            connectToMeta(twistAnim, self.networkNode, 'twistAnim')
            connectChainToMeta(control_joints, self.networkNode, 'bindJoints')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
            #add to meta
            self.networkNode.setAttr('twistFrom', twistLoc , f=1)
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot,  st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
        
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.bindJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.bindJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("AdditionalTwist.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = [self.networkNode.startJoint.listConnections()[0],self.networkNode.endJoint.listConnections()[0]]
            control_joints = self.networkNode.bindJoints.listConnections()
            twist_joints = self.networkNode.twistJoints.listConnections()
            for inc in xrange(len(fk_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
                if location == twist_joints[inc]:
                    return control_joints[inc]
        raise Exception("AdditionalTwist.getConnectObj: location wasn't found, try 'start', 'end', or name of bind twist or control joint ")
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        
        anim = self.getTwistAnim()
        animRot = anim.rotateX.get()
        if other == self:
            anim.rotateX.set(-animRot)
            return [self]
        else:
            otherAnim = other.getTwistAnim()
            otherRot = otherAnim.rotateX.get()
            if bothSides:
                otherAnim.rotateX.set(-animRot)
                anim.rotateX.set(-otherRot)
                return [self, other]
            else:
                anim.rotateX.set(-otherRot)
                return [self]    
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return [self.getTwistAnim()]
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        anim = self.getTwistAnim()
        resetAttrs(anim)
                                    
    def twistConstraint(self, constObject, axis = 'X'):
        '''
        tells which obect controls the twist of the additional twist t
        used well for automatic forearm twist
        '''
        anim = self.getTwistAnim()
        twist_grp = group(empty = 1, n = "%s_auto_twist_grp"%anim.name())
        par = anim.getParent()
        parent(twist_grp, par)
        alignPointOrient(anim, twist_grp,1,1)
        makeIdentity(twist_grp, apply=1, t=1, r=0,s=0, n=0)
        for x in ["translateX", "translateY", "translateZ"]:
            anim.attr(x).unlock()
        parent(anim, twist_grp)
        for x in ["translateX", "translateY", "translateZ"]:
            anim.attr(x).lock()
        
        orientConstraint(constObject, twist_grp, skip = ('y','z'), mo=1, w=1)
                                    
    def getTwistAnim(self):
        """
        returns the twist anim
        """
        return self.networkNode.twistAnim.listConnections()[0]
        
 
class FKIKHair(RigComponent):
    def __init__(self, start, end, circle, curve, hairID, node = ''):
        self.ID = hairID
        ik_joints = []
        fk_joints = []
        compName = "hair_" + str(self.ID)
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKHair'):
                    self.networkNode = node
                else:
                    printError("FKIKHair: node %s is not a FKIKHair metaNode"%(node))
            else:
                printError("FKIKHair: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKIKHair', 1.0, 'creates FKIK spline controls specifically meant for hair', 'center', compName, start, end)
            self.bigSize = 2  #size relate to anim
            self.meshSize = 1
            self.baseRatio = 1.4
            self.controlAnim = [] 
            self.controlJoint = []
            self.control_joints = []
            self.fkanims = []
            self.ikanims = []
            self.ikcounter = 0
            print circle
            self.makeFkIkControlOnly(PyNode(curve), PyNode(circle), PyNode(start));
            
            bindChain = chainBetween(start, end)
            bind_joints = []
            for i in bindChain:
                i = PyNode(i)
                if i.type() == 'joint':
                    bind_joints.append(i)

            ikChain = chainBetween('hair_'+str(self.ID)+'_root_ik_joint', 'hair_'+str(self.ID)+'_ik_end_joint')
            ik_joints = []
            for i in ikChain:
                i = PyNode(i)
                if i.type() == 'joint':
                    ik_joints.append(i)
                    
            fkChain = chainBetween('hair_'+str(self.ID)+'_root_fk_joint', 'hair_'+str(self.ID)+'_fk_end_joint')
            fk_joints = []
            
            #for anim in self.fkanims:
            #    anim = PyNode(anim)
            #    delete(anim)
                
            counter = 0
            for i in fkChain:
                i = PyNode(i)
                if i.type() == 'joint':
                    fk_joints.append(i)
                    
            for i in fk_joints:
                if counter < len(self.fkanims):
                    #print self.fkanims[counter]
                    appendShape(self.fkanims[counter], i)
                    #parent(self.fkanims[counter], i, add =1, s=1, r=1)
                    #print test
                addAnimAttr(i)
                changeName = i.name().replace('joint', 'anim')
                lockAndHideAttrs(i, ['sx', 'sy', 'sz', 'radius'])
                rename(i, changeName)
                counter += 1
                
            for anim in self.fkanims:
                anim = PyNode(anim)
                delete(anim)
                
            #for i in self.ikanims:
            #    appendShape(i[0], i[1])
            #    addAnimAttr(i)
            #    changeName = i[1].name().replace('joint', 'anim')
            #    rename(i[1], changeName)
            #    control_joints.append(i[1])
                
            #for anim in self.ikanims:
            #    parent(anim[1], w=True)
            
            #for anim in self.ikanims:
             #   delete(anim)
                
                
            '''
                for inc in xrange(len(fk_joints)-1):
                    obj = fk_joints[inc]
                    addBoxToJoint(obj)
                    lockAndHideAttrs(obj, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius'])
                    obj.v.set(keyable = 0)
                    addAnimAttr(obj)
                    print obj
            '''
                   
            base_curve = PyNode('hair_'+str(self.ID)+'_base_curve')
            inheritTransform(base_curve, off=True)
            ik_curve = PyNode('hair_'+str(self.ID)+'_ik_control_curve')
            inheritTransform(ik_curve, off=True)
            ik_control = PyNode('hair_'+str(self.ID)+'_control_ik')
            fkik_grp = PyNode('hair_'+str(self.ID)+'_fk_ik_group')
            self.base = PyNode('hair_'+str(self.ID)+'_base_anim')
            
            #parentConstraint(self.base, PyNode('hair_'+str(self.ID)+'_root_fk_anim'), mo=True)
            parent(PyNode('hair_'+str(self.ID)+'_root_fk_anim'), self.base)
            
            #addAnimAttr(anim_grp)
            '''
            switchGroup = group(n = '%s_FKIK_switch'%compName)
            switchGroup.addAttr('FKIK_switch', keyable = 1)
            switchGroup.FKIK_switch.setMax(1)
            switchGroup.FKIK_switch.setMin(0)
            switchGroup.FKIK_switch.setKeyable(1)
            rev = createNode('reverse')
            switchGroup.FKIK_switch >> rev.inputX
            rev.outputX >> anim_grp.fk_ik
            switchGroup.FKIK_switch >> anim_grp.fk_ik
            switchGroup.addAttr('animNode', at= 'message')
            '''
            self.base.addAttr('animNode', at= 'message')

            
            
            mainGrp = group([base_curve, ik_curve, ik_control, fkik_grp, self.base],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(ik_joints, self.networkNode, 'IKJoints')
            connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
            connectChainToMeta(self.ikanims, self.networkNode, 'IKAnims')
            connectChainToMeta(self.control_joints, self.networkNode, 'controlJoints')
            connectToMeta(self.base, self.networkNode, 'baseAnim')
            numb = 0
            #for x in self.anims:
             #   connectToMeta(x, self.networkNode, 'anims' + str(numb))
             #   numb += 1
            
          #  connectToMeta(switchGroup, self.networkNode, 'switchGroup')
           # self.networkNode.setAttr('switchAttr', 'FKIK_switch', f=1)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')

            '''
                connectToMeta(startAnim, self.networkNode, 'startAnim')
                connectToMeta(midAnim, self.networkNode, 'midAnim')
                connectToMeta(endAnim, self.networkNode, 'endAnim')
                connectToMeta(switchGroup, self.networkNode, 'switchGroup')
                self.networkNode.setAttr('switchAttr', 'FKIK_switch', f=1)
                connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            '''
        
        # fk hair functions

    def makeControl(self, j) :
        markoff = 1;
        count = 0;
        counter = 0;
        old = None
        
        while j.getChildren() != [] :
            if count == 0:
                select(j)
                location = xform(j, q=1, ws=1, t=1)
                c = circle(name="hair_"+str(self.ID)+"_fk_anim_"+str(counter), nr=[1, 0, 0])
                g = group(em=1, name="hair_"+str(self.ID)+"_freeHack_fk")
                parent(c, g)
                select(g)
                move(location)
                tempAnim = PyNode("hair_"+str(self.ID)+"_fk_anim_"+str(counter))
                self.fkanims.append(tempAnim)
                j2 = j.getChildren()[0]
                c[0].scale.set([self.bigSize, self.bigSize, self.bigSize])
                aimConstraint(j2, g, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])
                aimConstraint(j2, g, rm=1)
                makeIdentity(c, apply=1)
                #parentConstraint(c, j, mo=1)
                if old != None:
                    parent(g, old)
                old = c
                count = markoff
            
            counter += 1
            count = count - 1
            j = j.getChildren()[0]
        
        #print old[0]
        while old[0].listRelatives(p=1) != []:
            old = old[0].listRelatives(p=1)
        return old
    
    # make a joint chain
    def jointChain(self, c, type):
        select(c)
        joints = []
        for x in c.cv:
            location = xform(x, q=1, ws=1, t=1)
            jtemp=joint(p=location, name="hair_" +str(self.ID)+"_" + type + "_joint")
            joints.append(jtemp)
        
        for x in joints:
            joint(x, e=1, sao="yup", oj="xyz", zso=1)
        
        j=c.getChildren()[1]
        select(j)
        parent(w=1)
        #print j
        return j[0]
        
    # make a actual mesh
    def makeMesh(self, c) :
        location = xform(c.cv[0], q=1, ws=1, t=1)
        size = len(c.cv) / 3
        #print size
        c2 = circle(name="hair_" + str(self.ID) + "_base_circle")
        c2[0].scale.set([size * self.meshSize, size * self.meshSize, size * self.meshSize])
        move(location)
        aimConstraint(c , c2, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])
        aimConstraint(c, c2, rm=1)
        mesh = extrude(c2[0], c, ch=1, rn=0, po = 1, et=2, ucp =0, fpt = 0, upn = 0, rotation = 0, scale= 1, rsp = 1)
        rename(mesh[0], "hair_" + str(self.ID) + "_mesh")
        mesh[1].scale.set(0)
        return c2
    
    # make a copy of the current given j
    def copyJoints(self, j, type):
        j2 = duplicate(j)[0];
        #print j2
        jTemp = j2;
        #print jTemp
        #print jTemp.getChildren()
        numb = 0
        while jTemp.getChildren() != []:
            if numb == 0:
                rename(jTemp, "hair_" +str(self.ID) + "_root_" + type + "_joint")
            else:
                rename(jTemp, "hair_" +str(self.ID) + "_" + type + "_joint_"+str(numb))
            numb += 1
            jTemp = jTemp.getChildren()[0]
        rename(jTemp, "hair_" +str(self.ID)+"_"+ type + "_end_joint")
        return j2
    
    # make a fkhair
    def makeFkHair(self, c, js):
        j2 = self.copyJoints(js, "fk")
        con = self.makeControl(j2)
        return (j2, con)
    
    #ik hair function
    def helpIkControl(self, j):
        j3 = duplicate(j)[0]
        rename(j3, "hair_"+str(self.ID)+"_control_joint"+str(self.ikcounter))
        if j3.getParent() != None :
            select(j3)
            parent(w=1)
        if(j3.getChildren() != []):
            delete(j3.getChildren()[0])
        select(j)
        self.controlJoint.append(j3)
        self.control_joints.append(j3)
        location = xform(j, q=1, ws=1, t=1)
        c = circle(name="hair_"+str(self.ID)+"_ik_anim_"+str(self.ikcounter), nr=[0, 0, 1])
        g = group(em=1, name="hair_"+str(self.ID)+"_freeHack_ik")
        parent(c, g)
        self.controlAnim.append(c)
        #self.anims.append(c)
        select(g)
        tempAnim = PyNode("hair_"+str(self.ID)+"_ik_anim_"+str(self.ikcounter))
        self.ikcounter += 1
        move(location)
        #self.ikanims.append([tempAnim, j3])
        
        self.ikanims.append(tempAnim)       
        c[0].scale.set([self.bigSize, self.bigSize, self.bigSize])
        if j.getChildren() != []:
            j2 = j.getChildren()[0]
            aimConstraint(j2, g, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])
            aimConstraint(j2, g, rm=1)
            makeIdentity(c, apply=1)
            #parentConstraint(c, j, mo=1)
        else :
            j3 = j.getParent()
            location2 = xform(j3, q=1, ws=1, t=1)
            j2 = j
            select(g)
            move(location2)
            aimConstraint(j2, g, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])
            aimConstraint(j2, g, rm=1)
            select(g)
            move(location)
            makeIdentity(c, apply=1)
            #parentConstraint(c, j, mo=1)
        return g
            
    # make a single ikcontrols
    def makeIkControl(self, j):
        markoff = 3;
        count = 0;
        old = None
        
        while j.getChildren() != [] :
            if count == 0:
                c = self.helpIkControl(j)
                if old != None:
                    parent(c, old.listRelatives()[0])
                old = c
                count = markoff
            
            count = count - 1
            j = j.getChildren()[0]
        # last anim
        c = self.helpIkControl(j)
        parent(c, old.listRelatives()[0])
        
        #print old
        while old.listRelatives(p=1) != []:
            old = old.listRelatives(p=1)[0]
        return old
    
    # create control curve for the joint chain
    def makeControlCurve(self, j):
        location = []
        while j.getChildren() != [] :
            p = xform(j, q=1, ws=1, t=1)
            location.append(p)
            j = j.getChildren()[0]
        p = xform(j, q=1, ws=1, t=1)
        location.append(p)
        
        c = curve(p = location, name="hair_"+str(self.ID)+"_ik_control_curve")
        return c
    
    # return the last joint in jointChain
    def endJoint(self, j):
        while j.getChildren() != []:
            j = j.getChildren()[0]
        return j
    
    # make a ik hair
    def makeIkHair(self, c, js) :
        j = self.copyJoints(js, "ik")
        endJ = self.endJoint(j)
        c = self.makeControlCurve(j)
        
        select(endJ, r = 1)
        select(j, add=1)
        select(c, add = 1)
        controlik = ikHandle(sol='ikSplineSolver', ccv=0)
        rename(controlik[0], "hair_"+str(self.ID)+"_control_ik")
        hide(controlik)
        
        control = self.makeIkControl(j)
        
        select(clear = 1)
        for x  in self.controlJoint :
            select(x, add=1)
        select(c, add=1)
        skinCluster(tsb=True, maximumInfluences=4, normalizeWeights=1,obeyMaxInfluences=True)
        
        size = len(self.controlAnim)
        #print size
        for x in range(size):
            parent(self.controlJoint[x], self.controlAnim[x])
        return (j, control, c)
    
    # prepare the binding process
    def helpIkFkHair(self, fJ, iJ, j, c, re):
        pi = parentConstraint(iJ, j)
        pf = parentConstraint(fJ, j)
        p = j.listRelatives()
        if len(p) == 1:
            p = p[0]
        else:
            p = p[1]
            
        #strIK = "hair_"+str(self.ID)+"_ik_jointW0"
        #strFK =

        pWeights = parentConstraint(p, q=1, wal=True)
        
        c.fk_ik >> pWeights[0]
        re.outputX >> pWeights[1]
        c.scale >> iJ.scale
    
    # hide some anims
    def helpHideAnim(self, fc, ic, c, re):
        while fc.getChildren() != []:
            re.outputX >> fc.visibility
            fc = fc.getChildren()[0]
        re.outputX >> fc.visibility
        #print ic
        while ic.getChildren() != []:
            c.fk_ik >> ic.visibility
            ic = ic.getChildren()[0]
        c.fk_ik >> ic.visibility
    
    # make a ik fk control
    def makeFkIkControl(self, c, js):
        ik = self.makeIkHair(c, js)
        fk = self.makeFkHair(c, js)
        j = js
        jMaster = j
        location = xform(j, q=1, ws=1, t=1)
        cir = circle(name = "hair_"+str(self.ID)+"_base_anim")
        move(location)
        
        cir[0].scale.set([self.bigSize * self.baseRatio, self.bigSize * self.baseRatio, self.bigSize * self.baseRatio])
        aimConstraint(fk[0].getChildren()[0], cir, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])
        aimConstraint(fk[0].getChildren()[0], cir, rm=1)
        addAttr(cir,ln="fk_ik", at="enum", en="fk:ik:", k=1)
        makeIdentity(cir, apply=1)
    
        re = shadingNode("reverse", au=1)
        
        cir[0].fk_ik >> re.inputX
        iJ = ik[0]
        fJ = fk[0]
        while j.getChildren() != []:
            self.helpIkFkHair(fJ, iJ, j, cir[0], re)
            j = j.getChildren()[0]
            fJ = fJ.getChildren()[0]
            iJ = iJ.getChildren()[0]
        self.helpIkFkHair(fJ, iJ, j, cir[0], re)
        jtemp = fJ.getParent()
        cir[0].scale >> jtemp.scale
        cir[0].fk_ik >> ik[2].visibility
        parent(fk[1], cir)
        parent(ik[1], cir)
        self.helpHideAnim(PyNode("hair_"+str(self.ID)+"_root_fk_joint"), ik[1], cir[0], re)

        hide(ik[0])
        hide(fk[0])
        
        select(jMaster, r=1)
        select(ik[0], add=1)
        select(fk[0], add =1)
        group(name="hair_"+str(self.ID)+"_fk_ik_group")
        self.controlJoint = []
        self.controlAnim = []
        # joint, ikJoint, fkJoint, ikAnim, fkAnim
        return (jMaster, ik[0], fk[0], cir, re)
    
    # aim a c pointing to j
    def moveAndAim(self, c, j):
        location = xform(j, q=1, ws=1, t=1)
        select(c)
        move(location)
        aimConstraint(j.getChildren()[0], c, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])
        aimConstraint(j.getChildren()[0], c, rm=1)
    
    # link the base circle to the FkIk rig
    def fixBaseCircle(self, cf, ci, c, topCon, re):
        parentConstraint(ci.listRelatives()[0], c, mo=1)
        parentConstraint(cf.listRelatives()[0], c, mo=1)
        p = c.listRelatives()[1]
    
        topCon.fk_ik >> PyNode(p.name()+".hair_"+str(self.ID)+"_ik_animW0")
        re.outputX >> PyNode(p.name()+".hair_"+str(self.ID)+"_fk_animW1")
        #topCon.scale >> c.scale
        
    # last binding process
    def finalBind(self, j, c):
        select(j, r=1)
        select(c, add=1)
        skinCluster()
        
    def hideScaleAndVisibility(self, j):
        while j.getChildren() != []:
            setAttr(j.scale, k=0, l=1, cb=0)
            setAttr(j.visibility, k=0, l=1, cb=0)
            j = j.getChildren()[0]
        setAttr(j.scale, k=0, l=1, cb=0)
        setAttr(j.visibility, k=0, l=1, cb=0)
    
    def makeFkIkHair(self, c, js):
        baseCircle = self.makeMesh(c)
        return self.makeFkIkControlOnly(c, baseCircle[0], js)
    
    def makeFkIkControlOnly(self, c, circle, js):
        list = self.makeFkIkControl(c, js)
        baseCircle = circle
        #self.moveAndAim(baseCircle, list[0])
        
        fc = list[3][0].getChildren()[1]
        ic = list[3][0].getChildren()[2]
        #self.fixBaseCircle(fc, ic, baseCircle, list[3][0], list[4])
        self.finalBind(list[0], c)
        hide(baseCircle)
        #self.hideScaleAndVisibility(fc)
        #self.hideScaleAndVisibility(ic)
        
        rename(c, "hair_"+str(self.ID)+"_base_curve")
        parent(baseCircle, list[3])
        return (list[3])
        
    def getAllAnims(self):
        allAnims = []
        map(lambda x: allAnims.append(x), self.networkNode.IKAnims.listConnections()[:-1])
        map(lambda x: allAnims.append(x), self.networkNode.FKJoints.listConnections()[:-1])
        map(lambda x: allAnims.append(x), self.networkNode.baseAnim.listConnections())
        #allAnims(self.base)baseAnim
        return allAnims

    def selectBase(self):
        select(cl=True)
        select(self.networkNode.baseAnim.listConnections()[0])
    
    def switch(self):
        anim = self.networkNode.baseAnim.listConnections()[0]
        type = getAttr(PyNode(anim.name()+".fk_ik"))
        select(cl=True)
        if type == 0:
            setAttr(PyNode(anim.name()+".fk_ik"), 1)
        else:
            setAttr(PyNode(anim.name()+".fk_ik"), 0)
    
    def straight(self):
        selected = ls(sl=1)[0]
        if "fk_anim" in (str(selected)):
            while selected.getChildren() != []:
                if not "root" in (str(selected)):
                    if  selected.type() == "joint":
                        jOrient = selected.jointOrient.get()
                        selected.rotate.set(-jOrient[0], -jOrient[1], -jOrient[2])
                        setAttr(selected.translateY, 0)
                        setAttr(selected.translateZ, 0)
                    else:
                        print "found a node that is not a joint {0}".format(selected)
                selected = selected.getChildren()[0]
        else:
            printError("Select an FK anim to use")
            
    def selectChild(self):
        selected = ls(sl=1)[0]
        if "anim" in (str(selected)):
            select(cl=True)
            while selected.getChildren() != []:
                if "anim" in (str(selected)):
                    select(selected, add=True)
                selected = selected.getChildren()[0]

	
class FKDeformerChain(RigComponent):
    widgets = {}
    def __init__(self, side, bodyPart, startJoint, endJoint, deform = 'sine', node = ''): 
		'''
		side:
			the side is this component on, ex. center, left, right
					
		bodyPart:
			the body part the component is for, ex. arm, leg, clavicle, foot
					
		startJoint:
			the place where the component starts
					
		endJoint:
			the place where the component end

		controlEnd:
			Last joint in the chain specified is affected by the NURBs ribbon
			if true, otherwise is remains untouched (but the IK end anim is still
			created on top of it)
		'''
        
		if node:
			if objExists(node):
				node = PyNode(node)
				if( isMetaNode(node) and node.metaType.get() == 'FKDeformerChain'):
					self.networkNode = node
				else:
					printError("FKDeformerChain: node %s is not a 'FKDeformerChain' metaNode"%(node))
			else:
				printError("FKDeformerChain: node %s doesn't exist"%(node))
		else:
			RigComponent.__init__(self, 'FKDeformerChain', 1.0, 'FK Chain that rotates like a sine or bend deformer', side, bodyPart, startJoint, endJoint)
			stuff = FK_deformer(side,bodyPart,startJoint,endJoint,deform)

			bind_joints = stuff[0]
			fk_joints = stuff[1]
			#switch = stuff[2]
			component_grp = stuff[3]
			deformer = stuff[4]
						
			connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
			connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
			connectToMeta(component_grp, self.networkNode, 'componentGrp')
			self.widgets['component_grp'] = component_grp

			self.widgets['deformer'] = deformer

    def getAllAnims(self):
		allAnims = []
		allAnims.append(self.networkNode.FKJoints.listConnections())		
		return allAnims
    
    def getComponentGrp(self):
		component_grp = []
		component_grp .append(self.networkNode.componentGrp.listConnections())
				
		return self.widgets['component_grp']

    def getDeformer(self):
		return self.widgets['deformer']
    
class FKIKReverseSplineChain(RigComponent):
	widgets = {}
	def __init__(self, side, bodyPart, startJoint, endJoint, node = ''): 
		'''
		side:
			the side is this component on, ex. center, left, right
					
		bodyPart:
			the body part the component is for, ex. arm, leg, clavicle, foot
					
		startJoint:
			the place where the component starts
					
		endJoint:
			the place where the component end

		controlEnd:
			Last joint in the chain specified is affected by the NURBs ribbon
			if true, otherwise is remains untouched (but the IK end anim is still
			created on top of it)
		'''
        
		if node:
			if objExists(node):
				node = PyNode(node)
				if( isMetaNode(node) and node.metaType.get() == 'FKIKReverseSplineChain'):
					self.networkNode = node
				else:
					printError("FKIKReverseSplineChain: node %s is not a FKIKReverseSplineChain metaNode"%(node))
			else:
				printError("FKIKReverseSplineChain: node %s doesn't exist"%(node))
		else:
			RigComponent.__init__(self, 'FKIKReverseSplineChain', 1.0, 'spline chain of IK joints with reversable a FK joint chain', side, bodyPart, startJoint, endJoint)
			stuff = reversible_FKIK_spine(side,bodyPart,startJoint,endJoint)

			bind_joints = stuff[0]
			ik_joints = stuff[1]
			fk_joints = stuff[2][1::2]+stuff[3][1::2]
			#rev_fk_joints = stuff[3][1::2]
			switch = stuff[4]
			component_grp = stuff[5]
						
			connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
			connectChainToMeta(ik_joints, self.networkNode, 'IKJoints')
			connectChainToMeta(fk_joints, self.networkNode, 'FK_Joints')
			#connectChainToMeta(rev_fk_joints, self.networkNode, 'Reverse_FK_Joints')
			connectToMeta(switch, self.networkNode, 'switchGroup')
			self.networkNode.setAttr('switchAttr', 'FKIK_Switch', f=1)
			connectToMeta(component_grp, self.networkNode, 'componentGrp')
			self.widgets['component_grp'] = component_grp
        
	def getAllAnims(self):
		allAnims = []
		allAnims.append(self.networkNode.FK_Joints.listConnections())
		#allAnims.append(self.networkNode.Reverse_FK_Joints.listConnections())
				
		return allAnims

	def getComponentGrp(self):
		component_grp = []
		component_grp.append(self.networkNode.componentGrp.listConnections())
				
		return self.widgets['component_grp']

class FKIKSplineChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = '', controlEnd = False, directControlOfEnds = False, useReverseEndAimer = False): 
        '''
        side:
            the side is this component on, ex. center, left, right
            
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
            
        startJoint:
            the place where the component starts
            
        endJoint:
            the place where the component end

        controlEnd:
            Last joint in the chain specified is affected by the NURBs ribbon
            if true, otherwise is remains untouched (but the IK end anim is still
            created on top of it)
            
        directControlOfEnds:
            The start and end joints aren't controlled by the NURBs ribbon,
            but by the IK controls themselves.  This allows for more predictable
            posing in general but will be a bit more work to create a smooth chain.
        
        useReverseEndAimer:
            If true, make a secondary aimer anim under the final control
        '''
        
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKSplineChain'):
                    self.networkNode = node
                else:
                    printError("FKIKSplineChain: node %s is not a FKIKSplineChain metaNode"%(node))
            else:
                printError("FKIKSplineChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKIKSplineChain', 1.0, 'spline chain of IK joints with fk switching', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            bind_joints = []
            for item in chain:
                item = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
                    
            # Create chains
            ik_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'ik')
            fk_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'fk')
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
            
            # Create an FK system where each FK node can be scaled independently
            # without affecting the scale of the anims themselves.
            fk_scaleGrps = []
            fk_zeroGrps = []
            
            for inc in xrange(len(fk_joints)):
                
                obj = fk_joints[inc]
                
                # Setup the zero group
                zeroGrp = createZeroedOutGrp(obj)
                fk_zeroGrps.append(zeroGrp)
                
                # Create the anims
                addBoxToJoint(obj)
                if inc == 0:
                    lockAndHideAttrs(obj, ['s', 'radius'])
                else:
                    lockAndHideAttrs(obj, ['t', 's', 'radius'])
                obj.v.set(keyable = 0)
                addAnimAttr(obj)
                obj.rename('%s_%i_anim'%(compName, inc+1))

                # Setup the scale system
                if (inc == 0): continue
                
                parentObj = fk_joints[inc-1]
                
                scaleGrp = group(empty=1, n="%s_scale_grp"%parentObj.shortName())
                alignPointOrient(parentObj, scaleGrp, 1, 1)
                parent(scaleGrp, parentObj)
                fk_scaleGrps.append(scaleGrp)

                animLocation = group(empty=1, n="%s_anim_location"%parentObj.shortName())
                alignPointOrient(zeroGrp, animLocation, 1, 1)
                parent(animLocation, scaleGrp)
                
                distFromParentAnim = animLocation.translate.get().length()
                parent(animLocation, w=1)
                scaleGrp.scale.set(distFromParentAnim, distFromParentAnim, distFromParentAnim)
                makeIdentity(scaleGrp, s=1, apply=1)
                parent(animLocation, scaleGrp)
                
                parentConstraint(animLocation, zeroGrp, mo=0)
                
                # Add stretch attribute to the parent
                parentObj.addAttr("stretch", keyable=1, dv=1, min=0.001)
                stretchAttr = parentObj.attr("stretch")
                stretchAttr >> scaleGrp.scaleX
                stretchAttr >> scaleGrp.scaleY
                stretchAttr >> scaleGrp.scaleZ
                
            
            fk_jntAnimGrp = group(fk_zeroGrps, n="%s_fk_joint_anims"%compName)
            
            returns = createNurbsPlaneIKChain(ik_joints[0], ik_joints[-1], compName, useReverseEndAimer)
            startAnim = returns[0]
            midAnim = returns[1]        
            endAnim = returns[2]        
            animGrp = returns[3]        
            ik_joints_grp = returns[4]     
            nurbsPlane = returns[5]     
            transGrp = returns[6]         
            dummyGrp = returns[7]         
            ikLocGrp = returns[8]        
            distDimGrp = returns[9]
            reverseEndAimer = returns[10]           
            
            control_joint_grp = group(control_joints[0], n = '%s_control_joints'%compName)
            for cj in control_joints[1:]:
                control_joint_grp | cj
            
            select(cl=1)
            switchGroup = group(n = '%s_FKIK_switch'%compName)
            switchGroup.addAttr('FKIK_switch', keyable = 1)
            switchGroup.FKIK_switch.setMax(1)
            switchGroup.FKIK_switch.setMin(0)
            switchGroup.FKIK_switch.setKeyable(1)
            rev = createNode('reverse')
            switchGroup.FKIK_switch >> rev.inputX

            # Set up FK/IK switch constraints
            lastControlJointIndex = len(control_joints)-1
            for i in xrange(len(control_joints)):
                isFirstControlJoint = (i==0)
                isLastControlJoint = (i==lastControlJointIndex)
                
                if directControlOfEnds and isFirstControlJoint:
                    switchConst = parentConstraint(fk_joints[i], startAnim, control_joints[i], mo=1)
                elif directControlOfEnds and isLastControlJoint:
                    switchConst = parentConstraint(fk_joints[i], endAnim, control_joints[i], mo=1)
                else:
                    switchConst = parentConstraint(fk_joints[i], ik_joints[i], control_joints[i], mo=1)
                '''
                if not controlEnd or not isLastControlJoint:
                    switchScaleConst = scaleConstraint(fk_joints[i], ik_joints[i], control_joints[i], skip=['y','z'])
                '''
                    
                rev.outputX >> switchConst.w0
                '''rev.outputX >> switchScaleConst.w0'''
                switchGroup.FKIK_switch >> switchConst.w1
                '''
                if not controlEnd or not isLastControlJoint:
                    switchGroup.FKIK_switch >> switchScaleConst.w1
                '''
                    
            lockAndHideAttrs(switchGroup, ['s','v'])
            
            # Switch groups hide FK or IK
            rev.outputX >> fk_jntAnimGrp.visibility
            switchGroup.FKIK_switch >> animGrp.visibility 
            
            # Connect to bind joints
            allowSafeScale(bind_joints[0], bind_joints[-1])
            range= len(bind_joints)-1
            if controlEnd:
                range = len(bind_joints)
            for i in xrange(range):
                parentConstraint(control_joints[i], bind_joints[i], w=1, mo=1)
                
            # Create IK matching approximation locators
            startAnimMatcher = spaceLocator(n=compName+'_startAnimMatcher')
            delete(parentConstraint(startAnim, startAnimMatcher, mo=0))
            parent(startAnimMatcher, startAnim.getParent())
            parentConstraint(fk_joints[0], startAnimMatcher, mo=1)
            hide(startAnimMatcher)
            
            midAnimMatcher = spaceLocator(n=compName+'_midAnimMatcher')
            delete(parentConstraint(midAnim, midAnimMatcher, mo=0))
            parent(midAnimMatcher, midAnim.getParent())
            parentConstraint(fk_joints[len(fk_joints)/2], midAnimMatcher, mo=1)
            hide(midAnimMatcher)
            
            endAnimMatcher = spaceLocator(n=compName+'_endAnimMatcher')
            delete(parentConstraint(endAnim, endAnimMatcher, mo=0))
            parent(endAnimMatcher, endAnim.getParent())
            parentConstraint(fk_joints[-1], endAnimMatcher, mo=1)
            hide(endAnimMatcher)
            
            # Grouping
            select(cl=1)
            jointGrp = group([ik_joints_grp, fk_jntAnimGrp, control_joint_grp],n='%s_joint_grp'%compName)
            dntGrp = group([nurbsPlane, transGrp, dummyGrp, ikLocGrp, distDimGrp], n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp, switchGroup],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            switchGroup.FKIK_switch.set(1)
            parentConstraint(mainGrp, switchGroup, mo=0)
            
            # Hide
            dntGrp.hide()
            switchGroup.FKIK_switch >> ik_joints[0].v
            lockAndHideAttrs(switchGroup, ['t', 'r'])
            
            # Connect To Meta
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(ik_joints, self.networkNode, 'IKJoints')
            connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectToMeta(startAnim, self.networkNode, 'startAnim')
            connectToMeta(midAnim, self.networkNode, 'midAnim')
            connectToMeta(endAnim, self.networkNode, 'endAnim')
            connectToMeta(reverseEndAimer, self.networkNode, 'reverseEndAimer')
            connectToMeta(startAnimMatcher, self.networkNode, 'startAnimMatcher')
            connectToMeta(midAnimMatcher, self.networkNode, 'midAnimMatcher')
            connectToMeta(endAnimMatcher, self.networkNode, 'endAnimMatcher')
            connectToMeta(switchGroup, self.networkNode, 'switchGroup')
            self.networkNode.setAttr('switchAttr', 'FKIK_switch', f=1)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
    def getSwitchAttr(self):
        switchNode = listConnections(self.networkNode.switchGroup)[0]  
        switchAttrName = self.networkNode.switchAttr.get()
        return switchNode.attr(switchAttrName)
        
    def alignSwitch(self):
        '''
        toggle between FK and IK while keeping current joint placement
        '''
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        switchAttr = self.networkNode.switchAttr.get()
        attr = switchGroup.attr(switchAttr)
        attr.set(1-attr.get())
        
        # Switch IK -> FK.
        # Straight forward, exact[ish] match.  Factors in stretch.
        if switchGroup.attr(switchAttr).get() < .5:
            
            ikJoints = self.networkNode.IKJoints.listConnections()
            fkJoints = self.networkNode.FKJoints.listConnections()
            
            for i in xrange(len(ikJoints)):
                ikj = ikJoints[i]
                fkj = fkJoints[i]
                
                alignPointOrient(ikj, fkj, (i==0), 1)
                
                if (i < len(ikJoints)-1):
                    stretchAttr = fkj.attr("stretch")
                    stretchAttr.set(ikJoints[i+1].scaleX.get())
            
        # Switch FK -> IK.
        # Approximate match.  
        else:
            
            startAnim = self.networkNode.startAnim.listConnections()[0]
            midAnim = self.networkNode.midAnim.listConnections()[0]
            endAnim = self.networkNode.endAnim.listConnections()[0]
            try:
                reverseEndAimer = self.networkNode.reverseEndAimer.listConnections()[0]
            except:
                reverseEndAimer = None
            
            startAnimMatcher = self.networkNode.startAnimMatcher.listConnections()[0]
            midAnimMatcher = self.networkNode.midAnimMatcher.listConnections()[0]
            endAnimMatcher = self.networkNode.endAnimMatcher.listConnections()[0]
            
            alignPointOrient(startAnimMatcher, startAnim, 1, 1)
            alignPointOrient(midAnimMatcher, midAnim, 1, 1)
            alignPointOrient(endAnimMatcher, endAnim, 1, 1)
            
            if reverseEndAimer != None:
                reverseEndAimer.rotate.set(0,0,0)
            
            
            
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []   
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
   
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKSPlineChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            for inc in xrange(len(control_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
        raise Exception("FKIKSplineChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or fk joint ")
    
    def getAllAnims(self):
        allAnims = []
        allAnims.append(self.networkNode.startAnim.listConnections()[0])
        allAnims.append(self.networkNode.midAnim.listConnections()[0])
        allAnims.append(self.networkNode.endAnim.listConnections()[0])
        try:
            rea = self.networkNode.reverseEndAimer.listConnections()[0]
            allAnims.append(rea)
        except:
            """ Skip """
        allAnims.append(self.networkNode.switchGroup.listConnections()[0])
        map(lambda x: allAnims.append(x), self.networkNode.FKJoints.listConnections())
        return allAnims

    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''        
        anims = []
        anims.append(self.networkNode.startAnim.listConnections()[0])
        anims.append(self.networkNode.midAnim.listConnections()[0])
        anims.append(self.networkNode.endAnim.listConnections()[0])
        try:
            rea = self.networkNode.reverseEndAimer.listConnections()[0]
            anims.append(rea)
        except:
            """ Skip """
        map(lambda x: anims.append(x), self.networkNode.FKJoints.listConnections()[:-1])
        for anim in anims:
            resetAttrs(anim)
            
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        printWarning("FKIKSplineChain.mirror: not yet implemented")
        

class FKIKSplineTail(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = '', numIKAnims = 3, numDetailAnims = 5): 
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKSplineTail'):
                    self.networkNode = node
                else:
                    printError("FKIKSplineTail: node %s is not a FKIKSplineTail metaNode"%(node))
            else:
                printError("FKIKSplineTail: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKIKSplineTail', 1.0, 'Switchable FK/IK spline chain meant for use as a long tail with detail controls on the tip', side, bodyPart, startJoint, endJoint)

            chain = chainBetween(startJoint, endJoint)
            bind_joints = filter(lambda obj: PyNode(obj).type() == 'joint', chain)
            compName = side+'_'+bodyPart

            # Main chain driven by both IK/FK setup
            control_joints = duplicateChain(bind_joints[0], bind_joints[-2], 'bind', 'ctrl')



            # IK SPLINE CONTROL RIG

            # Chain influenced by ik joints
            ik_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'ik') 
            rename(ik_joints[-1], compName+'_ik_end_joint')

            # Curve
            ik_curve = createCurveThroughObjects(ik_joints, degree=len(ik_joints)/2)
            rename(ik_curve, compName+'_curve')
            ik_curve.inheritsTransform.set(0)

            # IK Spline Handle
            ik = ikHandle(sol='ikSplineSolver', ccv=False, c=ik_curve, sj=ik_joints[0], ee=ik_joints[-1])

            # Create anims
            animLocs = mu.locatorsOnCurve(ik_curve, numIKAnims, method='motionPath')
            animLocsParent = animLocs[0].getParent()

            ik_anims = []
            zeroGrps = []

            for i in xrange(numIKAnims):
                select(cl=1)
                anim = joint(n = compName+'_ik_'+str(i+1)+'_anim')
                addAnimAttr(anim)
                crcle = circle(nr=(0,1,0), ch=0)[0]
                appendShape(crcle, anim)
                delete(crcle)
                ik_anims.append(anim)
                
                loc = animLocs[i]
                delete(parentConstraint(loc, anim, mo=0))
                
                zeroGrp = createZeroedOutGrp(anim)
                zeroGrps.append(zeroGrp)
                
                if (i == 0):
                    lockAndHideAttrs(anim, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
                else:
                    lockAndHideAttrs(anim, ['sx', 'sy', 'sz', 'v', 'radius'])
                
                
            delete(animLocsParent)

            # Create IK Spline curve control joints
            ik_ctrl_jnts = []

            for anim in ik_anims:
                select(cl=1)
                cj = joint(n=anim.shortName()+'_ctrl_jnt')
                ik_ctrl_jnts.append(cj)
                parentConstraint(anim, cj, mo=0)

            # Bind IK Spline curve to the control joints
            skinCluster(ik_ctrl_jnts, ik_curve)


            # IK SPLINE TIP DETAIL CONTROL RIG
            # TODO: Error check number of anims

            # Create FK anims for detail joint chain
            detail_anims = duplicateChain(chain[-numDetailAnims-1], chain[-2], 'bind', 'detail') # Skip end joint
            detail_control_joints = duplicateChain(chain[-numDetailAnims-1], chain[-2], 'bind', 'detail_control')
            detail_anim_constraints = []
            
            for i in xrange(numDetailAnims):
                anim = detail_anims[i]
                addAnimAttr(anim)
                crcle = circle(nr=(1,0,0), ch=0)[0]
                scale(crcle, .5, .5, .5)
                makeIdentity(crcle, s=1, r=0, t=0, a=1)
                appendShape(crcle, anim)
                delete(crcle)
                
                zeroGrp = createZeroedOutGrp(anim)
                zeroGrps.append(zeroGrp)
                
                # Detail anim needs to be constrained to both its normal parent and
                # a joint on the ik chain so it can switch between
                corresponding_ctrl_joint = detail_control_joints[i]
                corresponding_ik_joint = ik_joints[i-numDetailAnims-1]
                
                if (i == 0): 
                    fk_parent = corresponding_ik_joint.getParent()
                    origin_to_fk_parent = spaceLocator(n=anim.shortName()+'_origin_loc')
                    delete(parentConstraint(anim, origin_to_fk_parent, mo=0))
                    hide(origin_to_fk_parent)
                    parent(origin_to_fk_parent, fk_parent)
                    parentConstraint(origin_to_fk_parent, zeroGrp, mo=1)
                    
                # Setup detail anim control chain
                pc = parentConstraint([corresponding_ik_joint, anim], corresponding_ctrl_joint, mo=0)
                pc.interpType.set(2) # Set interp to "Shortest"
                detail_anim_constraints.append(pc)
              
              
            # Add attribute to the root detail anim to control visibility and
            # presence of the control rig
            ik_anims[0].addAttr('followTailTipCurve', keyable=1, dv=1, min=0, max=1)
            follow_attr = ik_anims[0].attr('followTailTipCurve')
            
            for i in xrange(0, numDetailAnims):
                anim = detail_anims[i]
                pc = detail_anim_constraints[i]
                pcWeightAttrs = pc.getWeightAliasList()
                
                follow_attr.set(1)
                
                anim.visibility.set(0)
                pcWeightAttrs[0].set(1)
                pcWeightAttrs[1].set(0)
                setDrivenKeyframe(anim.visibility, cd=follow_attr, itt='stepnext', ott='stepnext')
                setDrivenKeyframe(pcWeightAttrs[0], cd=follow_attr, itt='linear', ott='linear')
                setDrivenKeyframe(pcWeightAttrs[1], cd=follow_attr, itt='linear', ott='linear')
                
                follow_attr.set(0)
                
                anim.visibility.set(1)
                pcWeightAttrs[0].set(0)
                pcWeightAttrs[1].set(1)
                setDrivenKeyframe(anim.visibility, cd=follow_attr, itt='stepnext', ott='stepnext')
                setDrivenKeyframe(pcWeightAttrs[0], cd=follow_attr, itt='linear', ott='linear')
                setDrivenKeyframe(pcWeightAttrs[1], cd=follow_attr, itt='linear', ott='linear')
                
            follow_attr.set(1)

            # Lock and hide attrs on the detail anims.  We had to was until after setting the SDKs.
            for anim in detail_anims:
                lockAndHideAttrs(anim, ('tx', 'ty', 'tz','sx', 'sy','sz','v', 'radius'))
                


            # FK CONTROL RIG

            # Chain influenced by fk joints
            fk_anims = duplicateChain(bind_joints[0], bind_joints[-2]) 

            for i in xrange(len(fk_anims)):
                anim = fk_anims[i]
                anim.rename(compName+'_fk_'+str(i+1)+'_anim')
                addAnimAttr(anim)
                crcle = circle(nr=(1,0,0), ch=0)[0]
                scale(crcle, .5, .5, .5)
                makeIdentity(crcle, s=1, r=0, t=0, a=1)
                appendShape(crcle, anim)
                delete(crcle)
                
                zeroGrp = createZeroedOutGrp(anim)
                zeroGrps.append(zeroGrp)
                


            # HOOK FK/IK CONTROL RIGS TOGETHER

            # FK/IK switcher
            switchGroup = group(n = compName+'_FKIK_switch', em=1)
            switchGroup.addAttr('FKIK_switch', keyable=1)
            switchGroup.FKIK_switch.setMax(1)
            switchGroup.FKIK_switch.setMin(0)
            switchRev = createNode('reverse')
            switchGroup.FKIK_switch >> switchRev.inputX

            # Add visibility for guide curve
            ik_anims[0].addAttr('showGuideCurve', keyable=0, dv=1, min=0, max=1)
            visAttr = ik_anims[0].attr('showGuideCurve')
            visAttr.showInChannelBox(1)
            visAttr >> ik_curve.visibility
            
            ik_curve_shape = ik_curve.getShape()
            ik_curve_shape.overrideEnabled.set(1)
            ik_curve_shape.overrideColor.set(0)
            ik_curve_shape.overrideDisplayType.set(1)
            
            # Tail guide curve vis group
            tail_vis_grp = group(ik_curve, n=compName+'_curve_vis_grp')
            switchGroup.FKIK_switch >> tail_vis_grp.visibility
            
            # All important joints on the ik component
            ik_jnts_complete_list = ik_joints[0:-numDetailAnims-1] + detail_control_joints 

            for i in xrange(len(control_joints)):
                ikJnt = ik_jnts_complete_list[i]
                fkJnt = fk_anims[i]
                ctrlJnt = control_joints[i]
                bindJnt = bind_joints[i]
                
                parentConstraint(ctrlJnt, bindJnt, mo=0)
                
                pc = parentConstraint([ikJnt, fkJnt], ctrlJnt, mo=0)
                pc.interpType.set(2) # Set interp to "Shortest"
                pcWeightAttrs = pc.getWeightAliasList()
                
                # Hook switcher up to the chains
                switchGroup.FKIK_switch >> pcWeightAttrs[0]
                switchRev.outputX >> pcWeightAttrs[1]
            
            # Hook switcher up to anim visibilities
            switchRev.outputX >> fk_anims[0].getParent().visibility
            switchGroup.FKIK_switch >> detail_anims[0].getParent().visibility
            for ikAnim in ik_anims:
                switchGroup.FKIK_switch >> ikAnim.getParent().visibility
            
            

            # ORGANIZE
            for zeroGrp in zeroGrps+[tail_vis_grp]:
                lockAndHideAttrs(zeroGrp, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            
            doNotTouchGrp = group(n=compName+'_DO_NOT_TOUCH_grp', em=1)
            parent([ik[0], ik_joints[0], control_joints[0], detail_control_joints[0]]+ik_ctrl_jnts, doNotTouchGrp)
            for obj in doNotTouchGrp.getChildren():
                hide(obj)
            parent(ik_curve.getParent(), doNotTouchGrp)

            animGrp = group(n=compName+'_anims_grp', em=1)
            parent(map(lambda a: a.getParent(), [fk_anims[0], detail_anims[0]]+ik_anims), animGrp)
            parent(switchGroup, animGrp)

            mainGrp = group(n=compName+'_main_grp', em=1)
            parent([doNotTouchGrp, animGrp], mainGrp)

            parentConstraint(mainGrp, switchGroup, mo=0)
            lockAndHideAttrs(switchGroup, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            switchGroup.FKIK_switch.set(1)
            
          
            # CONNECT TO META SYSTEM
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(ik_jnts_complete_list, self.networkNode, 'IKJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectChainToMeta(ik_anims+detail_anims+fk_anims+[switchGroup], self.networkNode, 'anims')
            connectToMeta(switchGroup, self.networkNode, 'switchGroup')
            self.networkNode.setAttr('switchAttr', 'FKIK_switch', f=1)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
            
    def getSwitchAttr(self):
        switchNode = self.networkNode.switchGroup.listConnections()[0]
        switchAttrName = self.networkNode.switchAttr.get()
        return switchNode.attr(switchAttrName)
        
    def alignSwitch(self):
        '''
        toggle between FK and IK while keeping current joint placement
        '''
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        switchAttr = self.networkNode.switchAttr.get()
        attr = switchGroup.attr(switchAttr)
        
        # Switch IK -> FK.
        # Straight forward exact match
        if switchGroup.attr(switchAttr).get() >= .5:
            
            control_joints = self.networkNode.controlJoints.listConnections()
            anims = self.networkNode.anims.listConnections()
            fk_anims = filter(lambda a: '_fk_' in str(a), anims)

            for i in xrange(len(control_joints)):
                cj = control_joints[i]
                fk = fk_anims[i]

                fk.rotate.set(cj.rotate.get())
            
        # Switch FK -> IK.
        # Approximate match.  
        else:
            
            """
            """
        
        # Toggle the switcher
        attr.set(1-attr.get())
        
    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []   
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        
        
    def getAllAnims(self):
        '''
        Returns a list of all the anims
        '''
        allAnims = self.networkNode.anims.listConnections()
        return allAnims
        
        
    def toDefaultPose(self):
        '''
        Sets all anims to their default pose
        '''
        allAnims = self.getAllAnims()
        for anim in allAnims:            
            resetAttrs(anim)
            
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        printWarning("FKIKSplineTail.mirror: not yet implemented")
        

        
class FKIKSplineFollow(RigComponent):
    
    def __init__(self, side, bodyPart, startJoint, endJoint, skinnedMeshToFollow=None, curveCreationDirection=(0,0,1), numIkAnims=3, node = ''):
        '''
        An FKIK Spline Chain that is driven by curves which are created following the contour of the
        joint chain.  These curves can be set to follow a skinned mesh.  The chain can also use partial
        or full FK control starting from the tip going down to the root of the chain.
        
        Assumes x-axis (pos or neg) is pointing down the joint.
        
        side:
            Side of the face.
        
        bodyPart:
            Unique label of this component.
            
        startJoint:
            Base joint of the chain.
            
        endJoint:
            End joint of the chain.  Should be an "end cap" joint, meaning it
            won't actually get a corresponding anim.
            
        skinnedMeshToFollow:
            If specified, the curves controlling the joint chain will follow along with an already
            skinned mesh: They will be skinned then have the mesh's weight's copied over to them.
            
        curveCreationDirection:
            The direction from the joint chain the driving curve will be created.  Another driving
            curve will be created using negative curveCreationDirection.
            
        numIkAnims:
            Number of manual ik anims available on the follow chain.
        '''
    
        # REQUISITE META SETUP
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKSplineFollow'):
                    self.networkNode = node
                else:
                    printError("FKIKSplineFollow: node %s is not an FKIKSplineFollow metaNode"%(node))
            else:
                printError("FKIKSplineFollow: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        # Initiate the component
        RigComponent.__init__(self, 'FKIKSplineFollow', 1.0, 'FKIK spline chain that can be set up to follow another skinned mesh', side, bodyPart)
        compName = '%s_%s'%(side, bodyPart)
        
        # START COMPONENT SETUP
        
        chain = chainBetween(startJoint, endJoint)
        chain = map(lambda obj: PyNode(obj), chain)
        
        ikSplineChain = duplicateChain(startJoint, endJoint)
        for i in xrange(len(ikSplineChain)):
            ikSplineChain[i].rename(compName+'_'+str(i)+'_ikSplineJnt')
        
        # Create NURBS plane for the IK Spline to follow
        leftCurve = createCurveThroughObjects(chain, offset=curveCreationDirection)
        rightCurve = createCurveThroughObjects(chain, offset=-dt.Vector(curveCreationDirection))
        
        # - Force curves to travel through their CVs
        # - These curves will form the basis of the following behavior
        # - These curves won't have all the deformation layers necessary for the final output, but we need them for the ik anim parents
        leftFollowCurve = fitBspline(leftCurve, ch=0, tol=0.01, n=compName+'_leftCurve')[0] 
        rightFollowCurve = fitBspline(rightCurve, ch=0, tol=0.01, n=compName+'_rightCurve')[0]
        
        # - Curves with following behavior that will also stack on ik anim movement
        leftPoseCurve = duplicate(leftFollowCurve, n=compName+'_leftPoseCurve')[0]
        rightPoseCurve = duplicate(rightFollowCurve, n=compName+'_rightPoseCurve')[0]
        
        ikSplinePlane = loft(leftPoseCurve, rightPoseCurve, ch=1, ss=1, d=3, ar=1, c=0, rn=0, po=0, rsn=0, n=compName+'_mainFollowPlane')[0]
        delete(leftCurve, rightCurve)
        
        # Create curve that will follow the plane and be the nurbsIKChain
        select(ikSplinePlane.u[.5], sym=1)
        ikSplineCurve = PyNode(duplicateCurve(ch=1, rn=0, local=0, n=compName+'_mainFollowCrv')[0])
        
        # IK Spline handle
        ik = ikHandle(sol='ikSplineSolver', ccv=False, c=ikSplineCurve, sj=ikSplineChain[0], ee=ikSplineChain[-1], n=compName+'_ikSplineHandle')[0]
        
        # Create locators that the main chain can connect to later
        followLocs = []
        followLocsGrp = group(em=1, n=compName+'_followLocsGrp')
        
        for i in xrange(len(chain)-1):
            mainJnt = chain[i]
            splineJnt = ikSplineChain[i]
            
            # Locator that indirectly follows an IK Spline joint:
            # 1) Its position will be determined by the IK Spline joint
            # 2) Its rotation will be the normal of the NURBs plane
            followLoc = spaceLocator(n=str(mainJnt)+'_followLoc')
            followLocs.append(followLoc)
            parent(followLoc, followLocsGrp)
            
            # IK Spline handle position -> Follow joint position
            pointConstraint(splineJnt, followLoc, mo=0)
            
            # Normal direction of the NURBS plane -> Orientation of follow joint
            normalConstraint(   ikSplinePlane,
                                followLoc,
                                aim=[0,1,0],
                                u=[1,0,0],
                                wu=[1,0,0],
                                wut='objectrotation',
                                wuo=splineJnt    )
        
        # Create FK alternate control scheme
        fkChain = duplicateChain(startJoint, endJoint)
        delete(fkChain[-1])
        del fkChain[-1]
        makeIdentity(fkChain, r=1, a=1)
        
        # Component anchor
        mainGrp = group(em=1, n=compName+'_component_group')
        
        # Connect FK and IK chains up to the main chain
        fkIkPcs = []
        fkParentPcs = []
        zeroGrps = []
        zeroGrpsGrp = group(em=1, n=compName+'_zeroGrps')
        
        for i in xrange(len(chain)-1):
            pc = parentConstraint(followLocs[i], fkChain[i], chain[i], mo=1)
            pc.interpType.set(2)
            fkIkPcs.append(pc)
        
            anim = fkChain[i]
            anim.rename(compName+'_fk_'+str(i+1)+'_anim')
            addAnimAttr(anim)
            crcle = circle(nr=(1,0,0), ch=0)[0]
            scale(crcle, 1, 1, 1)
            makeIdentity(crcle, s=1, r=0, t=0, a=1)
            appendShape(crcle, anim)
            delete(crcle)
            
            zeroGrp = createZeroedOutGrp(anim)
            
            # Fk chain parent targets: Its own parent or the IK Spline locator
            if (i != 0):
                parent(zeroGrp, w=1)
                fkPc = parentConstraint(followLocs[i], fkChain[i-1], zeroGrp, mo=1)
                
            else:
                fkPc = parentConstraint(followLocs[0], zeroGrp, mo=1)
                
            fkPc.interpType.set(2)
            fkParentPcs.append(fkPc)
            
            zeroGrps.append(zeroGrp)
            parent(zeroGrp, zeroGrpsGrp)
        
        
        # Create manual IK control on top of the automatic IK follow control
        # - Set up curves for the follow curves to use as blendshapes
        manualIKGrp = group(em=1, n=compName+'_manual_ik_grp')
        
        leftIkCurve = duplicate(leftPoseCurve, n=compName+'_leftIkCurve')[0]
        rightIkCurve = duplicate(rightPoseCurve, n=compName+'_rightIkCurve')[0]
        
        leftCurveBs = blendShape(leftIkCurve, leftPoseCurve, foc=1, weight=(0,1))[0]
        rightCurveBs = blendShape(rightIkCurve, rightPoseCurve, foc=1, weight=(0,1))[0]
        
        # - Set up plane for IK anims to follow (since the other plane will be driven
        #   by these anims
        ikAnimPlane = loft(leftFollowCurve, rightFollowCurve, ch=1, ss=1, d=3, ar=1, c=0, rn=0, po=0, rsn=0, n=compName+'_ikAnimPlane')[0]
        ikCurveDrivers = []
        ikAnims = []
        
        for i in xrange(numIkAnims):
            select(cl=1)
            vValue = i*(1.0/(numIkAnims-1))
            ikAnimParent = group(em=1, n=compName+'_'+str(i+1)+'_ik_anim_zero_grp')
            ikAnim = joint(n=compName+'_'+str(i+1)+'_ik_anim')
            parent(ikAnim, ikAnimParent)
            nc = nurbsConstraint(ikAnimPlane, ikAnimParent, .5, vValue)
            
            ikCurveDriverParent = group(em=1, n=compName+'_'+str(i)+'_curveDriver_grp')
            ikCurveDriver = joint(n=compName+'_'+str(i)+'_curveDriver')
            parent(ikCurveDriver, ikCurveDriverParent)
            delete(parentConstraint(ikAnimParent, ikCurveDriverParent, mo=0))
            
            parent(ikCurveDriverParent, nc[1], manualIKGrp)
            
            ikAnim.t >> ikCurveDriver.t
            ikAnim.r >> ikCurveDriver.r
            
            ikCurveDrivers.append(ikCurveDriver)
            
            # Finish ik anim setup
            ikAnims.append(ikAnim)
            zeroGrps.append(ikAnimParent)
            crcle = circle(nr=(1,0,0), ch=0)[0]
            scale(crcle, 2, 2, 2)
            makeIdentity(crcle, s=1, r=0, t=0, a=1)
            appendShape(crcle, ikAnim)
            delete(crcle)
            parent(ikAnimParent, zeroGrpsGrp)
            addAnimAttr(ikAnim)
            
            # If this is the root ik anim, it is desginated the "main" anim
            # and gets the ability to toggle the fk anims
            if (i == 0):
            
                # IK/FK anim switch
                numFkSegments = len(fkChain)
                
                select(cl=1)
                ikAnim.rename(compName+'_main_anim')
                ikAnimParent.rename(compName+'_main_anim_zero_grp')
                ikAnim.addAttr('FkAnimsInUse', keyable=1, min=0, max=numFkSegments, dv=0)
                switchAttr = ikAnim.FkAnimsInUse
                
                # Create a toggle for each individual FK anim starting from the tip of the
                # chain and going down to the root, driven by one attribute
                for i in xrange(numFkSegments):
                    
                    fkIndex = numFkSegments-i-1
                    
                    anim = fkChain[fkIndex]
                    zeroGrp = zeroGrps[fkIndex]
                    pc = fkIkPcs[fkIndex]
                    fkPc = fkParentPcs[fkIndex]
                    
                    mu.sdk(switchAttr, [i, i+1], zeroGrp.v, [0, 1], itt='clamped', ott='stepnext')
                    
                    mu.sdk(switchAttr, [i, i+1], pc.w0, [1, 0], itt='linear', ott='linear')
                    mu.sdk(switchAttr, [i, i+1], pc.w1, [0, 1], itt='linear', ott='linear')
                
                    # Skip fk parentConstraint on the first control since it won't need to switch
                    if fkIndex != 0:
                        mu.sdk(switchAttr, [i, i+1], fkPc.w0, [1, 0], itt='linear', ott='linear')
                        mu.sdk(switchAttr, [i, i+1], fkPc.w1, [0, 1], itt='linear', ott='linear')

        parent(leftIkCurve, rightIkCurve, ikAnimPlane, manualIKGrp)
                        
        # Hook up driver joints to the manual ik curves
        for curveBs in [leftIkCurve, rightIkCurve]:
            select(ikCurveDrivers)
            select(curveBs, add=1)
            skinCluster(tsb=1, dr=3.0)
        
        
        # Organize
        anims = fkChain+ikAnims
        
        for obj in [zeroGrpsGrp,
                    followLocsGrp,
                    ik,
                    ikSplinePlane,
                    ikSplineCurve,
                    manualIKGrp]:
            obj.inheritsTransform.set(0)
            parent(obj, mainGrp)
        
        parent(leftFollowCurve, rightFollowCurve, leftPoseCurve, rightPoseCurve, ikSplineChain[0], mainGrp)
        
        # Lock attrs
        for anim in fkChain:
            lockAndHideAttrs(anim, ['t', 's', 'v', 'radius'])
        for anim in ikAnims:
            lockAndHideAttrs(anim, ['s', 'v', 'radius'])
        
        # Hide stuff
        hide(followLocsGrp, ik, ikSplineChain[0], ikSplinePlane, ikSplineCurve,
             leftFollowCurve, rightFollowCurve, manualIKGrp, leftPoseCurve, rightPoseCurve)

        # HOOK UP TO META SYSTEM
        connectChainToMeta(anims, self.networkNode, 'anims')
        connectChainToMeta(fkChain, self.networkNode, 'fkAnims')
        connectChainToMeta(ikAnims, self.networkNode, 'ikAnims')
        connectChainToMeta(followLocs, self.networkNode, 'followLocs')
        connectToMeta(leftFollowCurve, self.networkNode, 'leftFollowCurve')
        connectToMeta(rightFollowCurve, self.networkNode, 'rightFollowCurve')
        connectToMeta(leftPoseCurve, self.networkNode, 'leftPoseCurve')
        connectToMeta(rightPoseCurve, self.networkNode, 'rightPoseCurve')
        connectToMeta(ikSplineCurve, self.networkNode, 'mainFollowCurve')
        connectToMeta(ikSplinePlane, self.networkNode, 'followSurface')
        
        connectToMeta(mainGrp, self.networkNode, 'componentGrp')
        
        # Optional way to hook up the follow chain to a skinCluster immediately
        if (skinnedMeshToFollow != None):
            self.followSkinnedMesh(skinnedMeshToFollow)
            
            
    def followSkinnedMesh(self, skinnedMeshToFollow):
        '''
        Drive the IK spline chain by skinning the follow curves and copying influences/weights
        over from a specified skin mesh.  This replaces whatever was previously driving the curves.
        '''
        
        if skinnedMeshToFollow == None:
            raise Exception('FKIKSplineFollow.followSkinnedMesh: Please specify a skinned mesh/surface.')
        
        skinnedMeshToFollow = PyNode(skinnedMeshToFollow)
        
        if isinstance(skinnedMeshToFollow, nt.Transform):
            skinnedMeshToFollow = skinnedMeshToFollow.getShape()
            
        if (skinnedMeshToFollow == None):
            raise Exception('FKIKSplineFollow.followSkinnedMesh: No skinned mesh/surface specified.')
        
        leftFollowCurve = self.networkNode.leftFollowCurve.listConnections()[0]
        rightFollowCurve = self.networkNode.rightFollowCurve.listConnections()[0]
        leftPoseCurve = self.networkNode.leftPoseCurve.listConnections()[0]
        rightPoseCurve = self.networkNode.rightPoseCurve.listConnections()[0]
        
        # Find the skinCluster
        skin = listConnections(skinnedMeshToFollow, type='skinCluster')
        if (len(skin) == 0):
            raise Exception('FKIKSplineFollow.followSkinnedMesh: No skinCluster found.')
        else:
            skin = skin[0]
            
        # Query skinCluster information
        influences = skin.getInfluence()
        skinMethod = skin.getSkinMethod()
        bindMethod = skin.getBindMethod()
        
        # Create skinCluster and copy over weights for each curve
        for c in [leftFollowCurve, rightFollowCurve, leftPoseCurve, rightPoseCurve]:
            '''delete(c, ch=1) # Messes with blendShape '''
            c.inheritsTransform.set(0)
            select(influences, c)
            cSkin = skinCluster(toSelectedBones=1, obeyMaxInfluences=0, nw=1, sm=skinMethod, bm=bindMethod, n=str(c)+'_skinCluster')
            copySkinWeights(ss=skin, ds=cSkin, noMirror=1, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
    
    
    def getAllAnims(self):
        '''
        Returns a list of all the anims
        '''
        return self.networkNode.anims.listConnections()
        
        
    def toDefaultPose(self):
        '''
        Moves the component into its bind position
        '''
        for anim in self.getAllAnims():
            resetAttrs(anim)
            
            
    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        Connects this component to another component.  For this particular component, however,
        if followSkinnedMesh has been called connectToComponent has no influence. 
        
        comp:
            The component to attach to.
        location:
            The place where the components connect, ex, start, end, jointName.
        point:
            Attach by translation.
        orient:
            Attach by orientation.
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans, w=1, mo=1)
            
            
        
class FKIKSpine(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = ''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKSpine'):
                    self.networkNode = node
                else:
                    printError("FKIKSpine: node %s is not a FKIKSpine metaNode"%(node))
            else:
                printError("FKIKSpine: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKIKSpine', 1.0, 'has ik stretchy spine, and fk with pelvis', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            bind_joints = []
            for item in chain:
                item = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
            #create chains
            ik_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'ik')
            rev_joints = duplicateChain(bind_joints[0], bind_joints[1], 'bind', 'reverse')
            fk_joints = duplicateChain(bind_joints[1], bind_joints[-1], 'bind', 'fk')
            fk_control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'fk_control')
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
            
            
            #create FK
                #reverse
            returns = createReverseChain(rev_joints[0], rev_joints[1], side + "_pelvis")
            pelvis_anim = returns[0]
            pelvis_anim_grp = returns[1]
            pelvis_joint_grp = returns[2]
            
            
                #fk
            inc = 1
            for obj in fk_joints[:-1]:
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius'])
                obj.v.set(keyable = 0)
                addAnimAttr(obj)
                obj.rename('%s_%i_anim'%(compName, inc))
                inc+=1
                
                #connect To FK_control
            
            parentConstraint(rev_joints[0], fk_control_joints[0], w=1, mo=1)
            inc=1
            for x in fk_joints[:-1]:
                parentConstraint(x,fk_control_joints[inc],w=1, mo=1)
                inc+=1
            
            #create IK
            returns = createNurbsPlaneIKChain(ik_joints[0], ik_joints[-1], compName)
            startAnim = returns[0]
            midAnim = returns[1]        
            endAnim = returns[2]        
            ik_animGrp = returns[3]        
            ik_joints_grp = returns[4]     
            nurbsPlane = returns[5]     
            transGrp = returns[6]         
            dummyGrp = returns[7]         
            ikLocGrp = returns[8]        
            distDimGrp = returns[9]        
            
            control_joint_grp = group(control_joints[0], n = '%s_control_joints'%compName)
            for cj in control_joints[1:]:
                control_joint_grp | cj
            
            select(cl=1)
            switchGroup = group(n = '%s_FKIK_switch'%compName)
            switchGroup.addAttr('FKIK_switch', keyable = 1)
            switchGroup.FKIK_switch.setMax(1)
            switchGroup.FKIK_switch.setMin(0)
            switchGroup.FKIK_switch.setKeyable(1)
            rev = createNode('reverse')
            switchGroup.FKIK_switch >> rev.inputX
            #set up control joint constraints
            for inc in xrange(len(control_joints)):
                constpar = parentConstraint(fk_control_joints[inc], ik_joints[inc], control_joints[inc])
                #constscl = scaleConstraint(fk_control_joints[inc], ik_joints[inc], control_joints[inc], skip=['y','z'])
                rev.outputX >> constpar.w0
                #rev.outputX >> constscl.w0
                switchGroup.FKIK_switch >> constpar.w1
                #switchGroup.FKIK_switch >> constscl.w1
            lockAndHideAttrs(switchGroup, ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy','sz','v'))
            
            switchGroup.FKIK_switch >> ik_animGrp.visibility
            rev.outputX >> pelvis_anim_grp.visibility
            rev.outputX >> fk_joints[0].visibility
            
            #connect to bind joints
            allowSafeScale(bind_joints[0], bind_joints[-1])
            for inc in xrange(len(bind_joints)):
                parentConstraint(control_joints[inc], bind_joints[inc], w=1, mo=1)
                #scaleConstraint(control_joints[inc], bind_joints[inc], w=1, mo=1, skip = ['y','z']), test
                
                
            #grouping
            select(cl=1)
            jointGrp = group([ik_joints_grp, fk_joints[0], rev_joints[0], fk_control_joints[0],pelvis_joint_grp, control_joint_grp],n='%s_joint_grp'%compName)
            dntGrp = group([nurbsPlane,    transGrp,dummyGrp,ikLocGrp,    distDimGrp], n = "%s_DO_NOT_TOUCH_grp"%compName)
            animGrp = group(ik_animGrp, pelvis_anim_grp,switchGroup)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            #hide
            switchGroup.FKIK_switch.set(1)
            
            dntGrp.hide()
            switchGroup.FKIK_switch >> ik_joints[0].v
            
            
            #connect To Meta
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(ik_joints, self.networkNode, 'IKJoints')
            connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
            connectToMeta(pelvis_anim, self.networkNode, 'pelvisAnim')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectToMeta(startAnim, self.networkNode, 'startAnim')
            connectToMeta(midAnim, self.networkNode, 'midAnim')
            connectToMeta(endAnim, self.networkNode, 'endAnim')
            connectToMeta(switchGroup, self.networkNode, 'switchGroup')
            self.networkNode.setAttr('switchAttr', 'FKIK_switch', f=1)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
    
    def alignSwitch(self):
        #NOT TRULY IMPLEMENTED
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        switchAttr = self.networkNode.switchAttr.get()
        attr = switchGroup.attr(switchAttr)
        attr.set(1-attr.get())
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []   
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
   
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKSpine.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            for inc in xrange(len(control_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
        raise Exception("FKIKSpine.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or fk joint ")
    
    def getAllAnims(self):
        allAnims = []
        
        '''
        Get the first connected node and append it to the list.
        If there are no connections don't do anything.
        '''
        def addFirstConnection(addToList, obj):
            if obj == None or addToList == None: return None
            connections = obj.listConnections()
            if len(connections) > 0: addToList.append(connections[0])
        
        addFirstConnection(allAnims, self.networkNode.startAnim)
        addFirstConnection(allAnims, self.networkNode.midAnim)
        addFirstConnection(allAnims, self.networkNode.endAnim)
        addFirstConnection(allAnims, self.networkNode.switchGroup)
        addFirstConnection(allAnims, self.networkNode.pelvisAnim)
        map(lambda x: allAnims.append(x), self.networkNode.FKJoints.listConnections()[:-1])
        return allAnims

    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''        
        anims = []
        anims.append(self.networkNode.startAnim.listConnections()[0])
        anims.append(self.networkNode.midAnim.listConnections()[0])
        anims.append(self.networkNode.endAnim.listConnections()[0])
        anims.append(self.networkNode.pelvisAnim.listConnections()[0])
        map(lambda x: anims.append(x), self.networkNode.FKJoints.listConnections()[:-1])
        for anim in anims:
            resetAttrs(anim)
            
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        printWarning("FKIKSpine.mirror: not yet implemented")
    
class FKIKChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node=''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKChain'):
                    self.networkNode = node
                else:
                    printError("FKIKChain: node %s is not a FKIKChain metaNode"%(node))
            else:
                printError("FKIKChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKIKChain', 1.0, 'chain that can switch between Fk and IK', side, bodyPart, startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            for item in chain:
                item  = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
                    
            #create and connect ik, fk, control and bind joints to meta
            FK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "FK")
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
            IK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "IK")
            
            if FK_joints[0].name().endswith("1"):
                FK_joints[0].rename(FK_joints[0].name().replace("1", '', -1))
            
            #connect FK joints
            for obj in FK_joints[:-1]:
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius'])
                obj.v.set(keyable = 0)
                addAnimAttr(obj)
                obj.rename(obj.name().replace('joint', 'anim'))
            
            #connect IK Joints
            
            #IKHandle
            buf = ikHandle(startJoint = IK_joints[0], endEffector = IK_joints[2], sol = 'ikRPsolver', w=1)
            ik = buf[0]
            ik.rename('%s_ik'%compName)
            eff = buf[1]
            eff.rename('%s_eff'%compName)
            
            
            #Ik anim
            select(cl=1)
            animJoint = joint()
            labels = getJointLabels(IK_joints[2])
            animJoint.rename("%s_%s_ik_anim"%(labels[0], labels[1]))
            addAnimAttr(animJoint)
            
            cube = polyCube()[0]
            appendShape(cube, animJoint)
            delete(cube)
            
            alignPointOrient(IK_joints[2], animJoint, 1,1)
            ikGrp = group(ik, n = "ik_anim_control_grp")
            pointConstraint(animJoint, ikGrp, w=1, mo=1)
            animJointGrp = createZeroedOutGrp(animJoint)
            animJoint.v.set(keyable = 0)
            orientConstraint(animJoint, IK_joints[-1], mo=1, w=1)
            
            
            #PV
            pvLoc = createPVLocator(FK_joints[0], FK_joints[1], FK_joints[2])
            labels = getJointLabels(IK_joints[1])
            select(cl=1)
            pvJoint = joint()
            pvJoint.rename("%s_%s_pv_anim"%(labels[0], labels[1]))
            sphere = polySphere()[0]
            appendShape(sphere, pvJoint)
            alignPointOrient(pvLoc, pvJoint, 1,0)
            alignPointOrient(IK_joints[1], pvJoint, 0,1)
            addAnimAttr(pvJoint)
            delete(pvLoc)
            delete(sphere)
            poleVectorConstraint(pvJoint, ik, w=1)
            pvJointGrp = createZeroedOutGrp(pvJoint)
            pvJoint.v.set(keyable = 0)
            
            
            #connect IK and FK to the control
            select(cl=1)
            switchGroup = group(n = '%s_FKIK_switch'%compName)
            switchGroup.addAttr('FKIK_switch', keyable = 1)
            switchGroup.FKIK_switch.setMax(1)
            switchGroup.FKIK_switch.setMin(0)
            switchGroup.FKIK_switch.setKeyable(1)
            rev = createNode('reverse')
            switchGroup.FKIK_switch >> rev.inputX
            for inc in xrange(len(FK_joints)):
                const = parentConstraint(FK_joints[inc], IK_joints[inc], control_joints[inc])    
                rev.outputX >> const.w0
                switchGroup.FKIK_switch >> const.w1
            lockAndHideAttrs(switchGroup, ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy','sz','v'))
                
            #connect control joints to bind joints
            for inc in xrange(len(FK_joints)):#-1
                parentConstraint(control_joints[inc], bind_joints[inc])
            
            lockAndHideAttrs(animJoint, ['sx','sy','sz','radius'])
            lockAndHideAttrs(pvJoint, ['rx', 'ry', 'rz','sx','sy','sz','radius'])    
                
            #grouping
            select(cl=1)
            jointGrp = group([FK_joints[0], IK_joints[0], control_joints[0]],n='%s_joint_grp'%compName)
            animGrp = group([animJointGrp, pvJointGrp, switchGroup], n = "%s_anim_grp"%compName)
            animGrp.inheritsTransform.set(0)
            
            dntGrp = group([ikGrp], n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            #hiding
            control_joints[0].hide()
            dntGrp.hide()
            switchGroup.FKIK_switch >> IK_joints[0].visibility
            rev.outputX >> FK_joints[0].visibility
            switchGroup.FKIK_switch >> pvJoint.v
            switchGroup.FKIK_switch >> animJoint.v
            
            
            #connections to meta
            connectToMeta(ik, self.networkNode, 'ikHandle')
            connectToMeta(pvJoint, self.networkNode, 'pvAnim')
            connectToMeta(animJoint, self.networkNode, 'ikAnim')
            connectToMeta(switchGroup, self.networkNode, 'switchGroup')        
            self.networkNode.setAttr('switchAttr', 'FKIK_switch',  f=1)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            connectToMeta(dntGrp, self.networkNode, 'dntGrp')
            connectChainToMeta(FK_joints, self.networkNode, 'FKJoints')
            connectChainToMeta(IK_joints, self.networkNode, 'IKJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
        
    def alignSwitch(self):
        '''
        toggle between FK and IK while keeping current joint placement
        '''
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        switchAttr = self.networkNode.switchAttr.get()
        
        if switchGroup.attr(switchAttr).get() < .5:
            #snap ik to fk
            alignPointOrient(listConnections(self.networkNode.FKJoints[2])[0],listConnections(self.networkNode.ikAnim)[0], 1,1)
            pvLoc = createPVLocator(listConnections(self.networkNode.FKJoints[0])[0], listConnections(self.networkNode.FKJoints[1])[0], listConnections(self.networkNode.FKJoints[2])[0])
            alignPointOrient(pvLoc, listConnections(self.networkNode.pvAnim)[0], 1,0)
            alignPointOrient(listConnections(self.networkNode.IKJoints)[1], listConnections(self.networkNode.pvAnim)[0], 0,1)
            delete(pvLoc)
            switchGroup.attr(switchAttr).set(1)
            setKeyframe(switchGroup.attr(switchAttr), itt='spline' , ott = 'step')
            select(self.networkNode.FKJoints.listConnections())
            
        else:
            #snap fk to ik
            ikjs = self.networkNode.IKJoints.listConnections()
            fkjs = self.networkNode.FKJoints.listConnections()
            for inc in xrange(3):
                alignPointOrient(ikjs[inc],fkjs[inc], 0,1)
            switchGroup.attr(switchAttr).set(0)
            setKeyframe(switchGroup.attr(switchAttr), itt='spline' , ott = 'step')
            select(ikjs)
            
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
            
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            ik_joints = self.networkNode.IKJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
                if location == fk_joints[inc]:
                    return control_joints[inc]
                if location == ik_joints[inc]:
                    return control_joints[inc]
        raise Exception("FKIKChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind ,fk, ik, or control joint ")

    def isIK(self):
        return True
    
    def getIK(self):
        return self.networkNode.ikHandle.listConnections()[0]
        
    def isFK(self):
        return True

    def getIKAnim(self):
        '''
        returns the ik anim at the end of the IK chain
        '''
        return self.networkNode.ikAnim.listConnections()[0]
        
    def getPVAnim(self):
        '''
        returns the pole vector anim
        '''    
        return self.networkNode.pvAnim.listConnections()[0]
        
    def getFKAnims(self):
        '''
        returns all the FK anims
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        allAnims = []
        allAnims.append(self.getPVAnim())
        allAnims.append(self.getIKAnim())
        map(lambda x: allAnims.append(x), self.getFKAnims())
        return allAnims
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''
        anims = self.getAllAnims()
        for anim in anims:            
            resetAttrs(anim)    
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        switchGroup = self.networkNode.switchGroup.listConnections()[0]
        switchAttr = self.networkNode.switchAttr.get()
        fkikMode = switchGroup.attr(switchAttr).get() < .5#true if fk
        
        pvAnim = self.getPVAnim()
        pvTrans = pvAnim.translate.get()
        ikAnim = self.getIKAnim()
        ikTrans = ikAnim.translate.get()
        ikRot = ikAnim.rotate.get()
        fkAnims = self.getFKAnims()
        fkRots = map(lambda x: x.rotate.get(), fkAnims)
        if other == self:
            if fkikMode:
                map(lambda x: x.rotate.set(-x.rotate.get()[0],-x.rotate.get()[1],x.rotate.get()[2] ), fkAnims)
            else:    
                pvAnim.translate.set(pvTrans[0], pvTrans[1], -pvTrans[2])
                ikAnim.rotate.set(ikRot[0], ikRot[1], -ikRot[2])
                ikAnim.translate.set(ikTrans[0], ikTrans[1], -ikTrans[2])
                return [self]
        else:
            otherPvAnim = other.getPVAnim()
            otherPvTrans = otherPvAnim.translate.get()
            otherIkAnim = other.getIKAnim()
            otherIkTrans = otherIkAnim.translate.get()
            otherIkRot = otherIkAnim.rotate.get()
            otherFkAnims = other.getFKAnims()
            otherFkRots = map(lambda x: x.rotate.get(), otherFkAnims)
            otherSwitchGroup = other.networkNode.switchGroup.listConnections()[0]
            otherSwitchAttr = other.networkNode.switchAttr.get()
            other_fkikMode = otherSwitchGroup.attr(otherSwitchAttr).get() < .5#true if fk        
            if bothSides:
                #mirror self
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                if other_fkikMode:
                    for num in xrange(len(otherFkAnims)):
                        thisAnim = fkAnims[num]
                        thisAnim.rotate.set(otherFkRots[num])
                else:
                    try:
                        pvAnim.translate.set(-otherPvTrans)
                    except: pass
                    try:
                        ikAnim.translate.set(-otherIkTrans)
                    except: pass
                    try:
                        ikAnim.rotate.set(otherIkRot)
                    except: pass
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                #mirror other
                if not fkikMode == other_fkikMode:
                    other.alignSwitch()
                if fkikMode:
                    for num in xrange(len(fkAnims)):
                        otherAnim = otherFkAnims[num]
                        otherAnim.rotate.set(fkRots[num])
                else:
                    try:
                        otherPvAnim.translate.set(-pvTrans)
                    except: pass
                    try:
                        otherIkAnim.translate.set(-ikTrans)
                    except: pass
                    try:
                        otherIkAnim.rotate.set(ikRot)
                    except: pass
                if not fkikMode == other_fkikMode:
                    other.alignSwitch()
                return [self, other]
            else:
                #mirror self
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                if other_fkikMode:
                    for num in xrange(len(otherFkAnims)):
                        thisAnim = fkAnims[num]
                        thisAnim.rotate.set(otherFkRots[num])
                else:
                    try:
                        pvAnim.translate.set(-otherPvTrans)
                    except: pass
                    try:
                        ikAnim.translate.set(-otherIkTrans)
                    except: pass
                    try:
                        ikAnim.rotate.set(otherIkRot)
                    except: pass
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
            return [self]

class FKIKArm(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint,stretchy = 0, node=''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKArm'):
                    self.networkNode = node
                else:
                    printError("FKIKArm: node %s is not a FKIKArm metaNode"%(node))
            else:
                printError("FKIKArm: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKIKArm', 1.0, 'arm chain that can switch between Fk and IK', side, bodyPart, startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            for item in chain:
                item  = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
                    
            #error checking
            #num in joint chain need 4
                    
            #create ik, fk, control joints
            FK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "FK")
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
            IK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "IK")
                #Rename
            for x in xrange(len(FK_joints)):
                FK_joints[x].rename("%s_%i_fk_joint"%(compName, x+1))
                IK_joints[x].rename("%s_%i_ik_joint"%(compName, x+1))
                control_joints[x].rename("%s_%i_control_joint"%(compName, x+1))
            
            #connect FK joints
            for obj in FK_joints[:-1]:
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, [ 'tx','ty', 'tz', 'sx', 'sy', 'sz', 'radius'])
                obj.tx.set(keyable = 0)
                obj.v.set(keyable = 0)
                addAnimAttr(obj)
                obj.rename(obj.name().replace('joint', 'anim'))
            lockAndHideAttrs(FK_joints[1], ["ry", "rx"])
            
            #IKHandle
            buf = ikHandle(startJoint = IK_joints[0], endEffector = IK_joints[-2], sol = 'ikRPsolver', w=1)
            ik = buf[0]
            ik.rename('%s_ik'%compName)
            eff = buf[1]
            eff.rename('%s_eff'%compName)
            
            #Ik anim
            select(cl=1)
            animJoint = joint()
            labels = getJointLabels(IK_joints[2])
            animJoint.rename("%s_%s_ik_anim"%(labels[0], labels[1]))
            addAnimAttr(animJoint)
            
            cube = polyCube()[0]
            appendShape(cube, animJoint)
            delete(cube)
            
            alignPointOrient(IK_joints[2], animJoint, 1,1)
            ikGrp = group(ik, n = "ik_anim_control_grp")
            pointConstraint(animJoint, ikGrp, w=1, mo=1)
            animJointGrp = createZeroedOutGrp(animJoint)
            animJoint.v.set(keyable = 0)
            orientConstraint(animJoint, IK_joints[2], mo=1, w=1)
            
            
            #PV
            pvLoc = createPVLocator(FK_joints[0], FK_joints[1], FK_joints[2])
            labels = getJointLabels(IK_joints[1])
            select(cl=1)
            pvJoint = joint()
            pvJoint.rename("%s_%s_pv_anim"%(labels[0], labels[1]))
            sphere = polySphere()[0]
            appendShape(sphere, pvJoint)
            alignPointOrient(pvLoc, pvJoint, 1,0)
            alignPointOrient(animJoint, pvJoint, 0,1)
            addAnimAttr(pvJoint)
            delete(pvLoc)
            delete(sphere)
            poleVectorConstraint(pvJoint, ik, w=1)
            pvJointGrp = createZeroedOutGrp(pvJoint)
            pvJoint.v.set(keyable = 0)
            
            #ik stretchyness
            startPoint = None
            globalMultiplier = createNode('multiplyDivide')
            distDim = None
            if stretchy:
                #get total distance
                totalLength = 0
                totalLength += IK_joints[1].translateX.get() #upper arm length
                totalLength += IK_joints[2].translateX.get() #lower arm length
                totalLength = abs(totalLength)
                #create way of keeping currnet distance
                startPoint = spaceLocator()
                startPoint.translate.set(3.3615,2.2215554,7.659)#random point
                endPoint = spaceLocator()
                endPoint.translate.set(2.84596,23.2155,0.3325)#random point
                distDim = distanceDimension(sp=startPoint.translate.get(),ep= endPoint.translate.get())
                distDim = PyNode(distDim)
                alignPointOrient(IK_joints[0], startPoint, 1,0)
                alignPointOrient(IK_joints[2], endPoint, 1,0)
                parent(endPoint, animJoint)
                
                #create basic setup with calc nodes
                    #multipler
                
                
                globalMultiplier.input1X.set(totalLength)
                globalMultiplier.input2X.set(1)
                #still have to put topCon globalscale input globalMultiplier.input2X
                
                ratio = createNode('multiplyDivide') #outputX = currentLength\(orig*globalScale)
                ratio.operation.set(2)#divide
                globalMultiplier.outputX >> ratio.input2X
                distDim.distance >> ratio.input1X
                    #conditional
                condition = createNode('condition')
                ratio.outputX >> condition.firstTerm
                condition.secondTerm.set(1)
                condition.operation.set(2)#greater than, if current ratio > 1
                condition.colorIfFalseR.set(1)
                ratio.outputX >> condition.colorIfTrueR
                
                #add stretchy to the FK and IK joints
                for j in xrange(2):
                    ikJoint = IK_joints[j+1] # want to use FK/IK_joints[1,2] 
                    jointMult = createNode('multiplyDivide')
                    orig = ikJoint.translateX.get()
                    jointMult.input1X.set(orig)
                    condition.outColorR >> jointMult.input2X
                    jointMult.outputX >> ikJoint.translateX
            
            
            #connect IK and FK to the control
            select(cl=1)
            switchGroup = group(n = '%s_FKIK_switch'%compName)
            switchGroup.addAttr('FKIK_switch', keyable = 1)
            switchGroup.FKIK_switch.setMax(1)
            switchGroup.FKIK_switch.setMin(0)
            switchGroup.FKIK_switch.setKeyable(1)
            rev = createNode('reverse')
            switchGroup.FKIK_switch >> rev.inputX
            for inc in xrange(len(FK_joints)):
                const = parentConstraint(FK_joints[inc], IK_joints[inc], control_joints[inc])    
                rev.outputX >> const.w0
                switchGroup.FKIK_switch >> const.w1
            lockAndHideAttrs(switchGroup, ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy','sz','v'))
                
            #connect control joints to bind joints
            for inc in xrange(len(FK_joints)):#-1
                parentConstraint(control_joints[inc], bind_joints[inc])
            
            lockAndHideAttrs(animJoint, ['s','radius'])
            lockAndHideAttrs(pvJoint, ['r','s','radius'])
                
            #grouping
            select(cl=1)
            jointGrp = group([FK_joints[0], IK_joints[0], control_joints[0]],n='%s_joint_grp'%compName)
            animGrp = group([animJointGrp, pvJointGrp, switchGroup], n = "%s_anim_grp"%compName)
            
            dntGrp = group([distDim, ikGrp], n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            #hiding
            if stretchy:
                parent(startPoint, dntGrp)
            control_joints[0].hide()
            dntGrp.hide()
            switchGroup.FKIK_switch >> IK_joints[0].visibility
            rev.outputX >> FK_joints[0].visibility
            switchGroup.FKIK_switch >> pvJoint.v
            switchGroup.FKIK_switch >> animJoint.v
            animJointGrp.inheritsTransform.set(0)#allows the feet not to move when hip moves, if hip.
            
            #connections to meta
            connectToMeta(ik, self.networkNode, 'ikHandle')
            connectToMeta(pvJoint, self.networkNode, 'pvAnim')
            connectToMeta(animJoint, self.networkNode, 'ikAnim')
            connectToMeta(switchGroup, self.networkNode, 'switchGroup')        
            self.networkNode.setAttr('switchAttr', 'FKIK_switch',  f=1)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            connectToMeta(dntGrp, self.networkNode, 'dntGrp')
            self.networkNode.setAttr('stretchy', stretchy,  f=1)
            connectChainToMeta(FK_joints, self.networkNode, 'FKJoints')
            connectChainToMeta(IK_joints, self.networkNode, 'IKJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectToMeta(globalMultiplier, self.networkNode, 'globalMultiplier')
    
    def getSwitchAttr(self):
        switchNode = self.networkNode.switchGroup.listConnections()[0]
        switchAttrName = self.networkNode.switchAttr.get()
        return switchNode.attr(switchAttrName)
        
    def alignSwitch(self):
        '''
        toggle between FK and IK while keeping current joint placement
        '''
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        switchAttr = self.networkNode.switchAttr.get()
        
        if switchGroup.attr(switchAttr).get() < .5:
            #snap ik to fk
            alignPointOrient(listConnections(self.networkNode.FKJoints[2])[0],listConnections(self.networkNode.ikAnim)[0], 1,1)
            pvLoc = createPVLocator(listConnections(self.networkNode.FKJoints[0])[0], listConnections(self.networkNode.FKJoints[1])[0], listConnections(self.networkNode.FKJoints[2])[0])
            alignPointOrient(pvLoc, listConnections(self.networkNode.pvAnim)[0], 1,0)
            alignPointOrient(listConnections(self.networkNode.IKJoints)[1], listConnections(self.networkNode.pvAnim)[0], 0,1)
            delete(pvLoc)
            wrist_fk_joint = self.networkNode.FKJoints.listConnections()[-2]
            ik_anim = self.networkNode.ikAnim.listConnections()[0]
            alignPointOrient(wrist_fk_joint, ik_anim , 0,1)
            switchGroup.attr(switchAttr).set(1)
            setKeyframe(switchGroup.attr(switchAttr), itt='spline' , ott = 'step')
            select(self.networkNode.FKJoints.listConnections())
        else:
            #snap fk to ik
            ikjs = self.networkNode.IKJoints.listConnections()
            fkjs = self.networkNode.FKJoints.listConnections()
            for inc in xrange(4):
                if inc == 1 or inc == 2:
                    fkjs[inc].translateX.unlock()
                    fkjs[inc].translateX.set(ikjs[inc].translateX.get())
                    fkjs[inc].translateX.lock()
                alignPointOrient(ikjs[inc],fkjs[inc], 0,1)
            switchGroup.attr(switchAttr).set(0)
            setKeyframe(switchGroup.attr(switchAttr), itt='spline' , ott = 'step') 
            select(self.networkNode.IKJoints.listConnections())            
            
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
            
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            ik_joints = self.networkNode.IKJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
                if location == fk_joints[inc]:
                    return control_joints[inc]
                if location == ik_joints[inc]:
                    return control_joints[inc]
        raise Exception("FKIKArm.getConnectObj: location wasn't found, try 'start', 'end', or name of bind, fk, ik, or control joint.")

    def isIK(self):
        return True
    
    def getIK(self):
        return self.networkNode.ikHandle.listConnections()[0]
        
    def isFK(self):
        return True

    def getIKAnim(self):
        '''
        returns the ik anim at the end of the IK chain
        '''
        return self.networkNode.ikAnim.listConnections()[0]
        
    def getPVAnim(self):
        '''
        returns the pole vector anim
        '''    
        return self.networkNode.pvAnim.listConnections()[0]
        
    def getFKAnims(self):
        '''
        returns all the FK anims
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        allAnims = []
        allAnims.append(self.getPVAnim())
        allAnims.append(self.getIKAnim())
        map(lambda x: allAnims.append(x), self.getFKAnims())
        allAnims.append(self.networkNode.switchGroup.listConnections()[0])
        return allAnims
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''
        allAnims = []
        allAnims.append(self.getPVAnim())
        allAnims.append(self.getIKAnim())
        map(lambda x: allAnims.append(x), self.getFKAnims())
        for anim in allAnims:            
            resetAttrs(anim)    
        
    def parentUnder(self, obj):
        '''
        parent this rigComponent under the obj
        obj:
            object to parent under
        '''
        if not objExists(obj):
            raise Exception("RigComponent: can't parent under $s, obj doesn't exist"%obj)
        try:
            parent(self.networkNode.componentGrp.listConnections()[0], obj)
            root = getMetaRoot(obj, 'CharacterRig')
            if root:
                try:
                    topCon = root.getTopCon()
                    topCon.globalScale >> self.networkNode.globalMultiplier.listConnections()[0].input2X
                    ikAnim = self.networkNode.ikAnim.listConnections()[0]
                    zeroGrp = ikAnim.getParent()
                    parentConstraint(topCon, zeroGrp, w=1, mo=1)
                    scaleConstraint(topCon, zeroGrp, w=1, mo =1)
                except:
                    pass
        except:
            raise Exception("%s.parentUnder: not implemeneted"%self.networkNode.metaType.get())
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        switchGroup = self.networkNode.switchGroup.listConnections()[0]
        switchAttr = self.networkNode.switchAttr.get()
        fkikMode = switchGroup.attr(switchAttr).get() < .5#true if fk
        
        pvAnim = self.getPVAnim()
        pvTrans = pvAnim.translate.get()
        ikAnim = self.getIKAnim()
        ikTrans = ikAnim.translate.get()
        ikRot = ikAnim.rotate.get()
        fkAnims = self.getFKAnims()
        fkRots = map(lambda x: x.rotate.get(), fkAnims)
        if other == self:
            if fkikMode:
                map(lambda x: x.rotate.set(-x.rotate.get()[0],-x.rotate.get()[1],x.rotate.get()[2] ), fkAnims)
            else:    
                pvAnim.translate.set(pvTrans[0], pvTrans[1], -pvTrans[2])
                ikAnim.rotate.set(ikRot[0], ikRot[1], -ikRot[2])
                ikAnim.translate.set(ikTrans[0], ikTrans[1], -ikTrans[2])
                return [self]
        else:
            otherPvAnim = other.getPVAnim()
            otherPvTrans = otherPvAnim.translate.get()
            otherIkAnim = other.getIKAnim()
            otherIkTrans = otherIkAnim.translate.get()
            otherIkRot = otherIkAnim.rotate.get()
            otherFkAnims = other.getFKAnims()
            otherFkRots = map(lambda x: x.rotate.get(), otherFkAnims)
            otherSwitchGroup = other.networkNode.switchGroup.listConnections()[0]
            otherSwitchAttr = other.networkNode.switchAttr.get()
            other_fkikMode = otherSwitchGroup.attr(otherSwitchAttr).get() < .5#true if fk        
            if bothSides:
                #mirror self
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                if other_fkikMode:
                    for num in xrange(len(otherFkAnims)):
                        thisAnim = fkAnims[num]
                        if not thisAnim.rotateX.isLocked():
                            thisAnim.rotateX.set(otherFkRots[num][0])
                        if not thisAnim.rotateY.isLocked():
                            thisAnim.rotateY.set(otherFkRots[num][1])
                        if not thisAnim.rotateZ.isLocked():
                            thisAnim.rotateZ.set(otherFkRots[num][2])
                else:
                    try:
                        pvAnim.translate.set(-otherPvTrans)
                    except: pass
                    try:
                        ikAnim.translate.set(-otherIkTrans)
                    except: pass
                    try:
                        ikAnim.rotate.set(otherIkRot)
                    except: pass
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                #mirror other
                if not fkikMode == other_fkikMode:
                    other.alignSwitch()
                if fkikMode:
                    for num in xrange(len(fkAnims)):
                        otherAnim = otherFkAnims[num]
                        if not otherAnim.rotateX.isLocked():
                            otherAnim.rotateX.set(fkRots[num][0])
                        if not otherAnim.rotateY.isLocked():
                            otherAnim.rotateY.set(fkRots[num][1])
                        if not otherAnim.rotateZ.isLocked():
                            otherAnim.rotateZ.set(fkRots[num][2])
                else:
                    try:
                        otherPvAnim.translate.set(-pvTrans)
                    except: pass
                    try:
                        otherIkAnim.translate.set(-ikTrans)
                    except: pass
                    try:
                        otherIkAnim.rotate.set(ikRot)
                    except: pass
                if not fkikMode == other_fkikMode:
                    other.alignSwitch()
                return [self, other]
            else:
                #mirror self
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                if other_fkikMode:
                    for num in xrange(len(otherFkAnims)):
                        thisAnim = fkAnims[num]
                        if not thisAnim.rotateX.isLocked():
                            thisAnim.rotateX.set(otherFkRots[num][0])
                        if not thisAnim.rotateY.isLocked():
                            thisAnim.rotateY.set(otherFkRots[num][1])
                        if not thisAnim.rotateZ.isLocked():
                            thisAnim.rotateZ.set(otherFkRots[num][2])
                else:
                    try:
                        pvAnim.translate.set(-otherPvTrans)
                    except: pass
                    try:
                        ikAnim.translate.set(-otherIkTrans)
                    except: pass
                    try:
                        ikAnim.rotate.set(otherIkRot)
                    except: pass
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
            return [self]

class FKIKArm2(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint,stretchy = 0, node='', fkStretchy = False):
        '''
         side:
             the side is this component on, ex. center, left, right
         bodyPart:
             the body part the component is for, ex. arm, leg, clavicle, foot
         startJoint:
             the place where the component starts
         endJoint:
             the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKArm2'):
                    self.networkNode = node
                else:
                    printError("FKIKArm2: node %s is not a FKIKArm metaNode"%(node))
            else:
                printError("FKIKArm2: node %s doesn't exist"%(node))
        else:
                RigComponent.__init__(self, 'FKIKArm2', 1.0, 'arm chain that can switch between Fk and IK', side, bodyPart, startJoint, endJoint)
                compName = '%s_%s'%(side, bodyPart)
                chain = chainBetween(startJoint, endJoint)
                bind_joints = []
                for item in chain:
                    item  = PyNode(item)
                    if item.type() == 'joint':
                        bind_joints.append(item)

                #error checking
                #num in joint chain need 4

                #create ik, fk, control joints
                FK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "FK")
                control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
                IK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "IK")
                 #Rename
                for x in xrange(len(FK_joints)):
                    FK_joints[x].rename("%s_%i_fk_joint"%(compName, x+1))
                    IK_joints[x].rename("%s_%i_ik_joint"%(compName, x+1))
                    control_joints[x].rename("%s_%i_control_joint"%(compName, x+1))

                #connect FK joints
                for obj in FK_joints[:-1]:
                    addBoxToJoint(obj)
                    lockAndHideAttrs(obj, [ 'tx','ty', 'tz', 'sx', 'sy', 'sz', 'radius'])
                    obj.tx.set(keyable = 0)
                    obj.v.set(keyable = 0)
                    addAnimAttr(obj)
                    obj.rename(obj.name().replace('joint', 'anim'))
                lockAndHideAttrs(FK_joints[1], ["ry", "rx"])

                #IKHandle
                buf = ikHandle(startJoint = IK_joints[0], endEffector = IK_joints[-2], sol = 'ikRPsolver', w=1)
                ik = buf[0]
                ik.rename('%s_ik'%compName)
                eff = buf[1]
                eff.rename('%s_eff'%compName)

                #Ik anim
                select(cl=1)
                animJoint = joint()
                labels = getJointLabels(IK_joints[2])
                animJoint.rename("%s_%s_ik_anim"%(labels[0], labels[1]))
                addAnimAttr(animJoint)

                cube = polyCube()[0]
                appendShape(cube, animJoint)
                delete(cube)

                alignPointOrient(IK_joints[2], animJoint, 1,1)
                ikGrp = group(ik, n = "ik_anim_control_grp")
                pointConstraint(animJoint, ikGrp, w=1, mo=1)
                animJointGrp = createZeroedOutGrp(animJoint)
                animJoint.v.set(keyable = 0)
                orientConstraint(animJoint, IK_joints[2], mo=1, w=1)


                #PV
                pvLoc = createPVLocator(FK_joints[0], FK_joints[1], FK_joints[2])
                labels = getJointLabels(IK_joints[1])
                select(cl=1)
                pvJoint = joint()
                pvJoint.rename("%s_%s_pv_anim"%(labels[0], labels[1]))
                sphere = polySphere()[0]
                appendShape(sphere, pvJoint)
                alignPointOrient(pvLoc, pvJoint, 1,0)
                alignPointOrient(animJoint, pvJoint, 0,1)
                addAnimAttr(pvJoint)
                delete(pvLoc)
                delete(sphere)
                poleVectorConstraint(pvJoint, ik, w=1)
                pvJointGrp = createZeroedOutGrp(pvJoint)
                pvJoint.v.set(keyable = 0)

                select(cl=1)
                switchGroup = group(n = '%s_FKIK_switch'%compName)
                switchGroup.addAttr('FKIK_switch', keyable = 1)
                switchGroup.FKIK_switch.setMax(1)
                switchGroup.FKIK_switch.setMin(0)
                switchGroup.FKIK_switch.setKeyable(1)

                #ik stretchyness
                if stretchy:
                    startPoint = None
                    globalMultiplier = createNode('multiplyDivide', n='%s_%s_gs_mult'%(side, bodyPart))
                    fkMultiplier = createNode('multiplyDivide', n='%s_%s_fk_mult'%(side, bodyPart))
                    
                    distDim = None
                    #get total distance
                    totalLength = 0
                    totalLength += IK_joints[1].translateX.get() #upper arm length
                    totalLength += IK_joints[2].translateX.get() #lower arm length
                    totalLength = abs(totalLength)
                    #create way of keeping currnet distance
                    startPoint = spaceLocator(n='%s_%s_sloc'%(side,bodyPart))
                    startPoint.translate.set(3.3615,2.2215554,7.659)#random point
                    endPoint = spaceLocator(n='%s_%s_eloc'%(side,bodyPart))
                    endPoint.translate.set(2.84596,23.2155,0.3325)#random point
                    distDim = distanceDimension(sp=startPoint.translate.get(),ep= endPoint.translate.get())
                    distDim = PyNode(distDim)
                    alignPointOrient(IK_joints[0], startPoint, 1,0)
                    alignPointOrient(IK_joints[2], endPoint, 1,0)
                    parent(endPoint, animJoint)
                    #create basic setup with calc nodes
                    #multipler
                    globalMultiplier.input1X.set(totalLength)
                    globalMultiplier.input2X.set(1)


                    #still have to put topCon globalsclae input globalMultiplier.input2X

                    ratio = createNode('multiplyDivide', n='%s_%s_stretch_ratio'%(side, bodyPart)) #outputX = currentLength\(orig*globalScale)
                    ratio.operation.set(2)#divide

                    if fkStretchy:
                        switchGroup.addAttr('stretch', keyable = 1)
                        switchGroup.stretch.set(1)
                        switchGroup.stretch.setMin(1)
                        switchGroup.stretch.setKeyable(1)

                        switchGroup.stretch >> fkMultiplier.input2X
                        globalMultiplier.outputX >> fkMultiplier.input1X
                        fkMultiplier.outputX >> ratio.input2X
                    else:
                        globalMultiplier.outputX >> ratio.input2X
                     
                    distDim.distance >> ratio.input1X
                    #conditional
                    condition = createNode('condition')
                    ratio.outputX >> condition.firstTerm
                    condition.secondTerm.set(1)
                    condition.operation.set(2)#greater than, if current ratio > 1
                    condition.colorIfFalseR.set(1)
                    ratio.outputX >> condition.colorIfTrueR
                 
                #add stretchy to the FK and IK joints
                for j in xrange(2):
                    ikJoint = IK_joints[j+1] # want to use FK/IK_joints[1,2]
                    jointMult = createNode('multiplyDivide', n='%s_%s_%d_j_mult'%(side, bodyPart,j))
                    orig = ikJoint.translateX.get()
                    if fkStretchy:
                        fkJoint = FK_joints[j+1]
                        jointSMult = createNode('multiplyDivide', n='%s_%s_fk_%d_j_mult'%(side, bodyPart,j))
                        jointSMult.input1X.set(orig)
                        switchGroup.stretch >> jointSMult.input2X
                        jointSMult.outputX >> jointMult.input1X
                        fkJoint.translateX.unlock()
                        fkJoint.translateX.showInChannelBox(False)
                        jointSMult.outputX >> fkJoint.translateX
                    else:
                        jointMult.input1X.set(orig)
                         
                    condition.outColorR >> jointMult.input2X
                    jointMult.outputX >> ikJoint.translateX

                #connect IK and FK to the control

                rev = createNode('reverse')
                switchGroup.FKIK_switch >> rev.inputX
                for inc in xrange(len(FK_joints)):
                    const = parentConstraint(FK_joints[inc], IK_joints[inc], control_joints[inc])
                    rev.outputX >> const.w0
                    switchGroup.FKIK_switch >> const.w1
                lockAndHideAttrs(switchGroup, ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy','sz','v'))

                #connect control joints to bind joints
                for inc in xrange(len(FK_joints)):#-1
                    parentConstraint(control_joints[inc], bind_joints[inc])

                lockAndHideAttrs(animJoint, ['sx','sy','sz','radius'])
                lockAndHideAttrs(pvJoint, ['rx', 'ry', 'rz','sx','sy','sz','radius'])

                #grouping
                select(cl=1)
                jointGrp = group([FK_joints[0], IK_joints[0], control_joints[0]],n='%s_joint_grp'%compName)
                animGrp = group([animJointGrp, pvJointGrp, switchGroup], n = "%s_anim_grp"%compName)

                dntGrp = group([distDim, ikGrp], n = "%s_DO_NOT_TOUCH_grp"%compName)
                mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
                xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)

                #hiding
                if stretchy:
                 parent(startPoint, dntGrp)
                control_joints[0].hide()
                dntGrp.hide()
                switchGroup.FKIK_switch >> IK_joints[0].visibility
                rev.outputX >> FK_joints[0].visibility
                switchGroup.FKIK_switch >> pvJoint.v
                switchGroup.FKIK_switch >> animJoint.v
                animJointGrp.inheritsTransform.set(0)#allows the feet not to move when hip moves, if hip.

                #connections to meta
                connectToMeta(ik, self.networkNode, 'ikHandle')
                connectToMeta(pvJoint, self.networkNode, 'pvAnim')
                connectToMeta(animJoint, self.networkNode, 'ikAnim')
                connectToMeta(switchGroup, self.networkNode, 'switchGroup')
                connectToMeta(ratio, self.networkNode, 'autoStretchRatio')
                self.networkNode.setAttr('switchAttr', 'FKIK_switch',  f=1)
                connectToMeta(mainGrp, self.networkNode, 'componentGrp')
                connectToMeta(dntGrp, self.networkNode, 'dntGrp')
                self.networkNode.setAttr('stretchy', stretchy,  f=1)
                connectChainToMeta(FK_joints, self.networkNode, 'FKJoints')
                connectChainToMeta(IK_joints, self.networkNode, 'IKJoints')
                connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
                connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
                connectToMeta(globalMultiplier, self.networkNode, 'globalMultiplier')
    
    def getSwitchAttr(self):
        switchNode = self.networkNode.switchGroup.listConnections()[0]
        switchAttrName = self.networkNode.switchAttr.get()
        return switchNode.attr(switchAttrName)
        
    def alignSwitch(self, setKey = True):
        '''
        toggle between FK and IK while keeping current joint placement
        '''
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        switchAttr = self.networkNode.switchAttr.get()
        hasStretch = switchGroup.hasAttr('stretch')
        if switchGroup.attr(switchAttr).get() < .5:
            #snap ik to fk
            alignPointOrient(listConnections(self.networkNode.FKJoints[2])[0],listConnections(self.networkNode.ikAnim)[0], 1,1)
            pvLoc = createPVLocator(listConnections(self.networkNode.FKJoints[0])[0], listConnections(self.networkNode.FKJoints[1])[0], listConnections(self.networkNode.FKJoints[2])[0])
            alignPointOrient(pvLoc, listConnections(self.networkNode.pvAnim)[0], 1,0)
            alignPointOrient(listConnections(self.networkNode.IKJoints)[1], listConnections(self.networkNode.pvAnim)[0], 0,1)
            delete(pvLoc)
            wrist_fk_joint = self.networkNode.FKJoints.listConnections()[-2]
            ik_anim = self.networkNode.ikAnim.listConnections()[0]
            alignPointOrient(wrist_fk_joint, ik_anim , 0,1)
            switchGroup.attr(switchAttr).set(1)
            
        else:
            #snap fk to ik
            ikjs = self.networkNode.IKJoints.listConnections()
            fkjs = self.networkNode.FKJoints.listConnections()
            if hasStretch:
                ratio = self.networkNode.autoStretchRatio.listConnections()[0]
                currentRatio = ratio.outputX.get()
                print switchGroup.stretch.get()
                print currentRatio
                switchGroup.stretch.set(max(switchGroup.stretch.get()*max(currentRatio,1),1))
            for inc in xrange(4):
                if hasStretch:
                    alignPointOrient(ikjs[inc],fkjs[inc], 0,1)
                else:
                    if inc == 1 or inc == 2:
                        fkjs[inc].translateX.unlock()
                        fkjs[inc].translateX.set(ikjs[inc].translateX.get())
                        fkjs[inc].translateX.lock()
                    alignPointOrient(ikjs[inc],fkjs[inc], 0,1)
            switchGroup.attr(switchAttr).set(0)
        
        if setKey:
            setKeyframe(switchGroup.attr(switchAttr), itt='spline' , ott = 'step')    
            
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
            
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            ik_joints = self.networkNode.IKJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
                if location == fk_joints[inc]:
                    return control_joints[inc]
                if location == ik_joints[inc]:
                    return control_joints[inc]
        raise Exception("FKIKChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind ,fk, ik, or control joint ")

    def isIK(self):
        return True
    
    def getIK(self):
        return self.networkNode.ikHandle.listConnections()[0]
        
    def isFK(self):
        return True

    def getIKAnim(self):
        '''
        returns the ik anim at the end of the IK chain
        '''
        return self.networkNode.ikAnim.listConnections()[0]
        
    def getPVAnim(self):
        '''
        returns the pole vector anim
        '''    
        return self.networkNode.pvAnim.listConnections()[0]
        
    def getFKAnims(self):
        '''
        returns all the FK anims
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        allAnims = []
        allAnims.append(self.getPVAnim())
        allAnims.append(self.getIKAnim())
        map(lambda x: allAnims.append(x), self.getFKAnims())
        allAnims.append(self.networkNode.switchGroup.listConnections()[0])
        return allAnims
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''
        allAnims = []
        allAnims.append(self.getPVAnim())
        allAnims.append(self.getIKAnim())
        map(lambda x: allAnims.append(x), self.getFKAnims())
        for anim in allAnims:            
            resetAttrs(anim)
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        if switchGroup.hasAttr('stretch'):
            switchGroup.stretch.set(1)
        
    def parentUnder(self, obj):
        '''
        parent this rigComponent under the obj
        obj:
            object to parent under
        '''
        if not objExists(obj):
            raise Exception("RigComponent: can't parent under $s, obj doesn't exist"%obj)
        try:
            parent(self.networkNode.componentGrp.listConnections()[0], obj)
            root = getMetaRoot(obj, 'CharacterRig')
            if root:
                try:
                    topCon = root.getTopCon()
                    topCon.globalScale >> self.networkNode.globalMultiplier.listConnections()[0].input2X
                    ikAnim = self.networkNode.ikAnim.listConnections()[0]
                    zeroGrp = ikAnim.getParent()
                    parentConstraint(topCon, zeroGrp, w=1, mo=1)
                    scaleConstraint(topCon, zeroGrp, w=1, mo =1)
                except:
                    pass
        except:
            raise Exception("%s.parentUnder: not implemeneted"%self.networkNode.metaType.get())
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        switchGroup = self.networkNode.switchGroup.listConnections()[0]
        switchAttr = self.networkNode.switchAttr.get()
        fkikMode = switchGroup.attr(switchAttr).get() < .5#true if fk
        stretch = switchGroup.attr('stretch').get()
        pvAnim = self.getPVAnim()
        pvTrans = pvAnim.translate.get()
        ikAnim = self.getIKAnim()
        ikTrans = ikAnim.translate.get()
        ikRot = ikAnim.rotate.get()
        fkAnims = self.getFKAnims()
        fkRots = map(lambda x: x.rotate.get(), fkAnims)
        if other == self:
            if fkikMode:
                map(lambda x: x.rotate.set(-x.rotate.get()[0],-x.rotate.get()[1],x.rotate.get()[2] ), fkAnims)
            else:    
                pvAnim.translate.set(pvTrans[0], pvTrans[1], -pvTrans[2])
                ikAnim.rotate.set(ikRot[0], ikRot[1], -ikRot[2])
                ikAnim.translate.set(ikTrans[0], ikTrans[1], -ikTrans[2])
                return [self]
        else:
            otherPvAnim = other.getPVAnim()
            otherPvTrans = otherPvAnim.translate.get()
            otherIkAnim = other.getIKAnim()
            otherIkTrans = otherIkAnim.translate.get()
            otherIkRot = otherIkAnim.rotate.get()
            otherFkAnims = other.getFKAnims()
            otherFkRots = map(lambda x: x.rotate.get(), otherFkAnims)
            otherSwitchGroup = other.networkNode.switchGroup.listConnections()[0]
            otherSwitchAttr = other.networkNode.switchAttr.get()
            other_fkikMode = otherSwitchGroup.attr(otherSwitchAttr).get() < .5#true if fk        
            other_stretch = otherSwitchGroup.attr('stretch').get()
            #mirror self
            if not fkikMode == other_fkikMode:
                self.alignSwitch()
            switchGroup.attr('stretch').set(other_stretch)
            if other_fkikMode:
                for num in xrange(len(otherFkAnims)):
                    thisAnim = fkAnims[num]
                    if not thisAnim.rotateX.isLocked():
                        thisAnim.rotateX.set(otherFkRots[num][0])
                    if not thisAnim.rotateY.isLocked():
                        thisAnim.rotateY.set(otherFkRots[num][1])
                    if not thisAnim.rotateZ.isLocked():
                        thisAnim.rotateZ.set(otherFkRots[num][2])
            else:
                try:
                    pvAnim.translate.set(-otherPvTrans)
                except: pass
                try:
                    ikAnim.translate.set(-otherIkTrans)
                except: pass
                try:
                    ikAnim.rotate.set(otherIkRot)
                except: pass
            if not fkikMode == other_fkikMode:
                self.alignSwitch()
            if bothSides:
                #mirror other
                if not fkikMode == other_fkikMode:
                    other.alignSwitch()
                otherSwitchGroup.attr('stretch').set(stretch)
                if fkikMode:
                    for num in xrange(len(fkAnims)):
                        otherAnim = otherFkAnims[num]
                        if not otherAnim.rotateX.isLocked():
                            otherAnim.rotateX.set(fkRots[num][0])
                        if not otherAnim.rotateY.isLocked():
                            otherAnim.rotateY.set(fkRots[num][1])
                        if not otherAnim.rotateZ.isLocked():
                            otherAnim.rotateZ.set(fkRots[num][2])
                else:
                    try:
                        otherPvAnim.translate.set(-pvTrans)
                    except: pass
                    try:
                        otherIkAnim.translate.set(-ikTrans)
                    except: pass
                    try:
                        otherIkAnim.rotate.set(ikRot)
                    except: pass
                if not fkikMode == other_fkikMode:
                    other.alignSwitch()
                return [self, other]
            else:
                return [self]

class FKIKLeg(RigComponent):
    def __init__(self, heelJoint, toeJoint, insideJoint, outsideJoint,  side, bodyPart, startJoint, endJoint,stretchy = 0, node=''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKLeg'):
                    self.networkNode = node
                else:
                    printError("FKIKLeg: node %s is not a FKIKLeg metaNode"%(node))
            else:
                printError("FKIKLeg: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FKIKLeg', 1.0, 'leg chain that can switch between Fk and IK', side, bodyPart, startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            for item in chain:
                item  = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
                    
            #error checking
            heelJoint = PyNode(heelJoint)
            insideJoint = PyNode(insideJoint)
            outsideJoint = PyNode(outsideJoint)
            toeJoint = PyNode(toeJoint)
            
            #num in joint chain need 5
                    
            #create ik, fk, control joints
            FK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "FK")
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
            IK_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', "IK")
            
            #create pivot joints, use the foot joint to base rotation
            heel_piv = duplicate(bind_joints[3], po =1, n= '%s_heel_piv_joint'%compName)[0]
            toe_piv = duplicate(bind_joints[3], po =1, n= '%s_toe_piv_joint'%compName)[0]
            toe_lift_piv = duplicate(bind_joints[3], po =1, n= '%s_toe_lift_piv_joint'%compName)[0]
            toe_fk_piv = duplicate(bind_joints[3], po =1, n= '%s_toe_fk_piv_joint'%compName)[0]# will take rotate info from FK when align switching
            inside_piv = duplicate(bind_joints[3], po =1, n= '%s_inside_piv_joint'%compName)[0]
            outside_piv = duplicate(bind_joints[3], po =1, n= '%s_outside_piv_joint'%compName)[0]
            parent([heel_piv, toe_piv, toe_lift_piv, toe_fk_piv, inside_piv, outside_piv], w=1)
            alignPointOrient(heelJoint, heel_piv, 1,0)
            alignPointOrient(insideJoint, inside_piv, 1,0)
            alignPointOrient(outsideJoint, outside_piv, 1,0)
            alignPointOrient(toeJoint, toe_piv, 1,0)
            alignPointOrient(bind_joints[3], toe_lift_piv, 1,0)
            alignPointOrient(bind_joints[3], toe_fk_piv, 1,0)
            delete(heelJoint, toeJoint, insideJoint, outsideJoint)
            
            #Rename
            for x in xrange(len(FK_joints)):
                FK_joints[x].rename("%s_%i_fk_joint"%(compName, x+1))
                IK_joints[x].rename("%s_%i_ik_joint"%(compName, x+1))
                control_joints[x].rename("%s_%i_control_joint"%(compName, x+1))
            
            #connect FK joints
            for obj in FK_joints[:-1]:
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius'])
                obj.tx.set(keyable = 0)
                obj.v.set(keyable = 0)
                addAnimAttr(obj)
                obj.rename(obj.name().replace('joint', 'anim'))
            lockAndHideAttrs(FK_joints[1], ["ry", "rx"]) #knee
            lockAndHideAttrs(FK_joints[3], ["ry", "rx"]) #toe/ball
            
            #IKHandle
            buf = ikHandle(startJoint = IK_joints[0], endEffector = IK_joints[2], sol = 'ikRPsolver', w=1)
            ik = buf[0]
            ik.rename('%s_ik'%compName)
            eff = buf[1]
            eff.rename('%s_eff'%compName)
            
            #create single chain Ik's for foot
            foot_ik = ikHandle( sj= IK_joints[2], ee = IK_joints[3], sol ='ikSCsolver')[0]
            toe_ik = ikHandle( sj= IK_joints[3], ee = IK_joints[4], sol ='ikSCsolver')[0]
            
            #Ik anim
            select(cl=1)
            animJoint = joint()
            labels = getJointLabels(IK_joints[2])
            animJoint.rename("%s_%s_ik_anim"%(labels[0], labels[1]))
            addAnimAttr(animJoint)
            
            cube = polyCube()[0]
            appendShape(cube, animJoint)
            delete(cube)
            
            alignPointOrient(IK_joints[2], animJoint, 1,1)
            animJointGrp = createZeroedOutGrp(animJoint)
            animJoint.v.set(keyable = 0)
            
            # Value flips the animation on certain set driven attributes
            # based on the side of the character this component is on
            if (side == 'right'):
                flipValue = -1
            else:
                flipValue = 1
            
            #add and connect attrs to the IK anim
            animJoint.addAttr('heelSpin', keyable=1,dv =0, min = -180, max = 180)
            animJoint.addAttr('heelLift', keyable =1, dv=0,min = -180, max = 180)
            animJoint.addAttr('toeSpin',  keyable=1, dv = 0, min = -180, max = 180)
            animJoint.addAttr('ballLift',  keyable=1, dv = 0, min = -180, max = 180)
            animJoint.addAttr('toeLift',  keyable=1, dv = 0, min = -180, max = 180)
            animJoint.addAttr('toeWiggle', keyable=1, dv = 0, min = -180, max = 180)
            animJoint.addAttr('sideToSide', keyable=1, dv = 0, min = -90, max = 90)
            animJoint.addAttr('ballSpin',  keyable=1, dv = 0, min = -180, max = 180)
            
            #heelspin
            animJoint.heelSpin.set(-180)
            heel_piv.rotateY.set(flipValue*-180)
            setDrivenKeyframe(heel_piv.rotateY, cd = animJoint.heelSpin, itt='linear', ott = 'linear')
            animJoint.heelSpin.set(180)
            heel_piv.rotateY.set(flipValue*180)
            setDrivenKeyframe(heel_piv.rotateY, cd = animJoint.heelSpin, itt='linear', ott = 'linear')
            
            #heelLift
            animJoint.heelLift.set(-180)
            heel_piv.rotateZ.set(-180)
            setDrivenKeyframe(heel_piv.rotateZ, cd = animJoint.heelLift, itt='linear', ott = 'linear')
            animJoint.heelLift.set(180)
            heel_piv.rotateZ.set(180)
            setDrivenKeyframe(heel_piv.rotateZ, cd = animJoint.heelLift, itt='linear', ott = 'linear')
            
            #toeSpin
            animJoint.toeSpin.set(180)
            toe_piv.rotateY.set(flipValue*-180)
            setDrivenKeyframe(toe_piv.rotateY, cd = animJoint.toeSpin, itt='linear', ott = 'linear')
            animJoint.toeSpin .set(-180)
            toe_piv.rotateY.set(flipValue*180)
            setDrivenKeyframe(toe_piv.rotateY, cd = animJoint.toeSpin, itt='linear', ott = 'linear')
            
            #ballLift
            animJoint.ballLift.set(180)
            toe_lift_piv.rotateZ.set(-180)
            setDrivenKeyframe(toe_lift_piv.rotateZ, cd = animJoint.ballLift, itt='linear', ott = 'linear')
            animJoint.ballLift .set(-180)
            toe_lift_piv.rotateZ.set(180)
            setDrivenKeyframe(toe_lift_piv.rotateZ, cd = animJoint.ballLift, itt='linear', ott = 'linear')
            
            #toeLift
            animJoint.toeLift.set(180)
            toe_piv.rotateZ.set(-180)
            setDrivenKeyframe(toe_piv.rotateZ, cd = animJoint.toeLift, itt='linear', ott = 'linear')
            animJoint.toeLift .set(-180)
            toe_piv.rotateZ.set(180)
            setDrivenKeyframe(toe_piv.rotateZ, cd = animJoint.toeLift, itt='linear', ott = 'linear')
            
            #toeWiggle
            animJoint.toeWiggle.set(180)
            toe_fk_piv.rotateZ.set(180)
            setDrivenKeyframe(toe_fk_piv.rotateZ, cd = animJoint.toeWiggle, itt='linear', ott = 'linear')
            animJoint.toeWiggle .set(-180)
            toe_fk_piv.rotateZ.set(-180)
            setDrivenKeyframe(toe_fk_piv.rotateZ, cd = animJoint.toeWiggle, itt='linear', ott = 'linear')
            
            #sideToSide
            animJoint.sideToSide.set(0)
            inside_piv.rotateX.set(0)
            outside_piv.rotateX.set(0)
            setDrivenKeyframe(inside_piv.rotateX, cd = animJoint.sideToSide, itt='linear', ott = 'linear')
            setDrivenKeyframe(outside_piv.rotateX, cd = animJoint.sideToSide, itt='linear', ott = 'linear')    
            animJoint.sideToSide.set(90)
            outside_piv.rotateX.set(flipValue*-90)
            setDrivenKeyframe(outside_piv.rotateX, cd = animJoint.sideToSide, itt='linear', ott = 'linear')
            animJoint.sideToSide.set(-90)
            inside_piv.rotateX.set(flipValue*90)
            setDrivenKeyframe(inside_piv.rotateX, cd = animJoint.sideToSide, itt='linear', ott = 'linear')
            
            #ballSpin
            animJoint.ballSpin.set(180)
            inside_piv.rotateY.set(flipValue*180)
            setDrivenKeyframe(inside_piv.rotateY, cd = animJoint.ballSpin, itt='linear', ott = 'linear')
            animJoint.ballSpin .set(-180)
            inside_piv.rotateY.set(flipValue*-180)
            setDrivenKeyframe(inside_piv.rotateY, cd = animJoint.ballSpin, itt='linear', ott = 'linear')
            
            #reset animJoint
            resetAttrs(animJoint)
            
            #IK foot parenting
            '''
            anim
                heel via parent constraint
                    outside
                        inside
                            toe
                                toe fk
                                    toe ik
                                toe lift
                                    foot ik
                                    leg ik
            '''
            parent(foot_ik, ik, toe_lift_piv)
            parent(toe_ik, toe_fk_piv)
            parent(toe_fk_piv, toe_lift_piv, toe_piv)
            parent(toe_piv, inside_piv)
            parent(inside_piv, outside_piv)
            parent(outside_piv, heel_piv)
            heel_piv_grp = group(heel_piv, n = (heel_piv.name() + "_grp"))
            parentConstraint(animJoint, heel_piv_grp, mo =1, w=1)
            
            #PV
            pvLoc = createPVLocator(FK_joints[0], FK_joints[1], FK_joints[2])
            labels = getJointLabels(IK_joints[1])
            select(cl=1)
            pvJoint = joint()
            pvJoint.rename("%s_%s_pv_anim"%(labels[0], labels[1]))
            sphere = polySphere()[0]
            appendShape(sphere, pvJoint)
            alignPointOrient(pvLoc, pvJoint, 1,0)
            alignPointOrient(animJoint, pvJoint, 0,1)
            addAnimAttr(pvJoint)
            delete(pvLoc)
            delete(sphere)
            poleVectorConstraint(pvJoint, ik, w=1)
            pvJointGrp = createZeroedOutGrp(pvJoint)
            pvJoint.v.set(keyable = 0)
            
            #connect IK and FK to the control
            select(cl=1)
            switchGroup = group(n = '%s_FKIK_switch'%compName)
            switchGroup.addAttr('FKIK_switch', keyable = 1)
            switchGroup.FKIK_switch.setMax(1)
            switchGroup.FKIK_switch.setMin(0)
            switchGroup.FKIK_switch.setKeyable(1)
            rev = createNode('reverse')
            switchGroup.FKIK_switch >> rev.inputX
            for inc in xrange(len(FK_joints)):
                const = parentConstraint(FK_joints[inc], IK_joints[inc], control_joints[inc])    
                rev.outputX >> const.w0
                switchGroup.FKIK_switch >> const.w1
            lockAndHideAttrs(switchGroup, ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy','sz','v'))
            
            #ik stretchyness
            startPoint = None
            endPoint = None
            zeroGrp = None
            globalMultiplier = createNode('multiplyDivide')
            distDim = None
            if stretchy:
                #get total distance
                totalLength = 0
                totalLength += IK_joints[1].translateX.get() #upper arm length
                totalLength += IK_joints[2].translateX.get() #lower arm length
                totalLength = abs(totalLength)
                #create way of keeping currnet distance
                startPoint = spaceLocator()
                startPoint.translate.set(3.3615,2.2215554,7.659)#random point
                endPoint = spaceLocator()
                endPoint.translate.set(2.84596,23.2155,0.3325)#random point
                distDim = distanceDimension(sp=startPoint.translate.get(),ep= endPoint.translate.get())
                distDim = PyNode(distDim)
                alignPointOrient(IK_joints[0], startPoint, 1,0)
                alignPointOrient(IK_joints[2], endPoint, 1,0)
                #move end with foot attrs
                heelRotGrp = group(empty = 1, n = "%s_heel_rot"%compName)
                alignPointOrient(heel_piv, heelRotGrp, 1,1)
                heelRotGrp.rotateOrder.set(heel_piv.rotateOrder.get())
                
                ballRotGrp = group(empty = 1, n = "%s_ball_rot"%compName)
                alignPointOrient(IK_joints[3], ballRotGrp, 1,1)
                ballRotGrp.rotateOrder.set(IK_joints[3].rotateOrder.get())
                
                toeRotGrp = group(empty = 1, n = "%s_toe_rot"%compName)
                alignPointOrient(toe_piv, toeRotGrp,1,1)
                toeRotGrp.rotateOrder.set(toe_piv.rotateOrder.get())
                
                insideRotGrp = group(empty =1, n = "%s_inside_rot"%compName)
                alignPointOrient(inside_piv, insideRotGrp, 1,1)
                insideRotGrp.rotateOrder.set(inside_piv.rotateOrder.get())
                
                outsideRotGrp = group(empty = 1, n = "%s_outside_rot"%compName)
                alignPointOrient(outside_piv, outsideRotGrp, 1,1)
                outsideRotGrp.rotateOrder.set(outside_piv.rotateOrder.get())
                
                heelZeroGrp = createZeroedOutGrp(heelRotGrp)
                ballZeroGrp = createZeroedOutGrp(ballRotGrp)
                toeZeroGrp = createZeroedOutGrp(toeRotGrp)
                insideZeroGrp = createZeroedOutGrp(insideRotGrp)
                outsideZeroGrp = createZeroedOutGrp(outsideRotGrp)
                
                parent(outsideZeroGrp,heelRotGrp)
                parent(insideZeroGrp, outsideRotGrp)
                parent(toeZeroGrp, insideRotGrp)
                parent(ballZeroGrp, toeRotGrp)
                parent(endPoint, ballRotGrp)
                
                
                animJoint.heelSpin >> heelRotGrp.rotateY
                animJoint.heelLift >> heelRotGrp.rotateZ
                
                ballRotMult = createNode("multiplyDivide")
                ballRotMult.input2X.set(-1)
                animJoint.ballLift >> ballRotMult.input1X
                ballRotMult.outputX >> ballRotGrp.rotateZ
                
                toeRotMult = createNode("multiplyDivide")
                toeRotMult.input2X.set(-1)
                toeRotMult.input2Y.set(-1)
                animJoint.toeLift >> toeRotMult.input1X
                toeRotMult.outputX >> toeRotGrp.rotateZ
                animJoint.toeSpin >> toeRotMult.input1Y
                toeRotMult.outputY >> toeRotGrp.rotateY
                
                insideRotMult = createNode("multiplyDivide")
                insideRotMult.input2X.set(-1)
                transformLimits(insideRotGrp, erx=(True, False), rx=(0, 0))
                animJoint.sideToSide >> insideRotMult.input1X
                insideRotMult.outputX >> insideRotGrp.rotateX
                
                outsideRotMult = createNode("multiplyDivide")
                outsideRotMult.input2X.set(-1)
                transformLimits(outsideRotGrp, erx=(False, True), rx=(0, 0))
                animJoint.sideToSide >> outsideRotMult.input1X
                outsideRotMult.outputX >> outsideRotGrp.rotateX
                
                parentConstraint(animJoint, heelZeroGrp, mo=1, w=1)
                zeroGrp = heelZeroGrp
                #create basic setup with calc nodes
                    #multipler
                
                
                globalMultiplier.input1X.set(totalLength)
                globalMultiplier.input2X.set(1)
                #still have to put topCon globalsclae input globalMultiplier.input2X
                
                ratio = createNode('multiplyDivide') #outputX = currentLength\(orig*globalScale)
                ratio.operation.set(2)#divide
                globalMultiplier.outputX >> ratio.input2X
                distDim.distance >> ratio.input1X
                    #conditional
                condition = createNode('condition')
                ratio.outputX >> condition.firstTerm
                condition.secondTerm.set(1)
                condition.operation.set(2)#greater than, if current ratio > 1
                condition.colorIfFalseR.set(1)
                ratio.outputX >> condition.colorIfTrueR
                
                #add stretchy to the FK and IK joints
                for j in xrange(2):
                    ikJoint = IK_joints[j+1] # want to use FK/IK_joints[1,2] 
                    jointMult = createNode('multiplyDivide')
                    orig = ikJoint.translateX.get()
                    jointMult.input1X.set(orig)
                    condition.outColorR >> jointMult.input2X
                    jointMult.outputX >> ikJoint.translateX
            
            #connect control joints to bind joints
            for inc in xrange(len(FK_joints)):#-1
                parentConstraint(control_joints[inc], bind_joints[inc])
            
            lockAndHideAttrs(animJoint, ['sx','sy','sz','radius'])
            lockAndHideAttrs(pvJoint, ['rx', 'ry', 'rz','sx','sy','sz','radius'])    
                
            #grouping
            select(cl=1)
            jointGrp = group([FK_joints[0], IK_joints[0], control_joints[0]],n='%s_joint_grp'%compName)
            animGrp = group([animJointGrp, pvJointGrp, switchGroup], n = "%s_anim_grp"%compName)
            dntGrp = group([distDim, heel_piv_grp], n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            #hiding
            if stretchy:
                parent(startPoint, dntGrp)
                parent(zeroGrp, dntGrp)
            control_joints[0].hide()
            dntGrp.hide()
            heel_piv.v.set(0)
            switchGroup.FKIK_switch >> IK_joints[0].visibility
            rev.outputX >> FK_joints[0].visibility
            switchGroup.FKIK_switch >> pvJoint.v
            switchGroup.FKIK_switch >> animJoint.v
            animJointGrp.inheritsTransform.set(0)#allows the feet not to move when hip moves, if hip.
            
            
            #connections to meta
            connectToMeta(ik, self.networkNode, 'ikHandle')
            connectToMeta(pvJoint, self.networkNode, 'pvAnim')
            connectToMeta(animJoint, self.networkNode, 'ikAnim')
            connectToMeta(switchGroup, self.networkNode, 'switchGroup')        
            self.networkNode.setAttr('switchAttr', 'FKIK_switch',  f=1)
            self.networkNode.setAttr('stretchy', stretchy,  f=1)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            connectToMeta(dntGrp, self.networkNode, 'dntGrp')
            connectToMeta(heel_piv, self.networkNode, 'heelPiv')
            connectToMeta(toe_piv, self.networkNode, 'toePiv')
            connectToMeta(inside_piv, self.networkNode, 'insidePiv')
            connectToMeta(outside_piv, self.networkNode, 'outsidePiv')
            connectToMeta(toe_lift_piv, self.networkNode, 'toeLiftPiv')
            connectToMeta(toe_fk_piv, self.networkNode, 'toeFKPiv')
            connectToMeta(globalMultiplier, self.networkNode, 'globalMultiplier')
            connectChainToMeta(FK_joints, self.networkNode, 'FKJoints')
            connectChainToMeta(IK_joints, self.networkNode, 'IKJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
    
    def getSwitchAttr(self):
        switchNode = self.networkNode.switchGroup.listConnections()[0]
        switchAttrName = self.networkNode.switchAttr.get()
        return switchNode.attr(switchAttrName)
    
    def alignSwitch(self):
        '''
        toggle between FK and IK while keeping current joint placement
        '''
        switchGroup = listConnections(self.networkNode.switchGroup)[0]    
        switchAttr = self.networkNode.switchAttr.get()
        
        if switchGroup.attr(switchAttr).get() < .5:
            #snap ik to fk
            ikjs = self.networkNode.IKJoints.listConnections()
            fkjs = self.networkNode.FKJoints.listConnections()
            controljs = self.networkNode.controlJoints.listConnections()
            ikAnim = listConnections(self.networkNode.ikAnim)[0]
            pvAnim = listConnections(self.networkNode.pvAnim)[0]
            ikAnim.translate.lock()
            resetAttrs(ikAnim)
            ikAnim.translate.unlock()
            alignPointOrient(controljs[2],ikAnim, 1,1)
            pvLoc = createPVLocator(fkjs[0], fkjs[1], fkjs[2])
            alignPointOrient(pvLoc, pvAnim, 1,0)
            alignPointOrient(ikjs[1], pvAnim, 0,1)
            delete(pvLoc)
            ball_fk_joint = fkjs[-2]
            ikAnim.toeWiggle.set(ball_fk_joint.rotateZ.get())
            switchGroup.attr(switchAttr).set(1)
            setKeyframe(switchGroup.attr(switchAttr), itt='spline' , ott = 'step')
             
        else:
            #snap fk to ik
            ikjs = self.networkNode.IKJoints.listConnections()
            fkjs = self.networkNode.FKJoints.listConnections()
            for inc in xrange(len(fkjs)):
                if inc == 1 or inc == 2:
                    fkjs[inc].translateX.unlock()
                    fkjs[inc].translateX.set(ikjs[inc].translateX.get())
                    fkjs[inc].translateX.lock()
                alignPointOrient(ikjs[inc],fkjs[inc], 0,1)
            switchGroup.attr(switchAttr).set(0)
            setKeyframe(switchGroup.attr(switchAttr), itt='spline' , ott = 'step')    
    
            
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
            
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            ik_joints = self.networkNode.IKJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
                if location == fk_joints[inc]:
                    return control_joints[inc]
                if location == ik_joints[inc]:
                    return control_joints[inc]
        raise Exception("FKIKLeg.getConnectObj: location wasn't found, try 'start', 'end', or name of bind, fk, ik, or control joint.")

    def isIK(self):
        return True
    
    def getIK(self):
        return self.networkNode.ikHandle.listConnections()[0]
        
    def isFK(self):
        return True

    def getIKAnim(self):
        '''
        returns the ik anim at the end of the IK chain
        '''
        return self.networkNode.ikAnim.listConnections()[0]
        
    def getPVAnim(self):
        '''
        returns the pole vector anim
        '''    
        return self.networkNode.pvAnim.listConnections()[0]
        
    def getFKAnims(self):
        '''
        returns all the FK anims
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        allAnims = []
        allAnims.append(self.getPVAnim())
        allAnims.append(self.getIKAnim())
        map(lambda x: allAnims.append(x), self.getFKAnims())
        allAnims.append(self.networkNode.switchGroup.listConnections()[0])
        return allAnims
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''
        allAnims = []
        allAnims.append(self.getPVAnim())
        allAnims.append(self.getIKAnim())
        map(lambda x: allAnims.append(x), self.getFKAnims())
        for anim in allAnims:            
            resetAttrs(anim)    
        
    def parentUnder(self, obj):
        '''
        parent this rigComponent under the obj
        obj:
            object to parent under
        '''
        if not objExists(obj):
            raise Exception("RigComponent: can't parent under $s, obj doesn't exist"%obj)
        try:
            parent(self.networkNode.componentGrp.listConnections()[0], obj)
            root = getMetaRoot(obj, 'CharacterRig')
            if root:
                try:
                    topCon = root.getTopCon()
                    topCon.globalScale >> self.networkNode.globalMultiplier.listConnections()[0].input2X
                    ikAnim = self.networkNode.ikAnim.listConnections()[0]
                    zeroGrp = ikAnim.getParent()
                    parentConstraint(topCon, zeroGrp, w=1, mo=1)
                    scaleConstraint(topCon, zeroGrp, w=1, mo =1)
                except:
                    pass
        except:
            raise Exception("%s.parentUnder: not implemeneted"%self.networkNode.metaType.get())
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        switchGroup = self.networkNode.switchGroup.listConnections()[0]
        switchAttr = self.networkNode.switchAttr.get()
        fkikMode = switchGroup.attr(switchAttr).get() < .5#true if fk
        
        pvAnim = self.getPVAnim()
        pvTrans = pvAnim.translate.get()
        ikAnim = self.getIKAnim()
        ikTrans = ikAnim.translate.get()
        ikRot = ikAnim.rotate.get()
        fkAnims = self.getFKAnims()
        fkRots = map(lambda x: x.rotate.get(), fkAnims)
        ikAnimAttrs = {"heelSpin": ikAnim.heelSpin.get(), "heelLift": ikAnim.heelLift.get(), "toeSpin": ikAnim.toeSpin.get(), "ballLift": ikAnim.ballLift.get(), "toeLift": ikAnim.toeLift.get(), "toeWiggle": ikAnim.toeWiggle.get(), "sideToSide": ikAnim.sideToSide.get() }
        if other == self:
            if fkikMode:
                map(lambda x: x.rotate.set(-x.rotate.get()[0],-x.rotate.get()[1],x.rotate.get()[2] ), fkAnims)
            else:    
                pvAnim.translate.set(pvTrans[0], pvTrans[1], -pvTrans[2])
                ikAnim.rotate.set(ikRot[0], ikRot[1], -ikRot[2])
                ikAnim.translate.set(ikTrans[0], ikTrans[1], -ikTrans[2])
                ikAnim.heelSpin.set(-ikAnim.heelSpin.get())
                ikAnim.toeSpin.set(-ikAnim.toeSpin.get())
                ikAnim.sideToSide.set(-ikAnim.sideToSide.get())
                return [self]
        else:
            otherPvAnim = other.getPVAnim()
            otherPvTrans = otherPvAnim.translate.get()
            otherIkAnim = other.getIKAnim()
            otherIkTrans = otherIkAnim.translate.get()
            otherIkRot = otherIkAnim.rotate.get()
            otherFkAnims = other.getFKAnims()
            otherFkRots = map(lambda x: x.rotate.get(), otherFkAnims)
            otherIkAnimAttrs = {"heelSpin": otherIkAnim.heelSpin.get(), "heelLift": otherIkAnim.heelLift.get(), "toeSpin": otherIkAnim.toeSpin.get(), "ballLift": otherIkAnim.ballLift.get(), "toeLift": otherIkAnim.toeLift.get(), "toeWiggle": otherIkAnim.toeWiggle.get(), "sideToSide": otherIkAnim.sideToSide.get() }
            otherSwitchGroup = other.networkNode.switchGroup.listConnections()[0]
            otherSwitchAttr = other.networkNode.switchAttr.get()
            other_fkikMode = otherSwitchGroup.attr(otherSwitchAttr).get() < .5#true if fk        
            if bothSides:
                if not fkikMode and not other_fkikMode: #both IK, do a nicer switch
                    #change this
                    ikAnim.translate.set(-otherIkTrans)
                    ikAnim.rotate.set(otherIkRot)
                    for x in ikAnimAttrs.keys():
                        ikAnim.attr(x).set(otherIkAnimAttrs[x])
                    pvAnim.translate.set(-otherPvTrans)
                    #change other
                    otherIkAnim.translate.set(-ikTrans)
                    otherIkAnim.rotate.set(ikRot)
                    for x in otherIkAnimAttrs.keys():
                        otherIkAnim.attr(x).set(ikAnimAttrs[x])
                    otherPvAnim.translate.set(-pvTrans)
                    return [self, other]
                else:
                    switched = 0
                    if not (other_fkikMode == fkikMode):
                        other.alignSwitch()
                        switched = 1
                        otherPvTrans = otherPvAnim.translate.get()
                        otherIkTrans = otherIkAnim.translate.get()
                        otherIkRot = otherIkAnim.rotate.get()
                        otherFkAnims = other.getFKAnims()
                        otherFkRots = map(lambda x: x.rotate.get(), otherFkAnims)
                        otherIkAnimAttrs = {"heelSpin": otherIkAnim.heelSpin.get(), "heelLift": otherIkAnim.heelLift.get(), "toeSpin": otherIkAnim.toeSpin.get(), "ballLift": otherIkAnim.ballLift.get(), "toeLift": otherIkAnim.toeLift.get(), "toeWiggle": otherIkAnim.toeWiggle.get(), "sideToSide": otherIkAnim.sideToSide.get() }
                    if fkikMode: #swap FKs
                        #change this
                        for num in xrange(len(otherFkAnims)):
                            anim = fkAnims[num]
                            if not anim.rotateX.isLocked():
                                anim.rotateX.set(otherFkRots[num][0])
                            if not anim.rotateY.isLocked():
                                anim.rotateY.set(otherFkRots[num][1])
                            if not anim.rotateZ.isLocked():
                                anim.rotateZ.set(otherFkRots[num][2])
                        #change other
                        for num in xrange(len(fkAnims)):
                            otherAnim = otherFkAnims[num]
                            if not otherAnim.rotateX.isLocked():
                                otherAnim.rotateX.set(fkRots[num][0])
                            if not otherAnim.rotateY.isLocked():
                                otherAnim.rotateY.set(fkRots[num][1])
                            if not otherAnim.rotateZ.isLocked():
                                otherAnim.rotateZ.set(fkRots[num][2])
                    else: #swap IKs
                        #change this
                        ikAnim.translate.set(-otherIkTrans)
                        ikAnim.rotate.set(otherIkRot)
                        for x in ikAnimAttrs.keys():
                            ikAnim.attr(x).set(otherIkAnimAttrs[x])
                        pvAnim.translate.set(-otherPvTrans)
                        #change other
                        otherIkAnim.translate.set(-ikTrans)
                        otherIkAnim.rotate.set(ikRot)
                        for x in otherIkAnimAttrs.keys():
                            otherIkAnim.attr(x).set(ikAnimAttrs[x])
                        otherPvAnim.translate.set(-pvTrans)
                    if switched:
                        other.alignSwitch()
                    return [self, other]                
            else:
                #mirror self
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                if other_fkikMode:
                    for num in xrange(len(otherFkAnims)):
                            anim = fkAnims[num]
                            if not anim.rotateX.isLocked():
                                anim.rotateX.set(otherFkRots[num][0])
                            if not anim.rotateY.isLocked():
                                anim.rotateY.set(otherFkRots[num][1])
                            if not anim.rotateZ.isLocked():
                                anim.rotateZ.set(otherFkRots[num][2])
                else:
                    try:
                        pvAnim.translate.set(-otherPvTrans)
                    except: pass
                    try:
                        ikAnim.translate.set(-otherIkTrans)
                    except: pass
                    try:
                        ikAnim.rotate.set(otherIkRot)
                    except: pass
                    try:
                        for x in ikAnimAttrs.keys():
                            ikAnim.attr(x).set(otherIkAnimAttrs[x])
                    except: pass
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
            return [self]

            
class FKIKQuadrupedLeg(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, heelJoint, toeJoint, insideJoint, outsideJoint,
                        kneeAngleBias=None, ankleAngleBias=None, primaryRotationAxis='z', stretchy=0, flipSpringHandle=False, node=''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        
        
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKQuadrupedLeg'):
                    self.networkNode = node
                else:
                    printError("FKIKQuadrupedLeg: node %s is not a FKIKQuadrupedLeg metaNode"%(node))
            else:
                printError("FKIKQuadrupedLeg: node %s doesn't exist"%(node))
            return None

        RigComponent.__init__(self, 'FKIKQuadrupedLeg', 1.0, 'FK/IK switchable leg for a quadruped.', side, bodyPart, startJoint, endJoint)
        compName = side+'_'+bodyPart
        
        '''
        # FOR TESTING
        import re
        from pymel.core import *
        from scene_manager.methods import *
        import maya.mel as mel
        import scene_manager.metaUtil as mu
        import scene_manager.metaCore as meta
        import pymel.core.runtime as rt
        import pymel.core.other as other
        import os
        import random
        reload(meta)
        reload(mu)


        lastFilePromptValue = mel.eval('file -q -pmt')
        mel.eval('file -pmt 0') # Squelch any error prompts
        openFile(sceneName(), f=1)
        mel.eval('file -pmt '+str(lastFilePromptValue))

        char = meta.CharacterRig('Puppy', 'y', 'z', ['center_root'])

        hindLeg = meta.FKIKQuadrupedLeg('left', 'hindLeg', 'femur_jnt', 'toe_jnt_end',
                                        'heel_piv', 'toe_piv', 'inside_piv', 'outside_piv')
        char.addRigComponent(hindLeg)
        '''
        
        chain = chainBetween(startJoint, endJoint)
        springChain = duplicateChain(chain[0], chain[3])
        ikChain = duplicateChain(chain[0], chain[-1])



        # Set primary rotation axis on ik chain's knee joint.  This reduces (but does not eliminate)
        # the knee locking problem that happens when it's driven by the spring chain and both ends
        # of the ik handle are moved close together.
        if primaryRotationAxis == 'x':
            ikChain[1].jointTypeX.set(1)
            ikChain[1].jointTypeY.set(0)
            ikChain[1].jointTypeZ.set(0)
        elif primaryRotationAxis == 'y':
            ikChain[1].jointTypeX.set(0)
            ikChain[1].jointTypeY.set(1)
            ikChain[1].jointTypeZ.set(0)
        elif primaryRotationAxis == 'z':
            ikChain[1].jointTypeX.set(0)
            ikChain[1].jointTypeY.set(0)
            ikChain[1].jointTypeZ.set(1)
        else:
            raise '[methodname]: Primary rotation axis not recognized.  Please specify "x", "y", or "z"'


        # Ik Spring chain to guide the direction of the main ik chain
        mel.eval('ikSpringSolver;')
        springIk = ikHandle(  n=compName+'_springIkHandle',
                              priority=0, # Order in which handles are evaluated
                              sj=springChain[0], # Start joint
                              ee=springChain[3], # End joint
                              solver='ikSpringSolver'  ) # Spring Solver
        springIkHandle = springIk[0]

        # Set angle bias
        refresh() # Spring angle bias attribute not detected without refresh
        
        kneeAngleWeight = (mu.getWorldPositionVector(chain[0]) - mu.getWorldPositionVector(chain[2])).length()
        ankleAngleWeight = (mu.getWorldPositionVector(chain[1]) - mu.getWorldPositionVector(chain[3])).length()
        normalizer = max(kneeAngleWeight, ankleAngleWeight)
        kneeAngleWeight = kneeAngleWeight/normalizer
        ankleAngleWeight = ankleAngleWeight/normalizer
        
        if kneeAngleBias != None:
            kneeAngleWeight = kneeAngleBias
        if ankleAngleBias != None:
            ankleAngleWeight = ankleAngleBias
        
        #springIkHandle.springAngleBias[0].springAngleBias_FloatValue.set(kneeAngleWeight)
        #springIkHandle.springAngleBias[1].springAngleBias_FloatValue.set(ankleAngleWeight)
                             
        # Main IK chain
        mainIk = ikHandle(  n=compName+'mainIkHandle',
                            priority=2, # Order in which handles are evaluated
                            sj=ikChain[0], # Start joint
                            ee=ikChain[2], # End joint
                            solver='ikRPsolver'  ) # Spring Solver
        mainIkHandle = mainIk[0]

        # Hook main ik ankle to a locator which will later be driven by an ankle rotation anim
        ankleMainTarget = spaceLocator(n=compName+'ankleMainTarget')
        delete(parentConstraint(ikChain[2], ankleMainTarget, mo=0))
        mainIkPcHook = pointConstraint(ankleMainTarget, mainIkHandle, mo=0)
        hide(ankleMainTarget)
        
        # Create an ik chain which simulates the maximum angle of ankle joint when the leg is completely straight
        length_ToAnkle =   mu.getChainLength(chain[0], chain[2])
        length_ToFoot =    mu.getChainLength(chain[0], chain[3])
        
        select(cl=1)

        maxRotChain_startPos = mu.getWorldPositionVector(chain[0])
        maxRotChain_middlePos = mu.getWorldPositionVector(chain[0], [length_ToAnkle, 0, 0])
        maxRotChain_endPos = mu.getWorldPositionVector(chain[0], [length_ToFoot, 0, 0])

        maxRotChain_startJnt = joint(p=maxRotChain_startPos, n='ankleMaxRot_leg_jnt')
        delete(parentConstraint(chain[0], maxRotChain_startJnt))
        makeIdentity(maxRotChain_startJnt, r=1, t=0, s=0, jo=0, a=1)
        maxRotChain_middleJnt = joint(p=maxRotChain_middlePos, n='ankleMaxRot_ankle_jnt')
        maxRotChain_endJnt = joint(p=maxRotChain_endPos, n='ankleMaxRot_end_jnt')

        select(cl=1)

        maxRot_ik = ikHandle(  n=compName+'ankleMaxRot_ikHandle',
                            priority=1, # Order in which handles are evaluated
                            sj=maxRotChain_startJnt, # Start joint
                            ee=maxRotChain_endJnt, # End joint
                            solver='ikRPsolver'  ) # Spring Solver
        maxRot_ikHandle = maxRot_ik[0]

        delete(pointConstraint(springChain[3], maxRot_ikHandle, mo=0))
        parent(maxRot_ikHandle, springChain[3])
        poleVectorConstraint(ankleMainTarget, maxRot_ikHandle)
        
        # Create the condition required to make the ikleg (to the ankle) use the stopping point rather than the
        # ankle target.  If current distance from origin of the ankle > chain length to the ankle then
        # use the stopping point.

        # Current dist to ankle
        hipLoc = spaceLocator(n=compName+'hipLocation')
        delete(parentConstraint(springChain[0], hipLoc, mo=0))
        parent(hipLoc, springChain[0])
        distToAnkle = distanceDimension(hipLoc, ankleMainTarget).getParent()
        distToAnkle.rename(compName+'distToAnkle')

        # Default dist to ankle. Uses another distance measure instead of a constant value to account for rig scaling.
        maxDistAnkleLoc = spaceLocator(n=compName+'maxDistAnkleLocation')
        delete(parentConstraint(maxRotChain_middleJnt, maxDistAnkleLoc, mo=0))
        parent(maxDistAnkleLoc, maxRotChain_middleJnt)
        defaultDistToAnkle = distanceDimension(hipLoc, maxDistAnkleLoc).getParent()
        defaultDistToAnkle.rename(compName+'defaultDistToAnkle')

        # Condition: if current dist > max dist
        cond = createNode('condition', n='ifLegIsOverExtended')
        cond.operation.set(3) # Greater than or equal
        defaultDistToAnkle.distance >> cond.firstTerm
        distToAnkle.distance >> cond.secondTerm
        cond.colorIfTrue.set(1,0,0)
        cond.colorIfFalse.set(0,1,0)

        # Add max rotation target to main ik handle and plug in the condition node's output to the target weights
        pointConstraint( maxRotChain_middleJnt, mainIkHandle, mo=0 )
        cond.outColor.outColorR >> mainIkPcHook.w0
        cond.outColor.outColorG >> mainIkPcHook.w1

        # Prepare foot pivot structure for SDKs
        heelJoint = PyNode(heelJoint)
        insideJoint = PyNode(insideJoint)
        outsideJoint = PyNode(outsideJoint)
        toeJoint = PyNode(toeJoint)

        heel_piv = duplicate(ikChain[4], po=1, n='%s_heel_piv_joint'%compName)[0]
        toe_piv = duplicate(ikChain[4], po=1, n='%s_toe_piv_joint'%compName)[0]
        toe_lift_piv = duplicate(ikChain[4], po=1, n='%s_toe_lift_piv_joint'%compName)[0]
        toe_fk_piv = duplicate(ikChain[4], po=1, n='%s_toe_fk_piv_joint'%compName)[0]
        inside_piv = duplicate(ikChain[4], po=1, n='%s_inside_piv_joint'%compName)[0]
        outside_piv = duplicate(ikChain[4], po=1, n='%s_outside_piv_joint'%compName)[0]

        parent([heel_piv, toe_piv, toe_lift_piv, toe_fk_piv, inside_piv, outside_piv], w=1)

        alignPointOrient(heelJoint, heel_piv, 1,0)
        alignPointOrient(insideJoint, inside_piv, 1,0)
        alignPointOrient(outsideJoint, outside_piv, 1,0)
        alignPointOrient(toeJoint, toe_piv, 1,0)
        alignPointOrient(ikChain[4], toe_lift_piv, 1,0)
        alignPointOrient(ikChain[4], toe_fk_piv, 1,0)

        delete(heelJoint, insideJoint, outsideJoint, toeJoint)

        ballIkHandle = ikHandle( sj= ikChain[3], ee = ikChain[4], sol ='ikSCsolver', n=compName+'ballIkHandle')[0]
        toeIkHandle = ikHandle( sj= ikChain[4], ee = ikChain[5], sol ='ikSCsolver', n=compName+'toeIkHandle')[0]

        '''
        anim
            heel via parent constraint
                outside
                    inside
                        toe
                            toe fk
                                toe ik
                            toe lift
                                foot ik
                                leg ik
        '''
        parent(ballIkHandle, springIkHandle, toe_lift_piv)
        parent(toeIkHandle, toe_fk_piv)
        parent(toe_fk_piv, toe_lift_piv, toe_piv)
        parent(toe_piv, inside_piv)
        parent(inside_piv, outside_piv)
        parent(outside_piv, heel_piv)
        heelPivGrp = group(n=heel_piv.name() + "_grp", em=1)
        delete(parentConstraint(heel_piv, heelPivGrp, mo=0))
        parent(heel_piv, heelPivGrp)

        #################
        ##  IK ANIMS   ##
        #################



        ## FOOT ANIM ##
        select(cl=1)
        footIkAnim = joint()
        addAnimAttr(footIkAnim)
        footIkAnim.rename(compName + '_foot_ik_anim')

        delete(parentConstraint(chain[3], footIkAnim, mo=0)) # Align foot anim with the foot joint

        mu.transferShapes(polyCube(ch=0)[0], footIkAnim) # Default anim shape

        footIkAnim_zeroGrp = createZeroedOutGrp(footIkAnim)
        lockAndHideAttrs(footIkAnim, ['s', 'radius'])

        parentConstraint(footIkAnim, heelPivGrp, mo=1) # Hook ik leg to the anim
        
        # Add the foot's SDK attrs
        for sdkName in ['ballLift', 'ballSwivel', 'sideToSide', 'heelToToe',
                        'toeWiggle', 'toeSwivel', 'toeSpin', 'ballSpin', 'heelSpin']:
            footIkAnim.addAttr(sdkName,   k=1, dv=0, min=-180, max=180)

        # Value that flips the animation on certain set driven attributes
        # based on the side of the character this component is on
        if (side == 'right'):
            flip = -1
        else:
            flip = 1

        # ballLift
        mu.sdk( footIkAnim.ballLift, [-180, 180], toe_lift_piv.rz, [180, -180] )
                
        # ballSwivel
        mu.sdk( footIkAnim.ballSwivel, [-180, 180], toe_lift_piv.ry, [-flip*180, flip*180] )
                
        # sideToSide
        mu.sdk( footIkAnim.sideToSide, [-180, 0], inside_piv.rx, [flip*180, 0] )
        mu.sdk( footIkAnim.sideToSide, [0, 180], outside_piv.rx, [0, -flip*180] )
                
        # heelToToe
        mu.sdk( footIkAnim.heelToToe, [-180, 0], toe_piv.rz, [-180, 0] )
        mu.sdk( footIkAnim.heelToToe, [0, 180], heel_piv.rz, [0, 180] )
                
        # toeSpin
        mu.sdk( footIkAnim.toeSpin, [-180, 180], toe_piv.ry, [-flip*180, flip*180] )

        # ballSpin
        mu.sdk( footIkAnim.ballSpin, [-180, 180], inside_piv.ry, [-flip*180, flip*180] )

        # heelSpin
        mu.sdk( footIkAnim.heelSpin, [-180, 180], heel_piv.ry, [-flip*180, flip*180] )

        # toeWiggle
        mu.sdk( footIkAnim.toeWiggle, [-180, 180], toe_fk_piv.rz, [-180, 180] )

        # toeSwivel
        mu.sdk( footIkAnim.toeSwivel, [-180, 180], toe_fk_piv.ry, [-flip*180, flip*180] )
        
        ## KNEE AIM ANIM ##
        select(cl=1)
        kneeAimAnim = joint()
        addAnimAttr(kneeAimAnim)
        kneeAimAnim.rename(compName + '_knee_aim_anim')

        pvLoc = createPVLocator(chain[0], chain[1], chain[2]) # Use pv loc to align anim
        delete(pointConstraint(pvLoc, kneeAimAnim, mo=0))
        delete(orientConstraint(footIkAnim, kneeAimAnim, mo=0))
        
        # Will aim main ik chain knee at the pvLock later
        pvLoc.rename(compName + '_mainIkTarget')
        parent(pvLoc, springChain[1])

        mu.transferShapes(polySphere(ch=0)[0], kneeAimAnim) # Default anim shape

        kneeAimAnim_zeroGrp = createZeroedOutGrp(kneeAimAnim)
        lockAndHideAttrs(kneeAimAnim, ['r', 's', 'radius'])
        
        # Aim the spring chain at the knee aim anim
        poleVectorConstraint(kneeAimAnim, springIkHandle)
        if(flipSpringHandle): springIkHandle.twist.set(180) # TOFIX: Need more permanent solution
        
        # The main ik leg will aim at the spring's knee instead
        # of the aim anim in case the ankle aimer has rotation
        poleVectorConstraint(pvLoc, mainIkHandle)

        # Connect ik pin handle to this anim
        '''
        pointConstraint(kneeAimAnim, ikPinUpper_ikHandle)
        '''
        

        ## ANKLE AIM ##
        
        # By default the ankle's parent will aim along the spring chain,
        # but this can be switched to be controlled by the foot
        
        select(cl=1)
        ankleAimAnim = joint()
        addAnimAttr(ankleAimAnim)
        ankleAimAnim.rename(compName+ '_ankle_angle_anim')

        c = polyCone(ch=0)[0]
        delete(pointConstraint(chain[3], c, mo=0))
        delete(aimConstraint(chain[2], c, mo=0, aim=[0,1,0]))
        delete(pointConstraint(chain[2], c, mo=0))
        delete(pointConstraint(chain[3], ankleAimAnim, mo=0))
        delete(orientConstraint(chain[2], ankleAimAnim, mo=0))

        mu.transferShapes(c, ankleAimAnim, 'world')
        
        ankleAimAnim_zeroGrp = createZeroedOutGrp(ankleAimAnim)
        lockAndHideAttrs(ankleAimAnim, ['t', 's', 'radius'])

        # Alternate ankle aimer parent space
        ankleAimerFootParentSpace = group(em=1, n=compName+'_ankleAimerFootParentSpace')
        delete(parentConstraint(ankleAimAnim, ankleAimerFootParentSpace))
        parent(ankleAimerFootParentSpace, heelPivGrp)
        pointConstraint(springIkHandle, ankleAimerFootParentSpace, mo=0)
        
        ankleAimAnimOrientationPc = parentConstraint(springChain[2], ankleAimerFootParentSpace, ankleAimAnim_zeroGrp, mo=1)
        ankleAimAnimOrientationPc.interpType.set(2) # Shortest path
        
        # Blend attribute to follow leg by default
        ankleAimAnim.addAttr('followLeg', k=1, dv=1, min=0, max=1)
        ankleAimRev = createNode('reverse')
        ankleAimAnim.followLeg >> ankleAimAnimOrientationPc.w0
        ankleAimAnim.followLeg >> ankleAimRev.inputX
        ankleAimRev.outputX >> ankleAimAnimOrientationPc.w1
        
        # The ankle main target will be aimed by this anim
        parent(ankleMainTarget,  ankleAimAnim)


        # Ankle joint alignment on the main chain
        aimConstraint(  springChain[3],
                        ikChain[2],
                        aim=[1,0,0],
                        u=[0,1,0],
                        wut='objectrotation',
                        wuo=ankleAimAnim,
                        wu=[0,1,0],
                        mo=1  ) 



        ## IK ANIM INFO ##
        ikAnims = [footIkAnim, kneeAimAnim, ankleAimAnim]
        ikAnimZeroGrps = [footIkAnim_zeroGrp, kneeAimAnim_zeroGrp, ankleAimAnim_zeroGrp]


        #################
        ##  FK ANIMS   ##
        #################



        ## ALL FK ANIMS ##
        fkAnims = duplicateChain(chain[0], chain[-1])
        makeIdentity(fkAnims[0], t=0, s=1, r=1, jo=0, a=1)

        for i in xrange(len(fkAnims)-1):
            
            # Transofrm each individual FK chain joint to an anim.
            # We don't need zero groups since we have joint orient to work with.
            fkAnim = fkAnims[i]
            addAnimAttr(fkAnim)
            fkAnim.rename(compName + '_' + str(i) + '_fk_anim')
            
            addBoxToJoint(fkAnim)
            
            lockAndHideAttrs(fkAnim, ['t', 's', 'radius'])

        # We just needed the end joint to create the default box shape.  Remove it.
        delete(fkAnims[-1])
        del fkAnims[-1]

        # Lock in knee axis
        if primaryRotationAxis == 'x':
            lockAndHideAttrs(fkAnims[1], ['ry', 'rz'])
        elif primaryRotationAxis == 'y':
            lockAndHideAttrs(fkAnims[1], ['rx', 'rz'])
        elif primaryRotationAxis == 'z':
            lockAndHideAttrs(fkAnims[1], ['rx', 'ry'])

        # Lock toe x rotate
        lockAndHideAttrs(fkAnims[4], ['rx'])

        #################
        ##  SWITCHER   ##
        #################



        ## SWITCHER ANIM ##
        switchAnim = group(n=compName + '_FKIK_switch', em=1)
        switchAnim.addAttr('FKIK_switch', k=1, min=0, max=1, dv=1)
        switchRev = ankleAimRev # Reuse the reverse node from the ankle aim anim parent space
        switchAnim.FKIK_switch >> switchRev.inputY
        delete(pointConstraint(chain[0], switchAnim, mo=0))
        lockAndHideAttrs(switchAnim, ['t', 'r', 's', 'v'])

        # Connect FK/IK chains to the main chain and hook the switcher up to their
        # constraint weights and visibilities
        for i in xrange(len(chain)-1):
            mainJnt = chain[i]
            ikJnt = ikChain[i]
            fkAnim = fkAnims[i]
            if i == 0:
                const = parentConstraint(fkAnim, ikJnt, mainJnt, mo=0)
            else:
                const = orientConstraint(fkAnim, ikJnt, mainJnt, mo=0) # Use orient constraints for better blending
            switchAnim.FKIK_switch >> const.w1
            switchRev.outputY >> const.w0
            switchRev.outputY >> fkAnim.visibility
            lockAndHideAttrs(fkAnim, ['v'])
            
        # Make sure ikAnims get hidden correctly
        for ikAnim in ikAnims:
            switchAnim.FKIK_switch >> ikAnim.visibility
            lockAndHideAttrs(ikAnim, ['v'])

            
            
        #################
        ##  CLEAN-UP   ##
        #################


        
        # Main anchor group for what to attach the leg to
        anchorGrp = group(n=compName + '_anchor_grp', em=1)

        delete(parentConstraint(chain[0], anchorGrp, mo=0))
        makeIdentity(anchorGrp, t=1, r=1, s=1, a=1)
        parent(springChain[0], ikChain[0], maxRotChain_startJnt, fkAnims[0], switchAnim, anchorGrp)

        # Technical workaround for spring chain pivoting oddly: pretend like it's not in the hierarchy.
        # Redundant constraints but necessary to not have the spring chain influenced directly
        # by its place in the hierarchy, and thus bug out.
        springChain[0].inheritsTransform.set(0)
        for j in springChain: j.segmentScaleCompensate.set(0)
        pointConstraint(anchorGrp, springChain[0], mo=0)
        scaleConstraint(anchorGrp, springChain[0], mo=1)
        
        # Do not touch group
        dntGrp = group([springChain[0], ikChain[0], maxRotChain_startJnt], n=compName + '_DO_NOT_TOUCH')
        parent(defaultDistToAnkle, distToAnkle, mainIkHandle, heelPivGrp, dntGrp)
        hide(dntGrp)

        # Main group
        mainGrp = group(n=compName + '_component_group', em=1)
        parent([anchorGrp]+ikAnimZeroGrps, mainGrp)
 
        # Connections to the meta node
        # - Groups
        connectToMeta(mainGrp, self.networkNode, 'componentGrp')
        connectToMeta(anchorGrp, self.networkNode, 'anchorGrp')
        connectToMeta(dntGrp, self.networkNode, 'dntGrp')
        # - Anims
        connectToMeta(switchAnim, self.networkNode, 'switchAnim') 
        connectChainToMeta(fkAnims, self.networkNode, 'fkAnims')
        connectChainToMeta(ikAnims, self.networkNode, 'ikAnims')
        # - Attr names
        self.networkNode.setAttr('switchAttr', 'FKIK_switch',  f=1)
        # self.networkNode.setAttr('stretchy', stretchy,  f=1)
        # - Structural components
        connectToMeta(heel_piv, self.networkNode, 'heelPiv')
        connectToMeta(toe_piv, self.networkNode, 'toePiv')
        connectToMeta(inside_piv, self.networkNode, 'insidePiv')
        connectToMeta(outside_piv, self.networkNode, 'outsidePiv')
        connectToMeta(toe_lift_piv, self.networkNode, 'toeLiftPiv')
        connectToMeta(toe_fk_piv, self.networkNode, 'toeFKPiv')
        connectChainToMeta(springChain, self.networkNode, 'springJoints')
        connectChainToMeta(ikChain, self.networkNode, 'ikJoints')
        connectChainToMeta(chain, self.networkNode, 'bindJoints')
        
        
    def getSwitchAttr(self):
        '''
        Returns the switch attribute of the FK/IK switcher.
        '''
        switchAnim = self.getSwitchAnim()
        switchAttrName = self.networkNode.switchAttr.get()
        return switchAnim.attr(switchAttrName)
    
    def getSwitchAnim(self):
        '''
        Returns the FK/IK switcher anim.
        '''
        return self.networkNode.switchAnim.listConnections()[0]
        
    def getFKAnims(self):
        '''
        Returns the FK anims from the root to the toe.
        '''
        return self.networkNode.fkAnims.listConnections()
        
    def getIKAnims(self):
        '''
        Returns only the three ik anims in this order: foot, knee aim, ankle aim.
        '''
        return self.networkNode.ikAnims.listConnections()
        
    def getAllAnims(self):
        '''
        Returns a list of all the anims.
        '''
        return [self.getSwitchAnim()] + self.getFKAnims() + self.getIKAnims()
        
    def alignSwitch(self, fkToIkMaxAlignIterations=32, fkToIkMatchEpsilon=0.0001):
        '''
        Toggle between FK and IK while keeping current joint placement
        
        To fix: knee aim anim drift
        '''
        
        switchAttr = self.getSwitchAttr()

        if switchAttr.get() < .5:
            # Match IK to FK
            fkAnims = self.getFKAnims()
            ikAnims = self.getIKAnims()
            ikJoints = self.networkNode.ikJoints.listConnections()
            
            foot = ikAnims[0]
            kneeAim = ikAnims[1]
            ankleAim = ikAnims[2]
            
            # FK foot -> IK foot
            alignPointOrient(fkAnims[3], foot, 1, 1)

            # Initial knee aim alignment
            kneeLoc = createPVLocator(fkAnims[0], fkAnims[1], fkAnims[3])
            alignPointOrient(kneeLoc, kneeAim, 1,0)
            delete(kneeLoc)
            
            # Initial ankle aim alignment
            alignPointOrient(fkAnims[2], ankleAim, 0, 1)
            refresh() # alignPointOrient not applied correctly without a refresh
            
            fkKneeWorldPos = mu.getWorldPositionVector(fkAnims[1])
            
            # Time fudge the knee aim anim closer until it's below a certain threshold.
            # Doing an exact match isn't feasible because of the nested ik handle setup
            for i in xrange(fkToIkMaxAlignIterations):
                ikKneeWorldPos = mu.getWorldPositionVector(ikJoints[1])
                ikAnimChange = fkKneeWorldPos-ikKneeWorldPos
                
                # If the knee is close enough, time to quit
                if (dt.Vector(ikAnimChange).length() < fkToIkMatchEpsilon):
                    break
                
                move(kneeAim, ikAnimChange, r=1, ws=1)
                
                # Adjust the ankle aim since it probably received partial
                # movement from the knee aim anim
                alignPointOrient(fkAnims[2], ankleAim, 0, 1)
                refresh() # alignPointOrient not applied correctly without a refresh
            
            # set toe orientation
            foot.t.lock()
            foot.r.lock()
            resetAttrs(foot)
            foot.t.unlock()
            foot.r.unlock()
            
            foot.toeWiggle.set(fkAnims[4].rz.get())
            foot.toeSwivel.set(fkAnims[4].ry.get())
            
            # Set switch to IK
            switchAttr.set(1)

        else:
            # Match FK to IK
            fkAnims = self.getFKAnims()
            ikJoints = self.networkNode.ikJoints.listConnections()
            for i in xrange(len(fkAnims)):
                alignPointOrient(ikJoints[i], fkAnims[i], 0, 1)
            
            # Set switch to FK
            switchAttr.set(0)
    
    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        Connects this component to the other component.
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
  
        connectObj = comp.getConnectObj(location)
        connector = self.networkNode.anchorGrp.listConnections()[0]

        skipRot = []
        skipTrans = []
        if not point:
            skipTrans = ['x','y','z']
        if not orient:
            skipRot = ['x','y','z'] 
            
        parentConstraint(connectObj, connector, sr = skipRot, st = skipTrans, mo=1)
            
    def getConnectObj(self, location):
        '''
        Gets the component to connect to at location.
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        
        if location == 'start':
            return self.networkNode.bindJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.bindJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKQuadrupedLeg.getConnectObj: location obj,%s , doesn't exist"%location)
                
            location = PyNode(location)
            
            switchAnim = self.getSwitchAnim()
            bindJoints = self.networkNode.bindJoints.listConnections()
            ikJoints = self.networkNode.ikJoints.listConnections()
            ikAnims = self.networkNode.ikAnims.listConnections()
            fkAnims = self.networkNode.fkAnims.listConnections()
            
            if (location == switchAnim): return switchAnim
            for bj in bindJoints:
                if location == bj: return bj
            for ij in ikJoints:
                if location == ij: return ij
            for ia in ikAnims:
                if location == ia: return ia
            for fa in fkAnims:
                if location == fa: return fa
            
        raise Exception("FKIKQuadrupedLeg.getConnectObj: location wasn't found, try 'start', 'end', or name of bind, fk, ik, or control joint.")

    def isIK(self):
        return True
        
    def isFK(self):
        return True
        
    def toDefaultPose(self):
        '''
        Moves the component into the bind position.
        '''
        for anim in self.getAllAnims():            
            resetAttrs(anim)   

    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        switchGroup = self.networkNode.switchGroup.listConnections()[0]
        switchAttr = self.networkNode.switchAttr.get()
        fkikMode = switchGroup.attr(switchAttr).get() < .5#true if fk
        
        pvAnim = self.getPVAnim()
        pvTrans = pvAnim.translate.get()
        ikAnim = self.getIKAnim()
        ikTrans = ikAnim.translate.get()
        ikRot = ikAnim.rotate.get()
        fkAnims = self.getFKAnims()
        fkRots = map(lambda x: x.rotate.get(), fkAnims)
        ikAnimAttrs = {"heelSpin": ikAnim.heelSpin.get(), "heelLift": ikAnim.heelLift.get(), "toeSpin": ikAnim.toeSpin.get(), "ballLift": ikAnim.ballLift.get(), "toeLift": ikAnim.toeLift.get(), "toeWiggle": ikAnim.toeWiggle.get(), "sideToSide": ikAnim.sideToSide.get() }
        if other == self:
            if fkikMode:
                map(lambda x: x.rotate.set(-x.rotate.get()[0],-x.rotate.get()[1],x.rotate.get()[2] ), fkAnims)
            else:    
                pvAnim.translate.set(pvTrans[0], pvTrans[1], -pvTrans[2])
                ikAnim.rotate.set(ikRot[0], ikRot[1], -ikRot[2])
                ikAnim.translate.set(ikTrans[0], ikTrans[1], -ikTrans[2])
                ikAnim.heelSpin.set(-ikAnim.heelSpin.get())
                ikAnim.toeSpin.set(-ikAnim.toeSpin.get())
                ikAnim.sideToSide.set(-ikAnim.sideToSide.get())
                return [self]
        else:
            otherPvAnim = other.getPVAnim()
            otherPvTrans = otherPvAnim.translate.get()
            otherIkAnim = other.getIKAnim()
            otherIkTrans = otherIkAnim.translate.get()
            otherIkRot = otherIkAnim.rotate.get()
            otherFkAnims = other.getFKAnims()
            otherFkRots = map(lambda x: x.rotate.get(), otherFkAnims)
            otherIkAnimAttrs = {"heelSpin": otherIkAnim.heelSpin.get(), "heelLift": otherIkAnim.heelLift.get(), "toeSpin": otherIkAnim.toeSpin.get(), "ballLift": otherIkAnim.ballLift.get(), "toeLift": otherIkAnim.toeLift.get(), "toeWiggle": otherIkAnim.toeWiggle.get(), "sideToSide": otherIkAnim.sideToSide.get() }
            otherSwitchGroup = other.networkNode.switchGroup.listConnections()[0]
            otherSwitchAttr = other.networkNode.switchAttr.get()
            other_fkikMode = otherSwitchGroup.attr(otherSwitchAttr).get() < .5#true if fk        
            if bothSides:
                if not fkikMode and not other_fkikMode: #both IK, do a nicer switch
                    #change this
                    ikAnim.translate.set(-otherIkTrans)
                    ikAnim.rotate.set(otherIkRot)
                    for x in ikAnimAttrs.keys():
                        ikAnim.attr(x).set(otherIkAnimAttrs[x])
                    pvAnim.translate.set(-otherPvTrans)
                    #change other
                    otherIkAnim.translate.set(-ikTrans)
                    otherIkAnim.rotate.set(ikRot)
                    for x in otherIkAnimAttrs.keys():
                        otherIkAnim.attr(x).set(ikAnimAttrs[x])
                    otherPvAnim.translate.set(-pvTrans)
                    return [self, other]
                else:
                    switched = 0
                    if not (other_fkikMode == fkikMode):
                        other.alignSwitch()
                        switched = 1
                        otherPvTrans = otherPvAnim.translate.get()
                        otherIkTrans = otherIkAnim.translate.get()
                        otherIkRot = otherIkAnim.rotate.get()
                        otherFkAnims = other.getFKAnims()
                        otherFkRots = map(lambda x: x.rotate.get(), otherFkAnims)
                        otherIkAnimAttrs = {"heelSpin": otherIkAnim.heelSpin.get(), "heelLift": otherIkAnim.heelLift.get(), "toeSpin": otherIkAnim.toeSpin.get(), "ballLift": otherIkAnim.ballLift.get(), "toeLift": otherIkAnim.toeLift.get(), "toeWiggle": otherIkAnim.toeWiggle.get(), "sideToSide": otherIkAnim.sideToSide.get() }
                    if fkikMode: #swap FKs
                        #change this
                        for num in xrange(len(otherFkAnims)):
                            anim = fkAnims[num]
                            if not anim.rotateX.isLocked():
                                anim.rotateX.set(otherFkRots[num][0])
                            if not anim.rotateY.isLocked():
                                anim.rotateY.set(otherFkRots[num][1])
                            if not anim.rotateZ.isLocked():
                                anim.rotateZ.set(otherFkRots[num][2])
                        #change other
                        for num in xrange(len(fkAnims)):
                            otherAnim = otherFkAnims[num]
                            if not otherAnim.rotateX.isLocked():
                                otherAnim.rotateX.set(fkRots[num][0])
                            if not otherAnim.rotateY.isLocked():
                                otherAnim.rotateY.set(fkRots[num][1])
                            if not otherAnim.rotateZ.isLocked():
                                otherAnim.rotateZ.set(fkRots[num][2])
                    else: #swap IKs
                        #change this
                        ikAnim.translate.set(-otherIkTrans)
                        ikAnim.rotate.set(otherIkRot)
                        for x in ikAnimAttrs.keys():
                            ikAnim.attr(x).set(otherIkAnimAttrs[x])
                        pvAnim.translate.set(-otherPvTrans)
                        #change other
                        otherIkAnim.translate.set(-ikTrans)
                        otherIkAnim.rotate.set(ikRot)
                        for x in otherIkAnimAttrs.keys():
                            otherIkAnim.attr(x).set(ikAnimAttrs[x])
                        otherPvAnim.translate.set(-pvTrans)
                    if switched:
                        other.alignSwitch()
                    return [self, other]                
            else:
                #mirror self
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
                if other_fkikMode:
                    for num in xrange(len(otherFkAnims)):
                            anim = fkAnims[num]
                            if not anim.rotateX.isLocked():
                                anim.rotateX.set(otherFkRots[num][0])
                            if not anim.rotateY.isLocked():
                                anim.rotateY.set(otherFkRots[num][1])
                            if not anim.rotateZ.isLocked():
                                anim.rotateZ.set(otherFkRots[num][2])
                else:
                    try:
                        pvAnim.translate.set(-otherPvTrans)
                    except: pass
                    try:
                        ikAnim.translate.set(-otherIkTrans)
                    except: pass
                    try:
                        ikAnim.rotate.set(otherIkRot)
                    except: pass
                    try:
                        for x in ikAnimAttrs.keys():
                            ikAnim.attr(x).set(otherIkAnimAttrs[x])
                    except: pass
                if not fkikMode == other_fkikMode:
                    self.alignSwitch()
            return [self]
        '''
            
            
class FaceRig(RigComponent):
    def __init__(self, faceGeo, node = ''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FaceRig'):
                    self.networkNode = node
                else:
                    printError("FaceRig: node %s is not a FaceRig metaNode"%(node))
            else:
                printError("FaceRig: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'FaceRig', 1.0, 'rig that contains many NurbsFaceComponent','center', 'face')
            connectToMeta(faceGeo, self.networkNode, 'faceGeo')
            self.networkNode.addAttr('faceComponents',dt = 'string', multi = 1)
        
    def addFaceComponent(self, faceComponent):    
        if not isinstance(faceComponent, NurbsFaceComponent):
            printError('addFaceComponent: %s is not a faceComponent'%faceComponent)
            
        num = self.networkNode.faceComponents.evaluateNumElements()
        connectToMeta(faceComponent.networkNode, self.networkNode, 'faceComponents')
        
    def getFaceComponents(self):
        return listConnections(self.networkNode.faceComponents)
    
    def createFaceComponent(self, locators):
        if not (type(locators) is list or type(locators) is tuple):
            locators = [locators]
        for locator in locators:    
            comp = NurbsFaceComponent(locator, listConnections(self.networkNode.faceGeo)[0])
            self.addFaceComponent(comp)

class SDKComponent(RigComponent):
    def __init__(self, obj, side, bodyPart, copyLimits = 0, node = None):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        obj:
            the object that has the location of the SDKAttr, inherits transform limits
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'SDKComponent'):
                    self.networkNode = node
                else:
                    printError("SDKComponent: node %s is not a SDKComponent metaNode"%(node))
            else:
                printError("SDKComponent: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'SDKComponent', 1.0, 'allows for SDKs on the rig', side, bodyPart, '', obj)
            
            
            #create SDK Anim
            compName = "%s_%s"%(side, bodyPart)
            obj = PyNode(obj)
            sdk_anim = None
            
            #createGrps
            select(cl=1)
            animGrp = group(empty = 1, n = "%s_anim_grp"%compName)
            mainGrp = group(animGrp,n = "%s_component_group"%compName)
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            alignPointOrient(obj, mainGrp, 1,1)
            
            # copy limits
            objLimits = {}
            if copyLimits:
                limits = ["translateMinX", "translateMaxX","translateMinY", "translateMaxY","translateMinZ", "translateMaxZ",
                            "rotateMinX", "rotateMaxX","rotateMinY", "rotateMaxY","rotateMinZ", "rotateMaxZ",
                            "scaleMinX", "scaleMaxX","scaleMinY", "scaleMaxY","scaleMinZ", "scaleMaxZ"]
                for limit in limits:
                    lim = obj.getLimit(limit)
                    enable = obj.isLimited(limit)
                    objLimits[limit] = [enable, lim]
                
            
            #create Anim
            if hasAnimAttr(obj):
                sdk_anim = obj
            if not sdk_anim:
                sdk_anim = joint(n = "%s_sdk_anim"%compName)
                cube = polyCube()[0]
                alignPointOrient(sdk_anim, cube, 1,1)
                swapShape(sdk_anim, cube)
                lockAndHideAttrs(sdk_anim, ['radius'])
                addAnimAttr(sdk_anim)
                alignPointOrient(obj, sdk_anim, 1, 1)
                delete(obj)
                parent(sdk_anim, animGrp)
                createZeroedOutGrp(sdk_anim)
            
            #paste limits
            if copyLimits:
                for key, value in objLimits.items():
                    sdk_anim.setLimited(key, value[0])
                    sdk_anim.setLimit(key, value[1])
            
            #connect to meta
            connectToMeta(animGrp, self.networkNode, 'animGrp')
            connectToMeta(sdk_anim, self.networkNode, 'SDKAnim')
            self.networkNode.addAttr('SDK', dt = 'string', m=1)
    
    def addSDK(self, folder, endPose, sdk_attr, startPose = 'neutral', startValue = 0, endValue = 1, multiply = 0):
        anim = self.networkNode.SDKAnim.listConnections()[0]
        if not anim.hasAttr(sdk_attr):
            anim.addAttr(sdk_attr, at= 'float', k=1,min = startValue, max = endValue, dv = startValue)
        sdkNode = SDK(folder, endPose, anim.name() + "." + sdk_attr, startPose = startPose, startValue = startValue, endValue = endValue, multiply = multiply)
        connectToMeta(sdkNode.networkNode, self.networkNode, 'SDK')
            
    def mirror(self, bothSides = 0):
        pass
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
        
        
    def getConnectObj(self, location):
        return self.networkNode.SDKAnim.listConnections()[0]
    
    def getAllAnims(self):
        return [self.networkNode.SDKAnim.listConnections()[0]]
        
    def toDefaultPose(self):
        metaSDKs = self.networkNode.SDK.listConnections()
        metaSDKs = map(lambda x: fromNetworkToObject(x), metaSDKs)
        for sdk in metaSDKs:
            sdk.toDefaultPose()
        #part added for nebbish production, reset the objects actual attributes
        resetAttrs(self.networkNode.SDKAnim.listConnections()[0])
        
        
    
class SDK(MetaNode):
    def __init__(self, sdkFolder, endPose, sdk_attr, startPose = 'neutral', startValue = 0, endValue = 1,multiply = 0, node = None):
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'SDK'):
                    self.networkNode = node
                else:
                    printError("SDK: node %s is not a SDK metaNode"%(node))
            else:
                printError("SDK: node %s doesn't exist"%(node))
        else:
            MetaNode.__init__( self, "SDK", 1.0, 'stores information about a set driven key')
            self.networkNode.addAttr('SDKGrps', dt = 'string', m=1)
            self.networkNode.addAttr('SDKAdds', dt = 'string', m=1)
            
            sdk_attr = PyNode(sdk_attr)
            node = PyNode(sdk_attr.node())
            sdkAttrName = sdk_attr.name().replace(node.name() + ".", "",1)

            # Check range and extend if needed
            [currentStart,currentEnd] = sdk_attr.getRange()
            if startValue < endValue :
                if startValue < currentStart :
                    currentStart = startValue
                if endValue > currentEnd:
                    currentEnd = endValue
            else : 
                if endValue < currentStart :
                    currentStart = endValue
                if startValue > currentEnd:
                    currentEnd = startValue
            try:
                sdk_attr.setRange(currentStart, currentEnd)
                sdk_attr.set(keyable=1)
            except:
                sdk_attr.set(keyable=1)
                
            
            #read in poses
            startPoseFile = sdkFolder + "/" + startPose + ".xml"
            endPoseFile = sdkFolder + "/" + endPose + ".xml"
            
            pose1 = Pose().readXML(startPoseFile)
            pose2 = Pose().readXML(endPoseFile)
            
            p1Attrs = pose1.getAttributes()
            p2Attrs = pose2.getAttributes()
            
            #make dictionary attribute start and end Values {attr: [startValue, endValue]}
            attrStartEnd = {}
            for attr in p2Attrs:
                if attr in p1Attrs:
                    animStartValue = pose1.getValue(attr)
                    animEndValue =  pose2.getValue(attr)
                    #if animStartValue != animEndValue:
                    attrStartEnd[attr] = [animStartValue, animEndValue]
            
            #make dictionary for amin attriutes {anim, [attr1, attr2, ...]} 
            animAttrs = {}
            for attr in attrStartEnd.keys():
                anim = attr.split(".")[0]
                if objExists(anim):
                    if anim in animAttrs.keys():
                        list = animAttrs[anim]
                        list.append(attr)
                        animAttrs[anim] = list
                    else:
                        animAttrs[anim] = [attr]
            
            for anim, attrs in animAttrs.items():
                anim = PyNode(anim)
                transformAttrs = []
                otherAttrs = []
                #organize by transform and other attributes
                for attr in attrs:
                    attr = PyNode(attr)
                    transattrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
                    if attr.name().split(anim.name() + ".")[-1] in transattrs:
                        transformAttrs.append(attr)
                    else:
                        otherAttrs.append(attr)
                
                if transformAttrs:
                    #create sdk grp 
                    
                    sdk_grp = None
                    if objExists(anim.name() + "_%s_sdk_grp"%sdkAttrName):
                        sdk_grp = PyNode(anim.name() + "_%s_sdk_grp"%sdkAttrName)
                    #create sdk grp
                    else:
                        sdk_grp = group(empty = 1, n = anim.name() + "_%s_sdk_grp"%sdkAttrName)
                        alignPointOrient(anim, sdk_grp, 1, 1)
                        par = anim.getParent()
                        parent(sdk_grp, par)
                        parent(anim, sdk_grp)
                        if not par.name().endswith("_sdk_grp"):
                            zgrp = createZeroedOutGrp(sdk_grp)
                    
                        #if sdk_grp.rotateOrder.get() != anim.rotateOrder.get():
                        #  print 'Matching sdk rotation for '+anim+' anim order '+str(anim.rotateOrder.get())+' sdk order '+str(sdk_grp.rotateOrder.get())
                        #Make sure to match the rotate order or saved poses won't work
                        sdk_grp.rotateOrder.set( anim.rotateOrder.get())
                    
                    # Unlock any translation attributes and remember
                    wasLocked = {}
                    for attrib in ['translate','tx','ty','tz']:
                        if anim.attr(attrib).isLocked():
                            wasLocked[attrib] = True
                            anim.attr(attrib).unlock()
                        else:
                            wasLocked[attrib] = False
                    
                    # Set anim translation to zero so it isn't double
                    # translated now that the zgrp is a parent of it
                    anim.translate.set([0,0,0])
                    
                    # Re-lock the translation attributes
                    for attrib in ['translate','tx','ty','tz']:
                        if wasLocked[attrib]:
                            anim.attr(attrib).lock()

                    #create sdk
                    for attr in transformAttrs:
                        #getValues
                        attrName = attr.name().replace(attr.node().name() + ".", "")
                        sdk_grp_attr = sdk_grp.attr(attrName)
                        currentValue = attr.get()
                        animStartValue = attrStartEnd[attr.name()][0]
                        animEndValue = attrStartEnd[attr.name()][1]
                        
                        
                        hasMultiply = None
                        con = sdk_grp_attr.listConnections(s=1, d=0,scn=1)
                        if con: #if a connection already exists add another key into orig SDK animCurve
                            
                            hasMultiply = con[0].type() == 'multiplyDivide'
                            animCurv = con[0]
                            if hasMultiply:
                                animCurv = con[0].input1X.listConnections(s=1, d=0,scn=1)[0]
                            setKeyframe(animCurv, f=startValue, v = animStartValue, itt='linear', ott='linear')
                            setKeyframe(animCurv, f=endValue, v = animEndValue, itt='linear', ott='linear')
                            connectAttr(sdk_attr, animCurv.input, f=1)
                            
                            
                        else:#if no connection create a new one
                            #startSDK
                            sdk_attr.set(startValue)
                            sdk_grp_attr.set(animStartValue)
                            setDrivenKeyframe(sdk_grp_attr, cd=sdk_attr, itt = 'linear', ott = 'linear', dv = startValue,v=animStartValue, ib=0)
                            
                            #end SDK
                            sdk_attr.set(endValue)
                            sdk_grp_attr.set(animEndValue)
                            setDrivenKeyframe( sdk_grp_attr, cd=sdk_attr, itt = 'linear', ott= 'linear', dv = endValue,v=animEndValue, ib=0)
                            
                            # Set the attribute back to the default value, if it doesn't
                            # have one, assume 0
                            value = addAttr(sdk_attr,q=1, dv=1)
                            if value == None:
                                value = 0
                            sdk_attr.set(value)
                            #sdk_attr.set(addAttr(sdk_attr,q=1, dv=1))
                            #attr.set(currentValue)
                            
                        #connectToMeta
                        connectToMeta(sdk_grp, self.networkNode, 'SDKGrps')
                            
                        if multiply: #add Multiply Node 
                            if not hasMultiply: #add Multiply node if one doesn't already exists
                                animationCurve = sdk_grp_attr.listConnections(s=1, d=0,scn=1)[0]
                                
                                #create amplitude attribute
                                multAttrName = sdk_attr.name().split(".")[-1] + "_multiply"
                                if not objExists(sdk_attr.node().name() + "."+multAttrName):
                                    sdk_attr.node().addAttr(multAttrName, keyable = 1, dv = 1)
                                mult_attr = sdk_attr.node().attr(multAttrName)
                                
                                #create multiplyDivideNode
                                multiNode = createNode('multiplyDivide', n = sdk_grp_attr.name().replace(".", "_") + "amplitude")
                                
                                #connect amplitude Node
                                connectAttr(animationCurve.output, multiNode.input1X, f=1)
                                connectAttr(mult_attr, multiNode.input2X, f=1)
                                connectAttr(multiNode.outputX, sdk_grp_attr, f=1)
                            else: #connect To existing node
                                multiNode = sdk_grp_attr.listConnections(s=1, d=0,scn=1)[0]
                                connectAttr(multiNode.outputX, sdk_grp_attr, f=1)
                                    
                if otherAttrs:
                    for attr in otherAttrs:
                        '''
                        from:
                        animation ---> node.attr ---> otherNode


                        to:
                                        metaAnimation--->|addNode|-->  node.meta_attr_attr ----> otherNode
                        animation --->  node.attr -----/
                        '''

                        attr = PyNode(attr)
                        node = attr.node()

                        #create new attr
                        attrName = attr.name().replace(node.name() + ".", "")
                        newAttrName = "meta_attr_" + attrName
                        node.addAttr(newAttrName, keyable = 0)
                        newAttr= node.attr(newAttrName)

                        #change the output connections
                        outputConnections = attr.outputs(p=1)
                        for out_con in outputConnections:
                            newAttr >> out_con

                        #create add node for multiple input connections
                        addNode = createNode('plusMinusAverage')
                        multiNode = createNode('multiplyDivide')

                        attr >> addNode.input3D[0].input3Dx
                        multiNode.outputX >>  addNode.input3D[1].input3Dx
                        #input1 saved for the meta animation
                        input_attr = multiNode.input1X
                        
                        #create SDK
                        inputStartValue = attrStartEnd[attr.name()][0]
                        inputEndValue = attrStartEnd[attr.name()][1]
                        
                        con = input_attr.listConnections(s=1, d=0)
                        if con: #if a connection already exists add another key into orig SDK animCurve
                            animCurv = con[0]
                            setKeyframe(animCurv, f=startValue, v = inputStartValue, itt='linear', ott='linear')
                            setKeyframe(animCurv, f=startValue, v = inputEndValue, itt='linear', ott='linear')
                            connectAttr(sdk_attr, animCurv.input, f=1)
                        
                        else:
                            #startSDK
                            sdk_attr.set(startValue)
                            input_attr.set(inputStartValue)
                            setDrivenKeyframe(input_attr, cd=sdk_attr, itt = 'linear', ott = 'linear', dv = startValue,v=inputStartValue, ib=0)
                            
                            #end SDK
                            sdk_attr.set(endValue)
                            input_attr.set(inputEndValue)
                            setDrivenKeyframe(input_attr, cd=sdk_attr, itt = 'linear', ott = 'linear', dv = endValue,v=inputEndValue, ib=0)
                            
                            # Set the attribute back to the default value, if it doesn't
                            # have one, assume 0
                            value = addAttr(sdk_attr,q=1, dv=1)
                            if value == None:
                                value = 0
                            sdk_attr.set(value)
                            #sdk_attr.set(addAttr(sdk_attr,q=1, dv=1))
                            
                        #connect the addNode to the newAttr
                        addNode.output3Dx >> newAttr
                        
                        connectToMeta(addNode, self.networkNode, 'SDKAdds')
                        
                        if multiply: #add Multiply Node 
                            if not hasMultiply: #add Multiply node if one doesn't already exists
                                animationCurve = input_attr.listConnections(s=1, d=0)[0]
                                
                                #create amplitude attribute
                                multAttrName = sdk_attr.name().split(".")[-1] + "_multiply"
                                sdk_attr.node().addAttr(multAttrName, keyable = 1, dv = 1)
                                mult_attr = sdk_attr.node().attr(multAttrName)
                                
                                #create multiplyDivideNode
                                multiNode = createNode('multiplyDivide', n = input_attr.name().replace(".", "_") + "amplitude")
                                
                                #connect amplitude Node
                                connectAttr(animationCurve.output, multiNode.input1X, f=1)
                                connectAttr(mult_attr, multiNode.input2X, f=1)
                                connectAttr(multiNode.outputX, input_attr, f=1)
                                
                                
            #connect To MetaNode
            self.networkNode.setAttr('folder', sdkFolder, f=1)
            self.networkNode.setAttr('startPose', startPose, f=1)
            self.networkNode.setAttr('endPose', endPose, f=1)
            self.networkNode.setAttr('startValue', startValue, f=1)
            self.networkNode.setAttr('endValue', endValue, f=1)
            connectToMeta(node, self.networkNode, 'SDKNode')
            self.networkNode.setAttr('SDKAttrName', sdkAttrName, f=1)
    
    def toDefaultPose(self):
        node = self.networkNode.SDKNode.listConnections()[0]
        attrName = self.networkNode.SDKAttrName.get()
        attr = PyNode(node.name() + "." + attrName)
        value = addAttr(node,q=1, dv=1)
        if value == None:
            value = 0
        attr.set(value)
            
            
class EyeAimComponent(RigComponent):
    def __init__(self, leftEyeAnim, rightEyeAnim, direction, distance, side, bodyPart, node = None):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'EyeAimComponent'):
                    self.networkNode = node
                else:
                    printError("EyeAimComponent: node %s is not a EyeAimComponent metaNode"%(node))
            else:
                printError("EyeAimComponent: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'EyeAimComponent', 1.0, 'allows for eye aim on the rig', side, bodyPart, leftEyeAnim, rightEyeAnim)
            #create groups above anims
            direction = direction.upper()
            compName = "%s_%s"%(side, bodyPart)
            leftEyeAnim = PyNode(leftEyeAnim)
            rightEyeAnim = PyNode(rightEyeAnim)
            
            leftEyePar = leftEyeAnim.getParent()
            rightEyePar = rightEyeAnim.getParent()
            
            select(cl=1)
            left_anim_grp = group(n = leftEyeAnim.name() + "_aim_grp")
            parent(left_anim_grp, leftEyePar)
            alignPointOrient(leftEyeAnim, left_anim_grp,0,1)
            rot = left_anim_grp.rotate.get()
            left_anim_grp.rotate.set((0,0,0))
            pos = xform(leftEyeAnim, q=1, piv=1, ws=1)
            xform(left_anim_grp, piv=pos[:3], ws=1)
            left_anim_grp.rotateAxis.set(rot)
            parent(leftEyeAnim, left_anim_grp)
            
            select(cl=1)
            right_anim_grp = group(n = rightEyeAnim.name() + "_aim_grp")
            parent(right_anim_grp, rightEyePar)
            alignPointOrient(rightEyeAnim, right_anim_grp,0,1)
            rot = right_anim_grp.rotate.get()
            right_anim_grp.rotate.set((0,0,0))
            pos = xform(rightEyeAnim, q=1, piv=1, ws=1)
            xform(right_anim_grp, piv=pos[:3], ws=1)
            right_anim_grp.rotateAxis.set(rot)
            parent(rightEyeAnim, right_anim_grp)
            
            #make component groups
            select(cl=1)
            aimGrp = group(empty = 1, n = "%s_aim_grp"%compName)
            mainGrp = group(aimGrp,n = "%s_component_group"%compName)
            
            
            
            #make aim constraints
            direction = direction.upper()
            directionAttr = "translate" + direction
            
                #left aim anim
            select(cl=1)
            left_eye_aim_anim = joint(n = "left_eye_aim_anim")
            parent(left_eye_aim_anim, aimGrp)
            alignPointOrient(leftEyeAnim, left_eye_aim_anim,1,1)
            cube = polyCube()[0]
            alignPointOrient(left_eye_aim_anim, cube, 1,1)
            swapShape(left_eye_aim_anim, cube)
            
            addAnimAttr(left_eye_aim_anim)
            distVect = ( (direction == "X")*-distance,(direction == "Y")*-distance,(direction == "Z")*-distance) #bad assumption, assume left axis is negative for forward direction
            move(left_eye_aim_anim, distVect, os=1, r=1 )
            makeIdentity(left_eye_aim_anim, apply=1, t=1, r=1, s=1, n=1)
            left_eye_aim_anim.jointOrient.set((0,0,0))
            lockAndHideAttrs(left_eye_aim_anim, ['rx','ry','rz','sx','sy','sz','v', 'radius'])
            left_aim_grp = createZeroedOutGrp(left_eye_aim_anim)
            
            
                #right aim anim
            select(cl=1)
            right_eye_aim_anim = joint(n = "right_eye_aim_anim")
            parent(right_eye_aim_anim, aimGrp)
            alignPointOrient(rightEyeAnim, right_eye_aim_anim,1,1)
            cube = polyCube()[0]
            alignPointOrient(right_eye_aim_anim, cube, 1,1)
            swapShape(right_eye_aim_anim, cube)
            addAnimAttr(right_eye_aim_anim)
            distVect = ( (direction == "X")*distance,(direction == "Y")*distance,(direction == "Z")*distance) #bad assumption, assume right axis is positive for forward direction
            move(right_eye_aim_anim, distVect, os=1, r=1 )
            makeIdentity(right_eye_aim_anim, apply=1, t=1, r=1, s=1, n=1)
            right_eye_aim_anim.jointOrient.set((0,0,0))
            lockAndHideAttrs(right_eye_aim_anim, ['rx','ry','rz','sx','sy','sz','v', 'radius'])
            right_aim_grp = createZeroedOutGrp(right_eye_aim_anim)
            
                #both aim anim
            select(cl=1)
            both_eye_aim_anim = joint(n = "both_eye_aim_anim")
            parent(both_eye_aim_anim, aimGrp)
            pc = pointConstraint((left_eye_aim_anim, right_eye_aim_anim), both_eye_aim_anim, mo=0, w=1 )
            delete(pc)
            cube = polyCube()[0]
            alignPointOrient(both_eye_aim_anim, cube, 1,1)
            swapShape(both_eye_aim_anim, cube)
            lockAndHideAttrs(both_eye_aim_anim, ['sx','sy','sz','v', 'radius'])
            addAnimAttr(both_eye_aim_anim)
            createZeroedOutGrp(both_eye_aim_anim)
            parent(left_aim_grp, both_eye_aim_anim)
            parent(right_aim_grp, both_eye_aim_anim)
                
                #create Constraint
            aimVector = ("X"==direction,"Y"==direction, 'Z'== direction)
            
            leftAimConst = aimConstraint(left_eye_aim_anim, left_anim_grp,mo=1,weight=1, aimVector=aimVector ,upVector =(0, 1, 0), worldUpType = "vector", worldUpVector= (0, 1, 0))
            rightAimConst  = aimConstraint(right_eye_aim_anim, right_anim_grp,mo=1,weight=1, aimVector=aimVector ,upVector =(0, 1, 0), worldUpType = "vector", worldUpVector= (0, 1, 0))
            
            #connectToMeta
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            connectToMeta(left_eye_aim_anim, self.networkNode, 'leftAnim')
            connectToMeta(right_eye_aim_anim, self.networkNode, 'rightAnim')
            connectToMeta(both_eye_aim_anim, self.networkNode, 'centerAnim')
            connectToMeta(left_anim_grp, self.networkNode, 'leftGrp')
            connectToMeta(right_anim_grp, self.networkNode, 'rightGrp')
            connectToMeta(aimGrp, self.networkNode, 'aimGrp')
            
    def getConnectObj(self, location):
        return self.networkNode.centerAnim.listConnections()[0]
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
    
    def getAllAnims(self):
        anims = []
        anims.append(self.networkNode.centerAnim.listConnections()[0])
        anims.append(self.networkNode.leftAnim.listConnections()[0])
        anims.append(self.networkNode.rightAnim.listConnections()[0])
        return anims
            
            
class NurbsFaceComponent(RigComponent):
    def __init__(self, locator, facePoly, node = ''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        #test inputs
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'NurbsFaceComponent'):
                    self.networkNode = node
                else:
                    printError("NurbsFaceComponent: node %s is not a NurbsFaceComponent metaNode"%(node))
            else:
                printError("NurbsFaceComponent: node %s doesn't exist"%(node))
        else:
            if objExists(locator):
                locator = PyNode(locator)
                if not locator.getShape().type() == 'locator':
                    printError("NurbsFaceComponent: %s isn't a locator"%locator)
            else:
                printError("NurbsFaceComponent: %s doesn't exist"%locator)
                
            if objExists(facePoly):
                facePoly = PyNode(facePoly)
                if not facePoly.getShape().type() == 'mesh':
                    printError("FaceComponent: %s isn't a polygon"%facePoly)
            else:
                printError("NurbsFaceComponent: %s doesn't exist"%facePoly)
            
            
            #setup
            locName = locator.name()
            side = 'center'
            bodyPart = locName
            compName = '%s_%s'%(side, bodyPart)
            
            vertex = findClosestVertex(locator.getTranslation(space = 'world') ,facePoly)
            nurbs = createNurbsOnVertex(vertex)
            retObjs = createJointsOnNurbs(nurbs)
            wrapObj(nurbs, facePoly)
                
            baseJoint = retObjs[0] 
            tipJoint = retObjs[1]
            baseLoc = retObjs[2]
            control = retObjs[3]
            posInfo = retObjs[4]
            pointGrp = retObjs[5]
            
            baseJoint.rename('face_%s_base_joint'%bodyPart)
            tipJoint.rename('face_%s_tip_joint'%bodyPart)
            baseLoc.rename('face_%s_base_locator'%bodyPart)
            control.rename('face_%s_control_locator'%bodyPart)
            posInfo.rename('face_%s_pos_info'%bodyPart)
            pointGrp.rename('face_%s_translate_group'%bodyPart)
            nurbs.rename('face_%s_nurbs_plane'%bodyPart)
            
            nurbs.hide()
            locator.hide()
            
            #call RIG Component
            RigComponent.__init__(self, 'NurbsFaceComponent', 1.0, 'a joint on burbs component for the face', side, bodyPart, baseJoint, tipJoint)
    
            #organize
            select(cl=1)
            jointGrp = group([baseJoint],n='%s_joint_grp'%compName)
            animGrp = group([baseLoc], n = "%s_anim_grp"%compName)
            dntGrp = group([locator, nurbs, pointGrp], n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_face_component_group"%compName)
                    
            #connect to meta
            connectToMeta(locator, self.networkNode, 'initialLoc')
            connectToMeta(nurbs, self.networkNode, 'nurbs')
            connectToMeta(retObjs[0], self.networkNode, 'nurbsJoint')
            connectToMeta(retObjs[1], self.networkNode, 'bindJoint')
            connectToMeta(retObjs[2], self.networkNode, 'baseLoc')
            connectToMeta(retObjs[3], self.networkNode, 'controlLoc')
            connectToMeta(retObjs[4], self.networkNode, 'pointOnSurface')
            connectToMeta(retObjs[5], self.networkNode, 'TranslateGroup')
            connectToMeta(mainGrp, self.networkNode, 'mainGroup' )



class TwistChainComponent(RigComponent):

    def __init__(   self, side, bodyPart, startAnchor, endAnchor, twistChainStart, twistChainEnd, twistRotationAnchor = 'start', node = '',    ):
        '''
        
        Component that drives a twist chain for more gradual joint twisting.  Works well in places like the
        upper arm and lower arm of bipedal characters.  The x-axis is assumed to be the "twist" axis.  Meant
        to work in conjunction with other rig components.
        
        side:
            The side is this component on: center, left, or right.
            
        bodyPart:
            The body part the component is for: arm, leg, clavicle, foot, etc.
            
        startAnchor:
            The first joint which drives this twist chain (e.g. upperarm_joint)
            
        endAnchor:
            The second joint which drives this twist chain (e.g. lowerarm_joint)
            
        twistChainStart:
            The first joint of this twist chain.  For best results, the twist chain itself should line up
            evenly from the startAnchor to endAnchor, and the twist chain start should have the same parent
            as the start anchor or be parented to the startAnchor.
            
        twistChainEnd:
            Last joint in the twist chain.
            
        twistRotationAnchor:
            Where the end of the anchor derives its twist rotation from: the start anchor or the end anchor.
            Please specify "start" or "end"
            
        '''
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'TwistChainComponent'):
                    self.networkNode = node
                else:
                    printError("TwistChainComponent: node %s is not an ElasticComponent metaNode"%(node))
            else:
                printError("TwistChainComponent: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here


        # Initiate the component
        RigComponent.__init__(  self, 'TwistChainComponent', 1.0, 'Twist chain that gradually rotates a series of joints from a start anchor to end anchor.',
                                side, bodyPart)
        
        compName = '%s_%s'%(side, bodyPart)
        
        startAnchor = PyNode(startAnchor)
        endAnchor = PyNode(endAnchor)
        
        twistChainStart = PyNode(twistChainStart)
        twistChainEnd = PyNode(twistChainEnd)
        twistChain = chainBetween(twistChainStart, twistChainEnd)
        
        
        # Create joint chain that aims towards the anchor without twisting on the x-axis
        anchorDirStart = duplicateChain(startAnchor, startAnchor)[0]
        anchorDirStart.rename(compName+'_notwistAnchorDirection')
        
        anchorDirEnd = duplicateChain(endAnchor, endAnchor)[0]
        anchorDirEnd.rename(compName+'notwistAnchorDirectionEnd')
        
        parent(anchorDirEnd, anchorDirStart)
        
        anchorDirIk = ikHandle(anchorDirStart, anchorDirEnd, solver='ikRPsolver', n=compName+'notwistIk')
        anchorDirIkHandle = anchorDirIk[0]
        anchorDirIkHandle.poleVector.set(0,0,0)
        
        anchorOrientGrp = group(em=1, n=compName+'_anchorOrientGrp')
        delete(parentConstraint(anchorDirStart, anchorOrientGrp, mo=0))
        parent(anchorDirStart, anchorOrientGrp)
        if startAnchor.getParent() != None:
            parentConstraint(startAnchor.getParent(), anchorOrientGrp, mo=1)
        else:
            pointConstraint(startAnchor, anchorOrientGrp, mo=0)
        
        pointConstraint(endAnchor, anchorDirIkHandle, mo=0)
        
        
        # Create joint positioned on the end anchor, but which
        # derives its orientation from the start anchor
        twistJnt = duplicateChain(startAnchor, startAnchor)[0]
        twistJnt.rotateOrder.set(0)
        
        twistJnt.rename(compName+'_twistEndJnt') # Force x to get applied correctly
        
        pointConstraint(endAnchor, twistJnt, mo=0)
        
        if twistRotationAnchor == 'start':
            orientConstraint(startAnchor, twistJnt, mo=1)
        elif twistRotationAnchor == 'end':
            orientConstraint(endAnchor, twistJnt, mo=1)
        else:
            printError('TwistChainComponent: Please specify "start" or "end" for twistRotationAnchor.')
        
        
        # Create nurbs plane corresponding to the twist chain then attach it to the
        # notwist anchor direction and the twist joint position over the end anchor
        # via clusters (more predictable than skinning)
        leftCurve = createCurveThroughObjects([anchorDirStart, anchorDirEnd], offset=(0,0,-4))
        rightCurve = createCurveThroughObjects([anchorDirStart, anchorDirEnd], offset=(0,0,4))
        
        twistPlane = PyNode(loft(leftCurve, rightCurve, ch=0, ss=1, d=3, ar=1, c=0, rn=0, po=0, rsn=0, n=compName+'_twistSurface')[0]).getShape()
        delete(rightCurve)
        delete(leftCurve)
        
        startCluster = cluster(twistPlane.cv[:][0], n=compName+'_startCluster')[1]
        endCluster = cluster(twistPlane.cv[:][1], n=compName+'_endCluster')[1]
        
        parentConstraint(anchorDirStart, startCluster)
        parentConstraint(twistJnt, endCluster)
        
        ncTransforms = []
        
        
        # Create anchors along the twist plane for each twist joint to attach to
        for i in xrange(len(twistChain)):
            tj = twistChain[i]
            v = i*1.0/(len(twistChain)-1)
            nurbsGrp = group(em=1, n=str(PyNode(tj))+'_nurbsAnchor')
            ncTransforms.append(nurbsConstraint(twistPlane, nurbsGrp, .5, v)[1])
            ncTransforms.append(nurbsGrp)
            parentConstraint(nurbsGrp, tj, mo=1)
        
            
        # Organize
        mainGrp = group(em=1, n=compName+'_component_group')
        
        dntGrp = group(em=1, n=compName+'_DO_NOT_TOUCH')
        dntGrp.inheritsTransform.set(0)
        hide(dntGrp)
        
        parent(dntGrp, mainGrp)
        
        parent(twistPlane.getParent(), ncTransforms, anchorDirIkHandle, anchorOrientGrp, twistJnt, startCluster, endCluster, dntGrp)
                
        # Connect the mess of Maya nodes that we've created and organized into the meta system
        connectChainToMeta(twistChain, self.networkNode, 'twistJoints')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp') # Required otherwise '.parentUnder' not implemented Exception thrown

        
        
    def getAllAnims(self):
        '''
        Returns a list of all the anims.
        '''
        return []
        
    def connectToComponent(self):
        raise Exception("TwistChainComponent.connectToComponent: Cannot change component attachment.")
        
        
    def getConnectObj(self, location):
        '''
        Gets the component to connect to at location.
        
        location:
            The location to connect to.
        return:
            The obj which others can connect to.
        '''
        if location == 'start':
            return self.networkNode.twistJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.twistJoints.listConnections()[-1]
        raise Exception("TwistChainComponent.getConnectObj: location wasn't found, needs 'start' or 'end'.")
        
        
    def toDefaultPose(self):
        '''
        Moves the component's anims back to the bind position.
        '''
        pass
        

class ElasticComponent(RigComponent):

    def __init__(   self, side, bodyPart, startJoint, endJoint, # Required
                    startAnchor=None, endAnchor=None, worldUpAxis=(0,1,0), numControls = 2, # Optional
                    createStartAnim = False, createEndAnim = False, # Optional
                    node = ''   ):
        '''
        side:
            The side is this component on: center, left, or right.
        bodyPart:
            The body part the component is for: arm, leg, clavicle, foot, etc.
        startJoint:
            The joint where the component starts.
        endJoint:
            The joint where the component ends.
        '''
        
        # TODO: World up object for permanent aim constraints should be determined by connectToComponent
        # TODO: x aim should be consistent from side to side (current solution is hacky)
        # TODO: Squash/stretch via z and y scaling
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'ElasticComponent'):
                    self.networkNode = node
                else:
                    printError("ElasticComponent: node %s is not an ElasticComponent metaNode"%(node))
            else:
                printError("ElasticComponent: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here

        # Initiate the component
        RigComponent.__init__(self, 'ElasticComponent', 1.0, 'Elastic chain with approximately evenly spaced joints.', side, bodyPart, startJoint, endJoint)
        
        compName = '%s_%s'%(side, bodyPart)
        
        LOCAL_UP_DIR = (0,1,0)
        WORLD_UP_DIR = worldUpAxis

        # Bind joint chain
        bindJoints = filter(lambda i: PyNode(i).type() == 'joint', chainBetween(startJoint, endJoint))

        # Cluster start locations match bind joints if the numbers match up
        if (numControls == len(bindJoints)-2):
            startLocs = bindJoints
        else:
            startLocs = []
        
        # Locator influence system
        sc = mu.stretchyLocatorCurve(startJoint, endJoint, numCtrls=numControls, numLocs=len(bindJoints), clusterStartLocations=startLocs)
        locRoot = sc[0]
        clusters = sc[1]
        locators = sc[2]

        # Connect the bind joints to the locator system
        jointScaleStretcher = group(em=1, n="jointScaleStretcher")
        measurerParents = []
        
        for i in xrange(len(bindJoints)-1):
            j = PyNode(bindJoints[i])
            nextj = PyNode(bindJoints[i+1])
            
            loc = PyNode(locators[i])
            nextloc = PyNode(locators[i+1])
            
            dirToNextJnt = mu.getLocalDir(j, nextj)
            
            # Set up a hierarchy that allows for distance to be measured
            # via the translateX of the transform and plugged into the scaleX
            # of the corresponding joint
            
            # Set up node
            measurerParent = group(em=1, n="measurerParent")
            measurerParents.append(measurerParent)
            delete(parentConstraint(j, measurerParent, mo=0))
            measurer = group(em=1, n="measurer")
            delete(parentConstraint(measurerParent, measurer, mo=0))
            parent(measurer, measurerParent)
            ac = aimConstraint(measurerParent, measurer, mo=0, u=(0,1,0), wu=(0,1,0), aim=(1,0,0))
            
            # Set the measurer's translateX such that '1' is where the next joint is
            delete(pointConstraint(nextj, measurer, mo=0))
            parentScale = measurer.translateX.get()
            measurer.translateX.set(1)
            measurerParent.scale.set(parentScale, parentScale, parentScale)
            measurerParent.scale.lock()
            delete(ac)
            
            # Connect the first locator directly to the first bind joint
            if (i == 0):
                pointConstraint(loc, j, mo=0)
                
            # Hook measurement system up for this joint up to the corresponding locators
            locPc = pointConstraint(loc, measurerParent, mo=0)
            if (startAnchor != None):
                locAc = aimConstraint(nextloc, measurerParent, mo=0, u=LOCAL_UP_DIR, wu=WORLD_UP_DIR, wut="objectrotation", wuo=startAnchor, aim=dirToNextJnt)
            else:
                locAc = aimConstraint(nextloc, measurerParent, mo=0, u=LOCAL_UP_DIR, wu=WORLD_UP_DIR, aim=dirToNextJnt)
            measurePc = pointConstraint(nextloc, measurer, mo=0)
            
            # Hook bind joint up to measurement system
            orientConstraint(measurerParent, j, mo=0)
            measurer.translateX >> j.scaleX
            
            # Organize
            parent(measurerParent, jointScaleStretcher)
    
        # Special case: If we have an end anim we'll need a measurerParent to orient it
        measurerParents.append(measurerParents[-1])
        
        # Create anims for the clusters sans the start and end
        zeroGrps =[]
        anims = []
        animNum = 0
        
        startAnimRange = 1
        if (createStartAnim): startAnimRange = 0
        
        endAnimRange = len(clusters)-1
        if (createEndAnim): endAnimRange = len(clusters)
        
        for i in xrange(startAnimRange, endAnimRange):
            clstr = clusters[i]
            select(clear=1)
            anim = joint(n = '%s_anim_%i'%(compName,animNum+1))
            alignPointOrient(clstr, anim, 1,0)
            alignPointOrient(measurerParents[i], anim, 0,1)
            zeroGrp = createZeroedOutGrp(anim)
            zeroGrps.append(zeroGrp)
            
            # NOTE: Quick fix for control x-axis
            if (side == "right"): zeroGrp.scaleX.set(-1)
            
            # Skip making anims for cluster handles not in the anim range
            if (i < startAnimRange or i >= endAnimRange): continue
            
            addAnimAttr(anim)
            sph = polySphere()[0]
            appendShape(sph, anim)
            delete(sph)
            lockAndHideAttrs(anim, [ 'v', 'radius', 'sx', 'rx', 'ry', 'rz', 'sy', 'sz' ])
            anims.append(anim)
            
            
            pointConstraint(anim, clstr, mo=0) # Attach anim to cluster
            
            animNum += 1
        
        # Organize
        animGrp = group([zeroGrps], n = "%s_anim_grp"%compName)
        
        dntGrp = group([locRoot, jointScaleStretcher], n = "%s_DO_NOT_TOUCH_grp"%compName)
        dntGrp.visibility.set(0)
        
        mainGrp = group([animGrp, dntGrp],n = "%s_component_group"%compName)
        
        # Create system to stretch out anim zero groups with joint
        if (startAnchor != None and endAnchor != None):
            slt = mu.stretchyLocatorTransforms(startAnchor, endAnchor, zeroGrps, 1)
            hide(slt[0])
            parent(slt[0], mainGrp)
        
        # Connect the mess of Maya nodes that we've created and organized into the meta system
        connectChainToMeta(bindJoints, self.networkNode, 'bindJoints')
        connectChainToMeta(clusters, self.networkNode, 'controlClusters')
        connectChainToMeta(anims, self.networkNode, 'anims')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp') # Required otherwise '.parentUnder' not implemented Exception thrown

    def getAllAnims(self):
        '''
        Returns a list of all the anims.
        '''
        return self.networkNode.anims.listConnections()
        
    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        Connects this component to another component.
        comp:
            The component to attach to.
        location:
            The place where the components connect, ex, start, end, jointName.
        point:
            Attach by translation.
        orient:
            Attach by orientation.
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans, w=1, mo=1)
        
    def getConnectObj(self, location):
        '''
        Gets the component to connect to at location.
        
        location:
            The location to connect to.
        return:
            The obj which others can connect to.
        '''
        if location == 'start':
            return self.networkNode.controlClusters.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlClusters.listConnections()[-1]
        raise Exception("ElasticComponent.getConnectObj: location wasn't found, needs 'start' or 'end'.")
        
    def toDefaultPose(self):
        '''
        Moves the component's anims back to the bind position.
        '''
        for anim in self.networkNode.anims.listConnections():
            anim.translate.set(0,0,0)
            
    def connectEndToComponent(self, comp, location):
        '''
        Hook the end of this component to the start of another.
        '''
        
        myObj = self.getConnectObj("end")
        compObj = comp.getConnectObj(location)
        parentConstraint(compObj, myObj, mo=1)

        
class FeatherComponent(RigComponent):

    def __init__(   self, side, bodyPart, startJoint, endJoint, # Required
                    worldUpObj=None, worldUpAxis=(0,1,0), numControls = 2, createStartAnim = False, createEndAnim = False, # Optional
                    node = '', wingCurve=None, featherLayers = [], featherLayerParentIndices = {}, featherLayerBendFactors = {},
                    lastCurvePointIsDoubled = True, curveCVBindJointIndices = None, createBendContols = True):
        '''
        side:
            The side is this component on: center, left, or right.
        bodyPart:
            The body part the component is for: arm, leg, clavicle, foot, etc.
        startJoint:
            The joint where the component starts.
        endJoint:
            The joint where the component ends.
        '''
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FeatherComponent'):
                    self.networkNode = node
                else:
                    printError("FeatherComponent: node %s is not an FeatherComponent metaNode"%(node))
            else:
                printError("FeatherComponent: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here

        # Initiate the component
        RigComponent.__init__(self, 'FeatherComponent', 1.0, 'Automatic feather spread and high level feather controls.', side, bodyPart, startJoint, endJoint)
        
        compName = '%s_%s'%(side, bodyPart)
        
        LOCAL_UP_DIR = (0,1,0)
        WORLD_UP_DIR = worldUpAxis

        wingCurveShape = PyNode(wingCurve).getShapes()[0]
        # Bind joint chain
        bindJoints = filter(lambda i: PyNode(i).type() == 'joint', chainBetween(startJoint, endJoint))

        # Create cluster deformers along the wing curve
        curveClusters = []
        curveClusterGroups = []
        anims = []
        zeroGrps = []
        for i in range(len(wingCurveShape.cv)):
            select(clear=True)
            select(wingCurveShape.cv[i])
            clu = cluster()
            clu[1].rename('%s_wing_curve_control_point_%d'%(side, i+1))
            curveClusters.append(clu[1])
            clu[1].hide()

        curveAnims = []
        # Create wing curve anims
        for i in range(len(curveClusters)):
            if lastCurvePointIsDoubled and i == len(curveClusters) - 1:
                continue

            select(clear=1)
            anim = joint(n = '%s_curve_anim_%i'%(compName,i+1))
            alignPointOrient(curveClusters[i], anim, 1,0)
            zeroGrp = createZeroedOutGrp(anim)
            
            addAnimAttr(anim)
            sph = polySphere()[0]
            appendShape(sph, anim)
            delete(sph)
            lockAndHideAttrs(anim, [ 'v', 'radius', 'sx', 'rx', 'ry', 'rz', 'sy', 'sz' ])
            anims.append(anim)
            zeroGrps.append(zeroGrp)
            
            if curveCVBindJointIndices is not None:
                parentConstraint(bindJoints[curveCVBindJointIndices[i]], zeroGrp, maintainOffset = True )
            else:
                parentConstraint(bindJoints[i], zeroGrp, maintainOffset = True )

            curveAnims.append(anim)
            
            pointConstraint(anim, curveClusters[i], mo=0) # Attach anim to cluster
            # The two last clusters are at the same place (adds more resolution to the curve shape)
            if lastCurvePointIsDoubled and i == len(curveClusters) - 2:
                pointConstraint(anim, curveClusters[i+1], mo=0) # Attach anim to cluster

        bendAnims = []
        if createBendContols:
            for i in range(len(bindJoints)):

                select(clear=1)
                dir = 1 if side != 'right' else -1
                anim = joint(bindJoints[i], n = '%s_feather_bend_anim_%i_a'%(compName,i+1), relative=True, p = (0, dir * 5, dir * -3))
                select(curveAnims[i], anim)
                a = aimConstraint(aimVector = (0,0,-1))
                delete(a)
                animGroup = createZeroedOutGrp(anim)
                
                addAnimAttr(anim)
                cube = polyCube(h = 0.15, w = 0.7, d = 2)[0]
                for v in cube.getShape().vtx:
                    moveVertexAlongDirection(v, d = (0,0,-1), m = 1)

                appendShape(cube, anim)
                delete(cube)
                lockAndHideAttrs(anim, [ 'v', 'radius', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz' ])
                anims.append(anim)
                zeroGrps.append(animGroup)
                
                parentConstraint(bindJoints[i], animGroup, maintainOffset = True )


                anim2 = joint(anim, n = '%s_feather_bend_anim_%i_b'%(compName,i+1), relative=True, p = (0, 0, -2))
                anim2Group = createZeroedOutGrp(anim2)
                addAnimAttr(anim2)
                cube2 = polyCube(h = 0.15, w = 0.7, d = 2)[0]
                for v in cube2.getShape().vtx:
                    moveVertexAlongDirection(v, d = (0,0,-1), m = 1)
                appendShape(cube2, anim2)
                delete(cube2)
                lockAndHideAttrs(anim2, [ 'v', 'radius', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz' ])
                anims.append(anim2)
                zeroGrps.append(anim2Group)

                parentConstraint(anim, anim2Group, maintainOffset = True )
                bendAnims.append([anim, anim2])
        
        multdivNodes = []
        addNodes = []
        curveClusterGroup = group(curveClusters, n = '%s_wing_curve_control_points'%(side))
        zeroGroupGroup = group(zeroGrps, n = '%s_feather_component_zero_groups'%(side))
        # Setup feather constraints

        featherLocatorGroups = []
        for featherLayerIndex in range(len(featherLayers)):
            featherLayer = featherLayers[featherLayerIndex]
            feathers = listRelatives(featherLayer)
            parentIndices = featherLayerParentIndices[featherLayer]
            currentParentIndex = 0
            featherLocators = []

            layerBendFactor = featherLayerBendFactors[featherLayer]

            for i in range(len(feathers)):
                if i >= parentIndices[currentParentIndex + 1]:
                    currentParentIndex += 1

                featherParentStartIndex = parentIndices[currentParentIndex]
                featherParentEndIndex = parentIndices[currentParentIndex + 1]

                feather = feathers[i]
                f = float(i) / (len(feathers) - 1)
                locatorName = side + "_" + feather + '_locator'
                locator = spaceLocator(n=locatorName)
                select(clear=True)
                select(wingCurve, locator)
                motionPath = PyNode(pathAnimation(fractionMode = True))
                motionPath.disconnectAttr('uValue')
                motionPath.setAttr('uValue', f)

                

                jointStartZ = feather.getPivots()[0].z

                jointEndZ = 999999.0
                for v in feather.getShape().vtx:
                    p = v.getPosition(space='object')
                    if p.z < jointEndZ:
                        jointEndZ = p.z

                joints = []
                nJoints = 4
                for i2 in range(nJoints):
                    jf = i2 / float(nJoints - 1)
                    jointType = 'bind' if  i2 < nJoints - 1 else 'end'
                    jointName = ("%s_%s_joint") % (feather.name(), jointType)
                    j = joint(feather, p = (0, 0, (1 - jf) * jointStartZ + jf * jointEndZ), relative=True, n = jointName)
                    j.hide()
                    if len(joints) > 0:
                        parent(j, joints[-1])

                    joints.append(j)

                parent(joints[0], featherLayer)
                
                zg2 = createZeroedOutGrp(joints[0])
                zg = createZeroedOutGrp(zg2)
                inheritTransform(zg, off=True, preserve=True )
                inheritTransform(feather, off=True, preserve=True)

                skinCluster(joints[0:-1], feather)

                select(clear=True)
                select(locator, zg)
                aimConstraint(maintainOffset = True)

                parentJointMix = (float(i) - featherParentStartIndex) / (featherParentEndIndex - featherParentStartIndex)

                orientConstraint( bindJoints[currentParentIndex], zg2, w = 1 - parentJointMix, maintainOffset = True, skip = ['x', 'y'])
                orientConstraint( bindJoints[currentParentIndex + 1], zg2, w = parentJointMix, maintainOffset = True, skip = ['x', 'y'])

                if createBendContols:

                    def connectWeightedRotate(source1, source2, target, source1Weight, source2Weight):
                        multdiv1 = PyNode(cmds.shadingNode('multiplyDivide', asUtility=True, name='multiplyDivideTest'))
                        connectAttr(source1.rotate, multdiv1.input1)
                        multdiv1.input2.set(source1Weight, source1Weight, source1Weight)

                        multdiv2 = PyNode(cmds.shadingNode('multiplyDivide', asUtility=True, name='multiplyDivideTest'))
                        connectAttr(source2.rotate, multdiv2.input1)
                        multdiv2.input2.set(source2Weight, source2Weight, source2Weight)

                        addNode = PyNode(cmds.shadingNode('plusMinusAverage', asUtility=True, name='pusMinusAverageTest'))
                        addNode.setAttr('operation', 1)
                        connectAttr(multdiv1.output, addNode.input3D[0])
                        connectAttr(multdiv2.output, addNode.input3D[1])

                        connectAttr(addNode.output3D, target.rotate)
                        multdivNodes.append(multdiv1)
                        multdivNodes.append(multdiv2)
                        addNodes.append(addNode)
                        # TODO: Group and store multdivNodes in component group (is it possible to group utility nodes?)

                    bendSource1Weight = layerBendFactor * (1 - parentJointMix)
                    bendSource2Weight = layerBendFactor * parentJointMix
                    connectWeightedRotate(bendAnims[currentParentIndex][0], bendAnims[currentParentIndex+1][0], joints[1], bendSource1Weight, bendSource2Weight)
                    connectWeightedRotate(bendAnims[currentParentIndex][1], bendAnims[currentParentIndex+1][1], joints[2], bendSource1Weight, bendSource2Weight)

                #orientConstraint( bendAnims[currentParentIndex][0], joints[1], w = 1 - parentJointMix, maintainOffset = True)
                #orientConstraint( bendAnims[currentParentIndex+1][0], joints[1], w = parentJointMix, maintainOffset = True)
                #orientConstraint( bendAnims[currentParentIndex][1], joints[2], w = 1 - parentJointMix, maintainOffset = True)
                #orientConstraint( bendAnims[currentParentIndex+1][1], joints[2], w = parentJointMix, maintainOffset = True)

                parentConstraint(bindJoints[currentParentIndex], zg, maintainOffset = True, sr = ['x', 'y', 'z'])

                featherLocators.append(locator)
                zeroGrps.append(zg)
                
                inheritTransform(locator, off=True)
                locator.hide()

            featherLocatorGroups.append(group(featherLocators, name = side + "_" + featherLayer + '_locators'))

        featherGroup = group(featherLayers, n= "%s_all_feathers"%side)
        featherLocatorsGroup = group(featherLocatorGroups, n = "%s_feather_locators"%side)

        mainGrp = group([featherGroup, featherLocatorsGroup, curveClusterGroup, zeroGroupGroup, wingCurve] , n = "%s_component_group"%compName)

        # Connect the Maya nodes that we've created and organize into the meta system
        connectChainToMeta(bindJoints, self.networkNode, 'bindJoints')
        connectChainToMeta(curveClusters, self.networkNode, 'curveClusters')
        connectChainToMeta(anims, self.networkNode, 'anims')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp') # Required otherwise '.parentUnder' not implemented Exception thrown

    def getAllAnims(self):
        '''
        Returns a list of all the anims.
        '''
        return self.networkNode.anims.listConnections()

    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        Connects this component to another component.
        comp:
            The component to attach to.
        location:
            The place where the components connect, ex, start, end, jointName.
        point:
            Attach by translation.
        orient:
            Attach by orientation.
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        #parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans, w=1, mo=1)
        
    def getConnectObj(self, location):
        '''
        Gets the component to connect to at location.
        
        location:
            The location to connect to.
        return:
            The obj which others can connect to.
        '''
        if location == 'start':
            return self.networkNode.bindJoints[0]
        elif location == 'end':
            return self.networkNode.bindJoints[-1]
        raise Exception("FeatherComponent.getConnectObj: location wasn't found, needs 'start' or 'end'.")
        
    def toDefaultPose(self):
        '''
        Moves the component's anims back to the bind position.
        '''
        anims = self.getAllAnims()
        for anim in anims:
            if anim.translate.get(settable = True):
                anim.translate.set([0,0,0])

            if anim.rotate.get(settable = True):
                anim.rotate.set([0,0,0])


    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            pass
        else:
            thisAnims = self.getAllAnims()
            otherAnims = other.getAllAnims()

            print self
            print other
            if bothSides: #copy over from other side, then copy this side to that side
                for x in xrange(len(otherAnims)):
                    #get
                    otherAnim = otherAnims[x]
                    otherTrans = otherAnim.translate.get()
                    otherRotate = otherAnim.rotate.get()
                    thisAnim = thisAnims[x]
                    thisTrans = thisAnim.translate.get()
                    thisRotate = thisAnim.rotate.get()
                    
                    #set
                    if thisAnim.translate.get(settable = True):
                        thisAnim.translate.set(-otherTrans[0], otherTrans[1], otherTrans[2])
                        otherAnim.translate.set(-thisTrans[0], thisTrans[1], thisTrans[2])

                    if thisAnim.rotate.get(settable = True):
                        thisAnim.rotate.set(otherRotate[0], otherRotate[1], otherRotate[2])
                        otherAnim.rotate.set(thisRotate[0], thisRotate[1], thisRotate[2])
                return [self, other]
            else:# just copy over from other side
                for x in xrange(len(otherAnims)):
                    otherTrans = otherAnims[x].translate.get()
                    otherRotate = otherAnims[x].rotate.get()
                    thisAnim = thisAnims[x]

                    if thisAnim.translate.get(settable = True):
                        thisAnim.translate.set(-otherTrans[0], otherTrans[1], otherTrans[2])

                    if thisAnim.rotate.get(settable = True):
                        thisAnim.rotate.set(otherRotate[0], otherRotate[1], otherRotate[2])
                return [self]
    
                
class MultiDigitController(RigComponent): 
    '''
    A single component to control a set of fingers or toes.  The default
    values are revolved around making a standard five finger
    '''
    
    def __init__(self, side, bodyPart, rootJnt, digits,
                       digitNames = ['thumb', 'index', 'middle', 'ring', 'pinky'],
                       firstDigitIsThumb = True, indexOfPeakDigit = 2, digitRadius = 1, scrunchRotate = -70,
                       upAxis = 'y', rotateAxis = 'z', lengthAxis = '-x', rootJntUpAxis='z', bonusAttrs=False,
                       node = None):
        '''
        rootJnt:
            Parent joint of all the digit chains.

        digits:
            Chains of joints each represented a three boned digit with an end joint.
            Chains should be provided in tuples of the start and end joints.  For example:
            [   ('right_thumb_1_bind_joint', 'right_thumb_end_joint'),
                ('right_index_1_bind_joint', 'right_index_end_joint')   ]

        digitNames:
            List of names to give the provided digit chains from the start of the list to the end.
            The number of names MUST correspond to the number of digits given.  The default corresponds
            to the four non-thumb digits.

        firstDigitIsThumb:
            If true, treat the creation of the first digit chain as a thumb.  This creates
            a slightly different set of attributes on it.
            
        indexOfPeakDigit:
            When automatically making SDKs for relaxing knuckles, the index of this digit (in digits)
            will have the highest values.  It will also stay static on spread.  Index 1, usually the middle
            digit, is the default.
            
        digitRadius:
            Radius of the digit at the base.  Used for automatically determining spread distance.

        scrunchRotate:
            Rotation of the root finger for scrunching.
            
        upAxis:
            Axis that represents up on the digit, going up through the back of the hand.  Default is 'y'.

        rotateAxis:
            Axis used for major digit rotations.
            
        lengthAxis:
            Axis pointing down the length of the finger.

        rootJntUpAxis:
            The up direction of the root joint, which the upAxis of the digits will align with.
            
        bonusAttrs:
            Add a few more control options to the hand, but may be too much node-wise to justify
            adding to the rig unless absolutely necessary.
        '''
        
        # REQUISITE META SETUP
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'MultiDigitController'):
                    self.networkNode = node
                else:
                    printError("MultiDigitController: node %s is not a MultiDigitController metaNode"%(node))
            else:
                printError("MultiDigitController: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        # Initiate the component
        RigComponent.__init__(self, 'MultiDigitController', 1.0, 'Mass finger/toe control component', side, bodyPart)
        compName = '%s_%s'%(side, bodyPart)
        
        
        # START COMPONENT SETUP
        
        rootJnt = PyNode(rootJnt)
        anims = []
        mainGrp = group(em=1, n=compName+'_component_group')
        xform(mainGrp, piv=mu.getWorldPositionVector(rootJnt))
        
        # Extract chains from the start/end joints of the digits.
        digits = map(lambda ends: chainBetween(ends[0], ends[1]), digits)
        
        # Argument error checking
        if len(digits) != len(digitNames):
            raise Exception('Digits: Please provide the same number of digit labels as there are digits.')

        # Determine a common transform that the digits can be 'flattened' to
        commonTransform = spaceLocator(n='commonDigitBase')

        if firstDigitIsThumb:
            baseJnts = digits[1:]
        else:
            baseJnts = digits
        allBaseDigitJnts = map(lambda obj: PyNode(obj[0]), baseJnts)
        pc = pointConstraint(allBaseDigitJnts, commonTransform, mo=0)
        ac = aimConstraint(rootJnt, commonTransform,
                           aim=-mu.axisVector(lengthAxis), u=mu.axisVector(upAxis), wu=mu.axisVector(rootJntUpAxis),
                           wut='objectrotation', wuo=rootJnt)
        delete(ac, pc)
        
        # Useful information for later
        numDigits = len(digits)

        # Depending on which digit index is input, a magnitude is output depending on how far it is from the digit peak
        peakFunc = lambda x: ((-(x-indexOfPeakDigit)**2)/float(numDigits))+1

        # Create mass digit controller
        select(cl=1)
        allDigitAnim = joint(n=compName+'all_anim')
        addAnimAttr(allDigitAnim) ###
        anims.append(allDigitAnim)
        select(cl=1)
        allDigitAnim.drawStyle.set(2)
        delete(parentConstraint(rootJnt, allDigitAnim, mo=0))
        makeIdentity(allDigitAnim, t=0, r=1, s=0, jo=0, a=1)
        animShape = circle(normal=(0,0,1), center=(0,0,3*digitRadius), r=digitRadius, ch=0)[0]
        parent(animShape.getShape(), allDigitAnim, s=1, add=1)
        delete(animShape)
        parent(allDigitAnim, mainGrp)
        lockAndHideAttrs(allDigitAnim, ['t','r','s','radius','v'])

        # Create mass digit attributes (to be hooked up on single digit creation)
        allDigitAnim.addAttr('fkAnimVis', k=1, at='bool', dv=0)
        allDigitAnim.addAttr('spread', k=1, min=-10, max=10, dv=0)
        allDigitAnim.addAttr('flattenKnuckles', k=1, min=-10, max=10, dv=0)

        # Handle each digit individually
        waveJnts = [] # For optional bonus attribute
        digitIndex = 0
        for digitChain in digits:

            digitName = digitNames[digitIndex]
            digitChain = map(lambda name: PyNode(name), digitChain)
            isNormalDigit = not ((digitIndex == 0) and firstDigitIsThumb)
            
            # Create copy of digit chain to drive controls
            digitCopy = duplicateChain(digitChain[0], digitChain[-1]) # Main digit segments
            for i in xrange(len(digitCopy)):
                digitCopy[i].rename(digitName+'_'+str(i)+'_ctrlJnt')
                digitCopy[i].drawStyle.set(2)
                
            digitLength = mu.getChainLength(digitCopy[0], digitCopy[-1])
            baseJnt   = digitCopy[0]
            middleJnt = digitCopy[1]
            tipJnt    = digitCopy[2]
            endJnt    = digitCopy[3]
            if isNormalDigit: waveJnts.append(baseJnt)
            
            # Straighten the chain
            digitLength = mu.getChainLength(digitCopy[0], digitCopy[-1])
            
            digitDirTrans = group(em=1, n='tempDigitDir')
            delete(pointConstraint(baseJnt, digitDirTrans, mo=0))
            delete(aimConstraint(middleJnt, digitDirTrans, mo=0, aim=(1,0,0)))
            digitEndMarker = spaceLocator(n='tempDigitEnd')
            parent(digitEndMarker, digitDirTrans)
            
            digitTempIK = ikHandle(sj=baseJnt, ee=endJnt)[0] # IK chain used to straighten and sample rotations
            pc = pointConstraint(digitEndMarker, digitTempIK, mo=0)
            
            digitEndMarker.translate.set(digitLength, 0, 0) 
            refresh()
            
            delete(pc, digitTempIK, digitDirTrans)
            
            # Orient the base with the common digit transform
            if isNormalDigit:
                delete(orientConstraint(commonTransform, baseJnt, mo=0))
            
            makeIdentity(baseJnt, t=0, r=1, s=0, jo=0, a=1)
            
            # Align the base of the digit's translate with the common digit transform
            if isNormalDigit:
                digitCopyGrp = group(em=1, n='tempDigitAligner')
                delete(parentConstraint(baseJnt, digitCopyGrp, mo=0))
                parent(baseJnt, digitCopyGrp)
                delete(pointConstraint(commonTransform, baseJnt, mo=0, sk=mu.getSkipAxes(upAxis)))
                parent(baseJnt, w=1)
                delete(digitCopyGrp)
            
            # Create a zero grp for the digit
            digitZeroGrp = group(em=1, n=digitName+'_zeroGrp')
            delete(parentConstraint(baseJnt, digitZeroGrp, mo=0))
            parent(digitCopy[0], digitZeroGrp)
            
            # Create manual FK anims
            fkAnims = []
            for i in xrange(len(digitCopy)-1):
                select(cl=1)
                srcDigit = digitCopy[i]
                srcDigitNext = digitCopy[i+1]
                fkAnim = joint(n=compName+'_'+digitName+'_fk_'+str(i+1)+'_anim')
                fkAnim.drawStyle.set(2)
                fkAnims.append(fkAnim)
                fkAnimShape = circle(normal=mu.axisVector(lengthAxis), radius=1.25*digitRadius, ch=0)[0]
                appendShape(fkAnimShape, fkAnim)
                delete(fkAnimShape)
                addAnimAttr(fkAnim)
                delete(parentConstraint(srcDigit, fkAnim))
                parent(fkAnim, srcDigit)
                makeIdentity(fkAnim, r=1, t=0, s=0, jo=0, a=1)
                lockAndHideAttrs(fkAnim, ['t', 's', 'radius', 'v'])
                parent(srcDigitNext, fkAnim)

            # For each segment, create an adder for all of the rotate values to feed into and stack
            digitAdders = []
            adderProxies = []
            
            for jnt in digitCopy[:-1]:
                adder = createNode('plusMinusAverage', n=digitName+'_'+str(i)+'_adder')
                adder.output3D >> jnt.rotate
                digitAdders.append(adder)
                
                # A couple of the attributes will need to drive the adders
                # with SDKs.  This needs to be done indirectly.
                adderProxy = group(em=1, n=digitName+'_'+str(i)+'_adderProxy')
                hide(adderProxy)
                delete(parentConstraint(jnt, adderProxy, mo=0))
                parent(adderProxy, jnt)
                adderProxies.append(adderProxy)
                
                adderProxy.rotate >> adder.input3D[0]
            
            # Adder for just the base of the finger to move the knuckle
            if isNormalDigit:
                translateAdder = createNode('plusMinusAverage', n=digitName+'_0_translateAdder')
                translateAdder.output3D >> digitCopy[0].translate
                adderProxies[0].translate >> translateAdder.input3D[0]

            # Create an animation control at the base of the digit and
            # hook up its attributes to the digit chain
            select(cl=1)
            anim = joint(n=compName+'_'+digitName+'_con')
            addAnimAttr(anim)
            anims.append(anim)
            anim.drawStyle.set(2)
            delete(parentConstraint(digitZeroGrp, anim, mo=0))
            makeIdentity(anim, t=0, r=1, s=0, jo=0, a=1)
            animShape = circle(normal=(1,0,0), center=(0,3*digitRadius,0), r=digitRadius, ch=0)[0]
            parent(animShape.getShape(), anim, s=1, add=1)
            delete(animShape)
            parent(anim, digitZeroGrp)
            parent(digitZeroGrp, mainGrp)
            
            # Indicate added attrs
            anim.addAttr('extraAttrs', at='enum', en='-----')
            anim.extraAttrs.lock()
            anim.extraAttrs.showInChannelBox(True)
            
            # Digit segment curl
            anim.addAttr('curl1', k=1)
            anim.addAttr('curl2', k=1)
            anim.addAttr('curl3', k=1)
            
            anim.curl1 >> mu.axisAttr(digitAdders[0].input3D[1], rotateAxis)
            anim.curl2 >> mu.axisAttr(digitAdders[1].input3D[1], rotateAxis)
            anim.curl3 >> mu.axisAttr(digitAdders[2].input3D[1], rotateAxis)
            
            # Digit segment side-to-side
            anim.addAttr('sideToSide', k=1)
            
            anim.sideToSide >> mu.axisAttr(digitAdders[0].input3D[1], upAxis)
            
            # Digit segment twist
            anim.addAttr('twist', k=1)
            
            anim.twist >> mu.axisAttr(digitAdders[0].input3D[1], lengthAxis)

            # Digit scrunch
            anim.addAttr('scrunch', k=1, min=-10, max=10, dv=0)
            for i in xrange(len(digitCopy)-1):
                if i == 0:
                    rot = scrunchRotate
                else:
                    numDigits = (len(digitChain)-1)
                    rot = (-scrunchRotate * numDigits) / float(numDigits-1)

                scrunchAttr = mu.axisAttr(adderProxies[i].r, rotateAxis)
                mu.sdk(anim.scrunch, [-10, 0, 10], scrunchAttr, [-rot, 0, rot])

            
            # Knuckle height
            if isNormalDigit:
                anim.addAttr('knuckle', k=1)
                anim.knuckle >> mu.axisAttr(translateAdder.input3D[1], upAxis)

            # Whole digit rotation
            # - Note: to avoid more constraints, this will just plug into the digits' joint orient
            for i in xrange(len(digitCopy)-1):
                jnt = digitCopy[i]
                mu.axisAttr(anim.r, rotateAxis) >> mu.axisAttr(digitAdders[i].input3D[2], rotateAxis)
                if i == 0:
                    mu.axisAttr(anim.r, upAxis) >> mu.axisAttr(digitAdders[i].input3D[2], upAxis)
                    mu.axisAttr(anim.r, lengthAxis) >> mu.axisAttr(digitAdders[i].input3D[2], lengthAxis)

            
            if isNormalDigit:
            
                # All digits: Spread
                spreadRotate = -30*(digitIndex-indexOfPeakDigit)
                spreadTwistRotate = 15*(digitIndex-indexOfPeakDigit)
                mu.sdk(allDigitAnim.spread, [-10, 0, 10], mu.axisAttr(adderProxies[0].r, upAxis), [-spreadRotate, 0, spreadRotate])
                mu.sdk(allDigitAnim.spread, [-10, 0, 10], mu.axisAttr(adderProxies[0].r, lengthAxis), [-spreadTwistRotate, 0, spreadTwistRotate])

                # All digits: Knuckle flatten
                relaxedTranslate = 2*digitRadius*(peakFunc(digitIndex)-.5)
                mu.sdk(allDigitAnim.flattenKnuckles, [-10, 0, 10], mu.axisAttr(adderProxies[0].t, upAxis), [2*relaxedTranslate, relaxedTranslate, 0])

            # All digits: Hide on finger FK controls
            allDigitAnim.fkAnimVis >> baseJnt.v
                
            # Hook the digit joints up to this component
            for j in xrange(len(digitChain)-1):
                src = fkAnims[j]
                tgt = digitChain[j]
                if j == 0:
                    pointConstraint(src, tgt, mo=0)
                orientConstraint(src, tgt, mo=0)

            # Clean up, increment, and handle the next digit
            lockAndHideAttrs(anim, ['t', 's', 'radius', 'v'])
            digitIndex += 1

        delete(commonTransform)

        # Add bonus attributes if applicable
        if bonusAttrs:
            
            # All fingers: Sine wave movement
            sineDriverGrp = mu.sineDriver(map(lambda jnt: jnt.jointOrientZ, waveJnts), n=compName+'_sineDriver')
            parent(sineDriverGrp, mainGrp)
            
            allDigitAnim.addAttr('waveAnimation', k=1, dv=0)
            allDigitAnim.addAttr('waveAmplitude', k=1, dv=0)
            allDigitAnim.addAttr('waveFrequency', k=1, dv=sineDriverGrp.frequency.get())
            
            allDigitAnim.waveAnimation >> sineDriverGrp.offset
            allDigitAnim.waveAmplitude >> sineDriverGrp.amplitude
            allDigitAnim.waveFrequency >> sineDriverGrp.frequency
            
        # HOOK UP TO META SYSTEM
        connectChainToMeta(anims, self.networkNode, 'anims')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp') # Required otherwise '.parentUnder' not implemented Exception thrown

        
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        Connects this component to the other component.
        
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []   
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans, w=1, mo=1)

        
    def getAllAnims(self):
        '''
        Return a list of all anims.
        '''
        
        return self.networkNode.anims.listConnections()

        
class BlendShapeController(RigComponent):
    '''
    Compile blendshapes into a set of anims using a hierarchy ordered like this example:

    (BASE SHAPES)
    headGeo
    browGeo

    (BLENDS SHAPE HIERARCHY)
    blendshapes
        left_eye
            blink
                headGeo
                browGeo
            anger
                headGeo
                browGeo         
    '''

    def __init__(self, side, bodyPart, bsGrp, baseShapes=[], min=0, max=1, node=None):
        '''
        side:
            The side is this component on: center, left, or right.
        bodyPart:
            The body part the component is for: arm, leg, clavicle, foot, etc.
        bsGrp:
            The hierarchy of blendshapes using the structure described above
        baseShapes:
            The base shapes the will receive blendshape nodes
        dv, min, max:
            Minimum and maximum for the attributes driving the blendshapes
        '''
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'BlendShapeController'):
                    self.networkNode = node
                else:
                    printError("BlendShapeController: node %s is not an BlendShapeController metaNode"%(node))
            else:
                printError("BlendShapeController: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        # Initiate the component
        RigComponent.__init__(self, 'BlendShapeController', 1.0, 'Anims that drive a set of blendshapes.', side, bodyPart)
        
        compName = '%s_%s'%(side, bodyPart)

        # Base shape stuff
        bsGrpNode = PyNode(bsGrp)
        baseNames = []
        baseObjMap = {}
        for baseShape in baseShapes:
            baseName = mu.getBaseName(baseShape)
            baseNames.append(baseName)
            baseObjMap[baseName] = PyNode(baseShape)
        
        # Create empty blendshape nodes and remember name to blendshape node mapping
        bsMap = {}
        for bs in baseShapes:
            baseName = mu.getBaseName(bs)
            bsNode = blendShape(bs, n=mu.getBaseName(bs)+"_bsNode", frontOfChain=1, origin="local")[0]
            bsMap[baseName] = bsNode
        
        # Create anims
        anims = []
        zeroGrps = []
        bsAnimMap = {}
        for animSet in bsGrpNode.getChildren():
            select(cl=1)
            animSetName = mu.getBaseName(animSet)
            anim = joint(n=animSetName+"_blend_anim")
            cube = polyCube()[0]
            appendShape(cube, anim)
            delete(cube)
            anims.append(anim)
            addAnimAttr(anim)
            lockAndHideAttrs(anim, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius'])
            zeroGrp = createZeroedOutGrp(anim)
            zeroGrps.append(zeroGrp)
            bsAnimMap[animSetName] = anim
        
        # Connect blendshapes nested in the bsGrp as thus:
        # For each child, the blend weight name is the group name, and meshes within
        # that child group determine the blends to the baseShapes.
        for animSet in bsGrpNode.getChildren():
            animSetName = mu.getBaseName(animSet)
            for bsSet in animSet.getChildren():
                attrName = mu.getBaseName(bsSet)
                for bs in bsSet.getChildren():
                    targetName = mu.getBaseName(bs)
                    if targetName in baseNames:
                        bs.rename(animSetName+"_"+attrName)
                        bsNode = bsMap[targetName]
                        blendShape( bsNode, e=1, t=( baseObjMap[targetName], bsNode.numWeights(), bs, 1.0 ) )
                        bs.rename(targetName)
             
        # Create attributes on the anim and hook up to blendshapes
        attrs = []
        for animSet in bsGrpNode.getChildren():
            animSetName = mu.getBaseName(animSet)
            anim = bsAnimMap[animSetName]
            for bsSet in animSet.getChildren():
                attrName = mu.getBaseName(bsSet)
                addAttr(anim, ln=attrName, sn=attrName, at='double', min=min, max=max, dv=0)
                attr = anim.attr(attrName)
                attr.showInChannelBox(1)
                attr.setKeyable(1)
                attrs.append(attr)
                for bsNode in bsMap.values():
                    if bsNode.hasAttr(animSetName+"_"+attrName):
                        bsWeightAttr = bsNode.attr(animSetName+"_"+attrName)
                        attr >> bsWeightAttr
                    
        # Prune deformer membership
        for attr in attrs: attr.set(max)
        for bsNode in bsMap.values(): bsNode.prune()
        for attr in attrs: attr.set(0)
        
        # Delete blendshapes group
        delete(bsGrpNode)
        
        # Group all the anims under one group
        mainGrp = group(zeroGrps,n = "%s_component_group"%compName)
        
        # Connect the mess of Maya nodes that we've created and organized into the meta system
        connectChainToMeta(anims, self.networkNode, 'anims')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp') # Required otherwise '.parentUnder' not implemented Exception thrown
    
    
    def getAllAnims(self):
        '''
        Returns a list of all the anims.
        '''
        return self.networkNode.anims.listConnections()
        
    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        Connects this component to another component.
        comp:
            The component to attach to.
        location:
            The place where the components connect, ex, start, end, jointName.
        point:
            Attach by translation.
        orient:
            Attach by orientation.
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans, w=1, mo=1)
        
    def getConnectObj(self, location=None):
        '''
        Gets the component to connect to at location.
        
        location:
            The location to connect to.  Doesn't really matter for this component.
        return:
            The obj which others can connect to.
        '''
        return self.networkNode.componentGrp.listConnections()[0]
        
    def toDefaultPose(self):
        '''
        Moves the component's anims back to the bind position.
        '''
        for anim in self.networkNode.anims.listConnections():
            for attr in anim.listAttr(k=1):
                attr.set(0)

                
class FlexibleEyelid(RigComponent):

    def __init__(  self, side, bodyPart, eyeForward, eyeUp, eyeWidthMarker,
                   innerCornerJnt, outerCornerJnt, upperLidJnts, lowerLidJnts,
                   blinkOvershoot=1.05, node=None):
        '''
        Creates a flexible eyelid component.  Input joints should be ordered from inner-most joint to
        outer-most joint, and for best automatic weight generation there should be one joint corresponding
        with each edge loop.
        
        For assistance in generating these joints use the tool found in scene_manager.metaUtil:
        
        import scene_manager.metaUtil as mu; mu.FlexibleEyelidJointCreator()
        
        side:
            Side of the face.
        
        bodyPart:
            Unique label of this component.
         
        eyeForward:
            Locator marking the forward direction and surface of the non-uniform eyelid.  This is not necessarily where
            the pupil will be aimed by default, but where the squished sphere representing how the eyelid
            should move is aimed.
        
        eyeUp:
            Locator marking the top direction and surface of the non-uniform eyelid. 
        
        eyeWidthMarker:
            Width of the non-uniform eyelid relative to the plane created by eyeForward, eyeUp, and the eye
            down direction which is world negative y.
        
        innerCornerJnt:
            Joint representing the inner corner of the eye.
        
        outerCornerJnt:
            Joint representing the outer corner of the eye.
            
        upperLidJnts:
            List of joints representing the upper lid.  For maximum accuracy there should be one joint per edge loop.
            The order should be inner-most joint to outer-most.
            
        lowerLidJnts:
            List of joints representing the lower lid.  For maximum accuracy there should be one joint per edge loop.
            The order should be inner-most joint to outer-most.
            
        blinkOvershoot:
            For the blink attribute, this is the magnitude at which the lids overshoot when blink is set to 1.
            This is to ensure the eyelid geometry appears to fully close.
        
        '''
        
        # REQUISITE META SETUP
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FlexibleEyelid'):
                    self.networkNode = node
                else:
                    printError("FlexibleEyelid: node %s is not an FlexibleEyelid metaNode"%(node))
            else:
                printError("FlexibleEyelid: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        # Initiate the component
        RigComponent.__init__(self, 'FlexibleEyelid', 1.0, 'Flexible, non-uniform eyelid component', side, bodyPart)
        compName = '%s_%s'%(side, bodyPart)

        eyeForward = PyNode(eyeForward)
        eyeUp = PyNode(eyeUp)
        eyeWidthMarker = PyNode(eyeWidthMarker)
        
        # START COMPONENT SETUP

        # Transform representing the scaling of this non-uniform eye.  
        # All rotations for the lid will happen within this transform.
        scaleSpace = mu.getScaleSpace(eyeForward, eyeUp, eyeWidthMarker, name=compName+'_scaleGrp')
        hide(scaleSpace)
        
        if side == 'left':
                doUpperLidAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(1,0,0), u=(0,-1,0), wut='object', wuo=eyeUp)
                doLowerLidAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(-1,0,0), u=(0,1,0), wut='object', wuo=eyeUp)
        elif side == 'right' or side == 'center':
                doUpperLidAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(-1,0,0), u=(0,1,0), wut='object', wuo=eyeUp)
                doLowerLidAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(1,0,0), u=(0,-1,0), wut='object', wuo=eyeUp)
        else:
            raise Exception('createEyeLidComponent: Invalid side specified. Please choose "left", "right", or "center".')
        
        # Lists of aim locators, where the joint aimers within the scaled eye space will always point
        upperLidAimerTargets = []
        lowerLidAimerTargets = []
        
        # Info for iterating through all lid joints at once
        lidJoints = [innerCornerJnt]+upperLidJnts+[outerCornerJnt]+lowerLidJnts
        lowerLidStartIndex = len(upperLidJnts)+2
        
        # Constrain the bind joints to their respective locators along the non-uniform space.
        for i in xrange(len(lidJoints)):
            j = PyNode(lidJoints[i])
            
            # True if we're working on an upper lid joint or one of the corner joints
            isUpperLid = (i < lowerLidStartIndex)
            
            if isUpperLid:
                doAim = doUpperLidAim
            else:
                doAim = doLowerLidAim
                
            # Aimer within the scaled eye space that will point to where a joint should be
            jAimer = group(em=1, n=compName+'_'+str(i)+'_aimerGrp')
            delete(parentConstraint(scaleSpace, jAimer, mo=0))
            parent(jAimer, scaleSpace)
            jAimer.scale.set(1,1,1)
            delete(doAim(eyeForward, jAimer))
            
            # Locator at the "edge" of the non-uniform eye.  It will slide along the non-uniform
            # surface of the eye, directing where its corresponding joint should go.
            jExtentsMarker = spaceLocator(n=compName+'_'+str(i)+'_extents')
            parent(jExtentsMarker, jAimer)
            delete(pointConstraint(eyeForward, jExtentsMarker, mo=0))
            jExtentsMarker.rotate.set(0,0,0)
            jExtentsMarker.scale.set(1,1,1)
            
            delete(doAim(j, jAimer))
            
            # Along side the extents markers are up and side locators to indicate the plane
            # (in world space) that the joint will need to slide along
            jExtentsUp = duplicate(jExtentsMarker, n=jExtentsMarker.replace('extents', 'extentsUp'))[0]
            jExtentsUp.ty.set(1)
            
            jExtentsSide = duplicate(jExtentsMarker, n=jExtentsMarker.replace('extents', 'extentsSide'))[0]
            jExtentsSide.tz.set(1)

            # Attach bind joint to the extents
            pointConstraint(jExtentsMarker, j, mo=1)
            aimConstraint(jExtentsUp, j, mo=1, aim=(0,1,0), u=(0,0,1), wut='object', wuo=jExtentsSide)
            
            # Create locator for the joint aimer transform to aim at
            jAimerTarget = spaceLocator(n=compName+'_'+str(i)+'_target')
            delete(pointConstraint(j, jAimerTarget, mo=0))
            
            jAimerAc = doAim(jAimerTarget, jAimer)
            '''
            # Set aimer world up to align with the scale group
            jAimerAc.setWorldUpType('objectrotation')
            jAimerAc.setWorldUpObject(scaleSpace)
            '''
            
            if isUpperLid:
                upperLidAimerTargets.append(jAimerTarget)
            else:
                lowerLidAimerTargets.append(jAimerTarget)
        
        # Organize the aimer targets
        targetGrp = group(upperLidAimerTargets+lowerLidAimerTargets, n=compName+'_targetGrp')
        targetGrp.inheritsTransform.set(0)
        hide(targetGrp)
        
        # Drive upper lid aimer targets by a highres curve
        upperLid_highResCurve = createCurveThroughObjects(upperLidAimerTargets, degree=1)
        upperLid_highResCurve.rename(compName+'_upperLidCurve')
        
        i = 0
        for t in upperLidAimerTargets:
            u = i/float(len(upperLidAimerTargets)-1) # TEMPORARY SOLUTION: EVENLY SPACE
            poc = createNode('pointOnCurveInfo')
            upperLid_highResCurve.worldSpace >> poc.inputCurve
            poc.turnOnPercentage.set(1)
            poc.position >> t.translate
            poc.parameter.set(u)
            i += 1
            
        # Drive lower lid aimer targets be a highres curve
        lowerLid_highResCurve = createCurveThroughObjects([upperLidAimerTargets[0]]+lowerLidAimerTargets+[upperLidAimerTargets[-1]], degree=1)
        lowerLid_highResCurve.rename(compName+'_lowerLidCurve')
        
        i = 1
        for t in lowerLidAimerTargets:
            u = i/float(len(lowerLidAimerTargets)+1) # TEMPORARY SOLUTION: EVENLY SPACE
            poc = createNode('pointOnCurveInfo')
            lowerLid_highResCurve.worldSpace >> poc.inputCurve
            poc.turnOnPercentage.set(1)
            poc.position >> t.translate
            poc.parameter.set(u)
            i += 1
            
        # Create control curves for lids: upper, lower, blink curves
        upperLid_ctrlCurve = rebuildCurve(   upperLid_highResCurve,
                                             ch=False,
                                             rebuildType=0, # Uniform rebuild
                                             keepEndPoints=True,
                                             spans=4,
                                             degree=3,
                                             replaceOriginal=False,
                                             name=upperLid_highResCurve.replace('upperLidCurve', 'upperLidCtrlCurve')  )[0]
                        
        lowerLid_ctrlCurve = rebuildCurve(   lowerLid_highResCurve,
                                             ch=False,
                                             rebuildType=0, # Uniform rebuild
                                             keepEndPoints=True,
                                             spans=4,
                                             degree=3,
                                             replaceOriginal=False,
                                             name=lowerLid_highResCurve.replace('lowerLidCurve', 'lowerLidCtrlCurve')  )[0]
        
        upperBlink_ctrlCurve = duplicate(upperLid_ctrlCurve, n=upperLid_ctrlCurve.replace('upperLidCtrlCurve', 'upperBlinkCurve'))[0]
        lowerBlink_ctrlCurve = duplicate(lowerLid_ctrlCurve, n=lowerLid_ctrlCurve.replace('lowerLidCtrlCurve', 'lowerBlinkCurve'))[0]
        blink_ctrlCurve = duplicate(upperLid_ctrlCurve, n=upperLid_ctrlCurve.replace('upperLidCtrlCurve', 'blinkCurve'))[0]

        # Make wire to enable the lowres curves to drive the hires ones
        upperLid_wire = wire(upperLid_highResCurve, w=upperLid_ctrlCurve)
        lowerLid_wire = wire(lowerLid_highResCurve, w=lowerLid_ctrlCurve)
        
        upperLid_wire_baseCurve = str(upperLid_wire[1])+'BaseWire'
        lowerLid_wire_baseCurve = str(lowerLid_wire[1])+'BaseWire'
        
        upperLid_wire = upperLid_wire[0]
        lowerLid_wire = lowerLid_wire[0]
        
        upperLid_wire.dropoffDistance[0].set(100)
        upperLid_wire.scale[0].set(0)
        upperLid_wire.rotation.set(0)
        
        lowerLid_wire.dropoffDistance[0].set(100)
        lowerLid_wire.scale[0].set(0)
        lowerLid_wire.rotation.set(0)
        
        # Organize control curves
        curveGrp = group([  upperLid_highResCurve, lowerLid_highResCurve,
                            upperLid_ctrlCurve, lowerLid_ctrlCurve,
                            upperBlink_ctrlCurve, lowerBlink_ctrlCurve, blink_ctrlCurve,
                            upperLid_wire_baseCurve, lowerLid_wire_baseCurve],
                            n=compName+'_ctrlCurveGrp'    )
        curveGrp.inheritsTransform.set(0)
        hide(curveGrp)
        
        # Setup up control joints (which will all become eyelid tweak anims later)
        def makeCtrlJnt(t, n):
            worldPos = xform(t, q=1, ws=1, t=1)
            select(cl=1)
            j = joint(p=worldPos)
            j.rename(n)
            return j
        
        innerCornerUpperTweak_ctrlJnt = makeCtrlJnt(upperLid_ctrlCurve.cv[1], compName+'_upper_innercorner_anim')
        innerCorner_ctrlJnt = makeCtrlJnt(innerCornerJnt, compName+'_innercorner_anim')
        innerCornerLowerTweak_ctrlJnt = makeCtrlJnt(lowerLid_ctrlCurve.cv[1], compName+'_lower_innercorner_anim')

        outerCornerUpperTweak_ctrlJnt = makeCtrlJnt(upperLid_ctrlCurve.cv[5], compName+'_upper_outercorner_anim')
        outerCorner_ctrlJnt = makeCtrlJnt(outerCornerJnt, compName+'_outercorner_anim')
        outerCornerLowerTweak_ctrlJnt = makeCtrlJnt(lowerLid_ctrlCurve.cv[5], compName+'_lower_outercorner_anim')
        
        upperLidTweak1_ctrlJnt = makeCtrlJnt(upperLid_ctrlCurve.cv[2], compName+'_upper_innerlid_anim')
        upperLidMiddle_ctrlJnt = makeCtrlJnt(upperLid_ctrlCurve.cv[3], compName+'_upper_lid_anim')
        upperLidTweak2_ctrlJnt = makeCtrlJnt(upperLid_ctrlCurve.cv[4], compName+'_upper_outerlid_anim')
        
        lowerLidTweak1_ctrlJnt = makeCtrlJnt(lowerLid_ctrlCurve.cv[2], compName+'_lower_innerlid_anim')
        lowerLidMiddle_ctrlJnt = makeCtrlJnt(lowerLid_ctrlCurve.cv[3], compName+'_lower_lid_anim')
        lowerLidTweak2_ctrlJnt = makeCtrlJnt(lowerLid_ctrlCurve.cv[4], compName+'_lower_outerlid_anim')

        # Bind control curves to control joints
        select([innerCorner_ctrlJnt,
                innerCornerUpperTweak_ctrlJnt,
                upperLidTweak1_ctrlJnt,
                upperLidMiddle_ctrlJnt,
                upperLidTweak2_ctrlJnt,
                outerCornerUpperTweak_ctrlJnt,
                outerCorner_ctrlJnt])
        select(upperLid_ctrlCurve, add=1) # Upper lid ctrl curve
        
        skinCluster(toSelectedBones=1,
                    obeyMaxInfluences=0,
                    skinMethod=0,
                    ignoreHierarchy=1,
                    dropoffRate=4,
                    nw=1,
                    mi=1)
                    
        select([innerCorner_ctrlJnt,
                innerCornerUpperTweak_ctrlJnt,
                upperLidTweak1_ctrlJnt,
                upperLidMiddle_ctrlJnt,
                upperLidTweak2_ctrlJnt,
                outerCornerUpperTweak_ctrlJnt,
                outerCorner_ctrlJnt])
        select(upperBlink_ctrlCurve, add=1) # Upper blink ctrl curve
        
        skinCluster(toSelectedBones=1,
                    obeyMaxInfluences=0,
                    skinMethod=0,
                    ignoreHierarchy=1,
                    dropoffRate=4,
                    nw=1,
                    mi=1)
                    
        select([innerCorner_ctrlJnt,
                innerCornerLowerTweak_ctrlJnt,
                lowerLidTweak1_ctrlJnt,
                lowerLidMiddle_ctrlJnt,
                lowerLidTweak2_ctrlJnt,
                outerCornerLowerTweak_ctrlJnt,
                outerCorner_ctrlJnt])
        select(lowerLid_ctrlCurve, add=1) # Lower lid ctrl curve
        
        skinCluster(toSelectedBones=1,
                    obeyMaxInfluences=0,
                    skinMethod=0,
                    ignoreHierarchy=1,
                    dropoffRate=4,
                    nw=1,
                    mi=1)
                    
        select([innerCorner_ctrlJnt,
                innerCornerLowerTweak_ctrlJnt,
                lowerLidTweak1_ctrlJnt,
                lowerLidMiddle_ctrlJnt,
                lowerLidTweak2_ctrlJnt,
                outerCornerLowerTweak_ctrlJnt,
                outerCorner_ctrlJnt])
        select(lowerBlink_ctrlCurve, add=1) # Lower blink ctrl curve
        
        skinCluster(toSelectedBones=1,
                    obeyMaxInfluences=0,
                    skinMethod=0,
                    ignoreHierarchy=1,
                    dropoffRate=4,
                    nw=1,
                    mi=1)
        
        
        
        # ANIM SETUP
        
        anims = [   innerCornerUpperTweak_ctrlJnt,innerCorner_ctrlJnt,innerCornerLowerTweak_ctrlJnt,
                    outerCornerUpperTweak_ctrlJnt,outerCorner_ctrlJnt,outerCornerLowerTweak_ctrlJnt,
                    upperLidTweak1_ctrlJnt,upperLidMiddle_ctrlJnt,upperLidTweak2_ctrlJnt,
                    lowerLidTweak1_ctrlJnt,lowerLidMiddle_ctrlJnt,lowerLidTweak2_ctrlJnt]
                    
        zeroGrps = []
        
        # Create upper lid main control anim (it'll be added to the above list later)
        select(cl=1)
        mainUpperAnim = duplicate(upperLidMiddle_ctrlJnt, n=compName+'_upper_lid_main_anim')[0]
        
        # Create lower lid main control anim (it'll be added to the above list later)
        select(cl=1)
        mainLowerAnim = duplicate(lowerLidMiddle_ctrlJnt, n=compName+'_lower_lid_main_anim')[0]
        
        # Do a pass setting up all the basic anims
        i = 0
        for anim in anims:
            zeroGrp = createZeroedOutGrp(anim)
            
            # Skip these zero groups, since their anims will be parented
            # to the main anims later
            if i < 6:
                zeroGrps.append(zeroGrp)
                
            addAnimAttr(anim)
            animShape = polySphere(r=.5, ch=0)[0]
            appendShape(animShape, anim)
            delete(animShape)
            lockAndHideAttrs(anim, ['v', 'radius', 's', 'r'])
            anim.drawStyle.set(2)
            i += 1
            
            # Flip this anim's functional direction based on the side
            if side == 'left':
                zeroGrp.scaleX.set(-1)
        
        # Set up main anims
        for anim in [mainUpperAnim, mainLowerAnim]:
            zeroGrp = createZeroedOutGrp(anim)
            zeroGrps.append(zeroGrp)
            addAnimAttr(anim)
            animShape = polySphere(r=.75, ch=0)[0]
            appendShape(animShape, anim)
            delete(animShape)
            lockAndHideAttrs(anim, ['v', 'radius', 's'])
            anim.drawStyle.set(2)
            
            # Flip this main anim's functional direction based on the side
            if side == 'left':
                zeroGrp.scaleX.set(-1)
        
        parent(map(lambda a: a.getParent(), [upperLidTweak1_ctrlJnt,upperLidMiddle_ctrlJnt,upperLidTweak2_ctrlJnt]), mainUpperAnim)
        parent(map(lambda a: a.getParent(), [lowerLidTweak1_ctrlJnt,lowerLidMiddle_ctrlJnt,lowerLidTweak2_ctrlJnt]), mainLowerAnim)
        
        # Do some additional setup on the corner tweak anims
        pointConstraint(upperLidTweak1_ctrlJnt, innerCorner_ctrlJnt, innerCornerUpperTweak_ctrlJnt.getParent(), mo=1)
        
        pointConstraint(lowerLidTweak1_ctrlJnt, innerCorner_ctrlJnt, innerCornerLowerTweak_ctrlJnt.getParent(), mo=1)
        
        pointConstraint(upperLidTweak2_ctrlJnt, outerCorner_ctrlJnt, outerCornerUpperTweak_ctrlJnt.getParent(), mo=1)
        
        pointConstraint(lowerLidTweak2_ctrlJnt, outerCorner_ctrlJnt, outerCornerLowerTweak_ctrlJnt.getParent(), mo=1)
            
        cornerTweakAnims = [    innerCornerUpperTweak_ctrlJnt, innerCornerLowerTweak_ctrlJnt,
                                outerCornerUpperTweak_ctrlJnt, outerCornerLowerTweak_ctrlJnt]
        
        mainAnims = [   mainUpperAnim, mainLowerAnim,
                        innerCorner_ctrlJnt, outerCorner_ctrlJnt,
                        upperLidTweak1_ctrlJnt,upperLidMiddle_ctrlJnt,upperLidTweak2_ctrlJnt,
                        lowerLidTweak1_ctrlJnt,lowerLidMiddle_ctrlJnt,lowerLidTweak2_ctrlJnt    ]
        
        anims.append(mainUpperAnim)
        anims.append(mainLowerAnim)
        
        # SMART BLINK SETUP

        # Upper lid blink
        upperBlink_bs = blendShape(blink_ctrlCurve, upperLid_ctrlCurve, after=1)[0]
        upperBlinkAttr = mu.addAttrToAnim(mainUpperAnim, 'blink', None, 0, 0, 1)
        mu.sdk(upperBlinkAttr, [0,1], upperBlink_bs.w[0], [0,blinkOvershoot])
        
        # Lower lid blink
        lowerBlink_bs = blendShape(blink_ctrlCurve, lowerLid_ctrlCurve, after=1)[0]
        lowerBlinkAttr = mu.addAttrToAnim(mainLowerAnim, 'blink', None, 0, 0, 1)
        mu.sdk(lowerBlinkAttr, [0,1], lowerBlink_bs.w[0], [0,blinkOvershoot])
        
        # Blink height
        blink_ctrlCurve_bs = blendShape(upperBlink_ctrlCurve, lowerBlink_ctrlCurve, blink_ctrlCurve, frontOfChain=1)[0]
       
        smartBlinkAttr = mu.addAttrToAnim(mainUpperAnim, 'blinkHeight', blink_ctrlCurve_bs.w[1], .5, 0, 1) 
        smartBlinkReverse = createNode('reverse')
        smartBlinkAttr >> smartBlinkReverse.inputX
        smartBlinkReverse.outputX >> blink_ctrlCurve_bs.w[0]
        
        
        
        # ORGANIZE AND CLEAN-UP
        
        # main anim group
        animGrp = group(em=1,n = compName+'_animGrp')
        delete(parentConstraint(scaleSpace, animGrp, mo=0))
        parent(zeroGrps, animGrp)

        # Main component group
        mainGrp = group(em=1,n = compName+'_component_group')
        parent(animGrp, mainGrp)
        parent(scaleSpace, mainGrp)
        parent(targetGrp, mainGrp)
        parent(curveGrp, mainGrp)
        
        delete(eyeForward, eyeWidthMarker)
        parent(eyeUp, mainGrp)
        hide(eyeUp)
        
        
        
        # HOOK UP TO META SYSTEM
        
        connectChainToMeta(anims, self.networkNode, 'anims')
        connectChainToMeta(lidJoints, self.networkNode, 'lidJoints')
        connectChainToMeta(cornerTweakAnims, self.networkNode, 'cornerTweakAnims')
        connectChainToMeta(mainAnims, self.networkNode, 'mainAnims')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp') # Required otherwise '.parentUnder' not implemented Exception thrown

    
    def getCornerTweakAnims(self):
        '''
        Returns only the corner tweak anims.
        '''
        return self.networkNode.cornerTweakAnims.listConnections()
        
    def getAllMainAnims(self):
        '''
        Returns only the main anims.
        '''
        return self.networkNode.mainAnims.listConnections()
        
    def getAllAnims(self):
        '''
        Returns a list of all the anims
        '''
        return self.networkNode.anims.listConnections()
        
        
    def toDefaultPose(self):
        '''
        Moves the component into the bind position
        '''
        for anim in self.getAllAnims():
            resetAttrs(anim)
            
    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        Connects this component to another component.
        comp:
            The component to attach to.
        location:
            The place where the components connect, ex, start, end, jointName.
        point:
            Attach by translation.
        orient:
            Attach by orientation.
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans, w=1, mo=1)
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        raise Exception('FlexibleEyelid.getConnectObj: No connection locations exist for this component.')

    def mirror(self, bothSides = 0):
        '''
        Mirrors the component's attributes.
        
        bothSides:
             If true, swaps the values between this and a corresponding component on the other side.
             
        return:
             A list components which had its anims effected.
        '''
        
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        
        if other == self:
            pass
            
        else:
        
            myAnims = self.getAllAnims()
            otherAnims = other.getAllAnims()
            
            if bothSides: # Swap anim attributes
                
                numAnims = len(myAnims)
                for i in xrange(numAnims):
                    mu.swapChannelBoxAttributes(myAnims[i], otherAnims[i])
                    
                return [self, other]
                
            else: # Transfer other object's anim attributes to this one
            
                numAnims = len(myAnims)
                for i in xrange(numAnims):
                    mu.transferChannelBoxAttributes(otherAnims[i], myAnims[i])
                    
                return [self]    
        


class FlexibleMouth(RigComponent):

    def __init__(  self, side, bodyPart,
                   leftCornerJnt, rightCornerJnt, upperLipJnts, lowerLipJnts,
                   lipControlPlane, node=None  ):
        '''
        Creates a flexible eyelid component.  Input joints should be ordered from inner-most joint to
        outer-most joint, and for best automatic weight generation there should be one joint corresponding
        with each edge loop.
        
        For assistance in generating these joints use the tool found in scene_manager.metaUtil:
        
        import scene_manager.metaUtil as mu; mu.FlexibleEyelidJointCreator()
        
        side:
            Side of the face.
        
        bodyPart:
            Unique label of this component.

        # TO DOCUMENT
        leftCornerJnt:
            Joint representing the left corner of the mouth.
        
        rightCornerJnt:
            Joint representing the right corner of the mouth.
            
        upperLipJnts:
            List of joints representing the upper lip between the corners.
            For maximum accuracy there should be one joint per edge loop.
            The order MUST be the right-most joint to the left-most joint (relative to character facing direction)
            
        lowerLipJnts:
            List of joints representing the lower lip between the corners.
            For maximum accuracy there should be one joint per edge loop.
            The order MUST be the right-most joint to the left-most joint (relative to character facing direction).
        '''
        
        
        # REQUISITE META SETUP
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FlexibleMouth'):
                    self.networkNode = node
                else:
                    printError("FlexibleMouth: node %s is not an FlexibleEyelid metaNode"%(node))
            else:
                printError("FlexibleMouth: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        # Initiate the component
        RigComponent.__init__(self, 'FlexibleMouth', 1.0, 'Flexible lips component', side, bodyPart)
        compName = '%s_%s'%(side, bodyPart)
        
        
        # START COMPONENT SETUP
        
        lowerRotationUpLoc = spaceLocator(n=compName+'_lowerNormalConstraintUp')
        upperRotationUpLoc = spaceLocator(n=compName+'_upperNormalConstraintUp')
        
        delete(listRelatives(lipControlPlane, children=1, type='transform'))
        
        lowerLipCtrlPlane = duplicate(lipControlPlane, n=compName+'_lowerLipCtrlPlane')[0].getShape()
        upperLipCtrlPlane = duplicate(lipControlPlane, n=compName+'_upperLipCtrlPlane')[0].getShape()
        
        # Info for iterating through all lid joints at once
        lipJnts = [leftCornerJnt,rightCornerJnt]+upperLipJnts+lowerLipJnts
        
        # Create series of locators that will ultimately drive their corresponding joints.
        # Locator NURBs plane -> Inbetween joint for additional rotation -> bind joint
        upperLipLocs = []
        lowerLipLocs = []
        
        upperLipInbetweenJnts = []
        lowerLipInbetweenJnts = []
        
        def createJntLocator(jnt, ctrlPlane=upperLipCtrlPlane, upObj=upperRotationUpLoc):
            
            # Locator that slides along the nurbs plane
            jLoc = spaceLocator(n=str(jnt)+'_loc')
            delete(pointConstraint(jnt, jLoc, mo=0))
            normalConstraint(ctrlPlane, jLoc, wut='objectrotation', wuo=upObj)
            
            
            # Intermediary joint parented to the locator which will drive the bind joint
            select(cl=1)
            inbetweenJnt = joint(n=str(jnt)+'_loc_intermed')
            delete(pointConstraint(jnt, inbetweenJnt, mo=0))
            delete(orientConstraint(jLoc, inbetweenJnt, mo=0))
            parent(inbetweenJnt, jLoc)
            makeIdentity(inbetweenJnt, r=1, t=0, s=0, jo=0, a=1)
            
            # Hook to bind joint
            pointConstraint(inbetweenJnt, jnt, mo=0)
            orientConstraint(inbetweenJnt, jnt, mo=1)
            
            return (jLoc, inbetweenJnt)

        for jnt in [rightCornerJnt]+upperLipJnts+[leftCornerJnt]:
            ret = createJntLocator(jnt)
            upperLipLocs.append(ret[0])
            upperLipInbetweenJnts.append(ret[1])
        
        for jnt in lowerLipJnts:
            ret = createJntLocator(jnt, lowerLipCtrlPlane, lowerRotationUpLoc)
            lowerLipLocs.append(ret[0])
            lowerLipInbetweenJnts.append(ret[1])


        # HIGHRES LOCATOR CURVES
        
        # Drive drive the upper lip locators via a high res curve
        upperLip_highResCurve = createCurveThroughObjects(upperLipLocs, degree=1)
        upperLip_highResCurve.rename(compName+'_upperLipCurve')
        
        i = 0
        for t in upperLipLocs:
            u = i/float(len(upperLipLocs)-1) # Evenly space
            poc = createNode('pointOnCurveInfo')
            upperLip_highResCurve.worldSpace >> poc.inputCurve
            poc.turnOnPercentage.set(1)
            poc.position >> t.translate
            poc.parameter.set(u)
            i += 1
            
        # Drive drive the lower lip locators via a high res curve
        lowerLip_highResCurve = createCurveThroughObjects(lowerLipLocs, degree=1)
        lowerLip_highResCurve.rename(compName+'_lowerLipCurve')
        
        i = 1
        for t in lowerLipLocs:
            u = i/float(len(lowerLipLocs)+1) # Evenly space
            poc = createNode('pointOnCurveInfo')
            lowerLip_highResCurve.worldSpace >> poc.inputCurve
            poc.turnOnPercentage.set(1)
            poc.position >> t.translate
            poc.parameter.set(u)
            i += 1

        # LOWRES CONTROL CURVES

        # Create control curves for lids: upper, lower, blink curves
        upperLip_ctrlCurve = rebuildCurve(   upperLip_highResCurve,
                                             ch=False,
                                             rebuildType=0, # Uniform rebuild
                                             keepEndPoints=True,
                                             spans=4,
                                             degree=3,
                                             replaceOriginal=False,
                                             name=upperLip_highResCurve.replace('upperLipCurve', 'upperLipCtrlCurve')  )[0]
                        
        lowerLip_ctrlCurve = rebuildCurve(   lowerLip_highResCurve,
                                             ch=False,
                                             rebuildType=0, # Uniform rebuild
                                             keepEndPoints=True,
                                             spans=4,
                                             degree=3,
                                             replaceOriginal=False,
                                             name=lowerLip_highResCurve.replace('lowerLipCurve', 'lowerLipCtrlCurve')  )[0]
        
        
        # WIRES
        
        # Make wire to enable the lowres curves to drive the hires ones
        upperLip_wire = wire(upperLip_highResCurve, w=upperLip_ctrlCurve)
        lowerLip_wire = wire(lowerLip_highResCurve, w=lowerLip_ctrlCurve)
        
        upperLip_wire_baseCurve = str(upperLip_wire[1])+'BaseWire'
        lowerLip_wire_baseCurve = str(lowerLip_wire[1])+'BaseWire'
        
        upperLip_wire = upperLip_wire[0]
        lowerLip_wire = lowerLip_wire[0]
        
        upperLip_wire.dropoffDistance[0].set(100)
        upperLip_wire.scale[0].set(0)
        upperLip_wire.rotation.set(0)
        
        lowerLip_wire.dropoffDistance[0].set(100)  
        lowerLip_wire.scale[0].set(0)
        lowerLip_wire.rotation.set(0)
        
        # CREATE AND BIND CONTROL JOINTS
        
        upperLipCtrlJnts = []
        lowerLipCtrlJnts = []
        leftCornerCtrlJnt = None
        rightCornerCtrlJnt = None
        
        
        def makeCtrlJnt(t, n):
            worldPos = xform(t, q=1, ws=1, t=1)
            select(cl=1)
            j = joint(p=worldPos)
            j.rename(n)
            return j
        
        # Upper lip control joints
        for pair in [    (upperLip_ctrlCurve.cv[1], compName+'_upper_rightCorner_ctrlJnt'),
                         (upperLip_ctrlCurve.cv[2], compName+'_upper_right_ctrlJnt'),
                         (upperLip_ctrlCurve.cv[3], compName+'_upper_middle_ctrlJnt'),
                         (upperLip_ctrlCurve.cv[4], compName+'_upper_left_ctrlJnt'),
                         (upperLip_ctrlCurve.cv[5], compName+'_upper_leftCorner_ctrlJnt') ]:
            upperLipCtrlJnts.append(makeCtrlJnt(pair[0], pair[1]))
        
        # Lower lip control joints
        for pair in [    (lowerLip_ctrlCurve.cv[1], compName+'_lower_rightCorner_ctrlJnt'),
                         (lowerLip_ctrlCurve.cv[2], compName+'_lower_right_ctrlJnt'),
                         (lowerLip_ctrlCurve.cv[3], compName+'_lower_middle_ctrlJnt'),
                         (lowerLip_ctrlCurve.cv[4], compName+'_lower_left_ctrlJnt'),
                         (lowerLip_ctrlCurve.cv[5], compName+'_lower_leftCorner_ctrlJnt') ]:
            lowerLipCtrlJnts.append(makeCtrlJnt(pair[0], pair[1]))
            
        # Corner control joints
        leftCornerCtrlJnt = makeCtrlJnt(leftCornerJnt, compName+'_left_ctrlJnt')
        rightCornerCtrlJnt = makeCtrlJnt(rightCornerJnt, compName+'_right_ctrlJnt')
        
        # Bind control curves to control joints
        select([rightCornerCtrlJnt]+upperLipCtrlJnts+[leftCornerCtrlJnt])
        select(upperLip_ctrlCurve, add=1) # Upper lid ctrl curve
        
        skinCluster(toSelectedBones=1,
                    obeyMaxInfluences=0,
                    skinMethod=0,
                    ignoreHierarchy=1,
                    dropoffRate=4,
                    nw=1,
                    mi=1)
                    
        select([rightCornerCtrlJnt]+lowerLipCtrlJnts+[leftCornerCtrlJnt])
        select(lowerLip_ctrlCurve, add=1) # Lower lid ctrl curve
        
        skinCluster(toSelectedBones=1,
                    obeyMaxInfluences=0,
                    skinMethod=0,
                    ignoreHierarchy=1,
                    dropoffRate=4,
                    nw=1,
                    mi=1)
                    
                    
        # LIP CONTROL PLANE
                
        # Make sure lowres lip controller only slides along the control plane
        ctrlJnts = [leftCornerCtrlJnt, rightCornerCtrlJnt]+upperLipCtrlJnts+lowerLipCtrlJnts
        nurbsLocs = []
        anims = []
        leftCornerAnim = None
        rightCornerAnim = None
        upperLipAnims = []
        lowerLipAnims = []
        
        def createAnimJnt(cj, ctrlPlane=upperLipCtrlPlane, upObj=upperRotationUpLoc):
            select(cj)
            anim = duplicate(n=cj.replace('ctrlJnt', 'anim'))[0]
            anims.append(anim)
            
            # Create locator which will slide along the nurbs control plane and 
            # subsequently drive the controlJoint
            nurbsLoc = spaceLocator(n=cj.replace('ctrlJnt', 'nurbsLoc'))
            nurbsLocs.append(nurbsLoc)
            ctrlPlane.worldSpace >> nurbsLoc.geometry
            normalConstraint(ctrlPlane, nurbsLoc, wut='objectrotation', wuo=upObj)
            nurbsLocPc = pointConstraint(anim, nurbsLoc, mo=0)
            delete(orientConstraint(nurbsLoc, anim, mo=0))
            makeIdentity(anim, r=1, apply=1)
            
            parentConstraint(nurbsLoc, cj, mo=1)
            
            return anim
            
        leftCornerAnim = createAnimJnt(leftCornerCtrlJnt)
        
        rightCornerAnim = createAnimJnt(rightCornerCtrlJnt)
            
        for cj in upperLipCtrlJnts: upperLipAnims.append(createAnimJnt(cj))
        
        for cj in lowerLipCtrlJnts: lowerLipAnims.append(createAnimJnt(cj, lowerLipCtrlPlane, lowerRotationUpLoc))
        
        
        # Default positions of anims should be with closed lips
        for i in xrange(0, 5):
            upperAnim = upperLipAnims[i]
            lowerAnim = lowerLipAnims[i]
            midPoint = spaceLocator(n=compName+'_tempMidPoint')
            delete(parentConstraint(upperAnim, lowerAnim, midPoint))
            delete(parentConstraint(midPoint, upperAnim))
            delete(parentConstraint(midPoint, lowerAnim))
            delete(midPoint)
        
        # Do a pass setting up all the anims
        upperLipZeroGrps = []
        lowerLipZeroGrps = []
        
        for anim in anims:
            zeroGrp = createZeroedOutGrp(anim)
            if anim in lowerLipAnims:
                lowerLipZeroGrps.append(zeroGrp)
            else:
                upperLipZeroGrps.append(zeroGrp)
                
            addAnimAttr(anim)
            animShape = polySphere(r=.25, ch=0)[0]
            move(animShape.vtx, .75, 0, 0, r=1, os=1)
            appendShape(animShape, anim)
            delete(animShape)
            lockAndHideAttrs(anim, ['v', 'radius', 's', 'r'])
            anim.drawStyle.set(2)
        
        for anim in upperLipAnims:
            move(anim.getShape().vtx, 0, .25, 0, r=1, os=1)
            
        for anim in lowerLipAnims:
            move(anim.getShape().vtx, 0, -.25, 0, r=1, os=1) 
        
        mainAnims = upperLipAnims[1:-1]+lowerLipAnims[1:-1]+[leftCornerAnim, rightCornerAnim]
        
        # Do some additional setup on the corner tweak anims
        pointConstraint(rightCornerAnim, upperLipAnims[1], upperLipAnims[0].getParent(), mo=1)
        
        pointConstraint(rightCornerAnim, lowerLipAnims[1], lowerLipAnims[0].getParent(), mo=1)
        
        pointConstraint(leftCornerAnim, upperLipAnims[-2], upperLipAnims[-1].getParent(), mo=1)
        
        pointConstraint(leftCornerAnim, lowerLipAnims[-2], lowerLipAnims[-1].getParent(), mo=1)
        
        cornerTweakAnims = [upperLipAnims[0], lowerLipAnims[0], upperLipAnims[-1], lowerLipAnims[-1]]
        
        
        # LIP CURL ATTRIBUTES
        
        # Anim info
        ul_numJntsPerAnim = int(floor((len(upperLipJnts))/2.0))
        ul_numJntsPerSide = int(floor(ul_numJntsPerAnim/2.0))
        ul_midPoint = ul_numJntsPerAnim
        
        ll_numJntsPerAnim = int(floor(len(lowerLipJnts)/2.0))
        ll_numJntsPerSide = int(floor(ll_numJntsPerAnim/2.0))
        ll_midPoint = ll_numJntsPerAnim
              
        # Weight blend list
        ul_weights = []
        ll_weights = []
        
        for i in xrange(ul_numJntsPerAnim):
            if i < ul_numJntsPerSide+1:
                weight = (i+1) / float(ul_numJntsPerSide+1)
            else:
                weight = 1 - ((i-ul_numJntsPerSide) / float(ul_numJntsPerSide+1))
                
            ul_weights.append(weight)

        for i in xrange(ll_numJntsPerAnim):
            if i < ll_numJntsPerSide+1:
                weight = (i+1) / float(ll_numJntsPerSide+1)
            else:
                weight = 1 - ((i-ll_numJntsPerSide) / float(ll_numJntsPerSide+1))
                
            ll_weights.append(-weight)
        
        '''
        print ul_numJntsPerAnim
        print ul_numJntsPerSide
        print ul_weights
        '''
        
        # Utility node table
        adders = {}
        adderIncs = {}
        
        def hookUpCustomAttrs(anim, startIndex, numJntsPerAnim, weights, inbetweenJnts, pushScalar=1, curlScalar=1):
            
            if not anim.hasAttr('curl'):
                anim.addAttr('curl', keyable=1, dv=0)
            anim_curlAttr = anim.attr('curl')
            
            if not anim.hasAttr('push'):
                anim.addAttr('push', keyable=1, dv=0)
            anim_pushAttr = anim.attr('push')
            
            for i in xrange(numJntsPerAnim):
                gi = startIndex+i
                
                # If the 'global index', which is the index into the joint
                # array, is out of bounds then skip node creation/handling
                if ((gi < 0) or (gi >= len(inbetweenJnts))):
                    continue
                
                w = weights[i]
                j = inbetweenJnts[gi]
                
                md = createNode('multiplyDivide')
                anim_curlAttr >> md.input1X
                anim_pushAttr >> md.input1Y
                md.input2X.set(curlScalar*w)
                md.input2Y.set(pushScalar*w)
                
                if str(j) not in adders:
                    adder = createNode('plusMinusAverage')
                    adderInc = 0
                    adders[str(j)] = adder
                    adderIncs[str(j)] = adderInc
                    adder.output2Dx >> j.rotateZ
                    adder.output2Dy >> j.translateX
                    
                else:
                    adder = adders[str(j)]
                    adderInc = adderIncs[str(j)]
                    
                md.outputX >> adder.input2D[adderInc].input2Dx
                md.outputY >> adder.input2D[adderInc].input2Dy
                adderIncs[str(j)] = adderInc+1
                
        hookUpCustomAttrs(upperLipAnims[1], 1, ul_numJntsPerAnim, ul_weights, upperLipInbetweenJnts, .1)
        hookUpCustomAttrs(upperLipAnims[2], 1+ul_midPoint-ul_numJntsPerSide, ul_numJntsPerAnim, ul_weights, upperLipInbetweenJnts, .1)
        hookUpCustomAttrs(upperLipAnims[3], 1+ul_midPoint+1, ul_numJntsPerAnim, ul_weights, upperLipInbetweenJnts, .1)
        
        hookUpCustomAttrs(lowerLipAnims[1], 0, ll_numJntsPerAnim, ll_weights, lowerLipInbetweenJnts, -.1) 
        hookUpCustomAttrs(lowerLipAnims[2], ll_midPoint-ll_numJntsPerSide, ll_numJntsPerAnim, ll_weights, lowerLipInbetweenJnts, -.1)
        hookUpCustomAttrs(lowerLipAnims[3], ll_midPoint+1, ll_numJntsPerAnim, ll_weights, lowerLipInbetweenJnts, -.1)
        
        # Hook up right corner of mouth 
        hookUpCustomAttrs(rightCornerAnim, -ul_numJntsPerSide, ul_numJntsPerAnim, ul_weights, upperLipInbetweenJnts, .1)
        hookUpCustomAttrs(rightCornerAnim, -ll_numJntsPerSide-1, ll_numJntsPerAnim, ll_weights, lowerLipInbetweenJnts, -.1, -1)
        
        # Hook up left corner of mouth
        hookUpCustomAttrs(leftCornerAnim, len(upperLipInbetweenJnts)-1-ul_numJntsPerSide, ul_numJntsPerAnim, ul_weights, upperLipInbetweenJnts, .1)
        hookUpCustomAttrs(leftCornerAnim, len(lowerLipInbetweenJnts)-ll_numJntsPerSide, ll_numJntsPerAnim, ll_weights, lowerLipInbetweenJnts, -.1, -1)
        
        
        # ORGANIZE
        
        curveGrp = group(em=1, n=compName+'_ctrlCurveGrp')
        parent([upperLip_highResCurve, lowerLip_highResCurve,
                upperLip_ctrlCurve, lowerLip_ctrlCurve,
                upperLip_wire_baseCurve, lowerLip_wire_baseCurve], curveGrp)
        curveGrp.inheritsTransform.set(0)
        
        ctrlJntGrp = group(em=1, n=compName+'_ctrlJntGrp')
        parent(ctrlJnts, ctrlJntGrp)
        ctrlJntGrp.inheritsTransform.set(0)
        
        locGrp = group(em=1, n=compName+'_locGrp')
        parent(upperLipLocs, lowerLipLocs, locGrp)
        locGrp.inheritsTransform.set(0)

        nurbsLocGrp = group(em=1, n=compName+'_nurbsLocGrp')
        parent(nurbsLocs, nurbsLocGrp)
        nurbsLocGrp.inheritsTransform.set(0)
        
        upperAnimsGrp = group(em=1, n=compName+'_upperAnims') # Count corners as "upper" anims
        parent(upperLipZeroGrps, upperLipCtrlPlane, upperRotationUpLoc, upperAnimsGrp)
        hide(upperLipCtrlPlane.getParent(), upperRotationUpLoc)
        
        lowerAnimsGrp = group(em=1, n=compName+'_lowerAnims')
        parent(lowerLipZeroGrps, lowerLipCtrlPlane, lowerRotationUpLoc, lowerAnimsGrp)
        hide(lowerLipCtrlPlane.getParent(), lowerRotationUpLoc)
        
        hide(locGrp, nurbsLocGrp, ctrlJntGrp, curveGrp)
        delete(lipControlPlane)
        
        # Main component group
        mainGrp = group(em=1,n = compName+'_component_group')
        parent(upperAnimsGrp, lowerAnimsGrp, nurbsLocGrp, ctrlJntGrp, curveGrp, locGrp, mainGrp)
        
        
        # HOOK UP TO META SYSTEM
        connectChainToMeta(lipJnts, self.networkNode, 'lipJoints')
        connectChainToMeta(anims, self.networkNode, 'anims')
        connectChainToMeta(mainAnims, self.networkNode, 'mainAnims')
        connectChainToMeta(cornerTweakAnims, self.networkNode, 'cornerTweakAnims')
        
        connectToMeta(lowerAnimsGrp, self.networkNode, 'lowerAnimsGrp')
        connectToMeta(upperAnimsGrp, self.networkNode, 'upperAnimsGrp')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp')
        
        
    def getCornerTweakAnims(self):
        '''
        Returns only the corner tweak anims.
        '''
        return self.networkNode.cornerTweakAnims.listConnections()
        
        
    def getAllMainAnims(self):
        '''
        Returns only the main anims.
        '''
        return self.networkNode.mainAnims.listConnections()
        
        
    def getAllAnims(self):
        '''
        Returns a list of all the anims
        '''
        return self.networkNode.anims.listConnections()
            
            
    def toDefaultPose(self):
        '''
        Moves the component into the bind position
        '''
        for anim in self.getAllAnims():
            resetAttrs(anim)


    def connectToComponent(self, comp, location, point=1, orient=1, level='all'):
        '''
        Connects this component to another component.
        comp:
            The component to attach to.
        location:
            The place where the components connect, ex, start, end, jointName.
        point:
            Attach by translation.
        orient:
            Attach by orientation.
        '''
        obj = comp.getConnectObj(location)
        
        # Determine what attributes to skip
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []
            
        # Extract attach point
        if level == 'all':
            attachPoint = self.networkNode.componentGrp.listConnections()[0]
        elif level == 'lower':
            attachPoint = self.networkNode.lowerAnimsGrp.listConnections()[0]
        elif level == 'upper':
            attachPoint = self.networkNode.upperAnimsGrp.listConnections()[0]
        else:
            raise Exception('FlexibleMouth.connectToComponent: Invalid level specified.  Please choose "all", "upper", or "lower".')
        
        # Attach me!
        parentConstraint(obj, attachPoint, sr = skipRot, st = skipTrans, w=1, mo=1)
            
    def getConnectObj(self, location):
        pass
        
        
class FKIKLimb(RigComponent):

    def __init__(self,  side, bodyPart, startJoint, endJoint, defaultSwitchValue = 0, stretchMode = 'translate', node=''):
        '''
        side:
            Component side.
            
        bodyPart:
            Specific body part this limb is used for.
        
        startJoint:
            Start of the component's chain.
        
        endJoint:
            End of the component's chain.
            
        defaultSwitchValue:
            Sets the default value of the switcher. 0 is FK, 1 is IK.
            
        stretchMode:
            Determines how the pin and stretch attributes stretch limb segments,
            either through "translate" or "scale".  Scale works well for Classic Linear
            skinning, whereas translate may be required for Dual Quaternion to prevent
            awkward deformations.  Default is translate.
        '''
        
        # REQUISITE META SETUP
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKLimb'):
                    self.networkNode = node
                else:
                    printError("FKIKLimb: node %s is not a FKIKLimb metaNode"%(node))
            else:
                printError("FKIKLimb: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        
        # Initiate the component
        RigComponent.__init__(self, 'FKIKLimb', 1.0, 'Two bone limb FKIK chain', side, bodyPart)
        
        
        # Setup the component
        self.setup(side, bodyPart, startJoint, endJoint, defaultSwitchValue, stretchMode)
        
        
        
    def setup(self, side, bodyPart, startJoint, endJoint, defaultSwitchValue, stretchMode):
        '''
        Keep FKIKLimb setup here so inheriting component classes
        can run the setup without running the FKIKLimb meta setup.
        '''
        
        compName = '%s_%s'%(side, bodyPart)
        
        chain = chainBetween(startJoint, endJoint)
        chain = map(lambda obj: PyNode(obj), chain)
        mainGrp = group(em=1, n=compName + '_component_group')
        anchorGrp = group(em=1, n=compName+'_anchorGrp')
        alignPointOrient(chain[0], mainGrp, 1, 1)
        alignPointOrient(mainGrp, anchorGrp, 1, 1)
        parent(anchorGrp, mainGrp)
        
        if ((stretchMode != 'translate') and (stretchMode != 'scale')):
            raise Exception('FKIKLimb: Invalid stretch mode.  Please specify "translate" or "scale".')
        
        
        ###################
        # SET UP IK CHAIN #
        ###################
        
        ikChain = duplicateChain(chain[0], chain[2], 'bind', 'ik')
        parent(ikChain[0], anchorGrp)
        hide(ikChain[0])
        
        select(ikChain[2])
        endLengthJnt = duplicate()[0]
        endLengthJnt.rename(compName+'_ikEndMarker_joint')
        
        ikOutputChain = [ikChain[0], ikChain[1], endLengthJnt]
        
        
        # Maya IK handle
        mainIk = ikHandle(  n=compName+'_mainIkHandle',
                            sj=ikChain[0], # Start joint
                            ee=ikChain[2], # End joint
                            solver='ikRPsolver'  )
        mainIkHandle = mainIk[0]
        
        
        # IK Anim
        select(cl=1)
        ikLabels = getJointLabels(chain[2])
        ikAnim = joint(n=ikLabels[0]+'_'+ikLabels[1]+'_ik_anim')
        ikAnim.drawStyle.set(2)
        addAnimAttr(ikAnim)
        ikAnimShape = polyCube()[0]
        appendShape(ikAnimShape, ikAnim)
        delete(ikAnimShape)

        ikAnim.rotateOrder.set(chain[2].rotateOrder.get())
        alignPointOrient(chain[2], ikAnim, 1, 1)
        ikAnim_zeroGrp = createZeroedOutGrp(ikAnim)
        
        parent(mainIkHandle, ikAnim)
        hide(mainIkHandle)

        orientConstraint(ikAnim, endLengthJnt, mo=0)
        
        lockAndHideAttrs(ikAnim, ['s', 'v', 'radius'])
        
        mu.createRotateOrderProxyAttr(ikAnim)
        
        # PV Anim
        select(cl=1)
        pvLabels = getJointLabels(chain[1])
        pvAnim = joint(n=pvLabels[0]+'_'+pvLabels[1]+'_pv_anim')
        pvAnim.drawStyle.set(2)
        addAnimAttr(pvAnim)
        pvAnimShape = polySphere()[0]
        appendShape(pvAnimShape, pvAnim)
        delete(pvAnimShape)
        
        pvLoc = createPVLocator(chain[0], chain[1], chain[2])
        alignPointOrient(pvLoc, pvAnim, 1, 0)
        alignPointOrient(ikAnim, pvAnim, 0, 1)
        delete(pvLoc)
        pvAnim_zeroGrp = createZeroedOutGrp(pvAnim)
        
        poleVectorConstraint(pvAnim, mainIkHandle)
        
        lockAndHideAttrs(pvAnim, ['r', 's', 'v', 'radius'])

        
        # Measurements for IK scaling
        totalLength = mu.getChainLength(chain[0], chain[2])
        firstBoneLength = mu.getChainLength(chain[0], chain[1])
        secondBoneLength = mu.getChainLength(chain[1], chain[2])
        
        
        # Point of interest locators
        anchor_loc = spaceLocator(n=compName+'_anchor_loc')
        lockAndHideAttrs(anchor_loc, ['t', 'r', 's'])
        parent(anchor_loc, anchorGrp)
        
        ikAnim_loc = spaceLocator(n=compName+'_ikAnim_loc')
        lockAndHideAttrs(ikAnim_loc, ['t', 'r', 's'])
        parent(ikAnim_loc, ikAnim)
        
        pvAnim_loc = spaceLocator(n=compName+'_pvAnim_loc')
        lockAndHideAttrs(pvAnim_loc, ['t', 'r', 's'])
        parent(pvAnim_loc, pvAnim)
        
        totalLength_loc = spaceLocator(n=compName+'_totalLength_loc')
        totalLength_loc.ty.set(totalLength)
        lockAndHideAttrs(totalLength_loc, ['t', 'r', 's'])
        parent(totalLength_loc, anchorGrp)
        
        hide(anchor_loc, ikAnim_loc, pvAnim_loc, totalLength_loc)
        
        
        # Distance measurements
        ikAnim_dist = distanceDimension(anchor_loc, ikAnim_loc)
        ikAnim_dist.getParent().rename(compName+'_ikAnim_dist')
        
        pvToAnchor_dist = distanceDimension(pvAnim_loc, anchor_loc)
        pvToAnchor_dist.getParent().rename(compName+'_pvToAnchor_dist')
        
        pvToIk_dist = distanceDimension(pvAnim_loc, ikAnim_loc)
        pvToIk_dist.getParent().rename(compName+'_pvToIk_dist')
        
        totalLength_dist = distanceDimension(anchor_loc, totalLength_loc)
        totalLength_dist.getParent().rename(compName+'_totalLength_dist')
        
        boneLength_md = createNode('multiplyDivide', n=compName+'_boneLength_md') # Calculate lengths of individual bones
        totalLength_dist.distance >> boneLength_md.input1Y
        totalLength_dist.distance >> boneLength_md.input1Z
        boneLength_md.input2Y.set(firstBoneLength/float(totalLength))
        boneLength_md.input2Z.set(secondBoneLength/float(totalLength))
        
        distNodes = map(lambda obj: obj.getParent(), [ikAnim_dist, pvToAnchor_dist, pvToIk_dist, totalLength_dist])
        hide(distNodes)
        parent(distNodes, mainGrp)
        
        
        # Measurement ratios
        pinBoneRatios_md = createNode('multiplyDivide', n=compName+'_pinBoneRatios_md')
        
        ikAnim_dist.distance >> pinBoneRatios_md.input1X
        pvToAnchor_dist.distance >> pinBoneRatios_md.input1Y
        pvToIk_dist.distance >> pinBoneRatios_md.input1Z
        
        totalLength_dist.distance >> pinBoneRatios_md.input2X
        boneLength_md.outputY >> pinBoneRatios_md.input2Y
        boneLength_md.outputZ >> pinBoneRatios_md.input2Z
        
        pinBoneRatios_md.operation.set(2)
        
        # How stretched the IK chain is
        ikStretchRatio_clamp = createNode('clamp', n=compName+'_totalLengthRatio_clamp')
        ikStretchRatio_clamp.minR.set(1.0)
        ikStretchRatio_clamp.maxR.set(sys.float_info.max)
        pinBoneRatios_md.outputX >> ikStretchRatio_clamp.inputR
        
        
        # - STRETCH MODE: TRANSLATE
        if (stretchMode == 'translate'):
        
            # Bone lengths when the pin attribute is activated
            pinBoneLength_md = createNode('multiplyDivide', n=compName+'_pinBoneLength_md')
            pinBoneRatios_md.outputY >> pinBoneLength_md.input1Y
            pinBoneRatios_md.outputZ >> pinBoneLength_md.input1Z
            pinBoneLength_md.input2Y.set(ikChain[1].tx.get())
            pinBoneLength_md.input2Z.set(ikChain[2].tx.get())
            
            # Bone when the IK chain is overextended
            ikOverextendBoneLength_md = createNode('multiplyDivide', n=compName+'_ikOverextendBoneLength_md')
            ikStretchRatio_clamp.outputR >> ikOverextendBoneLength_md.input1Y
            ikStretchRatio_clamp.outputR >> ikOverextendBoneLength_md.input1Z
            ikOverextendBoneLength_md.input2Y.set(ikChain[1].tx.get())
            ikOverextendBoneLength_md.input2Z.set(ikChain[2].tx.get())
            
            # Blend arm that doesn't stretch vs arm that does stretch
            ikStretch_blend = createNode('blendColors', n=compName+'_ikStretch_blend')
            ikOverextendBoneLength_md.outputY >> ikStretch_blend.color1G
            ikOverextendBoneLength_md.outputZ >> ikStretch_blend.color1B
            ikOverextendBoneLength_md.input2Y >> ikStretch_blend.color2G
            ikOverextendBoneLength_md.input2Z >> ikStretch_blend.color2B
            
            mu.addAttrToAnim(ikAnim, 'stretchy', ikStretch_blend.blender)
            
            # Blend between normal ik stretching and pv pinning
            ikPin_blend = createNode('blendColors', n=compName+'_pin_blend')
            pinBoneLength_md.outputY >> ikPin_blend.color1G
            pinBoneLength_md.outputZ >> ikPin_blend.color1B
            ikStretch_blend.outputG >> ikPin_blend.color2G
            ikStretch_blend.outputB >> ikPin_blend.color2B
            ikPin_blend.outputG >> ikChain[1].tx
            ikPin_blend.outputB >> ikChain[2].tx
            
            # Re-use arm stretch blend node to blend between possible final bone lengths
            ikChain[2].tx >> ikStretch_blend.color1R
            ikStretch_blend.color2R.set(endLengthJnt.tx.get())
            ikStretch_blend.outputR >> endLengthJnt.tx
        
        # - STRETCH MODE: SCALE
        else:
            
            # Blend arm that doesn't stretch vs arm that does stretch
            ikStretch_blend = createNode('blendColors', n=compName+'_ikStretch_blend')
            ikStretchRatio_clamp.outputR >> ikStretch_blend.color1G
            ikStretch_blend.color2G.set(1)
            
            mu.addAttrToAnim(ikAnim, 'stretchy', ikStretch_blend.blender)

            # Blend between normal ik stretching and pv pinning
            ikPin_blend = createNode('blendColors', n=compName+'_pin_blend')
            pinBoneRatios_md.outputY >> ikPin_blend.color1G
            pinBoneRatios_md.outputZ >> ikPin_blend.color1B
            ikStretch_blend.outputG >> ikPin_blend.color2G
            ikStretch_blend.outputG >> ikPin_blend.color2B
            ikPin_blend.outputG >> ikChain[0].sx
            ikPin_blend.outputB >> ikChain[1].sx
        
        pinAttrName = 'pin'+pvLabels[1].title()
        mu.addAttrToAnim(ikAnim, pinAttrName, ikPin_blend.blender)
        
        
        ###################
        # SET UP FK CHAIN #
        ###################
        
        fkAnims = duplicateChain(chain[0], chain[-1])
        parent(fkAnims[0], anchorGrp)
        
        for i in xrange(len(fkAnims)):
            fkAnim = fkAnims[i]
            fkAnim.rename(compName + '_' + str(i+1) + '_fk_anim')
            fkAnim.drawStyle.set(2)
            addAnimAttr(fkAnim)
            
            fkAnimShape = circle(normal=(1,0,0), ch=0)[0]
            appendShape(fkAnimShape, fkAnim)
            delete(fkAnimShape)
            
            mu.createRotateOrderProxyAttr(fkAnim)

            
        # CONNECT FK STRETCHING TO RIG
        
        # Add stretch attribute to the first two bones
        fkStretch = createNode('multiplyDivide', n=compName+'_fkStretch_md')
        fkStretch1Attr = mu.addAttrToAnim(fkAnims[0], 'stretch', fkStretch.input2Y, 1, 0, sys.float_info.max)
        fkStretch2Attr = mu.addAttrToAnim(fkAnims[1], 'stretch', fkStretch.input2Z, 1, 0, sys.float_info.max)
        
        # Hook up the stretch attributes
        fkStretch.input1Y.set(fkAnims[1].tx.get())
        fkStretch.input1Z.set(fkAnims[2].tx.get())
        fkStretch.outputY >> fkAnims[1].tx
        fkStretch.outputZ >> fkAnims[2].tx

        # Lock FK anim attributes
        for fkAnim in fkAnims: lockAndHideAttrs(fkAnim, ['t', 's', 'v', 'radius'])
        
        
        ###################
        # SET UP SWITCHER #
        ###################
        
        select(cl=1)
        switchAnim = joint(n=compName + '_switch_anim')
        switchAnim.drawStyle.set(2)
        addAnimAttr(switchAnim)
        
        switchAnimShape = curve(d=1, p=[(0,0,0), (0,0,2)])
        appendShape(switchAnimShape, switchAnim)
        delete(switchAnimShape)

        lockAndHideAttrs(switchAnim, ['t', 'r', 's', 'v', 'radius'])
        
        parent(switchAnim, anchorGrp)
        
        switchOrientConstraints = []
        
        # Set up orient constraints for switching
        for i in xrange(3):
            fkJnt = fkAnims[i]
            ikJnt = ikOutputChain[i]
            targetJnt = chain[i]
            
            oc = orientConstraint([fkJnt, ikJnt], targetJnt, mo=0)

            switchOrientConstraints.append(oc)
            
        # Create switch attribute and its reverse
        switchAttr = mu.addAttrToAnim(switchAnim, 'FKIKswitch', None, defaultValue=defaultSwitchValue)
        revSwitchNode = createNode('reverse', n=compName+'_switch_rev')
        switchAttr >> revSwitchNode.inputX
        
        
        # BLEND BETWEEN FK AND IK
        # The blending connections will be slightly different between stretch modes.
        
        # - STRETCH MODE: TRANSLATE
        if (stretchMode == 'translate'):
        
            # Translate blend node
            translateBlend = createNode('blendColors', n=compName+'_translate_blend')
            
            fkStretch.outputY >> translateBlend.color2G
            fkStretch.outputZ >> translateBlend.color2B
            ikOutputChain[1].tx >> translateBlend.color1G
            ikOutputChain[2].tx >> translateBlend.color1B
            
            translateBlend.outputG >> chain[1].tx
            translateBlend.outputB >> chain[2].tx
            
            # Connect switch attribute to translate blender (determining joint length)
            switchAttr >> translateBlend.blender
            
        # - STRETCH MODE: SCALE
        else:
        
            # Re-use ikStretch blend node to blend between the second bone's
            # scale with no stretch and its scale with pinning/overextension stretch
            ikChain[1].sx >> ikStretch_blend.color1R 
            ikStretch_blend.color2R.set(1)
            
            # Scale blend node
            scaleBlend = createNode('blendColors', n=compName+'_scale_blend')
            
            fkStretch1Attr >> scaleBlend.color2G
            fkStretch2Attr >> scaleBlend.color2B
            ikOutputChain[0].sx >> scaleBlend.color1G
            ikStretch_blend.outputR >> scaleBlend.color1B
            
            scaleBlend.outputG >> chain[0].sx
            scaleBlend.outputB >> chain[1].sx
            
            # Connect switch attribute to translate blender (determining joint length)
            switchAttr >> scaleBlend.blender
        
        
        # Connect switch attribute to orient constraints
        for c in switchOrientConstraints:
            switchAttr >> c.w1
            revSwitchNode.outputX >> c.w0
        
        # Connect switch attribute to FK/IK control visibility
        fkAnims[0].v.unlock()
        mu.sdk(switchAttr, [.01,.99], fkAnims[0].v, [.99,.01], itt='clamped', ott='step')
        mu.sdk(switchAttr, [.01,.99], ikAnim_zeroGrp.v, [.01,.99], itt='clamped', ott='stepnext')
        mu.sdk(switchAttr, [.01,.99], pvAnim_zeroGrp.v, [.01,.99], itt='clamped', ott='stepnext') 
        fkAnims[0].v.lock()

        switchAttr.set(defaultSwitchValue)
        
        
        # DEFINE ATTACH POINTS
        # Create proxy attach points when using "scale" stretch mode to prevent
        # transformation space issues when attaching components to each other.
        # This problem doesn't exist with the translate method luckily.
        
        # - STRETCH MODE: TRANSLATE
        if (stretchMode == 'translate'):
            
            startHandle = chain[0]
            endHandle = chain[2]
            
        # - STRETCH MODE: SCALE
        else:
            
            startHandle = group(em=1, n=compName+'_startHandle')
            parentConstraint(chain[0], startHandle, mo=0)
            parent(startHandle, mainGrp)
            
            endHandle = group(em=1, n=compName+'_endHandle')
            parentConstraint(chain[2], endHandle, mo=0)
            parent(endHandle, mainGrp)


        # ORGANIZE
        
        ##### Unecessarily patch to make some existing keys still work
        animsGrp = group(em=1, n=compName+'_animsGrp')
        ikAnimsGrp = group(em=1, n=compName+'_ikAnimsGrp')
        ikAnimsGrp.inheritsTransform.set(1)
        parent(ikAnim_zeroGrp, ikAnimsGrp)
        parent(pvAnim_zeroGrp, ikAnimsGrp)
        parent(ikAnimsGrp, animsGrp)
        parent(animsGrp, mainGrp)
        scaleConstraint(mainGrp, ikAnimsGrp, mo=0)
        lockAndHideAttrs(ikAnimsGrp, ['t', 'r', 'v'])
        lockAndHideAttrs(ikAnimsGrp, ['s'])

        anims = fkAnims+[ikAnim, pvAnim, switchAnim]
        
        # Drive the root of the arm with constraints for a solid
        # basis with which to use blendColors nodes set up earlier
        pointConstraint(anchorGrp, chain[0], mo=0)
        
        # SET UP META NODES
        
        connectToMeta(mainGrp, self.networkNode, 'componentGrp')
        
        connectChainToMeta(chain, self.networkNode, 'bindJoints')
        connectToMeta(switchAnim, self.networkNode, 'switchAnim')
        connectChainToMeta(anims, self.networkNode, 'anims')

        connectChainToMeta(fkAnims, self.networkNode, 'fkAnims')
        
        connectToMeta(startHandle, self.networkNode, 'startHandle')
        connectToMeta(endHandle, self.networkNode, 'endHandle')
        
        connectToMeta(anchorGrp, self.networkNode, 'anchorGrp')
        connectToMeta(ikAnim, self.networkNode, 'ikAnim')
        connectToMeta(ikAnim_loc, self.networkNode, 'ikAnim_loc')
        self.networkNode.setAttr('pinAttrName', pinAttrName,  f=1)
        self.networkNode.setAttr('stretchMode', stretchMode, f=1)
        connectToMeta(pvAnim, self.networkNode, 'pvAnim')
        connectChainToMeta(ikChain, self.networkNode, 'ikChain')
        connectChainToMeta(ikOutputChain, self.networkNode, 'ikOutputChain')
        connectToMeta(mainIkHandle, self.networkNode, 'mainIkHandle')
        connectToMeta(revSwitchNode, self.networkNode, 'revSwitchNode')
        
        connectChainToMeta(switchOrientConstraints, self.networkNode, 'switchOrientConstraints')

        
        # Holds original bone lengths in input1Y and input1Z
        connectToMeta(fkStretch, self.networkNode, 'fkStretch')
        
    def getSwitchAttr(self):
        '''
        Return the FKIK switch attribute.
        '''
        switchAnim = self.networkNode.switchAnim.listConnections()[0]
        return switchAnim.FKIKswitch
        
    def getAllAnims(self):
        '''
        Returns a list of all the anims
        '''
        return self.networkNode.anims.listConnections()
        
    def toDefaultPose(self):
        '''
        Moves the component into the default position
        '''
        for anim in self.getAllAnims():
            resetAttrs(anim)
            
    def connectToComponent(self, comp, location, point=1, orient=1):
        '''
        Connects this componen to a specified component.
        
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        anchorGrp = self.networkNode.anchorGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, anchorGrp, sr=skipRot, st=skipTrans, w=1, mo=1)
        
    def getConnectObj(self, location):
        '''
        Gets the component to connect to at location.
        
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.startHandle.listConnections()[0]
        elif location == 'end':
            return self.networkNode.endHandle.listConnections()[0]
        else: # an object
            if not objExists(location):
                raise Exception("FKIKLimb.getConnectObj: Location %s , doesn't exist"%location)
            location = PyNode(location)
            bindJoints = self.networkNode.bindJoints.listConnections()
            for inc in xrange(len(bindJoints)):# test for a bind joint
                if location == bindJoints[inc]:
                    return bindJoints[inc]
        raise Exception("FKIKLimb.getConnectObj: Location wasn't found. Try 'start', 'end', or name of a bind joint.")
        
    def alignSwitch(self):
        '''
        Align switch between FK and IK taking into account stretching and pinning
        '''
        
        switchAttr = self.getSwitchAttr()
        
        # Load anim references
        ikAnim = self.networkNode.ikAnim.listConnections()[0]
        pvAnim = self.networkNode.pvAnim.listConnections()[0]
        fkAnims = self.networkNode.fkAnims.listConnections()
        
        # Load other useful information
        bindJoints = self.networkNode.bindJoints.listConnections()
        pinAttrName = self.networkNode.pinAttrName.get()
        pinAttr = ikAnim.attr(pinAttrName)
        
        # Determine current bone lengths
        stretchMode = self.networkNode.stretchMode.get()
        
        if (stretchMode == 'translate'):
            fkStretch = self.networkNode.fkStretch.listConnections()[0]
            bone1_origLength = fkStretch.input1Y.get()
            bone2_origLength = fkStretch.input1Z.get()
            bone1_currLength = bindJoints[1].tx.get()
            bone2_currLength = bindJoints[2].tx.get()
        else:
            bone1_origLength = 1
            bone2_origLength = 1
            bone1_currLength = bindJoints[0].sx.get()
            bone2_currLength = bindJoints[1].sx.get()
        
        # Arm stretch states
        hasStretchedSecondBone = (bone2_origLength != bone2_currLength)
        hasStretchedBones = (bone1_origLength != bone1_currLength) or \
                            (bone2_origLength != bone2_currLength)
        
        # Create temporary bind joint locators for stable alignment targets
        bindJointLocs = []
        for bj in bindJoints:
            bjLoc = spaceLocator()
            alignPointOrient(bj, bjLoc, 1, 1)
            bindJointLocs.append(bjLoc)
        
        if switchAttr.get() > .5:
            '''
            IK -> FK switch
            '''

            # Peform normal IK -> FK align switch first
            ikChain = self.networkNode.ikChain.listConnections()
            for i in xrange(3):
                alignPointOrient(bindJointLocs[i], fkAnims[i], 0, 1)
                    
            # Bones are using IK pinning or are stretched out
            if hasStretchedBones:
                fkAnims[0].stretch.set(bone1_currLength/bone1_origLength)
                fkAnims[1].stretch.set(bone2_currLength/bone2_origLength)
            else:
                fkAnims[0].stretch.set(1)
                fkAnims[1].stretch.set(1)
                
            switchAttr.set(0)
            
        else:
            '''
            FK -> IK switch
            '''

            # Stretch attribute used in FK so use IK pinning
            if hasStretchedBones:
                pinAttr.set(1)
                alignPointOrient(bindJointLocs[2], ikAnim, 1, 1)
                alignPointOrient(bindJointLocs[1], pvAnim, 1, 0)
                if hasStretchedSecondBone:
                    ikAnim.stretchy.set(1)
                else:
                    ikAnim.stretchy.set(0)
                    
            # Normal FK -> IK align switch
            else:
                pinAttr.set(0)
                pvLoc = createPVLocator(bindJointLocs[0], bindJointLocs[1], bindJointLocs[2])
                alignPointOrient(bindJointLocs[2], ikAnim, 1, 1)
                alignPointOrient(pvLoc, pvAnim, 1, 0)
                delete(pvLoc)
                
            switchAttr.set(1)
        
        delete(bindJointLocs)
            
            
class FKIKBipedLeg(FKIKLimb):

    def __init__(self, side, bodyPart, startJoint, endJoint, heelLoc, toeLoc, insideLoc, outsideLoc,
                 defaultSwitchValue = 1, stretchMode = 'translate', node=''):
        '''
        side:
            Component side.
            
        bodyPart:
            Specific body part this limb is used for.
        
        startJoint:
            Start of the component's chain.
        
        endJoint:
            End of the component's chain.
            
        defaultSwitchValue:
            Sets the default value of the switcher. 0 is FK, 1 is IK.
            
        stretchMode:
            Determines how the pin and stretch attributes stretch limb segments,
            either through "translate" or "scale".  Scale works well for Classic Linear
            skinning, whereas translate may be required for Dual Quaternion to prevent
            awkward deformations.  Default is translate.
        '''
        
        
        # REQUISITE META SETUP
        
        # If a node is provided, check to see if it is this type of meta component
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'FKIKBipedLeg'):
                    self.networkNode = node
                else:
                    printError("FKIKBipedLeg: node %s is not a FKIKBipedLeg metaNode"%(node))
            else:
                printError("FKIKBipedLeg: node %s doesn't exist"%(node))
            return None # Whatever the case, we're done here
        
        # Initiate the component
        RigComponent.__init__(self, 'FKIKBipedLeg', 1.0, 'FKIKLimb with a foot attached', side, bodyPart)
        compName = '%s_%s'%(side, bodyPart)
        chain = chainBetween(startJoint, endJoint)
        
        # Setup the FKIKLimb structure
        FKIKLimb.setup(self, side, bodyPart, chain[0], chain[2], defaultSwitchValue, stretchMode)
        
        
        
        # IK FOOT SETUP
        
        # Prepare foot pivot structure for SDKs
        ikChain = self.networkNode.ikChain.listConnections()
        footChain = [ikChain[2]]+duplicateChain(chain[3], chain[4], 'bind', 'ik')
        parent(footChain[1], ikChain[2])
        
        heelLoc = PyNode(heelLoc)
        insideLoc = PyNode(insideLoc)
        outsideLoc = PyNode(outsideLoc)
        toeLoc = PyNode(toeLoc)

        heel_piv = duplicate(footChain[2], po=1, n='%s_heel_piv_joint'%compName)[0]
        toe_piv = duplicate(footChain[2], po=1, n='%s_toe_piv_joint'%compName)[0]
        toe_lift_piv = duplicate(footChain[2], po=1, n='%s_toe_lift_piv_joint'%compName)[0]
        toe_fk_piv = duplicate(footChain[2], po=1, n='%s_toe_fk_piv_joint'%compName)[0]
        inside_piv = duplicate(footChain[2], po=1, n='%s_inside_piv_joint'%compName)[0]
        outside_piv = duplicate(footChain[2], po=1, n='%s_outside_piv_joint'%compName)[0]

        parent([heel_piv, toe_piv, toe_lift_piv, toe_fk_piv, inside_piv, outside_piv], w=1)

        alignPointOrient(heelLoc, heel_piv, 1,0)
        alignPointOrient(insideLoc, inside_piv, 1,0)
        alignPointOrient(outsideLoc, outside_piv, 1,0)
        alignPointOrient(toeLoc, toe_piv, 1,0)
        alignPointOrient(footChain[1], toe_lift_piv, 1,0)
        alignPointOrient(footChain[1], toe_fk_piv, 1,0)

        delete(heelLoc, insideLoc, outsideLoc, toeLoc)

        mainIkHandle = self.networkNode.mainIkHandle.listConnections()[0]
        ikAnim_loc = self.networkNode.ikAnim_loc.listConnections()[0]
        ballIkHandle = ikHandle(sj=footChain[0], ee=footChain[1], sol='ikSCsolver', n=compName+'ballIkHandle')[0]
        toeIkHandle = ikHandle(sj=footChain[1], ee=footChain[2], sol='ikSCsolver', n=compName+'toeIkHandle')[0]
        hide(ballIkHandle, toeIkHandle)
        
        # Do custom setup on the foot joints
        '''
        anim
            heel via parent constraint
                outside
                    inside
                        toe
                            toe fk
                                toe ik
                            toe lift
                                foot ik
                                leg ik
        '''
        for a in ['tx', 'ty', 'tz']: ikAnim_loc.attr(a).unlock()
        parent(ballIkHandle, mainIkHandle, ikAnim_loc, toe_lift_piv)
        lockAndHideAttrs(ikAnim_loc, ['t'])
        
        parent(toeIkHandle, toe_fk_piv)
        parent(toe_fk_piv, toe_lift_piv, toe_piv)
        parent(toe_piv, inside_piv)
        parent(inside_piv, outside_piv)
        parent(outside_piv, heel_piv)
        heelPivGrp = group(n=heel_piv.name() + "_grp", em=1)
        delete(parentConstraint(heel_piv, heelPivGrp, mo=0))
        parent(heel_piv, heelPivGrp)
        
        # Note: parent ikAnimLoc to parent of mainIkHandle
        # Modify existing ikAnim with new SDK attributes
        ikAnim = self.networkNode.ikAnim.listConnections()[0]
        
        parent(heelPivGrp, ikAnim)

        # Add the foot's SDK attrs
        for sdkName in ['ballLift', 'sideToSide', 'heelToToe', 'toeWiggle', 'toeSpin', 'ballSpin', 'heelSpin']:
            ikAnim.addAttr(sdkName,   k=1, dv=0, min=-180, max=180)

        # Value that flips the animation on certain set driven attributes
        # based on the side of the character this component is on
        if (side == 'right'):
            flip = -1
        else:
            flip = 1

        # ballLift
        mu.sdk( ikAnim.ballLift, [-180, 180], toe_lift_piv.rz, [180, -180] )
                
        # sideToSide
        mu.sdk( ikAnim.sideToSide, [-180, 0], inside_piv.rx, [flip*180, 0] )
        mu.sdk( ikAnim.sideToSide, [0, 180], outside_piv.rx, [0, -flip*180] )
                
        # heelToToe
        mu.sdk( ikAnim.heelToToe, [-180, 0], toe_piv.rz, [-180, 0] )
        mu.sdk( ikAnim.heelToToe, [0, 180], heel_piv.rz, [0, 180] )
                
        # toeSpin
        mu.sdk( ikAnim.toeSpin, [-180, 180], toe_piv.ry, [-flip*180, flip*180] )

        # ballSpin
        mu.sdk( ikAnim.ballSpin, [-180, 180], inside_piv.ry, [-flip*180, flip*180] )

        # heelSpin
        mu.sdk( ikAnim.heelSpin, [-180, 180], heel_piv.ry, [-flip*180, flip*180] )

        # toeWiggle
        mu.sdk( ikAnim.toeWiggle, [-180, 180], toe_fk_piv.rz, [-180, 180] )
        
        
        # FK TOE/FOOT ADDITIONS
        
        # Load all relevent component nodes
        fkAnims = self.networkNode.fkAnims.listConnections()
        switchOrientConstraints = self.networkNode.switchOrientConstraints.listConnections()
        revSwitchNode = self.networkNode.revSwitchNode.listConnections()[0]
        switchAnim = self.networkNode.switchAnim.listConnections()[0]
        switchAttr = switchAnim.FKIKswitch
        
        # Recreate previous IK foot orient constraint
        delete(switchOrientConstraints[-1])
        del switchOrientConstraints[-1]
        footOrientConstraint = orientConstraint([fkAnims[-1], footChain[0]], chain[2], mo=0)
        
        switchAttr >> footOrientConstraint.w1
        revSwitchNode.outputX >> footOrientConstraint.w0
        
        # Add FK toe anim
        toeFkAnim = duplicateChain(chain[3], chain[3])[0]
        parent(toeFkAnim, fkAnims[-1])

        toeFkAnim.rename(compName + '_4_fk_anim')
        toeFkAnim.drawStyle.set(2)
        addAnimAttr(toeFkAnim)
        
        fkAnimShape = circle(normal=(1,0,0), ch=0)[0]
        appendShape(fkAnimShape, toeFkAnim)
        delete(fkAnimShape)
    
        lockAndHideAttrs(toeFkAnim, ['rx', 'ry', 't', 's', 'v', 'radius'])
        
        toeRotateBlend = createNode('blendColors', n=compName+'_rotate_3_blend')
        toeFkAnim.rotate >> toeRotateBlend.color2
        footChain[1].rotate >> toeRotateBlend.color1
        toeRotateBlend.output >> PyNode(chain[3]).rotate
        switchAttr >> toeRotateBlend.blender
        
        
        # SET UP META NODES
        
        anims = self.getAllAnims()
        
        # Update existing meta attributes
        connectChainToMeta(chain, self.networkNode, 'bindJoints')
        connectChainToMeta(anims+[toeFkAnim], self.networkNode, 'anims')
        connectChainToMeta(fkAnims+[toeFkAnim], self.networkNode, 'fkAnims')
        connectChainToMeta(ikChain+footChain[1:], self.networkNode, 'ikChain')
        connectChainToMeta(switchOrientConstraints+[footOrientConstraint], self.networkNode, 'switchOrientConstraints')
        
        
    def alignSwitch(self):
        '''
        Align switch between FK and IK taking into account stretching and pinning
        '''
        
        switchOldValue = self.getSwitchAttr().get()
        toeRzOldValue = self.networkNode.listConnections()[4].rz.get()
        
        # Handle most of the align switch with the limb logic
        FKIKLimb.alignSwitch(self)
        
        # Load toe anim info
        ikAnim = self.networkNode.ikAnim.listConnections()[0]
        toeWiggleAttr = ikAnim.toeWiggle
        toeWiggleAttr.unlock()
        
        toeFkAnim = self.networkNode.fkAnims.listConnections()[3]
        toeFkAnim.rz.unlock()
        
        # Update the toe
        if switchOldValue > .5:
            '''
            IK -> FK switch
            '''

            toeFkAnim.rz.set(toeRzOldValue)

        else:
            '''
            FK -> IK switch
            '''

            for a in ['ballLift', 'sideToSide', 'heelToToe', 'toeWiggle', 'toeSpin', 'ballSpin', 'heelSpin']:
                ikAnim.attr(a).unlock()
                ikAnim.attr(a).set(0)
                
            wiggleValue = (toeFkAnim.rz.get())%360.0
            if wiggleValue > 180:
                wiggleValue += -360
            elif wiggleValue < -180:
                wiggleValue += 360
            
            toeWiggleAttr.set(wiggleValue)
        
        
class StretchyJointChain(RigComponent):
    def __init__(self, startDistance, endDistance, side, bodyPart, startJoint, endJoint,node = None):
        '''
        numSegments:
            the number of segments to split chain, animCount = numSegments - 1
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'StretchyJointChain'):
                    self.networkNode = node
                else:
                    printError("StretchyJointChain: node %s is not a StretchyJointChain metaNode"%(node))
            else:
                printError("StretchyJointChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'StretchyJointChain', 1.0, 'a foot rig, with many types of movement', side, bodyPart, startJoint, endJoint)
            compName = '%s_%s'%(side, bodyPart)
            
            chain = chainBetween(startJoint, endJoint)
            numSegments = len(chain)-2
            
            #create control joints
            controlJoints = duplicateChain(startJoint, endJoint, 'bind', 'control')
            controlJoints = map(lambda x: PyNode(x), controlJoints)
            bindJoints = chainBetween(startJoint, endJoint)
            bindJoints = map(lambda x: PyNode(x), bindJoints)
            transformJoints = duplicateChain(startJoint, endJoint, 'bind','transform')
            
                #rename
            for x in xrange(len(controlJoints)):
                controlJoints[x].rename("%s_%i_control_joint"%(compName, x+1))
            
            #create distances
            startLoc = spaceLocator(p=(0,0,0))
            endLoc = spaceLocator(p=(0,1,0))
            currentLength = PyNode(distanceDimension(sp = (0,0,0), ep = (0,1,0)))
            alignPointOrient(startDistance, startLoc, 1, 1)
            alignPointOrient(endDistance, endLoc, 1,1)
            parentConstraint(startDistance, startLoc, mo=0, w=1)
            parentConstraint(endDistance, endLoc, mo=0, w=1)
            parentConstraint(startJoint, transformJoints[0], mo=1,w=1)
            origTotal = 0
            for t in transformJoints[1:]:
                origTotal += t.translateX.get()
            oldRatio = 0
            for t in transformJoints[1:]: 
                #get transslate to move with stretchy
                ratioMulti = createNode('multiplyDivide') #startjointDist/ origTotalDistance
                ratioMulti.operation.set(2)
                ratioMulti.input2X.set(origTotal)
                ratioMulti.input1X.set(abs(t.translateX.get()))
                outputMulti = createNode('multiplyDivide')
                ratioMulti.outputX >> outputMulti.input1X
                currentLength.distance >> outputMulti.input2X
                outputMulti.outputX >> t.translateX
                #gets rotate to smooth rotations
                ratio = abs(ratioMulti.outputX.get())+oldRatio
                print ratio
                revRatio = 1-ratio
                if revRatio < 0:
                    revRatio = 0
                orConst = PyNode(orientConstraint([startDistance, endDistance], t,skip=('z',"y"), mo=0))
                orConst.w0.set(revRatio)
                orConst.w1.set(ratio)
                oldRatio += abs(ratioMulti.outputX.get())
                
                
            #create anims
            zeroGrps =[]
            anims = []
            for num in xrange(numSegments):
                select(clear=1)
                anim = joint(n = '%s_anim_%i'%(compName,num+1))
                alignPointOrient(controlJoints[num+1], anim, 1,1)
                zeroGrp = createZeroedOutGrp(anim)
                addAnimAttr(anim)
                cube = polyCube()[0]
                appendShape(cube, anim)
                delete(cube)
                lockAndHideAttrs(anim, [ 'v', 'radius', 'sx', 'sy', 'sz'])
                anims.append(anim)
                zeroGrps.append(zeroGrp)
            
            #connectDistances
            for num in xrange(numSegments):
                pointConstraint(transformJoints[num+1], zeroGrps[num], mo =1)
                orientConstraint(transformJoints[num+1], zeroGrps[num], mo =1)
            
            #connect anims
            for x in xrange(numSegments):
                parentConstraint(anims[x],controlJoints[x+1], w=1, mo=1)
            
            #connect bindJoints
            for x in xrange(len(controlJoints)-1):
                parentConstraint(controlJoints[x], bindJoints[x], w=1, mo=1)
            
            #grouping
            select(cl=1)
            jointGrp = group([controlJoints[0], transformJoints[0]],n='%s_joint_grp'%compName)
            animGrp = group([zeroGrps], n = "%s_anim_grp"%compName)
            dntGrp = group([startLoc, endLoc,currentLength], n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            
            #hide
            dntGrp.hide()
            jointGrp.hide()
            
            #connectToMeta
            connectChainToMeta(bindJoints, self.networkNode, 'bindJoints')
            connectChainToMeta(controlJoints, self.networkNode, 'controlJoints')
            connectChainToMeta(anims, self.networkNode, 'anims')
            connectToMeta(dntGrp, self.networkNode, 'dntGrp')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            pass
        else:
            thisAnims = self.getAllAnims()
            otherAnims = other.getAllAnims()
            if bothSides: #copy over from other side, then copy this side to that side
                for x in xrange(len(otherAnims)):
                    #get
                    otherAnim = otherAnims[x]
                    otherTrans = otherAnim.translate.get()
                    otherRotate = otherAnim.rotate.get()
                    thisAnim = thisAnims[x]
                    thisTrans = thisAnim.translate.get()
                    thisRotate = thisAnim.rotate.get()
                    
                    #set
                    thisAnim.translate.set(otherTrans[0], otherTrans[1], -otherTrans[2])
                    thisAnim.rotate.set(-otherRotate[0], -otherRotate[1], otherRotate[2])
                    otherAnim.translate.set(thisTrans[0], thisTrans[1], -thisTrans[2])
                    otherAnim.rotate.set(-thisRotate[0], -thisRotate[1], thisRotate[2])
                return [self, other]
            else:# just copy over from other side
                for x in xrange(len(otherAnims)):
                    otherTrans = otherAnims[x].translate.get()
                    otherRotate = otherAnims[x].rotate.get()
                    thisAnim = thisAnims[x]
                    thisAnim.translate.set(otherTrans[0], otherTrans[1], -otherTrans[2])
                    thisAnim.rotate.set(-otherRotate[0], -otherRotate[1], otherRotate[2])
                return [self]    
                
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        raise Exception("can't connect to this component getConnectObj() not implemented, %s"%self.networkNode.metaType.get())
            
    def getBindJoints(self):
        '''
        return the joints which should be bound to
        '''
        try:
            return self.networkNode.bindJoints.listConnections()[1:-1]
        except:
            return None 
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return self.networkNode.anims.listConnections()
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''            
        anims = self.getAllAnims()
        for anim in anims:
            anim.translate.set([0,0,0])
            anim.rotate.set([0,0,0])
                        
class AdvancedFoot(RigComponent):
    def __init__(self, heelJoint, toeJoint, insideJoint, outsideJoint, side, bodyPart, startJoint, endJoint, node = None):
        '''
        heelJoints:
            a joint placed at the heel location
        toeJoint:
            a joint placed at the toe of the character
        outisdeJoint:
            a joint placed on the outside of the foot, side of foot farthest from other body center
        insideJoint:
            a joint placed on the inside of the foot, side of foot closest to the body center
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'AdvancedFoot'):
                    self.networkNode = node
                else:
                    printError("AdvancedFoot: node %s is not a AdvancedFoot metaNode"%(node))
            else:
                printError("AdvancedFoot: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'AdvancedFoot', 1.0, 'a foot rig, with many types of movement', side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            compName = '%s_%s'%(side, bodyPart)
            for item in chain:
                item  = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
            
            #test pivot joints
            if not objExists(heelJoint):
                raise Exception("AdvanceFoot.__init__: obj given as heelJoint, %s, doesn't exist"%heelJoint)        
            if not objExists(toeJoint):
                raise Exception("AdvanceFoot.__init__: obj given as toeJoint, %s, doesn't exist"%toeJoint)
            if not objExists(insideJoint):
                raise Exception("AdvanceFoot.__init__: obj given as insideJoint, %s, doesn't exist"%insideJoint)
            if not objExists(outsideJoint):
                raise Exception("AdvanceFoot.__init__: obj given as outsideJoint, %s, doesn't exist"%outsideJoint)
                
            #make pivot joints PyNodes
            heelJoint = PyNode(heelJoint)
            toeJoint = PyNode(toeJoint)
            insideJoint = PyNode(insideJoint)
            outsideJoint = PyNode(outsideJoint)
                    
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')

            #create iks
            foot_ik = ikHandle( sj= control_joints[0], ee = control_joints[1], sol ='ikSCsolver')[0]
            ball_ik = ikHandle( sj= control_joints[1], ee = control_joints[-1], sol ='ikSCsolver')[0]
            
            #create ball and wiggle joints
            select(cl=1)
            ballJoint = duplicate(control_joints[1], n = '%s_ball_joint'%compName)[0]
            delete(ballJoint.getChildren())
            select(cl=1)
            wiggleJoint = duplicate(control_joints[1], n = '%s_wiggle_joint'%compName)[0]
            delete(ballJoint.getChildren())
            
            #orient pivot joints to foot ball to match rotation
            for x in [heelJoint, toeJoint, insideJoint, outsideJoint, ballJoint, wiggleJoint]:
                alignPointOrient(control_joints[1], x, 0, 1)
                makeIdentity(x,apply = 1, t=0,r=1, s=1,n=0)
            
            #create Anim
            select(clear=1)
            anim = joint(n = '%s_anim'%compName)
            alignPointOrient(startJoint, anim, 1,1)
            zeroGrp = createZeroedOutGrp(anim)
            addAnimAttr(anim)
            cube = polyCube()[0]
            appendShape(cube, anim)
            delete(cube)
            lockAndHideAttrs(anim, ['tx','ty', 'tz', 'v', 'radius', 'sx', 'sy', 'sz'])
            
            #create attrs on anim
            anim.addAttr('roll', keyable=1,dv =0)
            anim.addAttr('toeLift',  keyable=1,dv = 15)
            anim.addAttr('toeStraight',  keyable=1,dv = 50)
            anim.addAttr('lean',  keyable=1,dv = 0)
            anim.addAttr('tilt', keyable=1, dv = 0)
            anim.addAttr('toeSpin',  keyable=1, dv = 0)
            anim.addAttr('toeWiggle', keyable=1, dv = 0)
            anim.addAttr('heelSpin',  keyable=1,dv = 0)
            
            #parenting
            anim | heelJoint
            heelJoint | toeJoint
            toeJoint | outsideJoint
            outsideJoint | insideJoint
            insideJoint | ballJoint
            ballJoint | wiggleJoint
            wiggleJoint | ball_ik
            insideJoint | foot_ik
            
            exprStr = '''
                $roll = %s.roll;
                $toeLift = %s.toeLift;
                $toeStraight = %s.toeStraight;
                $lean = %s.lean;
                $side = %s.tilt;
                $toeSpin = %s.toeSpin;
                $wiggle = %s.toeWiggle;
                $heelSpin = %s.heelSpin;
                
                %s.rotateZ = max(-$roll,0);
                %s.rotateZ = (linstep(0, $toeLift,$roll)) * (1-(linstep($toeLift, $toeStraight, $roll))) * -$roll;
                %s.rotateZ = linstep($toeLift, $toeStraight, $roll) * -$roll;
                %s.rotateX = -$lean;
                %s.rotateX = min(-$side,0);
                %s.rotateX = max(-$side,0);
                
                %s.rotateY = -$toeSpin;
                %s.rotateZ = $wiggle + (linstep(0, $toeLift,$roll)) * (1-(linstep($toeLift, $toeStraight, $roll))) * $roll;
                %s.rotateY = $heelSpin;
            '''%(anim, anim, anim, anim, anim, anim, anim, anim, heelJoint, ballJoint, toeJoint, ballJoint, outsideJoint, insideJoint, toeJoint, wiggleJoint, heelJoint)
            
            
            expr = expression(s=exprStr, n = '%s_expression'%compName,ae=1, uc='all')
            
            #bindJoints
            for j in xrange(len(bind_joints)-1):
                parentConstraint(control_joints[j], bind_joints[j], w=1, mo=1)
            
            #grouping
            select(cl=1)
            jointGrp = group([control_joints[0]],n='%s_joint_grp'%compName)
            animGrp = group([zeroGrp], n = "%s_anim_grp"%compName)
            dntGrp = group(empty = 1, n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            #hide
            dntGrp.hide()
            control_joints[0].hide()
            heelJoint.hide()
            
            #connectToMeta
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectToMeta(foot_ik, self.networkNode, 'footIK')
            connectToMeta(ball_ik, self.networkNode, 'ballIK')
            connectToMeta(heelJoint, self.networkNode, 'heelJoint')
            connectToMeta(toeJoint, self.networkNode, 'toeJoint')
            connectToMeta(insideJoint, self.networkNode, 'insideJoint')
            connectToMeta(outsideJoint, self.networkNode, 'outsideJoint')
            connectToMeta(ballJoint, self.networkNode, 'ballJoint')
            connectToMeta(wiggleJoint, self.networkNode, 'wiggleJoint')
            connectToMeta(anim, self.networkNode, 'anim')
            connectToMeta(dntGrp, self.networkNode, 'dntGrp')
            connectToMeta(zeroGrp, self.networkNode, 'zeroAnimGrp')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
                    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        
        #############################################################################3
        ## WARNING CURRENTLY ONLY ABLE TO HANDLE CONNECTING TO FKIKCHAINS
        ##############################################################################
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        scaleConstraint(obj, mainGrp, w=1, mo = 1)
        
        if comp.isIK():
            ikHandle = comp.getIK()
            zeroGrp = self.networkNode.zeroAnimGrp.listConnections()[0]
            zeroGrp.inheritsTransform.set(0)
            parentConstraint(self.networkNode.ballJoint.listConnections()[0], ikHandle, w=1, mo=1)            
            
            ## FKIKChain only
            ikLoc = spaceLocator()
            fkLoc = spaceLocator()
            ik = comp.networkNode.ikAnim.listConnections()[0]
            fk = comp.networkNode.FKJoints.listConnections()[-1]
            pointConstraint(ik, ikLoc, w=1, mo=0)
            pointConstraint(fk, fkLoc, w=1, mo=0)
            ikLoc.inheritsTransform.set(0)
            fkLoc.inheritsTransform.set(0)
            dntGrp = self.networkNode.dntGrp.listConnections()[0]
            parent(ikLoc, fkLoc, dntGrp)
            switch = comp.networkNode.switchGroup.listConnections()[0]
            switchAttr = switch.attr(comp.networkNode.switchAttr.get())
            
            const = parentConstraint([fkLoc, ikLoc], zeroGrp, w=1, mo=1)
            switchAttr >> const.w1
            rev = createNode('reverse')
            switchAttr >> rev.inputX
            rev.outputX >> const.w0
            lockAndHideAttrs(ik, ['rx', 'ry','rz'])
            
            #parentConstraint(obj, zeroGrp, w=1, mo=1)
        
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("AdvancedFoot.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.FKJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
        raise Exception("AdvancedFoot.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or control joint ")    
    
    def getAnim(self):
        '''
        returns the anim with all the rotation information
        '''    
        return self.networkNode.anim.listConnections()[0]
    
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        return [self.getAnim()]
        
    def toDefaultPose(self):
        '''
        moves the component into the bind position
        '''        
        resetAttrs(self.getAnim())    
            
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        character = self.getCharacterRig()
        other = character.getOppositeComponent(self)
        if other == self:
            anim = self.getAnim()
            anim.rotateX.set(anim.rotateX.get()*-1)
            anim.rotateY.set(anim.rotateY.get()*-1)
            return [self]
        else:
            anim = self.getAnim()
            attrs = anim.listAttr(keyable = 1)
            attrValue = {}
            attrs = map(lambda x: x.name().split(".")[-1], attrs)
            for x in attrs:
                attrValue[x] = anim.attr(x).get()
            otherAnim = other.getAnim()
            otherAttrs = otherAnim.listAttr(keyable = 1)
            otherAttrs = map(lambda x: x.name().split(".")[-1], otherAttrs)
            otherAttrValue = {}    
            for x in otherAttrs:
                otherAttrValue[x] = otherAnim.attr(x).get()
            if bothSides:
                for attr in attrs:
                    otherAnim.attr(attr).set(attrValue[attr])
                for attr in otherAttrs:
                    anim.attr(attr).set(otherAttrValue[attr])
                return [self, other]
            else:
                for attr in otherAttrs:
                    anim.attr(attr).set(otherAttrValue[attr])
            return [self]
        
class DynamicChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node = ''):
        '''
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'DynamicChain'):
                    self.networkNode = node
                else:
                    printError("DynamicChain: node %s is not a DynamicChain metaNode"%(node))
            else:
                printError("DynamicChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'DynamicChain', 1.0, 'a joint chain which is influenced by Dynamics',side, bodyPart, startJoint, endJoint)
            chain = chainBetween(startJoint, endJoint)
            bind_joints = []
            compName = '%s_%s'%(side, bodyPart)
            for item in chain:
                item  = PyNode(item)
                if item.type() == 'joint':
                    bind_joints.append(item)
            
            #create Joint chains
            dyn_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'dynamic')
            control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
            fk_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'dynFK')
                    
            #create dynamic system
            origCurve = self.createCurveThroughObjects(bind_joints, degree=3)
            origCurve.rename('%s_orig_curve'%compName)
            
            select(origCurve, r=1)
            rt.MakeCurvesDynamic(1, 0,1)
            follicle = listConnections(origCurve.getShape().worldSpace[0])[0]
            follicle.rename('%s_follicle'%compName)
            hair = listConnections(follicle.outHair)[0]
            hair.rename('%s_hair_system'%compName)
            dynCurve = listConnections(follicle.outCurve)[0]
            
            dynCurve.rename('%s_dyn_curve'%compName)
            origCurve.inheritsTransform.set(0)
            b = dynCurve.getParent()
            parent(dynCurve, w=1)
            delete(b);
            
            #create anim 
            select(cl=1)
            animJoint = joint(n = '%s_dyn_anim'%compName)
            addAnimAttr(animJoint)
            p = polySphere()[0]
            appendShape(p, animJoint)
            delete(p) 
            alignPointOrient(dyn_joints[-1], animJoint, 1,1)
            pointConstraint(dyn_joints[-1], animJoint, mo=1, w=1)
            zeroGrp = createZeroedOutGrp(animJoint)
            
            
            #add attrs to anim
            animJoint.addAttr('enable', min = 0, max =1, dv = 1, keyable = 0)
            animJoint.enable.set(channelBox=1)
            animJoint.addAttr('stiff', min =0 , max =1 , dv =.001, keyable =1)
            animJoint.addAttr('lengthFlex', min =0 , max =1 , dv =0, keyable =1)
            animJoint.addAttr('damping', min =0 , max =100 , dv =0, keyable =1)
            animJoint.addAttr('drag', min =0 , max =1 , dv =.5, keyable =1)
            animJoint.addAttr('friction', min =0 , max =1 , dv =.5, keyable =1)
            animJoint.addAttr('gravity', min =0 , max =10 , dv =1, keyable =1)
            animJoint.addAttr('turbulenceCtrl', at = 'bool', keyable =1)
            animJoint.turbulenceCtrl.lock()
            animJoint.addAttr('strength', min =0 , max =1 , dv =0, keyable =1)
            animJoint.addAttr('frequency', min =0 , max =2 , dv =.2, keyable =1)
            animJoint.addAttr('speed', min =0 , max =2 , dv =.2, keyable =1)
    
            #set enable/disable
            animJoint.enable.set(0)
            follicle.getShape().simulationMethod.set(0)
            setDrivenKeyframe(follicle.getShape().simulationMethod,cd = animJoint.enable)
            animJoint.enable.set(1)
            follicle.getShape().simulationMethod.set(2)
            setDrivenKeyframe(follicle.getShape().simulationMethod,cd = animJoint.enable)
            
            #connect up dynamics
            follicle.overrideDynamics.set(1)
            follicle.pointLock.set(1)
            animJoint.stiff >> follicle.stiffness
            animJoint.lengthFlex >> follicle.lengthFlex
            animJoint.damping >> follicle.damp
            animJoint.drag >> hair.drag
            animJoint.friction >> hair.friction
            animJoint.gravity >> hair.gravity
            animJoint.strength >> hair.turbulenceStrength
            animJoint.frequency >> hair.turbulenceFrequency
            animJoint.speed >> hair.turbulenceSpeed
            
            lockAndHideAttrs(animJoint, ['tx','ty','tz','rx','ry','rz','sx','sy','sz', 'radius'])
            animJoint.v.set(keyable = 0)
            
            #create ik spline
            b = ikHandle(c = dynCurve, startJoint = dyn_joints[0], endEffector = dyn_joints[-1], sol = 'ikSplineSolver', w=1, ccv=0)
            ik = b[0]
            ik.rename('%s_ik_curve'%compName)
            eff = b[1]
            
            #switch Grp
            switchGrp = group(empty = 1, n =  "%s_switch_grp"%compName)
            switchGrp.addAttr('fk_dyn_switch', min = 0, max =1, dv = 1)
            
            rev = createNode('reverse')
            switchGrp.fk_dyn_switch >> rev.inputX
            
            #create fk anims
            for inc in xrange(len(fk_joints)-1):
                obj = fk_joints[inc]
                addBoxToJoint(obj)
                lockAndHideAttrs(obj, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius'])
                obj.v.set(keyable = 0)
                addAnimAttr(obj)
                obj.rename('%s_%s_%i_anim'%(getJointLabels(obj)[0], getJointLabels(obj)[1], inc))
            
            #connect to control joints
            for inc in xrange(len(control_joints)):
                const = parentConstraint([fk_joints[inc], dyn_joints[inc]], control_joints[inc], mo=1, w=1)
                switchGrp.fk_dyn_switch >> const.w1
                rev.outputX >> const.w0    
                        
            #connect to bind joints
            for inc in xrange(len(bind_joints)-1):
                parentConstraint(control_joints[inc], bind_joints[inc], mo=1, w=1)
            
            #grouping
            select(cl=1)
            jointGrp = group([fk_joints[0], control_joints[0], dyn_joints[0]],n='%s_joint_grp'%compName)
            animGrp = group([zeroGrp], n = "%s_anim_grp"%compName)
            dntGrp = group([switchGrp, dynCurve, ik, hair, follicle.getParent()], n = "%s_DO_NOT_TOUCH_grp"%compName)
            mainGrp = group([jointGrp, animGrp, dntGrp],n = "%s_component_group"%compName)
            xform(mainGrp, piv = bind_joints[0].getTranslation(space = 'world'), ws=1)
            
            #hide
            dntGrp.hide()
            control_joints[0].hide()
            rev.outputX >> fk_joints[0].v
            switchGrp.fk_dyn_switch >> zeroGrp.v
            switchGrp.fk_dyn_switch >> dyn_joints[0].v
            
            #connectToMeta
            connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
            connectChainToMeta(dyn_joints, self.networkNode, 'dynamicJoints')
            connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
            connectChainToMeta(fk_joints, self.networkNode, 'FKJoints')
            connectToMeta(follicle, self.networkNode, 'follicle')
            connectToMeta(hair, self.networkNode, 'hair')
            connectToMeta(animJoint, self.networkNode, 'dynAnim')
            connectToMeta(switchGrp, self.networkNode, 'switchGroup')        
            self.networkNode.setAttr('switchAttr', 'fk_dyn_switch',  f=1)
            connectToMeta(origCurve, self.networkNode, 'originalCurve')
            connectToMeta(dynCurve, self.networkNode, 'dynamicCurve')
            connectToMeta(mainGrp, self.networkNode, 'componentGrp')
            
    def collideWith(self, objects):
        '''
        make dynamic chain collide with obj(s)
        '''
        hair = listConnections(self.networkNode.hair)[0].getShape()
        time = PyNode('time1')
        
        #make objects into a list
        if not type(objects) is list or not type(objects) is tuple:
            objects = [objects]
        
        for obj in objects:
            
            #test obj
            if not objExists(obj):
                raise Exception("DynamicChain.collideWith: obj given, %s, doesn't exist"%obj)
            obj = PyNode(obj)
            shape = obj.getShape()
            geoLink = createNode('geoConnector')
            
            #connect shape to connector
            shape.message >> geoLink.owner
            shape.worldMatrix[0] >> geoLink.worldMatrix
            shape.outMesh >> geoLink.localGeometry
            connectAttr(geoLink.resilience, hair.collisionResilience, na =1)
            connectAttr(geoLink.friction, hair.collisionFriction, na=1)
            connectAttr(geoLink.sweptGeometry, hair.collisionGeometry, na=1)
            time.outTime >> geoLink.currentTime
        
    def bake(self):
        '''
        bakes the dynamic chain into a fk joint chain for further animation
        '''
        #get variables from node
        fk_joints = listConnections(self.networkNode.FKJoints)
        dyn_joints = listConnections(self.networkNode.dynamicJoints)
        switchGrp = self.networkNode.switchGroup.listConnections()[0]
        switchAttr = switchGrp.attr(self.networkNode.switchAttr.get())
        dynAnim = self.networkNode.dynAnim.listConnections()[0]
        
        #create orientConstraints
        consts = []
        
        for inc in xrange(len(fk_joints)):
            const = orientConstraint(dyn_joints[inc], fk_joints[inc], w=1, mo=0)
            consts.append(const)
            
        #bake the fk_joints
        startTime = playbackOptions(min=1, q=1)
        endTime = playbackOptions(max=1, q=1)
        bakeResults ( fk_joints,simulation=1, t=(startTime,endTime), sb=1, at=["rx","ry","rz"], hi="none")
    
        #delete constraints
        map(lambda x: delete(x), consts)
        
        #switch to the fk joints
        switchAttr.set(0)
        
        #disable dyn Joints
        dynAnim.enable.set(0)
        
    def unbake(self):
        '''
        if baked, then will turn delete keys on fk chain and turn to dynamic chain
        '''
        #get variables from node
        fk_joints = listConnections(self.networkNode.FKJoints)
        dyn_joints = listConnections(self.networkNode.dynamicJoints)
        switchGrp = self.networkNode.switchGroup.listConnections()[0]
        switchAttr = switchGrp.attr(self.networkNode.switchAttr.get())
        dynAnim = self.networkNode.dynAnim.listConnections()[0]
        
        #delete all keys on fk_joints
        startTime = playbackOptions(min=1, q=1)
        endTime = playbackOptions(max=1, q=1)
        for j in fk_joints:
            cutKey(j, animation = 'objects' ,clear=1)
        
        #switch to the fk joints
        switchAttr.set(1)
        
        #disable dyn Joints
        dynAnim.enable.set(1)
            
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []    
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        #scaleConstraint(obj, mainGrp, w=1, mo = 1)
            
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("DynamicChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            fk_joints = self.networkNode.FKJoints.listConnections()
            dyn_joints = self.networkNode.dynamicJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
                if location == fk_joints[inc]:
                    return control_joints[inc]
                if location == dyn_joints[inc]:
                    return control_joints[inc]
        raise Exception("DynamicChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind ,fk, ik, or control joint ")
    
        
    def isFK(self):
        return True
        
    def getAllAnims(self):
        return [self.getDynamicAnim()]
        
    def getDynamicAnim(self):
        '''
        returns the anim that controls the dynamics
        '''
        return self.networkNode.dynAnim.listConnections()[0]
        
    def mirror(self, bothSides = 0):
        '''
        mirrors the component
        bothSides:
             if True, mirrors the others side as well
        return a list components Mirrored
        '''
        return [self]
        
        
    def getFKAnims(self):
        '''
        returns all the FK anims, used when dynamic is baked
        '''
        return self.networkNode.FKJoints.listConnections()[:-1]
        
class MultiConstraint(MetaNode):
    def __init__(self, control, targets, translate = True, rotate = True, node=None):
        '''
        control:
            the child of the constraint
        targets:
            the parents in the relationship
        translate:
            whether or not to constrain translate
        rotate:
            where or not to constrain rotation
            
        example use (first select control then select all desired targets):
            x = MultiConstraint(ls(sl=True)[0], ls(sl=True)[1:len(ls(sl=True))])
        
        note: if looking for the old implementation of MultiConstraint, refer to
        metaCore from previous productions
        '''
        
        self.translate = translate
        self.rotate = rotate
        
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'MultiConstraint'):
                    self.networkNode = node
                else:
                    printError("MultiConstraint: node %s is not a MultiConstraint metaNode"%(node))
            else:
                printError("MultiConstraint: node %s doesn't exist"%(node))
            
        else:
            MetaNode.__init__(self, 'MultiConstraint', 1.0, 'creates multi parents on obj with easy switch ability')
            self.create(control, targets)
            self.networkNode.addAttr('translateBool', at="bool", k=0, dv=self.translate)
            self.networkNode.addAttr('rotateBool', at="bool", k=0, dv=self.rotate)
            self.networkNode.attr('translateBool').setLocked(1)
            self.networkNode.attr('rotateBool').setLocked(1)
            char = getMetaRoot(control, 'CharacterRig')
            connectToMeta(self.networkNode, char.networkNode, 'utilComponents')
            
    def create(self, control, targets):
        '''
        control:
            the child of the constraint
        targets:
            the parents in the relationship
        '''
        
        #creates null transform that will be constrained
        ctrlParent = listRelatives(control, p=True, pa=True)
        nullTransform = group(em=True, name = "t_" + control)
        alignPointOrient(control, nullTransform, 1, 0)
        if len(ctrlParent) != 0:
            parent(nullTransform, ctrlParent)
        parent(control, nullTransform)
        
        nullParent = listRelatives(nullTransform, p=True)
        zeroGrp = group(em=True, name = control + "_zeroGrp")
        connectToMeta(zeroGrp, self.networkNode, 'zeroGrp')
        prtCst = parentConstraint(control, zeroGrp, mo=0)
        delete(prtCst)
        parent(zeroGrp, nullTransform)
        makeIdentity(zeroGrp, a=1, r=1, t=1)
        parent(control, zeroGrp)
        
        origLoc = spaceLocator()
        ptCt = pointConstraint(zeroGrp, origLoc, mo=False)
        orCt = orientConstraint(zeroGrp, origLoc, mo=False)
        delete(ptCt)
        delete(orCt)
        
        self.networkNode.setAttr('origLoc', origLoc.translate.get(), f=1)
        self.networkNode.setAttr('origRot', origLoc.rotate.get(), f=1)
        
        #create enum attribute on control to switch between targets
        enumStr = ""
        for target in targets:
            enumStr = enumStr + mu.getBaseName(target) +":"
        control.addAttr('multiSwitch', at="enum", enumName=enumStr, k=True)
              
        connectToMeta(nullTransform, self.networkNode, 'nullTransform')
        
        if self.translate:
            offsetStoreTran = createNode('plusMinusAverage', n=control + "_offsetStoreTran")
            connectToMeta(offsetStoreTran, self.networkNode, 'offsetStoreTran')
        if self.rotate:
            offsetStoreRot = createNode('plusMinusAverage', n=control + "_offsetStoreRot")
            connectToMeta(offsetStoreRot, self.networkNode, 'offsetStoreRot')
        
        for target in targets:
            self.addTarget(control, target)
        
        if self.translate:
            connectAttr(offsetStoreTran.output3D, zeroGrp.translate, f=True)
        if self.rotate:
            connectAttr(offsetStoreRot.output3D, zeroGrp.rotate, f=True)
            
        #locks attributes of the previously created null transform
        for att in listAttr(nullTransform, k=True):
            nullTransform.attr(att).setLocked(True)
        
        lockedAttr = []
        for trns in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            if control.attr(trns).isLocked():
                control.attr(trns).setLocked(False)
                lockedAttr.append(trns)
               
        for att in lockedAttr:
            control.attr(att).setLocked(True)
        
        delete(origLoc)
           
        connectToMeta(control, self.networkNode, 'control')
        
    def addTarget(self, control, targets):
        '''
        creates switch to be controlled by the previously created enum attribute
        only supports adding one at a time
         
        control:
            the child of the constraint
        targets:
            the parents in the relationship
        
        example to add to existing multiconstraint(select control then target):
            x.addTarget(ls(sl=True)[0], ls(sl=True)[1])
        '''
        
        autoKey = False
        if autoKeyframe(q=True, state=True):
            autoKeyframe(e=True, state=False)
            autoKey = True
        
        origLoc = spaceLocator()
        origLoc.translate.set(self.networkNode.origLoc.get())
        origLoc.rotate.set(self.networkNode.origRot.get())
        
        #caches locked attributes and unlocks them
        #used to lock them again after creating constraints
        lockedAttr = []
        for trns in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            if control.attr(trns).isLocked():
                control.attr(trns).setLocked(False)
                lockedAttr.append(trns)

        nullTransform = self.networkNode.nullTransform.listConnections()[0]
        zeroGrp = self.networkNode.zeroGrp.listConnections()[0]
        
        offsetTran = 0
        offsetRot = 0
        
        if self.translate:
            offsetStoreTran = self.networkNode.offsetStoreTran.listConnections()[0]
        if self.rotate:
            offsetStoreRot = self.networkNode.offsetStoreRot.listConnections()[0]
        
        multRotNode = createNode('multiplyDivide', n=control + "_multRot_" + targets)
        multTranNode = createNode('multiplyDivide', n=control + "_multTran_" + targets)
        
        #creates constraints
        if self.translate:
            trnParent = pointConstraint(targets, nullTransform, mo=True, w=0, n="pConstTranslate_" + control)
            connectToMeta(trnParent, self.networkNode, 'pointConstraint')

        if self.rotate:
            rtParent = orientConstraint(targets, nullTransform, mo=True, w=0, n="pConstRotate_" + control)
            connectToMeta(rtParent, self.networkNode, 'orientConstraint')
   
        numTargets = 0
        
        if self.translate:
            numTargets = len(pointConstraint(trnParent, q=True, wal=True))
        
        if self.rotate:
            numTargets = len(orientConstraint(rtParent, q=True, wal=True))
        
        condNode = createNode('condition', n=control + "_condition_" + targets)
        condNode.firstTerm.set(0)
        condNode.secondTerm.set(numTargets - 1)
        for att in ['colorIfTrueR', 'colorIfTrueG', 'colorIfTrueB']:
            condNode.attr(att).set(1)
        for att in ['colorIfFalseR', 'colorIfFalseG', 'colorIfFalseB']:
            condNode.attr(att).set(0)
            
        connectAttr(control.multiSwitch, condNode.firstTerm, f=True)
        
        if self.translate:
            ptWeightsLs = pointConstraint(trnParent, q=True, wal=True)        
            for weight in ptWeightsLs:
                if str(targets) in str(weight):
                    connectAttr(condNode.outColorR, PyNode(trnParent + '.' + weight),f=True)
            connectAttr(condNode.outColorR, multTranNode.input2X ,f=True)
            connectAttr(condNode.outColorR, multTranNode.input2Y ,f=True)
            connectAttr(condNode.outColorR, multTranNode.input2Z ,f=True)
            connectAttr(multTranNode.outputX, PyNode(str(offsetStoreTran) + '.input3D[' + str(numTargets -1) + '].input3Dx'), f=True)
            connectAttr(multTranNode.outputY, PyNode(str(offsetStoreTran) + '.input3D[' + str(numTargets -1) + '].input3Dy'), f=True)
            connectAttr(multTranNode.outputZ, PyNode(str(offsetStoreTran) + '.input3D[' + str(numTargets -1) + '].input3Dz'), f=True)
        
        if self.rotate:
            orWeightsLs = orientConstraint(rtParent, q=True, wal=True)        
            for weight in orWeightsLs:
                if str(targets) in str(weight):
                    connectAttr(condNode.outColorR, PyNode(rtParent + '.' + weight),f=True)
            connectAttr(condNode.outColorR, multRotNode.input2X ,f=True)
            connectAttr(condNode.outColorR, multRotNode.input2Y ,f=True)
            connectAttr(condNode.outColorR, multRotNode.input2Z ,f=True)
            connectAttr(multRotNode.outputX, PyNode(str(offsetStoreRot) + '.input3D[' + str(numTargets -1) + '].input3Dx'), f=True)
            connectAttr(multRotNode.outputY, PyNode(str(offsetStoreRot) + '.input3D[' + str(numTargets -1) + '].input3Dy'), f=True)
            connectAttr(multRotNode.outputZ, PyNode(str(offsetStoreRot) + '.input3D[' + str(numTargets -1) + '].input3Dz'), f=True)
        
        enumStr = ""
        
        if self.translate:
            enumStr = ""
            targetList = []
            for target in pointConstraint(trnParent, q=True, tl=True):
                targetList.append(target)
                enumStr = enumStr + "" + target + ":"
                
        if self.rotate:
            enumStr = ""
            targetList = []
            for target in orientConstraint(rtParent, q=True, tl=True):
                targetList.append(target)
                enumStr = enumStr + "" + target + ":"
                
        addAttr(control.multiSwitch, at="enum", enumName=enumStr, e=True)
        
        origSpace = control.attr('multiSwitch').get()
        control.attr('multiSwitch').set(numTargets - 1)
        
        dupCtrl = duplicate(zeroGrp)
        ptCt = pointConstraint(origLoc, dupCtrl[0], mo=0, w=1)
        orCt = orientConstraint(origLoc, dupCtrl[0], mo=0, w=1)
        tr = dupCtrl[0].attr('translate').get()
        rt = dupCtrl[0].attr('rotate').get()
        delete(ptCt)
        delete(orCt)
        delete(dupCtrl)
        offsetTran = tr
        offsetRot = rt
        
        delete(origLoc)
        
        if self.translate:
            multTranNode.attr('input1X').set(offsetTran[0])
            multTranNode.attr('input1Y').set(offsetTran[1])
            multTranNode.attr('input1Z').set(offsetTran[2])
        
        if self.rotate:
            multRotNode.attr('input1X').set(offsetRot[0])
            multRotNode.attr('input1Y').set(offsetRot[1])
            multRotNode.attr('input1Z').set(offsetRot[2])
        
        control.attr('multiSwitch').set(origSpace)
        
        #re-locks the attributes of the control
        for att in lockedAttr:
            control.attr(att).setLocked(True)
            
        connectChainToMeta(targetList, self.networkNode, 'targets')
        
        if autoKey:
            autoKeyframe(e=True, state=True)
        
    def alignSwitch(self, control, target):
        '''
        switches to desired target and keeps the control position and
        orientation aligned with previous target
         
        control:
            the child of the constraint
        target:
            the parents to switch to
            
        example use(select control then target):
            x.alignSwitch(ls(sl=True)[0], ls(sl=True)[1])
        '''
        
        loc = spaceLocator()
        ptCt = pointConstraint(control, loc, mo=False)
        orCt = orientConstraint(control, loc, mo=False)
        delete(ptCt)
        delete(orCt)

        nullTransform = self.networkNode.nullTransform.listConnections()[0]
        
        control.attr('multiSwitch').set(control.attr('multiSwitch').getEnums()[str(target)])
        
        lockedAttr = []
        for trns in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            if control.attr(trns).isLocked():
                control.attr(trns).setLocked(False)
                lockedAttr.append(trns)
        
        dupCtrl = duplicate(control)
        ptCt = pointConstraint(loc, dupCtrl[0], mo=False)
        orCt = orientConstraint(loc, dupCtrl[0], mo=False)
        tr = dupCtrl[0].attr('translate').get()
        rt = dupCtrl[0].attr('rotate').get()
        delete(ptCt)
        delete(orCt)
        delete(loc)
        delete(dupCtrl)
        
        control.attr('translate').set(tr)
        control.attr('rotate').set(rt)       
        
        for att in lockedAttr:
            control.attr(att).setLocked(True)
            
    def bakeAndSwitch(self, control, target, startTime=playbackOptions(q=1, min=1), endTime=playbackOptions(q=1, max=1)):
        #x = meta.getMetaRoot(PyNode('batman_rig:center_head_1_anim'), 'MultiConstraint')
        #x.bakeAndSwitch(ls(sl=True)[0])
        
        currentTime(1)
        control = self.networkNode.control.listConnections()[0]
        bakeStore = spaceLocator()
        
        lckTrans = []
        for trans in ['x', 'y', 'z']:
            if control.attr('t' + trans).isLocked():
                    lckTrans.append(trans)
                    
        lckRot = []
        for rot in ['x', 'y', 'z']:
            if control.attr('r' + rot).isLocked():
                lckRot.append(lckRot)
                
        prtCst = parentConstraint(control, bakeStore, mo=0)
        
        bakeResults(bakeStore, t=(playbackOptions(q=1, min=1), playbackOptions(q=1, max=1)), sm=True, pok=1)
        delete(prtCst)
        
        for ax in ['x','y','z']:
            if ax not in lckTrans:
                cutKey(control, at='t' + ax, t=(startTime, endTime), o='keys')
        
        for ax in ['x','y','z']:
            if ax not in lckRot:
                cutKey(control, at='r' + ax, t=(startTime, endTime), o='keys')
        
        cutKey(control.multiSwitch, t=(startTime, endTime), at='multiSwitch', o='keys')

        enumNum = control.attr('multiSwitch').getEnums()[str(target)]
        print enumNum
        
        setKeyframe(control, t=startTime + 1, at='multiSwitch', v=enumNum)
        prtCst = parentConstraint(bakeStore, control, st=lckTrans, sr=lckRot, mo=0)
        
        for ax in ['x','y','z']:
            if ax not in lckTrans:
                bakeResults(control, at='t' + ax, t=(startTime, endTime-1), sm=True, pok=1)
                
        for ax in ['x','y','z']:
            if ax not in lckRot:
                bakeResults(control, at='r' + ax, t=(startTime, endTime-1), sm=True, pok=1)
                
        setKeyframe(control, t=endTime-1, at='multiSwitch', v=enumNum)
        currentTime(endTime-1)
        currentTime(findKeyframe(control, w='next', at='multiSwitch'))
        enumNum = control.attr('multiSwitch').get()
        enumDict = control.attr('multiSwitch').getEnums()
        targetName = 0;
        for key, value in enumDict.items():
            if value == enumNum:
                targetName = key
                           
        print targetName
        currentTime(endTime)
        self.alignSwitch(control, targetName)
        setKeyframe(control, t=endTime)
        
        delete(prtCst)
        delete(bakeStore)
        select(cl=True)
        select(control)
        
    def removeTarget(self, control, target):
        '''
        remove a target from the list
        only supports removing one at a time
         
        control:
            the child of the constraint
        targets:
            the parents in the relationship
        
        example to add to existing multiconstraint(select control then target):
            x.removeTarget(ls(sl=True)[0], ls(sl=True)[1])
        '''
        
        if not target in control.attr('multiSwitch').getEnums().keys() :
            raise Exception("chosen target not in target list")
        
        autoKey = False
        if autoKeyframe(q=True, state=True):
            autoKeyframe(e=True, state=False)
            autoKey = True
        
        zeroGrp = self.networkNode.zeroGrp.listConnections()[0]
        
        offsetStoreTran = 0
        offsetStoreRot = 0
        
        if self.translate:
            offsetStoreTran = self.networkNode.offsetStoreTran.listConnections()[0]      
            disconnectAttr(offsetStoreTran.output3D, zeroGrp.rotate)
        if self.rotate:
            offsetStoreRot = self.networkNode.offsetStoreRot.listConnections()[0]
            disconnectAttr(offsetStoreRot.output3D, zeroGrp.rotate)
        
        enumVal = control.attr('multiSwitch').getEnums()[str(target)]
        
        numKeys = len(keyframe(control, at='multiSwitch', time=(playbackOptions(q=True, ast=True),playbackOptions(q=True, aet=True)), query=True, valueChange=True, timeChange=True));
        
        for i in xrange(0, numKeys):
            enumInd = keyframe(control, at='multiSwitch', index=i, query=True, valueChange=True)[0]
            if enumInd > enumVal:
                keyframe(control, at='multiSwitch', index=i, edit=True, valueChange=enumInd - 1)
        
        nullTransform = self.networkNode.nullTransform.listConnections()[0]

        loc = spaceLocator()
        ptCt = pointConstraint(zeroGrp, loc, mo=False)
        orCt = orientConstraint(zeroGrp, loc, mo=False)
        delete(ptCt)
        delete(orCt)
        
        if self.translate:
            mel.eval('AEremoveMultiElement ' + str(offsetStoreTran) + '.input3D[' + str(enumVal) + ']');
            mel.eval('AEremoveMultiElement ' + str(offsetStoreTran) + '.input3D[' + str(enumVal) + ']');
        if self.rotate:
            mel.eval('AEremoveMultiElement ' + str(offsetStoreRot) + '.input3D[' + str(enumVal) + ']');
            mel.eval('AEremoveMultiElement ' + str(offsetStoreRot) + '.input3D[' + str(enumVal) + ']');
            
        delete(control + '_condition_' + target)
        
        delete(control + "_multRot_" + target)
        delete(control + "_multTran_" + target)
        
        # delete()
        
        if self.translate:
            trnParent = pointConstraint(target, nullTransform, e=True, rm=True)
        if self.rotate:
            rtParent = orientConstraint(target, nullTransform, e=True, rm=True)
        
        enumStr = ""
        
        if self.translate:
            enumStr = ""
            targetList = []
            for t in pointConstraint(trnParent, q=True, tl=True):
                targetList.append(t)
                enumStr = enumStr + "" + t + ":"
                
        if self.rotate:
            enumStr = ""
            targetList = []
            for t in orientConstraint(rtParent, q=True, tl=True):
                targetList.append(t)
                enumStr = enumStr + "" + t + ":"
                
        addAttr(control.multiSwitch, at="enum", enumName=enumStr, e=True)
                
        lockedAttr = []
        for trns in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            if control.attr(trns).isLocked():
                control.attr(trns).setLocked(False)
                lockedAttr.append(trns)
        
        i = 0
        for t in control.attr('multiSwitch').getEnums().keys():
            PyNode(control + '_condition_' + t).attr('secondTerm').set(i)
            i = i + 1
        origSpace = control.attr('multiSwitch').get()
        control.attr('multiSwitch').set(0)
        
        dupCtrl = duplicate(zeroGrp)
        ptCt = pointConstraint(loc, dupCtrl[0], mo=False)
        orCt = orientConstraint(loc, dupCtrl[0], mo=False)
        tr = dupCtrl[0].attr('translate').get()
        rt = dupCtrl[0].attr('rotate').get()
        delete(ptCt)
        delete(orCt)
        delete(loc)
        delete(dupCtrl)
        
        zeroGrp.attr('translate').set(tr)
        zeroGrp.attr('rotate').set(rt)       
        
        for att in lockedAttr:
            control.attr(att).setLocked(True)           
        
        #remove from meta
        i = 0
        for parent in self.networkNode.targets:
            if parent.listConnections(d=1):
                if (target == parent.listConnections(d=1)[0]):
                    disconnectAttr(PyNode(target + '.metaParent'), self.networkNode.targets[i])
            i = i + 1
        
        control.attr('multiSwitch').set(origSpace)
        
        if self.translate:
            connectAttr(offsetStoreTran.output3D, zeroGrp.translate, f=True)
        if self.rotate:
            connectAttr(offsetStoreRot.output3D, zeroGrp.rotate, f=True)
        
        if autoKey:
            autoKeyframe(e=True, state=True)
    
    def getConstraints(self):
        '''
        returns a list of the constraints used
        '''
        constraintList = []
        if objExists("pConstTranslate_" + self.getChild().name()) :
            constraintList.append(self.networkNode.pointConstraint.listConnections()[0])
        
        if  objExists("pConstRotate_" + self.getChild().name()) :
            constraintList.append(self.networkNode.orientConstraint.listConnections()[0])
               
        return constraintList
        
    def getChild(self):
        '''
        returns the object that has the multiConstraint
        '''
        return self.networkNode.control.listConnections()[0]
        
    def getParents(self):
        '''
        return a list of parents of the multiConstraint
        '''
        return self.networkNode.targets.listConnections()
        
    def getAllAnims(self):
        return []
        
    def toDefaultPose(self):
        return 0
        # allComps = self.getAllRigComponents()
            # for comp in allComps:
                # comp.toDefaultPose()
        
        
class ReversePelvis(RigComponent):
    def __init__(self, side, bodyPart, rootJoint, pivotJoint, node=None):
        '''
        Component for pelvis meant to work with RFKChain on a spine. 
        
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        rootJoint:
            the place where the component starts, makes most sense to use on rootJoint
        pivotJoint:
            the joint this component will actually pivot around
            in a RFK spine, this would be the first joint of the RFK component
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'ReversePelvis'):
                    self.networkNode = node
                else:
                    printError("ReversePelvis: node %s is not a ReversePelvis metaNode"%(node))
            else:
                printError("ReversePelvis: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'ReversePelvis', 1.0, 'create reverse pelvis component', side, bodyPart, rootJoint, pivotJoint)
            self.create(side, bodyPart, rootJoint, pivotJoint)
        
    def create(self, side, bodyPart, rootJoint, pivotJoint):
        compname = side + "_" + bodyPart
        bind_joints = chainBetween(rootJoint, pivotJoint)
        control_joint = duplicateChain(bind_joints[1], bind_joints[1], 'bind', 'control')[0]
        cube = polyCube()[0];
        control_joint.rename(compname + '_anim')
        prtCts = parentConstraint(control_joint, cube, mo=0)
        appendShape(cube, control_joint)
        addAnimAttr(control_joint)
        delete(cube)
        parentConstraint(control_joint, bind_joints[0], mo=1)
        
        mainGrp = group(control_joint, n=compname + '_component_grp')
        lockAndHideAttrs(control_joint, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
        
        connectToMeta(mainGrp, self.networkNode, 'mainGrp')
        connectToMeta(control_joint, self.networkNode, 'controlJoint')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp')

    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.mainGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []   
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        allAnims = self.networkNode.controlJoint.listConnections()
        return allAnims
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoint.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoint.listConnections()[-1]
        else: # an object
            raise Exception("ReversePelvis.getConnectObj: location obj,%s , doesn't exist"%location)
        raise Exception("ReversePelvis.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or control joint ")
        
    def toDefaultPose(self):
        allAnims = self.getAllAnims()
        for anim in allAnims:            
            resetAttrs(anim)  

            
class RFKChain(RigComponent):
    def __init__(self, side, bodyPart, startJoint, endJoint, node=None):
        '''
        Creates a Reverse FKChain. Useful aternative for necks and spines.
        
        side:
            the side is this component on, ex. center, left, right
        bodyPart:
            the body part the component is for, ex. arm, leg, clavicle, foot
        startJoint:
            the place where the component starts
        endJoint:
            the place where the component end
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'RFKChain'):
                    self.networkNode = node
                else:
                    printError("RFKChain: node %s is not a RFKChain metaNode"%(node))
            else:
                printError("RFKChain: node %s doesn't exist"%(node))
        else:
            RigComponent.__init__(self, 'RFKChain', 1.0, 'chain of RFK Joints', side, bodyPart, startJoint, endJoint)
            rfkChain = chainBetween(startJoint, endJoint)
            self.create(side, bodyPart, rfkChain)
        
    def create(self, side, bodyPart, chain):
        compname = side + '_' + bodyPart
        animList = []
        twistLoc = []
        aimerLocs = []
        zeroGrp = []
        animGrpList = []
        chainLength = 0 # Total chain length
        midChainLength = 0 # Length of just the middle joints
        bind_joints = []
        for item in chain:
            item = PyNode(item)
            if item.type() == 'joint':
                bind_joints.append(item)
        
        rfk_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'RFK')
        control_joints = duplicateChain(bind_joints[0], bind_joints[-1], 'bind', 'control')
        
        for joint in rfk_joints:
            if joint != rfk_joints[0]:
                parent(joint, w=1)
            
        plcHld = polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=[0, 1, 0], cuv=4, ch=1);
        
        #initial anim set up and create locators to be aim constrained
        inc = 1
        for joint in control_joints:
            nameStr = joint.name().replace("_control_joint", "_")
            shape = rfk_joints[inc - 1]
            cube = duplicate(plcHld)[0]
            cube = PyNode(cube)
            appendShape(cube, shape)
            addAnimAttr(shape)
            animList.append(shape)
            shape.rename(nameStr + "anim")
            delete(cube)
            if joint == control_joints[0]:
                pointConstraint(shape, joint, mo=1)
            orientConstraint(shape, joint, mo=1)
            if (joint != control_joints[0]) & (joint != control_joints[-1]):
                midChainLength+=PyNode(str(joint)).attr('translateX').get()
                grp = group(shape, name=shape.name() + '_grp')
                pointConstraint(joint, grp, mo=0)
                loc = spaceLocator(n=nameStr + 'aimer')
                aimerLocs.append(loc)
            elif joint == control_joints[0]:
                loc = spaceLocator(n=compname + '_start_twist')
                zeroGrp.append(loc)
            else:
                loc = spaceLocator(n=compname + '_end_twist')
                zeroGrp.append(loc)
            if joint == control_joints[-1]:
                pointConstraint(joint, shape, mo=0)
            twistLoc.append(loc)
            prtCt = parentConstraint(shape, loc, mo=0)
            delete(prtCt)
            chainLength+=PyNode(str(joint)).attr('translateX').get()
            inc+=1
        
        delete(plcHld)
        
        avgLength = chainLength / (len(control_joints) - 1)
        
        topPosY = twistLoc[-1].attr('translateY').get()

        simLocs = []
        midY = []
        startY = 0
        endY = 0
        
        #create and constrain locators for each joint to simulate desired joint movement
        #locators will be the aim targets for previously created locators
        inc = 1
        for loc in twistLoc:
            if loc == twistLoc[0]:
                locDup = duplicate(loc, n=compname + '_start_sim')[0]
                locDupY = duplicate(loc, n=compname + '_start_y')[0]
                startY = locDupY
                orientConstraint(animList[0], locDupY)
            elif loc == twistLoc[-1]:
                locDup = duplicate(loc, n=compname + '_end_sim')[0]
                locDupY = duplicate(loc, n=compname + '_end_y')[0]
                endY = locDupY
                orientConstraint(animList[-1], locDupY)
            else:
                locDup = duplicate(loc, n=compname + '_mid_%i_sim'%(inc))[0]
                locDupY = duplicate(loc, n=compname + '_mid_%i_y'%(inc))[0]
                simLocs.append(locDup)
                midY.append(locDupY)
                inc+=1
                
            # Robert: Used to be topPosY + avgLength.  This worked well for three joint spines
            # since the mid joint used to be about the avgLength in size.  However, as you add
            # more joints to the middle of the spine this causes the end_sim locator to provide
            # less and less room for the mid_sim locators -- thus the spine does not bend down as well.
            locDup.attr('translateY').set(topPosY + midChainLength)
            
            pointConstraint(locDup, locDupY, mo=0)
        
        strTwst = PyNode(compname + '_start_twist')
        endTwst = PyNode(compname + '_end_twist')
        strSim = PyNode(compname + '_start_sim')
        endSim = PyNode(compname + '_end_sim')
        parent(strSim, strTwst)
        parent(endSim, endTwst)
        
        #set up aim constraint group to point to previously created locators
        #and create offset group which will consrtain anim group
        offsetList = []
        inc = 0
        for loc in aimerLocs:
            aimGrp = group(loc, name=loc.name() + '_grp')
            offgrp = group(em=1, name=loc.name() + '_offset')
            offsetList.append(offgrp)
            parent(offgrp, loc)
            zeroGrp.append(aimGrp)
            aimConstraint(simLocs[inc], loc, mo=1, aim=[0,1,0], u=[0,1,0], wut='object', wuo=simLocs[inc])
            inc+=1
        
        zrGrp = group(em=1, name=compname + '_zero_grp')
        
        parent(zeroGrp, zrGrp)
        
        pointConstraint(control_joints[0], zrGrp, mo=1)
           
        #set up weights for previously constrained locators
        #set up twistBias attribute
        #connect twistBias to XZ twist locators
        weightBase = 1.0 / (len(midY) + 1)
        animList[-1].addAttr('twistBias', at="float", dv=0, k=1, hnv=1, min=-1, hxv=1, max=1)
        animList[-1].attr('twistBias').set(keyable = 0, cb = 0)
        plus = []
        rev = []
        inc = 0
        for loc in simLocs:
            ptCt = pointConstraint([strSim, endSim], loc, mo=1)
            startWeight = (weightBase * len(midY)) - (inc * weightBase)
            endWeight = (weightBase) + (inc * weightBase)
            mult = createNode('multiplyDivide', n="twist_mult_" + str(loc))
            pls = createNode('plusMinusAverage', n="twist_plus_" + str(loc))
            plus.append(pls)
            reverse = createNode('reverse', n="twist_rev_" + str(loc))
            rev.append(reverse)
            connectAttr(animList[-1].twistBias, mult.input1X, f=1)
            mult.attr('input2X').set(weightBase)
            connectAttr(pls.output2Dx, reverse.inputX, f=1)
            pls.attr('input2D[1].input2Dx').set(endWeight)
            connectAttr(mult.outputX, pls.input2D[0].input2Dx, f=1)
            connectAttr(reverse.outputX, ptCt.attr(compname + '_start_simW0'), f=1)
            connectAttr(pls.output2Dx, ptCt.attr(compname + '_end_simW1'), f=1)
            inc+=1
            
        orientConstraint(animList[0], strTwst, mo=0)    
        orientConstraint(animList[-1], endTwst, mo=0)
        
        #constrain anim group to offset group driven by aim constraint
        inc = 0
        for anim in animList:
            if (anim != animList[0]) & (anim != animList[-1]):
                animPrt = anim.listRelatives(p=1)
                orientConstraint(offsetList[inc], animPrt, mo=1)
                inc+=1
        
        #connect twistBias to Y twist locators
        inc = 0
        for loc in midY:
            # Robert: Removed skip=["y", "z"] since it was causing flipping in >3 joints.  Basically
            # when rotateX flipped the other values weren't there to compensate for it.
            orCt = orientConstraint([startY, endY], loc)
            orCt.attr('interpType').set(2)
            connectAttr(rev[inc].outputX, orCt.attr(compname + '_start_yW0'), f=1)
            connectAttr(plus[inc].output2Dx, orCt.attr(compname + '_end_yW1'), f=1)
            rotGrp = group(offsetList[inc], n='rotGrp')
            orientConstraint(loc, rotGrp, mo=1, skip=["y", "z"])
            
            inc+=1
        
        # Robert: avgLength -> midChainLength
        strSim.attr('translateX').set(strSim.attr('translateX').get() - midChainLength)
        
        #constrain bind joints
        for inc in xrange(len(rfk_joints)):#-1
            parentConstraint(control_joints[inc], bind_joints[inc])
        
        #set up anims and clean up uneeded attributes from channel box
        animGrp = group(em=True, n=compname + '_anim_grp')
        for anim in animList:
            lockAndHideAttrs(anim, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius'])
            makeIdentity(anim, a=1, t=0,r=1, s=0, n=0)
            if (anim != animList[0]) & (anim != animList[-1]):
                parent(listRelatives(anim, p=1), animGrp)
            else :
                parent(anim, animGrp)
        
        #create clean up groups and hide system from animators
        print simLocs, startY, endY, midY, zrGrp, compname
        dntGrp = group(simLocs, startY, endY, midY, zrGrp, n=compname + '_DO_NOT_TOUCH_grp')
        ctrlJts = group(control_joints[0], n=compname + '_joint_grp')
        mainGrp = group([ctrlJts, dntGrp, animGrp], n=compname + '_component_grp')
        dntGrp.attr('visibility').set(0)
        xform(mainGrp, piv=bind_joints[0].getTranslation(space = 'world'), ws=1)
        
        #connect to meta
        connectChainToMeta(bind_joints, self.networkNode, 'bindJoints')
        connectChainToMeta(rfk_joints, self.networkNode, 'RFKJoints')
        connectChainToMeta(control_joints, self.networkNode, 'controlJoints')
        connectToMeta(dntGrp, self.networkNode, 'dntGrp')
        connectToMeta(mainGrp, self.networkNode, 'componentGrp')
    
    def connectToComponent(self, comp, location, point=1, orient =1):
        '''
        connects this component to the other component
        comp:
            the component to attach to
        location:
            the place where the components connect, ex, start, end, jointName
        point:
            attach by translation
        orient:
            attach by orientation
        '''
        obj = comp.getConnectObj(location)
        mainGrp = self.networkNode.componentGrp.listConnections()[0]
        skipRot = ['x','y','z']
        skipTrans = ['x','y','z']
        if point:
            skipTrans = []
        if orient:
            skipRot = []   
        parentConstraint(obj, mainGrp, sr = skipRot, st = skipTrans,w=1, mo=1)
        
    def getAllAnims(self):
        '''
        returns a list of all the anims
        '''
        allAnims = self.networkNode.RFKJoints.listConnections()
        return allAnims
        
    def getConnectObj(self, location):
        '''
        gets the component to connect to at location
        location:
            the location to connect to
        return:
            the obj which others can connect to
        '''
        if location == 'start':
            return self.networkNode.controlJoints.listConnections()[0]
        elif location == 'end':
            return self.networkNode.controlJoints.listConnections()[-1]
        else: # an object
            if not objExists(location):
                raise Exception("RFKChain.getConnectObj: location obj,%s , doesn't exist"%location)
            location = PyNode(location)
            bind_joints = self.networkNode.bindJoints.listConnections()
            control_joints = self.networkNode.controlJoints.listConnections()
            for inc in xrange(len(bind_joints)):# test for a bind joint
                if location == bind_joints[inc]:
                    return control_joints[inc]
                if location == control_joints[inc]:
                    return control_joints[inc]
        raise Exception("RFKChain.getConnectObj: location wasn't found, try 'start', 'end', or name of bind or control joint ")
        
    def toDefaultPose(self):
        allAnims = self.getAllAnims()
        for anim in allAnims:            
            resetAttrs(anim)
        
class Evil(MetaNode):
    def __init__(self,evilCurve, numJoints = 50, radius = 1, taper = 0, node = None):
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'Evil'):
                    self.networkNode = node
                else:
                    printError("Evil: node %s is not a Evil metaNode"%(node))
            else:
                printError("Evil: node %s doesn't exist"%(node))
            
        else:
            MetaNode.__init__(self, 'Evil', 1.0, 'evil growth')
            
            
            #error testing
            if not objExists(evilCurve):
                raise Exception("Evil.__init__: object doesn't exist, %s "%evilCurve)
            evilCurve = PyNode(evilCurve)
            
            #rebuild the curve
            makeCurveUniform(evilCurve)
            
            #createJoints
            joints = []
            select(cl = 1)
            for num in xrange(numJoints):
                j = joint()
                select(cl=1)
                joints.append(j)
            select(cl=1)
            
            #alignJoints to curve
            incPar = 1.0/(numJoints-1)
        
            pointOnCurves = []
            locs = []
            
            for j in joints[:-1]:
                j.orientJoint('xyz', zso=1, sao = 'zup')
            
            
            for inc in xrange(numJoints):
                j = joints[inc]
                poc ,loc = attachToCurve(evilCurve, j, incPar*inc, 1,1)
                pointOnCurves.append(poc)
                locs.append(loc)
                
            #draw override on joint color
            joints[0].overrideEnabled.set(1)
            joints[0].overrideColor.set(9)

            #createpoly
            orient = pointOnCurves[0].result.tangent.get()
            subdiv = 10
            poly, temp = polyCylinder(axis = orient,ch=1, o=1,r=radius,h=1,sx = subdiv, sc=0,cuv=3)
            delete(poly.f[:-1])
            
            #align poly to curve
            poly.centerPivots()
            alignPointOrient(joints[0], poly, 1,0)
            
            
            #extrude poly along curve
            polyExtrudeFacet(poly.f[0], ch=0, keepFacesTogether=1, pvx = 2.384185791e-007, pvy=0.5,pvz =3.576278687e-007,divisions=numJoints-1, twist=0, taper=taper, off=0,smoothingAngle=30 ,inputCurve=evilCurve)
            
            
            #unwrap UVs
            poc = PyNode(pointOnCurve(evilCurve, ch=1))
            incPar = 1.0/(numJoints-1)
            incOffset = 1.0/(numJoints-1)/2
            numFaces = poly.numFaces()
            for nf in xrange(numJoints-1):
                faces = []
                for sd in xrange(subdiv):
                    faces.append(poly.f[((numFaces-2)/subdiv)*(sd)+2+nf])
                
                poc.parameter.set(incPar*nf+incOffset)
                loc1 = spaceLocator()
                loc1.translate.set(poc.result.position.get())
                trans = poc.result.position.get()
                
                poc.parameter.set(incPar*(nf+1)+incOffset)
                loc2 = spaceLocator()
                loc2.translate.set(poc.result.position.get())
                
                aimConstraint(loc2, loc1, w=1, mo=0, aimVector= [0, -1, 0], upVector= [0, 1, 0], worldUpType ="vector", worldUpVector=[ 0, 1, 0])
                
                rot = loc1.rotate.get()
                
                delete(loc1)
                delete(loc2)
                select(cl=1)
                map(lambda x: select(x, add=1), faces)
                polyCylindricalProjection( projectionCenter = trans,psu=360, smartFit = 1, rotate = rot)    
                        
                
                
            delete(poc)
            select(poly, r=1)
            rt.DeleteHistory()
            select(cl=1)
            
            #bind poly to joints
            skinClust = skinCluster(poly, joints, sw=1)[0]

            #create anims
            anims = []
            
            #put first 2 cv in first anim
            select("%s.cv[%i]"%(evilCurve, 0))
            clust1, clustHandle1 = cluster()
            select("%s.cv[%i]"%(evilCurve, 1))
            clust2, clustHandle2 = cluster()
            cube, shape = polyCube()
            anims.append(cube)
            delete(parentConstraint(clustHandle2, clustHandle1, cube, w=1, mo=0))
            parent(clustHandle1, cube)
            parent(clustHandle2, cube)
            clustHandle1.hide()
            clustHandle2.hide()
            
            #rest of anims    
            for cv in xrange(evilCurve.numCVs()-2):
                cv = cv+2
                select("%s.cv[%i]"%(evilCurve, cv))
                clust, clustHandle = cluster()
                cube, shape = polyCube()
                anims.append(cube)
                alignPointOrient(clustHandle, cube, 1,1)
                parent(clustHandle, cube)
                clustHandle.hide()
            
            #zero out anims
            for anim in anims:
                makeIdentity(anim, apply=1, t=1, r=1, s=1, n=0)    
            
                
            #create Control obj
            
            controlGrp = group(empty = 1, n = 'evil_control')
            controlGrp.addAttr('evilGrow', min = 0, max =50, dv = 0, keyable =1)
            lockAndHideAttrs(controlGrp, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz','sx', 'sy', 'sz','v'])
            attr = controlGrp.evilGrow
            
            #make setdriven keys        
            
            maximum = attr.getMax()
            if not maximum:
                maximum = 50
        
            incValue = maximum/numJoints
            
            for inc in xrange(numJoints):
                j = joints[inc]
                poc = pointOnCurves[inc]
                par = poc.parameter.get()
                
                #translate along curve
                attr.set(0)
                poc.parameter.set(0)
                setDrivenKeyframe(poc.parameter, cd = attr)
                
                attr.set(incValue*(inc))
                poc.parameter.set(par)
                setDrivenKeyframe(poc.parameter, cd = attr)
                
                #scales
                attr.set(incValue*inc)
                j.scale.set([0,0,0])
                setDrivenKeyframe(j.scale ,cd = attr)
                
                attr.set(maximum)
                j.scale.set(1,1,1)
                setDrivenKeyframe(j.scale, cd= attr)
                pointOnCurves.append(poc)
                
            #prepare the evil for attachment
            attachGrp = spaceLocator()
            attachGrp.rename('evil_attach_grp')
            poc, loc = attachToCurve(evilCurve, attachGrp, 0, 1,1)
            delete(poc, loc)
            #####orient down the x axis
            attachGrp.rotateY.set(attachGrp.rotateY.get() + 90)
            attachRotateControlGrp = group(empty = 1, n = 'evil_attach_rot_grp')
            alignPointOrient(attachGrp, attachRotateControlGrp, 1,1)
            parent(attachRotateControlGrp, attachGrp)
            makeIdentity(attachRotateControlGrp, apply=1, t=1, r=1, s=1, n=0)
                
            #groupings            
            animGrp = group(anims, n = 'evil_anims')
            locGrp = group(locs, n = 'locator_grp')
            jointGrp = group(joints, n = 'evil_joint_grp')
            dntGrp = group(locGrp, n = 'evil_DO_NOT_TOUCH')
            animGrp = group([controlGrp, animGrp],n = 'evil_anim_grp')
            evilGrp = group([attachGrp,dntGrp, evilCurve, jointGrp, poly], n = 'evil')
            parent(animGrp, attachRotateControlGrp)
            
            animGrp.hide()
            jointGrp.hide()
            dntGrp.hide()
            
            #attach all info to metaNodes

            connectToMeta(evilCurve, self.networkNode, 'curve')
            connectChainToMeta(joints, self.networkNode, 'joints')
            connectChainToMeta(anims, self.networkNode, 'anims')
            connectChainToMeta(pointOnCurves, self.networkNode, 'pocs')
            connectToMeta(controlGrp, self.networkNode, 'growGrp')
            connectToMeta(evilGrp, self.networkNode, 'mainGrp')
            self.networkNode.setAttr('growAttr', 'evilGrow', f=1)
            connectToMeta(animGrp, self.networkNode, 'animGrp')
            connectToMeta(poly, self.networkNode, 'mesh')
            connectToMeta(dntGrp, self.networkNode, 'dntGrp')
            self.networkNode.setAttr('radius', radius, f=1)
            self.networkNode.setAttr('taper', taper, f=1)
            
            #add attached information
            connectToMeta(attachGrp, self.networkNode, 'attachGrp')
            connectToMeta(attachRotateControlGrp, self.networkNode, 'rotateGrp')
            self.networkNode.setAttr('rotateAttr', 'rotateX' ,f=1)
            
            self.networkNode.addAttr('attachPoc', dt='string')
            self.networkNode.addAttr('attachLoc', dt='string')
            self.networkNode.setAttr('percentAttr', 'parameter', f=1)
            
            self.networkNode.addAttr('evilChildren', dt= 'string', multi=1)
            self.networkNode.setAttr('attached', 0, f=1)
            

    def toggleAnims(self):
        '''
        toggles showing and hiding the evil anims
        '''
        animGrp = self.networkNode.animGrp.listConnections()[0]
        if animGrp.v.get():
            animGrp.hide()
        else:
            animGrp.show()
            
    def hideAnims(self):
        '''
        hides the anims
        '''
        animGrp = self.networkNode.animGrp.listConnections()[0]
        animGrp.hide()
        
    def showAnims(self):
        '''
        shows the anims
        '''
        animGrp = self.networkNode.animGrp.listConnections()[0]
        animGrp.show()
        
        
        
    def attachEvil(self, other, percent = .5):
        '''
        attached the other evil to this evil at the percent given
        other:
            other evil to attach to self
        percent:
            where along the curve to add evil [0,1]
        return True if connection was successful, else False
        '''
        #error test
        if other == self:
            raise Exception("can't connect self as parent and child")
        if percent > 1 or percent < 0:
            raise Exception("percent needs to be between 0 and 1")
        if not isMetaNodeOfType(other.networkNode, 'Evil'):
            raise Exception("other evil object isn't of class Evil")
        if other.networkNode in self.listEvilParents():    
            raise Exception("other evil is a parent of this evil, parenting would cause loop")
        #don't attach if already attached
        if other.isAttached():
            return False
            
        attachGrp = other.getAttachGrp()
        poc, loc = attachToCurve(self.getCurve(), attachGrp, percent,1,1)
        
        #meta Connections
        connectToMeta(poc, other.networkNode, 'attachPoc')
        connectToMeta(loc, other.networkNode, 'attachLoc')
        parent(loc, other.networkNode.dntGrp.listConnections()[0])
        connectToMeta(other.networkNode, self.networkNode, 'evilChildren')
    
        other.networkNode.attached.set(1)
        return True
        
    def detach(self):
        '''
        detach self from all other evils
        '''
        if not self.isAttached():
            raise Exception("Evil.detach: This Evil is already detached")
        poc = self.networkNode.attachPoc.listConnections()[0]
        loc = self.networkNode.attachLoc.listConnections()[0]
        delete(poc)
        delete(loc)
        self.networkNode.metaParent.disconnect()
        self.networkNode.attached.set(0)

    def listEvilParents(self):
        """
        returns a list of all parents and parent's parent etc of this evil
        return:
            [parent, parent, ...]
        """
        parents = []
        currentPar = None
        try:
            currentPar = self.networkNode.metaParent.listConnections()[0]
        except:
            pass
        if currentPar:
            parents.append(currentPar)
        while currentPar:
            par = None
            try:
                par = currentPar.networkNode.metaParent.listConnections()[0]
            except:
                pass
            if par:
                parents.append(par)
            currentPar = par
        return parents
        
    def getAttachGrp(self):
        '''
        returns the group to attach To
        '''
        return self.networkNode.attachGrp.listConnections()[0]
        
    def isAttached(self):
        '''
        returns whether this evil is attached to something else
        '''
        return self.networkNode.attached.get()
        
    def getCurve(self):
        '''
        returns the curve controling the evil
        '''
        return self.networkNode.curve.listConnections()[0]
        
    def listAnims(self):
        '''
        return a list of the anims that control curve
        '''
        return self.networkNode.anims.listConnections()
        
    def keyAnims(self):
        '''
        keyframes all the anims at their current position at the current time
        '''
        for anim in self.listAnims():
            setKeyframe(anim)
    
    def randomizeAnims(self, value):
        '''
        randomizes all anims except the start anim by offseting translation by the given value
        value:
            how much to offset by
        '''        
        import random
        attrs = ['tx', 'ty', 'tz']
        for anim in self.listAnims()[1:]:
            for attr in attrs:
                pos = random.choice([-1,1])
                at = anim.attr(attr)
                at.set(at.get() + (random.random()* value*pos))
        
    
    def delete(self):
        '''
        removes the everything related to the evil except the curve it was created from
        return:
            the curve it was created from
        '''
        
        #delete point On Curves
        pocs = self.networkNode.pocs.listConnections()
        delete(pocs)
        
        #unparent Curve
        evilCurve = self.networkNode.curve.listConnections()[0]
        parent(evilCurve, world = 1)
        evilCurve2 = duplicate(evilCurve)[0]
        evilChildren = evilCurve2.getChildren()
        for obj in evilChildren:
            if obj != evilCurve2.getShape():
                delete(obj)
        delete(evilCurve)
        
        
        #delete maingrp
        mGrp = self.networkNode.mainGrp.listConnections()[0]
        delete(mGrp)
        
        #delete metaNode
        try:
            delete(self.networkNode)
        except:
            pass
            
        #return
        return evilCurve2
        
    def recreate(self, numJoints = None, radius = None, taper = None):
        '''
        recreate evil with new inputs
        '''
        if numJoints == None:
            numJoints = len(self.networkNode.joints.listConnections())
        if radius == None:
            radius = self.networkNode.radius.get()
        if taper == None:
            taper = self.networkNode.taper.get()
            
        #get connected evil and percent
        percent = None
        if self.isAttached():
            percent = self.getPercentAttr().get()
            evilPar = self.networkNode.metaParent.listConnections()[0]
            ep = None
            if isMetaNodeOfType(evilPar,'Evil'):
                ep = evilPar
        
        #list children for re attach children nodes        
        allChildren = self.listEvilChildren()
        allChildren = map(lambda x: Evil('', node = x.name()), allChildren)        
        childPer = {}
        for child in allChildren:
            childPer[child] = child.getPercentAttr().get()
            child.detach()    
            
            
        ecurve = self.delete()
        newEvil = Evil(ecurve, numJoints = int(numJoints), radius = radius, taper = taper)
        
        for child in allChildren:
            newEvil.attachEvil(child, childPer[child])
        
        
        if not percent == None:
            Evil('', node = ep).attachEvil(newEvil, percent)
        
            
        return newEvil
        
    def getGrowAttr(self):
        '''
        gets the attribute that causes the evil to grow
        return:
            the attribute object
        '''
        growGrp = self.networkNode.growGrp.listConnections()[0]
        attr = self.networkNode.growAttr.get()
        return PyNode(growGrp.attr(attr))
        
    def getRotateAttr(self):
        '''
        gets the attribute that causes the evil to rotate around parent
        return:
            the attribute if isAttached to another evil, else None    
        '''
        if not self.isAttached():
            return None
        rotateGrp = self.networkNode.rotateGrp.listConnections()[0]
        attr = self.networkNode.rotateAttr.get()
        return PyNode(rotateGrp.attr(attr))
        
    def getPercentAttr(self):
        '''
        gets the attribute that causes the evil to move along parent
        return:
            the attribute, if isAttached to another evil, else None    
        '''
        if not self.isAttached():
            return None
        percentGrp = self.networkNode.attachPoc.listConnections()[0]
        attr = self.networkNode.percentAttr.get()
        return PyNode(percentGrp.attr(attr))
    
    def listEvilChildren(self):
        '''
        returns a list of all the Evil Children directly attached to this Evil
        '''
        return self.networkNode.evilChildren.listConnections()
        
    def recreateDownChain(self, startTime, endTime):
        '''
        generates new evil down the chain
        '''
        
        
        #new start Time keying
        currentTime(startTime)
        self.getGrowAttr().set(0)
        setKeyframe(self.getGrowAttr())
        self.keyAnims()
        
        
        #new end time keying
        currentTime(endTime)
        self.getGrowAttr().set(50)
        setKeyframe(self.getGrowAttr())
        self.randomizeAnims(self.networkNode.radius.get()*2)
        self.keyAnims()
        
        for child in self.listEvilChildren():
            child = Evil('', node = child)
            #get new values
            ratio = child.getPercentAttr().get()
            newRadius = (self.networkNode.radius.get() - ((1-self.networkNode.taper.get())*self.networkNode.radius.get())*ratio)
            offsetTime = endTime -startTime
            newStartTime = offsetTime * ratio +startTime
            newEndTime = offsetTime + newStartTime
            
            #recreate child curve
            child = child.recreate(radius = newRadius)
            child.recreateDownChain(newStartTime, newEndTime)
        
        currentTime(startTime)

class VillageHouse(MetaNode):
    def __init__(self, node = None):
        '''
        creates a house based on random points
        '''
        if node:
            if objExists(node):
                node = PyNode(node)
                if( isMetaNode(node) and node.metaType.get() == 'VillageHouse'):
                    self.networkNode = node
                else:
                    printError("VillageHouse: node %s is not a VillageHouse metaNode"%(node))
            else:
                printError("VillageHouse: node %s doesn't exist"%(node))
        else:
            MetaNode.__init__( self, "VillageHouse", 1.0, "a village house")
            #add some variables to the meta
            self.networkNode.addAttr('houseParts', dt = 'string', m=1)
            self.networkNode.setAttr("housePartsDirectory", "C:/Users/Jason/LampLighter/LL project/scenes/models/house/for import/low", f=1)
            
            #door
            hasRightDoor = random.random() < .5
            hasLeftDoor = 1-hasRightDoor
            self.networkNode.setAttr("hasRightDoor", hasRightDoor, f=1)
            self.networkNode.setAttr("hasLeftDoor", hasLeftDoor, f=1)
            
            #trim
            hasTrim = random.random() < .75
            hasFlattenedTrim = 0 #if false, has ribbed Trim
            hasTrimBase = 0
            if hasTrim:
                hasFlattenedTrim = random.random() < .5
                hasTrimBase = random.random() < .8            
            #meta trim
            self.networkNode.setAttr("hasTrim", hasTrim, f=1)
            self.networkNode.setAttr("hasFlattenedTrim", hasFlattenedTrim, f=1)
            self.networkNode.setAttr("hasTrimBase", hasTrimBase, f=1)
                
            #side accent trim 
            hasSideAccentTrim = random.random() < .5
            hasSideAccentTrimCenter = 0
            hasSideAccentTrimCorners = 0
            if hasSideAccentTrim:
                hasSideAccentCorners = random.random() < .75
                if hasSideAccentCorners:
                    hasSideAccentTrimCenter = random.random() < .6
                else:
                    hasSideAccentTrimCenter = 1
            hasBackAccentTrim = random.random() < .25
            hasBackAccentTrimCenter = 0
            hasBackAccentTrimCorners = 0
            if hasBackAccentTrim:
                hasBackAccentCorners = random.random() < .75
                if hasBackAccentCorners:
                    hasBackAccentTrimCenter = .6
                else:
                    hasBackAccentTrimCenter = 1
            hasFrontAccentTrim = random.random() < .1
            hasFrontAccentTrimCenter = 0
            hasFrontAccentTrimCorners = 0
            if hasFrontAccentTrim:
                hasFrontAccentTrimCorners = random.random() < .75
                if hasFrontAccentTrimCorners:
                    hasFrontAccentTrimCenter = .6
                else:
                    hasFrontAccentTrimCenter = 1    
            #side accent trim meta
            self.networkNode.setAttr("hasSideAccentTrim", hasSideAccentTrim, f=1)
            self.networkNode.setAttr("hasSideAccentTrimCenter", hasSideAccentTrimCenter, f=1)
            self.networkNode.setAttr("hasSideAccentTrimCorners", hasSideAccentTrimCorners, f=1)
            self.networkNode.setAttr("hasBackAccentTrim", hasBackAccentTrim, f=1)
            self.networkNode.setAttr("hasBackAccentTrimCenter", hasBackAccentTrimCenter, f=1)
            self.networkNode.setAttr("hasBackAccentTrimCorners", hasBackAccentTrimCorners, f=1)
            self.networkNode.setAttr("hasFrontAccentTrim", hasFrontAccentTrim, f=1)
            self.networkNode.setAttr("hasFrontAccentTrimCenter", hasFrontAccentTrimCenter, f=1)
            self.networkNode.setAttr("hasFrontAccentTrimCorners", hasFrontAccentTrimCorners, f=1)
            
            #side addition
            hasLeftSideAddition = random.random() < .5 #has side addition on both sides on left
            hasRightSideAddition = random.random() < .5 #has side addition on both sides on right
            hasBackAddition = random.random() < .3
            
            #side addition meta
            self.networkNode.setAttr("hasLeftSideAddition", hasLeftSideAddition, f=1)
            self.networkNode.setAttr("hasRightSideAddition", hasRightSideAddition, f=1)
            self.networkNode.setAttr("hasBackAddition", hasBackAddition, f=1)
            
            #roof accent arc/awning        
            hasRoofAccentLeft = random.random() < .75
            hasRoofAccentRight = random.random() < .75
            hasLeftAwning = 0 #if not should have arcs on left
            hasRightAwning = 0 # if not should have arcs on right
            if hasRoofAccentLeft:
                hasLeftAwning = random.random() < .5
            if hasRoofAccentRight:
                hasRightAwning = random.random() < .5
            hasRoofFrontAccent = random.random() < .8
            hasRoofBackAccent = random.random() < .6
            hasFrontAwning = 0
            hasBackAwning = 0
            if hasRoofFrontAccent:
                hasFrontAwning = random.random() < .5
            if hasRoofBackAccent:
                hasBackAwning = random.random() < .5    
            
            #roof accent arc/awning meta
            self.networkNode.setAttr("hasRoofAccentLeft", hasRoofAccentLeft, f=1)
            self.networkNode.setAttr("hasRoofAccentRight", hasRoofAccentRight, f=1)
            self.networkNode.setAttr("hasLeftAwning", hasLeftAwning, f=1)
            self.networkNode.setAttr("hasRightAwning", hasRightAwning, f=1)
            self.networkNode.setAttr("hasRoofFrontAccent", hasRoofFrontAccent, f=1)
            self.networkNode.setAttr("hasRoofBackAccent", hasRoofBackAccent, f=1)
            self.networkNode.setAttr("hasFrontAwning", hasFrontAwning, f=1)
            self.networkNode.setAttr("hasBackAwning", hasBackAwning, f=1)
            
                
            #roof cylinder/window
            hasFrontRoofCylinder = random.random() < .2
            hasRightRoofCylinder = 0
            hasLeftRoofCylinder = 0
            hasBackRoofCylinder = 0
            if not (hasRightSideAddition or hasLeftSideAddition):
                hasRightRoofCylinder = random.random() < .2
            if not (hasRightSideAddition or hasLeftSideAddition):
                hasLeftRoofCylinder = random.random() < .2
            if not hasBackAddition:
                hasBackRoofCylinder = random.random() < .2
            hasFrontWindow = 0
            hasBackWindow = 0
            hasLeftWindow = 0
            hasRightWindow = 0    
            if hasBackRoofCylinder:
                hasBackWindow = random.random() < .2
            if hasFrontRoofCylinder:
                hasFrontWindow = random.random() < .2
            if hasLeftRoofCylinder:
                hasLeftWindow = random.random() < .2
            if hasRightRoofCylinder:
                hasRightWindow = random.random() < .2
            #roof cylinder/window meta
            self.networkNode.setAttr("hasFrontWindow",hasFrontWindow,f=1)
            self.networkNode.setAttr("hasBackWindow",hasBackWindow,f=1)
            self.networkNode.setAttr("hasRightWindow",hasRightWindow,f=1)
            self.networkNode.setAttr("hasLeftWindow",hasLeftWindow,f=1)
            self.networkNode.setAttr("hasFrontRoofCylinder",hasFrontRoofCylinder,f=1)
            self.networkNode.setAttr("hasBackRoofCylinder",hasBackRoofCylinder,f=1)
            self.networkNode.setAttr("hasRightRoofCylinder", hasRightRoofCylinder,f=1)
            self.networkNode.setAttr("hasLeftRoofCylinder",hasLeftRoofCylinder,f=1)    
                    
            #put together the house    
            self.putTogether()
        
    def putTogether(self):
        '''
        imports all the house pieces and to create house
        if house already put together, deletes all then puts together again
        '''
        oldHouse = None
        try:
            oldHouse = self.networkNode.house.listConnections()
        except:
            pass
        oldHouseTrans = None
        oldHouseRot = None
        oldHouseScale = None
        loc = spaceLocator()
        if oldHouse:
            #connect a temp locator, so deletion doesn't delete self.networkNode
            connectToMeta(loc, self.networkNode, 'house')
            oldHouseTrans = oldHouse[0].translate.get()
            oldHouseRot = oldHouse[0].rotate.get()
            oldHouseScale = oldHouse[0].scale.get()
            delete(oldHouse[0])
        
        #import the house base
        houseBase = self.importHousePart('main_house')
        connectToMeta(houseBase, self.networkNode, 'house')
        
        #delete temp locator
        delete(loc)
        
        #label with name
        houseBase.attr("type").set(18)    
        houseBase.otherType.set(houseBase.name())
        
        #addRoof
        roof = self.importHousePart('roof')
        self.attachTo(roof)
        
        #add roof corners
        bumps = self.importHousePart("roof_corner_bump")
        self.attachTo(bumps)
        
        #door
        hasRightDoor = self.networkNode.hasRightDoor.get()
        hasLeftDoor = self.networkNode.hasLeftDoor.get()
        if hasRightDoor:
            rdoor = self.importHousePart("right_door")
            self.attachTo(rdoor)
        if hasLeftDoor:
            ldoor = self.importHousePart("left_door")
            self.attachTo(ldoor)
        
        #add trim to house
        hasTrim = self.networkNode.hasTrim.get()
        hasFlattenedTrim = self.networkNode.hasFlattenedTrim.get()
        hasTrimBase = self.networkNode.hasTrimBase.get()
        if hasTrim:
            if hasFlattenedTrim:
                trim = self.importHousePart("flattened_trim")
                self.attachTo(trim)
            else:
                trim = self.importHousePart("ribbed_trim")
                self.attachTo(trim)
        if hasTrimBase:
            trimBase = self.importHousePart("trim_base")
            self.attachTo(trimBase)
        
        #side accent trim meta
        #sideAccentTrim = self.networkNode.hasSideAccentTrim.get()
        hasSideAccentTrimCenter = self.networkNode.hasSideAccentTrimCenter.get()
        hasSideAccentTrimCorners = self.networkNode.hasSideAccentTrimCorners.get()
        #hasBackAccentTrim = self.networkNode.hasBackAccentTrim.get()
        hasBackAccentTrimCenter = self.networkNode.hasBackAccentTrimCenter.get()
        hasBackAccentTrimCorners = self.networkNode.hasBackAccentTrimCorners.get()
        #hasFrontAccentTrim = self.networkNode.hasFrontAccentTrim.get()
        hasFrontAccentTrimCenter = self.networkNode.hasFrontAccentTrimCenter.get()
        hasFrontAccentTrimCorners = self.networkNode.hasFrontAccentTrimCorners.get()
        if hasSideAccentTrimCenter:
            sideAccentTrim = self.importHousePart("side_accent_trim_center")
            self.attachTo(sideAccentTrim,90)
            sideAccentTrim = self.importHousePart("side_accent_trim_center")
            self.attachTo(sideAccentTrim,270)
        if hasSideAccentTrimCorners:
            sideAccentTrim = self.importHousePart("side_accent_trim_corners")
            self.attachTo(sideAccentTrim,90)
            sideAccentTrim = self.importHousePart("side_accent_trim_corners")
            self.attachTo(sideAccentTrim,270)
        if hasBackAccentTrimCorners:
            sideAccentTrim = self.importHousePart("side_accent_trim_corners")
            self.attachTo(sideAccentTrim)
        if hasBackAccentTrimCenter:
            sideAccentTrim = self.importHousePart("side_accent_trim_center")
            self.attachTo(sideAccentTrim,180)
        if hasFrontAccentTrimCorners:
            sideAccentTrim = self.importHousePart("side_accent_trim_corners")
            self.attachTo(sideAccentTrim)
        if hasFrontAccentTrimCenter:
            sideAccentTrim = self.importHousePart("side_accent_trim_center")
            self.attachTo(sideAccentTrim)
            
        
        #add additions
        hasLeftSideAddition = self.networkNode.hasLeftSideAddition.get()
        hasRightSideAddition = self.networkNode.hasRightSideAddition.get()
        hasBackAddition = self.networkNode.hasBackAddition.get()
        if hasLeftSideAddition:
            rightAddition = self.importHousePart("side_addition_right")
            leftAddition = self.importHousePart("side_addition_left")
            self.attachTo(rightAddition,90)
            self.attachTo(leftAddition,270)
        if hasRightSideAddition:
            rightAddition = self.importHousePart("side_addition_left")
            leftAddition = self.importHousePart("side_addition_right")
            self.attachTo(rightAddition,90)
            self.attachTo(leftAddition,270)
        if hasBackAddition:
            rightAddition = self.importHousePart("side_addition_right")
            leftAddition = self.importHousePart("side_addition_left")
            self.attachTo(rightAddition,180)
            self.attachTo(leftAddition,180)
        
        
            
        #add roof accent arc/awning
        hasRoofAccentLeft = self.networkNode.hasRoofAccentLeft.get()
        hasRoofAccentRight = self.networkNode.hasRoofAccentRight.get()
        hasLeftAwning = self.networkNode.hasLeftAwning.get()
        hasRightAwning = self.networkNode.hasRightAwning.get()
        hasRoofFrontAccent = self.networkNode.hasRoofFrontAccent.get()
        hasRoofBackAccent = self.networkNode.hasRoofBackAccent.get()
        hasFrontAwning = self.networkNode.hasFrontAwning.get()
        hasBackAwning = self.networkNode.hasBackAwning.get()    
        if hasRoofAccentLeft:
            if hasLeftAwning:
                awning = self.importHousePart("roof_accent_awning")
                self.attachTo(awning,270)
            else:
                arc = self.importHousePart("roof_accent_arc")
                self.attachTo(arc, 270)
        if hasRoofAccentRight:
            if hasRightAwning:
                awning = self.importHousePart("roof_accent_awning")
                self.attachTo(awning,90)
            else:
                arc = self.importHousePart("roof_accent_arc")
                self.attachTo(arc, 90)
        if hasRoofFrontAccent:
            if hasFrontAwning:
                awning = self.importHousePart("roof_accent_awning")
                self.attachTo(awning)
            else:
                arc = self.importHousePart("roof_accent_arc")
                self.attachTo(arc)
        if hasRoofBackAccent:
            if hasBackAwning:
                awning = self.importHousePart("roof_accent_awning")
                self.attachTo(awning,180)
            else:
                arc = self.importHousePart("roof_accent_arc")
                self.attachTo(arc, 180)
        
        
        
        #add windows/cylinders
        hasFrontWindow = self.networkNode.hasFrontWindow.get()
        hasBackWindow = self.networkNode.hasBackWindow.get()
        hasRightWindow = self.networkNode.hasRightWindow.get()
        hasLeftWindow = self.networkNode.hasLeftWindow.get()
        hasFrontRoofCylinder = self.networkNode.hasFrontRoofCylinder.get()
        hasBackRoofCylinder = self.networkNode.hasBackRoofCylinder.get()
        hasRightRoofCylinder = self.networkNode.hasRightRoofCylinder.get()
        hasLeftRoofCylinder = self.networkNode.hasLeftRoofCylinder.get()    
        if hasFrontWindow:
            houseWindow = self.importHousePart("window")
            self.attachTo(houseWindow)
        if hasBackWindow:
            houseWindow = self.importHousePart("window")
            self.attachTo(houseWindow,180)
        if hasRightWindow:
            houseWindow = self.importHousePart("window")
            self.attachTo(houseWindow,90)
        if hasLeftWindow:
            houseWindow = self.importHousePart("window")
            self.attachTo(houseWindow,270)
        if hasFrontRoofCylinder:
            roofCyl = self.importHousePart("roof_cylinder")
            self.attachTo(roofCyl)
        if hasBackRoofCylinder:
            roofCyl = self.importHousePart("roof_cylinder")
            self.attachTo(roofCyl,180)
        if hasRightRoofCylinder:
            roofCyl = self.importHousePart("roof_cylinder")
            self.attachTo(roofCyl,90)
        if hasLeftRoofCylinder:
            roofCyl = self.importHousePart("roof_cylinder")
            self.attachTo(roofCyl,270)
        
        
        
        if oldHouse:
            print str(oldHouse) + "!!!"
            houseBase.translate.set(oldHouseTrans)
            houseBase.rotate.set(oldHouseRot)
            houseBase.scale.set(oldHouseScale)
            
            
            
    def importHousePart(self, obj):
        '''
        imports object into scene from the house parts directory
        obj:
            the file name of the obj in the houseparts directory
        return:
            the obj that was imported
        '''
        if obj.endswith(".ma"):
            obj = obj.replace(".ma", "")
        all = ls(dag = 1, type = 'joint')
        importFile(self.networkNode.housePartsDirectory.get() + "/" + obj + ".ma", defaultNamespace = 1)
        new =  ls(dag =1, type = 'joint')
        for obj in new:
            if not obj in all:
                return obj
                
    def attachTo(self, obj, rot=0):
        '''
        attaches the object to the house
        obj:
            the object to attach
        rotate:
            the amount to rotate around Y, to match possible sides
        '''
        house = self.networkNode.house.listConnections()[0]
        obj = PyNode(obj)
        obj.scale.set(house.scale.get())
        alignPointOrient(house, obj, 1,1)
        rotate(obj, [0,rot,0],os=1, r=1)
        parent(obj, house)
        obj.inverseScale.disconnect()
        connectToMeta(obj, self.networkNode, "houseParts")
    
    def alignToObj(self, obj, point =1, orient = 1):
        '''
        aligns the house to the given object
        obj:
            object to align to
        point:
            should align by point
        orient:
            should aling by rotation
        '''
        if not objExists(obj):
            raise Exception("VillageHouse.alignToObj: object given,%s , doesn't exist"%obj)
        obj = PyNode(obj)
        house = self.networkNode.house.listConnections()[0]
        alignPointOrient(obj, house, point, orient)
        
    
        
    
'''
THINGS TO POSSIBLY CHANGE FOR FURTHER DEVELOPMENT

connectToMeta and connectChainToMeta should look like      MetaObj.connectTo(obj, attrName)
    makes for a more fundamentally object oriented programming

each chain should be a meta structure, and have index, name, etc

should be able to create ik and fk chains as a method
    
metaNodes can be created by passing in attributes and by existing nodes, by metaNodes have to be passed many attrs to create by node
possible to create by factory,  MetaObj().create(....) and MetaObj().node(...) 
    separates the object to be created by multiple means easier and more efficent
    also allows possible calls like Meta().isMetaNode(obj), for making places for meta outside functions
    

possibly get side and bodypart from joint labels
    pro, less input into creation
    con, component can possible be labels the same if both joints have same label, (if based on start joint l_leg and l_thigh could have same name) 
    
    
possible interface classes for metaIK, metaFK, and MetaDyn for methods to help with .isIK, .getIKAnim and such

make anim a class which adds the node attrs\fbik, creates shapes, swaps shapes, etc.
'''
        
