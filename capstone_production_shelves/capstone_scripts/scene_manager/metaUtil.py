################################################################
# Misc utilities for the meta-rigging system and the templates #
################################################################

from pymel.core import *
from scene_manager.methods import *
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as api
import sys

# MAYA NODE STUFF

def getNextUniqueName(n):
    if objExists(n):
        return PyNode(n).nextUniqueName()
    else:
        return n
        
def getBaseName(n):
    if (isinstance(n, PyNode)):
        return n.shortName().split('|')[-1]
    elif (isinstance(n, str)):
        return n.split('|')[-1]
    return None

def getModdedName(n, newNamePattern="%s"):
    return getNextUniqueName(   newNamePattern.replace('%s', getBaseName(n))  )

def reloadWithoutSaving():
    lastFilePromptValue = mel.eval('file -q -pmt')
    mel.eval('file -pmt 0') # Squelch any error prompts
    openFile(sceneName(), f=1)
    mel.eval('file -pmt '+str(lastFilePromptValue))

def getSkipAxes(axis):
    '''
    Based on a single axis, return a list of axes to skip when
    specifying an axis for constraints.
    
    axis:
        A single letter axis as a string: 'x', 'y', or 'z'
    '''
    
    axis = axis.strip('-')
    
    if axis == 'x':
        return ['y', 'z']
    elif axis == 'y':
        return ['x', 'z']
    elif axis == 'z':
        return ['x', 'y']
    else:
        raise Exception("getSkipAxes: Please specify a valid axis 'x', 'y', or 'z'.")
        
def axisScalar(axis):
    '''
    Return 1 if the axis if positive or -1 if it's negative.
    '''
    
    sAxis = axis.strip('-')
    if (sAxis != 'x' and sAxis != 'y' and sAxis != 'z'):
        raise Exception("axisScalar: Please specify a positive or negative axis 'x', 'y', or 'z'.")
    
    if axis.startswith('-'):
        return -1
    else:
        return 1

def axisVector(axis):
    '''
    Return a normalized vector associated with the given axis.
    '''
    
    sAxis = axis.strip('-')
    if (sAxis != 'x' and sAxis != 'y' and sAxis != 'z'):
        raise Exception("getAxisVector: Please specify a positive or negative axis 'x', 'y', or 'z'.")
        
    if sAxis == 'x':
        return dt.Vector(axisScalar(axis), 0, 0)
    elif sAxis == 'y':
        return dt.Vector(0, axisScalar(axis), 0)
    else:
        return dt.Vector(0, 0, axisScalar(axis))
        
def axisAttr(attr, axis):
    '''
    Given an attribute that is divided into three components,
    return the child attribute associated with the given axis.
    '''
    
    # Check axis
    sAxis = axis.strip('-')
    if sAxis != 'x' and sAxis != 'y' and sAxis != 'z':
        raise Exception('axisAttr: Please specify a valid axis "x", "y", or "z".')
    
    # Check attribute
    if not isinstance(attr, Attribute):
        raise Exception('axisAttr: Please specify a valid attribute.')
        
    children = attr.getChildren()
    if len(children) != 3:
        raise Exception("axisAttr: Attribute doesn't have three child components.")
    
    # Return attribute
    if sAxis == 'x':
        return children[0]
    elif sAxis == 'y':
        return children[1]
    else:
        return children[2]

# SHAPES AND ANIMS

def transferShapes(srcs, tgt, space='local'):
    '''
    Replace the shapes of a target object with shapes from a list of source objects.
    Delete the source transforms when finished.
    
    srcs:
        List of objects with shapes to transfer
    tgt:
        Object receiving the shapes
    space:
        'local' maintains the same coordinates relative to its parent transform
        'world' maintains the same coordinates of the shape in world space
    '''
    tgtShapes = tgt.getChildren(s=1)
    
    if not isinstance(srcs, list):
        srcs = [srcs]
    
    for src in srcs:
    
        src = PyNode(src)
    
        if (space == 'local'):
        
            # Cancel out any tranformations so shape transfer is
            # always from the source's center to the target's center
            if src.getParent() != None:
                parent(src, w=1)
            worldCenter = group(em=1, n="world_center")
            delete(parentConstraint(worldCenter, src, mo=0))
            delete(worldCenter)
            
        elif (space == 'world'):
            
            # Make sure the shape transfers to the new transform but
            # maintains its current position in in world space
            objCenter = group(em=1, n="object_center")
            delete(parentConstraint(tgt, objCenter, mo=0))
            delete(scaleConstraint(tgt, objCenter, mo=0))
            parent(src, objCenter)
            objCenter.translate.set(0,0,0)
            objCenter.rotate.set(0,0,0)
            objCenter.scale.set(1,1,1)
            parent(src, w=1)
            delete(objCenter)

        else:
            raise Exception('replaceShapes: Specified space must be "local" or "world".')
        
        makeIdentity(src, t=1, r=1, s=1, apply=1)
        
        # Transfer source shapes to target transform
        srcShapes = src.getChildren(s=1)
        for srcShape in srcShapes:
            parent(srcShape, tgt, s=1, r=1)
    
    # Get rid of old shapes 
    for tgtShape in tgtShapes:
        parent(tgtShape, srcs[0], s=1, r=1)
    
    # Delete all sources
    delete(srcs)

def getScaleSpace(forwardMarker, upMarker, widthMarker, name='scaleSpace', worldDown=(0,-1,0)):
    '''
    Return a positioned and scaled group node representing a non-uniformly scaled sphere
    in world space.  The size and position of this group is determined by several locators.
    By default the world down direction is considered -y.

    forwardMarker:
        Locator representing the forward direction of the scaled space.
        This is where the z-axis will point.
        
    upMarker:
        Locator representing the top of the scaled space.
        This is where the y-axis will point.
        
    widthMarker:
        Distance of the width marker from the plane created by the forward direction, up direction, 
        down direction (world space -y), and calculated center determines the width of the scaled space.
    
    name:
        What to name the scaled space group.
        
    worldDown:
        The world direction considered "down" for the scale space.  This helps determine where the center
        of the scale space is.  Defaults to world negative y direction.
    '''
    
    # Establish down direction, assumes world -y is down
    downMarker = spaceLocator(n=name+'_downLoc')
    
    delete(pointConstraint(upMarker, downMarker, mo=0))
    move(downMarker, worldDown, ws=1, r=1)

    # Figure out center of scaled space
    centerMarker = spaceLocator(n=name+'_centerLoc')
    
    downMarkerAimUp = aimConstraint(upMarker, downMarker, aim=(0,0,1), u=(0,1,0), wut='object', wuo=forwardMarker)
    delete(parentConstraint(downMarker, centerMarker, mo=0))
    parent(centerMarker, downMarker)
    delete(pointConstraint(forwardMarker, centerMarker, sk=['x', 'y'], mo=0))
    delete(downMarkerAimUp)
    parent(centerMarker, w=1)
    delete(downMarker)
    
    # Figure out the width of this scale space using the position of the width marker
    # relative to the plane established by forwardMarker, upMarker, and centerMarker
    adjustedWidthMarker = spaceLocator(n=name+'_adjustedWidthLoc')
    
    delete(aimConstraint(forwardMarker, centerMarker, aim=(0,0,1), u=(0,1,0), wut='object', wuo=upMarker))
    delete(parentConstraint(centerMarker, adjustedWidthMarker, mo=0))
    parent(adjustedWidthMarker, centerMarker)
    delete(pointConstraint(widthMarker, adjustedWidthMarker, sk=['y','z'], mo=0))
    parent(adjustedWidthMarker, w=1)
    
    # Establish transform that represents the non-uniform scaled space
    scaleSpaceGrp = group(em=1, n=name)
    
    spaceHeight = getWorldPositionVector(centerMarker).distanceTo(getWorldPositionVector(upMarker))
    spaceWidth = getWorldPositionVector(centerMarker).distanceTo(getWorldPositionVector(adjustedWidthMarker))
    spaceDepth = getWorldPositionVector(centerMarker).distanceTo(getWorldPositionVector(forwardMarker))
    
    delete(pointConstraint(centerMarker, scaleSpaceGrp, mo=0))
    delete(aimConstraint(forwardMarker, scaleSpaceGrp, aim=(0,0,1), u=(0,1,0), wut='object', wuo=upMarker))
    scaleSpaceGrp.scale.set(spaceWidth, spaceHeight, spaceDepth)
    
    delete(adjustedWidthMarker)
    delete(centerMarker)
    
    return scaleSpaceGrp


# SKINNING

def followSkinnedMesh(skinMeshSource, meshTarget, removeUnusedInfluences=1):
    '''
    Copying the skinning of one mesh to another unskinned mesh.  Culls out unused influences by default.
    
    skinMeshSource:
        Source mesh with skinning.
        
    meshTarget:
        Mesh WITHOUT skinning that will have the source weights copied to.
    
    removeUnusedInfluences:
        After copying the weights over, if true removed unused skin influences.
    '''
    
    if skinMeshSource == None:
        raise Exception('metaUtil.followSkinnedMesh: Please specify a skinned mesh/surface source.')
    
    skinMeshSource = PyNode(skinMeshSource)
    
    if isinstance(skinMeshSource, nt.Transform):
        skinMeshSource = skinMeshSource.getShape()
        
    if (skinMeshSource == None):
        raise Exception('metaUtil.followSkinnedMesh: No skinned mesh/surface source specified.')
    
    meshTarget = PyNode(meshTarget)
    
    # Find the skinCluster
    skin = listConnections(skinMeshSource, type='skinCluster')
    if (len(skin) == 0):
        raise Exception('metaUtil.followSkinnedMesh: No skinCluster found on the source mesh.')
    else:
        skin = skin[0]
        
    # Query skinCluster information
    influences = skin.getInfluence()
    skinMethod = skin.getSkinMethod()
    bindMethod = skin.getBindMethod()
    
    # Create skinCluster and copy over weights for each curve
    meshTarget.inheritsTransform.set(0)
    select(influences, meshTarget)
    targetSkin = skinCluster(toSelectedBones=1, obeyMaxInfluences=0, nw=1, sm=skinMethod, bm=bindMethod, n=str(meshTarget)+'_skinCluster')
    copySkinWeights(ss=skin, ds=targetSkin, noMirror=1, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
    
    # Trim out unused influences
    if removeUnusedInfluences:
        select(meshTarget)
        mel.eval('removeUnusedInfluences;')
        select(cl=1)
    
    # Return the new skinCluster
    return targetSkin

def listInfluences(skinMesh):
    '''
    List the influences of a specified skinned mesh.
    
    skinMesh:
        Source mesh with skinning.
    '''
    
    if skinMesh == None:
        raise Exception('metaUtil.listInfluences: Please specify a skinned mesh/surface.')
    
    skinMesh = PyNode(skinMesh)
    
    if isinstance(skinMesh, nt.Transform):
        skinMesh = skinMesh.getShape()
        
    if (skinMesh == None):
        raise Exception('metaUtil.listInfluences: No skinned mesh/surface specified.')
        
    # Find the skinCluster
    skin = listConnections(skinMesh, type='skinCluster')
    if (len(skin) == 0):
        raise Exception('metaUtil.listInfluences: No skinCluster found on the specified skinned mesh.')
    else:
        skin = skin[0]
        
    return skin.getInfluence()
    

# ANIMATION AND ATTRIBUTES

def swapChannelBoxAttributes(o1, o2):
    '''
    Between two objects, swap tbe values of attributes visible in the channel box
    which share the same name (both keyable and non-keyable).
    '''
    
    o1Attrs = set(listAttr(o1, k=1, u=1) + listAttr(o1, cb=1, u=1))
    o2Attrs = set(listAttr(o2, k=1, u=1) + listAttr(o2, cb=1, u=1))
    sharedAttrs = o1Attrs.intersection(o2Attrs)
    
    for attrName in sharedAttrs:
        value = o1.attr(attrName).get()
        o1.attr(attrName).set( o2.attr(attrName).get() )
        o2.attr(attrName).set(value)
    
def transferChannelBoxAttributes(source, target):
    '''
    From the source object to the target, transfer values of attributes visible in the channel box
    which share the same name (both keyable and non-keyable).
    '''
    
    srcAttrs = set(listAttr(source, k=1, u=1) + listAttr(source, cb=1, u=1))
    tgtAttrs = set(listAttr(target, k=1, u=1) + listAttr(target, cb=1, u=1))
    sharedAttrs = srcAttrs.intersection(tgtAttrs)
    
    for attrName in sharedAttrs:
        target.attr(attrName).set( source.attr(attrName).get() )

def createRotateOrderProxyAttr(obj):
    '''
    Create a keyable attribute "Rot Order" that connects directly to the object's internal rotate order attribute.
    This allows for an alterable default value.
    '''

    obj = PyNode(obj)
    obj.addAttr("rotOrder", at="enum", enumName="xyz:yzx:zxy:xzy:yxz:zyx", keyable=1, dv=obj.rotateOrder.get())
    obj.rotOrder >> obj.rotateOrder
    #roAttr.showInChannelBox(1)
    return obj.rotOrder


# NURBs

def getClosestParamOnCurve(curve, worldPos):
    '''
    Return the closest param on a given NURBs curve
    to a specified world coordinate.
    '''
    slist = api.MSelectionList()
    api.MGlobal.getSelectionListByName(PyNode(curve).name(), slist)

    nurbsObj = api.MObject()
    nurbsDag = api.MDagPath()

    slist.getDependNode(0, nurbsObj)
    slist.getDagPath(0, nurbsDag, nurbsObj)
    fnCurve = api.MFnNurbsCurve(nurbsDag)

    su = api.MScriptUtil()
    param = su.asDoublePtr()
    cp = fnCurve.closestPoint(    api.MPoint(worldPos[0], worldPos[1], worldPos[2]),
                                    param, 1.0e-3, api.MSpace.kWorld  )

    return su.getDouble(param)

    
def getClosestPointOnSurface(surface, worldPos):
    '''
    Return the closest UV coordinate on a given NURBs surface
    to a specified world coordinate.
    '''
    slist = api.MSelectionList()
    api.MGlobal.getSelectionListByName(PyNode(surface).name(), slist)

    nurbsObj = api.MObject()
    nurbsDag = api.MDagPath()

    slist.getDependNode(0, nurbsObj)
    slist.getDagPath(0, nurbsDag, nurbsObj)
    fnSurface = api.MFnNurbsSurface(nurbsDag)

    su = api.MScriptUtil()
    u = su.asDoublePtr()
    v = su.asDoublePtr()
    cp = fnSurface.closestPoint(    api.MPoint(worldPos[0], worldPos[1], worldPos[2]),
                                    u, v, False, 1.0e-3, api.MSpace.kWorld  )

    return [su.getDouble(u), su.getDouble(v)]


# ANIMATION

def sdk(driverAttr, driverVals, drivenAttr, drivenVals, defaultDriverVal=0, itt='linear', ott='linear'):
    '''
    Method for succinctly setting SDKs.
    
    driverAttr:
        Attribute that's the driver.
    driverVals:
        List of values for the driver.
    drivenAttr:
        Attribute that's driven.
    drivenVals:
        List of values for the driven attribute.  Should be the same length as the
        list given for the driver.
    '''
    
    driverAttr = PyNode(driverAttr)
    if not isinstance(driverAttr, Attribute):
        raise Exception('sdk: Please specify a valid attribute for the driver.')
    
    drivenAttr = PyNode(drivenAttr)
    if not isinstance(drivenAttr, Attribute):
        raise Exception('sdk: Please specify a valid attribute to be driven.')
    
    if not isinstance(driverVals, list) or not isinstance(drivenVals, list):
        raise Exception('sdk: Please specify lists of driver and driven values.')
        
    if len(driverVals) != len(drivenVals) or len(driverVals) < 2 or len(drivenVals) < 2:
        raise Exception('sdk: Driver and driven value lists must be the same size and have at least 2 values each.')
        
    for i in xrange(len(driverVals)):
        driverVal = driverVals[i]
        drivenVal = drivenVals[i]
        driverAttr.set(driverVal)
        drivenAttr.set(drivenVal)
        setDrivenKeyframe(drivenAttr, cd=driverAttr, itt=itt, ott=ott)
        
    driverAttr.set(defaultDriverVal)

def sineDriver(attrs, attrEffectScale=10.0, n='sineDriver'):
    '''
    Drive a series of attributes using a system the generates sine-wave-like results.
    '''
    
    driverGrp = group(em=1, n=n+'_grp')
    driverGrp.inheritsTransform.set(0)
    driverGrp.addAttr('amplitude', k=1, dv=attrEffectScale)
    driverGrp.addAttr('offset', k=1)
    driverGrp.addAttr('frequency', k=1, dv=attrEffectScale)
    
    conversion = createNode('multiplyDivide', n=n+'_conversion_md')
    
    driverGrp.offset >> conversion.input1X
    conversion.input2X.set(360.0/attrEffectScale) # 10 units = 1 full sine rotation
    
    driverGrp.frequency >> conversion.input1Y
    conversion.input2Y.set(360.0/(len(attrs)-1)/attrEffectScale) # 10 units = 1 full sine rotation
    
    md = None
    
    for i in xrange(len(attrs)):
        
        j = i%3
        if (j==0):
            md = createNode('multiplyDivide', n=n+'_frequencyScalar_'+str(i/3)+'_md')    
            freqScalarInput1 = md.input1.getChildren()
            freqScalarInput2 = md.input2.getChildren()
            freqScalarOutput = md.output.getChildren()

        attr = attrs[i]
        
        # Create system to sample sine values from
        select(cl=1)
        sineSpinner = joint(n=n+'_spinner_'+str(i)+'_jnt')
        parent(sineSpinner, driverGrp)
        
        spinnerMarker = group(em=1, n=n+'_spinnerMarker_'+str(i)+'_loc')
        parent(spinnerMarker, sineSpinner)
        spinnerMarker.ty.set(1)
        
        sineSampler = group(em=1, n=n+'_sineSampler_'+str(i)+'_loc')
        parent(sineSampler, driverGrp)
        pointConstraint(spinnerMarker, sineSampler, sk=['x', 'z'], mo=0)
        
        # Hook up to driver's attributes
        driverGrp.amplitude >> sineSpinner.sx
        driverGrp.amplitude >> sineSpinner.sy
        driverGrp.amplitude >> sineSpinner.sz
        conversion.outputX >> sineSpinner.rz
        
        conversion.outputY >> freqScalarInput1[j]
        freqScalarInput2[j].set(i)
        freqScalarOutput[j] >> sineSpinner.jointOrientZ
        
        # Drive the main attribute
        sineSampler.ty >> attr
        
    # Clean-up and return root group
    hide(driverGrp)
    lockAndHideAttrs(driverGrp, ['t', 'r', 's', 'v'])
    
    return driverGrp


# MATH

def getLocalDir(obj, target):
    '''
    Return the normalized direction from obj to the target in obj space.
    '''
    temp = group(em=1, n="temp")
    loc = spaceLocator(n="tempLoc")
    parent(loc, temp)
    delete(parentConstraint(obj, temp))
    delete(pointConstraint(target, loc))
    dir = loc.translate.get().normal()
    delete(temp)
    return dir
    
def getLocalDirToPos(obj, worldPos):
    '''
    Return the normalized direction from obj to the target world position in obj space.
    '''
    temp = group(em=1, n="temp")
    delete(parentConstraint(obj, temp))
    loc = PyNode(spaceLocator(n="tempLoc"))
    loc.translate.set(worldPos)
    parent(loc, temp)
    dir = loc.translate.get().normal()
    delete(temp)
    return dir

def multiplyPoints(points, multiplyBy=1): 
    ''' 
    Return a series of points in between two points
    '''
    points = map(lambda p: dt.Point(p), points) 
    newPoints = [] 
    for i in xrange(len(points)): 
        point = points[i] 
        newPoints.append(point) 
        if i < len(points)-1: 
            nextPoint = points[i+1] 
            for spi in xrange(1, multiplyBy): 
                newPoint = spi*((nextPoint-point)/multiplyBy)+point 
                newPoints.append(newPoint) 
    return newPoints 

def getWorldPositionVector(obj, localPosition=None):
    '''
    Given a local position vector and an object, return the object's pivot plus
    the local position (in object space) in world space. If no local position vector
    is specified just return the world position.
    '''

    basePos = dt.Vector(cmds.pointPosition(str(obj)+'.rp', w=1))
    obj = str(obj)
	
    if localPosition == None: return basePos

    # Translate localPosition to an offset in world space
    '''
    tm = dt.TransformationMatrix(cmds.xform(obj, q=1, m=1, ws=1))
    pos1 = tm.getTranslation('world')
    tm.addTranslation(localPosition, 'preTransform')
    pos2 = tm.getTranslation('world')
    worldPosChange = pos2-pos1
    '''
    
    localPosition = dt.Vector(localPosition)
    
    # Use OpenMaya instead of the above code since it's
    # way faster than using PyMEL's matrix class
    matrixValues = cmds.xform(obj, q=1, m=1, ws=1)
    m = api.MMatrix()
    api.MScriptUtil.createMatrixFromList(matrixValues, m)
    tm = api.MTransformationMatrix(m)
    pos1 = tm.translation(api.MSpace.kWorld)
    tm.addTranslation(api.MVector(localPosition), api.MSpace.kPreTransform)
    pos2 = tm.translation(api.MSpace.kWorld)
    worldPosChange = pos2-pos1

    return basePos+(dt.Vector(worldPosChange))
    
def getWorldDirectionVector(trans, localDirection):
    '''
    Given a local direction vector and an object, return that
    direction vector in world space from object space.
    '''

    saveSelected = selected()
    select(cl=1)
    
    tempGrp = PyNode(group(em=1, n="tempTransTracker"))
    tempLoc = PyNode(spaceLocator(n="tempUpAim"))
    parent(tempLoc, tempGrp)
    tempLoc.translate.set(localDirection[0], localDirection[1], localDirection[2])
    pc = parentConstraint(trans, tempGrp, mo=0)
    delete(pc)
    dirVector = (tempLoc.getTranslation("world")-tempGrp.getTranslation("world")).normal()
    delete(tempGrp)
    
    select(saveSelected)
    
    return dirVector

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

def getChainLength(start, end):
    '''
    Returns the length of a transform chain in world units.
    '''

    try:
        chain = chainBetween(start, end)
    except Exception as exc:
        raise Exception('getChainLength: '+exc.args[0])

    worldPositions = map(lambda t: getWorldPositionVector(t), chain)
    
    totalLength = 0
    
    for i in xrange(len(chain)-1):
        firstPos = worldPositions[i]
        secondPos = worldPositions[i+1]
        dist = firstPos.distanceTo(secondPos)
        totalLength += dist
    
    return totalLength


# MINI-TRANSFORM RIGS

def horizontalCircleCoordTarget(n='circleCoord', radius=1):
    '''
    Provides a transform that represents the point along a circle lined up with a locator in world position.
    Only approximate, not exact.
    
    Return:
        circlePlane
    '''
    
    # Constants
    COORD_CIRCLE_RADIUS = 1000.0 # Work in bigger numbers to reduce floating point errors
    TANGENT_WEIGHT = COORD_CIRCLE_RADIUS*0.549675 # Fudge math
    FPS = 24.0
    
    # Set up circle target
    circleTarget = spaceLocator(n=n+'_coordLoc')
    transformLimits(circleTarget, tz=(-COORD_CIRCLE_RADIUS, COORD_CIRCLE_RADIUS), etz=(1, 1))

    # Map tranzlateZ to a corresponding coordinate on the semi-circle in translateX
    driver = circleTarget.tz
    driven = circleTarget.tx
    
    driver.set(-COORD_CIRCLE_RADIUS)
    driven.set(0)
    setDrivenKeyframe(  cd=driver,
                        at='tx',
                        itt='spline',
                        ott='spline'  )
                                    
    driver.set(0)
    driven.set(COORD_CIRCLE_RADIUS)
    setDrivenKeyframe(  cd=driver,
                        at='tx',
                        itt='spline',
                        ott='spline'  )
    
    driver.set(COORD_CIRCLE_RADIUS)
    driven.set(0)
    setDrivenKeyframe(  cd=driver,
                        at='tx',
                        itt='spline',
                        ott='spline'  )
    
    keyTangent(driven, wt=1) # Weighted Tangents
    keyTangent(driven, wl=0) # Unlock weights
    
    
    keyTangent(driven, e=1, index=[0], outAngle=90, outWeight=TANGENT_WEIGHT)
    keyTangent(driven, e=1, index=[1], inAngle=0, inWeight=FPS*TANGENT_WEIGHT)
    keyTangent(driven, e=1, index=[1], outAngle=0, outWeight=FPS*TANGENT_WEIGHT)
    keyTangent(driven, e=1, index=[2], inAngle=-90, inWeight=TANGENT_WEIGHT)

    # Set circle plane and its radius
    circlePlane = group(n=n+'_circlePlane', em=1)
    parent(circleTarget, circlePlane)
    
    circlePlane.addAttr('radiusScalar', keyable=0)
    radiusScalarAttr = circlePlane.attr('radiusScalar')
    radiusScalarAttr.set(1/COORD_CIRCLE_RADIUS)
    
    circlePlane.addAttr('radius', keyable=1, dv=1, min=0)
    radiusAttr = circlePlane.attr('radius')
    radiusAttr.showInChannelBox(1)
    
    md = createNode('multiplyDivide')
    radiusAttr >> md.input1X
    radiusScalarAttr >> md.input2X
    md.outputX >> circlePlane.sx
    md.outputX >> circlePlane.sy
    md.outputX >> circlePlane.sz
    
    radiusAttr.set(radius)
    
    # Lock and hide attrs
    for at in ['tx', 'ty', 'rx', 'ry', 'rz']:
        setAttr(circleTarget.attr(at), lock=1, keyable=0, channelBox=0)
        
    for at in ['sx', 'sy', 'sz']:
        setAttr(circlePlane.attr(at), lock=1, keyable=0, channelBox=0)
        
    select(cl=1)
    
    return circlePlane
    
def singleAxisAimer(n='singleAxisAimer'):
    '''
    Aims a transform at a locator along an axis plane using only the y-axis.
    
    Returns:
        [0]: Aimer Plane
        [1]: Aimer
        [2]: World aimer target
    '''
    aimerPlane = group(em=1, n=n+'_aimerPlane')
    aimer = spaceLocator(n=n+'_aimer')
    parent(aimer, aimerPlane)
    
    # A target for the aimer that only travels along the axis plane so the
    # aimer transform won't flip
    planeTarget = spaceLocator(n=n+'_planeTarget')
    parent(planeTarget, aimerPlane)
    hide(planeTarget)
    
    # A target in world space that can be moved around freely
    worldTarget = spaceLocator(n=n+'_worldTarget')
    
    # Hook up systems
    pointConstraint(worldTarget, planeTarget, sk=['y'], mo=0)
    aimConstraint(  planeTarget,
                    aimer,
                    mo=0,
                    sk=['x', 'z'],
                    aim=[0,0,1],
                    worldUpType='objectrotation',
                    worldUpObject=aimerPlane  )
    
    return [aimerPlane, aimer, worldTarget]



# JOINT CHAINS

def addSelectChain(namePattern, startNum, endNum, zeroPadding=0):
    '''
    Add to the selection list given a certain name pattern,
    with %s being replace by numbers  between startNum and
    endNum (inclusive).
    
    zeroPadding:
        Make sure up to this many zeros are padded.
    '''
    for i in xrange(startNum, endNum+1):
        select(namePattern%(str(i).zfill(zeroPadding)), add=1)

def createJointChainFromPoints(points, jointsPerPoint=1, templateOrient=None, namePattern="joint#"):
    ''' 
    Return joint chain that matches a series of points
    '''
    select(d=1) 
    points = multiplyPoints(points, jointsPerPoint) 
    joints = []
    startingNum = 1
    
    # Build the joint chain
    for i in xrange(len(points)): 
        point = points[i]
        j = joint(p=point, n=namePattern.replace("#", str(startingNum)))
        startingNum += 1
        joints.append(j)
        
    # Orient the joint chain
    joint(joints[0], e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)
        
    return joints

def createStretchyJointChain(start, end, NUM_STRETCHY_JNTS = 5):
    '''
    Create a joint chain used for stretchy meta-rig components.
    '''

    startJnt = PyNode(start)
    endJnt = PyNode(end)
    chain = []

    if (endJnt.getParent() != startJnt):
        raise "Start joint is not the parent of the end joint"
    
    # Naming setup
    try:
        baseName = startJnt.split('_bind_joint')[0]
    except:
        baseName = "stretchy"
    namePattern = baseName+"_stretch_#_bind_joint"
    
    # Joint creation setup
    translateIncrement = (1/float(NUM_STRETCHY_JNTS))*endJnt.getTranslation("object")
    
    # Create the base joint
    select(d=1)
    rootStretchyJnt = joint(p=(0,0,0), n=namePattern.replace("#", "1"))
    parent(rootStretchyJnt, startJnt)
    rootStretchyJnt.rotate.set(0,0,0)
    rootStretchyJnt.jointOrient.set(0,0,0)
    rootStretchyJnt.translate.set(0,0,0)
    
    chain.append(rootStretchyJnt)
    
    # Create the other joints
    lastJnt = rootStretchyJnt
    for i in xrange(NUM_STRETCHY_JNTS):
        if (i < NUM_STRETCHY_JNTS-1):
            jntName = namePattern.replace("#", str(i+2))
        else:
            jntName = baseName+"_stretch_end_joint"
        newJnt = joint(p=(0,0,0), n=jntName)
        parent(newJnt, lastJnt)
        lastJnt = newJnt
        newJnt.rotate.set(0,0,0)
        newJnt.jointOrient.set(0,0,0)
        newJnt.translate.set(translateIncrement)

        chain.append(newJnt)
    
    return chain

# LOCATOR SYSTEMS

'''
def vertexLocator(vert, n="vertexLocator"):
    if (not isinstance(vert, MeshVertex)):
        return None
    loc = spaceLocator(n=n)
    select(vert, loc)
    mel.eval('doCreatePointOnPolyConstraintArgList 1 { "0","0","0","1","","1" };');
'''

def locatorsOnCurve(c, numLocs=5, method="pointOnCurveInfo"):
    '''
    Creates a series of locators evenly distributed along a curve.
    The pointOnCurve doesn't behave like the uValue on motion paths, however.
    Recommendation is to run this on a rebuilt curve with even CV distribution
    without deleting its history.  Then use the original curve to drive the
    rebuilt curve.

    numLocs:
        Number of locators to add to the curve.
    
    method:
        Method of locator distribution along the curve.
        "pointOnCurveInfo" or "motionPath" (motionPath is more accurate).
        Default is pointOnCurveInfo.
    '''

    locs = []
    locGrp = group(em=1, n=getModdedName(c, '%s_loc_grp'))
    for i in xrange(numLocs):
        
        # Create the locator
        loc = spaceLocator(n=getModdedName(c, '%s_loc_'+str(i)))
        loc.inheritsTransform.set(0)
        parent(loc, locGrp)
        locs.append(loc)
        
        parameterValue = float(i)/float(numLocs-1)
        
        if method == "motionPath":
            # Create the motionPath
            mp = PyNode(pathAnimation(loc, c=c, fractionMode=1, follow=1))
            
            # Remove initial keys on the u value and set the correct value
            cutKey(mp.uValue, cl=1)
            mp.uValue.set(parameterValue)
            
        else:
            # Create the pointOnCurve node that feeds the locator information
            cop = PyNode(pointOnCurve(c, ch=1))
            cop.rename(loc.shortName()+"_pocInfo")
            cop.turnOnPercentage.set(1)
            cop.parameter.set(parameterValue)
            
            # Connect the COP node to the locator
            cop.position >> loc.translate
        
    return locs

def stretchyLocatorTransforms(startTrans, endTrans, locTransforms, anchorTransformsToLocators=False):
    '''
    Creates a stretchy system of locators.  The locators are positioned based on the
    provided transforms, and the stretchy handles are anchored to a start and end joint.
    If the anchor options is set to true this stretchy system will drive the original
    reference transforms.
    
    startTrans:
        The starting anchor of this stretchy system.
    
    endTrans:
        The end anchor of this stretchy system.
        
    locTransforms:
        Reference transforms for locator positioning.
        
    anchorTransformsToLocators:
        If true, constrain the locator transform sources to the created locators.
    '''
    
    startTrans = PyNode(startTrans)
    endTrans = PyNode(endTrans)
        
    # Create locator start handle
    startLoc = spaceLocator(n=getModdedName(startTrans, '%s_startHandle_loc'))
    pointConstraint(startTrans, startLoc, mo=0)
    
    # Create locator end handle
    endLoc = spaceLocator(n=getModdedName(endTrans, '%s_endHandle_loc'))
    pointConstraint(endTrans, endLoc, mo=0)
    delete(orientConstraint(startLoc, endLoc, mo=0))
    
    # Aim start locator at end locator
    aimDir = getLocalDir(startTrans, endTrans)
    aimConstraint(endLoc, startLoc, mo=0, aim=aimDir, wut="objectrotation", wuo=startTrans)
    
    # Create distance measurer and store initial distance between start and end joints
    measurer = distanceDimension(startLoc, endLoc)
    ratio = createNode("multiplyDivide")
    ratio.operation.set(2)
    measurer.distance >> ratio.input1X
    ratio.input2X.set(measurer.distance.get()) # Store original distance
    
    # Create group that will be scaled via the ratio
    scaleGrp = group(em=1, n="scaleLocsGrp")
    delete(pointConstraint(startLoc, scaleGrp, mo=0))
    delete(aimConstraint(endLoc, scaleGrp, mo=0, aim=(1,0,0)))
    parentConstraint(startLoc, scaleGrp, mo=1)
    ratio.outputX >> scaleGrp.scaleX
    
    # Create locators and parent to the scale group
    locs = []
    for locTrans in locTransforms:
        loc = spaceLocator(n=getModdedName(locTrans, '%s_loc'))
        locs.append(locs)
        parent(loc, scaleGrp)
        delete(parentConstraint(locTrans, loc, mo=0))
        if (anchorTransformsToLocators): parentConstraint(loc, locTrans, mo=0)
    
    # Stuff everything into one group
    root = group([scaleGrp, measurer, startLoc, endLoc], n="stretchyLocatorTransforms")
    root.inheritsTransform.set(0)
    hide(measurer)
    
    return [root, startLoc, endLoc, locs]
    
    
def stretchyLocatorCurve(startTrans, endTrans, numCtrls=3, numLocs=5, anchor=False, clusterStartLocations=[], method="pointOnCurveInfo"):
    '''
    Creates linear chain of locators between two transforms.
    
    startTrans:
        The starting anchor of this chain.
    
    endTrans:
        The end anchor of this chain.
        
    numCtrls:
        Number of control clusters for this chain.
        
    numLocs:
        Number of locators marking the chain.
        
    anchor:
        If true, constrain the start and end control clusters to the source transforms.
        
    clusterStartLocations:
        Use the provided transforms to move the clusters (in order) to a start location.
        
    method:
        Method of locator distribution along the stretchy curve.
        "pointOnCurveInfo" or "motionPath" (motionPath is more accurate).
        Default is pointOnCurveInfo.
    '''
    
    startTrans = PyNode(startTrans)
    endTrans = PyNode(endTrans)

    controlPoints = multiplyPoints([startTrans.getTranslation("world"), endTrans.getTranslation("world")], numCtrls+1)
    
    # Build main control curve and clusters to drive each point
    ctrlCurve = curve(degree=1, p=controlPoints)
    clusters = []
    for i in xrange(len(controlPoints)):
        clstr = cluster(ctrlCurve.cv[i])[1]
        clusters.append(clstr)
        if i == 0:
            clstr.rename("startCluster")
            if anchor: clstr.visibility.set(0)
        elif i == len(controlPoints)-1:
            clstr.rename("endCluster")
            if anchor: clstr.visibility.set(0)
        else:
            clstr.rename("ctrlCluster_"+str(i))
    
    # Build the curve containing locators that the joint chain can attach to.
    locCurve = rebuildCurve(ctrlCurve, ch=1, rpo=0, rt=0, end=1, kr=1, kcp=0, kt=0, s=numLocs, degree=3, tol=0.01)[0]
    locators = locatorsOnCurve(locCurve, numLocs, method)
    locChainParent = locators[0].getParent()
    locChainParent.rename("locatorChain")
     
    # Try to snap the clusters to start locations
    for i in xrange(len(clusters)):
        if i < len(clusterStartLocations):
            startLocation = clusterStartLocations[i]
            clstr = clusters[i]
            delete(parentConstraint(startLocation, clstr, mo=0))
     
    # Constrain clusters to start and end
    if anchor:
        pointConstraint(startTrans, clusters[0], mo=0)
        pointConstraint(endTrans, clusters[-1], mo=0)
    
    # Clean-up
    clustersGrp = group(clusters, n="controlClusters")
    curveGrp = group([ctrlCurve, locCurve], n="controlCurve")
    curveGrp.inheritsTransform.set(0)
    curveGrp.visibility.set(0)
    root = group([clustersGrp, curveGrp, locChainParent], n="stretchyLocatorChain")
    
    # Return the root node, list of control clusters (in order), and locators (in order)
    return [root, clusters, locators]

    
# AUTO-RIG HELPERS

class FlexibleEyelidJointCreator():
    '''
    A helper to create the numerous joints required for the 
    FlexibleEyelid meta component.  Start up this window, select
    a series of vertices on the eyelid mesh, specify eye size locators,
    then click the joint creation button.
    '''

    LABEL_WIDTH = 85
    VALUE_WIDTH = 215

    def __init__(self):
    
        # Toggle the selection setting needed for vertex selection
        selectPref(trackSelectionOrder=True)

        # Window
        wName = 'Flexible Eyelid Joints'
        if (window('FEJCreator', exists=1)): deleteUI('FEJCreator')
        w = window('FEJCreator', t=wName, s=0, rtf=1)
        
        menuLayout = verticalLayout()

        # Instructions
        text(ww=1, al='left', l="Specify the settings below then select eye lid vertices one-by-one starting from the inner part of the eye and moving on to the outer. "+\
                                 "It is important that vertices be selected after this window is already open, since it automatically enables a Maya preference "+\
                                 "that tracks selection order.")

        # Select side
        setParent(menuLayout)
        rowLayout(nc=2, cw2=[self.LABEL_WIDTH, self.VALUE_WIDTH])
        text('Side')
        self.select_side = optionMenu()
        self.select_side.addItems(['Left', 'Right', 'Center'])
        
        # Select lid
        setParent(menuLayout)
        rowLayout(nc=2, cw2=[self.LABEL_WIDTH, self.VALUE_WIDTH])
        text('Lid')
        self.select_lid = optionMenu()
        self.select_lid.addItems(['Upper', 'Lower'])
        
        # Eye forward locator
        setParent(menuLayout)
        rowLayout(nc=3, cw3=[self.LABEL_WIDTH, self.VALUE_WIDTH/3, 2*self.VALUE_WIDTH/3])
        text('Eye Forward')
        self.select_forward = button('Set Object')
        self.select_forward_text = text(l='Specify a locator.')
        self.select_forward.setCommand(Callback(lambda: self.select_forward_text.setLabel(selected()[0])))
        
        # Eye up locator
        setParent(menuLayout)
        rowLayout(nc=3, cw3=[self.LABEL_WIDTH, self.VALUE_WIDTH/3, 2*self.VALUE_WIDTH/3])
        text('Eye Up')
        self.select_up = button('Set Object')
        self.select_up_text = text(l='Specify a locator.')
        self.select_up.setCommand(Callback(lambda: self.select_up_text.setLabel(selected()[0])))
        
        # Eye width marker
        setParent(menuLayout)
        rowLayout(nc=3, cw3=[self.LABEL_WIDTH, self.VALUE_WIDTH/3, 2*self.VALUE_WIDTH/3])
        text('Width Marker')
        self.select_width = button('Set Object')
        self.select_width_text = text(l='Specify a locator.')
        self.select_width.setCommand(Callback(lambda: self.select_width_text.setLabel(selected()[0])))
        
        # Create joints button
        setParent(menuLayout)
        makeJointsButton = button(l='Create Joints on Vertices')
        makeJointsButton.setCommand(Callback(self.createJointsCallback))
        
        # Redistribute menu
        menuLayout.redistribute(2,1,1,1,1,1,1)
        
        # We're ready to roll
        showWindow(w)

        
    def createJointsCallback(guiClass):
        side = guiClass.select_side.getValue().lower()
        lid = guiClass.select_lid.getValue().lower()
        eyeForward = guiClass.select_forward_text.getLabel()
        eyeUp = guiClass.select_up_text.getLabel()
        eyeWidthMarker = guiClass.select_width_text.getLabel()
        guiClass.getEyeJoints(ls(os=1, fl=1), PyNode(eyeForward), PyNode(eyeUp), PyNode(eyeWidthMarker), side, lid)


    def getEyeJoints(self, verts, eyeForward, eyeUp, eyeWidthMarker, side='left', lid='upper'):
        
        compName = side+'_'+lid
        
        scaleSpace = getScaleSpace(eyeForward, eyeUp, eyeWidthMarker, name=compName+'_scaleGrp')
        
        # Set aim function based on side
        if side == 'left':
            if lid == 'upper':
                doAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(1,0,0), u=(0,-1,0), wut='object', wuo=eyeUp)
            else:
                doAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(-1,0,0), u=(0,1,0), wut='object', wuo=eyeUp)
        elif side == 'right' or side == 'center':
            if lid == 'upper':
                doAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(-1,0,0), u=(0,1,0), wut='object', wuo=eyeUp)
            else:
                doAim = lambda s, t: aimConstraint(s, t, mo=0, aim=(1,0,0), u=(0,-1,0), wut='object', wuo=eyeUp)

        # Constrain the bind joints to their respective locators along the non-uniform space.
        i = 0
        newJoints = []
        for v in verts:
            
            # Setup joint
            select(cl=1)
            worldPos = xform(v, q=1, ws=1, t=1)
            j = joint(p=worldPos)
            j.rename(side+'_'+lid+'_eyelid_'+str(i+1)+'_bind_joint')
            newJoints.append(j)
            
            # Aimer within the scaled eye space that will point to where a joint should be
            jAimer = group(em=1, n=compName+'_'+j.shortName()+'_aimerGrp')
            delete(parentConstraint(scaleSpace, jAimer, mo=0))
            parent(jAimer, scaleSpace)
            jAimer.scale.set(1,1,1)
            delete(doAim(eyeForward, jAimer))
            
            # Locator at the "edge" of the non-uniform eye.  It will slide along the non-uniform
            # surface of the eye, directing where its corresponding joint should go.
            jExtentsMarker = spaceLocator(n=compName+'_'+j.shortName()+'_extents')
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
            pointConstraint(jExtentsMarker, j, mo=0)
            aimConstraint(jExtentsUp, j, mo=0, aim=(0,1,0), u=(0,0,1), wut='object', wuo=jExtentsSide)
            
            # Create locator for the joint aimer transform to aim at
            jAimerTarget = spaceLocator(n=compName+'_'+j.shortName()+'_target')
            delete(pointConstraint(j, jAimerTarget, mo=0))
            doAim(jAimerTarget, jAimer)
            
            # Upkeep and delete junk
            refresh() # Update constraints
            delete(jAimerTarget)
            i += 1

        # Delete aimer system
        delete(scaleSpace)
        
        # Freeze rotation
        makeIdentity(newJoints, r=1, s=0, t=0, jo=0, a=1)

def addAnimVisSet(anim, visAttrName, objList):
    '''
    Create an attribute on the indicated top con that toggles the
    visibility of a list of anims.  Returns the new attribute.
    '''

    anim.addAttr(visAttrName, keyable=0, dv=1, min=0, max=1)
    visAttr = anim.attr(visAttrName)
    visAttr.showInChannelBox(1)
    
    '''
    for obj in objList:
        grp = group(em=1, n=obj+'_viz_grp')
        pc = parentConstraint(obj, grp, mo=0)
        delete(pc)
        parent(grp, PyNode(obj).getParent())
        makeIdentity(grp, apply=1, translate=1, rotate=1, scale=1)
        parent(obj, grp)
        visAttr >> grp.visibility
    '''
    
    for obj in objList:
        # Create intermediate group
        grp = group(em=1, n=obj+'_viz_grp')
        objParent = obj.getParent()
        delete(parentConstraint(objParent, grp, mo=0))
        delete(scaleConstraint(objParent, grp, mo=0))
        parent(grp, objParent)
        makeIdentity(grp, apply=1, translate=1, rotate=1, scale=0)
        parent(obj, grp)
        
        # Connect visibility
        visAttr >> grp.visibility
        
        # Lock all attributes
        lockAndHideAttrs(grp, ['v', 't', 'r', 's'])
        
        
    return visAttr

def addAttrToAnim(anim, attrName, driven=None, defaultValue=0, minValue=0, maxValue=1):
    '''
    Creates an attribute on an anim that directly drives another attribute.
    '''
    
    anim = PyNode(anim)
    if anim.hasAttr(attrName):
        print 'addAnimAttr ERROR: Attribute '+str(attrName)+' already exists on '+str(anim)+'.  Skipping.'
        return None
    
    # Create attribute
    anim.addAttr(attrName, keyable=1, dv=defaultValue, min=minValue, max=maxValue)
    animAttr = anim.attr(attrName)
    
    # Drive driven attribute
    
    if driven != None:
        try:
            driven = PyNode(driven)
            animAttr >> driven
        except:
            print 'addAnimAttr WARNING: '+str(driven)+' is not a valid attribute to drive.  Still creating '+str(anim)+'.'+str(attrName)
        
    return animAttr
    
def recolorCurves(transformList, ci):
    '''
    curveList:
        Transforms to check for curves to recolor.
        
    ci:
        Index of the curve color to use.
    '''
    for t in transformList:    
        for s in t.getShapes():
            if isinstance(s, nt.NurbsCurve):
                s.overrideEnabled.set(1)
                s.overrideColor.set(ci)
        t.overrideColor.set(ci)
                
def finalizeRig(char, animPath=None, animPathType='folder', importNewAnims=True):
    '''
    Standard clean-up and finalization method that should be called at the end of the rigging template. Does the following:
    1) Import anim shapes
    2) Apply anim shaders
    3) Recolor anim curves
    4) Make anim shapes non-renderable
    5) Hide skeleton and make component joints non-renderable
    
    char:
        Character meta root node.
        
    animPath:
        Directory path containing this preAutorig file.
        
    animPathType:
        If 'folder' then the animPath specified should be a folder containing a bunch of anims.
        If 'file' then the animPath specified should be a single file with all of the new anim shapes.
    
    importNewAnims:
        True if new anims should be imported
    '''
    
    # Make sure all rig components and their nodes have evaluated
    refresh()
    
    # Import any custom anim shapes
    if animPath != None and importNewAnims:
        if animPathType == 'folder':
            char.importAnims(animPath+"\\anim_shapes")
        elif animPathType == 'file':
            char.importAnimsFromFile(animPath)

    # Apply anim shaders
    char.createShader('right', color = (1,.467,0), apply=1)
    char.createShader('center', color = (.1,.1,.55), apply=1)
    char.createShader('left', color = (.506,.927,1), apply=1)
    
    # Set curve colors
    recolorCurves(char.getAllAnims("right"), 21)
    recolorCurves(char.getAllAnims("center"), 6)
    recolorCurves(char.getAllAnims("left"), 18)
    recolorCurves(filter(lambda a: a.endswith("_switch"), char.getAllAnims()), 1)
    
    # Makes all anim meshses and surfaces non-renderable
    for anim in char.getAllAnims():
        for s in anim.getShapes():
            try:
                s.castsShadows.set(0)
                s.receiveShadows.set(0)
                s.motionBlur.set(0)
                s.primaryVisibility.set(0)
                s.smoothShading.set(0)
                s.visibleInReflections.set(0)
                s.visibleInRefractions.set(0)
            except:
                continue # Not a renderable shape
    
    # Turn off drawing of joint in the component grp
    componentGrps = ls("component_grp", r=1)
    select(componentGrps, hi=1)
    componentJnts = ls(sl=1, type="joint")
    for j in componentJnts: j.drawStyle.set(2)

    # Turn off drawing of top con joint
    for tcj in ls("*_topCon", r=1, type="joint"): tcj.drawStyle.set(2)
    
    # Hide bind joints
    hide(ls("bind_joint_grp", r=1))