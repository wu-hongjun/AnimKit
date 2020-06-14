from pymel.all import *;from scene_manager import *
select(listRelatives(ls(sl=1), ad=1))
for anim in ls(sl=1): 
    if anim == '*_anim' or objExists(anim.name() + '.animNode'):
        resetAttrs(anim)
        
for anim in ls('*_anim', r=1, sl=1): resetAttrs(anim)