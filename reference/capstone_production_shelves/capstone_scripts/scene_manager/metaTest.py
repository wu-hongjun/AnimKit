from metaCore import *
import pymel.core.datatypes as dt

def createNurbsPlaneCurveIKChain(startJoint, endJoint, compName):
	'''
	create stretchy ik controls for the chain
	startJoint:
		the starting joint for the chain
	endJoint:
		the ending joint for the chain
	return:
		[startAnim,   	#0, the ik anim that controls the start of the chain   
		midAnim,		#1  the ik anim that controls the middle of the chain, note: parented contrained between start and end
		endAnim,		#2  the ik anim that controls the end of the chain
		animGrp,		#3  the grp created around the anims and their groups, note: reparent this group instead of the individual anims
		ik_joint_grp, 	#4  the group that contains the joints given, note: joints now aren't in a heirarchy
		nurbsPlane, 	#5  the plane created to control the joints
		transGrp, 		#6  the groups controled by the point on surface nodes
		dummyGrp, 		#7  groups which match joints and are nurbConstrained to surface
		ikLocGrp,		#8  locators to help measure distanced of the joints
		distDimGrp]		#9	distance dimension objects for scaling purposes
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
	nurbsPlane = loft(leftCurve, rightCurve,ch=0, ss=1, d=3, ar=1, c=0, rn=0, po=0, rsn = 0)[0]
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
	#pointConstraint(control_start, control_end, midConstGrp, mo=1, w=1)
	c1 = control_start.t.get()
	c2 = control_mid.t.get()
	c3 = control_end.t.get()
	curve_points = [c1, c2-((c3-c1)*.01), c2+((c3-c1)*.01), c3]
	mid_curve = curve(p=curve_points, bez=True, n='%s_constraint_curve'%control_mid.name())
	midp = (c1.distanceTo(c2))/(c1.distanceTo(c2)+c2.distanceTo(c3))
	mid_poc = pointOnCurve(mid_curve, pr=midp)
	mid_poc.p >> midConstGrp.t
	
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

class FKIKAutoSpine(RigComponent):
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
			dntGrp = group([nurbsPlane,	transGrp,dummyGrp,ikLocGrp,	distDimGrp], n = "%s_DO_NOT_TOUCH_grp"%compName)
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
		allAnims.append(self.networkNode.startAnim.listConnections()[0])
		allAnims.append(self.networkNode.midAnim.listConnections()[0])
		allAnims.append(self.networkNode.endAnim.listConnections()[0])
		allAnims.append(self.networkNode.switchGroup.listConnections()[0])
		allAnims.append(self.networkNode.pelvisAnim.listConnections()[0])
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
		stretch = switchGroup.attr('stretch')
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
