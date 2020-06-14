import pymel.all as pm
import os
import maya.cmds as mc
#=========================================================================================#
def roll_up(anim,start,end):
    anim = pm.PyNode(anim)
    jnts = mu.get_chain(start,end)[:-1]
    rev_jnts = jnts[::-1]
    total_v = 72.00 * len(jnts)
    
    anim.addAttr('roll_up',at = 'double',min = -100,max = 100,dv = 0,k = True)
    total = mu.create_node('multiplyDivide',n = '{0}_total'.format(anim))
    
    anim.roll_up >> total.input1X
    total.input2X.set(total_v / 100.00)
    
    for i, jnt in enumerate(rev_jnts):
        j = jnt.replace('_bind_joint','')
        range = mu.create_node('setRange',n = '{0}_range'.format(j))
        
        range.minX.set(-72)
        range.oldMinX.set(-72)
        range.maxX.set(72)
        range.oldMaxX.set(72)
        
        range.outValueX >> jnt.rotateZ
        
        if i == 0: total.outputX >> range.valueX
        else:
            limit = mu.create_node('multiplyDivide',n = '{0}_limit'.format(j))
            cond = mu.create_node('condition',n = '{0}_cond'.format(j))
            
            limit.input1X.set(72 * i)
            cond.operation.set(2)
            anim.roll_up >> cond.firstTerm
            cond.outColorR >> range.valueX
            
            for s in ['upper','lower']:
                v = 1
                if s == 'lower': v = -1
                upma = pm.createNode('plusMinusAverage',n = '{0}_{1}_pma'.format(j,s))
                ucond = mu.create_node('condition',n = '{0}_{1}_cond'.format(j,s))
                
                ucond.operation.set(0)
                if s == 'upper': upma.operation.set(2)
                ucond.secondTerm.set(72 * v)
                ucond.colorIfFalseR.set(0)
                
                rev_jnts[i - 1].rotateZ >> ucond.firstTerm
                total.outputX >> upma.input1D.input1D[0]
                limit.outputX >> upma.input1D.input1D[1]
                upma.output1D >> ucond.colorIfTrueR
                if s == 'upper': ucond.outColorR >> cond.colorIfTrueR
                else: ucond.outColorR >> cond.colorIfFalseR

def eye_scale_correction(eye_geo,locators):
    par = None
    try: par = eye_geo.getParent()
    except: pass
    eye_geo = pm.PyNode(eye_geo)
    front_loc, top_loc, side_loc = [pm.PyNode(x) for x in locators]
    center_loc = pm.spaceLocator(n = 'temp_center_eye_loc',p = (0,0,0))
    scale_correct = pm.group(center_loc,n = eye_geo + '_scale_grp')
    
    #Get Center
    info = eye_geo.boundingBox()
    tx = (info[0][0] + info[1][0])/2.00
    ty = (info[0][1] + info[1][1])/2.00
    tz = (info[0][2] + info[1][2])/2.00
    scale_correct.translate.set(tx,ty,tz)

    pm.delete(pm.aimConstraint(front_loc,scale_correct,aim = (0,0,1),u = (0,1,0),wuo = top_loc,mo = False))

    data = []
    cl_pos = pm.xform(center_loc, q= True, ws=True, rp=True);
    for loc in [side_loc,top_loc,front_loc]:
        loc_pos = pm.xform(loc, q= True, ws=True, rp=True);
        dist = pm.distanceDimension(sp=(cl_pos[0],cl_pos[1],cl_pos[2]),ep=(loc_pos[0],loc_pos[1],loc_pos[2]))
        data.append(dist.distance.get())
        pm.delete(dist.getParent())
        
    lowest = min(data)
    data = [x / lowest for x in data]
    
    scale_correct.scale.set(data)
    aligner(scale_correct,center_loc,position = False,rotation = False,pivot = True)
    pm.parent(eye_geo,scale_correct)
    pm.makeIdentity(eye_geo,t = True,r = True,s = True,a= True)
    pm.delete(front_loc,top_loc,side_loc,center_loc)
    
    if par != None: pm.parent(scale_correct,par)

    return scale_correct

def FK_stretch_setup(anims,nulls,controls, stretch_type):
    mds = []
    for i, anim in enumerate(anims[:-1]):
        anim.addAttr('stretch',at = 'double',min = 0,dv = 1,k = True)
        md = create_node('multiplyDivide',n = anim + '_stretch_md')
        anim.stretch >> md.input2X
        nulls[i + 1].translateX.unlock()
        md.input1X.set(nulls[i + 1].translateX.get())
        md.outputX >> nulls[i + 1].translateX
        if stretch_type == 'position':
            md.outputX >> controls[i + 1].translateX
            mds.append(md)
        else:
            stretch = create_node('multiplyDivide',n = controls[i] + '_FK_stretch_md')
            stretch.input1X.set(1.00)
            anim.stretch >> stretch.input2X
            stretch.outputX >> controls[i].scaleX #Look at this later.
            mds.append(stretch)
    return mds

def create_spline_anims(name,suffix,chain,amnt = 3,smooth = True,spots = None,spans = 8):
    start = chain[0]
    cv = make_spline(name,chain, smooth = smooth,spans = spans)
    cv.inheritsTransform.set(0)
    bones = [start for i in range(amnt)]
    anims, nulls = create_anims(bones, name,suffix = suffix, type = 'sphere', separate = True, end = False)
    if spots == None: pcnt = 1.00/(amnt - 1.00)
    else: pcnt = spots
    for i, null in enumerate(nulls):
        if spots == None: con = curve_constraint(cv,null,(pcnt * i))
        else: con = curve_constraint(cv,null,pcnt[i])
        tr = null.translate.get()
        pm.delete(con)
        null.translate.set(tr)
    return anims, nulls, cv

def switch_setup(name, start, constraints, switch = None, suffix = 'FKIK_switch', attribute = 'FKIK_switch', dv = 0):
    reverses = []
    if switch == None:
        switch = pm.group(n = name + '_' + suffix,em = True)
        switch.addAttr(attribute,at = 'double', min = 0, max = 1, dv = dv, k = True)
        lock_and_hide_attrs(switch,['translate','rotate','scale','v'])
    aligner(switch, start)
   
    for con in constraints:
        attrs = [pm.Attribute(con + '.' + x) for x in pm.listAttr(con,st = ['*W0','*W1','W2'])]
        rev = create_node('reverse',n = con + '_rev_node')
        switch_attr = pm.Attribute(switch + '.' + attribute)
        switch_attr >> rev.inputX
        rev.outputX >> attrs[0]
        switch_attr >> attrs[1]
    
    if switch != None: return switch, reverses
    else: return reverses
#=========================================================================================#
def get_chain(start,end,reverse = False):
    rn = len(pm.PyNode(start).longName()[1:].split('|'))-1
    output = pm.PyNode(end).longName()[1:].split('|')[rn:]
    bones = [pm.PyNode(x) for x in output]
    if reverse == True: bones = bones[::-1]
    return bones
        
def create_node(type,n = None):
    node = pm.shadingNode(type,au=True)
    if n: node.rename(n)
    attrs = node.listAttr(w=True,u=True,v=True,k=True)
    for attr in attrs: pm.setAttr(attr,k=False,cb=False)
    return node

def check_for_constraints(objs):
    for obj in objs:
        cons = list(set(obj.listConnections(s=True,type = pm.nt.Constraint)))
        for con in cons:
            if con in obj.getChildren(): pm.delete(cons)

def set_to_default_pose(anim):
    attrs = anim.listAttr(w=True,u=True,v=True,k=True)
    for attr in attrs:
        a = attr.replace((anim + '.'),'')
        dv = pm.attributeQuery(a,n=anim,ld=True)[0]
        anim.attr(a).set(dv)

def bone_labeling(bones):
    if not isinstance(bones,list): bones = [bones]
    names = [str(x).lower() for x in pm.attributeQuery('type',n = bones[0],le = True)[0].split(':')]
    for bone in bones:
        bone_name = bone.name()
        settings = [0,'center_']
        if 'left_' in bone_name: settings = [1,'left_']
        elif 'right_' in bone_name: settings = [2,'right_']
        
        bone.side.set(settings[0])
        bone_name = bone_name.replace(settings[1],'')
        
        for i, name in enumerate(names):
            if name in bone_name:
                pm.setAttr(bone.name() + '.type',i)
                break
            else:
                pm.setAttr(bone.name() + '.type',18)#other
                bone.otherType.set(bone_name.replace('_end_joint','').replace('_bind_joint',''))
                
def get_bone_length(start,end):
    bones = get_chain(start,end)
    value = 0
    for bone in bones[1:]:
        value += abs(pow(pow(bone.tx.get(),2) + pow(bone.ty.get(),2) + pow(bone.tz.get(),2),0.5))
    return value

def aligner(objs,target,position = True,rotation = True,pivot = False):
    if not isinstance(objs,list): objs = [objs]
    for obj in objs:
        if position == True:
            target_position = pm.xform(target, q= True, ws=True, rp=True)
            pm.move(target_position[0],target_position[1],target_position[2], obj, rpr = True)
        if rotation == True:
            target_rotation = pm.xform(target, q=True, ws = True, ro = True)
            pm.xform(obj, ws=True,ro=(target_rotation[0],target_rotation[1],target_rotation[2]))
        if pivot == True:
            target_pivot = pm.xform(target, q= True, ws=True, rp=True)
            pm.move(target_pivot[0],target_pivot[1],target_pivot[2], obj + '.rotatePivot', obj + '.scalePivot', rpr = True)
    
def align_between(obj,targets,position = True,rotation = True,pivot = False):
    if not isinstance(targets,list): targets = [targets]
    if len(targets) > 1:
        tx, ty, tz = 0,0,0
        rx, ry, rz = 0,0,0
        amnt = len(targets)
        for tar in targets:
            t = pm.xform(tar, q= True, ws=True, rp=True)
            r = pm.xform(tar, q=True, ws = True, ro = True)
            tx, ty, tz = tx + t[0],ty + t[1] ,tz + t[2]
            rx, ry, rz = rx + r[0],ry + r[1] ,rz + r[2]
        tx, ty, tz = tx/amnt,ty/amnt ,tz/amnt
        rx, ry, rz = rx/amnt,ry/amnt ,rz/amnt
        if position == True: pm.move(tx,ty,tz, obj, rpr = True)
        if rotation == True: pm.xform(obj, ws=True,ro=(rx,ry,rz))
        if pivot == True: pm.move(tx, ty, tz, obj + '.rotatePivot', obj + '.scalePivot', rpr = True)
    else: aligner(objs,targets,position = position,rotation = rotation,pivot = pivot)

def mirror_selection(anims):
    attrs = []
    values = []
    for anim in anims:
        if anim.hasAttr('animNode'):
            v = []
            components = list(set([str(x.node_type.get()) for x in pm.listConnections(anim.connected_to) if x.hasAttr('anims') and anim in pm.listConnections(x.anims)]))
            attrs.append(anim.listAttr(w=True,u=True,v=True,k=True))
            for attr in anim.listAttr(w=True,u=True,v=True,k=True):
                
                if str(attr).startswith('center_'):
                    if '.rotate' in str(attr):
                        if 'COGChain' in components:
                            if str(attr).endswith('translateX') or str(attr).endswith('rotateY') or str(attr).endswith('rotateZ'): v.append(attr.get() * -1.00)
                            else: v.append(attr.get())
                        else:
                            if str(attr).endswith('Z'): v.append(attr.get()) 
                            else: v.append(attr.get() * -1.00)
                    else:
                        if str(attr).endswith('translateX'): v.append(attr.get() * -1.00)
                        else: v.append(attr.get())
                else: v.append(attr.get())
            values.append(v)
    for i, att in enumerate(attrs):
        for k, a in enumerate(att):
            if 'left' in a.name(): rev_a = pm.Attribute(a.name().replace('left_','right_'))
            elif 'right' in a.name(): rev_a = pm.Attribute(a.name().replace('right_','left_'))
            else: rev_a = pm.Attribute(a.name())
            rev_a.set(values[i][k])
    
def con_link(objs,node,attribute):
    if isinstance(objs,str) and pm.objExists(objs) == False:
        node.setAttr(attribute,objs,f=True)
        node.attr(attribute).lock()
    else:
        start = 0
        if not isinstance(objs,list): objs = [objs]
        if node.hasAttr(attribute):
            items = pm.listConnections(node.attr(attribute))
            start = len(items)
            if start == 1: 
                node.deleteAttr(attribute)
                node.addAttr(attribute,dt = 'string',m = True)
                items[0].connected_to >> node.attr(attribute + '[0]')
        else:
            if len(objs) == 1: node.addAttr(attribute,at = 'message')
            else: node.addAttr(attribute,dt = 'string',m=True)
            
        for i, obj in enumerate(objs):
            if isinstance(obj,str) and pm.objExists(obj) == True: obj = pm.PyNode(obj)
            if not obj.hasAttr('connected_to'): obj.addAttr('connected_to',at = 'message')
            if (start + len(objs)) == 1: net_attr = attribute
            else: net_attr = attribute + '[' + str(start + i) + ']'
            obj.connected_to >> node.attr(net_attr)

def lock_and_hide_attrs(objs,attrs):
    if isinstance(attrs,str) and attrs != 'all': attrs = [attrs]
    if not isinstance(objs,list): objs = [objs]
    for obj in objs:
        if attrs == 'all':
            attrs = [str(x) for x in pm.listAttr(obj,r=True, w=True, v=True, k=True)]
            attrs += [str(x) for x in pm.listAttr(obj,cb = True)]
        triples = ['translate','rotate','scale']
        for t in triples:
            if t in attrs:
                attrs.remove(t)
                attrs += [t + 'X', t + 'Y',t + 'Z']
        for attr in attrs:
            connection = pm.listConnections(obj + '.' + attr, s=True,d=False)
            if connection: pm.setAttr(obj + '.' + attr,l=False,cb=False,k=False)
            else: pm.setAttr(obj + '.' + attr,l=True,cb=False,k=False)

def duplicate_chain(chain, prefix, suffix, separate = False, reverse = False, show = True, orient_to_world = False,end = False):
    if not isinstance(chain,list): chain = [chain]
    bones = chain
    pm.select(cl=True)
    new_bones = []
    amnt = len(chain)
    
    for i, bone in enumerate(bones):
        try: r = bone.radius.get() * 1.10
        except: r = 1.00
        if amnt <= 2 and separate == False: name = prefix + '_' + suffix
        else: name = prefix + '_' + str(i + 1) +'_' + suffix
        new_bone = pm.joint(n = name, rad = r, p=(0,0,0))
        new_bone.jointOrient.set(0,0,0)
        if show == False: new_bone.drawStyle.set(2)
        if orient_to_world == True: aligner(new_bone,bone,rotation = False)
        else: aligner(new_bone,bone)
        new_bones.append(new_bone)
        try: new_bone.side.set(bone.side.get())
        except: pass

        pm.makeIdentity(new_bone,t = True,r = True,s = True,jo = False,a = True)  
        pm.select(cl = True)
    
    if reverse == True: new_bones.reverse()
    if separate == False:
        for i, nb in enumerate(new_bones[1:]): pm.parent(nb,new_bones[i])
        if len(new_bones) > 1: new_bones[-1].rename(prefix + '_end_' + suffix)
    
    [x.rename(x.replace(suffix + '1',suffix)) for x in new_bones]
    return new_bones

def stack_chain(chain,rep = '',wi = '',separate = False):
    stack = []
    if not isinstance(chain,list): chain = [chain]
    for obj in chain:
        pm.select(cl= True)
        null = pm.joint(n = obj.replace(rep,wi),rad = (obj.radius.get() * 1.1))
        null.jointOrient.set(0,0,0)
        null.drawStyle.set(2)
        aligner(null,obj)
        stack.append(null)
        
        pm.makeIdentity(null,t = True,r = True,s = True,jo = False,a = True)  
        if separate == False:
            par = obj.getParent()
            if par != None: pm.parent(null,par)
            pm.parent(obj,null)
            
    return stack

def default_anim_shape(chain,type = 'circle',r = 1.25):
    if not isinstance(chain,list): chain = [chain]
    for all in chain:
        if isinstance(all,str): all = pm.PyNode(all)
        rad = all.radius.get()
        if type == 'circle':
            circ = pm.circle(r = rad * r,nr = (1,0,0),ch = False)[0]
            circ_shape = circ.getShape().rename(all.name() + 'Shape')
            pm.parent(circ_shape,all,r = True,s = True)
            pm.delete(circ)
        else: 
            circ1 = pm.circle(r = rad * r,nr = (1,0,0),ch = False)[0]
            circ2 = pm.circle(r = rad * r,nr = (0,1,0),ch = False)[0]
            circ3 = pm.circle(r = rad * r,nr = (0,0,1),ch = False)[0]
            for c in [circ1,circ2,circ3]:
                circ_shape = c.getShape().rename(all.name() + 'Shape')
                pm.parent(circ_shape,all,r = True,s = True)
                pm.delete(c)
        try: all.drawStyle.set(2)
        except: pass

def create_anims(chain, prefix,separate = False, reverse = False, show = True,
                 end = True, orient_to_world = False, type = 'circle', r = 1.25, suffix = 'anim'):
    anims = duplicate_chain(chain, prefix, suffix, separate = separate, reverse = reverse,
                               show = show, orient_to_world = orient_to_world,end = end)
    nulls = stack_chain(anims,rep = '_anim',wi = '_null')
    if end == True:
        default_anim_shape(anims[:-1],type = type, r = r)
        anims[-1].drawStyle.set(2)
    else:
        new = '_' + str(len(anims)) + '_'
        anims[-1].rename(anims[-1].replace('_end_',new))
        nulls[-1].rename(nulls[-1].replace('_end_',new))
        default_anim_shape(anims,type = type, r = r)
    if len(anims) == 1: anims = anims[0]
    if len(nulls) == 1: nulls = nulls[0]
    return [anims,nulls]

def make_spline(name, bones, spans = 8, smooth = True):
    bones = [pm.PyNode(bone) for bone in bones]
    co = []
    k=[]
    
    for i, bone in enumerate(bones):
        co.append(pm.xform(bone, q= True, ws=True, rp=True))
        k.append(i)
    cv = pm.curve(n = name + '_cv', d = 1, p = co, k = k)
    if smooth == True: pm.rebuildCurve(cv, rt = 0, ch = 0, s = spans, d = 3, tol = 0)
    pm.xform(cv,cpc=True)
    pm.delete(cv,ch=True)
    pm.select(cl=True)
    
    return cv

def make_nurb(name,chain,spans = 8,smooth = True,section = 'center'):
    cv_1 = make_spline(name,chain,spans = spans,smooth = smooth)
    cv_2 = make_spline(name,chain,spans = spans,smooth = smooth)
    mid_null = None
    if section == 'start': pm.parent(cv_1,cv_2,chain[0])
    elif section == 'end': pm.parent(cv_1,cv_2,chain[-1])
    else:
        if isinstance(section,int): pm.parent(cv_1,cv_2,chain[section])
        else: 
            amnt = len(chain)
            if amnt % 2 != 0: pm.parent(cv_1,cv_2,chain[(amnt - 1)/2])
            else:
                targets = [chain[(amnt - 1)/2],chain[amnt/2]]
                mid_null = pm.spaceLocator(p = (0,0,0))
                align_between(mid_null,targets)
                pm.parent(cv_1,cv_2,mid_null)
            
    pm.makeIdentity(cv_1,cv_2,t = True,r = True,s = True,a = True)
    cv_1.ty.set(1)
    cv_2.ty.set(-1)
    pm.parent(cv_1,cv_2,w = True)
    nurb = pm.loft(cv_2,cv_1,n = name + '_nurb', ch = False)[0]
    pm.delete(cv_1,cv_2)
    pm.select(cl = True)
    if mid_null != None: pm.delete(mid_null)
    
    return nurb
    
def create_nurb_anims(name,suffix,chain,amnt = 3,spans = 8,smooth = True, spots = None):
    anims, nulls, cv = create_spline_anims(name,suffix,chain,amnt = amnt,spots = spots)
    nurb = make_nurb(name,chain,spans = spans,smooth = smooth)
    pm.delete(cv)
    pm.select(cl = True)
    
    return anims, nulls, nurb
    
def nurbs_constraint(nurb, obj, u = 0, v = 0):
    #Variables
    obj = pm.PyNode(obj)
    zero_null = pm.group(n = obj + '_zero_null',em = True)
    con = pm.parentConstraint(zero_null, obj, w=1, mo = False)
    pos = pm.PyNode(pm.pointOnSurface( nurb, ch = True))
    matrix = pm.createNode('fourByFourMatrix')
    
    #Setup
    pos.turnOnPercentage.set(1)
    pos.parameterU.set(u)
    pos.parameterV.set(v)
    pos.normalizedNormalX >> matrix.in20
    pos.normalizedNormalY >> matrix.in21
    pos.normalizedNormalZ >> matrix.in22
    pos.normalizedTangentUX >> matrix.in10
    pos.normalizedTangentUY >> matrix.in11
    pos.normalizedTangentUZ >> matrix.in12
    pos.normalizedTangentVX >> matrix.in00
    pos.normalizedTangentVY >> matrix.in01
    pos.normalizedTangentVZ >> matrix.in02
    pos.positionX >> matrix.in30
    pos.positionY >> matrix.in31
    pos.positionZ >> matrix.in32
    matrix.output >> con.constraintParentInverseMatrix
    
    return zero_null

def curve_constraint(nurb,obj,pr):
    obj = pm.PyNode(obj)
    info = pm.PyNode(pm.pointOnCurve(nurb,top = True, p=True, pr=pr, ch=True))
    info.result.position >> obj.translate
    return info
    
def mirror_object(obj):
    for at in ['X','Y','Z']: obj.attr('scale' + at).unlock()
    obj.scale.set(-1,- 1,-1)
    for at in ['X','Y','Z']: obj.attr('scale' + at).lock()
    
def constraint_switch(anim,index,align = True):
    pm.undoInfo(ock = True)
    original_selection = pm.ls(sl = True)
    if align == True:
        align_loc = pm.group(em = True)
        position_null = None
        anim_null = anim.getParent()
        if anim_null.scaleX.get() == -1: 
            pm.parent(align_loc,anim_null)
            align_loc.translate.set(0,0,0)
            align_loc.rotate.set(0,0,0)
            align_loc.scale.set(1,1,1)
            aligner([align_loc],anim)
            position_null = pm.group(em = True)
            pm.parentConstraint(position_null,align_loc,mo = True)
        else: aligner([align_loc],anim)
    anim.parent_to.set(index)
    if align == True:
        aligner(anim,align_loc)
        pm.delete(align_loc)
        if position_null != None: pm.delete(position_null)
    pm.select(original_selection)
    pm.undoInfo(cck = True)
    
def run_autoRig_script():
    if os.path.exists(os.path.dirname(mc.file(q=1, loc=1)) + '/autoRig.py'):
        script = os.path.dirname(mc.file(q=1, loc=1)) + '/autoRig.py'
        string = open(script,'r')
        code = {}
        run_code = compile(string.read(),'<string>','exec')
        exec run_code in code
        
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