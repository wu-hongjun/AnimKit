import pymel.all as pm
import maya.cmds as mc
import os
import MARS.MarsUtilities as mu
reload(mu)

class AnimShaders():
    def __init__(self,rig):
        #Variables
        self.rig = pm.PyNode(rig)
        anims = rig.get_complete_rig_anims()
        
        #Create Shaders
        if not self.rig.hasAttr('connected_to'):
            center_shader = pm.shadingNode('lambert',n = ('center_' + self.rig.character_name.get() + '_anim_shader'),asShader=True)
            left_shader = pm.shadingNode('lambert',n = ('left_' + self.rig.character_name.get() + '_anim_shader'),asShader=True)
            right_shader = pm.shadingNode('lambert',n = ('right_' + self.rig.character_name.get() + '_anim_shader'),asShader=True)
            shaders = [center_shader,left_shader,right_shader]
            center_shader.color.set(0,0,1)
            left_shader.color.set(0,0.75,1)
            right_shader.color.set(1,0,0)
            topCon = pm.listConnections(self.rig.topCon)[0]
            topCon.addAttr('anim_opacity',min=0,max=1,dv=0.5,k=True)
            for shader in shaders:
                for at in ['R','G','B']: topCon.anim_opacity >> shader.attr('transparency' + at) 

        else:
            rigs = [self.rig]
            for all in rigs:
                if all.hasAttr('connected_to'): rigs += pm.listConnections(all.connected_to)
            root_rig = rigs[-1]
            shaders = pm.listConnections(root_rig.shaders)
            
        #Connections
        mu.con_link(shaders,self.rig,'shaders')
        
        #Import the Anim Shapes and Assign the Texture
        thisDir = os.path.dirname(mc.file(q=1, loc=1))
        if os.path.exists(thisDir+'/animShapes.ma') == True:
            #Imports modified anims from animShapes file
            self.import_anim_shapes()
            for anim in anims:
                if pm.objExists(anim + '_new') == True:
                    try: self.swap_shapes((anim + '_new'),anim)
                    except: print anim
            pm.delete('anims')
        list(set(anims))
        self.anim_shape_shaders(anims)
        pm.select(cl=True)
        
    def anim_shape_shaders(self,anims):
        for anim in anims:
            anim.addAttr('animNode',at = 'message')
            anim.overrideEnabled.set(1)
            shaders = pm.listConnections(self.rig.shaders)
            oc , s = 6 , 0
            if anim.startswith('left'): oc , s = 18, 1
            elif anim.startswith('right'): oc , s = 13, 2
            anim.overrideColor.set(oc)
            shapes = anim.getChildren(s=True)
            for shape in shapes:
                shape.rename(anim + 'Shape')
                if pm.objectType(shape) in ['nurbsSurface','mesh']:
                    attr_list = ['primaryVisibility','castsShadows','aiVisibleInDiffuseReflection',
                                 'aiVisibleInSpecularReflection','aiVisibleInDiffuseTransmission',
                                 'aiVisibleInSpecularTransmission','aiVisibleInVolume',
                                 'aiVisibleInDiffuse','aiOpaque','aiVisibleInGlossy',
                                 'visibleInReflections','visibleInRefractions',
                                 'receiveShadows','aiSelfShadows','motionBlur']
                    for attribute in attr_list:
                        try: shape.attr(attribute).set(0)
                        except: print 'error ' + attribute
                    pm.select(shape)
                    pm.hyperShade(assign = shaders[s])
                    pm.select(cl=True)
        pm.refresh()
    
    def import_anim_shapes(self):
        thisDir = os.path.dirname(mc.file(q=1, loc=1))
        mc.file((thisDir+'\\animShapes.ma'),i = True)
        pm.PyNode('anims').visibility.set(0)
        new_shapes = pm.listRelatives('anims',s=False)
        for new_shape in new_shapes: new_shape.rename(new_shape + '_new')
    
    def swap_shapes(self,new,anim):
        new = pm.PyNode(new)
        pm.parent(new,anim)
        pm.makeIdentity(new,a=True,t=True,r=True,s=True)
        pm.delete(anim.getChildren(s=True))
        pm.parent(new.getChildren(s=True),anim,r=True,s=True)
        pm.delete(new)
        pm.refresh()