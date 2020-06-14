from pymel.core import *

def makeSureAttrExistsOnTarget(srcAttr, targetAttr, targetObj):
    
    # If new input attribute doesn't exist, create one identical to the
    # other input attribute
    if not objExists(targetAttr): 
        addAttr(
            targetObj,
            at = addAttr(srcAttr, q=1, at=1),
            dv = addAttr(srcAttr, q=1, dv=1),
            ln = addAttr(srcAttr, q=1, ln=1),
            nn = addAttr(srcAttr, q=1, nn=1),
            r = addAttr(srcAttr, q=1, r=1),
            sn = addAttr(srcAttr, q=1, sn=1),
            h = addAttr(srcAttr, q=1, h=1),
            k = addAttr(srcAttr, q=1, k=1),
            s = addAttr(srcAttr, q=1, s=1),
            w = addAttr(srcAttr, q=1, w=1)
        )
        
        attr = PyNode(targetAttr)
        
        # Other attributes to add
        min = addAttr(srcAttr, q=1, min=1)
        max = addAttr(srcAttr, q=1, max=1)
        
        if min != None: addAttr(attr, e=1, min=min)
        if max != None: addAttr(attr, e=1, max=max)

def getExternalConstraintChildren(obj):
    '''
    Get a list of constraints parented to the given object
    that, if said object is referenced, are not part of the
    same reference node.
    '''
    
    obj = str(obj)

    constraints = cmds.listRelatives(obj, c=1, pa=1, type="constraint")
    if constraints == None: return None
    
    # If this object is referenced remember the reference node name.
    # If not, there's nothing to worry about so return all the constraints.
    if cmds.referenceQuery(obj, inr=1):
        objRefNodeName = cmds.referenceQuery(obj, rfn=1)
    else:
        return constraints
    
    # Check for constraints not associated with this reference node
    filteredConstraints = []
    for c in constraints:
        if cmds.referenceQuery(c, inr=1):
            constraintRefNodeName = cmds.referenceQuery(c, rfn=1)
            if (objRefNodeName == constraintRefNodeName): continue
        filteredConstraints.append(c)
        
    if len(filteredConstraints) < 1: return None
    return filteredConstraints
        
def redirectAdvancedAnimationConnections(obj, newObj=None):
    '''
    Redirect all constraint connections from a source object to a target object.
    
    If no target object is specified, create a suitable placeholder. Return the
    information necessary to reverse the process.
    '''
    
    try:
        obj = PyNode(obj)
        objName = obj.shortName()
    except:
        return None
    inputConns = listFullInputs(objName, ["animCurve", "constraint", "motionPath", "addDoubleLinear", "pairBlend"])
    outputConns = listFullOutputs(objName, ["animCurve", "constraint", "motionPath", "addDoubleLinear",  "pairBlend"])

    if len(inputConns) < 1 and len(outputConns) < 1:
        # No connections to swap here. End immediately.
        return None

    # Create placeholder
    if newObj == None:
        newObjName = str(duplicate(objName, po=1, rr=1, n=objName+"_redirectedConnections")[0])
        
        newObjParentName = cmds.listRelatives(newObjName, p=1)
        if (newObjParentName != None): newObjName = str(parent(newObjName, w=1, r=1)[0])
    else:
        newObjName = PyNode(newObj).shortName()
    
    '''
    if (cmds.nodeType(newObjName) != cmds.nodeType(objName)):
        raise Exception("ERROR. Cannot redirect animation connections. Source and target objects not the same type: "+objName+", "+newObjName)
    '''
    
    # Redirect connections
    for ic in inputConns:
        newInputAttr = ic[1].replace(objName, newObjName)
        makeSureAttrExistsOnTarget(ic[1], newInputAttr, newObjName) 
        connectAttr(ic[0], newInputAttr, f=1)
        
    for ic in inputConns:
        disconnectAttr(ic[0], ic[1])
    
    for oc in outputConns:
        newOutputAttr = oc[0].replace(objName, newObjName)
        makeSureAttrExistsOnTarget(oc[0], newOutputAttr, newObjName)
        connectAttr(newOutputAttr, oc[1], f=1)
    
    # Reparent any constraints
    constraints = getExternalConstraintChildren(objName)
    if constraints != None:
        cmds.parent(constraints, newObjName)
    
    return (newObjName, objName)

def listFullOutputs(obj, type="", skRefConn=True):
    '''
    Return tuples of src and destination connections,
    all outputs of the specified object.  If skRefConn
    is true, ignore connections to other objects that are
    part of the same FileReference node.
    
    Format: (<source plug>, [<destination plug>,...])
    
    All string output.
    '''
    
    objName = str(obj)
    
    plugConnections = []
    if isinstance(type, str): type = [type]
    for t in type:
        newPlugConnections = cmds.listConnections(objName, type=t, c=1, s=0, d=1, plugs=1, scn=1)
        if newPlugConnections != None: plugConnections += newPlugConnections
    
    if skRefConn and cmds.referenceQuery(objName, inr=1):
        try:
            # Try to get the associated reference node and bypass
            # any edge cases.  For example, querying a reference node
            # of a referenced reference node.
            refNodeName = cmds.referenceQuery(objName, rfn=1)
        except:
            refNodeName = None
    else:
        refNodeName = None
    outputs = []

    for i in xrange(len(plugConnections)/2):
        output = plugConnections[2*i]
        input = plugConnections[2*i+1]
        
        if  refNodeName != None and \
            cmds.referenceQuery(input, inr=1) and \
            cmds.referenceQuery(input, rfn=1) == refNodeName:
            continue
        
        outputs.append( (output, input) )
    
    return outputs

def listFullInputs(obj, type="", skRefConn=True):
    '''
    Return tuples of src and destination connections,
    all inputs into the specified object.  If skRefConn
    is true, ignore connections to other objects that are
    part of the same FileReference node.
    
    Format: (<source plug>, [<destination plug>])
    
    All string output.
    '''
    
    objName = str(obj)
    
    plugConnections = []
    if isinstance(type, str): type = [type]
    for t in type:
        newPlugConnections = cmds.listConnections(objName, type=t, c=1, s=1, d=0, plugs=1, scn=1)
        if newPlugConnections != None: plugConnections += newPlugConnections
    
    if skRefConn and cmds.referenceQuery(objName, inr=1):
        try:
            # Try to get the associated reference node and bypass
            # any edge cases.  For example, querying a reference node
            # of a referenced reference node.
            refNodeName = cmds.referenceQuery(objName, rfn=1)
        except:
            refNodeName = None
    else:
        refNodeName = None
    inputs = []
    
    for i in xrange(len(plugConnections)/2):
        output = plugConnections[2*i+1]
        input = plugConnections[2*i]
        
        if  refNodeName != None and \
            cmds.referenceQuery(output, inr=1) and \
            cmds.referenceQuery(output, rfn=1) == refNodeName:
            continue
        
        inputs.append( (output, input) )
    
    return inputs

def getRenderLayerConnections(refFile):
    '''
    Return render layer connections of a reference file.
    
    Same formatting as listFullInputs and listFullOutputs.
    '''
    toReturn = []
    
    for nodeName in cmds.referenceQuery(refFile, nodes=1):
        try:
            if u'dagNode' in nodeType(nodeName, i=1):
                toReturn += listFullInputs(nodeName, type="renderLayer")
        except:
            continue
    
    return toReturn

def getAllParentsOfReferencedNodes(refFile):
    '''
    Return parents of referenced nodes that live in the scene and are not
    referenced themselves.
    
    Format: (<child>, <parent>)
    
    All string output.
    '''
    toReturn = []
    
    refNodeName = FileReference(refFile).refNode.name()
    for nodeName in cmds.referenceQuery(refNodeName, nodes=1):
        try:
            if not u'transform' in nodeType(nodeName, i=1):
                continue
                
            parentName = cmds.listRelatives(nodeName, p=1)
            if (parentName == None):
                continue
            else:
                parentName = parentName[0]
                
            if not cmds.referenceQuery(parentName, inr=1):
                toReturn.append( (nodeName, parentName) )
            
        except:
            continue
            
    return toReturn
    
def getAllLightLinks(refFile):
    '''
    Returns a list of all light links on objects in the reference node.
    
    Format: (<obj>, [<light>,...])
    
    All string output.
    '''
    toReturn = []
    
    for nodeName in cmds.referenceQuery(refFile, nodes=1):
        try:
            lights = cmds.lightlink(q=1, object=nodeName)
            if len(lights) > 0:
                toReturn.append( (nodeName, filter(lambda l: u'light' in cmds.nodeType(l, i=1), lights)) )
        except:
            continue
            
    return toReturn

def getRedirectedAnimationConnections(refFile):
    '''
    Redirects and returns any advanced animation connections.
    
    Format: (<redirected obj>, <original obj>)
    
    All string output.
    '''
    toReturn = []
    
    for nodeName in cmds.referenceQuery(refFile, nodes=1):
        connectionPair = redirectAdvancedAnimationConnections(nodeName)
        if connectionPair != None:
            toReturn.append(connectionPair)
    
    return toReturn

lastRefInfo = None
    
def trueRefCleanup(refFile): 

    ## Reference information to remember
    print "Remembering old parents."
    oldParents = getAllParentsOfReferencedNodes(refFile)
    
    print "Remembering attributes with no keyframes."
    nonKeyedAttrValues = []
    for anim in ls(refFile.namespace+':*.animNode', r=1, o=1):
        for attr in anim.listAttr(keyable=1, u=1):
            if keyframe(attr, kc=1, q=1) > 0: continue
            nonKeyedAttrValues.append( (str(attr), attr.get()) )
    
    print "Remembering animation connections."
    oldAnimConns = getRedirectedAnimationConnections(refFile)
    
    print "Remembering light links."
    oldLightLinks = getAllLightLinks(refFile)
    
    print "Remember render layer connections."
    oldRenderLayerConns = getRenderLayerConnections(refFile)
    refresh()
    
    ## Unreference and cleanup
    refFile.unload()
    refFile.clean()
    refFile.load()
    refresh()
    global lastRefInfo
    lastRefInfo = [oldParents, nonKeyedAttrValues, oldAnimConns, oldLightLinks, oldRenderLayerConns]
    
    # Load saved information
    print "Restoring old parents." 
    for cp in oldParents:
        child = cp[0]
        parentTo = cp[1]
        parent(child, parentTo, r=1)
    refresh()
    
    print "Restoring anim curve connections."
    for pair in oldAnimConns:
        redirectAdvancedAnimationConnections(pair[0], pair[1])
        delete(pair[0])
    refresh()
    
    print "Restoring attributes with no keyframes."
    for nkv in nonKeyedAttrValues:
        attr = PyNode(nkv[0])
        value = nkv[1]
        if attr.isSettable(): attr.set(value)
    refresh()
    
    print "Restoring light links."
    for ll in oldLightLinks:
        obj = PyNode(ll[0])
        # Break existing connections (probably the defaults on reloading the reference)
        lightlink(b=1, object=obj, light=lightlink(q=1, object=obj))
        # Restore old connections
        lights = map(lambda l: PyNode(l), ll[1])
        lightlink(object=obj, light=lights)
    
    print "Restoring render layer connections."
    for sd in oldRenderLayerConns:
        src = PyNode(sd[0])
        dest = PyNode(sd[1])
        src >> dest
        
    print "FINISHED!"

refFilesToClean = set()

for s in selected():
    refFile = s.referenceFile()
    if refFile != None: refFilesToClean.add(refFile)

for refFile in refFilesToClean:
    trueRefCleanup(refFile)