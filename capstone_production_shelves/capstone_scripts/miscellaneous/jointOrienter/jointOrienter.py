from pymel.core import *
import maya.OpenMaya as api
import maya.cmds as cmds
import os

class JointOrienter:
    
    P_AXIS = (1,0,0)
    S_AXIS = (0,0,1)
    
    P_AXIS_MODE = None
    S_AXIS_MODE = None
    
    P_AXIS_MODE_ARGS = None
    S_AXIS_MODE_ARGS = None


    def __init__(self):
        pass
       
    ##################################
    #      World vector helpers      #
    ##################################
        
    def getWorldPositionVector(self, obj, localPosition=None):
        '''
        Given a local position vector and an object, return the object's pivot plus
        the local position (in object space) in world space. If no local position vector
        is specified just return the world position.
        '''
        
        basePos = dt.Vector(cmds.pointPosition(str(obj)+'.rp', w=1))
        obj = str(obj)
    	
        if localPosition == None: return basePos
        
        localPosition = dt.Vector(localPosition)
        
        # Use OpenMaya instead of the above code since it's
        # way faster than using PyMEL's matrix class
        matrixValues = cmds.xform(obj, q=1, m=1, ws=1)
        m = api.MMatrix()
        api.MScriptUtil.createMatrixFromList(matrixValues, m)
        tm = api.MTransformationMatrix(m)
        pos1 = tm.translation(api.MSpace.kWorld)
        tm.addTranslation(api.MVector(localPosition), api.MSpace.kPreTransform)
        pos2 = tm.translation(api.MSpace.kWorld)
        worldPosChange = pos2-pos1
    
        return basePos+(dt.Vector(worldPosChange))
    
    def getWorldDirectionVector(self, trans, localDirection):
        '''
        Given a local direction vector and an object, return that
        direction vector in world space from object space.
        '''
        tempGrp = PyNode(group(em=1, n="tempTransTracker"))
        tempLoc = PyNode(spaceLocator(n="tempUpAim"))
        parent(tempLoc, tempGrp)
        tempLoc.translate.set(localDirection[0], localDirection[1], localDirection[2])
        pc = parentConstraint(trans, tempGrp, mo=0)
        delete(pc)
        dirVector = (tempLoc.getTranslation("world")-tempGrp.getTranslation("world")).normal()
        delete(tempGrp)
        return dirVector
    
    ##################################
    #   Joint orientation helpers    #
    ##################################

    def getCoplanarNormal(self, transforms=[]):
        '''
        Return the normal of the coplanar space between three transforms.
        '''
        
        if (len(transforms) != 3): return None
        faceT = PyNode(polyCreateFacet(ch=0, p=map(lambda t: xform(t, q=1, ws=1, t=1), transforms))[0])
        normal = faceT.f.getNormal(space="world")
        delete(faceT)
        return normal
        
    def getWorldDirectionOfSingleChild(self, trans):
        '''
        Return the world direction vector towards a single child transform.
        '''
        
        children = trans.getChildren()
        dir = (self.getWorldPositionVector(children[0]) - self.getWorldPositionVector(trans))
        return dir

    def getWorldDirectionOfSingleTarget(self, trans, targetTrans):
        '''
        Return the world direction vector towards a single target.
        '''
        
        dir = (self.getWorldPositionVector(targetTrans) - self.getWorldPositionVector(trans))
        return dir
    
    def aimSingleAxisAtTransform(self, trans):
        return None
 
    ##################################
    # Process joints and orient them #
    ##################################
    
    def getAxisDir(self, j, axis, mode, args):
        '''
        Based on a given joint and axis/mode info, return a world direction vector.
        '''
        
        if mode == 'AIM_AT_CHILD':
            return self.getWorldDirectionOfSingleChild(j)
            
        elif mode == 'AIM_AT_TARGET':
            return self.getWorldDirectionOfSingleTarget(j, args[0])
            
        elif mode == 'MATCH_TARGET':
        
            # If an axis is specified, match to that target's specifed axis
            if (len(args) == 2):
                return self.getWorldDirectionVector(args[0], eval(args[1]))
                
            # If no axis is specifed, match to the axis being handled
            else:
                return self.getWorldDirectionVector(args[0], axis)
            
        elif mode == 'MATCH_PARENT':
            return self.getWorldDirectionVector(j.getParent(), axis)
        
        elif mode == 'MATCH_WORLD':
            return dt.Vector(eval(args[0]))
        
        elif mode == 'COPLANAR':
            return self.getCoplanarNormal(args)

        else:
            return None
            
    def orientJoint(self, j):
        '''
        Orient joint based on internal primary and secondary axis mode settings.
        '''

        primaryDir = self.getAxisDir(j, self.P_AXIS, self.P_AXIS_MODE, self.P_AXIS_MODE_ARGS)
        secondaryDir = self.getAxisDir(j, self.S_AXIS, self.S_AXIS_MODE, self.S_AXIS_MODE_ARGS)
 
        # Save hierarchy information
        jParent = j.getParent()
        jChildren = j.getChildren()
        
        # Remove from hiearchy
        if len(jChildren) > 0: parent(jChildren, w=1)
        if (jParent != None): parent(j, w=1)
        
        # Align to primary/secondary directions
        pLoc = spaceLocator(n='pLoc')
        sLoc = spaceLocator(n='sLoc')
        pos = self.getWorldPositionVector(j)
        move(pLoc, pos+primaryDir, ws=1)
        move(sLoc, pos+secondaryDir, ws=1)
        ac = aimConstraint(pLoc, j, aim=self.P_AXIS, u=self.S_AXIS, wut='object', wuo='sLoc')
        delete(ac, pLoc, sLoc)
        makeIdentity(j, t=0,r=1,s=0,jo=0,a=1)
        
        # Insert back into the hierarchy
        if (jParent != None): parent(j, jParent)
        parent(jChildren, j)

    def readTemplate(self, path):
        
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
                self.P_AXIS_MODE = lineComps[1]
                self.P_AXIS_MODE_ARGS = lineComps[2:]
            
            elif cmd == 'S_AXIS_MODE':
                # Secondary axis orientation commands
                self.S_AXIS_MODE = lineComps[1]
                self.S_AXIS_MODE_ARGS = lineComps[2:]
                
            elif cmd == 'ALL_AXIS_MODE':
                # Change both axis modes at once
                self.P_AXIS_MODE = self.S_AXIS_MODE = lineComps[1]
                self.P_AXIS_MODE_ARGS = self.S_AXIS_MODE_ARGS = lineComps[2:]
                
            elif cmd == 'P_AXIS':
                # Set the primary axis
                self.P_AXIS = eval(lineComps[1])
                
            elif cmd == 'S_AXIS':
                # Set the secondary axis
                self.S_AXIS = eval(lineComps[1])
                
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
                        
                    self.orientJoint(j)
                
            else:
                print 'WARNING: Command "'+str(cmd)+'" not recognized. Skipping.'
                
        f.close()
        
        
jo = JointOrienter()
jo.readTemplate("O:/unix/projects/instr/capstone4/preproduction/animatic/assets/character/baby_noodle/_rigging/joTemplate_baby_noodle.txt")