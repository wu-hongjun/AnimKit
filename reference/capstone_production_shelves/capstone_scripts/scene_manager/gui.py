from pymel.core import *
from metaCore import *

from scene_manager.methods import *

import os
import random
import pymel.core.animation as annie
import glob as glob
import maya.mel as mel
import subprocess

PRODUCTION_SERVER = "capstone1"


'''
Main Manager class
'''
class SceneWindow:
    def __init__(self):
        if window("sceneManagerWindow", q =1, exists = 1):
            deleteUI('sceneManagerWindow')

        manager = window("sceneManagerWindow",title = "Scene Manager")
        self.tabs = tabLayout('tabs')
        self.scenePanel = self.createScenePanel(self.tabs)
        self.lightPanel = self.createLightPanel(self.tabs)
        self.geometryPanel = self.createGeometryPanel(self.tabs)
        window(manager, e =1, width = 700, height = 800)
        showWindow(manager)
            
#==================SCENE PANEL====================
    def createScenePanel(self, parentPanel):
        '''
        creates a panel for the scene manager nodes and basic file options
        
        parentPanel:
            the parent of the panel created
            
        returns
            the top level layout created
        '''
        setParent(parentPanel)
        panel = columnLayout('scene', adj =1)
        label = text(label = 'Scene Manager')
        saveIter = button(label = 'Save Iteration', command = lambda *args: saveIterWindow())
        createScene = button(label = 'create Scene Meta Node', command = 'print("Not Implemented")')
        update = button(label = 'update', command = 'print("Not Implemented")')
        
        return panel
        

#================LIGHT PANEL=========================

    
    def createLightPanel(self,parentPanel):
        '''
        creates a panel for all the lights connected to lightGroups in the scene
        
        parentPanel:
            the parent to the panel created
            
        return:
            the top level layout created
        '''
        setParent(parentPanel)
        lightGroups = getMetaNodesOfType('LightGroup')
        scroll = scrollLayout('Lights')
        panel = columnLayout(adj=1)
        updateBut = button(label = "update", c = lambda *args: self.updateLights())
        batchBut = button(label = 'Batch Lights', c = lambda *args: BatchLightWindow()) 
        for group in lightGroups:
            self.createLightGroupPanel(panel, group)
        return scroll
        
            
    def createLightGroupPanel(self,parentPanel, meta):
        '''
        creates a panel for the Lightgroup and its options
        
        meta:
            the lightGroup meta node
        
        parentPanel:
            the parent to the panel created
            
        return:
            the top level layout created
        '''
        setParent(parentPanel)
        groupName = meta.groupName.get()
        width = parentPanel.getWidth()
        height = parentPanel.getHeight()
        frame = frameLayout(groupName,label = '%s_lights'%(groupName),collapsable = 1, cl = 1)
        panel = columnLayout('%s_lights_panel'%groupName)
        
        setParent(panel)
        keysFrame = frameLayout(label = 'keys',collapsable = 1, cl = 1)
        keys = listConnections(meta.keys)
        keysPanel = columnLayout('%s_keys'%(groupName),adj =1)
        self.createLightGroupOptionsPanel(keysPanel,meta,'keys')
        for keyLight in keys:
            self.createLightOptionsPanel(keysPanel, keyLight, meta, 'keys')
        
        setParent(panel)
        fillsFrame = frameLayout(label = 'fills',collapsable = 1, cl = 1)
        fills = listConnections(meta.fills)
        fillsPanel = columnLayout('%s_fills'%(groupName), w = width, h = height)
        self.createLightGroupOptionsPanel(fillsPanel,meta,'fills')
        for fillLight in fills:
            self.createLightOptionsPanel(fillsPanel, fillLight, meta, 'fills')
        
        setParent(panel)
        rimsFrame = frameLayout(label = 'rims',collapsable = 1, cl = 1)
        rims = listConnections(meta.rims)
        rimsPanel = columnLayout('%s_rims'%(groupName),w = width, h = height)
        self.createLightGroupOptionsPanel(rimsPanel,meta,'rims')
        for rimLight in rims:
            self.createLightOptionsPanel(rimsPanel, rimLight, meta, 'rims')
        
        setParent(panel)
        othersFrame = frameLayout(label = 'others',collapsable = 1, cl = 1)
        others = listConnections(meta.others)
        othersPanel = columnLayout('%s_others'%(groupName),w = width, h = height)
        self.createLightGroupOptionsPanel(othersPanel,meta,'others')
        for otherLight in others:
            self.createLightOptionsPanel(othersPanel, otherLight, meta, 'others')
        
        return panel
    
        
    def createLightGroupOptionsPanel(self, parentPanel, networkNode, groupName):
        '''
        creates a group with options for the lightGroup MetaNode for groupName
        
        networkNode:
            the lightGroup for the options
            
        groupName:
            the name of the lights, example: "keys" "fills" "rims" "others"
        
        parentPanel:
            the parent to the panel created
            
        return:
            the top level layout created
        '''
        setParent(parentPanel)
        lg = LightGroup('', node = networkNode)
        panel = rowLayout(nc = 6, ct6 = ['both','both','both','both','both','both'] )
        addSpot = button(label = "add Spot", c = lambda *args: lg.addLightToGroup(lg.createLightByType('spot'), groupName))
        addPoint = button(label = "add Point", c = lambda *args: lg.addLightToGroup(lg.createLightByType('point'), groupName))	
        addDirectional = button(label = "add Directional", c = lambda *args: lg.addLightToGroup(lg.createLightByType('directional'), groupName))
        addArea = button(label = "add Area", c = lambda *args: lg.addLightToGroup(lg.createLightByType('area'), groupName))
        addVolume = button(label = "add Volume", c = lambda *args: lg.addLightToGroup(lg.createLightByType('volume'), groupName))
        addSelected = button(label = "add selected", c = lambda *args: lg.addSelectedLightsToGroup(ls(sl=1), groupName))
        return panel
        
    
    def createLightOptionsPanel(self,parentPanel, light, networkNode, group):
        '''
        creates a panel for all option for a light
        
        networkNode:
            the networkNode that the light is connected to
            
        group:
            the name of the group that the light belongs to
    
        parentPanel:
            the parent to the panel created
            
        return:
            the top level layout created
        '''
        setParent(parentPanel)
        lg = LightGroup('', node = networkNode)
        light = PyNode(light)
        panel = rowLayout('%s_%s_row'%(light, networkNode.groupName.get()), nc= 4, cw4 = [300,125,75,75], ct4 = ['left', 'both', 'both', 'both'])
        named = nameField(object = light, width = 300)
        lookButton = button(label = 'Look Through Light', c = lambda *args: self.lookThroughObject(light) )
        selectButton = button(label = "Select Light", c = lambda *args: select(light, add =1 ))
        deleteButton = button(label = 'delete Light', c = lambda *args: lg.RemoveLightFromGroup(light, group))
        
        return panel 	
    
    
    def updateLights(self):
        '''
        updates the light panels
        '''
        deleteUI(self.lightPanel)
        self.lightPanel = self.createLightPanel(self.tabs)
        setFocus(self.lightPanel)		

#====================== GEOMETRY GROUP =======================
    
    def createGeometryPanel(self,parentPanel):
        '''
        creates a panel for all the GeometryGroups metaNodes in the scene file
        
        parentPanel:
            the parent to the panel created
            
        return:
            the top level layout created
        '''
        setParent(parentPanel)
        geoGroups = getMetaNodesOfType('GeometryGroup')
        scroll = scrollLayout('Geometry')
        panel = columnLayout(adj=1)
        updateBut = button(label = "update", c = lambda *args: self.notImplemented())
        for meta in geoGroups:
            self.createGeoGroupPanel(panel, meta)
        return scroll
        
        
    
    def createGeoGroupPanel(self, parentPanel, meta):
        '''
        creates a panel for the GeometryGroup node
        
        meta:
            the GeometryGroup node
        
        parentPanel:
            the parent to the panel created
            
        return:
            the top level layout created
        '''
        setParent(parentPanel)
        gg = GeometryGroup('', node = meta)
        frameLayout(gg.getGroupName(), collapsable = 1, cl = 1 )
        panel = columnLayout(adj=1)
        row = rowLayout(nc = 5, ct5 = ['both', 'both','both', 'both','both'], cl5 = ['left', 'left','left', 'left', 'left'])
        hideAllButton = button(label = 'hide all', c = lambda *args: gg.hideAllGeo())
        showAllButton = button(label = 'show all', c = lambda *args: gg.showAllGeo())
        lowAllButton = button(label = 'low Res', c = lambda *args: gg.makeLowGeo())
        hiAllButton = button(label = 'high Res', c = lambda *args: gg.makeHighGeo())
        addButton = button(label = "add Res Group", c = lambda *args: self.addGeometryResGroup(meta))
        for resgroup in gg.getResGroups():
            self.createGeoResPanel(panel, resgroup)
        return panel
    
        
    
    def createGeoResPanel(self, parentPanel, meta):
        '''
        creates a panel for all the GeometryResGroup
        
        meta:
            the GeometryResGroup metaNode
        
        parentPanel:
            the parent to the panel created
            
        return:
            the top level layout created
        '''
        setParent(parentPanel)
        panel = rowLayout(nc = 5, ct5 = ["both" ,'both', 'both', 'both', 'both'], cw5 = [200,100,50,200,100], cl5 = ['left','left' ,'left', 'left', 'left'])
        label = text(label = meta.getGroupName())
        ren = button(label = 'REN', c = lambda *args: self.renameGroup(meta))
        resLabel = text(label = 'Res')
        hilow = radioButtonGrp( labelArray2 = ['Low', 'Hi'], cl2 = ['both','both'], numberOfRadioButtons= 2, on1 = lambda *args: meta.setToLow(), on2 = lambda *args: meta.setToHigh())
        radioButtonGrp(hilow, edit =1 , select = meta.isHighRes()+1)
        vischeck = checkBox(label = 'vis', align = 'left', cc = lambda *args: meta.toggleVis(), value = meta.isVisible())
        return panel
        
    def addGeometryResGroup(self, meta):
        '''
        creates a window for the user to fill out to add a GeometryResGroup
        
        meta:
            the GeometryGroup meta node to add the GeometryResGroup	
        
        '''
        geoGrp = GeometryGroup('',node = meta)
        if window('CreateResGroup', q =1, exists = 1):
            deleteUI('CreateResGroup')
        win = window('CreateResGroup', title = 'add Res Group')
        columnLayout()
        
        nameLabel = text(label = 'Res Group Name: ')
        name = textField()
                    
        lowGeoLabel = text(label = 'Low Poly Geo')
        lowGeo = textField()
        loadLow = button(label = 'Load Sel', c = lambda *args: self.loadFromSelection(lowGeo))
        
        highGeoLabel = text(label = 'High Poly Geo')
        highGeo = textField()
        loadHigh = button(label = 'Load Sel', c = lambda *args: self.loadFromSelection(highGeo))
        
        create = button(label = 'Create', c = lambda *args: self.createResGroup(geoGrp, lowGeo, highGeo, name, win))
        
        showWindow(win)
    
    
    def loadFromSelection(self, field):
        '''
        helper method to other panels, load selection into the text of the field given
        
        field:
            the textfield to add the selection name to 
        '''
        geo = ls(sl=1)[0]
        if geo:
            textField(field, edit =1, text = geo.name())	

    
    def createResGroup(self, geoGrp, lowTextField, highTextField, nameTextField, win):
        '''
        helper method to addResGroup, uses panel info to create the ResGroup
        '''
        lowGeo = textField(lowTextField, q=1, text=1)
        highGeo = textField(highTextField, q=1, text =1)
        gn = textField(nameTextField, q=1, text =1)
        if lowGeo and highGeo and gn:
            if objExists(lowGeo) and objExists(highGeo):
                grg = GeometryResGroup(gn, low = lowGeo, high = highGeo)
                geoGrp.addResGroup(grg)
        deleteUI(win)
        
    
    def renameGroup(self, meta):
        '''
        rename the GeometryResGroup groupName
        
        meta:
             the GeometryResGroup  
        '''
        result = cmds.promptDialog(
            title='Rename Res Group',
            message='Enter Name:',
            button=['Rename', 'Cancel'],
            defaultButton='Rename',
            cancelButton='Cancel',
            dismissString='Cancel')
    
        if result == 'Rename':
            text = cmds.promptDialog(query=True, text=True)
            if text:
                meta.renameGroup(text)
            
            

#=============================MISC ===============================	


    
    def lookThroughObject(self,obj):
        '''
        creates a perspective window with the objects view as the camera
        
        obj:
            the object that will be looked through
            
        retrurn:
            returns the window created
        '''
        app = window(width = 600, height = 800)
        paneLayout()
        objView = modelPanel()
        lookThru(objView, obj)
        showWindow(app)
        return app
    
            
    def notImplemented(self):
        '''
        creates a window with the words "not yet implemented", good for testing code until implemeneted correctly
        
        return:
            the window that contains the words
        '''
        app = window(width = 600, height = 100)
        columnLayout()
        label = text(label = 'not yet implemented')
        showWindow(app)
        return app

        
        
        
        
        
class BatchLightWindow:
    def __init__(self):
        sel = ls(sl=1)
        types = ["volumeLight","areaLight","spotLight","pointLight", "directionalLight","ambientLight"]
        lights = []
        for obj in sel:
            if obj.getShape().type() in types or obj.type() in types:
                lights.append(obj)
    
        if window('BatchLights', q =1, exists = 1):
            deleteUI('BatchLights')
        win = window('BatchLights', title = 'Batch Lights')
        panel = columnLayout(adj =1)
        
        #color
        colorRow = rowLayout(nc = 4, ct4 = ['left','left','left','left'], cw4 = [50,400,100,100])
        colorChange = checkBox(label = '')
        color = colorSliderGrp( label='Color: ', rgb=(1, 1, 1))
        colorAdd = checkBox(label = 'add')
        colorClamp = checkBox(label = 'clamp')
        setParent(panel)
        
        #intensity
        intenRow = rowLayout(nc = 5)
        intenChange = checkBox(label = '')
        intenLabel = text("Intensity: ")
        intenField = floatField()
        intenAdd = checkBox(label = 'add')
        intenPercent = checkBox(label = 'percent')
        setParent(panel)
        
        #dropoff
        dropoffRow = rowLayout(nc = 6)
        dropOffLabel = text(label = 'Drop Off:')
        dropOff = radioCollection()
        dod = radioButton( label='No Change' )
        radioButton( label='No Decay', align='left' )
        radioButton( label='Linear', align='left' )
        radioButton( label='Quadratic', align='left' )
        radioButton( label='Cubic', align='left' )
        radioCollection(dropOff, e=1, select = dod)
        setParent(panel)
        
        #penumbra
        penumbraRow = rowLayout(nc = 5)
        penChange = checkBox(label = '')
        penumbraLab = text(label = 'Penumbra')
        penumbra = floatField()
        penAdd = checkBox(label = 'add')
        penPercent = checkBox(label = 'percent')
        setParent(panel)
        
        #emits by defualt
        emitsDRow = rowLayout(nc = 4)
        emitsDefLabel = text(label = 'Emits by Default: ')
        emitsDefault = radioCollection()
        edd = radioButton(label = 'No Change')
        radioButton(label = 'Yes')
        radioButton(label = 'No')
        radioCollection(emitsDefault, e=1, select = edd)
        setParent(panel)
        
        #emits spec
        specRow = rowLayout(nc = 4)
        emitsSpecLabel = text(label = 'Emits Specular: ')
        emitsSpecular = radioCollection()
        esd = radioButton(label = 'No Change')
        radioButton(label = 'Yes')
        radioButton(label = 'No')
        radioCollection(emitsSpecular, e=1, select = esd)
        setParent(panel)
        
        #Light Links
        linkRow = rowLayout(nc = 7)
        text(label = 'Light Links:')
        linkCol = radioCollection()
        linkNC = radioButton(label = 'No Change')
        radioButton(label = 'Make')
        radioButton(label = 'Break')
        radioCollection(linkCol, e=1, select = linkNC)
        setParent(linkRow)
        text(label = 'objs:')
        linkField = textField()
        button(label = 'Load Selection', c = lambda *args: self.loadSelection(linkField))
        setParent(panel)
        
        
        #duse depth map
        depthRow = rowLayout(nc = 4)
        depthLabel = text(label = 'Use Depth Map Shadows: ')
        useDepth = radioCollection()
        udd = radioButton(label = 'No Change')
        radioButton(label = 'Yes')
        radioButton(label = 'No')
        radioCollection(useDepth, e=1, select = udd)
        setParent(panel)
                
        #shadow Color
        shadowColorRow = rowLayout(nc = 4, ct4 = ['left','left','left','left'], cw4 = [50,400,100,100])
        shadowColorChange = checkBox(label = '')
        shadowColor = colorSliderGrp( label='ShadowColor: ', rgb=(1, 1, 1))
        shadowColorAdd = checkBox(label = 'add')
        shadowColorClamp = checkBox(label = 'clamp')
        setParent(panel)
        
        #shadow Resolution
        resRow = rowLayout(nc = 3)
        resChange = checkBox(label = '')		
        resLabel = text("Shadow Resolution: ")
        resField = floatField()
        setParent(panel)
        
        #filter size
        filterRow = rowLayout(nc = 4)
        filterChange = checkBox(label = '')
        filterSizeLabel = text("Shadow Filter Size: ")
        filterField = floatField()
        filterAdd = checkBox(label = 'add')
        setParent(panel)
        
        batchBut = button(label = "Batch", c = lambda *args: self.batchLightsCommand(	lights, colorChange, color,colorAdd, colorClamp, intenChange, intenField, intenAdd, intenPercent, 
                                                                                        dropOff, emitsDefault,emitsSpecular, penChange, penumbra, penAdd, penPercent, useDepth,shadowColorChange, shadowColor, 
                                                                                        shadowColorAdd, shadowColorClamp, resChange, resField, filterChange, filterField, filterAdd, linkCol, linkField))
        showWindow(win)

    
    
    def batchLightsCommand(	self, lights, colorChange, color,colorAdd, colorClamp, intenChange, intenField, intenAdd, intenPercent, 
                            dropOff, emitsDefault,emitsSpecular, penChange, penumbra, penAdd, penPercent, useDepth,shadowColorChange, shadowColor, 
                            shadowColorAdd, shadowColorClamp, resChange, resField, filterChange, filterField, filterAdd, linkCol, linkField):
        '''
        helper method to the batchLights method, takes the info from the batchLights panel and updates the lights
        '''					
                            
        linkText = textField(linkField, q=1, text=1)
        linkLights = []
        if linkText:
            linkLights = linkText.split(",")
            print linkLights
            linkLights  = map(lambda obj: PyNode(obj), linkLights)
        lights = map(lambda obj: PyNode(obj), lights)
        
        for light in lights:
            #color 
            cch = checkBox(colorChange, q=1, value = 1)
            if cch:
                cA = checkBox(colorAdd, q=1, value = 1)
                cCL = checkBox(colorClamp, q=1, value = 1)
                colorRGB = colorSliderGrp(color, q=1, rgb = 1)
                
                if cA:
                    lcolor = light.color.get()
                    light.color.set([lcolor[0] + colorRGB[0],lcolor[1] + colorRGB[1],lcolor[2] + colorRGB[2]])
                else:
                    light.color.set(colorRGB)
                
                print cCL
                print colorRGB
                if cCL:
                    cr = light.colorR.get()
                    if cr < 0: light.colorR.set(0)
                    if cr > 1: light.colorR.set(1)
                    
                    cg = light.colorG.get()
                    if cg < 0: light.colorG.set(0)
                    if cg > 1: light.colorG.set(1)
                    
                    cb = light.colorB.get()
                    if cb < 0: light.colorB.set(0)
                    if cb > 1: light.colorB.set(1)
                
            #intensity		
            ich = checkBox(intenChange, q=1, value =1)
            if ich:
                inten = floatField(intenField, q =1, value =1)
                iA = checkBox(intenAdd, q=1, v =1)
                iPer= checkBox(intenPercent, q=1, v=1)
                linten = light.intensity.get()
                
                if iA:
                    if iPer:
                        light.intensity.set(inten*.01 * linten + linten)
                    else:
                        light.intensity.set(inten + linten)
                else:
                    if iPer:
                        light.intensity.set(inten*.01*linten)
                    else:
                        light.intensity.set(inten)	
            
            #light decay rate
            dropoff_types = ["spotLight", 'pointLight', 'areaLight']	
            if light.getShape().type() in dropoff_types:	
                dropoff_index = radioCollection(dropOff, q=1, select =1)
                dropoff_name = radioButton(dropoff_index, q=1, label = 1)
                dropoff_dict = {'No Decay': 0, 'Linear':1, 'Quadratic':2, 'Cubic':3}
                if dropoff_name in dropoff_dict.keys():
                    light.decayRate.set(dropoff_dict[dropoff_name])
            
            #light Linking
            llindex = radioCollection(linkCol, q=1, select =1)
            llname = radioButton(llindex, q=1, label = 1)
            if llname == 'Make':
                lightlink(make=1, object = linkLights, light = light)
            elif llname == 'Break':
                lightlink(b=1, object = linkLights, light = light)
                
            #emits by defualt		
            emitsDefault_index = radioCollection(emitsDefault, q=1, select =1)
            ed_name = radioButton(emitsDefault_index, q =1, label =1)
            if ed_name == 'Yes':
                connectAttr(light.instObjGroups ,PyNode('defaultLightSet').dagSetMembers, nextAvailable = 1, f=1)
                print 'connected default lights'
            elif ed_name == 'No':
                list = listConnections(light.instObjGroups, s = 0, d = 1)
                i = 0
                for obj in list:
                    if obj.name() == 'defaultLightSet':
                        disconnectAttr(light.attr('instObjGroups[%i]'%i))
                        print 'disconnected defaults'
                    i += 1	
                print 'NO LIGHT DELINKED'
                
                
            #emits specular   NOT IMPLEMENTED
            if light.hasAttr('emitSpecular'):
                emitsSpec_index = radioCollection(emitsSpecular, q=1, select =1)
                es_name = radioButton(emitsSpec_index, q =1, label =1)
                es_dict = {'Yes':1, 'No': 0}
                if es_name in es_dict.keys():
                    light.emitSpecular.set(es_dict[es_name])
            
            #penumbra
            if light.hasAttr('penumbraAngle'):
                pch = checkBox(penChange, q=1, value =1)
                if pch:
                    pen = floatField(penumbra, q =1, value =1)
                    pA = checkBox(penAdd, q=1, v =1)
                    pPer= checkBox(penPercent, q=1, v=1) 
                    lpen = light.penumbraAngle.get()
                    
                    if pA:
                        if pPer:
                            light.penumbraAngle.set(lpen *.01* pen + lpen)
                        else:
                            light.penumbraAngle.set(lpen + pen)
                    else:
                        if pPer:
                            light.penumbraAngle.set(lpen * .01 *pen)
                        else:
                            light.penumbraAngle.set(pen)
                        
            #use depth map shadows
            if light.hasAttr('useDepthMapShadows'):
                udepth_index = radioCollection(useDepth, q=1, select =1)
                udepth_name = radioButton(udepth_index, q =1, label =1)
                udepth_dict = {'Yes':1, 'No': 0}
                if udepth_name in udepth_dict.keys():
                    light.useDepthMapShadows.set(udepth_dict[udepth_name])	
                
            #shadow colors
            if light.hasAttr('shadowColor'):
                scch = checkBox(shadowColorChange, q=1, value = 1)
                if scch:
                    scA = checkBox(shadowColorAdd, q=1, value = 1)
                    scCL = checkBox(shadowColorClamp, q=1, value = 1)
                    scRGB = colorSliderGrp(shadowColor, q=1, rgb = 1)
                    
                    if scA:
                        lscolor = light.shadowColor.get()
                        light.color.set([lscolor[0] + scRGB[0],lscolor[1] + scRGB[1],lscolor[2] + scRGB[2]])
                    else:
                        light.shadowColor.set(scRGB)
                    
                    if scCL:
                        scr = light.shadowColorR.get()
                        if scr < 0: light.shadowColorR.set(0)
                        if scr > 1: light.shadowColorR.set(1)
                        
                        scg = light.shadowColorG.get()
                        if scg < 0: light.shadowColorG.set(0)
                        if scg > 1: light.shadowColorG.set(1)
                        
                        scb = light.shadowColorB.get()
                        if scb < 0: light.shadowColorB.set(0)
                        if scb > 1: light.shadowColorB.set(1)
            
            #shadow Resolution
            if light.hasAttr('dmapResolution'):
                if resChange:
                    if light.hasAttr('dmapResolution'):
                        res = floatField(resField, q =1, value =1)
                        res_sizes = [128,256,512,1024,2048,4096]
                        if res in res_sizes:
                            light.dmapResolution.set(res)
            
            #shadow filter
            if light.hasAttr('dmapFilterSize'):
                filterCh = checkBox(filterChange,q=1, value=1)
                if filterCh:
                    filt = floatField(filterField, q =1, value =1)
                    fA = checkBox(filterAdd, q=1, v =1)
                    
                    if fA:
                        lfs = light.dmapFilterSize.get()	
                        light.intensity.set(filt + lfs)
                    else:
                        light.dmapFilterSize.set(lfs)
    
                                            
    def loadSelection(self, field):
        '''
        load selection into the given text field
        field:
            textfield to add the selection to
        '''
        sel = ls(sl=1)
        tex = ''
        for obj in sel:
            tex += "," + obj.name()
        tex = tex.replace(",","",1)
        textField(field, e=1, text=tex)
        
        
                        
class saveIterWindow():
    def __init__(self):
        if window('saveIter', q =1, exists = 1):
            deleteUI('saveIter')
        win = window('saveIter', title = 'Save Iteration')
        panel = columnLayout(adj =1)
        text(label = "Iteration Notes")
        iterText = textField()
        textField(iterText, e=1, enterCommand = lambda *args: self.saveIteration(iterText, win))
        button(label = 'save', c = lambda *args: self.saveIteration(iterText, win))
        showWindow(win)
        
        
    def saveIteration(self, iterField, win):
        '''
        helper method for when button is pressed
        '''
        updateNotes = textField(iterField, q=1, text=1)
        sn = sceneName()
        dir = sn.parent
        name = sn.replace(dir + '/', '').replace('.ma', '').replace('.mb','')
        iterDir = dir + '/iterations'
        if not iterDir.exists():
            iterDir.mkdir() 
        
        iterFiles = iterDir.files('*.ma')
        numFiles = len(iterFiles)
        iterFileName = '%s/%s_v%i.ma'%(iterDir, name, numFiles)
        
        notes = file(dir + "/notes.txt", mode = 'a')
        curTime = time.strftime("%a, %B %d %Y @ %H:%M:%S")
        notes.write('\r\n%s = %s :: %s'%(numFiles, curTime,updateNotes))
        notes.close()
        
        saveAs(iterFileName, f=1, type='mayaAscii')
        saveAs(sn, f=1, type = 'mayaAscii')
        deleteUI(win)


class UVWindow():
    def __init__(self):
        if window('UVs', q =1, exists = 1):
            deleteUI('UVs')
        win = window('UVs', title = 'Move UVs', sizeable = False)
        panel = columnLayout(adj =1)
        umber = None
        row1 = rowLayout(nc = 3, ct3 = ['both','both','both'] )
        mirrorU = button(label = 'Mirror right/left', c= lambda *args:polyFlipUV(flipType = 0, local = 1 ))
        moveUp = button(label = '/\\', c = lambda *args: self.moveUVs('up', number))
        mirrorV = button(label = 'Mirror up/down', c = lambda *args: polyFlipUV(flipType = 1, local = 1 ))

        setParent(panel)
        row2 = rowLayout(nc = 3, ct3 = ['both','both','both'] )
        moveLeft = button(label = '<<', c= lambda *args: self.moveUVs('left', number))
        number = textField(text = '1')
        moveRight = button(label = '>>', c = lambda *args: self.moveUVs('right', number))
        
        setParent(panel)
        row3 = rowLayout(nc = 3, ct3 = ['both','both','both'] )
        blank = button(label = 'normalize', c = lambda *args: polyNormalizeUV(normalizeType = 1, preserveAspectRatio = 0))
        moveDown = button(label = '\\/', c= lambda *args: self.moveUVs('down', number))
        unfoldBut = button(label = 'unfold', c = lambda *args:unfold(i=5000, ss= .001,gb=0,ps=0,pub=1,oa=0,us=0))
        showWindow(win)
    
            
    def moveUVs(self, direction, number):
        """
        move the selected UV's  in the direction and distance as given
        direction:
            the direction to move in, up down right or left
        number:
            the textField with the will contain the amount to move
        """	
        #get input field
        st = textField(number, q=1, text=1)
        num = 0
        try:
            num = float(st)
        except:
            pass	
        if direction == 'up':
            polyEditUV(v = num)
        elif direction == 'down':
            polyEditUV(v = -num)
        elif direction == 'right':
            polyEditUV(u = num)
        else: #left
            polyEditUV(u = -num)


            
class MultiConstraintWindow():
    def __init__(self, character, advanceControls = False):
        
        self.multiConNode = None
        
        for multiNode in getNodeOfTypeForChar(character, 'MultiConstraint'):
            curMult = MultiConstraint(None, None, multiNode.attr('translateBool').get(), multiNode.attr('rotateBool').get(), multiNode)
            if curMult.getChild() == ls(sl=True)[0]:
                self.multiConNode = curMult
        
        if self.multiConNode == None:
            printError("Select a child of a MulitConstraint relationship")
    
        if(window('MultiConstraintWindow', exists=1)):
            deleteUI('MultiConstraintWindow')
            
        self.window = window('MultiConstraintWindow', title = "MultiContraint", s=1)
        if advanceControls:
            self.window.setHeight(325)
            self.window.setWidth(350)
        else:
            window(self.window, e=1, wh=[350,150])
            
        self.mainPanel = formLayout()        
        self.switchOptions = columnLayout(p=self.mainPanel, cw=350, cat=("both", 75), h=120)
        
        # frame = frameLayout(lv=0, p=self.window)
        text(l=str(self.multiConNode.getChild()) + ':', fn='boldLabelFont', p=self.switchOptions)
        parentList = optionMenu(l='Parent List', p=self.switchOptions)
        self.switchList = []
        for item in self.multiConNode.getParents():
            menIt = menuItem(l=item)
            self.switchList.append(menIt)
        alSwChBx = checkBox(l='Align Switch', v=True, p=self.switchOptions)
        self.switchButtons = columnLayout(p=self.mainPanel, cw=120, cat=("both", 0), h=50)
        button(l='Switch!', command=lambda *args: self.switch(checkBox(alSwChBx, q=True, v=True), parentList), p=self.switchOptions, w=75, h=30)
        
        self.bake = horizontalLayout(p=self.mainPanel)
        startField = intField(p=self.bake, ed=0, v=playbackOptions(q=1, min=1))
        endField = intField(p=self.bake, ed=0, v=playbackOptions(q=1, max=1))
        
        # self.mainpPanel.attachControl(self.switchButtons, "top", 0, self.switchOptions)
        # self.mainPanel.attachControl(self.bake, "top", 0, self.switchButtons)
        # self.mainPanel.attachForm(self.bake, "right", 0)
        # self.mainPanel.attachForm(self.bake, "bottom", 0)
        # self.mainPanel.attachNone(self.bake, "bottom")
        # self.mainPanel.attachForm(self.bake, "left", 5)
        # self.mainPanel.attachControl(self.bake, "bottom", 5, self.switchPanel)
        # self.mainPanel.attachControl(self.bake, "top", 5, self.leftPanel)
        
        # button(l='Bake and Switch', command=lambda *args: self.bakeSwitch(), p=col, w=75, h=30)
        if not advanceControls:
            separator(hr=1, w=275, st="in", p=frame)
            text(l='Select Target to Add:', fn='boldLabelFont', p=frame)
            col = columnLayout(co=['both', 50], p=frame, adj=1)
            self.curSelect = text('Add Target', l="[Currently Selected Target]", bgc=(0.5,0.5,0.5), p=col, h=20, w=200)
            job = scriptJob(e=["SelectionChanged", lambda *args: self.changeText()], p=self.window)
            col = columnLayout(co=['both', 111], p=frame, adj=1)
            remList = optionMenu(l='Parent List', p=frame)
            button(l='Add Target!', command=lambda *args: self.addTarget(parentList, remList), p=col, w=75, h=30)
            separator(hr=1, w=275, st="in", p=frame)
            text(l='Remove Target:', fn='boldLabelFont', p=frame)
            self.remList = []
            for item in self.multiConNode.getParents():
                menIt = menuItem(l=item)
                self.remList.append(menIt)
            col = columnLayout(co=['both', 111], p=frame, adj=1)
            button(l='Remove!', command=lambda *args: self.removeTarget(remList), p=col, w=75, h=30)
        showWindow(self.window)
        
    def switch(self, align, menu):
        target = optionMenu(menu, q=True, v=True)
        if self.multiConNode.getChild().isReferenced():
            target = str(target).split(":")[1]
        if align:
            self.multiConNode.alignSwitch(self.multiConNode.getChild(), target)
        else:
            enumInd = self.multiConNode.getChild().attr('multiSwitch').getEnums()[str(target)]
            self.multiConNode.getChild().attr('multiSwitch').set(enumInd)
        select(cl=True)
        select(self.multiConNode.getChild())
        '''deleteUI(self.window)'''
    
    def bakeSwitch(self):
        target = self.switchTo
        if self.multiConNode.getChild().isReferenced():
            target = str(target).split(":")[1]
        if align:
            self.multiConNode.bakeAndSwitch(self.multiConNode.getChild(), target)
        else:
            enumInd = self.multiConNode.getChild().attr('multiSwitch').getEnums()[str(target)]
            self.multiConNode.getChild().attr('multiSwitch').set(enumInd)
        select(cl=True)
        select(self.multiConNode.getChild())
        deleteUI(self.window)
    
    def changeText(self):
        print ""
        selectStr = ""
        if not ls(sl=True):
            selectStr = "Select object to be added as a target"
        else:
            selectStr = str(ls(sl=True)[0])
        text(self.curSelect, e=1, l=selectStr)
    
    def addTarget(self, menu, remMenu):
        target = text(self.curSelect, q=1, l=1)
        if str(target) == "Select object to be added as a target":
            printError("No target selected. Select one object to be an additional parent in the relationship")
        self.multiConNode.addTarget(self.multiConNode.getChild(), target)
        menIt = menuItem(l=target, p=menu)
        self.switchList.append(menIt)
        mentItRm = menuItem(l=target, p=remMenu)
        self.remList.append(mentItRm)      
        
    def removeTarget(self, menu):
        toRemove = optionMenu(menu, q=True, v=True)
        self.multiConNode.removeTarget(self.multiConNode.getChild(), toRemove)
        for item in self.remList:
            if menuItem(item, q=1, l=1) == (toRemove):
                deleteUI(item, mi=1)
                self.remList.remove(item)
        for item in self.switchList:
            if menuItem(item, q=1, l=1) == (toRemove):
                deleteUI(item, mi=1)
                self.switchList.remove(item)
        
        
class EvilWindow():
    def __init__(self):
        """
        Shows the Evil UI
        """
        self.window = None
        self.mainPanel = None	
        self.evilList = None
        self.evil = None
        
        #delete the window if it already exists
        if(window('EvilWindow', exists=1)):
            deleteUI('EvilWindow')
        
        #main window
        self.window = window('EvilWindow', title = "Evil")
        windowHeight = 1000
        windowWidth = 400
        
        #main
        self.mainPanel = columnLayout("body", adj = 1, columnAlign = "center")
        

        #update
        updateButton = button(label = 'Update', c = lambda *args: self.updateEvil())
        
        #evil list
        self.evilList = optionMenu(changeCommand = lambda *args: self.changeEvilFromList())
        self.evilLabel = text(label = 'Current Evil = NONE')
        
        text(label = "", height = 45)		
        separator(style = 'double')
        text(label = "", height = 45)
        
        
        #change attrs
        
        self.growSlider = attrFieldSliderGrp( label = 'Grow', smn=0, smx=50)
        self.rotateSlider = attrFieldSliderGrp(label = 'Rotate', smn = 0, smx = 360)
        self.percentSlider = attrFieldSliderGrp(label = 'Percent', smn = 0, smx = 1 )
        
            
        text(label = "", height = 45)		
        separator(style = 'double')
        text(label = "", height = 45)
        
        #anims
        button(label = 'Select Anims', c = lambda *args: self.selectAnims())
        button(label = 'Key Anims', c = lambda *args: self.keyAnims())
        button(label = 'Randomize Anims', c = lambda *args: self.randomizeAnims())
        randomRow = rowLayout('randomAmountRow',nc=2, cl2 = ['right','left'])
        text(label = 'Random Amount: ')
        self.randomField = floatField(v= 10)
        setParent(self.mainPanel)
        
        
        text(label = "", height = 45)		
        separator(style = 'double')
        text(label = "", height = 45)
        
        #attach 
        setParent(self.mainPanel)
        attachChildRow = rowLayout('setChildRow',nc=2, cl2 = ['right','left'])
        childButton = button(label = 'child', c = lambda *args: self.updateChildField())
        self.attachChildField = textField()
        
        setParent(self.mainPanel)
        attachPercentRow = rowLayout('percentRow',nc=2, cl2 = ['right','left'])
        text(label = 'Percent')
        self.attachPercentField = floatField( minValue=0, maxValue=1, value=.5)
        
        setParent(self.mainPanel)
        button(label = 'attach' , c = lambda *args: self.attachChild())
        button(label = 'detach' , c = lambda *args: self.detachChild())
        
        text(label = "", height = 45)		
        separator(style = 'double')
        text(label = "", height = 45)
        
        #create
        setParent(self.mainPanel)
        curveRow = rowLayout(nc=2, cl2 = ['right','left'])
        curveButton = button(label = 'curve', c = lambda *args: self.updateCurveField())
        self.curveField = textField()
        
        setParent(self.mainPanel)
        radiusRow = rowLayout(nc=2, cl2 = ['right','left'])
        text(label = 'Radius')
        self.radiusField = floatField( minValue=0, value=1)
        
        setParent(self.mainPanel)
        taperRow = rowLayout(nc=2, cl2 = ['right','left'])
        text(label = 'Taper')
        self.taperField = floatField( minValue=0, maxValue=1, value=.1)
        
        setParent(self.mainPanel)
        numJointsRow = rowLayout(nc=2, cl2 = ['right','left'])
        text(label = 'numJoints')
        self.numJointsField = intField( minValue=0, maxValue=150, value=50)
        
        setParent(self.mainPanel)
        button(label = 'Create', c = lambda *args: self.createEvil())
        button(label = 'Recreate', c = lambda *args: self.recreateEvil())
        
        text(label = "", height = 45)		
        separator(style = 'double')
        text(label = "", height = 45)
        
        button(label = 'Delete', c = lambda *args: self.deleteEvil())
            
        #finish
        window(self.window, e=1, rtf=1)
        showWindow(self.window)
        
        #updateEvil
        self.updateEvil()
        
    def setEvil(self, node):
        '''
        sets the evil to the current network node selected
        '''
        if node == None:
            try:
                self.evil.hideAnims()
            except:
                pass
            self.evil = None
            text(self.evilLabel, e=1, label = 'Current Evil = None')
            return
            
        evil = Evil('',node = node)
        
        if self.evil:
            self.evil.hideAnims()
        
        #self.evil		
        self.evil = evil
        self.evil.showAnims()
        
        #change label
        text(self.evilLabel, e=1, label = 'Current Evil = %s'%self.evil.networkNode.name())
        
        #change attrs
        attrFieldSliderGrp(self.growSlider, e=1, en=1, at = evil.getGrowAttr())
        attrFieldSliderGrp(self.rotateSlider, e=1, en = evil.isAttached(), at = evil.getRotateAttr())
        attrFieldSliderGrp(self.percentSlider, e=1, en = evil.isAttached(), at = evil.getPercentAttr())
        
        
        #recreate updates
        
        
    def updateEvil(self):
        '''
        updates evil menus
        '''
        #see if part of an evil is selected, if it is make that the evil
        sel = ls(sl=1)
        if not sel:
            self.updateEvilList()
            
            if not self.evil:
                ev = optionMenu(self.evilList, q=1, value= 1)
                if ev:
                    self.setEvil(ev)	
            return
        
        obj = sel[0]
        evil = None
        try:
            metaParents = obj.metaParent.listConnections()
            for mp in metaParents:
                if isMetaNodeOfType(mp, 'Evil'):
                    evil = mp
        except:
            pass
        if evil:
            self.setEvil(evil)
        else:
            self.updateEvilList()
            
            if not self.evil:
                ev = optionMenu(self.evilList, q=1, value= 1)
                if ev:
                    self.setEvil(ev)	
            return
            
            
        self.updateEvilList()		
                
                     
    def changeEvilFromList(self):
        '''
        switches evil when evil list is changed
        '''
        evil = optionMenu(self.evilList, q=1, value=1);
        try:
            self.setEvil(PyNode(evil))
        except:
            self.updateEvilList(self)
    
            
    def updateEvilList(self):
        '''
        repopulates the  evil list
        '''
        numItems = optionMenu(self.evilList, q=1, numberOfItems=1)
        for inc in xrange(numItems):
            deleteUI("evilListMenuItem" + str(inc));
        
        allEvil = getMetaNodesOfType('Evil')
        if not allEvil:
            self.setEvil(None)
        
        inc = 0
        current = 0
        for node in allEvil:
            evil = Evil('', node = node )	
            try:
                if node == self.evil.networkNode:
                    current = inc+1
            except:
                pass
            menuItem("evilListMenuItem" + str(inc), parent=self.evilList, label=node.name())
            inc +=1
        
        if current:
            optionMenu(self.evilList, e=1, select = current )
    
    def selectAnims(self):
        '''
        select all the current Evils anims
        '''
        try:
            select(self.evil.listAnims())
        except:
            pass
            
        
    def keyAnims(self):
        try:
            self.evil.keyAnims()
        except:
            pass
            
    def randomizeAnims(self):
        '''
        randomize anims by set amount
        '''
        randAmount = floatField(self.randomField, q=1, value=1)
        try:
            self.evil.randomizeAnims(randAmount)
        except:
            pass
        
    
    def updateChildField(self):
        sel = ls(sl=1)
        if len(sel) < 1:	
            return
        obj = sel[0]
        evil = None
        try:
            metaParents = obj.metaParent.listConnections()
            for mp in metaParents:
                if isMetaNodeOfType(mp, 'Evil'):
                    evil = mp
        except:
            pass
        
        textField(self.attachChildField, e=1, text=evil.name())
                    
    def attachChild(self):
        percent = floatField(self.attachPercentField, q=1, value=1)
        evil = textField(self.attachChildField, q=1, text=1)
        print evil
        otherEvil = Evil('',node = evil)
        if self.evil:
            self.evil.attachEvil(otherEvil, percent)
            self.setEvil(otherEvil.networkNode)
        
        
    def detachChild(self):
        otherEvil = Evil('', node = textField(self.attachChildField, q=1, text=1))
        if otherEvil:
            otherEvil.detach()
        self.setEvil(otherEvil.networkNode)
            
    def updateCurveField(self):
        sel = ls(sl=1)
        if not sel:
            return
        
        obj = sel[0]
        if obj.getShape().type() == 'nurbsCurve':
            textField(self.curveField, e=1, text=obj.name())
            
    def createEvil(self):
        curve = textField(self.curveField, q=1, text=1)
        radius = floatField(self.radiusField, q=1, value =1)
        taper = floatField( self.taperField, q=1, value =1)
        numJoints = intField(self.numJointsField, q=1, value =1)
        
        evil = Evil(curve, radius = radius, taper = taper, numJoints = numJoints)
        self.setEvil(evil.networkNode)
        self.updateEvilList()
        
        
    def recreateEvil(self):
        pass
        
    def deleteEvil(self):
        if self.evil:
            self.evil.delete()
            self.setEvil(None)
            self.updateEvil()	



class RigMarkingMenu():
    def __init__(self):
        if (popupMenu("metaMarkingMenu", exists=1)):
            deleteUI("metaMarkingMenu")
        main = popupMenu("metaMarkingMenu",button = 1, ctl = 1, alt =0, sh = 1, allowOptionBoxes =1, parent = "viewPanes", mm=1)
        
        
        sel = ls(sl=1)
        if sel:
            #print "getMetaRoot" in dir()
            character = getMetaRoot(sel[0], 'CharacterRig')
            hasAlignSwitch = getMetaRoot(sel[0], ['FKIKSplineChain','FKIKChain', 'FKIKArm', 'FKIKArm2', 'FKIKLeg', 'FKIKSpine', 'FKIKSplineTail', 'FKIKQuadrupedLeg', 'FKIKLimb', 'FKIKBipedLeg'])
            isHair = getMetaRoot(sel[0], 'FKIKHair')
            hasMultiConstraint = 0
            allMultiConstraints = getNodeOfTypeForChar(character, "MultiConstraint")
            for x in allMultiConstraints:
                multi = fromNetworkToObject(x)
                if attributeQuery('control', node=multi.networkNode, ex=1): #check is to make sure old multiconstraint class doesn't break marking menu on old rigs  using said class
                    if sel[0] == multi.getChild():
                        hasMultiConstraint = multi
            isRigComp = getMetaRoot(sel[0], ['FKChain',"COGChain",'ReverseChain','AdditionalTwist','FKIKSplineChain','FKIKChain', 'SingleIKChain', 'StretchyJointChain', 'FKIKArm', 'FKIKArm2',"FKIKLeg",'FKFloatChain', 'RFKChain', 'ReversePelvis', 'FeatherComponent', 'FKIKSplineTail', 'FKIKQuadrupedLeg', 'FKIKLimb', 'FKIKBipedLeg', 'FlexibleEyelid', 'AnimGroup'])
            isFKIKLeg = getMetaRoot(sel[0], 'FKIKLeg')
            #print character, hasAlignSwitch, hasMultiConstraint, isRigComp
            
            if character:		
                # if isRigComp:
                    #mirror North
                menuItem(label = "Mirror", subMenu=1, enable = 1, rp = "N", allowOptionBoxes = 1)
                menuItem(label = "All Anims: Swap Sides", c= lambda *args:self.mirrorCharacter(character), enable=1, rp = "E", enableCommandRepeat =1)
                menuItem(label = "All Anims: Match Other Side", c= lambda *args:self.mirrorComponentSide(character, isRigComp), enable=1, rp = "W", enableCommandRepeat =1)
                menuItem(label = "Component: Swap Sides", c = lambda *args:self.mirrorBoth(isRigComp), enable =1, rp= "NE", ecr=1)
                menuItem(label = "Component: Match Other Side", c = lambda *args:self.mirrorSelf(isRigComp), enable =1, rp= "NW", ecr=1)
                '''
                if "face" in str(character.networkNode.attr('characterName').get()).lower():
                    menuItem(label = "Side", c = lambda *args:self.mirrorSide(), enable =1, rp= "S", ecr=1)
                '''
                setParent("..",m=1)
            
                #selectAllAnims NorthEast
                menuItem(label = "Select All Anims", c = lambda *args:self.selectAll(character), enable =1, rp="NE", ecr =1) 
                
                #key all East
                menuItem(label = "Key All Anims", c = lambda *args:self.keyAll(character), enable = 1, rp = "E", ecr =1)
        
                #default Pose South
                menuItem(label = "Default Pose", subMenu=1, enable = 1, rp = "S", allowOptionBoxes = 1)
                menuItem(label = "Character", c = lambda *args:self.defaultPoseCharacter(character), enable = 1, rp = "E", ecr = 1)
                menuItem(label = "Self", c = lambda *args:self.defaultPoseSelf(isRigComp), enable = 1, rp = "W", ecr = 1)
                setParent("..",m=1)
                    
            if hasAlignSwitch:			
                #alignSwitch SouthEast
                menuItem(label = "Switch", subMenu=1, enable = 1, rp = "SE", allowOptionBoxes = 1)
                menuItem(label = "Align Switch", c = lambda *args:self.alignSwitch(hasAlignSwitch), enable = 1, rp = "SE", ecr =1)
                menuItem(label = 'Align Switch and Key Before', c= lambda *args: self.alignSwitchAndKeyBefore(hasAlignSwitch), enable = 1, rp = "E", ecr = 1)
                menuItem(label = "Just Switch", c = lambda *args:self.justSwitch(hasAlignSwitch), enable = 1, rp = "SW", ecr =1)
                menuItem(label = "Select Switch", c = lambda *args: self.selectSwitch(hasAlignSwitch), enable = 1, rp = "N", ecr =1)
                setParent("..",m=1)
            
            if isHair:
                menuItem(label = "Hair", subMenu=1, enable = 1, rp = "W", allowOptionBoxes = 1)
                menuItem(label = "Select Base Anim", c = lambda *args:self.selectHairBase(isHair), enable = 1, rp = "S", ecr =1)
                menuItem(label = "FKIK Switch", c = lambda *args:self.hairFKIKSwitch(isHair), enable = 1, rp = "N", ecr =1)
                menuItem(label = "Straight", c = lambda *args:self.straight(isHair), enable = 1, rp = "E", ecr =1)
                menuItem(label = "Select Child Anims", c = lambda *args:self.slChildren(isHair), enable = 1, rp = "W", ecr =1)

            if hasMultiConstraint:
                # print character
                menuItem(label = "MultiConstraint", enable = 1, rp = "W", c= lambda *args: MultiConstraintWindow(character, 1))
                
            menuItem(label = "Rotate", subMenu=1, enable=1, rp="SW", p=main)
            menuItem(label = "Rotate 90 CCW",  c = lambda *args:self.rotateChar(character, 90), enable=1, rp="E", ecr=1)
            menuItem(label = "Rotate 90 CW",  c = lambda *args:self.rotateChar(character, -90), enable=1, rp="W", ecr=1)
            menuItem(label = "Rotate 180 CCW",  c = lambda *args:self.rotateChar(character, 180), enable=1, rp="S", ecr=1)
            menuItem(label = "Rotate 180 CW",  c = lambda *args:self.rotateChar(character, -180), enable=1, rp="N", ecr=1)
            #else:
            #	self.makeMultiConstraintMenu(None, sel[0], 0)
                
            #swap shape SouthWest
            #if len(sel) > 1:
            #	menuItem(label = "swap shape", c = lambda *args: self.swapShape(sel[0], sel[1]), enable =1, rp = "SW", ecr = 1)
            if character:
                if(character.networkNode.hasAttr("CustomMM")):
                    chtr = character
                    exec character.networkNode.CustomMM.get() in  globals(),locals()
                    makeMM(tmm=self,chtr=chtr,sel=sel)
					
            if isFKIKLeg:
                if sel[0] == isFKIKLeg.networkNode.ikAnim.listConnections()[0]:
                    menuItem(label = "Foot Locators", subMenu=1, enable = 1, rp = "NW", allowOptionBoxes = 1, p=main)
                    menuItem(label = "Create Foot Locators", c = lambda *args:self.createFootLocators(character, isFKIKLeg, sel[0]), enable = 1, rp = "W", ecr =1)
                    menuItem(label = "Clean Up Foot Locators", c = lambda *args:self.cleanFootLocators(character, isFKIKLeg, sel[0]), enable = 1, rp = "E", ecr =1)
                    
            
            
        # else:
            # self.makeMultiConstraintMenu(None, None,0)
    
    def rotateChar(self, character, rotation):
        autoKey = False
        if autoKeyframe(q=True, state=True):
            autoKeyframe(e=True, state=False)
            autoKey = True
            
        fkikLegs = getNodeOfTypeForChar(character, "FKIKLeg")
        switchBack = []
        for leg in fkikLegs:
            leg = fromNetworkToObject(leg)
            switch = leg.getSwitchAttr().get()
            if switch == 1:
                leg.alignSwitch()
                switchBack.append(leg)
        
        cog = fromNetworkToObject(getNodeOfTypeForChar(character, "COGChain")[0])
        cog = cog.getAllAnims()[0]
        curRot = cog.attr('rotateX').get()
        cog.attr('rotateX').set(curRot + rotation)
        
        for leg in switchBack:
            leg.alignSwitch()
        
        if autoKey:
            autoKeyframe(e=True, state=True)
        
    def createFootLocators(self, character, rigComp, footAnim):
        charName = str(character.getTopCon().split("_")[0])
        if footAnim.isReferenced():
            groupName = charName + "_" + footAnim.split(":")[1] + "_pos_loc"
        else: 
            groupName = charName + "_" + footAnim + "_pos_loc"
        if objExists(groupName):
            locGrp = PyNode(groupName)
        else:
            locGrp = group(em=1, n=groupName)
        locs = []
        heel = spaceLocator(n="heel#")
        locs.append(heel)
        toe = spaceLocator(n="toe#")
        locs.append(toe)
        inside = spaceLocator(n="inside#")
        locs.append(inside)
        outside = spaceLocator(n="outside#")
        locs.append(outside)
        
        pivs = [rigComp.networkNode.heelPiv.listConnections()[0], \
            rigComp.networkNode.toePiv.listConnections()[0], \
            rigComp.networkNode.insidePiv.listConnections()[0], \
            rigComp.networkNode.outsidePiv.listConnections()[0]]
            
        inc = 0
        for loc in locs:
            loc.attr('scale').set([5,5,5])
            loc.attr('overrideEnabled').set(1)
            loc.attr('overrideColor').set(17)
            ptC = pointConstraint(pivs[inc], loc, mo=0)
            orC = orientConstraint(pivs[inc], loc, mo=0)
            delete(ptC)
            delete(orC)
            parent(loc, locGrp)
            inc += 1
            
        select(cl=1)
        select(footAnim)
        
    def cleanFootLocators(self, character, rigComp, footAnim):
        charName = str(character.getTopCon().split("_")[0])
        if footAnim.isReferenced():
            groupName = charName + "_" + footAnim.split(":")[1] + "_pos_loc"
        else: 
            groupName = charName + "_" + footAnim + "_pos_loc"
        delete(groupName)
    
    def slChildren(self, rigComp):
        rigComp.selectChild()
    
    def straight(self, rigComp):
        rigComp.straight()
            
    def selectHairBase(self, rigComp):
        rigComp.selectBase()
    
    def	hairFKIKSwitch(self, rigComp):
        rigComp.switch()
                
    def mirrorSelf(self, rigComp):
        rigComp.mirror(bothSides = 0)
                
    def mirrorBoth(self, rigComp):
        rigComp.mirror(bothSides = 1)
    
    def mirrorCharacter(self, character):
        character.mirrorPose()

    def mirrorComponentSide(self, character, rigComp):
        character.mirrorComponentSide(rigComp)
    
    def mirrorSide(self):
        char = getMetaRoot(ls(sl=1)[0], 'CharacterRig')
        if not "face" in str(char.networkNode.attr('characterName').get()).lower():
            raise Exception('Select face rig')
        SIDE = ""
        if 'right' in str(ls(sl=1)[0]).lower():
            SIDE = "right"
        elif 'left' in str(ls(sl=1)[0]).lower():
            SIDE = "left"
        else:
            raise Exception('Select side you want to mirror')

        left_anims = []
        right_anims = []

        for anim in char.getAllAnims():
            if not "eye" in str(anim).lower():
                if 'left' in str(anim).lower():
                    left_anims.append(anim)
                elif 'right' in str(anim).lower():
                    right_anims.append(anim)

        count = 0
        for anim in left_anims:
            copyFrom = ""
            copyTo = ""
            if SIDE == "left":
                copyFrom = anim
                copyTo = right_anims[count]
            else:
                copyFrom = right_anims[count]
                copyTo = anim
                
            unlocked = []
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                if not copyTo.attr(attr).isLocked():
                    unlocked.append(attr)
            for attr in unlocked:
                if 't' in attr:
                    if "ik" in str(copyTo).lower():
                        if attr == "tz":
                            copyTo.attr(attr).set(-1 * copyFrom.attr(attr).get())        
                        else: 
                            copyTo.attr(attr).set(copyFrom.attr(attr).get()) 
                    else:
                        copyTo.attr(attr).set(-1 * copyFrom.attr(attr).get())
                else:
                    if "ik" in str(copyTo).lower():
                        if attr == "rz":
                            copyTo.attr(attr).set(copyFrom.attr(attr).get())        
                        else: 
                            copyTo.attr(attr).set(-1 * copyFrom.attr(attr).get()) 
                    else:
                        copyTo.attr(attr).set(copyFrom.attr(attr).get())
            count = count + 1
        
    def alignSwitch(self, rigComp):
        rigComp.alignSwitch()
        
    def alignSwitchAndKeyBefore(self, rigComp):
        rigComp.alignSwitch()
        attr = rigComp.getSwitchAttr()
        currentValue = attr.get()
        beforeValue = 1-currentValue
        node = attr.node()
        attrName = attr.name().split(node.name() + ".")[-1]
        print getCurrentTime()-1, node, beforeValue, attrName
        setKeyframe(node,v=beforeValue, at = attrName, t= getCurrentTime()-1, itt='spline' , ott = 'step')
        
    def justSwitch(self, rigComp):
        attr = rigComp.getSwitchAttr()
        currentValue = attr.get()
        attr.set(1-currentValue)
        
    def selectSwitch(self, rigComp):
        attr = rigComp.getSwitchAttr()
        select(attr.node())
    
    def selectAll(self, character):
        character.selectAllAnims()
    
    def keyAll(self, character):
        character.keyAllAnims()
            
    def defaultPoseSelf(self, rigComp):
        rigComp.toDefaultPose()
        
    def defaultPoseCharacter(self, character):
        character.toDefaultPose()
    
    def swapShape(self, newShape, obj):
        swapShape(newShape, obj)
    
    # def makeMultiConstraintMenu(self, mc, object, submenu):
        # if submenu:
            # menuItem(label = "MultiConstraint", subMenu = 1, enable = 1, rp = "W", allowOptionBoxes = 1)
            # parents = mc.getParents()
            # len(parents)
            # direction ={0:"NE",1:"E",2:"SE",3:"S",4:"SW",5:"NW"}
            # inc = 0
            # for par in parents:
                # mi = menuItem(label = par, enable = 1, c = eval("lambda *args: MultiConstraint('','',node = '"+mc.networkNode.name()+"').swapMultiConstraint("+str(inc)+")"), rp = direction[inc], ecr =1)#ugly command but only way with this version of pymel
                # inc+=1
            # menuItem(label = 'None', enable = 1, c = lambda *args: mc.swapMultiConstraint(len(parents)), rp = 'N', ecr =1)
            
            # #menuItem(label = "MultiConstraint", c = lambda *args: MultiConstraintWindow(object), enable = 1, rp = "W", ecr =1)
            # setParent("..", m=1)
            
        # else:
            # menuItem(label = "MultiConstraint", c = lambda *args: MultiConstraintWindow(object), enable = 1, rp = "W", ecr =1)

    def sList(self, chtr, set, add=1, remove=0):
        if(add==1):
            map(lambda (n):select(chtr.getTopCon().namespace()+n,add=add),set);
        
    def kList(self, chtr, sets):
        oldSelection = ls(sl=1);
        select(clear=1);
        nameSpace = chtr.getTopCon().namespace();
        for nodeName in sets:
            n = PyNode(nameSpace+nodeName)
            if(isinstance(n, nodetypes.ObjectSet)):
                n = n.asSelectionSet()
            if(isinstance(n, nodetypes.SelectionSet)):
                for selNodeName in n.getSelectionStrings():
                    select(selNodeName,add=1);
                setKeyframe();
            else:
                setKeyframe(n);
        select(oldSelection)
        
    def dpList(self,chtr,sets):
        oldSelection = ls(sl=1);
        select(clear=1);
        nameSpace = chtr.getTopCon().namespace();
        for nodeName in sets:
            n = PyNode(nameSpace+nodeName)
            if(isinstance(n, nodetypes.ObjectSet)):
                n = n.asSelectionSet()
            if(isinstance(n, nodetypes.SelectionSet)):
                for selNodeName in n.getSelectionStrings():
                    rigComp = getMetaRoot(PyNode(selNodeName), ['FKChain',"COGChain",'ReverseChain','AdditionalTwist','FKIKSplineChain','FKIKChain', 'SingleIKChain', 'StretchyJointChain', 'FKIKArm', 'FKIKArm2',"FKIKLeg",'FKFloatChain','IKLips'])
                    if(rigComp):
                        self.defaultPoseSelf(rigComp)
            else:
                rigComp = getMetaRoot(n, ['FKChain',"COGChain",'ReverseChain','AdditionalTwist','FKIKSplineChain','FKIKChain', 'SingleIKChain', 'StretchyJointChain', 'FKIKArm', 'FKIKArm2',"FKIKLeg",'FKFloatChain','IKLips'])
                if(rigComp):
                    self.defaultPoseSelf(rigComp)
        select(oldSelection)	
        
        
class TestRigMarkingMenu():
    def __init__(self):
        if (popupMenu("metaMarkingMenu", exists=1)):
            deleteUI("metaMarkingMenu")
        main = popupMenu("metaMarkingMenu",button = 1, ctl = 1, alt =0, sh = 1, allowOptionBoxes =1, parent = "viewPanes", mm=1)
        
        
        sel = ls(sl=1)
        if sel:
            #print "getMetaRoot" in dir()
            character = getMetaRoot(sel[0], 'CharacterRig')
            hasAlignSwitch = getMetaRoot(sel[0], ['FKIKSplineChain','FKIKChain', 'FKIKArm', 'FKIKArm2', "FKIKLeg", "FKIKSpine"])
            hasMultiConstraint = 0
            allMultiConstraints = getMetaNodesOfType("MultiConstraint")
            for x in allMultiConstraints:
                multi = fromNetworkToObject(x)
                if sel[0] == multi.getChild():
                    hasMultiConstraint = multi			
            isRigComp = getMetaRoot(sel[0], ['FKChain',"COGChain",'ReverseChain','AdditionalTwist','FKIKSplineChain','FKIKChain', 'SingleIKChain', 'StretchyJointChain', 'FKIKArm', 'FKIKArm2',"FKIKLeg",'FKFloatChain','IKLips'])
            #print character, hasAlignSwitch, hasMultiConstraint, isRigComp
            
            if character:		
                if isRigComp:
                    #mirror North
                    menuItem(label = "Mirror", subMenu=1, enable = 1, rp = "N", allowOptionBoxes = 1)
                    menuItem(label = "character", c= lambda *args:self.mirrorCharacter(character), enable=1, rp = "E", enableCommandRepeat =1)
                    menuItem(label = "both", c = lambda *args:self.mirrorBoth(isRigComp), enable =1, rp= "N", ecr=1)
                    menuItem(label = "self", c = lambda *args:self.mirrorSelf(isRigComp), enable =1, rp= "W", ecr=1)
                    setParent("..",m=1)
            
                #selectAllAnims NorthEast
                menuItem(label = "select all anims", c = lambda *args:self.selectAll(character), enable =1, rp="NE", ecr =1) 
                
                #key all East
                menuItem(label = "key all anims", c = lambda *args:self.keyAll(character), enable = 1, rp = "E", ecr =1)
        
                #default Pose South
                menuItem(label = "Default Pose", subMenu=1, enable = 1, rp = "S", allowOptionBoxes = 1)
                menuItem(label = "character", c = lambda *args:self.defaultPoseCharacter(character), enable = 1, rp = "E", ecr = 1)
                menuItem(label = "self", c = lambda *args:self.defaultPoseSelf(isRigComp), enable = 1, rp = "W", ecr = 1)
                setParent("..",m=1)
                    
            if hasAlignSwitch:			
                #alignSwitch SouthEast
                menuItem(label = "switch", subMenu=1, enable = 1, rp = "SE", allowOptionBoxes = 1)
                menuItem(label = "align switch", c = lambda *args:self.alignSwitch(hasAlignSwitch), enable = 1, rp = "SE", ecr =1)
                menuItem(label = 'align switch and key before', c= lambda *args: self.alignSwitchAndKeyBefore(hasAlignSwitch), enable = 1, rp = "E", ecr = 1)
                menuItem(label = "just switch", c = lambda *args:self.justSwitch(hasAlignSwitch), enable = 1, rp = "SW", ecr =1)
                menuItem(label = "select switch", c = lambda *args: self.selectSwitch(hasAlignSwitch), enable = 1, rp = "N", ecr =1)
                setParent("..",m=1)
            
            if hasMultiConstraint:
                self.makeMultiConstraintMenu(hasMultiConstraint,sel[0],1)
            #else:
            #	self.makeMultiConstraintMenu(None, sel[0], 0)
                
            #swap shape SouthWest
            #if len(sel) > 1:
            #	menuItem(label = "swap shape", c = lambda *args: self.swapShape(sel[0], sel[1]), enable =1, rp = "SW", ecr = 1)
            if(character.networkNode.hasAttr("CustomMM")):
                chtr = character
                exec character.networkNode.CustomMM.get() in  globals(),locals()
                makeMM(tmm=self,chtr=chtr,sel=sel)
                '''
def makeMM(**kwargs):
    tmm = kwargs['tmm']
    chtr = kwargs['chtr']
    sel = kwargs['sel']
    pymel = __import__('pymel.all')
    metaCore = __import__('scene_manager.metaCore')
    methods = __import__('scene_manager.methods')

    menuItem(label = 'CustomRigMenu', subMenu=1, enable=1, rp="NW", ecr=1);
    menuItem(label = 'R Cheek SDK', c=lambda *args:tmm.sList(chtr,['right_mouth_corner_anim'],add=1), enable=1, rp="W");
    menuItem(label = 'L Cheek SDK', c=lambda *args:tmm.sList(chtr,['left_mouth_corner_anim'],add=1), enable=1, rp="E");
    menuItem(label = 'Key All Face Anims',  c=lambda *args:tmm.kList(chtr,['primary_face_anims','secondary_face_anims']), enable=1);
    menuItem(label = 'Key Primary Face Anims',  c=lambda *args:tmm.kList(chtr,['primary_face_anims']), enable=1);
    menuItem(label = 'Key Secondary Face Anims',  c=lambda *args:tmm.kList(chtr,['secondary_face_anims']), enable=1);
    menuItem(label = 'Face Default Pose',  c=lambda *args:tmm.dpList(chtr,['primary_face_anims','secondary_face_anims']), enable=1);
    menuItem(label = 'Face Primary Default Pose',  c=lambda *args:tmm.dpList(chtr,['primary_face_anims']), enable=1);
    menuItem(label = 'Face secondary Default Pose',  c=lambda *args:tmm.dpList(chtr,['secondary_face_anims']), enable=1);
    menuItem(label = 'Selected to Default Pose', c=lambda *args:tmm.dpList(chtr,ls(sl=1)), enable=1);
    menuItem(label = 'Select All Face Anims',c=lambda *args:tmm.sList(chtr,['primary_face_anims','secondary_face_anims'],add=1), enable=1);
    menuItem(label = 'Select Primary Face Anims',c=lambda *args:tmm.sList(chtr,['primary_face_anims'],add=1), enable=1);
    menuItem(label = 'Select Secondary Face Anims',c=lambda *args:tmm.sList(chtr,['secondary_face_anims'],add=1), enable=1);
    #menuItem(label = 'Primary Face Anims Visible',  c=lambda *args:printError("NOT YET IMPLEMENTED"), enable=1, cb=1);
    #menuItem(label = 'Secondary Face Anims Visible',  c=lambda *args:printError("NOT YET IMPLEMENTED"), enable=1, cb=1);
    #menuItem(label = 'Toggle All Face Anim Visibillity',  c=lambda *args:printError("NOT YET IMPLEMENTED"), enable=1);
    menuItem(label = 'Pose Library', c=lambda *args:PoseLibWindow(), enable=1);
    #menuItem(label = 'Add to Selection', enable=1, rb=1);
    #menuItem(label = 'Remove from Selection', enable=1, rb=1);
    #menuItem(label = 'Toggle Selection', enable=1, rb=1);

    menuItem(label = 'EYES', subMenu=1, enable=1, rp="N", ecr=1);
    menuItem(label = 'R+L Upper Lid', c=lambda *args:tmm.sList(chtr,['right_upper_eyelid_anim','left_upper_eyelid_anim']), enable=1, rp="N");
    menuItem(label = 'R Brow', c=lambda *args:tmm.sList(chtr,['right_brow_1_anim','right_brow_2_anim','right_brow_3_anim']), enable=1, rp="NW");
    menuItem(label = 'L Brow', c=lambda *args:tmm.sList(chtr,['left_brow_1_anim','left_brow_2_anim','left_brow_3_anim']),enable=1, rp="NE");
    menuItem(label = 'R Upper Lid', c=lambda *args:tmm.sList(chtr,['right_upper_eyelid_anim']), enable=1, rp="W");
    menuItem(label = 'L Upper Lid', c=lambda *args:tmm.sList(chtr,['left_upper_eyelid_anim']), enable=1, rp="E");
    menuItem(label = 'R Lower Lid', enable=1, c=lambda *args:tmm.sList(chtr,['right_lower_eyelid_anim']), rp="SW");
    menuItem(label = 'L Lower Lid', enable=1, c=lambda *args:tmm.sList(chtr,['left_lower_eyelid_anim']), rp="SE");
    menuItem(label = 'R+L Lower Lid', c=lambda *args:tmm.sList(chtr,['right_lower_eyelid_anim','left_lower_eyelid_anim']), enable=1, rp="S");
    menuItem(label = 'Select All Eye Anims',  c=lambda *args:tmm.sList(chtr,['right_upper_eyelid_anim','right_lower_eyelid_anim','left_upper_eyelid_anim','left_lower_eyelid_anim']), enable=1);
    setParent("..",m=1);

    menuItem(label = 'MOUTH', subMenu=1, enable=1, rp="S", ecr=1);
    menuItem(label = 'Upper Lip', c=lambda *args:tmm.sList(chtr,['upper_lip_anim']), enable=1, rp="N");
    menuItem(label = 'RUp Stretchy Lip', c=lambda *args:tmm.sList(chtr,['upper_right_lips_ik_mid_anim']), enable=1, rp="NW");
    menuItem(label = 'LUp Stretchy Lip', c=lambda *args:tmm.sList(chtr,['upper_left_lips_ik_mid_anim']), enable=1, rp="NE");
    menuItem(label = 'R Corner', c=lambda *args:tmm.sList(chtr,['right_mouth_corner_tweak_anim']), enable=1, rp="W");
    menuItem(label = 'L Corner', c=lambda *args:tmm.sList(chtr,['left_mouth_corner_tweak_anim']), enable=1, rp="E");
    menuItem(label = 'RLw Stretchy Lip', c=lambda *args:tmm.sList(chtr,['lower_right_lips_ik_mid_anim']), enable=1, rp="SW");
    menuItem(label = 'LLw Stretchy Lip', c=lambda *args:tmm.sList(chtr,['lower_left_lips_ik_mid_anim']), enable=1, rp="SE");
    menuItem(label = 'Lower Lip', c=lambda *args:tmm.sList(chtr,['lower_lip_anim']), enable=1, rp="S");
    menuItem(label = 'INNER MOUTH', subMenu=1, enable=1, ecr=1);
    menuItem(label = 'Upper Teeth', c=lambda *args:tmm.sList(chtr,['center_teeth_upper_anim']), enable=1, rp="N");
    menuItem(label = 'Lower Teeth', c=lambda *args:tmm.sList(chtr,['center_teeth_lower_anim']), enable=1, rp="S");
    menuItem(label = 'Toungue End', c=lambda *args:tmm.sList(chtr,['center_tongue_ik_end_anim']), enable=1, rp="S");
    menuItem(label = 'Toungue Mid', c=lambda *args:tmm.sList(chtr,['center_tongue_ik_mid_anim']), enable=1, rp="S");
    #menuItem(label = 'Toungue Base', c=lambda *args:tmm.sList(chtr,['center_tongue_ik_start_anim']), enable=1, rp="S");
    setParent("..",m=1);

    setParent("..",m=1);
'''
        else:
            self.makeMultiConstraintMenu(None, None,0)
                
    def mirrorSelf(self, rigComp):
        rigComp.mirror(bothSides = 0)
                
    def mirrorBoth(self, rigComp):
        rigComp.mirror(bothSides = 1)
    
    def mirrorCharacter(self, character):
        character.mirrorPose()
        
    def alignSwitch(self, rigComp):
        rigComp.alignSwitch()
        
    def alignSwitchAndKeyBefore(self, rigComp):
        rigComp.alignSwitch()
        attr = rigComp.getSwitchAttr()
        currentValue = attr.get()
        beforeValue = 1-currentValue
        node = attr.node()
        attrName = attr.name().split(node.name() + ".")[-1]
        print getCurrentTime()-1, node, beforeValue, attrName
        setKeyframe(node,v=beforeValue, at = attrName, t= getCurrentTime()-1, itt='spline' , ott = 'step')
        
    def justSwitch(self, rigComp):
        grp = rigComp.networkNode.switchGroup.listConnections()[0]
        attr = rigComp.networkNode.switchAttr.get()		
        val = grp.attr(attr).get()
        grp.attr(attr).set(1-val)
        
    def selectSwitch(self, rigComp):
        select(rigComp.networkNode.switchGroup.listConnections()[0])
    
    def selectAll(self, character):
        character.selectAllAnims()
    
    def keyAll(self, character):
        character.keyAllAnims()
            
    def defaultPoseSelf(self, rigComp):
        rigComp.toDefaultPose()
        
    def defaultPoseCharacter(self, character):
        character.toDefaultPose()
    
    def swapShape(self, newShape, obj):
        swapShape(newShape, obj)
    
    def makeMenu(self, mc, object, submenu):
        if submenu:
            menuItem(label = "MultiConstraint", subMenu = 1, enable = 1, rp = "W", allowOptionBoxes = 1)
            parents = mc.getParents()
            len(parents)
            direction ={0:"NE",1:"E",2:"SE",3:"S",4:"SW",5:"NW"}
            inc = 0
            for par in parents:
                mi = menuItem(label = par, enable = 1, c = eval("lambda *args: MultiConstraint('','',node = '"+mc.networkNode.name()+"').swapMultiConstraint("+str(inc)+")"), rp = direction[inc], ecr =1)#ugly command but only way with this version of pymel
                inc+=1
            menuItem(label = 'None', enable = 1, c = lambda *args: mc.swapMultiConstraint(len(parents)), rp = 'N', ecr =1)
            
            #menuItem(label = "MultiConstraint", c = lambda *args: MultiConstraintWindow(object), enable = 1, rp = "W", ecr =1)
            setParent("..", m=1)
            
        else:
            menuItem(label = "MultiConstraint", c = lambda *args: MultiConstraintWindow(object), enable = 1, rp = "W", ecr =1)
        
    def sList(self, chtr, set, add=1, remove=0):
        if(add==1):
            map(lambda (n):select(chtr.getTopCon().namespace()+n,add=add),set);
        
    def kList(self, chtr, sets):
        oldSelection = ls(sl=1);
        select(clear=1);
        nameSpace = chtr.getTopCon().namespace();
        for nodeName in sets:
            n = PyNode(nameSpace+nodeName)
            if(isinstance(n, nodetypes.ObjectSet)):
                n = n.asSelectionSet()
            if(isinstance(n, nodetypes.SelectionSet)):
                for selNodeName in n.getSelectionStrings():
                    select(selNodeName,add=1);
                setKeyframe();
            else:
                setKeyframe(n);
        select(oldSelection)
        
    def dpList(self,chtr,sets):
        oldSelection = ls(sl=1);
        select(clear=1);
        nameSpace = chtr.getTopCon().namespace();
        for nodeName in sets:
            n = PyNode(nameSpace+nodeName)
            if(isinstance(n, nodetypes.ObjectSet)):
                n = n.asSelectionSet()
            if(isinstance(n, nodetypes.SelectionSet)):
                for selNodeName in n.getSelectionStrings():
                    rigComp = getMetaRoot(PyNode(selNodeName), ['FKChain',"COGChain",'ReverseChain','AdditionalTwist','FKIKSplineChain','FKIKChain', 'SingleIKChain', 'StretchyJointChain', 'FKIKArm', 'FKIKArm2',"FKIKLeg",'FKFloatChain','IKLips'])
                    if(rigComp):
                        self.defaultPoseSelf(rigComp)
            else:
                rigComp = getMetaRoot(n, ['FKChain',"COGChain",'ReverseChain','AdditionalTwist','FKIKSplineChain','FKIKChain', 'SingleIKChain', 'StretchyJointChain', 'FKIKArm', 'FKIKArm2',"FKIKLeg",'FKFloatChain','IKLips'])
                if(rigComp):
                    self.defaultPoseSelf(rigComp)
        select(oldSelection)	
    def visList(self,sets):
        pass
    def invisList(self,sets):
        pass			

def safeDeleteRigMarkingMenu():
    if (popupMenu("metaMarkingMenu", exists=1)):
            deleteUI("metaMarkingMenu")
            
def testFunc():
    print(42)

class CustomScriptsWindow():

    def __init__(self):
        '''
        Constructs the Custom Scripts Library window.
        '''
        
        self.customScriptsPath = '\\\\ntdfs\\cs\\unix\\projects\\instr\\'+PRODUCTION_SERVER+'\\production\\scripts\\capstone_shelves\\custom_scripts\\'
        
        self.selectedItem = None
        self.scriptsListWidth = 250
        self.editableInfo = False
        
        self.window = None
        self.mainPanel = None
        self.informationPanel = None
        self.customScriptsList = None
        self.runScriptButton = None
        self.refreshScriptsButton = None
        
        # Delete the window if it already exists
        if window('CustomScriptsWindow', exists=1): deleteUI('CustomScriptsWindow')
        
        # Main window
        self.window = window('CustomScriptsWindow', title='Custom Scripts', s=True, width=800, height=600)
        self.mainPanel = formLayout()
        
        # Information Panel
        self.informationPanel = formLayout(p=self.mainPanel)
        self.informationList = None
        
        # Custom Scripts List
        self.customScriptsList = textScrollList(p=self.mainPanel,
                                                allowMultiSelection=False,
                                                sc=Callback(self.newScriptSelectedCallback),
                                                dcc=Callback(self.runScriptButtonCallback),
                                                width=self.scriptsListWidth)
        
        # Open custom scripts folder
        self.openScriptsFolderButton = iconTextButton(  p=self.mainPanel,
                                                        st="iconOnly",
                                                        i="openScript.png",
                                                        w=.1*self.scriptsListWidth,
                                                        c=Callback(self.openCustomScriptsFolderCallback),
                                                        ann="Open custom scripts folder.  Modify scripts there or drop in new ones.  Don't modify the metadata folder, however!")
        
        # Run Script Button
        self.runScriptButton = button(p=self.mainPanel, l="Run Script", c=Callback(self.runScriptButtonCallback), w=.8*self.scriptsListWidth)
        
        # Refresh custom scripts list
        self.refreshScriptsButton = iconTextButton( p=self.mainPanel,
                                                    st="iconOnly",
                                                    i="refresh.png",
                                                    w=.1*self.scriptsListWidth,
                                                    c=Callback(self.refreshCustomScriptsCallback),
                                                    ann="Refresh the list of scripts.  If you added a new script to the custom scripts folder click here to make it show up.")
        
        # Hook controls up to main panel
        self.mainPanel.attachForm(self.informationPanel, "top", 0)
        self.mainPanel.attachForm(self.informationPanel, "left", 0)
        self.mainPanel.attachForm(self.informationPanel, "bottom", 0)
        self.mainPanel.attachControl(self.informationPanel, "right", 0, self.customScriptsList)
        
        self.mainPanel.attachForm(self.customScriptsList, "top", 0)
        self.mainPanel.attachControl(self.customScriptsList, "bottom", 0, self.runScriptButton)
        self.mainPanel.attachForm(self.customScriptsList, "right", 0)
        

        
        self.mainPanel.attachForm(self.runScriptButton, "bottom", 0)
        self.mainPanel.attachControl(self.runScriptButton, "right", 0, self.refreshScriptsButton)
        
        self.mainPanel.attachForm(self.refreshScriptsButton, "bottom", 0)
        self.mainPanel.attachControl(self.refreshScriptsButton, "right", 0, self.openScriptsFolderButton)
        
        self.mainPanel.attachForm(self.openScriptsFolderButton, "bottom", 0)
        self.mainPanel.attachForm(self.openScriptsFolderButton, "right", 0)
        
        # Finish up
        self.setupInformationPanel()
        self.refreshCustomScriptsCallback()
        showWindow(self.window)
    
    def openCustomScriptsFolderCallback(self):
        '''
        Opens the custom scripts folder on the network.
        '''
        
        subprocess.Popen(r'explorer /select, "'+os.path.join(self.customScriptsPath, self.indexToScriptTable[self.selectedItem])+'"')

    
    def refreshCustomScriptsCallback(self):
        '''
        Refresh the custom scripts window: read in custom scripts folder, meta data, and rebuild the scripts list.
        '''
        
        self.customScriptsList.removeAll()
        # Reset data tables
        self.indexToScriptTable = {}
        self.metadata_indexToName = {}
        self.metadata_indexToInformation = {}
        
        # Load script file names from the custom scripts folder
        scriptsList = glob.glob(self.customScriptsPath+"*.py")
        scriptsList += glob.glob(self.customScriptsPath+"*.mel")
        
        # Load metadata and construct custom scripts list
        toSelect = self.selectedItem
        scriptIndex = 1 # 1-based
        
        for s in scriptsList:
        
            scriptName = os.path.basename(s)
            if toSelect == None or toSelect > len(scriptsList): toSelect = scriptIndex
            
            self.indexToScriptTable[scriptIndex] = scriptName # Link index to script file
            self.loadScriptMetadata(scriptIndex) # Load metadata
            
            if (self.metadata_indexToName[scriptIndex] == ""):
                displayName = scriptName
            else:
                displayName = self.metadata_indexToName[scriptIndex]
                
            self.customScriptsList.append(displayName) # Add script to list

            scriptIndex += 1
        
        if toSelect != None: self.customScriptsList.setSelectIndexedItem(toSelect)
        
        self.newScriptSelectedCallback()
    
    def newScriptSelectedCallback(self):
        '''
        New script is selected from the list.
        '''
        
        selectionQuery = self.customScriptsList.getSelectIndexedItem()
        if (len(selectionQuery) == 0):
            self.selectedItem = None
            if self.informationList != None:
                deleteUI(self.informationList)
                self.informationList = None
            return None
        
        newSelectedItem = selectionQuery[0]
        if (newSelectedItem == self.selectedItem): return None
        
        self.selectedItem = newSelectedItem
        
        # Nothing is selected, no metadata
        if self.selectedItem == None:
            self.nameField.setText("")
            self.fileField.setText("N/A")
            self.informationField.setText("")
        # Update fields with appropriate metadata
        else:
            self.nameField.setText(self.metadata_indexToName[self.selectedItem])
            self.fileField.setText(self.indexToScriptTable[self.selectedItem])
            self.informationField.setText(self.metadata_indexToInformation[self.selectedItem])
    
    def loadScriptMetadata(self, scriptIndex):
        '''
        Given a script index, load that script's metadata into the appropriate tables.
        '''
 
        scriptFile = self.indexToScriptTable[scriptIndex]
        metadataFile = scriptFile.split('.')[0]+".xml"
        metadataFilePath = os.path.join(self.customScriptsPath, "metadata", metadataFile)
        
        # Load meta data related to script
        if os.path.exists(metadataFilePath):
            try:
                import xml.dom.minidom
                doc = xml.dom.minidom.parse(metadataFilePath)
                scriptNameE = doc.getElementsByTagName("ScriptName")[0]
                informationE = doc.getElementsByTagName("Information")[0]
                self.metadata_indexToName[scriptIndex] = scriptNameE.getAttribute("text")
                self.metadata_indexToInformation[scriptIndex] = informationE.getAttribute("text")
                return None
            except:
                print "Error reading "+scriptFile+" metadata."
                
        # No metadata or error reading in metadata
        self.metadata_indexToName[scriptIndex] = ""
        self.metadata_indexToInformation[scriptIndex] = ""
    
    def setupInformationPanel(self):
        '''
        Construct the information panel GUI.
        '''
        
        self.informationList = formLayout(p=self.informationPanel)
        self.informationPanel.attachForm(self.informationList, "left", 0)
        self.informationPanel.attachForm(self.informationList, "right", 0)
        self.informationPanel.attachForm(self.informationList, "top", 0)
        self.informationPanel.attachForm(self.informationList, "bottom", 0)
        
        nameLabel = text(l="Script Name", al="left", fn="boldLabelFont")
        self.informationList.attachForm(nameLabel, "left", 5)
        self.informationList.attachForm(nameLabel, "right", 5)
        self.informationList.attachForm(nameLabel, "top", 5)
        
        self.nameField = textField(tx="", ed=0)
        self.informationList.attachForm(self.nameField, "left", 5)
        self.informationList.attachForm(self.nameField, "right", 5)
        self.informationList.attachControl(self.nameField, "top", 2, nameLabel)

        fileLabel = text(l="File", al="left", fn="boldLabelFont")
        self.informationList.attachForm(fileLabel, "left", 5)
        self.informationList.attachForm(fileLabel, "right", 5)
        self.informationList.attachControl(fileLabel, "top", 5, self.nameField)
        
        self.fileField = textField(tx="", ed=0, bgc=(.2,.2,.2))
        self.informationList.attachForm(self.fileField, "left", 5)
        self.informationList.attachForm(self.fileField, "right", 5)
        self.informationList.attachControl(self.fileField, "top", 2, fileLabel)
        
        informationLabel = text(l="Information", al="left", fn="boldLabelFont")
        self.informationList.attachForm(informationLabel, "left", 5)
        self.informationList.attachForm(informationLabel, "right", 5)
        self.informationList.attachControl(informationLabel, "top", 5, self.fileField)
        
        self.informationField = scrollField(tx="", ed=0, ww=1)
        self.informationList.attachForm(self.informationField, "left", 5)
        self.informationList.attachForm(self.informationField, "right", 5)
        self.informationList.attachControl(self.informationField, "top", 2, informationLabel)
        
        metaDataButtons = horizontalLayout(h=30)
        
        self.toggleEdit = checkBox(l="Edit Information", v=self.editableInfo)
        self.saveEditButton = iconTextButton(   i="fileSave.png",
                                                l="Save Changes",
                                                st="iconAndTextHorizontal",
                                                c=Callback(self.saveEditButtonCallback),
                                                vis=self.editableInfo   )
                                                
        def toggleEditButtonCallback():
            self.editableInfo = self.toggleEdit.getValue()
            self.saveEditButton.setVisible(self.editableInfo)
            self.nameField.setEditable(self.editableInfo)
            self.informationField.setEditable(self.editableInfo)
            if self.editableInfo:
                fieldColor = (.15,.15,.15)
            else:
                fieldColor = (.2,.2,.2)
            self.nameField.setBackgroundColor(fieldColor)
            self.informationField.setBackgroundColor(fieldColor)
            # Display metadata stored in memory, getting rid of any edits
            if not self.editableInfo and self.selectedItem != None:
                self.nameField.setText(self.metadata_indexToName[self.selectedItem])
                self.informationField.setText(self.metadata_indexToInformation[self.selectedItem])
        
        toggleEditButtonCallback()
        self.toggleEdit.setChangeCommand(Callback(toggleEditButtonCallback))
         
        metaDataButtons.redistribute()
        
        self.informationList.attachForm(metaDataButtons, "left", 5)
        self.informationList.attachControl(self.informationField, "bottom", 0, metaDataButtons)
        self.informationList.attachNone(metaDataButtons, "top")
        self.informationList.attachForm(metaDataButtons, "bottom", 5)

    def saveEditButtonCallback(self):
        '''
        Save edits.
        '''
        
        if self.selectedItem == None or not self.selectedItem in self.indexToScriptTable:
            return None
        
        scriptFile = self.indexToScriptTable[self.selectedItem]
        metadataFile = scriptFile.split('.')[0]+".xml"
        metadataFolder = os.path.join(self.customScriptsPath, "metadata")
        metadataFilePath = os.path.join(metadataFolder, metadataFile)
        
        if not os.path.exists(metadataFolder):
            os.mkdir(metadataFolder)
        
        import xml.dom.minidom
        doc = xml.dom.minidom.Document()
        
        scriptMetadataE = doc.createElement("ScriptMetadata")
        doc.appendChild(scriptMetadataE)
        
        scriptNameE = doc.createElement("ScriptName")
        scriptNameE.setAttribute("text", self.nameField.getText())
        scriptMetadataE.appendChild(scriptNameE)
        
        informationE = doc.createElement("Information")
        informationE.setAttribute("text", self.informationField.getText())
        scriptMetadataE.appendChild(informationE)
        
        try:
            # Write metadata to file.
            file = open(metadataFilePath, "w")
            file.writelines(doc.toprettyxml())
            file.close()
            # Metadata successfully written, update internally loaded metadata tables.
            self.metadata_indexToName[self.selectedItem] = self.nameField.getText()
            self.metadata_indexToInformation[self.selectedItem] = self.informationField.getText()
            # Update display name
            if (self.metadata_indexToName[self.selectedItem] == ""):
                displayName = scriptName
            else:
                displayName = self.metadata_indexToName[self.selectedItem]
            self.customScriptsList.removeIndexedItem(self.selectedItem)
            self.customScriptsList.appendPosition((self.selectedItem, displayName))
            self.customScriptsList.setSelectIndexedItem(self.selectedItem)
        except:
            print "Error writing "+scriptFile+" metadata."
        
    def runScriptButtonCallback(self):
        '''
        Runs the selected Python or MEL script.
        '''
        
        if self.selectedItem == None: return None
        
        scriptName = self.indexToScriptTable[self.selectedItem]
        
        # Run Python script
        if scriptName.endswith(".py"):
            try:
                # Needs empty globals dictionary for imported modules to work
                execfile(self.customScriptsPath + scriptName, {})
            except Exception as e:
                print "===============\n"+"Error running "+scriptName+":\n"+str(e)+"\n==============="
        
        # Run MEL script
        if scriptName.endswith(".mel"):
            try:
                scriptFile = open(self.customScriptsPath + scriptName, "r")
            except Exception as e:
                print "===============\n"+"Error opening "+scriptName+":\n"+str(e)+"\n==============="
                return None
            
            scriptLines = scriptFile.readlines()
            scriptFile.close()
            script = "".join(scriptLines).replace("\r", "")
        
            mel.eval(script)
    
    
class PoseLibWindow():

    '''
    A way to have different rigs share the same pose library.
    '''
    CHAR_LIB_NAME_MAPPING = {}
                                
    def getMappedCharLibName(self, libName):
        if (libName in self.CHAR_LIB_NAME_MAPPING):
            return self.CHAR_LIB_NAME_MAPPING[libName]
        return libName
        
    def __init__(self):
        '''
        Constructs the Pose Library window.
        '''
        
        # Global variables if changes are necessary
        self.poseAttributesHeight = 40
        self.poseLibraryTextHeight = 140
        self.listEntryHeight = 50
        self.listEntryWidth = 290
        self.smallIconSize = 50
        self.largeIconSize = 400
        self.poseLibraryPath = '\\\\ntdfs\\cs\\unix\\projects\\instr\\'+PRODUCTION_SERVER+'\\production\\pose_library\\'
        
        self.window = None
        self.mainPanel = None
        self.leftPanel = None
        self.poseCommands = None
        self.scrollPanel = None
        self.listPanel = None
        self.poseEntries = None
        self.selectedPoseTable = {} # Stores the name of a selected pose for a particular library

        self.listColumns = 0
        self.listRows = 0
        
        self.filterNameString = ""
        
        self.lastSelectionChangeLibrary = None
        
        self.currentLibrary = ''
        
        # Delete the window if it already exists
        if window('PoseLibWindow', exists=1): deleteUI('PoseLibWindow')
        
        # Main window
        self.window = window('PoseLibWindow', title = "Pose Library", s=True)
        self.window.setHeight(self.poseAttributesHeight)
        self.window.setWidth(self.largeIconSize)
        
        # Makes a script job that updates the pose list every time the selection has changed.
        # This way what you see is based on the character you have selected.
        scriptJob(p='PoseLibWindow', e=("SelectionChanged", Callback(self.selectionChangeRefreshGUI)))
        
        # Main
        self.mainPanel = formLayout()
        
        # LEFT PANEL
        self.leftPanel = columnLayout(	p=self.mainPanel,
                                        cw=self.largeIconSize,
                                        cat=("both",0),
                                        h=self.largeIconSize+2*self.poseAttributesHeight	)
        
        # Instructional panel (hidden when a valid rig is selected)\
        self.poseLibraryInfo = text(	l="Select a rig control to see that character's corresponding pose library. "+\
                                        "Character faces and bodies are treated as separate rigs, and thus have separate libraries.",
                                        al="left",
                                        vis=False,
                                        ww=True,
                                        w=self.largeIconSize,
                                        h=self.poseLibraryTextHeight	)
        
        # Top bar of left panel
        self.leftPanelTop = horizontalLayout(h=40)
        
        def takeScreenCaptureButtonCallback():
            if self.currentLibrary is None or not self.currentLibrary in self.selectedPoseTable: return None
            self.takeScreenCapture(self.currentLibrary, self.selectedPoseTable[self.currentLibrary])
            self.refreshPoseLibraryGUI()
        
        # Retake pose image
        self.retakeImageButton = iconTextButton(	i="savePaintSnapshot.png",
                                                    st="iconOnly",
                                                    c=Callback(takeScreenCaptureButtonCallback),
                                                    ann="Retakes the picture representing this pose using the active viewport."	)
        
        # Rig and pose information
        self.rigInfo = text(l="",
                            fn="boldLabelFont",
                            ww=True,
                            align="center",
                            ann="Active library and the selected pose."	)
        
        # Delete pose from the library
        self.deleteButton = iconTextButton(	i="SP_TrashIcon.png",
                                            st="iconOnly",
                                            c=Callback(self.deleteButton),
                                            ann="Deletes this pose from the library."	) 
        
        self.leftPanelTop.redistribute(1,5,1)
        setParent(self.leftPanel)
        
        # Row layout for buttons at the top of the big image
        optionsPanel = rowLayout(nc=1, ad1=True, cl1=("center"), w=self.largeIconSize)
        
        setParent(self.leftPanel)
        
        
        # RIGHT PANEL
        
        # Filters
        self.filterOptions = rowLayout(p=self.mainPanel, h=self.leftPanelTop.getHeight(), nc=2)
        
        c1 = columnLayout(p=self.filterOptions)
        text("Show:", p=c1)
        self.showWhich = radioButtonGrp(p=c1, cw3=(35, 50,50), adj=False, numberOfRadioButtons=3, labelArray3=['All', 'Poses', 'Clips'])
        self.showWhich.setSelect(0)
        
        self.showWhich.changeCommand(Callback(self.filterBy))
        
        c2 = columnLayout(p=self.filterOptions)
        text("Name Filter:", p=c2)
        rowLayout(nc=2)
        self.filterName = textField(alwaysInvokeEnterCommandOnReturn=True)
        self.filterNameApply = button("Apply")
        
        def filterNameApplyCallback():
            self.filterNameString = self.filterName.getText()
            self.filterBy(True)
        self.filterName.enterCommand(Callback(filterNameApplyCallback))
        self.filterNameApply.setCommand(Callback(filterNameApplyCallback))
        
        # Scroll panel for poses
        self.listColumns = 0
        self.scrollPanel = scrollLayout(p=self.mainPanel, w = self.listEntryWidth+25, bgc = (.2, .2, .2))
        
        self.scrollPanel.resizeCommand(self.updateListPanel)
        
        # Create save pose button
        self.saveButtons = horizontalLayout(p=self.mainPanel)
        self.savePoseButton = button(label = 'Save New Pose', c = Callback(self.createSavePoseWindow))
        self.saveClipButton = button(label = 'Save New Animation', c = Callback(self.createSaveClipWindow))
        
        
        # ATTACH PANELS
        self.mainPanel.attachControl(self.scrollPanel, "top", 0, self.filterOptions)
        self.mainPanel.attachForm(self.scrollPanel, "right", 0)
        self.mainPanel.attachForm(self.scrollPanel, "bottom", 0)
        self.mainPanel.attachControl(self.scrollPanel, "left", 0, self.leftPanel)

        self.mainPanel.attachForm(self.filterOptions, "top", 0)
        self.mainPanel.attachForm(self.filterOptions, "right", 0)
        self.mainPanel.attachControl(self.filterOptions, "left", 0, self.leftPanel)
        
        self.mainPanel.attachNone(self.saveButtons, "bottom")
        self.mainPanel.attachForm(self.saveButtons, "left", 5)
        self.mainPanel.attachControl(self.saveButtons, "right", 5, self.scrollPanel)
        self.mainPanel.attachControl(self.saveButtons, "top", 5, self.leftPanel)
        
        self.saveButtons.redistribute()
        
        self.refreshPoseLibraryGUI()
        self.lastSelectionChangeLibrary = self.currentLibrary
        
        
        showWindow(self.window)
        
    def filterBy(self, update=True):
        for pe in self.poseEntries:
            sel = self.showWhich.getSelect()
            if sel == 1:
                pe.filterBy(isAnimationClip=None, nameFilter=self.filterNameString)
            elif sel == 2:
                pe.filterBy(isAnimationClip=False, nameFilter=self.filterNameString)
            else:
                pe.filterBy(isAnimationClip=True, nameFilter=self.filterNameString)
        if update: self.updateListPanel(True)
    
    def applyPoseBlend(self):
        '''
        Applies the pose blend node between the current pose in the scene 
        and the selected pose library pose.
        '''
        
        # No selected pose to apply.  Leave and do nothing!
        if (self.currentLibrary == None) or \
            (not self.currentLibrary in self.selectedPoseTable) or \
            (self.selectedPoseTable[self.currentLibrary] == None):
            return None
       
        char = getMetaRoot(ls(sl=1)[0])
        charName = self.getMappedCharLibName(char.getCharacterName())
        poseName = self.selectedPoseTable[self.currentLibrary]
        posePath = os.path.join(self.poseLibraryPath, charName, "poses", poseName+".xml")
        if (os.path.exists(posePath)):
            targetPose = Pose().readXML(posePath)
        else:
            print 'Cannot find a pose named "'+poseName+'".'
            return None
        
        lastSelection = ls(sl=1)
        char = getMetaRoot(lastSelection[0])
        anims = char.getAllAnims()
        
        blender = PoseBlend().blendWithCurrent(targetPose, anims)
        blender.gui()
    
    def applySelectedPoseOrClip(self):
        '''
        Applies the currently selected pose the selected rig.
        '''
        
        # No selected pose to apply.  Leave and do nothing!
        if (self.currentLibrary == None) or \
            (not self.currentLibrary in self.selectedPoseTable) or \
            (self.selectedPoseTable[self.currentLibrary] == None):
            return None
        
        poseName = self.selectedPoseTable[self.currentLibrary]
        
        char = getMetaRoot(ls(sl=1)[0])
        charName = self.getMappedCharLibName(char.getCharacterName())
        namespace = ls(sl=1)[0].namespace()
        
        # See if either pose or animation clip
        posePath = os.path.join(self.poseLibraryPath, charName, "poses", poseName+".xml")
        clipPath = os.path.join(self.poseLibraryPath, charName, "poses", poseName+".anim.xml")
        
        if (os.path.exists(clipPath)):
            clip = CompactAnimationClip().load(clipPath)
            clip.applyClip(namespace, startFrame=currentTime())
        elif (os.path.exists(posePath)):
            pose = Pose().readXML(posePath)
            pose.goToPose(namespace)
            print 'Applying pose'
        else:
            print 'Cannot find either a pose or an animation clip named "'+poseName+'".'
            

    # Check if pose directories exist for a given character.  If not, create those directories.
    def checkForCharacterDirectories(self, charName):
    
        path = self.poseLibraryPath + charName
        
        # Create folder of object if it does not exist
        if not os.path.exists(path):
            os.mkdir(path)
            os.mkdir(os.path.join(path, 'poses'))
            os.mkdir(os.path.join(path, 'pose_images'))
            os.mkdir(os.path.join(path, 'pose_images', 'large'))
            os.mkdir(os.path.join(path, 'pose_images', 'small'))
        
    def createSaveClipWindow(self):
        '''
        Window for saving animation clips.
        '''
        
        # Save window
        if(window('SaveWindow', exists=1)): deleteUI('SaveWindow')
        saveWindow = window('SaveWindow', title = "Save Clip", s = False)
        
        mainFrame = frameLayout(bv=False, lv=False, mh=5, mw=5)
        frameLayout(bs="out", lv=False, mh=7, mw=2)
        
        layout = columnLayout(adj=True, columnAlign="left", columnOffset=("both",5), rs=3)
        
        text("Animation Clip Name:")
        clipName = textField(w=200)
        
        separator(height=20, style='in')
        
        text("Save keys from which anims?")
        whichAnims = radioButtonGrp(cw2=(90,90), adj=False, numberOfRadioButtons=2, labelArray2=['All', 'Selected'])
        whichAnims.setSelect(0)
        
        separator(height=20, style='in')
        
        text("Sample keys from what time range?")
        whichRange = radioButtonGrp(cw2=(90,90), adj=False, numberOfRadioButtons=2, labelArray2=['Time Slider', 'Start/End'])
        whichRange.setSelect(0)
        
        buttonsFrame = frameLayout(bv=False, lv=False, enable=False)
        startEndLayout = columnLayout(rs=0)
        
        rowLayout(nc=2)
        text("Start:", w=30, align="left")
        rangeStart = floatField(v=playbackOptions(q=1, min=1), pre=2)
        setParent(startEndLayout)
        
        rowLayout(nc=2)
        text("End:", w=30, align="left")
        rangeEnd = floatField(v=playbackOptions(q=1, max=1), pre=2)
        setParent(mainFrame)
        
        buttons = horizontalLayout()
        saveButton = button(label = 'Save')		
        cancelbutton = button(label = 'Cancel', c = Callback(saveWindow.delete))
        buttons.redistribute()
        
        # Callback for Start/End range enabling and disabling
        def toggleRangeEditableCallback():
            rangeOn = (whichRange.getSelect() == 2)
            buttonsFrame.setEnable(rangeOn)
        whichRange.changeCommand(Callback(toggleRangeEditableCallback))
        
        # Callback for saving out the clip
        def saveClipButtonCallback():
            name = clipName.getText()
            whichAnimsChoice = whichAnims.getSelect()
            whichRangeChoice = whichRange.getSelect()
            rangeStartValue = rangeStart.getValue()
            rangeEndValue = rangeEnd.getValue()
            self.saveClip(name, whichAnimsChoice, whichRangeChoice, rangeStartValue, rangeEndValue)
        saveButton.setCommand(Callback(saveClipButtonCallback))
        
        showWindow(saveWindow)
    
    def createSavePoseWindow(self):
        '''
        Saves the selected pose into an xml file in the pose library.
        Offers to save all anims or just the selected one.
        '''
        
        # Save window
        if(window('SaveWindow', exists=1)): deleteUI('SaveWindow')
        saveWindow = window('SaveWindow', title = "Save Pose", s = False)
        
        mainFrame = frameLayout(bv=False, lv=False, mh=5, mw=5)
        frameLayout(bs="out", lv=False, mh=7, mw=2)
        
        layout = columnLayout(adj=True, columnAlign="left", columnOffset=("both",5), rs=3)
        
        text("Pose Name:")
        poseName = textField(w=200)
        
        separator(height=20, style='in')
        
        text("Save keys from which anims?")
        whichAnims = radioButtonGrp(cw2=(90,90), adj=False, numberOfRadioButtons=2, labelArray2=['All', 'Selected'])
        whichAnims.setSelect(0)
        
        setParent(mainFrame)
        
        buttons = horizontalLayout()
        saveButton = button(label = 'Save')		
        cancelbutton = button(label = 'Cancel', c = Callback(saveWindow.delete))
        buttons.redistribute()
        
        # Callback for saving out pose
        def savePoseButtonCallback():
            name = poseName.getText()
            whichAnimsChoice = whichAnims.getSelect()
            self.savePose(name, whichAnimsChoice)
        saveButton.setCommand(Callback(savePoseButtonCallback))
        
        showWindow(saveWindow)

    
    def deleteButton(self):
        '''
        Deletes the currently selected pose, as well as the corresponding image.
        '''
    
        # Nothing to delete.  Get out of here!
        if (self.currentLibrary == None) or \
            (not self.currentLibrary in self.selectedPoseTable) or \
            (self.selectedPoseTable[self.currentLibrary] == None):
            return None
        
        poseName = self.selectedPoseTable[self.currentLibrary]
        
        # Delete confirmation dialog
        shouldDelete = confirmDialog(	title= 'Confirm', message= 'Are you sure you want to delete the pose "'+poseName+'" for the '+self.currentLibrary+' rig?',
                                        button= ['Yes', 'No'],
                                        defaultButton= 'No',
                                        cancelButton= 'No',
                                        dismissString= 'No'	)
        
        # Proceed with deletion
        if shouldDelete =='Yes':
            path = os.path.join(self.poseLibraryPath, self.currentLibrary)
            pathsToRemove = []
            pathsToRemove.append(os.path.join(path, 'poses', poseName+'.xml')) # possible pose xml path
            pathsToRemove.append(os.path.join(path, 'poses', poseName+'.anim.xml')) # possible clip xml path
            pathsToRemove.append(os.path.join(path, 'pose_images', 'small', poseName+'small.png')) # small thumbnail path
            pathsToRemove.append(os.path.join(path, 'pose_images', 'large', poseName+'large.png')) # large thumbnail path
            for p in pathsToRemove:
                if os.path.exists(p): os.remove(p)
            self.PoseEntry.selectedPoseEntry.deselect()
            self.refreshPoseLibraryGUI()
            
    # Filter out anims not from the current pose library and return the filtered list.
    def filterAnims(self, animList):
        filteredAnimSet = set()
        for a in animList:
            animCharacter = getMetaRoot(a, 'CharacterRig')
            if animCharacter != None and \
                animCharacter.getCharacterName() == self.currentLibrary and \
                not a.name().endswith("topCon") and \
                not a in filteredAnimSet: filteredAnimSet.add(a)
        return list(filteredAnimSet)

    def refreshPoseLibraryGUI(self, justSelectedPoseChanged = False):
        '''
        Refresh the Pose Library interface base on the currently selected character rig and pose.
        
        For optimization:
        - justSelectedPoseChanged won't delete the entire pose list, but will query and alter existing buttons.
        '''
    
        if justSelectedPoseChanged: return None
    
        # Updates the panel of saved images based on the character selected
        setParent(self.mainPanel)
        
        # Clear the old list panel and viewed pose
        if self.listPanel != None:
            deleteUI(self.listPanel)
            self.listPanel = None
            
        self.rigInfo.setLabel("")
        
        self.deleteButton.setVisible(False)
        self.retakeImageButton.setVisible(False)
        try:
            char = getMetaRoot(ls(sl=1)[0])
            self.currentLibrary = self.getMappedCharLibName(char.getCharacterName())
            self.rigInfo.setLabel(self.currentLibrary.replace("_", " ")+" Pose Library\n(no pose selected)")
            self.saveButtons.setVisible(True)
            self.scrollPanel.setVisible(True)
            self.leftPanelTop.setVisible(True)
            self.poseLibraryInfo.setVisible(False)
            self.filterOptions.setVisible(True)
            self.leftPanel.setHeight(h=self.largeIconSize+2*self.poseAttributesHeight)
        except:
            self.saveButtons.setVisible(False)
            self.scrollPanel.setVisible(False)
            self.leftPanelTop.setVisible(False)
            self.poseLibraryInfo.setVisible(True)
            self.filterOptions.setVisible(False)
            self.leftPanel.setHeight(self.poseLibraryTextHeight)
            return None # Selected object not part of a character
        
        # Wipe out previous pose list and entries
        if columnLayout('PoseCommandsPanel', exists=1): deleteUI("PoseCommandsPanel")
        setParent(self.scrollPanel)
        self.listColumns = 1
        self.listPanel = gridLayout(nr=1, nc=1, cw=self.listEntryWidth, vis=0)
        columnLayout()
        self.listPanel.setVisible(False)

        self.poseEntries = []
        self.PoseEntry.selectedPoseEntry = None
        
        # See if character pose directory even exists
        poseLibPath = os.path.join(self.poseLibraryPath, self.currentLibrary)
        posesPath = os.path.join(poseLibPath, 'poses')
        if not os.path.exists(posesPath):
            text(l="There are no poses saved for this rig.")
            return None # Character directory doesn't even exist
        
        # See if poses even exists
        files = os.listdir(posesPath)
        if type(files) == list: files.sort(key=lambda u: str.lower(str(u)))
        if not len(files) > 0:
            text(l="There are no poses saved for this rig.")
            return None # No poses exist
        
        # Build list of pose entries
        for f in files:
            pe = self.PoseEntry(self, poseLibPath, f)
            self.poseEntries.append(pe)
            if self.currentLibrary in self.selectedPoseTable and self.selectedPoseTable[self.currentLibrary] == pe.poseName:
                pe.select()
        
        self.filterBy(True)
        self.listPanel.setVisible(True)
    
    # Update row/column arrangement of the list panel
    # override: If True then update order of list no matter what
    def updateListPanel(self, override=False):
        if self.listPanel == None or self.listPanel == None or self.poseEntries == None: return None
        
        # Visible columns
        currentListColumns = self.scrollPanel.getWidth()/self.listEntryWidth
        
        rowsDividedEvenly = int(ceil(len(self.poseEntries)/float(currentListColumns)))
        maxRowsInScrollSpace = self.scrollPanel.getHeight()/self.listEntryHeight
        # Less entries than visible slots
        if len(self.poseEntries) < currentListColumns*maxRowsInScrollSpace:
            currentListRows = maxRowsInScrollSpace
        # More entries than visible slots
        else:
            currentListRows = rowsDividedEvenly
                
        # see if number of columns should be changed
        if override or currentListColumns != self.listColumns or currentListRows != self.listRows:

            numVisible = self.PoseEntry.numVisible
            
            self.listPanel.setCellHeight(currentListRows*self.listEntryHeight)
            
            cols = []
            
            for col in self.listPanel.getChildArray():
                col = ui.ColumnLayout(col)
                cols.append(col)
            
            # Add columns
            if currentListColumns > self.listColumns:	
                self.listPanel.setNumberOfColumns(currentListColumns)
                for c in xrange(currentListColumns-self.listColumns):
                    cols.append(columnLayout(p=self.listPanel))

            ###### CHANGING LAYOUT ######
            self.listPanel.setVisible(False)
            tc = columnLayout(p=self.scrollPanel, vis=False) # temp garbage UI element
            
            # Reorganize row/column layout
            index = 0
            for j in xrange(len(cols)):
                col = cols[j]
                localIndex = 0
                while localIndex < currentListRows and index < len(self.poseEntries):
                    if index >= len(self.poseEntries): continue
                    entry = self.poseEntries[index].poseButton
                    b = ui.IconTextButton(entry)
                    if iconTextButton(b, q=1, vis=1): localIndex += 1
                    iconTextButton(b, e=1, p=tc)
                    iconTextButton(b, e=1, p=col)
                    index += 1
                    
            deleteUI(tc)
            self.listPanel.setVisible(True)
            #### END CHANGING LAYOUT ####
            
            # Remove columns
            if currentListColumns < self.listColumns:
                self.listPanel.setNumberOfColumns(currentListColumns)
                for col in cols[currentListColumns:]:
                    deleteUI(col)
            
            self.listColumns = currentListColumns
            self.listRows = currentListRows
    
    def savePose(self, name, whichAnimsChoice):
        '''
        Save function called when the save button is pressed
        '''

        lastSelection = ls(sl=1)
        char = getMetaRoot(lastSelection[0])
        charName = self.getMappedCharLibName(char.getCharacterName())
        
        self.checkForCharacterDirectories(charName)
        
        charNamespace = getNamespace(lastSelection[0])
        
        if whichAnimsChoice == 1:
            # Use all anims
            animList = char.getAllAnims()
        else:
            # Use only selected character anims
            animList = self.filterAnims(lastSelection)
        
        # Save paths
        path = os.path.join(self.poseLibraryPath, charName)
        posePath = os.path.join(path, 'poses', name+'.xml')
        imagePath = os.path.join(path, 'pose_images')
        
        # Check for save over if the file already exists
        doSaveFile = True
        if os.path.exists(posePath):
            result = confirmDialog( title= 'Confirm', message= 'A pose or clip by this name already exists. Overwrite?', button= ['Yes', 'No'], defaultButton= 'Yes');
            if result == 'No': doSaveFile = False
        
        # The actual saving process
        if doSaveFile:
            pose = Pose().create(name, animList, currentTime())
            pose.saveToXML(posePath)
            self.takeScreenCapture(self.currentLibrary, name)
        
        # Cleanup
        select(lastSelection)
        deleteUI('SaveWindow')
        self.selectedPoseTable[self.currentLibrary] = name
        self.refreshPoseLibraryGUI()
    
    def saveClip(self, name, whichAnimsChoice, whichRangeChoice, rangeStartValue, rangeEndValue):

        lastSelection = ls(sl=1)
        char = getMetaRoot(lastSelection[0])
        charName = self.getMappedCharLibName(char.getCharacterName())
        
        self.checkForCharacterDirectories(charName)

        charNamespace = getNamespace(lastSelection[0])
        
        if whichAnimsChoice == 1:
            # Use all anims
            animList = char.getAllAnims()
        else:
            # Use only selected character anims
            animList = self.filterAnims(lastSelection)
        
        if whichRangeChoice == 1:
            # Use Time Slider range
            timeRange = (playbackOptions(q=1, min=1), playbackOptions(q=1, max=1))
        else:
            # Use specified range
            timeRange = (rangeStartValue, rangeEndValue)
        
        # Save paths
        path = os.path.join(self.poseLibraryPath, charName)
        clipPath = os.path.join(path, 'poses', name+'.anim.xml')
        imagePath = os.path.join(path, 'pose_images')
        
        # Check for save over if the file already exists
        doSaveFile = True
        if os.path.exists(clipPath):
            result = confirmDialog( title= 'Confirm', message= 'A pose or clip by this name already exists. Overwrite?', button= ['Yes', 'No'], defaultButton= 'Yes');
            if result == 'No': doSaveFile = False
        
        # The actual saving process
        if doSaveFile:
            animClip = CompactAnimationClip().create(name, animList, timeRange)
            animClip.save(clipPath)
            self.takeScreenCapture(self.currentLibrary, name)
        
        # Cleanup
        select(lastSelection)
        deleteUI('SaveWindow')
        self.selectedPoseTable[self.currentLibrary] = name
        self.refreshPoseLibraryGUI()
    
    # Don't refresh the GUI if it's the same Pose Library
    def selectionChangeRefreshGUI(self):
        try:
            selected = ls(sl=1)
            if len(selected) == 0:
                thisLibrary = None
            else:
                char = getMetaRoot(selected[0])
                thisLibrary = char.getCharacterName()
        except:
            thisLibrary = None
            
        if thisLibrary == self.lastSelectionChangeLibrary:
            return None
            
        self.refreshPoseLibraryGUI()
        self.lastSelectionChangeLibrary = thisLibrary
    
    def takeScreenCapture(self, charName, poseName):
        '''
        Capture small and large thumbnails for the character's given pose.
        '''
        
        smallImagePath = os.path.join(self.poseLibraryPath, charName, "pose_images", "small", poseName+"small")
        largeImagePath = os.path.join(self.poseLibraryPath, charName, "pose_images", "large", poseName+"large")
        
        renderGlobs = PyNode("defaultRenderGlobals")
        
        # SAVE STATE AND HIDE ANIMS
        ############################
        # Store current image format, set current to png
        currentFormat = renderGlobs.imageFormat.get()
        renderGlobs.imageFormat.set(32)
        # Deselect selected objects
        selected = ls(sl=1)
        select(cl=1)
        # Hide anim shapes
        anims = ls("*_topCon", r=1) + ls("*_anim*", r=1, typ="joint") + ls("*_anim*", r=1, typ="mesh") + ls("*_switch*", r=1, typ="mesh")
        if len(anims) > 0: anim_shapes = listRelatives(anims, s=1, f=1)
        else: anim_shapes = []
        if (len(anim_shapes) > 0): hide(anim_shapes)
        # Hide everything but polygons in the active view
        meState = None
        try:
            p = getPanel(wf=1)
            meState = modelEditor(p, q=1, sts=1)
            modelEditor(p, e=1, alo=0) # show none
            modelEditor(p, e=1, pm=1) # show polygons
        except Exception as e:
            """ Do nothing. The panel with focus is not a model editor. """
        ############################

        try:
            toPlayblast = [(smallImagePath, self.smallIconSize), (largeImagePath, self.largeIconSize)]
            
            for (imagePath, imageSize) in toPlayblast:
                playblast(	frame=currentTime(),
                            os=True,
                            w=imageSize,
                            h=imageSize,
                            format='image',
                            compression='png',
                            orn=False,
                            viewer=False,
                            fo=True,
                            fp=0,
                            f=imagePath,
                            p=100	)
                if os.path.exists(imagePath+".png"): os.remove(imagePath+".png")
                os.rename(imagePath+".0.png", imagePath+".png")

        except Exception as e:
            print "Error taking screen captures for "+charName+"'s pose "+poseName+":"
            print e
        
        # RESTORE STATE AND SHOW ANIMS
        ###############################
        renderGlobs.imageFormat.set(currentFormat)
        if (len(anim_shapes) > 0): showHidden(anim_shapes)
        if (meState != None): mel.eval(meState.replace("$editorName", p))
        select(selected)
        ###############################
        
    # POSE LIST ENTRY
    # Class representing an entry in the pose list for easier manipulation, sorting, query-ability, etc.
    class PoseEntry():
    
        # Global pose entry attributes
        poseNormalColor = (.1, .1, .1)
        poseSelectColor = (.2, .7, .2)
        clipNormalColor = (.0, .3, .3)
        clipSelectColor = (.0, .8, .4)
        poseLibControl = None
        selectedPoseEntry = None
        numVisible = 0
    
        # PoseEntry attributes
        poseLibPath = None
        poseFileName = None
        poseName = None
        isAnimationClip = None
        poseButton = None
        isVisible = None
        

        # poseLibControl: Main PoseLibWindow instance
        # poseLibPath: Path to the root of this character's pose library
        # poseFileName: File name of this pose
        def __init__(self, poseLibControl, poseLibPath, poseFileName):
            self.poseLibControl = poseLibControl
            self.poseLibPath = poseLibPath
            self.poseFileName = poseFileName
            self.poseName = poseFileName.split('.')[0]
            self.isAnimationClip = poseFileName.endswith(".anim.xml")
                
            # Image displayed on the entry
            smallImagePath = os.path.join(poseLibPath, "pose_images", "small", self.poseName+"small.png")
            if not os.path.exists(smallImagePath): smallImagePath = 'ghostOff.png'
            
            # Button label
            if self.isAnimationClip:
                buttonLabel = self.poseName+" (Clip)"
            else:
                buttonLabel = self.poseName
            
            # Button representing this pose in the list
            #setParent(self.poseLibControl.listPanel)
            self.poseButton = iconTextButton(	style="iconAndTextHorizontal",
                                                i=smallImagePath,
                                                label=buttonLabel,
                                                w=poseLibControl.listEntryWidth-10,
                                                h=poseLibControl.listEntryHeight,
                                                ebg=True,
                                                bgc=self.getNormalColor(),
                                                c=Callback(self.select)	)
            
            self.isVisible = True
            self.__class__.numVisible += 1
            
        # Select this pose
        def select(self):
            if self.__class__.selectedPoseEntry != None: self.__class__.selectedPoseEntry.deselect()
            self.__class__.selectedPoseEntry = self
            self.poseLibControl.selectedPoseTable[self.poseLibControl.currentLibrary] = self.poseName
            self.poseLibControl.rigInfo.setLabel(self.poseLibControl.currentLibrary+" Pose Library:\n"+self.poseName+"")
            self.poseButton.setBackgroundColor(self.getSelectedColor())
            self.__setPoseCommandsPanel()
        
        # Deselect this pose
        def deselect(self):
            if self.__class__.selectedPoseEntry == self:
                self.__class__.selectedPoseEntry = None
                self.poseLibControl.selectedPoseTable[self.poseLibControl.currentLibrary] = None
                if columnLayout('PoseCommandsPanel', exists=1): deleteUI("PoseCommandsPanel")
                self.poseButton.setBackgroundColor(self.getNormalColor())
        
        # Return normal color
        def getNormalColor(self):
            if self.isAnimationClip:
                return self.__class__.clipNormalColor
            else:
                return self.__class__.poseNormalColor
        
        # Return selected color
        def getSelectedColor(self):
            if self.isAnimationClip:
                return self.__class__.clipSelectColor
            else:
                return self.__class__.poseSelectColor
        
        # Sets the main command window to the information of this pose
        def __setPoseCommandsPanel(self):
            bigImagePath = os.path.join(self.poseLibPath, "pose_images", "large", self.poseName+"large.png")
            
            setParent(self.poseLibControl.leftPanel)
            
            if columnLayout('PoseCommandsPanel', exists=1): deleteUI("PoseCommandsPanel")
            self.poseLibControl.poseCommands = columnLayout(	'PoseCommandsPanel',
                                                                adj=True,
                                                                cal='center',
                                                                cat=('both',0)	)
            
            if os.path.exists(bigImagePath):
                image(i=bigImagePath)
            else:
                text("No pose image found.", w=self.poseLibControl.largeIconSize, h=self.poseLibControl.largeIconSize, bgc=(.4,.4,.4), align="center")
            
            applyButtons = horizontalLayout()
            applyButtons.setHeight(self.poseLibControl.poseAttributesHeight)
            
            frameLayout(mh=5, mw=5, bv=False, lv=False)
            applyButton = iconTextButton(	ebg=True,
                                            st="iconAndTextHorizontal",
                                            h=self.poseLibControl.poseAttributesHeight,
                                            c=Callback(self.poseLibControl.applySelectedPoseOrClip)	)
            
            if self.isAnimationClip:
                def changeApplyClipLabelCallback():
                    applyButton.setLabel('       Apply Clip -> Starting at frame '+str(currentTime()))
                applyButton.setImage('ghost.png')
            else:
                def changeApplyClipLabelCallback():
                    applyButton.setLabel('       Apply Pose -> On frame '+str(currentTime()))
                applyButton.setImage('ghostOff.png')
                    
            changeApplyClipLabelCallback()
            scriptJob(p=applyButton, e=("timeChanged", Callback(changeApplyClipLabelCallback)))
            
            '''
            frameLayout(p=applyButtons, mh=5, mw=5, bv=False, lv=False)
            
            blendButton = button(   ebg=True,
                                    l="Blend",
                                    h=self.poseLibControl.poseAttributesHeight,
                                    c=Callback(self.poseLibControl.applyPoseBlend) )
            
            applyButtons.redistribute(7,1)
            '''
            
            applyButtons.redistribute()
            
            self.poseLibControl.deleteButton.setVisible(True)
            self.poseLibControl.retakeImageButton.setVisible(True)
        
        # Hide button if it doesn't meet certain constraints
        def filterBy(self, isAnimationClip=None, nameFilter=None):
            if ((self.isAnimationClip and isAnimationClip == False) or
                (not self.isAnimationClip and isAnimationClip == True) or
                (nameFilter != None and nameFilter != "" and not (nameFilter.lower() in self.poseName.lower()))):
                if self.isVisible: self.__class__.numVisible += -1
                self.isVisible = False
                self.poseButton.setVisible(False)
            else:
                if not self.isVisible: self.__class__.numVisible += 1
                self.isVisible = True
                self.poseButton.setVisible(True)