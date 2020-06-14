from pymel.core import *
from pymel.all import *

import scene_manager.metaCore as meta
from scene_manager.gui import *
import random

###################################################################
#              Nebbish Production
###################################################################
def createFaceComponent(char, joints, parentComponent, layer):
	components = createFaceComponent(char, joints, parentComponent)
	for component in components:
		map(lambda x: layer.append(x), component.getAllAnims())
	return components

def createFaceComponent(char, joints, parentComponent):
	components = []
	for j in joints:
		print j
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
		component = meta.SingleIKChain(side, bodyPart, par, j)
		component.connectToComponent(parentComponent, par)
		components.append(component)
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
	prunePlaces = 3
	values = [ skin, '[%s]'%','.join(mel.libSkin_getSelComps(skin[0])) ,mode , tol, mirrorMode, '', '', doPrune, prunePlaces]
	print values
	mel.cSaveW_load(skin[0], weightsFile, mel.libSkin_getSelComps(skin[0]) ,mode , tol, mirrorMode, '', '', doPrune, prunePlaces) 
