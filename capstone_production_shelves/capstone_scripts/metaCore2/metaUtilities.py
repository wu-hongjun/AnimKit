from pymel.all import *
import maya.cmds as mc
import os
#=======================================================================================================================================================#
def aligner(objs,target,position = True,rotation = True,pivot = False):
    for obj in objs:
        if position == True:
            target_position = xform(target, q= True, ws=True, rp=True);
            move(target_position[0],target_position[1],target_position[2], obj, rpr = True);
        if rotation == True:
            target_rotation = xform(target, q=True, ws = True, ro = True);
            xform(obj, ws=True,ro=(target_rotation[0],target_rotation[1],target_rotation[2]))
        if pivot == True:
            target_pivot = xform(target, q= True, ws=True, rp=True);
            move(target_pivot[0],target_pivot[1],target_pivot[2], obj + '.rotatePivot', obj + '.scalePivot', rpr = True)

def align_between(objs,targets,position = True,rotation = False,pivot = False):
    if position == True:
        target_position = xform(target, q= True, ws=True, rp=True);
        move(target_position[0],target_position[1],target_position[2], obj, rpr = True);
    if pivot == True:
        target_pivot = xform(target, q= True, ws=True, rp=True);
        move(target_pivot[0],target_pivot[1],target_pivot[2], obj + '.rotatePivot', obj + '.scalePivot', rpr = True)

#=======================================================================================================================================================#
def odd_eye(side,eye_joint,geo_grp,front_loc,top_loc,side_loc):
    geo_grp = PyNode(geo_grp)
    eye_joint = PyNode(eye_joint)
    meshes = listRelatives(geo_grp,c=True)
    front_loc = PyNode(front_loc)
    top_loc = PyNode(top_loc)
    side_loc = PyNode(side_loc)
    center_loc = spaceLocator(n = side + '_center_eye_loc',p = (0,0,0))
    scale_correct = group(center_loc,n = geo_grp + '_correction')
    
    #Get Center
    info = geo_grp.boundingBox()
    tx = (info[0][0] + info[1][0])/2.00
    ty = (info[0][1] + info[1][1])/2.00
    tz = (info[0][2] + info[1][2])/2.00
    scale_correct.translate.set(tx,ty,tz)
    
    delete(aimConstraint(front_loc,scale_correct,aim = (0,0,1),u = (0,1,0),wuo = top_loc,mo = False))
    
    data = []
    cl_pos = xform(center_loc, q= True, ws=True, rp=True);
    for loc in [side_loc,top_loc,front_loc]:
        loc_pos = xform(loc, q= True, ws=True, rp=True);
        dist = distanceDimension(sp=(cl_pos[0],cl_pos[1],cl_pos[2]),ep=(loc_pos[0],loc_pos[1],loc_pos[2]))
        data.append(dist.distance.get())
        delete(dist.getParent())
    #print data

    scale_correct.scale.set(data)
    parent(geo_grp,scale_correct)
    aligner([geo_grp],center_loc,position = False,rotation = False,pivot = True)
    delete(front_loc,top_loc,side_loc,center_loc)
    makeIdentity(geo_grp,t = True,r = True,s = True,a= True)
    parent(geo_grp,w= True)
    geo_grp.scale.set(1,1,1)
    #for mesh in meshes: skinCluster(eye_joint,mesh,n = mesh + '_skin',tsb = True, mi = 1, sm = 1, nw = 1)
    geo_grp.scale.set(data)
    parent(geo_grp,scale_correct)
    #orientConstraint(eye_joint,geo_grp,mo = True)
    select(cl = True)

def run_SDK_script(file_name):
    if not file_name.endswith('.py'): file_name = file_name + '.py'
    thisDir = os.path.dirname(mc.file(q=1, loc=1)) + '/set_driven_keys'
    items = os.listdir(thisDir)
    if file_name in items:
        script = thisDir + '/' + file_name 
        string = open(script,'r')
        code = {}
        run_code = compile(string.read(),'<string>','exec')
        exec run_code in code
    
def get_chain(start,end):
    rn = len(PyNode(start).longName()[1:].split('|'))-1
    output = PyNode(end).longName()[1:].split('|')[rn:]
    result = [PyNode(x) for x in output] #list Comprehension
    return result

def create_node(type,n = None):
    node = shadingNode(type,au=True)
    if n: node.rename(n)
    attrs = node.listAttr(w=True,u=True,v=True,k=True)
    for attr in attrs: setAttr(attr,k=False,cb=False)
    return node

def joint_orient(bone):
    try:
        rotation = bone.rotate.get()
    except:
        bone = PyNode(bone)
        rotation = bone.rotate.get()
    bone.rotate.set(0,0,0)
    bone.jointOrient.set(rotation)

def duplicate_chain(start ,end, rep = '', wi = '',reverse = False):
    bones = get_chain(start,end)
    select(cl=True)
    new_bones = []
    i = 0

    if reverse == True:
        bones.reverse()
    
    for all in bones:
        r = all.radius.get()
        new_bone = joint(n=(all.replace('_end_','_bind_').replace(rep,wi)),rad=(r*2),p=(0,0,0))
        aligner([new_bone],all)
        new_bones.append(new_bone)
        joint_orient(new_bone)
        select(cl=True)
    
    if len(bones) > 1: 
        for all in new_bones[1:]:
            parent(all,new_bones[i])
            i += 1
    
    select(cl=True)
    return new_bones

def duplicate_custom_chain(chain, rep = '', wi = '',reverse = False):
    bones = chain
    select(cl=True)
    new_bones = []
    i = 0

    if reverse == True:
        bones.reverse()
    
    for all in bones:
        r = all.radius.get()
        new_bone = joint(n=(all.replace('_end_','_bind_').replace(rep,wi)),rad=(r*2),p=(0,0,0))
        aligner([new_bone],all)
        new_bones.append(new_bone)
        joint_orient(new_bone)
        select(cl=True)
    
    if len(bones) > 1: 
        for all in new_bones[1:]:
            parent(all,new_bones[i])
            i += 1
    
    select(cl=True)
    return new_bones

def stacked_chain(start ,end, amnt = 1, rep = '', wi = '',reverse = False):
    bones = duplicate_chain(start ,end, rep = rep, wi = wi,reverse = reverse);
    chain = []
    parent(bones[1:],w=True);
    select(cl=True)
    i = 0
    if amnt < 0:
        amnt = 0;
    if amnt > 0:
        for all in bones:
            grps = []
            for j in range(0,amnt):
                select(cl=True)
                null = joint(n=(all + '_null' + str(j + 1)))
                aligner([null],all);
                joint_orient(null)
                if grps:
                    parent(null,grps[j-1])
                grps.append(null)
                chain.append(null)
                select(cl=True)
            parent(all,null)
            chain.append(PyNode(all))
            if i > 0:
                parent(grps[0],bones[i-1])
            i += 1
    chain.append(bones[-1])
    select(cl=True)
    return chain
    
def lock_and_hide_attrs(objs,attrs):
    for obj in objs:
        for attr in attrs:
            connection = listConnections(obj + '.' + attr, s=True,d=False)
            if connection:
                setAttr(obj + '.' + attr,l=False,cb=False,k=False)
            else:
                setAttr(obj + '.' + attr,l=True,cb=False,k=False)

def make_spline(name,start = None,end = None,chain = None, spans = 8, smooth = True):
    try:
        bones = get_chain(start,end)
    except:
        bones = chain
    i = 0
    co = []
    k=[]
    
    for all in bones:
        alPos = xform(all, q= True, ws=True, rp=True);
        co.append((alPos[0],alPos[1],alPos[2]))
        k.append(i)
        i += 1
    
    cv = curve(n=(name + '_cv'),d=1,p=co,k=k)
    if smooth == True:
        rebuildCurve(cv,rt=0,ch=0,s=spans,d=3,tol=0)
    xform(cv,cpc=True)
    delete(cv,ch=True)
    select(cl=True)
    
    return cv

def make_ribbon(name,start = None,end = None, chain = None, spans = 8, smooth = True, spread = True):
    cv_a = make_spline(name + '1',start = start,end = end,chain = chain, spans = spans, smooth = smooth)
    cv_b = make_spline(name + '2',start = start,end = end,chain = chain, spans = spans, smooth = smooth)
    if spread == True:
        cv_a.tx.set(1)
        cv_b.tx.set(-1)
    
    ribbon = loft(cv_a,cv_b,n=(name + '_ribbon'),ss=1,d=3,rn=False,po=False,rsn=True,u=True,ch=False)[0]
    delete(cv_a,cv_b)
    select(cl=True)
    
    return ribbon

def nurbs_constraint(nurb,obj,u,v):
    zero_null = group(n=obj+'_zero_null',em=True)
    con = parentConstraint(zero_null, obj, mo=True)
    info = PyNode(pointOnSurface(nurb,top = True, u=u, v=v, ch=True))
    nurbsMatrix = createNode('fourByFourMatrix')
    info.normalizedNormalX >> nurbsMatrix.in20
    info.normalizedNormalY >> nurbsMatrix.in21
    info.normalizedNormalZ >> nurbsMatrix.in22
    info.normalizedTangentUX >> nurbsMatrix.in10
    info.normalizedTangentUY >> nurbsMatrix.in11
    info.normalizedTangentUZ >> nurbsMatrix.in12
    info.normalizedTangentVX >> nurbsMatrix.in00
    info.normalizedTangentVY >> nurbsMatrix.in01
    info.normalizedTangentVZ >> nurbsMatrix.in02
    info.positionX >> nurbsMatrix.in30
    info.positionY >> nurbsMatrix.in31
    info.positionZ >> nurbsMatrix.in32
    nurbsMatrix.output >> con.constraintParentInverseMatrix
    
    return zero_null

def curve_constraint(nurb,obj,pr):
    info = PyNode(pointOnCurve(nurb,top = True, p=True, pr=pr, ch=True))
    try:
        info.result.position >> obj.translate
    except:
        info.result.position >> PyNode(obj).translate

def anim_finalize(anims):
    for a in anims:
        a.drawStyle.set(2)
        
def anim_shape_generator(objs,r=1.00):
    for obj in objs:
        circleS = circle(r=r,nr=(1,0,0),ch=0)[0]
        anim_shape = PyNode(circleS).getShapes()[0]
        parent(anim_shape,obj,r=True,s=True)
        anim_shape.rename(obj + 'Shape')
        delete(circleS)

def connect_objs_to_node(objs,network,attrName):
    network = PyNode(network);
    if len(objs) > 1:
        if network.hasAttr(attrName) == False:
            network.addAttr(attrName,dt = 'string',m=True)
        i= len(listConnections(network.attr(attrName)))
        for obj in objs:
            if obj.hasAttr('connected_to') == False:
                obj.addAttr('connected_to',at='message')
            obj.connected_to >> network.attr(attrName + '[' + str(i) + ']')
            i += 1
    else:
        obj = PyNode(objs[0])
        if network.hasAttr(attrName) == False:
            network.addAttr(attrName,dt = 'string')
            if obj.hasAttr('connected_to') == False:
                obj.addAttr('connected_to',at='message')
            obj.connected_to >> network.attr(attrName)
            
        else:
            if attributeQuery(attrName,n = network,m=True) == False:
                item = listConnections(network.attr(attrName))[0]
                network.deleteAttr(attrName)
                network.addAttr(attrName,dt = 'string',m=True)
                objs = [obj,item]
            i = 0
            for all in objs:
                if all.hasAttr('connected_to') == False:
                    all.addAttr('connected_to',at='message')
                all.connected_to >> network.attr(attrName + '[' + str(i) + ']')
                i += 1

def make_reverse_IK_locators(side,limb,type = 'foot'):
    name = side + '_' + limb
    ins = -1
    outs = 1
    
    if side == 'right':
        ins = 1
        outs = -1
    
    front = spaceLocator(n=(name + '_front_' + type + '_loc'))
    back = spaceLocator(n=(name + '_back_' + type + '_loc'))
    inner = spaceLocator(n=(name + '_inner_' + type + '_loc'))
    outer = spaceLocator(n=(name + '_outer_' + type + '_loc'))
    front.tz.set(1)
    back.tz.set(-1)
    inner.tx.set(ins)
    outer.tx.set(outs)
    
    grp = group(n=(name + '_' + type + '_grp'),em=True)
    parent([front,back,inner,outer],grp)
    if type == 'hand':
        middle = spaceLocator(n=(name + '_mid_' + type + '_loc'))
        parent(middle,grp)
    select(cl=True)
    
    return [grp,front,back,inner,outer]
def transfer_attrs(old_anim,new_anim,attrs):
    old_anim = PyNode(old_anim)
    new_anim = PyNode(new_anim)
    for all in attrs:
        if old_anim.getAttr(all,l=True) == True:
            old_anim.attr(all).unlock()
        ats = attributeQuery(all,n = old_anim,at = True)
        mins = attributeQuery(all,n = old_anim,min = True)[0]
        maxs = attributeQuery(all,n = old_anim,max = True)[0]
        dvs = attributeQuery(all,n = old_anim,ld = True)[0]
        
        new_anim.addAttr(all,at = ats,k=True)
        attribute = new_anim + '.' + all
        
        addAttr(attribute,e=True,min = mins)
        addAttr(attribute,e=True,max = maxs)
        addAttr(attribute,e=True,dv = dvs)
        new_anim.attr(all) >> old_anim.attr(all)

def check_constraint_connections(obj):
    attr = obj.listConnections(s=True,d=True, type = nt.Constraint)
    return list(set(attr))

def connection_change(con,replace_num,new_obj):
    new_obj = PyNode(new_obj)
    type = str(con.nodeType())
    original_object = PyNode(con.split('_' + type)[0])
    attributes = [Attribute(con + '.' + x) for x in listAttr(con,st = ['*W0','*W1'])]
    connections = [x.listConnections(p = True)[-1] for x in attributes]
    objs = [PyNode(x.split('W0')[0].split('W1')[0]) for x in listAttr(con,st = ['*W0','*W1'])]
    delete(con)
    for i in range(len(objs)):
        obj = objs[i]
        if i == replace_num: obj = new_obj
        if type == 'pointConstraint': new_con = pointConstraint(obj,original_object,mo = True)
        elif type == 'orientConstraint': new_con = orientConstraint(obj,original_object,mo = True)
        else: new_con = parentConstraint(obj,original_object,mo = True)
    new_attributes = [Attribute(new_con + '.' + x) for x in listAttr(new_con,st = ['*W0','*W1'])]
    for i in range(len(connections)): connections[i] >> new_attributes[i]
#=======================================================================================================================================================#
def ribbon_skin(nurbs,anims):
    weight = [0,0.1,0.4,0.7,0.9,1.0,0.9,0.7,0.4,0.1,0.0]
    shape = PyNode(nurbs).getShape()
    cvs = shape.cv[:]
    points = shape.cv[0][:]
    
    skin = listConnections(shape.create)[0]
    amount = len(cvs)/len(points)
    
    for i in range(amount-1):
        verts = shape.cv[i][:]
        for vert in verts:
            skinPercent(skin, vert, tv = [(anims[1],weight[i])])
            
def FKIK_switch(name,bones,IK,FK,type ='normal' ,v = 0.00):
    switch = group(n=(name + '_FKIK_switch'),em=True); i = 0
    aligner([switch],bones[0],position = False,rotation = False,pivot = True)
    lock_and_hide_attrs([switch],['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])
    
    if type == 'normal':
        addAttr(switch,ln='FKIK_switch',at='double',min=0,max=1,dv = v ,k=True)
        rev = create_node('reverse', n = name + '_switch_reverse')
        switch.FKIK_switch >> rev.inputX
    
    for all in bones:
        con = parentConstraint(IK[i],all,mo=True)
        if type == 'normal':
            parentConstraint(FK[i],all,mo=True)
            pCAttrs = listAttr(con,s=True,r=True,w=True,c=True,st=['*W0','*W1'])
            
            a1 = Attribute(con + '.' + pCAttrs[1])
            a2 = Attribute(con + '.' + pCAttrs[0])
           
            rev.outputX >> a1
            switch.FKIK_switch >> a2
        i += 1
    return switch

def FK_stretch(FK_joints):
    i=1;
    for all in FK_joints:
        setAttr(all + '.translateX',cb=False,k=False)
        lock_and_hide_attrs([all],['ty','tz','sx','sy','sz','v','radius'])
    
    for all in FK_joints[:-1]:
        bone = PyNode(all).getChildren()[0]
        addAttr(all,ln='stretch',at='double',min=0,dv=1,k=True)
        amnt = bone.translateX.get()
        md = create_node('multiplyDivide',n = all + '_stretch_md')
        md.input1X.set(amnt)
        PyNode(all).stretch >> md.input2X
        md.outputX >> bone.translateX
        i += 1
        
def IK_chain_stretch(IK_joints,IK_curve,network,switch):
    select(cl=True)
    cv = IK_curve
    network = PyNode(network)
    switch = PyNode(switch)
    norm_md = create_node('multiplyDivide',n = network + '_normalize')
    scale_md = create_node('multiplyDivide',n = network + '_scale')
    bc = create_node('blendColors',n = network + '_blend_colors')
    ci = create_node('curveInfo',n= network + '_curve_info')
    
    cv.worldSpace[0] >> ci.inputCurve
    
    ci.arcLength >> norm_md.input1X
    norm_md.operation.set(2)
    network.global_scale >> norm_md.input2X
    
    norm_md.outputX >> scale_md.input1X
    scale_md.input2X.set(ci.arcLength.get())
    scale_md.operation.set(2)
    
    switch.stretch >> bc.blender
    scale_md.outputX >> bc.color1R
    bc.color2.set(1,1,1)

    for jnts in IK_joints:
        bc.outputR >> jnts.scaleX
    select(cl=True)

def IK_chain_anim_make(name,IK_joints,IK_curve):
    select(cl=True); i = 0
    anims = []; grps = [];
    size = len(IK_joints)
    if size % 2 == 0:
        mid1 = IK_joints[(size + 1)/2]
        mid2 = IK_joints[((size + 1)/2)-1]
        joints = [IK_joints[0],mid1,IK_joints[-1]]
        for all in joints:
            anim = joint(n=(all.replace('joint','anim')),rad=5.00,p=(0,0,0))
            if i == 1:
                delete(parentConstraint(mid1,mid2,anim,mo=False,w=1))
            else:
                aligner([anim],all)
            rot = anim.rotate.get()
            anim.rotate.set(0,0,0)
            anim.jointOrient.set(rot)
            anims.append(anim)
            
            grp = group(n=(all.replace('joint','anim_zero_grp')),em=True)
            aligner([grp],anim)
            parent(anim,grp)
            grps.append(grp)
            
            lock_and_hide_attrs([anim],['sx','sy','sz','v','radius'])
            select(cl=True)
            i += 1
        
    else:
        joints = [IK_joints[0],IK_joints[size/2],IK_joints[-1]]
        for all in joints:
            anim = joint(n=(all.replace('joint','anim')),rad=5.00,p=(0,0,0))
            aligner([anim],all)
            rot = anim.rotate.get()
            anim.rotate.set(0,0,0)
            anim.jointOrient.set(rot)
            anims.append(anim)
            
            grp = group(n=(all.replace('joint','anim_zero_grp')),em=True)
            aligner([grp],anim)
            parent(anim,grp)
            grps.append(grp)
            
            lock_and_hide_attrs([anim],['sx','sy','sz','v','radius'])
            select(cl=True)
            
    for all in anims:
        c1 = circle(nr=(1,0,0),r=1.25,ch=0)[0]
        c2 = circle(nr=(0,1,0),r=1.25,ch=0)[0]
        c3 = circle(nr=(0,0,1),r=1.25,ch=0)[0]
        
        cs1 = c1.getShapes()[0]
        cs2 = c2.getShapes()[0]
        cs3 = c3.getShapes()[0]
        
        parent(cs1,cs2,cs3,all,r=True,s=True)
        delete(c1,c2,c3)   
        all.drawStyle.set(2)
    
    skinCluster(anims,IK_curve,tsb=True)
    
    anims[0].rename(name + '_bottom_IK_anim')
    anims[-1].rename(name + '_top_IK_anim')
    anims[1].rename(name + '_mid_IK_anim')
    
    return [grps,anims,joints]

def pole_vector(name,bone,r=0.75,distance = 5):
    items = IK_anim_make((name + '_PV'),r=r)
    grp = group(items[0],n=(name + '_PV_position_zero_grp'),em=True)
    PV = items[1]
    parent(items[0],grp)
    aligner([grp],bone)
    
    if name.startswith('left'):
        items[0].translate.set(0,-distance,0)
    elif name.startswith('right'):
        items[0].translate.set(0,distance,0)
    lock_and_hide_attrs([items[0]],['rx','ry','rz','sx','sy','sz'])
    lock_and_hide_attrs([PV],['sx','sy','sz','v','radius'])
    return [grp,PV]

def IK_anim_make(name,bone = None,r=0.75):
    name = name.replace('_bind_joint','')
    anim = joint(n=(name + '_anim'),rad = 2.50,p=(0,0,0))
    grp = group(n=(name + '_anim_zero_grp'),em=True)
    #anim.jointOrient.set(0,0,0)
    #anim.rotate.set(0,0,0)
    parent(anim,grp)
    if bone:
        aligner([grp],bone)
    
    c1 = circle(nr=(1,0,0),r=r,ch=0)[0]
    c2 = circle(nr=(0,1,0),r=r,ch=0)[0]
    c3 = circle(nr=(0,0,1),r=r,ch=0)[0]
        
    cs1 = c1.getShapes()[0]
    cs2 = c2.getShapes()[0]
    cs3 = c3.getShapes()[0]
    
    parent(cs1,anim,r=True,s=True)
    parent(cs2,anim,r=True,s=True)
    parent(cs3,anim,r=True,s=True)
    delete(c1,c2,c3)   
    anim.drawStyle.set(2)
    anim.jointOrient.set(0,0,0) 
    return [grp,anim]

def FKIK_anim_visibility(switch,IK_grp,FK_grp,style = 'normal'):
    IK_grp = PyNode(IK_grp)
    FK_grp = PyNode(FK_grp)
    name = switch.replace('_switch','')
    
    anim_rev = create_node('reverse', n = name + '_anim_vis_reverse')
    anim_md = create_node('multiplyDivide', n = name + '_anim_vis_multiply')
    anim_range = create_node('setRange', n = name + '_anim_vis_range')
        
    anim_md.input2.set(100,100,100)
    anim_range.max.set(1,1,1)
    anim_range.oldMax.set(1,1,1)
        
    switch.FKIK_switch >> anim_rev.inputX
    switch.FKIK_switch >> anim_md.input1X
    anim_rev.outputX >> anim_md.input1Y
    anim_md.output >> anim_range.value
        
    anim_range.outValueX >> IK_grp.visibility
    anim_range.outValueY >> FK_grp.visibility
        
    select(cl=True)

def network_grp_lock(name,start):
    select(name + '*_grp',add=True)
    if objExists(name + '*_zero_grp') == True:
        select(name + '*_zero_grp',d=True)
    if objExists(name + '*rev_foot_grp') == True:
        select(name + '*rev_foot_grp',d=True)
    if objExists(name + '*_component_grp|DO_NOT_TOUCH') == True:
        select(name + '*_component_grp|DO_NOT_TOUCH',add=True)
    objs = ls(sl=True)
    aligner(objs,start,position = False,rotation = False,pivot = True)
    lock_and_hide_attrs(objs,['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
    
def reverse_foot_setup(name,IK_Anim,front,back,inner,outer,toe,ball,ankle):
    IK_Anim = PyNode(IK_Anim)
    reverse_foot = []
    front = PyNode(front)
    back = PyNode(back)
    inner = PyNode(inner)
    outer = PyNode(outer)
    ball = PyNode(ball)
    ankle = PyNode(ankle)   
    toe = PyNode(toe)
    foot = [back,outer,inner,front,ball,ankle,ball,toe]
    fN = ['heel','inner_foot','outer_foot','rev_toe','rev_balltoe','rev_ankle','rev_rotate_toe','rev_toe_end']
    
    IK_Anim.addAttr('heel_to_toe',at='double',min=-180,max=180,dv=0,k=True)
    IK_Anim.addAttr('balltoe_lift',at='double',min=-90,max=90,dv=0,k=True)
    IK_Anim.addAttr('toe_lift',at = 'double',min = -90,max = 90, dv = 0, k=True)
    IK_Anim.addAttr('side_to_side',at='double',min=-90,max=90,dv=0,k=True)
    IK_Anim.addAttr('heel_pivot',at='double',min=-90,max=90,dv=0,k=True)
    IK_Anim.addAttr('toe_pivot',at='double',min=-90,max=90,dv=0,k=True)
    IK_Anim.addAttr('lean',at='double',min=-90,max=90,dv=0,k=True)

    for i in range(0,8):
        b = joint(n = (name + '_' + fN[i] + '_joint'),p=(0,0,0))
        aligner([b],foot[i])
        rot = b.rotate.get()
        if i > 3: rot = foot[3].jointOrient.get()
        b.jointOrient.set(rot)
        b.rotate.set(0,0,0)
        reverse_foot.append(b)
        if i > 0:
            if i == 6: parent(b,reverse_foot[i-3])
            else: parent(b,reverse_foot[i-1])
        else:
            rev_grp = group(n=(name + '_rev_foot_grp'),em=True)
            aligner([rev_grp],IK_Anim)
            parent(b,rev_grp)
        select(cl=True)
    
    #Reverse Foot nodes

    #Toe Lift
    rev_toe_rot = create_node('multiplyDivide',n = name + '_rev_rotate_toe_md')
    rev_toe_rot.input2X.set(-1)
    IK_Anim.toe_lift >> rev_toe_rot.input1X
    rev_toe_rot.outputX >> reverse_foot[-2].rotateX
    
    #Side to Side
    in_b = PyNode(reverse_foot[1])
    out_b = PyNode(reverse_foot[2])
        
    side_range = create_node('setRange',n = name + '_rev_foot_side_to_side_sr')
    rev_rot = create_node('multiplyDivide',n = name + '_rev_foot_side_to_side_md')
        
    side_range.min.set(-90,0,0)
    side_range.oldMin.set(-90,0,0)
    side_range.max.set(0,90,0)
    side_range.oldMax.set(0,90,0)
    IK_Anim.side_to_side >> side_range.valueX
    IK_Anim.side_to_side >> side_range.valueY
        
    side_range.outValue >> rev_rot.input1
    rev_rot.input2.set(1,1,1)
        
    rev_rot_md = create_node('multiplyDivide',n = name + '_rev_foot_reverse_side_to_side_md')
    rev_rot.outputX >> rev_rot_md.input1X
    rev_rot.outputY >> rev_rot_md.input1Y
    rev_rot_md.input2.set(1,1,1)
    rev_rot_md.outputX >> in_b.rotateZ
    rev_rot_md.outputY >> out_b.rotateZ
        
    #Heel Pivot
    heel_b = PyNode(reverse_foot[0])
    IK_Anim.heel_pivot >> heel_b.ry
        
    #Toe Pivot
    toe_b = PyNode(reverse_foot[3])
    IK_Anim.toe_pivot >> toe_b.ry
    '''else:
        rev_toe_piv = create_node('multiplyDivide',n = name + '_rev_toe_pivot_md')
        IK_Anim.toe_pivot >> rev_toe_piv.input1X
        rev_toe_piv.input2X.set(-1)
        rev_toe_piv.outputX >> toe_b.ry'''
        
    #Lean
    balltoe_b = PyNode(reverse_foot[3])
    IK_Anim.lean >> balltoe_b.rz

    #Balltoe Lift
    balltoe_b = PyNode(reverse_foot[4])
    IK_Anim.balltoe_lift >> balltoe_b.rx
    
    #Heel to Toe
    toe_b = PyNode(reverse_foot[3])
    heel_toe_range = create_node('setRange',n = name + '_rev_foot_heel_to_toe_sr')
    heel_toe_rot = create_node('multiplyDivide',n = name + '_rev_foot_heel_to_toe_md')
    heel_md = create_node('multiplyDivide',n = name + '_rev_foot_heel_md')
        
    heel_toe_range.min.set(-180,0,0)
    heel_toe_range.oldMin.set(-180,0,0)
    heel_toe_range.max.set(0,180,0)
    heel_toe_range.oldMax.set(0,180,0)
    IK_Anim.heel_to_toe >> heel_toe_range.valueX
    IK_Anim.heel_to_toe >> heel_toe_range.valueY
        
    heel_toe_range.outValue >> heel_toe_rot.input1
    heel_toe_rot.input2.set(1,1,1)
        
    heel_toe_rot.outputX >> heel_md.input1X
    heel_md.input2X.set(1)
    heel_md.outputX >> heel_b.rotateX
    heel_toe_rot.outputY >> toe_b.rotateX
    
    reverse_foot.insert(0,rev_grp)
    return reverse_foot

#=======================================================================================================================================================#
def save_post_autoRig(open = True):
    fileN = mc.file(q=True, sn=True, shn=True)
    thisDir = os.path.dirname(mc.file(q=1, loc=1))
    saveAs((thisDir+"\\post_autoRig.ma"),f=True,typ='mayaAscii')
    if open == True:
        openFile((thisDir+"\\post_autoRig.ma"),f=True)
        
def save_anim_shapes_factory(open = True):
    fileN = mc.file(q=True, sn=True, shn=True)
    thisDir = os.path.dirname(mc.file(q=1, loc=1))
    saveAs((thisDir+"\\animShapes_factory.ma"),f=True,typ='mayaAscii')
    if open == True:
        openFile((thisDir+"\\animShapes_factory.ma"),f=True)
    
def finalize_rig(rig):
    #Variables
    thisDir = os.path.dirname(mc.file(q=1, loc=1))
    rig = PyNode(rig)
    anims = []
    
    #Get all anims
    nodes = listConnections(rig.connected_networks)
    for node in nodes:
        if node.hasAttr('anims') == True:
            anims += listConnections(node.anims)
        if node.hasAttr('switch') == True:
            anims += listConnections(node.switch)
    
    try:
        #Imports modified anims from animShapes file
        mc.file((thisDir+'\\animShapes.ma'),i = True)
        PyNode('anims').visibility.set(0)
        new_shapes = listRelatives('anims',s=False)
        for new_shape in new_shapes:
            new_shape.rename(new_shape + '_new')
        
        #Swaps the anim shapes with the new ones and colors the anims
        '''Texture will be added later for anims shapes geometry'''
        
        for anim in anims:
            if objExists(anim + '_new') == True:
                new = PyNode(anim + '_new')
                parent(anim + '_new',anim)
                makeIdentity(anim + '_new',a=True,t=True,r=True,s=True)
                delete(anim.getChildren(s=True))
                parent(new.getChildren(s=True),anim,r=True,s=True)
                delete(new)
            shapes = anim.getChildren(s=True)
            for shape in shapes:
                shape.rename(anim + 'Shape')
            anim.overrideEnabled.set(1)
            items = anim.split('_')
            if items[0] == 'right':
                anim.overrideColor.set(13)
            elif items[0] == 'left':
                anim.overrideColor.set(18)
            else:
                anim.overrideColor.set(6)
            refresh()
        delete('anims')
    except:
        pass
    select(cl=True)
#=======================================================================================================================================================#
def delete_network_node(node):
    try:
        node = PyNode(node)
        for attr in ['parent_network','connected_networks','global_scale','root']:
            if node.hasAttr(attr) == True:
                node.attr(attr).unlock()
                node.disconnectAttr(attr)
        if node.network_type.get() == 'Character_Rig':
            topCon = listConnections(node.topCon)[0]
            bones = listConnections(node.bind_joint_grp)[0].getChildren()
            grps = listConnections(node.component_grp)[0].getChildren()
            parent(bones,grps,w=True)
            delete(node,topCon)
        else:
            grp = listConnections(node.component_grp)[0]
            bones = listConnections(node.bones)
            if bones[0].getParent() == 'component_grp':
                parent(bones[0],w=True)
            delete(node)
            for bone in bones:
                if objExists(bone + '*Constraint*') == True:
                    delete(bone + '*Constraint*');
                bone.disconnectAttr('translate')
                bone.disconnectAttr('rotate')
                bone.disconnectAttr('scale')
                bone.rotate.set(0,0,0)
                bone.scale.set(1,1,1)
                if bone.hasAttr('connected_to') == True and listConnections(bone.connected_to) == []:
                        deleteAttr(bone, at = 'connected_to')
            delete(grp)
            mel.eval('MLdeleteUnused;')
    except:
        pass;
    select(cl=True)
#=======================================================================================================================================================#
def anim_default_pose(anim):
        attrs = anim.listAttr(w=True,u=True,v=True,k=True)
        for attr in attrs:
            a = attr.replace((anim + '.'),'')
            dv = attributeQuery(a,n=anim,ld=True)[0]
            anim.attr(a).set(dv)

def mirror_anims():
    anims = ls(sl = True)
    attrs = []
    values = []
    for anim in anims:
        attrs.append(anim.listAttr(w=True,u=True,v=True,k=True))
        v = []
        for attr in anim.listAttr(w=True,u=True,v=True,k=True):
            if '.rotate' in str(attr) and str(attr).startswith('center_'):
                if str(attr).endswith('Z'): v.append(attr.get()) 
                else: v.append(attr.get() * -1)
            else: v.append(attr.get())
        values.append(v)
    
    for i in range(len(attrs)):
        for k in range(len(attrs[i])):
            a = str(attrs[i][k])
            try:
                if 'left_' in a: rev_a = Attribute(a.replace('left_','right_'))
                elif 'right_' in a: rev_a = Attribute(a.replace('right_','left_'))
                else: rev_a = Attribute(a)
                attr_value = values[i][k]
                rev_a.set(attr_value)
            except:pass
#=======================================================================================================================================================#
def mirror_components():
    original = ls(sl=True)
    nodes = get_node_from_anim()
    anims = []
    select(cl=True)
    for node in nodes:
        if node.hasAttr('anims'):
            anims += listConnections(node.anims)
        if node.hasAttr('switch'):
            anims += listConnections(node.switch)
    select(anims)
    mirror_anims()
    select(original)


def mirror_hierarchy():
    original = ls(sl=True)
    nodes = get_node_from_anim()
    for node in nodes:
        if node.hasAttr('connected_networks'):
            nodes += listConnections(node.connected_networks)
    anims = []
    select(cl=True)
    for node in nodes:
        if node.hasAttr('anims'):
            anims += listConnections(node.anims)
        if node.hasAttr('switch'):
            anims += listConnections(node.switch)
    select(anims)
    mirror_anims()
    select(original)
            
def mirror_rig():
    original = ls(sl=True)
    anims = []
    rigs = get_rig_from_anims()
    select(cl=True)
    for rig in rigs:
        if rig.hasAttr('connected_networks'):
            for node in listConnections(rig.connected_networks):
                if node.hasAttr('anims'):
                    anims += listConnections(node.anims)
                if node.hasAttr('switch'):
                    anims += listConnections(node.switch)
    select(anims)
    mirror_anims()
    select(original)

def mirror_complete_rig():
    original = ls(sl=True)
    anims = []
    rigs = []
    top_rigs = get_top_rig_from_anims()
    for top_rig in top_rigs:
        rigs.append(top_rig)
        if top_rig.hasAttr('connected_rigs'):
            rigs += listConnections(top_rig.connected_rigs)
    select(cl=True)
    for rig in rigs:
        if rig.hasAttr('connected_networks'):
            for node in listConnections(rig.connected_networks):
                if node.hasAttr('anims'):
                    anims += listConnections(node.anims)
                if node.hasAttr('switch'):
                    anims += listConnections(node.switch)
    select(anims)
    mirror_anims()
    select(original)

def get_top_rig_from_anims():
    rigs = []
    top_rigs = []
    if len(ls(sl=True)) > 0:
        for node in get_node_from_anim():
            rigs.append(listConnections(node.rig)[0])
        for rig in rigs:
            if rig.hasAttr('connected_to'):
                rigs.append(listConnections(rig.connected_to)[0])
            else:
                top_rigs.append(rig)
        return list(set(top_rigs))

def get_node_from_anim():
    networks = []
    for anim in ls(sl = True):
        if anim.hasAttr('animNode') or anim.endswith('switch'):
            networks.append(listConnections(anim.connected_to)[0])
    return list(set(networks))
    
def get_rig_from_anims():
    rigs = []
    if len(ls(sl=True)) > 0:
        for node in get_node_from_anim():
            rigs.append(listConnections(node.rig)[0])
        return list(set(rigs))

def character_text(string):
    txt = PyNode(textCurves(f='Arial', t= string, o = True)[0])
    objs = listRelatives(listRelatives(txt,c = True),c = True)
    parent(objs,w = True)
    delete(listRelatives(txt,c = True))
    
    for obj in objs:
        move(0,0,0,obj.name() + '.rotatePivot',obj.name() + '.scalePivot',rpr = True,ws = True)
        delete(obj,ch = True)
        makeIdentity(obj,a = True,r = True,t = True,s = True)
        parent(obj.getChildren(),txt,r = True, s = True)
        delete(obj)
    
    [rename(x,txt.name() + 'Shape' + str( i + 1)) for i, x in enumerate(txt.getShapes())]
    x,y,z = [((a - b)/2.00) for a,b in zip(exactWorldBoundingBox(txt)[:3],exactWorldBoundingBox(txt)[3:])]
    move(x,y,z,txt,rpr = True,ws = True)
    xform(txt,cp = True)
    makeIdentity(txt,t = True,r = True,s = True,a = True)
    
    select(cl = True)
    return txt
#=======================================================================================================================================================#
def ui_anim(name,text = None,tx = [],ty = [],rz = []):
    r = 1.00
    if not tx: tx = [0,0]
    if not ty: ty = [0,0]
    if not rz: rz = [0,0]
    
    tx1 = float(r * tx[0]) - 0.25
    tx2 = float(r * tx[1]) + 0.25
    ty1 = float(r * ty[0]) - 0.25
    ty2 = float(r * ty[1]) + 0.25
    
    ui_box = curve(n = name + '_box', d = 1,p = [(tx1,ty1,0),(tx2,ty1,0),(tx2,ty2,0),(tx1,ty2,0),(tx1,ty1,0)],k=[0,1,2,3,4])
    anim = circle(n = name + '_anim', d = 3,r = 0.25,nr = (0,0,1))[0]
    parent(anim,ui_box)
    for x in ['translateZ','rotateX','rotateY','scaleX','scaleY','scaleZ','visibility']:
        anim.setAttr(x,l = True,k = False,cb = False)
    if tx != [0,0]: transformLimits(anim,tx = tx, etx = (True,True))
    else: anim.setAttr('translateX',l = True,k = False,cb = False)
    if ty != [0,0]: transformLimits(anim,ty = ty, ety = (True,True))
    else: anim.setAttr('translateY',l = True,k = False,cb = False)
    if rz != [0,0]: transformLimits(anim,rz = rz, erz = (True,True))
    else: anim.setAttr('rotateZ',l = True,k = False,cb = False)
    
    select(cl = True)
    
    return anim, ui_box
#=======================================================================================================================================================#
def run_autoRig_script():
    if os.path.exists(os.path.dirname(mc.file(q=1, loc=1)) + '/autoRig.py'):
        script = os.path.dirname(mc.file(q=1, loc=1)) + '/autoRig.py'
        string = open(script,'r')
        code = {}
        run_code = compile(string.read(),'<string>','exec')
        exec run_code in code