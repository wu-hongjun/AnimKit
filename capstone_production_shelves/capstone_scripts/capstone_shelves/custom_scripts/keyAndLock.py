#keyAndLock.py
#key and lock settings at 0 frame
from pymel.core import *

fileName = sceneName()
newFile = fileName.replace("_factory_set", "_imported_set")

referenceList = listReferences()
topRootList = []

refList = ls(referencedNodes = True, type = "transform")
transformList = ls(type = "transform")

for i in range(len(transformList)):
    object = transformList[i]
    objectAttr = listAttr(object)
    cutKey(object, time = (0, 10), attribute = objectAttr)

transformList = filter(lambda t: not isinstance(t.getShape(), nt.Camera), transformList)

for i in range(len(refList)):
    transformList.remove(refList[i])

for ref in referenceList:
    tmp = referenceQuery(ref, referenceNode = True, topReference = True)
    tmpnodes = referenceQuery(tmp, nodes = True)
    topRootList.append(tmpnodes[0])
    ref.importContents()

for i in range(len(transformList)):
    object = transformList[i]
    keyAttr = listAttr(object, keyable = True)
    keyAttr.remove("visibility")
    setKeyframe(object, time = 0, attribute = keyAttr)
    
    for attr in keyAttr:
        if (attr != "visibility"):
            setAttr(object + "." + attr, lock = 1)

for i in range(len(topRootList)):
    object = topRootList[i]
    keyAttr = listAttr(object, keyable = True)
    keyAttr.remove("visibility")
    setKeyframe(object, time = 0, attribute = keyAttr)
    
    for attr in keyAttr:
        if (attr != "visibility"):
            setAttr(object + "." + attr, lock = 1)

saveAs(newFile) 