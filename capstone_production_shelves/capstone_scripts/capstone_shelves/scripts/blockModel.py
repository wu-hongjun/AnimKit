from pymel.core import *
import pymel.core.datatypes as dt

def getWorldPositionVector(trans, localPosition=dt.Vector(0,0,0)):
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


def create_block_model(jnt, parent_option=True, girth_size=3, ratio_option=True, ratio_value=0.25, skip_end_joints=True, default_dist=1):
    '''
    Creates a polygon the length of the input joint.  If ratio_option is true, girth value is 
    the distance multiplied by the ratio value.  If ratio_option is false, girth_value is used in world units.
    '''
    
    joint_name = jnt.name()
    if (skip_end_joints and len(jnt.getChildren())==0):
        '"'+joint_name+'" is an end joint, skipping.'
        return None
    
    # Create polygon cube with pivot at base 
    if joint_name.endswith('_bind_joint'):
        joint_name = jnt.name()[:-11]
        
    if joint_name.endswith('_end_joint'):
        joint_name = jnt.name()[:-10]
        
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
        j1Pos = getWorldPositionVector(jnt)
        j2Pos = getWorldPositionVector(child_joints[0])
        dist = j1Pos.distanceTo(j2Pos)
        # print 'dist {0}'.format(dist)
        if dist <= 0.001:
            dist = default_dist
            print 'Distance to first child on x axis is zero.  Setting distance to default distance of '+str(default_dist)
    else:
        dist = default_dist
        print 'Input joint has no descendents.  Using default scale value. {0}'.format(jnt.name())
    
    # Aim towards a like-named child or all joint children
    if child_joints:
        
        jnt_name_comps = jnt.shortName().split('_')
        
        # Assume we're aiming at all of the child joints to begin with
        aim_at_these_joints = child_joints
        
        # Aim toward the set of children with the most similar name components,
        # starting from left to right and separated by underscores.
        most_matched_comps = 0
        most_matched_comps_joints = []
        for c in child_joints:
            child_name_comps = c.shortName().split('_')
            matches = 0
            for i in xrange(min(len(child_name_comps), len(jnt_name_comps))):
                if (child_name_comps[i] == jnt_name_comps[i]):
                    matches += 1
                else:
                    break
            if matches > most_matched_comps:
                most_matched_comps = matches
                most_matched_comps_joints = [c]
            elif matches == most_matched_comps:
                most_matched_comps_joints += [c]
        
        aim_at_these_joints = most_matched_comps_joints
        
        ac = aimConstraint(aim_at_these_joints, block, aim=(1,0,0), u=(0,1,0), wut="objectrotation", wuo=jnt)
        delete(ac)

    else:
        block.rotate.set(0,0,0)
    
    # Create the block model based on input options for girth and ratio
    girth = girth_size
    
    if ratio_option:
        girth = dist * ratio_value
    
    block.scale.set([dist, girth, girth])
    makeIdentity(block, apply=True, t=True, r=False, s=True, n=False)
    
    if not parent_option:
        block.setParent(world=True)