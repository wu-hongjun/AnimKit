# copySkins.py

from pymel.core import *
import os
import maya.cmds as cmds

def createUI( pWindowTitle, bindCallback, saveCallback, copyCallback ):
    
    windowID = 'copySkinsID'
    
    if cmds.window( windowID, exists=True ):
        cmds.deleteUI( windowID )
    
    cmds.window( windowID, title=pWindowTitle, sizeable=False, resizeToFitChildren=True )
    
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1,150), (2,5), (3,350) ], columnOffset=[ (3, 'left', 3) ] ) 
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    
    cmds.button( label='Initial skin bind', command=bindCallback)
    cmds.separator( h=10, style='none')
    cmds.text( label='Select the mesh to do an initial skin bind for' )
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    
    cmds.button( label='Save current mesh weights', command=saveCallback)
    cmds.separator( h=10, style='none')
    cmds.text( label='Select the mesh to save weights for (should have a skin cluster)' )
    
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    cmds.separator( h=10, style='none')
    
    cmds.button( label='Copy over weights', command=copyCallback)
    cmds.separator( h=10, style='none')
    cmds.text( label='Select the mesh to copy to weights to' )
   
    cmds.showWindow()

def bindCallback( *pArgs ):
    print 'Initial skin bind pressed.'
    mesh = ls(sl=1)
    jts = ls('*bind_joint')
    if jts:
        select(jts)
    else:
        jts = ls('*:*bind_joint')
        select(jts)
    select(mesh, add=1)
    #bind skin
    skinCluster(toSelectedBones=1, obeyMaxInfluences=0, skinMethod=0, volumeBind=0, volumeType=1, dropoffRate=4, nw=1)

def saveCallback( *pArgs ):
    print 'Save current mesh weights pressed.'
    filename = os.path.join(sceneName().dirname(), 'weightProxy.ma')
    oldmeshname = ls(sl=1)[0]
    rename(ls(sl=1), 'weightproxymesh')
    select('weightproxymesh')
    exportSelected(filename, type="mayaAscii", constructionHistory=1, expressions=0, shader=0, constraints=0, channels=0, preserveReferences=0, f=1)
    rename(ls(sl=1), 'body_geo')
    select(cl=1)
    
def copyCallback( *pArgs ):
    print 'Copy over weights pressed.'
    mesh = ls(sl=1)
    jts = ls('*bind_joint')
    if jts:
        select(jts)
    else:
        jts = ls('*:*bind_joint')
        select(jts)

    select(mesh, add=1)
    #bind skin
    skinCluster(toSelectedBones=1, obeyMaxInfluences=0, skinMethod=0, volumeBind=0, volumeType=1, dropoffRate=4, nw=1)
    #filename for weight proxy
    proxyfile = os.path.join(sceneName().dirname(), 'weightProxy.ma')
    #import weight proxy
    importFile(proxyfile, groupReference=1, groupName='proxy')
    #copy weights over
    copySkinWeights(ss='weightProxy_skinCluster1', ds='skinCluster1', nm=1, ia='closestJoint', sa='closestPoint')
    #delete proxy
    delete('proxy')

createUI( 'Copy Skin Weights for Modeling', bindCallback, saveCallback, copyCallback)