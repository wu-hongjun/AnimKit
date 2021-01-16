# Source: https://bindpose.com/scripting-custom-shelf-in-maya-python/

import maya.cmds as mc

import animkit_wrapper
import animkit_playblast_plus_vp2
import animkit_iter_pp
import animkit_zoetrope
import animkit_fix_it_felix
import animkit_tweenMachine
import animkit_char_design
import animkit_rename_renders
import animkit_timelapse_creator

def _null(*args):
    pass


class _shelf():
    '''A simple class to build shelves in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf".'''

    def __init__(self, name="AnimKit", iconPath=""):
        self.name = name

        self.iconPath = iconPath

        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self._cleanOldShelf()
        mc.setParent(self.name)
        self.build()

    def build(self):
        '''This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf.'''
        pass

    def addButton(self, label, icon="commandButton.png", command=_null, doubleCommand=_null, noLabel=False, btn_annotation = ""):
        '''Adds a shelf button with the specified label, command, double click command and image.'''
        mc.setParent(self.name)
        if icon:
            icon = self.iconPath + icon

        if noLabel:
            mc.shelfButton(width=37, height=37, image=icon, l=label, command=command, dcc=doubleCommand, ann=btn_annotation)
        else:
            mc.shelfButton(width=37, height=37, image=icon, l=label, command=command, dcc=doubleCommand, imageOverlayLabel=label, olb=self.labelBackground, olc=self.labelColour, ann=btn_annotation)

    def addMenuItem(self, parent, label, command=_null, icon=""):
        '''Adds a shelf button with the specified label, command, double click command and image.'''
        if icon:
            icon = self.iconPath + icon
        return mc.menuItem(p=parent, l=label, c=command, i="")

    def addSubMenu(self, parent, label, icon=None):
        '''Adds a sub menu item with the specified label and icon to the specified parent popup menu.'''
        if icon:
            icon = self.iconPath + icon
        return mc.menuItem(p=parent, l=label, i=icon, subMenu=1)

    def _cleanOldShelf(self):
        '''Checks if the shelf exists and empties it if it does or creates it if it does not.'''
        if mc.shelfLayout(self.name, ex=1):
            if mc.shelfLayout(self.name, q=1, ca=1):
                for each in mc.shelfLayout(self.name, q=1, ca=1):
                    mc.deleteUI(each)
        else:
            mc.shelfLayout(self.name, p="ShelfLayout")


###################################################################################

# The AnimKit Shelf 
# Note: When pass a command we are not using the brackets after the name (), because that would call the command instead of passing it.
class animkitshelf(_shelf):
    def build(self):
        # The man, the legend. Cody.
        self.addButton(label="Cody", 
                        icon="animkit\\animkit_cody.png", 
                        command=animkit_wrapper.praise_cody, 
                        btn_annotation = "Praise and receive animation blessing from the all-mighty Cody.")
        
        # Playblast+
        self.addButton(label="Playblast+", 
                        icon="animkit\\animkit_playblast_plus.png", 
                        btn_annotation = "Playblast+ can playblast into AVI (Quality) and MP4 (Efficiency).", 
                        noLabel = True)
        p = mc.popupMenu(b=1)
        vp2_avi = self.addSubMenu(p, "Playblast AVI")
        self.addMenuItem(vp2_avi, label="AVI - No Padding", command=animkit_playblast_plus_vp2.vp2_avi_playblast_nopadding)
        self.addMenuItem(vp2_avi, label="AVI - With Padding", command=animkit_playblast_plus_vp2.vp2_avi_playblast_padding)
        vp2_mp4 = self.addSubMenu(p, "Playblast MP4")
        self.addMenuItem(vp2_mp4, label="MP4 - No Padding", command=animkit_playblast_plus_vp2.vp2_mp4_playblast_nopadding)
        self.addMenuItem(vp2_mp4, label="MP4 - With Padding", command=animkit_playblast_plus_vp2.vp2_mp4_playblast_padding)


        # iter++
        self.addButton(label="iter++", 
                        icon="animkit\\animkit_iter_pp.png", 
                        noLabel=True, 
                        btn_annotation = "iter++ is a better and faster way to save iterations.")
        p = mc.popupMenu(b=1)
        self.addMenuItem(p, label="Save Scene Iterations", command=animkit_iter_pp.save_iteration)
        self.addMenuItem(p, label="Save Scene Iterations with Playblast", command=animkit_iter_pp.save_iteration_with_playblast)

        # Zoetrope
        self.addButton(label="zoetrope", 
                        icon="animkit\\animkit_zoetrope.png", 
                        noLabel=True, 
                        btn_annotation = "Zoetrope is a one click background batch renderer.")
        p = mc.popupMenu(b=1)

        render_all_layers = self.addSubMenu(p, "Render All Separate Render Layers")
        self.addMenuItem(render_all_layers, label="Render With Padding", command=animkit_zoetrope.render_w_padding)
        self.addMenuItem(render_all_layers, label="Render Without Padding", command=animkit_zoetrope.render_nopadding)

        render_default_layers = self.addSubMenu(p, "Render Only Current Render Layer")
        self.addMenuItem(render_default_layers, label="Render Current Layer With Padding", command=animkit_zoetrope.render_default_w_padding)
        self.addMenuItem(render_default_layers, label="Render Current Layer Without Padding", command=animkit_zoetrope.render_default_nopadding)

        render_frame = self.addSubMenu(p, "Render Current Frame")
        self.addMenuItem(render_frame, label="Render Current Frame in PNG", command=animkit_zoetrope.render_one_frame_png)
        self.addMenuItem(render_frame, label="Render Current Frame in TIF", command=animkit_zoetrope.render_one_frame_tif)

        zoetrope_smart_encoder = self.addSubMenu(p, "Zoetrope Smart Video Encoder")
        self.addMenuItem(zoetrope_smart_encoder, label="Encode All Renders with Compressed MP4", command=animkit_zoetrope.smart_convert_all_renders_compressed)
        self.addMenuItem(zoetrope_smart_encoder, label="Encode All Renders with Lossless AVI", command=animkit_zoetrope.smart_convert_all_renders_lossless)

        # Timelapse
        self.addButton(label="Timelapse Creator", 
                        icon="animkit\\animkit_timelapse.png", 
                        noLabel=True, 
                        btn_annotation = "Start timelapse recording")
        p = mc.popupMenu(b=1)
        self.addMenuItem(p, label="Record timelapse from viewport", command=animkit_timelapse_creator.create_timelapse_from_viewport)
        self.addMenuItem(p, label="Record timelapse from timelapse cam", command=animkit_timelapse_creator.create_timelapse_from_tlcam)

        # Fix-it-Felix
        self.addButton(label="Fix-it-Felix", 
                        icon="animkit\\animkit_fix-it-felix.png", 
                        noLabel=True, 
                        btn_annotation = "Fix-it-Felix is a set of handy fixes to boost workflow.")
        p = mc.popupMenu(b=1)

        fix_nurbs = self.addSubMenu(p, "NURBS")
        self.addMenuItem(fix_nurbs, label="Rebuild Broken NURBS Surfaces", command=animkit_fix_it_felix.fix_broken_NURBS)

        fix_arnold = self.addSubMenu(p, "Arnold")
        self.addMenuItem(fix_arnold, label="Fix Locked Global Render Path", command=animkit_fix_it_felix.fix_defaultArnoldDriver_pre)
        self.addMenuItem(fix_arnold, label="Load Arnold mtoa.mll Plug-In", command=animkit_fix_it_felix.load_arnold_plugin)

        fix_scene = self.addSubMenu(p, "Scene")
        self.addMenuItem(fix_scene, label="Remove Student Version From Scene", command=animkit_fix_it_felix.graduator)
        self.addMenuItem(fix_scene, label="Convert Project Path to All Lower Case", command=animkit_fix_it_felix.fix_uppercase)

        fix_renders = self.addSubMenu(p, "Renders")
        self.addMenuItem(fix_renders, label="Rename Neg Sequence Images with Pos Padding", command=animkit_rename_renders.rename_renders)

        fix_render_cam = self.addSubMenu(p, "Camera")
        self.addMenuItem(fix_render_cam, label="Make render_cam From View", command=animkit_fix_it_felix.create_render_cam_from_view)

        # Character Design
        self.addButton(label="Character Design", 
                        icon="animkit\\animkit_chardesign.png", 
                        noLabel=True, 
                        btn_annotation = "Tools for character design.")
        p = mc.popupMenu(b=1)

        joint_axes = self.addSubMenu(p, "Joint Axes")
        self.addMenuItem(joint_axes, label="Turn Joint Axes On", command=animkit_char_design.turn_joint_axes_on)
        self.addMenuItem(joint_axes, label="Turn Joint Axes Off", command=animkit_char_design.turn_joint_axes_off)

        self.addMenuItem(p, label="Select Skeleton", command=animkit_char_design.select_skeleton)
        self.addMenuItem(p, label="Create Visibility Slider", command=animkit_char_design.create_visibility_slider)
        self.addMenuItem(p, label="Create Block Model", command=animkit_char_design.create_block_model)
        self.addMenuItem(p, label="Configure Reference Planes", command=animkit_char_design.config_reference_planes)

        # plug-ins
        self.addButton(label="Animkit plug-ins", 
                        icon="animkit\\animkit_plugins.png", 
                        noLabel=True, 
                        btn_annotation = "External tools and plug-ins loader.")
        p = mc.popupMenu(b=1)
        self.addMenuItem(p, label="TweenMachine", command=animkit_wrapper.load_tweenMachine)
        self.addMenuItem(p, label="reParent", command=animkit_wrapper.load_reParent)
        self.addMenuItem(p, label="Animschool Picker", command=animkit_wrapper.load_animschool_picker)




            
        
        
# Load AnimKit
animkitshelf()
print("[AnimKit Shelf]: Successfully loaded all components of AnimKit!")


###################################################################################
