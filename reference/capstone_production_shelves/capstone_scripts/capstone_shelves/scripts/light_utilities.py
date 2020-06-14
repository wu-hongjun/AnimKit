from pymel.core import *

def make_shadow_light(light):
    '''
    Convert a selected light into a "shadow light", which is a light that
    casts a shadow without any illumination.
    '''
    NEGATIVE_LIGHT_NAME = "DO_NOT_TOUCH_negative_light"

    for c in light.getChildren():
        if NEGATIVE_LIGHT_NAME in c.shortName():
            delete(c)
            break

    lightShape = ls(light.getChildren(), lt=1)[0]
    dupLight = duplicate(light)[0]
    dupLightShape = ls(dupLight.getChildren(), lt=1)[0]
    dupLightShape.rename(NEGATIVE_LIGHT_NAME)
    
    def connectAttrs(fromThis, toThat):
        for attr in fromThis.listAttr(c=1, k=1):
            attrName = attr.name().split('.')[-1]
            if (toThat.hasAttr(attrName)):
                toThatAttr = Attribute(toThat.name() + '.' + attrName)
                attr.connect(toThatAttr, f=1)
                
    connectAttrs(lightShape, dupLightShape)
    parent(dupLight, light)
    dupLight.translate.set([0,0,0])
    dupLight.rotate.set([0,0,0])
    dupLight.scale.set([1,1,1])
    parent(dupLightShape, light, s=1, add=1)
    
    # set attributes for original light
    lightShape.useRayTraceShadows.set(True)
    dupLightShape.useRayTraceShadows.disconnect()
    dupLightShape.useRayTraceShadows.set(False)
    md = createNode("multiplyDivide", n=light.name()+"_md")
    
    # reverse the intensity
    lightShape.intensity.connect(md.input1X)
    md.input2X.set(-1)
    md.outputX.connect(dupLightShape.intensity, f=1)
    
    # delete duplicate light transform
    delete(dupLight)
    
def safe_delete_light(selection):
    '''
    Safely delete any selected lights from a scene.  Normally deleting a light coupled
    with referencing has the chance of corrupting your file upon trying to save.
    '''
    
    transforms = filter(lambda s: isinstance(s, nt.Transform), selection)
    
    for t in transforms: 
        # Check if this is a valid light
        lightShapes = ls(t.getChildren(), lt=1)
        if (not len(lightShapes) > 0):
            print '"'+str(t)+'" is not a valid light. Skipping.'
            continue
            
        # Check if referenced
        if (t.isReferenced()):
            print '"'+str(t)+'" is a referenced light and cannot be deleted. Skipping.'
            continue
        
        deletedLightName = t.name()
        print "DELETING LIGHT: "+deletedLightName
        # Unlink it from everything
        print "--- Breaking all light links."
        objectLinks = lightlink(light=t, q=1)
        for obj in objectLinks:
            lightlink(b=True, light=t, object=obj)
        # In the light linker, any time this light is connected to an attribute -- sever that
        # connection and also sever any other connections to that light linker attribute
        print "-- Severing all light linker connections."
        for ll in ls(type="lightLinker"):
            for attr in ll.listAttr():
                try:
                    connections = attr.listConnections()
                    for possibleConnection in [t]+lightShapes:
                        if possibleConnection in connections:
                            attr.unlock()
                            attr.disconnect()
                except:
                    continue
        # Sever connections to other objects in the scene (anything not related to the light linker)
        print "- Severing all other attribute connections."
        for attr in t.listAttr(): # main light transform
            try:
                attr.unlock()
                attr.disconnect()
            except: continue
        for l in lightShapes:
            for attr in l.listAttr(): # light shapes
                try:
                    attr.unlock()
                    attr.disconnect()
                except: continue
        # GOODBYE LIGHT. YOU WILL PLAGUE US NO MORE!
        delete (t)
        print "Light deleted."
        

        
def make_shadow_light_cmd():
    make_shadow_light(ls(sl=1)[0])
    
def safe_delete_light_cmd():
    selection = ls(sl=1)
    if (len(selection) > 0): safe_delete_light(selection)