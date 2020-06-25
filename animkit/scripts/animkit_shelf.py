# Source: https://bindpose.com/scripting-custom-shelf-in-maya-python/

import maya.cmds as mc

import animkit_basic
import animkit_playblast_plus_vp2
import animkit_playblast_plus_arnold
import animkit_save_plus
import animkit_render_cam_plus

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
'''This is an example shelf.
class animkitshelf(_shelf):
    def build(self):
        self.addButton(label="button1")
        self.addButton("button2")
        self.addButton("popup")
        p = mc.popupMenu(b=1)
        self.addMenuItem(p, "popupMenuItem1")
        self.addMenuItem(p, "popupMenuItem2")
        sub = self.addSubMenu(p, "subMenuLevel1")
        self.addMenuItem(sub, "subMenuLevel1Item1")
        sub2 = self.addSubMenu(sub, "subMenuLevel2")
        self.addMenuItem(sub2, "subMenuLevel2Item1")
        self.addMenuItem(sub2, "subMenuLevel2Item2")
        self.addMenuItem(sub, "subMenuLevel1Item2")
        self.addMenuItem(p, "popupMenuItem3")
        self.addButton("button3")
'''

# The AnimKit Shelf 
# Note: When pass a command we are not using the brackets after the name (), because that would call the command instead of passing it.
class animkitshelf(_shelf):
    def build(self):
        # The man, the legend. Cody.
        self.addButton(label="Cody", 
                        icon="animkit\\animkit_cody.png", 
                        command=animkit_basic.praise_cody, 
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
        self.addMenuItem(p, label="Save Scene Iterations", command=animkit_save_plus.save_iteration)
        self.addMenuItem(p, label="Save Scene Iterations with Playblast", command=animkit_save_plus.save_iteration_with_playblast)


        # Create render_cam from view
        self.addButton(label="RenderCam+", 
                        icon="animkit\\animkit_rendercam_plus.png", 
                        noLabel=True, 
                        command=animkit_render_cam_plus.create_render_cam_from_view, 
                        btn_annotation = "render_cam+ creates a render_cam from one click.")


        # Animschool Picker
        # self.addButton(label="Animschool Picker", icon="animkit\\animkit-animschool.png", noLabel=True, command=animkit_basic.load_animschool_picker, btn_annotation = "Launch Animschool Picker.")

            
        
        
# Load AnimKit
animkitshelf()
print("AnimKit: Successfully loaded AnimKit!")


###################################################################################
