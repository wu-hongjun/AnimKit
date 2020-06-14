from pymel.core import *
import pymel.core as pm

result = [0,0,0,0]
print result
root = ls(assemblies = True)
size = len(root)

#Requirement 1:There should be only one top-level node.
if (size == 5) :
	result[0] = 1;

#Requirement 2:Name Check
name = sceneName().name.split('.')[0]
Testname = "hahaha"

for element in root:
	if element == name or element == Testname:
		result[1] = 1;

#Requirement 3:Freeze Transforms & Black Box
path = sceneName().parent.parent
propType = path.split('/')[-1]
if propType =='prop_static' :
	assetElement = root[-1]
	pm.makeIdentity( assetElement, a = True, t = False, r = False, s = True )
	cmdStr = 'setAttr "' + name + '.blackBox" 1'
	mel.eval(cmdStr)
	result[2]=1

#Requirement 4:Delete History if it's static prop.

if propType == 'prop_static':
	#delete history
	result[3]=1
	select(name)
	mel.eval('DeleteHistory')
	mel.eval('select -cl')

print result

#popup the result window
win = window(title="Prop Check result", w=100 ,h=100)
columnLayout(adjustableColumn=True)
resultText="\nProp Check Result:\n\n";

if result[0] == 0:
	resultText = resultText + "1) WARNING: There should be only one top-level node. [X FAILED X]\n\n"
else :
	resultText = resultText + "1) There is only one top-level node. [O PASSED O]\n\n"

if result[1] == 0:
	resultText = resultText + "2) WARNING: The asset name may be inconsistent with the prop.\n\n"
else:
	resultText = resultText + "2) The asset name is consistent with the prop. \n\n"

if result[2] == 0:
	resultText = resultText + "3) WARNING: The transforms are not freezed since this is a RIGGED prop. \n\n"
else:
	resultText = resultText + "3) The transforms are freezed and the asset is blackBox-ed. \n\n"

if result[3] == 0:
	resultText = resultText + "4) WARNING: The history is not deleted since this is a RIGGED prop.\n"
else:
	resultText = resultText + "4) The history is deleted since this is a static prop.\n"
text( label = resultText, align="left")
button(label='Got it!', command=Callback(win.delete))

win.show()