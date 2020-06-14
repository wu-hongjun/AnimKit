#randomly create 50 cubes
from pymel.core import *
import random

random.seed(1000)

cubeList = cmds.ls("myCube*")
if len(cubeList) > 0:
    cmds.delete(cubeList)

result = polyCube(w = 1, h = 1, d = 1, name = "myCube#")
transformName = result[0]

# create an empty group
instanceGroupName = group(empty = True, name = transformName + "instance_grp#")

for i in range(50):
	# duplicate the instance
    instanceResult = instance(transformName, name = transformName + "_instance#")
	# parent each cube under the group
    parent(instanceResult, instanceGroupName)
	# randomlize the translation, rotation and scale
    x = random.uniform(-10, 10)
    y = random.uniform(0, 20)
    z = random.uniform(-10, 10)
    
    move(x, y, z, instanceResult)
    
    xRot = random.uniform(0, 360)
    yRot = random.uniform(0, 360)
    zRot = random.uniform(0, 360)
    
    rotate(instanceResult, xRot, yRot, zRot)
    
    scaling = random.uniform(0.5, 1.5)
    
    scale(instanceResult, scaling, scaling, scaling)
    
hide(transformName)
# move pivot to the center of this group
xform(instanceGroupName, centerPivots = True)


# parent each child object to target object
from pymel.core import *

# select objects in order
selectionList = ls(orderedSelection = True)

if len(selectionList) >= 2:
    
    targetName = selectionList[0]
    selectionList.remove(targetName)
    
    for objectName in selectionList:
        aimConstraint(targetName, objectName)


		
# spin the group and playblast, select the object you want to animate first
from pymel.core import *

selectionList = ls(selection = True, type = "transform")

if len(selectionList) >= 1:
    
    startTime = playbackOptions(query = True, minTime = True)
    endTime = playbackOptions(query = True, maxTime = True)
    
    for objectName in selectionList:
        cutKey(objectName, time = (startTime, endTime), attribute = "rotateY")
        setKeyframe(objectName, time = startTime, attribute = "rotateY", value = 0)
        setKeyframe(objectName, time = endTime, attribute = "rotateY", value = 360)
        selectKey(objectName, time = (startTime, endTime), attribute = "rotateY", keyframe = True)
        keyTangent(inTangentType = "linear", outTangentType = "linear")
		
playblast()		

# use above three function in sequence, and check the amazing result

# add jitter motion on Y axis, simple version		
from pymel.core import *

obj = ls(selection = True, type = 'transform')
startTime = playbackOptions(query = True, minTime = True)
endTime = playbackOptions(query = True, maxTime = True)
print str(startTime) + ", " + str(endTime)

keys = keyframe(obj, attribute = "translateY", query = True)
print keys

for i in keys:
	orig = getAttr(obj, time = i, attribute = "translateY")
    setKeyframe(obj, time = i - 1, attribute = "translateY", value = orig - 1)
	setKeyframe(obj, time = i + 1, attribute = "translateY", value = orig + 1)
    
	
