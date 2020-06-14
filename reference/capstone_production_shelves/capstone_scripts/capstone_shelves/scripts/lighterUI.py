import maya.cmds as mc; import maya.mel; from functools import partial;
class Lighter():
    widgets = {};
    def __init__(self,*arg):
        if mc.window('Lights',ex=True):
            mc.deleteUI('Lights')
        lTypes = ['point','spot','directional','ambient','area','volume'];
        self.widgets['win'] = mc.window('Lights',t='Lighter UI',wh=(400,500),s=False);
        self.widgets['main'] = mc.columnLayout(w=400,h=625,p=self.widgets['win']);
        self.widgets['column'] = mc.scrollLayout(w=400,h=400,p=self.widgets['main']);
        self.widgets['mainButtons'] = mc.rowColumnLayout(nc=2,w=400,h=125,p=self.widgets['main'])
        mc.text(l='Amount',p=self.widgets['mainButtons']); self.widgets['amount'] = mc.intField(v=1,min=1,max=20,p=self.widgets['mainButtons'])
        for all in lTypes:
            self.widgets['create'+all.title()] = mc.button(l=('Create '+all.title()+' Lights'),
                w=200,h=35,c=partial(self.createLights,all),p=self.widgets['mainButtons']);
        self.widgets['deleteAll'] = mc.button(l='Delete All Lights',w=400,h=50,c=self.delAllLights,p=self.widgets['main'])
        self.widgets['refresh'] = mc.button(l='Refresh',w=400,h=50,c=self.refresher,p=self.widgets['main']);
        mc.showWindow(self.widgets['win']); self.lightSetup();
    def lightSetup(self,*arg):
        lights = mc.ls(lt=True,dag=True);
        for all in lights:
            n = all.replace('Shape',''); title = n.replace('_',' '); i=0; dOpt =['No Decay','Linear','Quadratic','Cubic']
            self.widgets[all+'Settings'] = mc.columnLayout(w=375,p= self.widgets['column']);
            self.widgets[all+'Controls'] = mc.frameLayout(w=375,l=(title.title()+' Settings'),cl=True,cll=True,p= self.widgets[all+'Settings']);
            self.widgets[all+'Color'] = mc.colorSliderGrp(l='Color       ',cw=(1,75),p=self.widgets[all+'Controls']);
            self.widgets[all+'Intensity'] = mc.floatSliderGrp(l=' Intensity  ',pre=3,fmx=1000,cw=(1,75),min=0,max=10.00,p=self.widgets[all+'Controls'],f=True);
            if mc.nodeType(all)=='spotLight':
                self.widgets[all+'ConeAngle'] = mc.floatSliderGrp(l='Cone Angle',pre=3,cw=(1,100),min=0,max=180,p=self.widgets[all+'Controls'],f=True);
                self.widgets[all+'PenAngle'] = mc.floatSliderGrp(l='Penumbra Angle',pre=3,cw=(1,100),fmx=100,min=0,max=20,p=self.widgets[all+'Controls'],f=True);
                mc.connectControl(self.widgets[all+'ConeAngle'],(all+'.coneAngle')); mc.connectControl(self.widgets[all+'PenAngle'],(all+'.penumbraAngle'));  
            if mc.nodeType(all)!='directionalLight':
                self.widgets[all+'Decay'] = mc.optionMenu(l='Decay Rate  ',p=self.widgets[all+'Controls']);
                for o in dOpt:
                    mc.menuItem(da=i,l=o,p=self.widgets[all+'Decay']); i=i+1;
                mc.connectControl(self.widgets[all+'Decay'],(all+'.decayRate'));
            self.widgets[all+'ShadOptions'] =mc.rowColumnLayout(nc=2,w=375,p=self.widgets[all+'Controls']);
            mc.separator(vis=True,p=self.widgets[all+'Controls'])
            self.widgets[all+'ShadColor'] = mc.colorSliderGrp(l='Shadow Color  ',cw=(1,100),p=self.widgets[all+'Controls']);
            self.widgets[all+'ShadSettings'] = mc.columnLayout(w=375,p=self.widgets[all+'Controls']);
            mc.separator(vis=True,p=self.widgets[all+'Controls']);
            if mc.nodeType(all)!='ambientLight':
                self.widgets[all+'DmShad'] = mc.checkBox(l='Depth Map',v=False,cc=partial(self.shadows,all),p=self.widgets[all+'ShadOptions']);
                self.widgets[all+'DmOpts'] = mc.columnLayout(w=375,p=self.widgets[all+'Controls']);
                self.widgets[all+'DmRes'] = mc.intSliderGrp(l='Resolution',cw=(1,100),min=16,max=4096,p=self.widgets[all+'DmOpts'],f=True);
                self.widgets[all+'DmFilSize'] = mc.intSliderGrp(l='Filter Size',cw=(1,100),min=1,max=5,p=self.widgets[all+'DmOpts'],f=True);
                mc.connectControl(self.widgets[all+'DmShad'],(all+'.useDepthMapShadows')); mc.connectControl(self.widgets[all+'DmRes'],(all+'.dmapResolution'));
                mc.connectControl(self.widgets[all+'DmFilSize'],(all+'.dmapFilterSize')); mc.separator(vis=True,p=self.widgets[all+'Controls']);
            self.widgets[all+'RtShad'] = mc.checkBox(l='Ray Trace',v=False,cc=partial(self.shadows,all),p=self.widgets[all+'ShadOptions']);
            self.widgets[all+'RtOpts'] = mc.columnLayout(w=375,p=self.widgets[all+'Controls']);
            self.widgets[all+'RtLightRad'] = mc.floatSliderGrp(l='Light Radius',pre=3,cw=(1,100),fmx=100,min=0,max=50,p=self.widgets[all+'RtOpts'],f=True);
            self.widgets[all+'RtShadRays'] = mc.intSliderGrp(l='Shadow Rays',cw=(1,100),fmx=100,min=0,max=40,p=self.widgets[all+'RtOpts'],f=True);
            self.widgets[all+'RtDepthLimit'] = mc.intSliderGrp(l='Ray Depth Limit',cw=(1,100),fmx=100,min=0,max=10,p=self.widgets[all+'RtOpts'],f=True);
            self.widgets[all+'Name'] = mc.textFieldButtonGrp(l='Name       ',bl='>>>',cw=(1,70),bc=partial(self.name,all),p=self.widgets[all+'Settings']);
            self.widgets[all+'Buttons'] = mc.rowColumnLayout(nc=2,w=375,p= self.widgets[all+'Settings']);
            self.widgets[all+'Select'] = mc.button(l='Select',w=175,h=25,c=partial(self.selectLight,all),p=self.widgets[all+'Buttons']); 
            self.widgets[all+'Delete'] = mc.button(l='Delete',w=175,h=25,c=partial(self.delLight,all),p=self.widgets[all+'Buttons']); 
            self.widgets[all+'Link'] = mc.button(l='Link To Selected Objects',w=175,h=25,c=partial(self.linkToObjs,all,'link'),p=self.widgets[all+'Buttons']); 
            self.widgets[all+'Unlink'] = mc.button(l='Unlink To Selected Objects',w=175,h=25,c=partial(self.linkToObjs,all,'unlink'),p=self.widgets[all+'Buttons']);
            mc.connectControl(self.widgets[all+'Color'],(all+'.color')); mc.connectControl(self.widgets[all+'Intensity'],(all+'.intensity'));
            mc.connectControl(self.widgets[all+'RtShad'],(all+'.useRayTraceShadows')); mc.connectControl(self.widgets[all+'ShadColor'],(all+'.shadowColor'));
            mc.connectControl(self.widgets[all+'RtLightRad'],(all+'.lightRadius')); mc.connectControl(self.widgets[all+'RtShadRays'],(all+'.shadowRays'));
            mc.connectControl(self.widgets[all+'RtDepthLimit'],(all+'.rayDepthLimit')); self.shadows(all);
    def linkToObjs(self,light,link,*arg):
        stuff = mc.ls(sl=True); list = mc.filterExpand(stuff,sm=12);
        try:
            str =mc.attributeQuery('unlinked',n=light,listEnum=True)[0];
            if list == None:
                warning = mc.confirmDialog(t='Error',m=('Please select geometry.'),b=['OK'],cb='OK');
            else:
                for all in list:
                    if link == 'link':
                        mc.lightlink(b=False,light = light, object = all);
                        if str != 'None':
                            str = str.replace(("'"+all+"'"),'');
                            str = str.replace(',,',',');
                    else:
                        mc.lightlink(b=True,light = light, object = all);
                        str = str+",'"+all+"'";
                        str= str.replace('None,','');
                    if str.startswith(','):
                        str = str[1:];
                    if str.endswith(','):
                        str = str[0:-1];
                    if str == '' or str == ',':
                        str = 'None';
                    mc.addAttr((light+'.unlinked'),e=True, en=(str+':'))
        except:
            pass;
    def shadows(self,n,*arg):
        if mc.nodeType(n)!='ambientLight': 
            if mc.getAttr(n+'.useDepthMapShadows')==False:
                mc.disable(self.widgets[n+'DmOpts']);
            if mc.getAttr(n+'.useRayTraceShadows')==False:
                mc.disable(self.widgets[n+'RtOpts']);
            if mc.getAttr(n+'.useDepthMapShadows')==True:
                mc.disable(self.widgets[n+'DmOpts'],v=False); mc.disable(self.widgets[n+'ShadColor'],v=False);
                
            if mc.getAttr(n+'.useRayTraceShadows')==True:
                mc.disable(self.widgets[n+'RtOpts'],v=False); mc.disable(self.widgets[n+'ShadColor'],v=False);
            if mc.getAttr(n+'.useDepthMapShadows')==False and mc.getAttr(n+'.useRayTraceShadows')==False:
                mc.disable(self.widgets[n+'ShadColor']);
        else:
            if mc.getAttr(n+'.useRayTraceShadows')==False:
                mc.disable(self.widgets[n+'RtOpts']); mc.disable(self.widgets[n+'ShadColor']);
            if mc.getAttr(n+'.useRayTraceShadows')==True:
                mc.disable(self.widgets[n+'RtOpts'],v=False); mc.disable(self.widgets[n+'ShadColor'],v=False);
    def name(self,n,*arg):
        newName = mc.textFieldButtonGrp(self.widgets[n+'Name'],q=True,tx=True); newName = newName.replace(' ','_')
        if newName != '':
            name = n.replace('Shape',''); mc.rename(name,newName); Lighter();
    def refresher(self,*arg):
        Lighter();
    def delLight(self,n,*arg):
        name = n.replace('Shape',''); mc.delete(name); Lighter();
    def delAllLights(self,*arg):
        ask = mc.confirmDialog(t='WARNING',m=('Are you sure you want to delete all lights in your scene?'),b=['Yes','No'],cb='No');
        if ask == 'Yes':
            lights = mc.ls(lt=True,dag=True);
            for all in lights:
                name = all.replace('Shape',''); mc.delete(name); mc.select(cl=True);
            Lighter();
    def selectLight(self,n,*arg):
        name = n.replace('Shape',''); mc.select(name);
    def createLights(self,type,*arg):
        i=1; amnt = mc.intField(self.widgets['amount'],q=True,v=True);
        while i < (amnt+1):
		    if type == 'point' or type == 'spot' or type == 'directional' or type == 'ambient':
		        exec('mc.'+type+'Light(rs=False)'); mc.select(cl=True); i=i+1;
		    else:
		        mc.shadingNode((type+'Light'),asLight = True); mc.select(cl=True); i=i+1;
		    #self.relinked();
        Lighter();
    
    def relinked(self,*arg):
        lights = mc.ls(lt=True,dag=True);
        for all in lights:
            items = mc.attributeQuery('unlinked',n=all,listEnum = True)[0];
            if items != 'None':
                exec('mc.select('+items+')'); list = mc.ls(sl=True);
                for all in list:
                    if mc.objExists(all)==True:
                        self.linkToObjs(all,'unlink');
                        
Lighter();