from pymel.core import *
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt
import maya.mel as mel

### LABEL TABLES ###

JNT_SIDE = {    "center":  0,
                "left":    1,
                "right":   2,
                "none":    3    }

JNT_TYPE = {    "none":          0,
                "root":          1,
                "hip":           2,
                "upperleg":      2, # House convention -> upperleg as Hip
                "knee":          3,
                "lowerleg":      3, # House convention -> lowerleg as Knee
                "foot":          4,
                "ball":          4, # House convetion -> "ball" is also labeled Foot
                "toe":           5,
                "spine":         6,
                "neck":          7,
                "head":          8,
                "collar":        9,
                "clavicle":      9, # House convention -> clavicle as Collar
                "shoulder":      10,
                "upperarm":      10, # House convention -> upperarm as Shoulder
                "elbow":         11,
                "lowerarm":      11, # House convention -> lowerarm as Elbow
                "hand":          12,
                "finger":        13,
                '''
                "thumb":         14, # House convention dictates that the thumb is an "other" joint
                '''
                "propa":         15,
                "propb":         16,
                "propc":         17,
                '''
                "palm":          17, # House convention dictates that the palm is an "other" joint
                "other":         18, # Joint not in this table automatically uses the "other" label
                '''
                "index finger":  19,
                "middle finger": 20,
                "ring finger":   21,
                "pinky finger":  22,
                "extra finger":  23,
                "big toe":       24,
                "index toe":     25,
                "middle toe":    26,
                "ring toe":      27,
                "pinky toe":     28,
                "extra toe":     29    }                

JNT_TYPE_OTHER = 18

### COMMANDS ###

def create_block_model_cmd():
    '''Creates block models for the selected joint(s).'''
    sel = ls(sl=True)
    if not sel:
        raise Exception('Select a joint to continue.')
    
    #check for node type joint
    joints = []
    for s in sel:
        if not isinstance(s, nodetypes.Joint):
            print 'Selection is not node type joint.  Skipping: {0}'.format(s.name())
        else:
            joints.append(s)
            
    for jnt in joints:
        create_block_model(jnt)
        

### Misc vector and geometric math helpers ###

def getWorldDirectionVector(trans, localDirection):
    '''
    Given a local direction vector and an object, return that
    direction vector in world space from object space.
    '''
    tempGrp = PyNode(group(em=1, n="tempTransTracker"))
    tempLoc = PyNode(spaceLocator(n="tempUpAim"))
    parent(tempLoc, tempGrp)
    tempLoc.translate.set(localDirection[0], localDirection[1], localDirection[2])
    pc = parentConstraint(trans, tempGrp, mo=0)
    delete(pc)
    dirVector = (tempLoc.getTranslation("world")-tempGrp.getTranslation("world")).normal()
    delete(tempGrp)
    return dirVector

def getWorldPositionVector(trans, localPosition):
    '''
    Given a local position vector and an object, return that
    position in world space from object space.
    '''
    tempGrp = PyNode(group(em=1, n="tempTransTracker"))
    tempLoc = PyNode(spaceLocator(n="tempUpAim"))
    parent(tempLoc, tempGrp)
    tempLoc.translate.set(localPosition[0], localPosition[1], localPosition[2])
    pc = parentConstraint(trans, tempGrp, mo=0)
    delete(pc)
    position = tempLoc.getTranslation("world")
    delete(tempGrp)
    return position
    
def getWorldRightVector(trans):
    '''
    Return the normalized x-axis vector of a transform in world space.
    '''
    return getWorldDirectionVector(trans, (1,0,0))
    
def getWorldUpVector(trans):
    '''
    Return the normalized y-axis vector of a transform in world space.
    '''
    return getWorldDirectionVector(trans, (0,1,0))
    
def getWorldForwardVector(trans):
    '''
    Return the normalized z-axis vector of a transform in world space.
    '''
    return getWorldDirectionVector(trans, (0,0,1))
    
def getCoplanarNormal(transforms=[]):
    '''
    Return the normal of the coplaner space between three transforms.
    '''
    
    if (len(transforms) != 3): return None
    faceT = PyNode(polyCreateFacet(ch=0, p=map(lambda t: xform(t, q=1, ws=1, t=1), transforms))[0])
    normal = faceT.f.getNormal(space="world")
    delete(faceT)
    return normal

def lockChildOrientsAndAim(aimAt, trans, yWorldUp=(0,1,0), xLocalAim=(1,0,0), yLocalUp=(0,1,0)):
    '''
    Aim an object and make sure its children maintain their world
    space orientations and while their translation remains relative to the parent.
    '''
    
    trans = PyNode(trans)
    
    # Lock child orient through locators
    pcs = []
    locs = []
    for c in trans.getChildren():
        loc = spaceLocator()
        delete(parentConstraint(c, loc, mo=0))
        parentConstraint(trans, loc, mo=1, sr=('x','y','z'))
        pcs.append(parentConstraint(loc, c, mo=0))
        locs.append(loc)
        
    # Aim
    delete(aimConstraint(aimAt, trans, mo=0, aim=xLocalAim, u=yLocalUp, wu=yWorldUp, wut='vector'))
    
    # Disassemble
    delete(pcs)
    delete(locs)
        
def lockChildOrientsAndAimUp(trans, objectUp=(0,1,0), objectForward=(0,0,1)):
    '''
    Aim the object up in world space.
    
    objectUp:
        Object axis to align with the world y-axis
        
    objectForward:
        Object axis to align with the world z-axis
    '''
    
    # Set up world space locator group
    yAxis = spaceLocator(n="yAxis")
    yAxis.translate.set(0,1,0)
    zAxis = spaceLocator(n="zAxis")
    zAxis.translate.set(0,0,1)
    wsGrp = group(n="wsGrp", em=1)
    parent(yAxis, zAxis, wsGrp)
    delete(pointConstraint(trans, wsGrp, mo=0))
    
    # Aim
    lockChildOrientsAndAim(zAxis, trans, (0,1,0), objectForward, objectUp)
    
    # Disassemble
    delete(wsGrp)

### Block model creation (MODIFIED) ###

def create_block_model(jnt, parent_option=True, girth_size=3, ratio_option=True, ratio_value=0.25, skip_end_joints=True):
    '''Creates a polygon the length of the input joint.  If ratio_option is true, girth value is 
    the distance multiplied by the ratio value.  If ratio_option is false, girth_value is used in world units.'''
    
    joint_name = jnt.name()
    if skip_end_joints and joint_name.endswith('_end_joint'):
        '"'+joint_name+'" is an end joint, skipping.'
        return None
    
    # Create polygon cube with pivot at base 
    if joint_name.endswith('_bind_joint'):
        joint_name = jnt.name()[:11]
    block_name = joint_name + '_block'
    block = polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=[ 0, 1, 0 ], cuv=4, ch=0, n=block_name)[0]
    move(block.f[:], [0.5, 0, 0], r=True)
    makeIdentity(block, apply=True, t=True, r=True, s=True, n=False)
    
    # Parent it to the joint and zero it out
    block.setParent(jnt)
    block.translate.set([0,0,0])
    
    # Scale the block based on distance to first child joint
    dist = 0
    child_joints = jnt.listRelatives(c=True, type='joint')
    
    # Determine distance to the first child joint in the list
    if child_joints:
        dist = abs(child_joints[0].tx.get())
        print 'dist {0}'.format(dist)
        if dist <= 0.001:
            dist = 5
            #print 'Distance to first child on x axis is zero.  Setting distance to minimum value of 5.'
    else:
        dist = 10
        print 'Input joint has no descendents.  Using default scale value 10. {0}'.format(jnt.name())
    
    # Aim towards a like-named child or all joint children
    if child_joints:
        
        aimingAtAll = len(child_joints) > 1
        
        # If a particular child shares the first two names of this bind joint, aim at that one, otherwise aim at all of them
        for c in child_joints:
            comp = c.shortName().split('_')
            if len(comp) < 2: continue
            if jnt.shortName().startswith(comp[0]+"_"+comp[1]):
                child_joints = [c]
                aimingAtAll = False
                break
        
        ac = aimConstraint(child_joints, block, aim=(1,0,0), u=(0,1,0), wut="objectrotation", wuo=jnt)
        delete(ac)
        
        # Round off rotation to a multiple of 90, since aiming at 2 or more joints will probably align this block slightly off an axis
        if aimingAtAll:
            roundedRotation = map(lambda rot: 90*round(rot/90.0), block.rotate.get())
            block.rotate.set(roundedRotation)

    else:
        block.rotate.set(0,0,0)
    
    # Create the block model based on input options for girth and ratio
    girth = girth_size
    
    if ratio_option:
        girth = dist * ratio_value
    
    block.scale.set([dist, girth, girth])
    makeIdentity(apply=True, t=True, r=False, s=True, n=False)
    
    if not parent_option:
        block.setParent(world=True)
        

### Bind joint mesh querying, parenting, and unparenting ###

def getBindJointMeshTransforms():
    '''
    Return a list of all mesh transforms parented to bind joints.
    '''
    
    bindJointMeshTransforms = []
    joints = ls('*bind_joint', r=1, type='joint')
    
    for j in joints:
        children = j.getChildren()
        for c in children:
            childShape = c.getShape()
            if (childShape != None and type(childShape) == nt.Mesh): bindJointMeshTransforms.append(c)
        
    return bindJointMeshTransforms


def selectBindJointMeshTransforms():
    '''
    Select all mesh transforms parented under bind joints
    '''
    select(getBindJointMeshTransforms())

def parentConstrainMeshesToBindJoints():
    unparentMeshesFromBindJoints()
    parentMeshesToBindJoints(False)
    
def parentMeshesToBindJoints(directParent=True):
    '''
    Parent visible meshes in the root of the scene to the closest bind joint in world space.
    '''

    joints = ls('*bind_joint', r=1, type='joint')
    visibleTransforms = filter(lambda t: t.hasAttr("visibility") and t.visibility.get(), ls(assemblies=1))
    transformShapes = map(lambda t: t.getShape(), visibleTransforms)
    meshes = filter(lambda t: type(t) == nt.Mesh, transformShapes)
    
    jntWorldPosCache = {}
    for j in joints: jntWorldPosCache[j] = dt.Vector(j.getRotatePivot(space='world'))
    
    for m in meshes:
        t = m.getParent()
        worldPos = dt.Vector(t.getRotatePivot(space='world'))
        
        minDist = None
        minDistJnt = None
        
        for j, jWorldPos in jntWorldPosCache.iteritems():
            dist = worldPos.distanceTo(jWorldPos)
            if (minDist == None or dist < minDist):
                minDist = dist
                minDistJnt = j
                
        if (minDistJnt != None):
            if directParent:
                parent(t, minDistJnt)
            else:
                parentConstraint(minDistJnt, t, mo=1)
    

def unparentMeshesFromBindJoints():
    '''
    Unparent all meshes from all bind joints, such that the meshes are in the root of the scene.
    '''
    
    bindJointMeshes_snapPivotToJoint()
    toUnparent = getBindJointMeshTransforms()
    for t in toUnparent: parent(t, w=1)
    select(toUnparent)


### Bind joint mesh modification ###
        
def bindJointMeshes_autoName(nameExtension="mesh"):
    '''
    Append a name to all meshes parented to bind joints.
    '''
    
    for t in getBindJointMeshTransforms(): t.rename(t.getParent().shortName()+"_"+nameExtension)


def bindJointMeshes_snapPivotToJoint():
    '''
    For bind joint meshes already parented, snap their pivots to the joint.  This will ensure correct joint
    assignment when meshes are reparented to the skeleton (assuming pivots don't move when unparented)
    '''
    
    for t in getBindJointMeshTransforms(): xform(t, piv=t.getParent().getRotatePivot(space='world'), ws=1)


def bindJointMeshes_mirror():
    '''
    Looks for right/left joint name matches then mirrors block model geometry over to where none exists.
    For example, if you wanted to redo arm geometry you may delete either side, work from the other, then
    run this method.
    '''
    
    origSelection = ls(sl=1)
    joints = ls('*bind_joint', r=1, type='joint')
    blockMeshTable = {} # { jointName -> [mesh] }
    
    # Build joint to block mesh table
    for t in getBindJointMeshTransforms():
        jointName = t.getParent().shortName()
        if (not jointName in blockMeshTable):
            blockMeshTable[jointName] = [t]
        else:
            blockMeshTable[jointName] += [t]
    
    # If a joint doesn't have block meshes, try to grab some from a sibling
    for j in joints:
        jointName = j.shortName()
        if (not jointName in blockMeshTable):
            
            blockSource = None
            if (jointName.startswith("left")):
                blockSource = jointName.replace("left", "right")
            elif (jointName.startswith("right")):
                blockSource = jointName.replace("right", "left")
                
            if (blockSource == None or not blockSource in blockMeshTable): continue # Neither right/left or in the block table
            
            select(blockMeshTable[blockSource])
            duplicate()
            parent(w=1)
            mirrorGrp = group()
            xform(mirrorGrp, piv=(0,0,0), ws=1)
            mirrorGrp.scaleX.set(-1)
            ungroup()
            mirroredTransforms = ls(sl=1)
            parent(mirroredTransforms, PyNode(jointName))
            select(d=1)
            refresh()
            
    # Select mirroed geometry
    select(origSelection)


### Block model skeleton modification ###

def selectBindJoints():
    '''
    Select all labeled bind joints
    '''
    select(ls("*bind_joint", r=1))
    

def showAllJointLocalRotationAxes():
    '''
    Show all joint local rotation axes.
    '''
    joints = ls('*', r=1, type='joint')
    for j in joints: j.displayLocalAxis.set(True)


def hideAllJointLocalRotationAxes():
    '''
    Hide all joint local rotaion axes.
    '''
    joints = ls('*', r=1, type='joint')
    for j in joints: j.displayLocalAxis.set(False)


def showAllJointLabels():
    '''
    Show all joint labels.
    '''
    joints = ls("*", r=1, type='joint')
    for j in joints:
        if (j.attr("drawLabel").isLocked()): continue
        j.attr("drawLabel").set(True)


def hideAllJointLabels():
    '''
    Hide all joint labels.
    '''
    joints = ls("*", r=1, type='joint')
    for j in joints:
        if (j.attr("drawLabel").isLocked()): continue
        j.attr("drawLabel").set(False)
    

def isBranching(j):
    '''
    True true if this joint branches into multiple joints.
    '''
    
    children = filter(lambda c: type(c) == nt.Joint, j.getChildren())
    if (len(children) > 1): return True
    return False

def autoLabelBindJoints():
    '''
    Set joint labels based on bind joint names
    '''
    joints = ls("*bind_joint", r=1)+ls("*end_joint", r=1)
    
    for j in joints:
        try:
            name = j.shortName().split('|')[-1]
            nameComps = name.split("_")[:-2]
            side = nameComps[0].lower()
            type = nameComps[1].lower()
            
            # Joint side
            if (side in JNT_SIDE): j.side.set(JNT_SIDE[side])
            
            # Joint name
            if (type in JNT_TYPE):
                j.attr("type").set(JNT_TYPE[type])
            else:
                j.attr("type").set(JNT_TYPE_OTHER)
                otherName = '_'.join(nameComps[1:])
                if (name.endswith("end_joint")): otherName += "_end_joint"
                j.otherType.set(otherName)
        except:
            print 'Unable to properly label joint "'+str(j)+'".  Check to see if the joint name is following conventions.'
            continue
            
            
def orientBipedalJointStructure():
    '''
    Assuming the proper naming conventions for our built in skeletons, grab a bunch of chains and fix their orientations.
    Forward world is z-axis, right world is the negative x-axis, and up is the y-axis.
    '''
    
    joints = ls('*bind_joint', r=1, type='joint')
    endJoints = ls(lf=1, dag=1, type="joint")
    

    """
    def skipJoint(s):
        for f in ["thumb", "index", "middle", "ring", "pinky"]:
            if f in s: return True
        return False
    """
    
    def skipJoint(s): return False
            
    for j in joints:
        
        n = j.shortName()
        
        if (j in endJoints or skipJoint(n)): continue
        """
        try:
        """
            
        # Handle orientation cases, starting with the most specific and moving on to the most generic
        if n.startswith("left_clavicle"):
            orientJoint_Absolute(j)
        
        elif n.startswith("right_clavicle"):
            orientJoint_Absolute(j, (180, 0, 0))
        
        elif n.startswith("left_foot") or n.startswith("right_foot"):
            orientJoint_Absolute(j)
            
        elif n.startswith("left_ball") or n.startswith("right_ball"):
            orientJoint_Absolute(j, (0,-90,0))
        
        elif n.startswith("left_palm") or n.startswith("right_palm"):
            orientJoint_Relative(j, (0, 0, 0))
        
        elif    n.startswith("left_upperarm") or \
                n.startswith("left_lowerarm") or \
                n.startswith("left_hand"):
            armTransforms = [   ls("left_hand_bind_joint")[0],
                                ls("left_lowerarm_bind_joint")[0],
                                ls("left_upperarm_bind_joint")[0]    ]
            normal = getCoplanarNormal(armTransforms)
            
            if n.startswith("left_upperarm"):
                sc = "left_lowerarm_bind_joint"
            elif n.startswith("left_lowerarm"):
                sc = "left_hand_bind_joint"
            else:
                sc = None
            
            orientJoint_Aim(j, normal, (1,0,0), (0,0,-1), sc)
            
        elif    n.startswith("left_upperleg") or \
                n.startswith("left_lowerleg"):
            legTransforms = [   ls("left_upperleg_bind_joint")[0],
                                ls("left_lowerleg_bind_joint")[0],
                                ls("left_foot_bind_joint")[0]    ]
            normal = getCoplanarNormal(legTransforms)
            
            if n.startswith("left_upperleg"):
                sc = "left_lowerleg_bind_joint"
            elif n.startswith("left_lowerleg"):
                sc = "left_foot_bind_joint"
            else:
                sc = None
            
            orientJoint_Aim(j, normal, (1,0,0), (0,0,-1), sc)
            
        elif    n.startswith("right_upperarm") or \
                n.startswith("right_lowerarm") or \
                n.startswith("right_hand"):
            armTransforms = [   ls("right_upperarm_bind_joint")[0],
                                ls("right_lowerarm_bind_joint")[0],
                                ls("right_hand_bind_joint")[0]    ]
            normal = getCoplanarNormal(armTransforms)
            
            if n.startswith("right_upperarm"):
                sc = "right_lowerarm_bind_joint"
            elif n.startswith("right_lowerarm"):
                sc = "right_hand_bind_joint"
            else:
                sc = None
            
            orientJoint_Aim(j, normal, (-1,0,0), (0,0,1), sc)
            
        elif    n.startswith("right_upperleg") or \
                n.startswith("right_lowerleg"):
            legTransforms = [   ls("right_foot_bind_joint")[0] ,
                                ls("right_lowerleg_bind_joint")[0],
                                ls("right_upperleg_bind_joint")[0]    ]
            normal = getCoplanarNormal(legTransforms)
            
            if n.startswith("right_upperleg"):
                sc = "right_lowerleg_bind_joint"
            elif n.startswith("right_lowerleg"):
                sc = "right_foot_bind_joint"
            else:
                sc = None
            
            orientJoint_Aim(j, normal, (-1,0,0), (0,0,1), sc)
            
        elif "thumb" in n or "index" in n or "middle" in n or "ring" in n or "pinky" in n:

            def fingerName(num):
                nameComps = n.split('_')
                nameComps[2] = str(num)
                return '_'.join(nameComps)
            
            makeIdentity(j, jo=0, t=0, s=0, r=1, a=1)
            
            if (n.startswith("left")):
                normal = getCoplanarNormal( [fingerName(1), fingerName(2), fingerName(3)] )
                orientJoint_Aim(j, yWorldUp=normal, xLocalAim=(1,0,0), yLocalUp=(0,0,1))
                
            elif (n.startswith("right")):
                normal = getCoplanarNormal( [fingerName(1), fingerName(2), fingerName(3)] )
                orientJoint_Aim(j, yWorldUp=-normal, xLocalAim=(-1,0,0), yLocalUp=(0,0,-1))
        
        elif n.startswith("center"):
            if (isBranching(j)):
                orientJoint_Absolute(j, (-90, 0, 90))
            else:
                orientJoint_Aim(j, (0,0,-1), (1,0,0))
            
        elif n.startswith("right"):
            orientJoint_Aim(j, (0,0,-1), (-1,0,0))
            
        elif n.startswith("left"):
            orientJoint_Aim(j, (0,0,1), (1,0,0))
        """
        except Exception as e:
            # Print the error and putter along.
            # Revisit this later... not the way to do things.
            print "ERROR ORIENTING JOINT: "+str(e)
        """
    for j in endJoints:
        
        for n in ['rx','ry','rz']: j.attr(n).unlock()
        j.rotate.set(0,0,0)
        j.jointOrient.set(0,0,0)


def orientJointChain(startJoint, endJoint, yWorldUp=(0,0,-1), xLocalAim=(1,0,0), yLocalUp=(0,1,0)):
    '''
    Aim an entire joint chain such that the y-axis points in a particular world direction.
    Default direction is backwards down the negative z-axis.
    '''
    
    if (type(startJoint) != nt.Joint):
        raise Exception('Invalid start joint specified: '+str(startJoint))
    if (type(endJoint) != nt.Joint):
        raise Exception('Invalid end joint specified: '+str(endJoint))
        
    # Extract entire joint chain
    chain = []
    currentJoint = endJoint
    chainComplete = False
    while (currentJoint != None):
        if (type(currentJoint) != nt.Joint): break
        chain = [currentJoint] + chain
        if (currentJoint == startJoint):
            chainComplete = True
            break
        currentJoint = currentJoint.getParent()
    if not chainComplete:
        raise Exception('Invalid joint chain specified: '+str(startJoint)+' to '+str(endJoint))
        
    # Orient each joint in the chain
    for i in xrange(len(chain)-1):
        currJ = chain[i]
        nextJ = chain[i+1]
        
        currParent = currJ.getParent()
        children = currJ.getChildren()
        
        if (currParent != None): parent(currJ, w=1)
        parent(children, w=1)
        
        for n in ['rx','ry','rz']: currJ.attr(n).unlock()
        ac = aimConstraint(nextJ, currJ, mo=0, aim=xLocalAim, u=yLocalUp, wu=yWorldUp, wut='vector')
        delete(ac)
        makeIdentity(currJ, jo=0, t=0, s=0, r=1, a=1)

        if (currParent != None): parent(currJ, currParent)
        parent(children, currJ)

 
def orientJoint_Aim(jointToOrient, yWorldUp=(0,0,-1), xLocalAim=(1,0,0), yLocalUp=(0,1,0), specifyChild=None):
    '''
    Orient a single joint toward its child joint.  If it branches into multiple joint, skip this.
    If there are multiple possible children on a joint then specify child must be set.
    '''
    
    if (type(jointToOrient) != nt.Joint): raise Exception('Invalid joint specified: '+str(jointToOrient))

    jointChildren = filter(lambda c: type(c) == nt.Joint, jointToOrient.getChildren())
    if (len(jointChildren) != 1):
        jcNames = map(lambda jc: jc.shortName(), jointChildren)
        if specifyChild in jcNames:
            jointChildren = [PyNode(specifyChild)]
        else:
            raise Exception("Specified joint has more than one child joint.  Set the specifyChild param: "+str(jointToOrient))
    
    jChild = jointChildren[0]
    jParent = jointToOrient.getParent()
    parent(jChild, w=1)
    if (jParent != None): parent(jointToOrient, w=1)
    
    for n in ['rx','ry','rz']: jointToOrient.attr(n).unlock()
    ac = aimConstraint(jChild, jointToOrient, mo=0, aim=xLocalAim, u=yLocalUp, wu=yWorldUp, wut='vector')
    delete(ac)
    makeIdentity(jointToOrient, jo=0, t=0, s=0, r=1, a=1)
    
    parent(jChild, jointToOrient)
    if (jParent != None): parent(jointToOrient, jParent)


def orientJoint_Absolute(jointToOrient, jointOrient=(0,0,0), unparentChildren=True):
    '''
    Orient the joint using absolute joint orient values in world space.
    '''
    
    children = jointToOrient.getChildren()
    jParent = jointToOrient.getParent()
    if (unparentChildren and len(children) > 0): parent(children, w=1)
    if (jParent != None): parent(jointToOrient, w=1)
    
    for n in ['rx','ry','rz']: jointToOrient.attr(n).unlock()
    jointToOrient.rotate.set(0,0,0)
    jointToOrient.jointOrient.set(jointOrient)
    
    if (unparentChildren and len(children) > 0): parent(children, jointToOrient)
    if (jParent != None): parent(jointToOrient, jParent)


def orientJoint_Relative(jointToOrient, jointOrient=(0,0,0), unparentChildren=True):
    '''
    Orient the joint using relative joint orient values in local space.
    '''
    
    children = jointToOrient.getChildren()
    if (unparentChildren and len(children) > 0): parent(children, w=1)
    
    for n in ['rx','ry','rz']: jointToOrient.attr(n).unlock()
    jointToOrient.rotate.set(0,0,0)
    jointToOrient.jointOrient.set(jointOrient)
    
    if (unparentChildren and len(children) > 0): parent(children, jointToOrient)


### Pre-autorig preparation ###

def prepareBipedalJointPoses(IK_DIST_FROM_ARM_LENGTH = 0.0075):
    '''
    Prepare skeleton's bind joint poses.  Assume everything is named correctly.
    
    IK_DIST_FROM_ARM_LENGTH: Determines arm bend on the skeleton's T-Pose
    '''
    
    root_bindJoint = ls("center_root_bind_joint")[0]
    
    leftUpperArm_bindJoint = ls("left_upperarm_bind_joint")[0]
    leftLowerArm_bindJoint = ls("left_lowerarm_bind_joint")[0]
    leftHand_bindJoint = ls("left_hand_bind_joint")[0]
    
    rightUpperArm_bindJoint = ls("right_upperarm_bind_joint")[0]
    rightLowerArm_bindJoint = ls("right_lowerarm_bind_joint")[0]
    rightHand_bindJoint = ls("right_hand_bind_joint")[0]
    
    spine_bindJoints = ls("center_spine_*_bind_joint")
    
    neck_bindJoints = ls("center_neck_*_bind_joint")
    
    allJoints = [leftUpperArm_bindJoint, leftLowerArm_bindJoint, leftHand_bindJoint,
              rightUpperArm_bindJoint, rightLowerArm_bindJoint, rightHand_bindJoint]
    
    # Save old arm transforms
    savedTransforms = {}
    def saveOldArmTransform(t):
        sl = spaceLocator(n=t.shortName()+"_saved", )
        pc = parentConstraint(t, sl, mo=0)
        delete(pc)
        savedTransforms[t] = sl
        
    for t in allJoints: saveOldArmTransform(t)
    
    # World space positions
    leftUpperArm_pos = dt.Vector(xform(leftUpperArm_bindJoint, q=1, ws=1, t=1))
    leftLowerArm_pos = dt.Vector(xform(leftLowerArm_bindJoint, q=1, ws=1, t=1))
    leftHand_pos = dt.Vector(xform(leftHand_bindJoint, q=1, ws=1, t=1))
    
    rightUpperArm_pos = dt.Vector(xform(rightUpperArm_bindJoint, q=1, ws=1, t=1))
    rightLowerArm_pos = dt.Vector(xform(rightLowerArm_bindJoint, q=1, ws=1, t=1))
    rightHand_pos = dt.Vector(xform(rightHand_bindJoint, q=1, ws=1, t=1))
    
    # Computed informations
    leftArm_length = leftUpperArm_pos.distanceTo(leftLowerArm_pos)+leftLowerArm_pos.distanceTo(leftHand_pos)
    rightArm_length = rightUpperArm_pos.distanceTo(rightLowerArm_pos)+rightLowerArm_pos.distanceTo(rightHand_pos)
    
    # Point arms toward their world axis ends
    orientJoint_Absolute(leftUpperArm_bindJoint, (90, 0, 0), False)
    orientJoint_Absolute(rightUpperArm_bindJoint, (-90, 0, 0), False)
    
    # Align hand along upper arm joints in world space
    leftIK = ikHandle(sj = leftUpperArm_bindJoint, ee = leftHand_bindJoint)[0]
    rightIK = ikHandle(sj = rightUpperArm_bindJoint, ee = rightHand_bindJoint)[0]
    
    leftIK.tz.set(leftUpperArm_pos.z)
    rightIK.tz.set(rightUpperArm_pos.z)
    
    leftIK.tx.set(leftArm_length+leftUpperArm_pos.x-IK_DIST_FROM_ARM_LENGTH)
    rightIK.tx.set(-rightArm_length+rightUpperArm_pos.x+IK_DIST_FROM_ARM_LENGTH)
    
    refresh() # So IK Handle leave skeleton changes on deletion
    delete(leftIK)
    delete(rightIK)
    
    # Point hands toward their world axis ends
    orientJoint_Absolute(leftHand_bindJoint, (90, 0, 0), False)
    orientJoint_Absolute(rightHand_bindJoint, (-90, 0, 0), False)
    
    # Aim start and end bind joints up in world space
    """
    lockChildOrientsAndAimUp(spine_bindJoints[0], (1,0,0), (0,-1,0))
    lockChildOrientsAndAimUp(spine_bindJoints[-1], (1,0,0), (0,-1,0))
    """
    
    # Re-orient bipedal structure
    orientBipedalJointStructure()
    
    # SET T-POSE
    if (objExists("charTPose")): delete(PyNode("charTPose"))
    dagPose(root_bindJoint, n="charTPose", save=1)

    # SET BIND POSE
    
    # Rotate to bind pose using the locators we saved earlier
    for t in allJoints:
        sl = savedTransforms[t]
        oc = orientConstraint(sl, t, mo=0)
        delete(oc)
        delete(sl)
    
    if (objExists("charBindPose")): delete(PyNode("charBindPose"))
    dagPose(root_bindJoint, n="charBindPose", save=1)


### Pre-autorig guides and helpers ###
    
def chainRotationPath(base, end, simRotation=45, detail=5, axis='z', curveColorIndex=16):
    '''
    Given a chain of transforms, draw a curve simulating what
    a consistent rotation value down the chain on a single axis looks like. 
    '''
    
    baseChain = map(lambda s: PyNode(s), chainBetween(base, end))
    
    rotArcDummyParent = group(em=1, n=str(baseChain[0])+'_rotArcDummyParent')
    parentConstraint(base, rotArcDummyParent, mo=0)
    
    endTransforms = [baseChain[-1]]
    
    # Create a series of chains that simulate what a given rotation
    # may look like on the specified chain.  These given rotation
    # are increments of 'simRotation' divided by 'detail'
    for i in xrange(detail-1):
        simChain = []
        
        # Base of simulated chain
        simBase = group(em=1, n=str(baseChain[0])+'_sim_'+str(i))
        delete(parentConstraint(baseChain[0], simBase, mo=0))
        parent(simBase, rotArcDummyParent)
        simChain.append(simBase)
        
        # The rest of the simulated chain
        prevSim = simBase
        for bcTrans in baseChain[1:]:
            simParent = group(em=1, n=str(bcTrans)+'_simParent_'+str(i))
            delete(parentConstraint(bcTrans, simParent, mo=0))
            parent(simParent, prevSim)
            bcTrans.translate >> PyNode(simParent).translate
            bcTrans.rotate >> PyNode(simParent).rotate
            if (isinstance(bcTrans, nt.Joint)): bcTrans.jointOrient >> simParent.rotateAxis
            bcTrans.scale >> PyNode(simParent).scale
            
            sim = group(em=1, n=str(bcTrans)+'_sim_'+str(i))
            delete(parentConstraint(bcTrans, sim, mo=0))
            parent(sim, simParent)
            
            prevSim = sim
            simChain.append(sim)
            
        # Locator marks the end of the chain
        endTransforms.append(simChain[-1])
        
        # Add rotation to the chain
        for sim in simChain[:-1]:
            rotAttr = None
            if (axis == 'z'):
                rotAttr = sim.rz
            elif (axis == 'y'):
                rotAttr = sim.ry
            elif (axis == 'x'):
                rotAttr = sim.rx
            else:
                raise Exception('Invalid rotation axis to simulate specified.')
            rotAttr.set((i+1)*(simRotation/float(detail)))
            
    # Create a curve driven by the tranform simulations
    simCurve = createCurveThroughObjects(endTransforms, degree=2)
    simCurve.inheritsTransform.set(0)
    
    
    simCurveShape = simCurve.getShape()
    simCurveShape.overrideEnabled.set(1) # Enable display overrides
    simCurveShape.overrideDisplayType.set(2) # Reference Curve
    
    '''
    simCurveShape.overrideColor.set(curveColorIndex) # Set curve to white
    '''

    clusters = []
    for i in xrange(detail):
        et = endTransforms[i]
        cv = simCurve.cv[i]
        clstr = cluster(cv)[1]
        clstr.inheritsTransform.set(0)
        clusters.append(clstr)
        pointConstraint(et, clstr, mo=0)
        hide(clstr)
    
    mainGrp = group(simCurve, clusters, rotArcDummyParent, n=str(baseChain[0])+'_simGrp')
    return mainGrp
    
def createFingerRotationPaths(simRotation = 45, sides = ['left', 'right'], fingers = ['thumb', 'index', 'middle', 'ring', 'pinky'], mainGrpName="FINGER_ROTATION_PATHS"):
    '''
    Show rotation paths for fingers.
    '''
    
    # Get the root group of all the finger simulation path systems
    if (objExists(mainGrpName)):
        mainGrp = PyNode(mainGrpName)
        delete(mainGrp.getChildren())
    else:
        mainGrp = group(em=1, n=mainGrpName)
    
    simGrps = []
    for side in sides:
        for finger in fingers:
            try:
                # See of the finger chain exists
                base = PyNode(side + '_' + finger + '_1_bind_joint')
                end = PyNode(side + '_' + finger + '_end_joint')
                chainBetween(base, end)
            except:
                # There's an error so move along...
                continue
            # Otherwise create the simulation curve
            simGrp = chainRotationPath(base, end, simRotation, 5, 'z')
            simGrps.append(simGrp)
    
    # Clean-up
    if (len(simGrps) == 0):
        delete(mainGrp)
    else:
        parent(simGrps, mainGrp)
    
    select(cl=1)


def removeFingerRotationPaths(mainGrpName="FINGER_ROTATION_PATHS"):
    '''
    Remove finger rotation path system.
    '''
    
    if (objExists(mainGrpName)): delete(mainGrpName)
    
 
### UTILITES COPIED FROM THE META-RIGGING SYSTEM ###

def chainBetween(start, end):
    '''
    get all the nodes between start obj and end obj
    
    start:
    
    end:
    
    return:
        a list of all objects between start obj and end obj
        if end is not an ancestor of start, returns a list containing start    
    '''
    if not objExists(start):
        printError("chainBetween: object %s doesn't exists"%start)
    if not objExists(end):
        printError("chainBetween: object %s doesn't exists"%end)
    
    start = PyNode(start)
    end = PyNode(end)
    
    chainList = [start.longName()]
    
    if start.longName() == end.longName():
        return [start]
    
    path = start
    rest = end.longName().replace(start.longName(), '', 1)
    if rest == end.longName():
        printError("chainBetween: %s isn't an ancestor of %s"%(end.name(), start.name()) )
    objList = rest.split('|')
    for obj in objList:
        if obj:
            path = path + "|" + obj
            chainList.append(path)
            
    return chainList
    
def createCurveThroughObjects(objects, degree=None, offset=None):
    '''
    creates a curve the goes through all the objects in the list given from start to finish
    
    objects:
        List of objects to weave curve through, goes in order.
    
    degree:
        Degree of the output curve.
        
    offset:
        Offset in local space from each given object in which a CV should be created.
        
    return:
        The curve transform object created.
    '''
    for obj in objects:
        if not objExists(obj):
            printWarning("createCurveThroughObjects: object %s doesn't exist"%obj)
            return None
    objects = map(lambda x: PyNode(x), objects)
    
    if not degree:
        degree = len(objects)-1
    if degree <= 0:
        printWarning('createCurveThroughObjects: less than two objects given')
        return None
        
    points = []
    for obj in objects:
        if (offset == None):
            pnt = obj.getTranslation(space = 'world')
        else:
            pnt = mu.getWorldPositionVector(obj, offset)
        points.append(pnt)
        
    newCurve = curve(d=degree, p=points)

    return newCurve
    
    
### GUI ###

class blockModelHelper_GUI:
    
    name = "BlockModelHelper"
    title = "Block Model Assistant"
    margins = 3
    buttonHeight = 35
    buttonWidth = 350
    doubleButtonRatios = [2,2,2]
    singleButtonRatios = [2,4]
    
    def __init__(self):
        self.gui()
        
    def gui(self):
        
        # Close an already open window
        if (window(self.name, exists=1)):
            deleteUI(self.name)
        
        # Destroy window prefs
        if windowPref(self.name, ex=1):
            windowPref(self.name, r=1)
        
        w = window(self.name, title=self.title, rtf=True, s=False) # rtf: resize to fit, s: window is resizable 
        
        mainFrame = frameLayout(bv=False, lv=False, mh=self.margins, mw=self.margins)
        sectionList = formLayout()
        
        # Resize main window
        def resizeMainWindow():
            w.setHeight(1)
            w.setResizeToFitChildren(True)
        
        # RELOAD FILE WITHOUT SAVING
        def reloadFileCallback():
            lastFilePromptValue = mel.eval('file -q -pmt')
            mel.eval('file -pmt 0') # Squelch any error prompts
            openFile(sceneName(), f=1)
            mel.eval('file -pmt '+str(lastFilePromptValue))
            
        refreshScene = iconTextButton(  p=sectionList,
                                        i='refresh.png',
                                        l='Reload scene without saving',
                                        st='iconAndTextHorizontal',
                                        al='right',
                                        mh=self.margins,
                                        mw=self.margins,
                                        height=self.buttonHeight,
                                        width=self.buttonWidth,
                                        c=reloadFileCallback  )
        sectionList.attachForm(refreshScene, "top", 0)
        
        # BEGIN SKELETON HELPER #
        skeletonFrame = frameLayout(  p=sectionList,
                                      bv=True,
                                      lv=True,
                                      cll=True,
                                      cl=False,
                                      mh=self.margins,
                                      mw=self.margins,
                                      l="Skeleton",
                                      fn="boldLabelFont",
                                      cc=resizeMainWindow  ) 
        skeletonList = verticalLayout(spacing=self.margins)
        
        # - Select bind joints
        frameLayout(p=skeletonList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        selectBindJointsButton = horizontalLayout(ratios=[1,2,6])
        image(i="aselect.png")
        image(i="pickJointObj.png")
        button("Select Bind Joints", c=Callback(selectBindJoints),
                ann='Select all joints in the scene ending with "_bind_joint".')
        selectBindJointsButton.redistribute()
        
        # - Show/hide joint axes
        frameLayout(p=skeletonList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        showHideJointAxesButtons = horizontalLayout(ratios=[1,1,2,2])
        image(i="showManip.png")
        text(l="Axes")
        button("Show", c=Callback(showAllJointLocalRotationAxes),
                ann='Show all joint axes.')
        button("Hide", c=Callback(hideAllJointLocalRotationAxes),
                ann='Hide all joint axes.')
        showHideJointAxesButtons.redistribute()
        
        # - Show/hide joint labels
        frameLayout(p=skeletonList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        showHideJointLabelButtons = horizontalLayout(ratios=[1,1,2,2])
        image(i="text.png")
        text(l="Labels")
        button("Show", c=Callback(showAllJointLabels),
                ann='Show all joint labels.')
        button("Hide", c=Callback(hideAllJointLabels),
                ann='Hide all joint labels.')
        showHideJointLabelButtons.redistribute()
        
        # - Auto label joints based on hierarchy names
        frameLayout(p=skeletonList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        autoLabelJointsButton = horizontalLayout(ratios=[1,2,6])
        image(i="text.png")
        image(i="pickJointObj.png")
        button("Auto-Label Bind Joints", c=Callback(autoLabelBindJoints),
                ann='Automatically label all bind and end joints according to the meta rigging system conventions. '+\
                    'To be labeled, joint names MUST be formatted as such: [side]_[body part]_["bind_joint" or "end_joint"]. '+\
                    'Joints not adhering to those conventions will not be labeled.')
        autoLabelJointsButton.redistribute()

        # - Auto orient joints based on meta rigging bipedal conventions
        frameLayout(p=skeletonList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        autoOrientJointsButton = horizontalLayout(ratios=[3,6])
        image(i="orientJoint.png")
        button("* Auto-Orient Skeleton (BIPED ONLY)", c=Callback(orientBipedalJointStructure),
                ann='Automically orient bind joints assuming a bipedal skeleton.  The result may not be perfect as this is '+\
                    'still "in beta", so check your skeleton anyway!')
        autoOrientJointsButton.redistribute()


        skeletonList.redistribute()
        sectionList.attachControl(skeletonFrame, "top", 0, refreshScene)
        # END SKELETON HELPER #

        
        ## BEGIN BLOCK MODEL HELPER ##
        blockModelFrame = frameLayout(  p=sectionList,
                                        bv=True,
                                        lv=True,
                                        cll=True,
                                        cl=False,
                                        mh=self.margins,
                                        mw=self.margins,
                                        l="Block Model",
                                        fn="boldLabelFont",
                                        cc=resizeMainWindow  )   
        blockModelList = verticalLayout(spacing=self.margins)
        

        ## - Select bind joint mesh transforms
        frameLayout(p=blockModelList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        selectBlockModelButton = horizontalLayout(ratios=[1,2,6])
        image(i="aselect.png")
        image(i="out_polyCube.png")
        button("Select Block Model", c=Callback(selectBindJointMeshTransforms),
                ann='Select all blocks parented to bind joints.')
        selectBlockModelButton.redistribute()
        
        ## - Parent/unparent block models
        frameLayout(p=blockModelList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        showHideJointAxesButtons = horizontalLayout(ratios=self.doubleButtonRatios)
        image(i="parent.png")
        button("Parent Blocks", c=Callback(parentMeshesToBindJoints),
                ann="Parent all polygon meshes in the root of the scene to bind joints with the same pivot location. "+\
                    "Polygon meshes unparented through this interface should have this property (unless they were moved).")
        button("Unparent Blocks", c=Callback(unparentMeshesFromBindJoints),
                ann="Unparent blocks from bind joints and set their pivot to the bind joint parent's location.")
        showHideJointAxesButtons.redistribute()
        
        ## - Create blocks
        frameLayout(p=blockModelList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        createBlocksButton = horizontalLayout(ratios=self.singleButtonRatios)
        image(i="polyCube.png")
        button("On Selected Joints: Create Blocks", c=Callback(create_block_model_cmd))
        createBlocksButton.redistribute()
        
        ## - Mirror blocks
        frameLayout(p=blockModelList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        mirrorBlocksButton = horizontalLayout(ratios=self.singleButtonRatios)
        image(i="polyMirrorCut.png")
        button("Mirror and Fill in Missing Blocks", c=Callback(bindJointMeshes_mirror))
        mirrorBlocksButton.redistribute()


        blockModelList.redistribute()
        sectionList.attachControl(blockModelFrame, "top", 0, skeletonFrame)
        ## END BLOCK MODEL HELPER ##
        

        ## BEGIN PROPORTION GUIDE HELPER ##
        guideFrame = frameLayout(  p=sectionList,
                                   bv=True,
                                   lv=True,
                                   cll=True,
                                   cl=False,
                                   mh=self.margins,
                                   mw=self.margins,
                                   l="Proportion Guides",
                                   fn="boldLabelFont",
                                   cc=resizeMainWindow  )   
        guideList = verticalLayout(spacing=self.margins)

        # - Preview finger rotation paths
        frameLayout(p=guideList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        fingerRotationPathsButton = horizontalLayout(ratios=[1,2,3,3])
        image(i="hands.png") # image(i="kinSplineHandle.png")
        text(l="Finger\nRotation")
        button("Create Curves", c=Callback(createFingerRotationPaths),
                ann='Create a system of curves which show the path of the fingertips when the finger joints are evenly rotated.  Updates in real-time.  Assumes capstone finger naming conventions.')
        button("Remove Curves", c=Callback(removeFingerRotationPaths),
                ann='Remove the fingertip rotation guides.')
        fingerRotationPathsButton.redistribute()
        
        
        guideList.redistribute()
        sectionList.attachControl(guideFrame, "top", 0, blockModelFrame)
        ## END PROPORTION GUIDE HELPER ##
        
        
        ## BEGIN PRE-AUTORIG HELPER ##
        preAutoRigFrame = frameLayout(  p=sectionList,
                                        bv=True,
                                        lv=True,
                                        cll=True,
                                        cl=False,
                                        mh=self.margins,
                                        mw=self.margins,
                                        l="Pre Auto-Rig",
                                        fn="boldLabelFont",
                                        cc=resizeMainWindow  )                                      
        preAutoRigList = verticalLayout(spacing=self.margins)
        
        
        ## - Remove all blocks from the skeleton and parent constrain them to the bind joints
        frameLayout(p=preAutoRigList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        parentConstrainBlocksButton = horizontalLayout(ratios=self.singleButtonRatios)
        image(i="parentConstraint.png")
        button("Parent Constrain Blocks", c=Callback(parentConstrainMeshesToBindJoints))
        parentConstrainBlocksButton.redistribute()
        
        ## - Create the required bipedal character poses
        frameLayout(p=preAutoRigList, bv=True, lv=False, bs="out", width=self.buttonWidth, height=self.buttonHeight)
        preparePosesButton = horizontalLayout(ratios=self.singleButtonRatios)
        image(i="goToBindPose.png")
        button("* Create Pre Auto-Rig Poses (BIPED ONLY)", c=Callback(prepareBipedalJointPoses))
        preparePosesButton.redistribute()
        
        
        preAutoRigList.redistribute()
        sectionList.attachControl(preAutoRigFrame, "top", 0, guideFrame)
        sectionList.attachForm(preAutoRigFrame, "bottom", 0)
        ## END PRE-AUTORIG HELPER ##
        
        showWindow(w)

blockModelHelper_GUI()