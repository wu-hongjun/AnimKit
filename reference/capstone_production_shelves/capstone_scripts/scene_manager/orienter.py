from pymel.core import *
import maya.OpenMaya as api
import maya.cmds as cmds
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

import os

import scene_manager.metaCore as meta
import scene_manager.metaUtil as mu

# Global axis and axis mode tracking for readTemplate
P_AXIS = (1,0,0)
S_AXIS = (0,0,1)
P_AXIS_MODE = None
S_AXIS_MODE = None
P_AXIS_MODE_ARGS = None
S_AXIS_MODE_ARGS = None


##################################
#   Joint orientation helpers    #
##################################

def getCoplanarNormal(transforms=[]):
    '''
    Return the normal of the coplanar space between three transforms.
    '''
    
    if (len(transforms) != 3): return None
    faceT = PyNode(polyCreateFacet(ch=0, p=map(lambda t: xform(t, q=1, ws=1, t=1), transforms))[0])
    normal = faceT.f.getNormal(space="world")
    delete(faceT)
    return normal
    
def getWorldDirectionOfSingleChildJoint(trans):
    '''
    Return the world direction vector towards a single child joint.
    '''
    
    children = trans.getChildren()
    jointChildren = filter(lambda c: isinstance(c, nt.Joint), children)
    dir = (mu.getWorldPositionVector(jointChildren[0]) - mu.getWorldPositionVector(trans))
    return dir

def getWorldDirectionOfSingleTarget(trans, targetTrans):
    '''
    Return the world direction vector towards a single target.
    '''
    
    dir = (mu.getWorldPositionVector(targetTrans) - mu.getWorldPositionVector(trans))
    return dir

def aimSingleAxisAtTransform(trans):
    return None


##################################
# Process joints and orient them #
##################################

def getAxisDir(j, axis, mode, args):
    '''
    Based on a given joint and axis/mode info, return a world direction vector.
    '''
    
    if mode == 'AIM_AT_CHILD':
        return getWorldDirectionOfSingleChildJoint(j)
        
    elif mode == 'AIM_AT_TARGET':
        return getWorldDirectionOfSingleTarget(j, args[0])
        
    elif mode == 'MATCH_TARGET':
    
        # If an axis is specified, match to that target's specifed axis
        if (len(args) == 2):
            return mu.getWorldDirectionVector(args[0], eval(args[1]))
            
        # If no axis is specifed, match to the axis being handled
        else:
            return mu.getWorldDirectionVector(args[0], axis)
        
    elif mode == 'MATCH_PARENT':
        return mu.getWorldDirectionVector(j.getParent(), axis)
    
    elif mode == 'MATCH_WORLD':
        return dt.Vector(eval(args[0]))
    
    elif mode == 'COPLANAR':
        return getCoplanarNormal(args)

    else:
        return None
        
def orientJoint(j):
    '''
    Orient joint based on internal primary and secondary axis mode settings.
    '''
    
    global P_AXIS
    global S_AXIS
    global P_AXIS_MODE
    global S_AXIS_MODE
    global P_AXIS_MODE_ARGS
    global S_AXIS_MODE_ARGS
    
    primaryDir = getAxisDir(j, P_AXIS, P_AXIS_MODE, P_AXIS_MODE_ARGS)
    secondaryDir = getAxisDir(j, S_AXIS, S_AXIS_MODE, S_AXIS_MODE_ARGS)
    # print P_AXIS, P_AXIS_MODE, P_AXIS_MODE_ARGS, S_AXIS, S_AXIS_MODE, S_AXIS_MODE_ARGS
    
    # Save hierarchy information
    jParent = j.getParent()
    jChildren = j.getChildren()
    
    # Remove from hiearchy
    if len(jChildren) > 0: parent(jChildren, w=1)
    if (jParent != None): parent(j, w=1)
    
    # Align to primary/secondary directions
    pLoc = spaceLocator(n='pLoc')
    sLoc = spaceLocator(n='sLoc')
    pos = mu.getWorldPositionVector(j)
    move(pLoc, pos+primaryDir, ws=1)
    move(sLoc, pos+secondaryDir, ws=1)
    ac = aimConstraint(pLoc, j, aim=P_AXIS, u=S_AXIS, wut='object', wuo='sLoc')
    delete(ac, pLoc, sLoc)
    makeIdentity(j, t=0,r=1,s=0,jo=0,a=1)
    
    # Insert back into the hierarchy
    if (jParent != None): parent(j, jParent)
    parent(jChildren, j)

def readTemplate(path):
    
    global P_AXIS
    global S_AXIS
    global P_AXIS_MODE
    global S_AXIS_MODE
    global P_AXIS_MODE_ARGS
    global S_AXIS_MODE_ARGS
    
    f = open(path, 'r')
    
    for l in f.readlines():
        lineComps = l.strip().split(' ')
        numComps = len(lineComps)
        
        # No info in this line, skip
        if numComps < 2 or lineComps[0] == '' or lineComps[0].startswith('//'): continue
        cmd = lineComps[0]
        
        # Read in commands
        if cmd == 'P_AXIS_MODE':
            # Primary axis orientation commands
            P_AXIS_MODE = lineComps[1]
            P_AXIS_MODE_ARGS = lineComps[2:]
        
        elif cmd == 'S_AXIS_MODE':
            # Secondary axis orientation commands
            S_AXIS_MODE = lineComps[1]
            S_AXIS_MODE_ARGS = lineComps[2:]
            
        elif cmd == 'ALL_AXIS_MODE':
            # Change both axis modes at once
            P_AXIS_MODE = S_AXIS_MODE = lineComps[1]
            P_AXIS_MODE_ARGS = S_AXIS_MODE_ARGS = lineComps[2:]
            
        elif cmd == 'P_AXIS':
            # Set the primary axis
            P_AXIS = eval(lineComps[1])
            
        elif cmd == 'S_AXIS':
            # Set the secondary axis
            S_AXIS = eval(lineComps[1])
            
        elif cmd == 'ORIENT':
            # Orient a single joint or multiple joints with the specified name pattern
            jNames = ls(lineComps[1])
            
            for jName in jNames:
        
                # Orient joint based on the input modes
                try:
                    j = PyNode(jName)
                except:
                    print 'ERROR: "'+lineComps[1]+'" is an invalid node name.'
                    continue
                    
                if not isinstance(j, nt.Joint):
                    print 'ERROR: "'+lineComps[1]+'" is not a joint.'
                    continue

                orientJoint(j)
            
        else:
            print 'WARNING: Command "'+str(cmd)+'" not recognized. Skipping.'
            
    f.close()