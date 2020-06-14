from pymel.all import *
import maya.cmds as mc;
from os import *
import snake

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
    
def reversible_IKFK_spine(name,start,end):
    
    bc = shadingNode('blendColors',au=True)
    bc.color1R.set(0)
    bc.color2R.set(1)
    
    #Get starting chain and length
    bones = get_chain(start,end); g=1; h=0; i=0; j=1; k=0; l=0; f=0
    bl = len(bones)-1
    
    #Creates switch component
    switch = group(n=(name+'_IKFK_switch'),em=True)
    addAttr(switch,ln='IK_0_to_FK_1',at='double',min=0,max=1,k=True)
    addAttr(switch,ln='show_FK_anim',at='double',min=0,max=1,k=True)
    addAttr(switch,ln='show_reverse_FK_anim',at='double',min=0,max=1,k=True)
    
    switch.IK_0_to_FK_1.set(1)
    switch.show_FK_anim.set(1)
    switch.show_reverse_FK_anim.set(1)
    switch.IK_0_to_FK_1 >> bc.blender
    
    ats = ['translateX','rotateX','scaleX','translateY','rotateY','scaleY','translateZ','rotateZ','scaleZ','visibility']
    ans = ['translateX','translateY','translateZ','scaleX','scaleY','scaleZ','visibility','radius']
    for at in ats:
        setAttr((name+'_IKFK_switch.'+at),k=False,l=True,cb=False)
    
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
    
    for f in FK:
        if f.endswith('_anim'):
            for a in ans:
                setAttr((f+'.'+a),k=False,l=True,cb=False)
            ctrl = circle(ch=0,nr=(0,0,1),r=1.25)
            shape = listRelatives(ctrl, shapes=True)
            parent(shape,f,r=True,s=True)
            delete(ctrl)
        PyNode(f).drawStyle.set(2)
            
    for r in rev_FK:
        if r.endswith('_anim'):
            for a in ans:
                setAttr((r+'.'+a),k=False,l=True,cb=False)
            ctrl = circle(ch=0,nr=(0,0,1),r=.75)
            shape = listRelatives(ctrl, shapes=True)
            parent(shape,r,r=True,s=True)
            delete(ctrl)
        PyNode(r).drawStyle.set(2)

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
    for all in bones:
        parentConstraint(IK[i],all,mo=False,w=0)
        parentConstraint(rev_FK[j],all,mo=False,w=1)

        pCAttrs = listAttr(all+'_parentConstraint1',s=True,r=True,w=True,c=True,st=['*W0','*W1'])
        
        a1 = Attribute(all+'_parentConstraint1.'+pCAttrs[0])
        a2 = Attribute(all+'_parentConstraint1.'+pCAttrs[1])  
        
        switch.IK_0_to_FK_1 >> a2
        bc.outputR >> a1
        
        i=i+1;j=j+2
    
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
        
        at = Attribute(name+'_IKFK_switch.FK_anim_'+str(g))
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
    component_grp = group(n='component_grp')
    
    select(IK[0],IK_curve,IKH)
    IK_grp = group(n=(name+'_IK_group'),em=False,p=component_grp)
    IK_grp.visibility.set(0)
    select(cl=True)
    
    select(pv_grps)
    pvs = group(n=(name+'_FK_rev_guide_pvs'),em=False)
    select(cl=True)
    
    select(rev_IKs)
    rev_IK_grp = group(n=(name+'_FK_rev_guide_iks'),em=False)
    select(cl=True)
    
    select(pvs,rev_guides[0],rev_IK_grp)
    rev_guide_grp = group(n=(name+'_FK_rev_guide_group'),em=False)
    rev_guide_grp.visibility.set(0)
    select(cl=True)
    
    select(FK[0],rev_FK[0],rev_guide_grp)
    FK_grp = group(n=(name+'_FK_group'),em=False,p=component_grp)
    select(cl=True)
    
    select(pin[0],cl[1],loc_grp,pin_curve,pin_ik_curve,pin_IKH)
    pin_grp = group(n=(name+'_pin_group'),em=False,p=component_grp)
    pin_grp.visibility.set(0)
    select(cl=True)
    
    select(sine_curve,sine[0],sine_IKH,sineDef)
    sine_grp = group(n=(name+'_sine_group'),em=False,p=component_grp)
    sine_grp.visibility.set(0)
    select(cl=True)
    
    parent(switch,component_grp)
    select(cl=True)