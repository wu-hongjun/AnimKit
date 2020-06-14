from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Anim_Shaders():
    def __init__(self,rig):
        #Variables
        self.rig = PyNode(rig)
        anims = []
        
        #Create Shaders
        if not self.rig.hasAttr('connected_to'):
            center_shader = shadingNode('lambert',n = ('center_' + self.rig.character_name.get() + '_anim_shader'),asShader=True)
            left_shader = shadingNode('lambert',n = ('left_' + self.rig.character_name.get() + '_anim_shader'),asShader=True)
            right_shader = shadingNode('lambert',n = ('right_' + self.rig.character_name.get() + '_anim_shader'),asShader=True)
            shaders = [center_shader,left_shader,right_shader]
            center_shader.color.set(0,0,1)
            left_shader.color.set(0,0.75,1)
            right_shader.color.set(1,0,0)
            topCon = listConnections(self.rig.topCon)[0]
            topCon.addAttr('anim_opacity',min=0,max=1,dv=0.5,k=True)
            for shader in shaders:
                topCon.anim_opacity >> shader.transparencyR
                topCon.anim_opacity >> shader.transparencyG
                topCon.anim_opacity >> shader.transparencyB

        else:
            rigs = [self.rig]
            for all in rigs:
                if all.hasAttr('connected_to'): rigs += listConnections(all.connected_to)
            root_rig = rigs[-1]
            shaders = listConnections(root_rig.shaders)

        
        #Connections
        connect_objs_to_node(shaders,rig,'shaders')
        
        #Get all anims
        nodes = listConnections(self.rig.connected_networks)
        for node in nodes:
            if node.hasAttr('anims') == True:
                anims += listConnections(node.anims)
            if node.hasAttr('switch') == True:
                anims += listConnections(node.switch)
        
        thisDir = os.path.dirname(mc.file(q=1, loc=1))
        if os.path.exists(thisDir+'/animShapes.ma') == True:
            #Imports modified anims from animShapes file
            self.import_anim_shapes()
            
            #Swaps the anim shapes with the new ones and colors the anims
            '''Texture will be added later for anims shapes geometry'''
            
            for anim in anims:
                if objExists(anim + '_new') == True:
                    try: self.swap_shapes((anim + '_new'),anim)
                    except: pass
            delete('anims')
        self.anim_shape_shaders(anims)
        select(cl=True)
        
    def anim_shape_shaders(self,anims):
        for anim in anims:
            anim.overrideEnabled.set(1)
            items = anim.split('_')
            shaders = listConnections(self.rig.shaders)
            s = 0
            oc = 6
            if items[0] == 'left':
                oc = 18
                s = 1
            elif items[0] == 'right':
                oc = 13
                s = 2
            anim.overrideColor.set(oc)
            shapes = anim.getChildren(s=True)
            for shape in shapes:
                shape.rename(anim + 'Shape')
                if objectType(shape) in ['nurbsSurface','mesh']:
                    attr_list = ['primaryVisibility','castsShadows','aiVisibleInDiffuseReflection',
                                 'aiVisibleInSpecularReflection','aiVisibleInDiffuseTransmission',
                                 'aiVisibleInSpecularTransmission','aiVisibleInVolume',
                                 'aiVisibleInDiffuse','aiOpaque','aiVisibleInGlossy',
                                 'visibleInReflections','visibleInRefractions',
                                 'receiveShadows','aiSelfShadows','motionBlur']
                    for attribute in attr_list:
                        try:
                            shape.attr(attribute).set(0)
                            print attribute
                        except: print 'error ' + attribute
                    select(shape)
                    hyperShade(assign = shaders[s])
                    select(cl=True)
        refresh()
    
    def import_anim_shapes(self):
        thisDir = os.path.dirname(mc.file(q=1, loc=1))
        mc.file((thisDir+'\\animShapes.ma'),i = True)
        PyNode('anims').visibility.set(0)
        new_shapes = listRelatives('anims',s=False)
        for new_shape in new_shapes:
            new_shape.rename(new_shape + '_new')
    
    def swap_shapes(self,new,anim):
        new = PyNode(new)
        parent(new,anim)
        makeIdentity(new,a=True,t=True,r=True,s=True)
        delete(anim.getChildren(s=True))
        parent(new.getChildren(s=True),anim,r=True,s=True)
        delete(new)
        refresh()