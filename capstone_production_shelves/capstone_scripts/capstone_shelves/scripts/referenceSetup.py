from pymel.all import *
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI


''' METHODS '''

def reference_planes(sideImagePath=None, frontImagePath=None):

    # Use a temporary namespace to prevent weird name clash errors
    ns = namespace(addNamespace="tempReferencePlaneConstructionNS")
    namespace(set=ns)
    
    # Make anim used to move reference planes
    refAnim = curve(p=[(-.5,0,0),(.5,0,0)], degree=1, name="reference_handle")
    for a in ['tx', 'rx', 'ry', 'rz', 'sz']:
        setAttr(refAnim.attr(a), l=1, k=0, cb=0)
        
    # Double the reference anims for the front and the side
    refAnimFrontGrp = group(refAnim, name="reference_handle_front_grp")
    refAnimSideGrp = instance(refAnimFrontGrp, name="reference_handle_side_grp")[0]

    # Orient the anims so positive z movement is outwards
    refAnimFrontGrp.ry.set(180)
    refAnimSideGrp.ry.set(-90)

    # Create and constrain planes
    frontPlane = polyPlane(w=1, h=1, sw=1, sh=1, n="front_ref_geo")[0]
    polyNormal(frontPlane, normalMode=0, ch=0) # Reverse normal on plane
    frontPlane.tz.set(-.5)
    xform(frontPlane, rp=[0,0,0], ws=1)
    xform(frontPlane, sp=[0,0,0], ws=1)
    frontPlane.rx.set(90)
    makeIdentity(frontPlane, t=1, r=1, s=1, a=1)

    sidePlane = duplicate(frontPlane, n="side_ref_geo")[0]

    parentConstraint(refAnim, frontPlane, mo=0)
    scaleConstraint(refAnim, frontPlane, mo=0)

    otherRefAnim = refAnimSideGrp.getChildren()[0]
    parentConstraint(otherRefAnim, sidePlane, mo=0)
    scaleConstraint(otherRefAnim, sidePlane, mo=0)
    
    for p in [frontPlane, sidePlane]:
        for a in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            setAttr(p.attr(a), l=1, k=0, cb=0)

    # Set default plane position
    refAnim.tz.set(1)

    # Organize under root group
    rootGrp = group([refAnimFrontGrp, refAnimSideGrp, frontPlane, sidePlane], n="reference_planes_grp")
    
    
    # Create display layer for planes
    namespace(set=":")
    if objExists('reference_lyr'):
        editDisplayLayerMembers('reference_lyr', [frontPlane, sidePlane])
    else:
        createDisplayLayer([frontPlane, sidePlane], n='reference_lyr')
    PyNode('reference_lyr').displayType.set(2)
    namespace(set=ns)
    
    # Add slider system
    namespace(set=":")
    faderRetArgs = transparency_fader( [frontPlane, sidePlane] )
    faderRoot = faderRetArgs[0]
    shaders = faderRetArgs[1]
    faderAnim = selected()[0]
    select(d=1)
    parent(faderRoot, rootGrp)
    
    # Assign texture files to planes if specified
    if (frontImagePath != None):
        s = shaders[0]
        sFile = shadingNode("file", asTexture=1)
        sFile.fileTextureName.set(frontImagePath)
        sFile.outColor.connect(s.color)
        
    if (sideImagePath != None):
        s = shaders[1]
        sFile = shadingNode("file", asTexture=1)
        sFile.fileTextureName.set(sideImagePath)
        sFile.outColor.connect(s.color)
   
    namespace(set=ns)
    
    # Adjust slider default location and constrain it to the image plane handles
    faderRoot.inheritsTransform.set(0)
    faderAnim.ControlMoverVisibility.set(0)
    faderRoot.ty.set(.333*faderRoot.ty.get())
    
    frontPlaneLoc = spaceLocator(n="front_plane_loc")
    hide(frontPlaneLoc)
    parent(frontPlaneLoc, rootGrp)
    pointConstraint(refAnim, frontPlaneLoc)
    
    sidePlaneLoc = spaceLocator(n="side_plane_loc")
    sidePlaneLocGrp = group(em=1, n="side_plane_loc_grp")
    sidePlaneLocGrp.ry.set(180)
    parent(sidePlaneLoc, sidePlaneLocGrp)
    hide(sidePlaneLocGrp)
    parent(sidePlaneLocGrp, rootGrp)
    pointConstraint(otherRefAnim, sidePlaneLoc)

    sidePlaneLoc.tx >> faderRoot.tx
    frontPlaneLoc.tz >> faderRoot.tz
    
    refAnim.sx >> faderRoot.sx
    refAnim.sy >> faderRoot.sy
    refAnim.sx >> faderRoot.sz
    
    # We're done with the temporary namespace
    namespace(f=1, set=":")
    namespace(f=1, mv=(ns, ":"))
    namespace(f=1, rm=ns)
    
    
    

def transparency_fader( polyObjs, useConstraint=False ):
    
    ## CURVE CREATION AND MODIFICATION METHODS ##
    
    def createCurve_DownArrow(name="downArrowCurve"):
        c = curve(n=name, d=1, p= ( [0.5, 0, 0], [0.5, -1, 0], [1, -1, 0], [0, -2, 0],\
                                    [-1, -1, 0], [-0.5, -1, 0], [-0.5, 0, 0], [0.5, 0, 0]))
        return c
    
    def twistShapeAndCombine(obj):
        objDup = duplicate(obj)[0]
        objDup.ry.set(90)
        makeIdentity(objDup, a=1)
        objDupShape = objDup.getShape()
        parent(objDupShape, obj, s=1, add=1)
        delete(objDup)
        return obj
        
    
    ## SETUP SLIDER BASED ON FIRST SELECTED POLYGON OBJECT ##
    
    polyObj = polyObjs[0]
    
    # Get bounds of polygon object, use to determine fader position and scale    
    bounds = polyEvaluate(polyObj, b=1)
    distance = math.sqrt((bounds[0][0] - bounds[0][1])**2 + (bounds[1][0] - bounds[1][1])**2)
    FADER_SIZE = distance / 3.0
    FADER_SCALE = FADER_SIZE / 7.0
    faderPos = [bounds[0][1] + (FADER_SIZE / 3.0), bounds[1][1] + (FADER_SIZE / 3.0), bounds[2][1]]
    
    # Create fader control
    ctrlFader = circle(n='transparency_fader')[0]
    
    twistShapeAndCombine(ctrlFader)
    
    ctrlFader.translate.set(faderPos)
    ctrlFader.scale.set(FADER_SCALE, FADER_SCALE, FADER_SCALE)
    makeIdentity(ctrlFader, a=1, t=0, r=1, s=1)
    
    # Create fade slider movement control
    ctrlMover = twistShapeAndCombine(createCurve_DownArrow('transparency_fader_mover'))
    
    ctrlMover.translate.set(faderPos)
    ctrlMover.scale.set(FADER_SCALE, FADER_SCALE, FADER_SCALE)
    makeIdentity(ctrlMover, a=1, t=0, r=1, s=1)
    
    # Create fader curve
    faderCurve = curve(n='transparency_fader_curve', d=1, p=[(faderPos[0], faderPos[1], faderPos[2]),\
     (faderPos[0], faderPos[1] + FADER_SIZE, faderPos[2])], k=[0,1])
    faderCurve.attr('overrideEnabled').set(1)
    faderCurve.attr('overrideDisplayType').set(2)
    
    # Create fader top groups
    transpGroup = group(n='transparency_slider', em=1)
    transpGroup.translate.set(faderPos)
    faderCtrlGroup = group(n='fader_control_group', em=1)
    faderCtrlGroup.scale.set(FADER_SIZE, FADER_SIZE, FADER_SIZE)
    faderCtrlGroup.translate.set(faderPos)
    
    # Arrange the parent hierarchy
    parent(faderCurve, faderCtrlGroup)
    parent(ctrlFader, faderCtrlGroup)
    parent(faderCtrlGroup, transpGroup)
    parent(ctrlMover, transpGroup)
    parentConstraint(ctrlMover, faderCtrlGroup, mo=1)
    
    # Lock uneeded attributes and set translate limits on the faders controls
    transforms = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    
    for trans in transforms:
        ctrlFader.attr(trans).set(lock=1, keyable=0, cb=0)
        faderCurve.attr(trans).set(lock=1, keyable=0, cb=0)
    
    ctrlFader.ty.set(lock=0, keyable=0, cb=1)
    ctrlFader.visibility.set(lock=1, keyable=0, cb=0)
    
    transformLimits(ctrlFader, ety=(1, 1), ty=(0, 1))
    
    # Lock uneeded attributes on the fader mover
    for trans in ['sx', 'sy', 'sz']:
        ctrlMover.attr(trans).set(lock=1, keyable=0, cb=0)
    
    for trans in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
        ctrlMover.attr(trans).set(lock=0, keyable=0, cb=1)
        
    # Lock uneeded attributes on the fader control group
    for trans in transforms+["visibility"]:
        faderCtrlGroup.attr(trans).set(lock=1, keyable=0, cb=0)
        
    # Connect visibility of control mover to a custom attribute on the fader control
    ctrlFader.addAttr("ControlMoverVisibility", at="bool", dv=1)
    ctrlFader.ControlMoverVisibility.connect(ctrlMover.visibility)
    ctrlFader.ControlMoverVisibility.set(lock=0, keyable=0, cb=1)
    ctrlMover.visibility.set(lock=1, keyable=0, cb=0)
    
    ## useConstraint FLAG ##
    # Constrain fader to polygon object
    if (useConstraint): parentConstraint(polyObj, transpGroup, mo=1)
    
    # Set default control position to half
    ctrlFader.ty.set(.5)
    
    
    ## CONNECT SLIDER TO SHADERS ##
    
    shaders = []
    
    for polyObj in polyObjs:
        
        # Get polygon's shader
        shEng = polyObj.listRelatives(c=1, s=1)[0].listConnections(t='shadingEngine')[0]
        shader = listConnections(shEng.name() + ".surfaceShader")
        
        # Creates a new shader if there is none or is using lambert1
        if not shader or 'lambert1' == shader[0]:
            shader = shadingNode('lambert', asShader=1, n = polyObj.name() + '_transparency_slider_shader');
            shader.diffuse.set(1)
            select(cl=1)
            select(polyObj)
            hyperShade(assign = shader)
        else:
        	shader = shader[0]
        shaders.append(shader)
        
        shader.transparency.disconnect()
        
        # Fader control's translate y drives transparency of shader
        for colorAttr in [shader.transparencyR, shader.transparencyG, shader.transparencyB]:
            setDrivenKeyframe(colorAttr, cd=ctrlFader.ty, dv=1, v=0, itt="linear", ott="linear")
            setDrivenKeyframe(colorAttr, cd=ctrlFader.ty, dv=0, v=1, itt="linear", ott="linear")
            
    # Select the fader
    select(ctrlFader)
    return [transpGroup, shaders]

''' COMMANDS '''
    
def transparency_fader_cmd():
    
    polyObjs = filter(lambda obj: 'mesh' == nodeType(obj.listRelatives(c=1, s=1)[0]), ls(sl=1))
    
    if len(polyObjs) > 0:
        transparency_fader(polyObjs)
    else:
        raise Exception('Select at least one polygon object.')
        
def reference_planes_cmd():

    reference_planes()
    
def reference_planes_gui_cmd():

    ICON_SIZE = 175

    # Close an already open window
    if window('crprOptions', q=1, exists=1):
        deleteUI('crprOptions')
        
    # Destroy window prefs
    if windowPref('crprOptions', ex=1):
        windowPref('crprOptions', r=1)
        
        
    w = window('crprOptions', t='Create Reference Plane Rig', rtf=0, s=0, width=350, height=315)
    mainLayout = columnLayout(adj=1)

    text('Create a resizable reference plane "rig" that has a fader control. You may specify the front '+\
         'and back images now or assign them later.', al='left', ww=1)


    # Front/side buttons
    imgs = formLayout(p=mainLayout, h=ICON_SIZE+25)

    sideImg = iconTextButton(p=imgs, i="img_ref_set_side.png",w=ICON_SIZE,h=ICON_SIZE)
    frontImg = iconTextButton(p=imgs, i="img_ref_set_front.png",w=ICON_SIZE,h=ICON_SIZE)
    sideLbl = text(l="SIDE", fn='boldLabelFont', w=ICON_SIZE)
    frontLbl = text(l="FRONT", fn='boldLabelFont', w=ICON_SIZE)

    imgs.attachForm(sideImg, 'top', 0)
    imgs.attachForm(sideImg, 'left', 0)
    imgs.attachControl(sideImg, 'bottom', 0, sideLbl)
    imgs.attachForm(sideLbl, 'bottom', 0)

    imgs.attachForm(frontImg, 'top', 0)
    imgs.attachForm(frontImg, 'right', 0)
    imgs.attachControl(frontImg, 'bottom', 0, frontLbl)
    imgs.attachForm(frontLbl, 'bottom', 0)

    imgs.attachControl(sideImg, 'right', 0, frontImg)

    imgs.attachForm(sideLbl, 'left', 0)
    imgs.attachControl(sideLbl, 'right', 0, frontLbl)
    imgs.attachForm(frontLbl, 'right', 0)

    # Set side image click callback
    def setSideImg():
        path = fileDialog2( 
                            fm = 1, # Return one existing file
                            ff = "*.jpg; *.jpeg; *.png; *.bmp; *.gif", # File filter
                            dir = ".", # Starting directory
                            ds = 1 # Use OS native file dialog
                            )
        path = path[0]
        sideImg.setImage(path)
    sideImg.setCommand(Callback(setSideImg))

    # Dummy callbacks to get the drop functionality to "wake up"
    frontImg.dropCallback('')
    sideImg.dropCallback('')
    
    # Maya external drop callback
    class ImgDropCallback(OpenMayaUI.MExternalDropCallback):
        
        def __init__(self):
            self.frontImg = frontImg
            self.sideImg = sideImg
            self.frontImgCtrlName = str(frontImg)
            self.sideImgCtrlName = str(sideImg)
            OpenMayaUI.MExternalDropCallback.__init__(self)
        
        def externalDropCallback( self, doDrop, controlName, data ):
        
            if (self.frontImgCtrlName == controlName):
                if doDrop and data.hasUrls():
                    path = ''.join(data.urls()[0].split('file:///'))
                    self.frontImg.setImage(path)
                return OpenMayaUI.MExternalDropCallback.kNoMayaDefaultAndAccept
                
            elif (self.sideImgCtrlName == controlName):
                if doDrop and data.hasUrls():
                    path = ''.join(data.urls()[0].split('file:///'))
                    self.sideImg.setImage(path)
                return OpenMayaUI.MExternalDropCallback.kNoMayaDefaultAndAccept
    
    externalCB = ImgDropCallback()
    OpenMayaUI.MExternalDropCallback.addCallback(externalCB)
                
    # Set front image callback
    def setFrontImg():
        path = fileDialog2( 
                            fm = 1, # Return one existing file
                            ff = "*.jpg; *.jpeg; *.png; *.bmp; *.gif", # File filter
                            dir = ".", # Starting directory
                            ds = 1 # Use OS native file dialog
                            )
        path = path[0]
        frontImg.setImage(path)
    frontImg.setCommand(Callback(setFrontImg))

    # Creation callback
    def createRefPlanes(si, fi, win):
        
        sideImagePath = si.getImage()
        if (sideImagePath == "img_ref_set_side.png"): sideImagePath = None
        
        frontImagePath = fi.getImage()
        if (frontImagePath == "img_ref_set_front.png"): frontImagePath = None
        
        reference_planes(sideImagePath, frontImagePath)
        
        win.delete()

    # Close callback
    def closeRefPlaneDialog(cb, win):
        OpenMayaUI.MExternalDropCallback.removeCallback(cb)
        win.delete()
        
    # Command buttons
    setParent(mainLayout)
    text( l='' )
    button( label='Create', command=Callback(createRefPlanes, sideImg, frontImg, w) )
    button( label='Close', command=Callback(closeRefPlaneDialog, externalCB, w) )

    showWindow(w)