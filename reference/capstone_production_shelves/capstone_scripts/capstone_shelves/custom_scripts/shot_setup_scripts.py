# Scripts that help the 2015 - 2016 Production create the layers needed for the water color look.
from pymel.core import *
import maya.cmds as cmds
import os
import fnmatch


def createUI( pWindowTitle, createRenderLayers, applyLightingMat, applyZDepthMat, createTestRenders, applyBeautyShaders ):
    
    windowID = 'watercolorSetupID'
    
    if cmds.window( windowID, exists=True ):
        cmds.deleteUI( windowID )
    
    cmds.window( windowID, title=pWindowTitle, sizeable=False, resizeToFitChildren=True )
    
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1,200), (2,10), (3,570) ], columnOffset=[ (3, 'left', 3) ] ) 
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    
    cmds.button( label='Create Render Layers', command=createRenderLayers)
    cmds.separator( h=10, style='none')
    cmds.text( label='Creates the render layers and places all meshes into these layers. NOTE: MUST have the masterLayer selected.')
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    '''
    cmds.button( label='Merge Indentical Layers', command=mergeRenderLayers)
    cmds.separator( h=10, style='none')
    cmds.text( label='Takes all references and re-references them so that they all share the same render layers' )
    '''
    
    cmds.button( label='Apply lighting_test_mat Material', command=applyLightingMat)
    cmds.separator( h=10, style='none')
    cmds.text( label='Applies the lighting_test_mat material. NOTE: You MUST have the lighting_test render layer selected.' )
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')

    cmds.button( label='Apply zdepth_mat Material', command=applyZDepthMat)
    cmds.separator( h=10, style='none')
    cmds.text( label='Applies the lighting_test_mat material. NOTE: You MUST have the z-depth render layer selected.' )
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    
    cmds.button( label='Apply beauty materials', command=applyBeautyShaders)
    cmds.separator( h=10, style='none')
    cmds.text( label='Will apply all beauty shaders. NOTE: You MUST have the beauty_layer selected.' )
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    

    cmds.button( label='Create Test Renders', command=createTestRenders)
    cmds.separator( h=10, style='none')
    cmds.text( label='Will create a test directory, in which single test renders will be made.' )
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    '''
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    '''

    cmds.showWindow()

# creates the 4 needed render layers
def createRenderLayers( *pArgs ):
    #get all render layers
    render_layer_list = cmds.ls(type="renderLayer")
    
    #check if the layer exists. If so, delete and remake
    lighting_test = 'lighting_test_layer'
    if lighting_test in render_layer_list:
        print 'lighting_test layer already exists. Deleting and remaking the layer.'
        cmds.delete( lighting_test )

    #create lighting_test_layer
    cmds.select(cmds.ls(type="mesh"))
    createRenderLayer(n=lighting_test)

    #check if the layer exists. If so, delete and remake
    beauty = 'beauty_layer'
    if beauty in render_layer_list:
        print 'beauty_layer layer already exists. Deleting and remaking the layer.'
        cmds.delete( beauty )

	#create beauty_layer
    cmds.select(cmds.ls(type="mesh"))
    createRenderLayer(n=beauty)

    #check if the layer exists. If so, delete and remake
    color_matte = 'color_matte_layer'
    if color_matte in render_layer_list:
        print 'color_matte_layer layer already exists. Deleting and remaking the layer.'
        cmds.delete( color_matte )

    #create color_matte_layer
    cmds.select(cmds.ls(type="mesh"))
    createRenderLayer(n=color_matte)
    
    #check if the layer exists. If so, delete and remake
    zdepth = 'zdepth_layer'
    if zdepth in render_layer_list:
        print 'zdepth_layer layer already exists. Deleting and remaking the layer.'
        cmds.delete( zdepth )

    #create zdepth_layer
    cmds.select(cmds.ls(type="mesh"))
    createRenderLayer(n=zdepth)

# creates test renders to see how the different render layers are
# working. Will look for the render_cam object to render from
def createTestRenders( *pArgs ):
    # get the file location
    file_loc =  cmds.file(q=True, sn=True)
    
    # get the file name
    file_name = cmds.file(q=True, sn=True, shn=True)
    
    # remove te file name from the file path to get the directory
    file_dir = file_loc.replace(file_name, "")
    
    # create the directory
    test_render_dir = file_dir + 'test_renders'
    cmds.sysFile( test_render_dir, makeDir=True )# Windows
    
    # get the current workspace
    curr_workspace = cmds.workspace(q=True, fullName=True)
    
    # set the current project to this folder
    cmds.workspace( dir=test_render_dir )
    
    # set render image format to png
    cmds.setAttr('defaultRenderGlobals.imageFormat', 3)

    # get all render layers
    render_layers_list = cmds.ls(type="renderLayer")

    # render out test images
    for rl in render_layers_list:
        if(rl != 'defaultRenderLayer'):
            # select the render cam
            cmds.Mayatomr( preview=True, camera='render_camShape', layer=rl, xResolution=1280, yResolution=720)
    
    # set the render project back to original directory
    test_workspace = cmds.workspace( dir=curr_workspace )

# applies the lighting_mat material to all objects in the lighting_test_layer
# MUST have the lighting_test_layer selected for this script to work!!
def applyLightingMat( *pArgs ):
	light_shader = ls('lighting_test_mat')

	if not light_shader:
		print 'importing lighting mat...'
		# import the shading network
		cmds.file( 'O:/unix/projects/instr/capstone4/production/interior_watercolor_pipeline/lighting_test.mb', i=True)
	else:
		print 'lighting mat is already in the set.'
		
	print 'applying lighting test mat...'
	render_objects = cmds.editRenderLayerMembers( 'lighting_test_layer', q=True)
	print render_objects
	# connect shading network to everything in the lighting_test_layer
	for ro in render_objects:
		select ( ro, r=True )
		hyperShade( assign='lighting_test_mat' )
		select ( cl=True )

# applies the lighting_mat material to all objects in the lighting_test_layer
# MUST have the lighting_test_layer selected for this script to work!!
def applyZDepthMat( *pArgs ):
	zdepth_shader = ls('zdepth_mtl')

	if not zdepth_shader:
		print 'importing z-depth mat...'
		# import the shading network
		cmds.file( 'O:/unix/projects/instr/capstone4/production/interior_watercolor_pipeline/zdepth.mb', i=True)
	else:
		print 'z-depth mat is already in the set.'
		
	print 'applying z-depth mat...'
	render_objects = cmds.editRenderLayerMembers( 'zdepth_layer', q=True)
	print render_objects
	# connect shading network to everything in the zdepth_layer
	for ro in render_objects:
		select ( ro, r=True )
		hyperShade( assign='zdepth_mtl' )
		select ( cl=True )
		
def applyBeautyShaders( *pArgs ):
    #sets
    all_sets = cmds.listRelatives('set' , children=True)
    print all_sets
    
    if all_sets: 
        i = 0
        for set in all_sets:
            set_name = all_sets[i]
            set_sn = set_name[(set_name.find(':')+1):]
            print 'set exists. Assigning shaders to: ' + set_sn
                   
            print 'get all areas in ' + set_sn
            
            if (set_sn == 'interior_set'): 
                areas = cmds.listRelatives(set , children=True)
                print areas
                
                for area in areas:
                    area_name = area[(area.find(':')+1):]
                    print area_name
                    if area_name == 'kitchen':
                        print 'add shaders to the kitchen...'
                        sides = cmds.listRelatives(area , children=True)
                        for side in sides:
                            print 'kitchen side is: ' + side
                            objects = cmds.listRelatives(side , children=True)
                            print objects
                            for ob in objects:
                                ob_name = ob[(ob.find(':')+1):(ob.find(':',(ob.find(':')+1)))]
                                poly = cmds.listRelatives(ob , children=True)
                                print 'assigning shader to ' + ob
                                for p in poly:
                                    if ob_name.find('kitchen_counter_small') != -1:
                                        cmds.select ( p, r=True )
                                        cmds.hyperShade( assign = 'interior_set:kitchen_counter_small_mat' )
                                        cmds.select ( cl=True )
                                    else:
                                        cmds.select ( p, r=True )
                                        cmds.hyperShade( assign = 'interior_set:' + ob_name + '_mat' )
                                        cmds.select ( cl=True )
                    
                    if area_name == 'entryway':
                        print 'add shaders to the entryway...'
                        props = cmds.listRelatives(area , children=True)
                        for prop in props:
                            prop_name = prop[(prop.find(':')+1):(prop.find(':',(prop.find(':')+1)))]
                            print prop_name
                            pieces = cmds.listRelatives(prop , children=True)
                            for piece in pieces:
                                cmds.select ( piece, r=True )
                                cmds.hyperShade( assign = 'interior_set:' + prop_name + '_mat' )
                                cmds.select ( cl=True )
                                
                    if area_name == 'dining_room':
                        print 'add shaders to the dining room...'
                        props = cmds.listRelatives(area , children=True)
                        for prop in props:
                            prop_name = prop[(prop.find(':')+1):(prop.find(':',(prop.find(':')+1)))]
                            print prop_name
                            pieces = cmds.listRelatives(prop , children=True)
                            for piece in pieces:
                                if prop_name.find('chair')!= -1:
                                    cmds.select ( piece, r=True )
                                    cmds.hyperShade( assign = 'interior_set:chair_mat' )
                                    cmds.select ( cl=True )
                                elif prop_name.find('window2')!= -1:
                                    cmds.select ( piece, r=True )
                                    cmds.hyperShade( assign = 'interior_set:window_mat' )
                                    cmds.select ( cl=True )
                                else:
                                    cmds.select ( piece, r=True )
                                    cmds.hyperShade( assign = 'interior_set:' + prop_name + '_mat' )
                                    cmds.select ( cl=True )
                    
                    if area_name == 'living_room':
                        print 'add shaders to the living room...'
                        props = cmds.listRelatives(area , children=True)
                        for prop in props:
                            prop_name = prop[(prop.find(':')+1):(prop.find(':',(prop.find(':')+1)))]
                            print prop_name
                            pieces = cmds.listRelatives(prop , children=True)
                            for piece in pieces:
                                if prop_name.find('rug_rectangle')!= -1:
                                    cmds.select ( piece, r=True )
                                    cmds.hyperShade( assign = 'interior_set:rug_mat' )
                                    cmds.select ( cl=True )
                                else:
                                    cmds.select ( piece, r=True )
                                    cmds.hyperShade( assign = 'interior_set:' + prop_name + '_mat' )
                                    cmds.select ( cl=True )
                            
    
                    if area_name == 'structure':
                        print 'add shaders to the structure...'
                        structure = cmds.listRelatives(area , children=True)
                        print structure
                        for struc in structure:
                            if (struc.find('floor') != -1):
                                print 'assigning floor shader...'
                                cmds.select ( struc, r=True )
                                cmds.hyperShade( assign = 'interior_set:floor_mat' )
                                cmds.select ( cl=True )
                            elif (struc.find('ceiling') != -1):
                                print 'assigning ceiling shader...'
                                cmds.select ( struc, r=True )
                                cmds.hyperShade( assign = 'interior_set:ceiling_mat' )
                                cmds.select ( cl=True )
                            else:
                                print 'assigning wall shader...'
                                cmds.select ( struc, r=True )
                                cmds.hyperShade( assign = 'interior_set:wall_mat' )
                                cmds.select ( cl=True )
                            pieces = cmds.listRelatives(struc , children=True)
                            print pieces
            else:
                print 'no shaders were assigned'    
            i = i + 1
        i = 0
            
    else:
        print 'there is no set, moving onto next shading assignment'
    
    #props
    all_props = cmds.listRelatives('props' , children=True)
    print all_props
    
    if all_props: 
        print 'add shaders to the props...'
        for prop in all_props:
            #if it is not a rig, then assign shaders
            if (prop.find ('top_con') == -1):
                prop_name = prop[(prop.find(':')+1):]
                pieces = cmds.listRelatives(prop , children=True)
                for piece in pieces:
                    cmds.select ( piece, r=True )
                    cmds.hyperShade( assign = prop_name + ':' + prop_name + '_mat' )
                    cmds.select ( cl=True )
    else:
        print 'there are no props, moving onto next shading assignment'

createUI( 'Water Color Set Up Helpers', createRenderLayers, applyLightingMat, applyZDepthMat, createTestRenders, applyBeautyShaders )

'''
def applyAllShaders( *pArgs ):

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
    
    #Get a list of constraints parented to the given object
    #that, if said object is referenced, are not part of the
    #same reference node.

    
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

    #Redirect all constraint connections from a source object to a target object.
    
    #If no target object is specified, create a suitable placeholder. Return the
    #information necessary to reverse the process.

    
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
        print 'short name = ' + PyNode(newObj).shortName()
        newObjName = PyNode(newObj).shortName()
    
    
    #if (cmds.nodeType(newObjName) != cmds.nodeType(objName)):
    #    raise Exception("ERROR. Cannot redirect animation connections. Source and target objects not the same type: "+objName+", "+newObjName)
    
    
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

    #Return tuples of src and destination connections,
    #all outputs of the specified object.  If skRefConn
    #is true, ignore connections to other objects that are
    #part of the same FileReference node.
    
    #Format: (<source plug>, [<destination plug>,...])
    
    #All string output.

    
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

    #Return tuples of src and destination connections,
    #all inputs into the specified object.  If skRefConn
    #is true, ignore connections to other objects that are
    #part of the same FileReference node.
    
    #Format: (<source plug>, [<destination plug>])
    
    #All string output.

    
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

    #Return render layer connections of a reference file.
    
    #Same formatting as listFullInputs and listFullOutputs.

    toReturn = []
    
    for nodeName in cmds.referenceQuery(refFile, nodes=1):
        try:
            if u'dagNode' in nodeType(nodeName, i=1):
                toReturn += listFullInputs(nodeName, type="renderLayer")
        except:
            continue
    
    return toReturn

def getAllParentsOfReferencedNodes(refFile):

    #Return parents of referenced nodes that live in the scene and are not
    #referenced themselves.
    
    #Format: (<child>, <parent>)
    
    #All string output.

    print refFile
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

    #Returns a list of all light links on objects in the reference node.
    
    #Format: (<obj>, [<light>,...])
    
    #All string output.

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

    #Redirects and returns any advanced animation connections.
    
    #Format: (<redirected obj>, <original obj>)
    
    #All string output.

    toReturn = []
    
    for nodeName in cmds.referenceQuery(refFile, nodes=1):
        connectionPair = redirectAdvancedAnimationConnections(nodeName)
        if connectionPair != None:
            toReturn.append(connectionPair)
    
    return toReturn

lastRefInfo = None

# in the file, this function will re-reference all referenced objects
# and make sure that they're render layers are merged ("shared") with the
# ones that were already in the set to begin with
def mergeRenderLayers( *pArgs ):
    # select all references in the scene
    reference_list = cmds.file( q=True, l=True )
    reference_list_filtered = fnmatch.filter(reference_list, '*set.ma')
    #reference_list_filtered.append(fnmatch.filter(reference_list, '*grace_rig.ma')[0])
    print reference_list_filtered

    # iterate through each file and re-reference in with shared render layers checked
    i = 0
    for ref in reference_list_filtered:
        if (i >= 0):
            refName = ref
            if (refName.find('.png') == -1 and refName.find('.jpg') == -1 and refName.find('.PNG') == -1 and refName.find('.tif') == -1 and refName.find('grace_rig.ma') == -1 and refName.find('baby_noodle_rig.ma') == -1 and refName.find('noodle_rig.ma') == -1 and refName.find('adolescent_noodle_rig.ma') == -1):
                refFile = refName[(refName.rindex('/')+1):(refName.find('.ma'))]
                print refFile

                ## Reference information to remember
                print "Remembering old parents."
                oldParents = getAllParentsOfReferencedNodes(refName)
    
                print "Remembering attributes with no keyframes."
                nonKeyedAttrValues = []
                for anim in ls(refFile+':*.animNode', r=1, o=1):
                    for attr in anim.listAttr(keyable=1, u=1):
                        if keyframe(attr, kc=1, q=1) > 0: continue
                        nonKeyedAttrValues.append( (str(attr), attr.get()) )
    
                print "Remembering animation connections."
                oldAnimConns = getRedirectedAnimationConnections(refName)
    
                print "Remembering light links."
                oldLightLinks = getAllLightLinks(refName)
    
                print "Remember render layer connections."
                oldRenderLayerConns = getRenderLayerConnections(refName)
                refresh()

                # remove the reference
                cmds.file( refName, rr=True )
            
                # re-reference the file with shared render layers selected
                cmds.file( refName, r=True, namespace='', shd='renderLayersByName')

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

                print "FINISHED!"
        # increment
        i = i + 1
'''


'''
all_char = cmds.listRelatives('characters' , children=True)
print all_char

for char in all_char:
    objects =  cmds.listRelatives(char , children=True)
    print objects
    
    for ob in objects:
        print ob
        if (ob.find('grace') != -1):
            grace_mesh = cmds.listRelatives(ob , children=True)
            print grace_mesh
        
        cmds.select ( ob, r=True )
        cmds.hyperShade( assign='interior_set:' + prop + '_mat' )
        cmds.select ( cl=True )
        

all_props = cmds.listRelatives('props' , children=True)
print all_props

for prop in all_props:
    objects =  cmds.listRelatives(prop , children=True)
    print objects

    for ob in objects:
        print ob
        cmds.select ( ob, r=True )
        cmds.hyperShade( assign = prop + '_mat' )
        cmds.select ( cl=True )
    

    
'''
'''
all_props = cmds.listRelatives('interior_set' , children=True)
print all_props

for prop in all_props:
    objects =  cmds.listRelatives(prop , children=True)
    print objects

    for ob in objects:
        print ob
        cmds.select ( ob, r=True )
        cmds.hyperShade( assign = 'interior_set:' + prop + '_mat' )
        cmds.select ( cl=True )
    

    
'''
'''
from pymel.core import *
import maya.cmds as cmds
import os
import fnmatch



#characters
all_chars = cmds.listRelatives('characters' , children=True)
print all_chars

if all_chars: 
    print 'add shaders to the characters...'
    for char in all_chars:
        if(char.find('BabyNoodle_topCon')!= -1):
            #assign body shaders
            cmds.select ( 'baby_noodle:body_geo', r=True )
            cmds.hyperShade( assign = 'baby_noodle:body_mat' )
            cmds.select ( cl=True )
            
            #assign eyes
            cmds.select ( 'baby_noodle:left_eye_geo', r=True )
            cmds.hyperShade( assign = 'baby_noodle:face_mat' )
            cmds.select ( cl=True )
            cmds.select ( 'baby_noodle:right_eye_geo', r=True )
            cmds.hyperShade( assign = 'baby_noodle:face_mat' )
            cmds.select ( cl=True )
            
            #assign mouth shaders
            inner_mouth = cmds.listRelatives('baby_noodle:mouth_grp' , children=True)
            for inm in inner_mouth:
                cmds.select ( inm, r=True )
                cmds.hyperShade( assign = 'baby_noodle:face_mat' )
                cmds.select ( cl=True )
        elif((char.find('Noodle_topCon')!= -1):
            #assign body shaders
            cmds.select ( 'noodle:body_geo', r=True )
            cmds.hyperShade( assign = 'noodle:body_mat' )
            cmds.select ( cl=True )
            
            #assign eyes
            cmds.select ( 'noodle:left_eye_geo', r=True )
            cmds.hyperShade( assign = 'noodle:face_mat' )
            cmds.select ( cl=True )
            cmds.select ( 'noodle:right_eye_geo', r=True )
            cmds.hyperShade( assign = 'noodle:face_mat' )
            cmds.select ( cl=True )
            
            #assign mouth shaders
            inner_mouth = cmds.listRelatives('noodle:mouth_grp' , children=True)
            for inm in inner_mouth:
                cmds.select ( inm, r=True )
                cmds.hyperShade( assign = 'noodle:face_mat' )
                cmds.select ( cl=True )
        elif((char.find('AdoNoodle_topCon')!= -1):
            #assign body shaders
            cmds.select ( 'noodle:body_geo', r=True )
            cmds.hyperShade( assign = 'noodle:body_mat' )
            cmds.select ( cl=True )
            
            #assign eyes
            cmds.select ( 'adolescent_noodle:left_eye_geo', r=True )
            cmds.hyperShade( assign = 'adolescent_noodle:face_mat' )
            cmds.select ( cl=True )
            cmds.select ( 'adolescent_noodle:right_eye_geo', r=True )
            cmds.hyperShade( assign = 'adolescent_noodle:face_mat' )
            cmds.select ( cl=True )
            
            #assign mouth shaders
            inner_mouth = cmds.listRelatives('adolescent_noodle:mouth_grp' , children=True)
            for inm in inner_mouth:
                cmds.select ( inm, r=True )
                cmds.hyperShade( assign = 'adolescent_noodle:face_mat' )
                cmds.select ( cl=True )
        elif((char.find('Grace_topCon')!= -1):
            #assign face
            cmds.select ( 'grace:face_geo', r=True )
            cmds.hyperShade( assign = 'grace:face_mat' )
            cmds.select ( cl=True )
            
            #assign hair & eyebrows
            cmds.select ( 'grace:hair_geo', r=True )
            cmds.hyperShade( assign = 'grace:hair_mat' )
            cmds.select ( cl=True )
            cmds.select ( 'grace:eyebrow_geo', r=True )
            cmds.hyperShade( assign = 'grace:hair_mat' )
            cmds.select ( cl=True )
            
            #assign mouth, eyes and lashes
            inner_mouth = cmds.listRelatives('grace:mouth_grp_geo' , children=True)
            for inm in inner_mouth:
                cmds.select ( inm, r=True )
                cmds.hyperShade( assign = 'grace:mouth_mat' )
                cmds.select ( cl=True )
            
            cmds.select ( 'grace:left_eye_geo', r=True )
            cmds.hyperShade( assign = 'grace:mouth_mat' )
            cmds.select ( cl=True )
            cmds.select ( 'grace:right_eye_geo', r=True )
            cmds.hyperShade( assign = 'grace:mouth_mat' )
            cmds.select ( cl=True )     
            
            cmds.select ( 'grace:eyelash_geo', r=True )
            cmds.hyperShade( assign = 'grace:mouth_mat' )
            cmds.select ( cl=True )  
            
            #assign body shaders
            body_all = cmds.listRelatives('grace:mesh_grp' , children=True)
            
            for body in body_all:
                if (body.find('grace:home_geo_grp') == -1 or body.find('grace:husbandcoat_geo_grp') == -1 or body.find('grace:gracecoat_geo_grp') == -1):
                    if (body.find('grace:left_upperleg_block') != -1):
                        cmds.select ( body, r=True )
                        cmds.hyperShade( assign = 'grace:body_mat' )
                        cmds.select ( cl=True )
            
            cmds.select ( 'noodle:body_geo', r=True )
            cmds.hyperShade( assign = 'noodle:body_mat' )
            cmds.select ( cl=True )
            

            #assign mouth shaders
            inner_mouth = cmds.listRelatives('adolescent_noodle:mouth_grp' , children=True)
            for inm in inner_mouth:
                cmds.select ( inm, r=True )
                cmds.hyperShade( assign = 'adolescent_noodle:face_mat' )
                cmds.select ( cl=True )
                
            
else:
    print 'there are no characters, moving onto next shading assignment'

'''
'''
for prop in all_props:
    objects =  cmds.listRelatives(prop , children=True)
    print objects
    prop_sn = prop[:(prop.find(':'))]
    print prop_sn
    
'''
