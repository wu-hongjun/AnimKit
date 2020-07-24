# AnimKit
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/Naereen/)
[![ForTheBadge powered-by-electricity](http://ForTheBadge.com/images/badges/powered-by-electricity.svg)](http://ForTheBadge.com)


<img align="right" src="https://github.com/Errrneist/AnimKit/blob/master/IMG/animkit.png" alt="AnimKit" width="200">


> Don't assume it is raining if you hear wind blowing. ——— The Elder.    
#### Developer: [@Errrneist](https://github.com/Errrneist/)
#### Don't forget to star this project if you like it ヽ(✿ﾟ▽ﾟ)ノ! 
#### Let me know if your studio or project needs a hand :)

## Installation
#### Windows: 
* Just run the animkit installation script `install_animkit.py`.
#### macOS & Linux (Untested, lmk if it works):
* Copy all `icon` to your a sub folder of your maya pref directory: `\maya\2020\prefs\icons\animkit\`.
* Copy all `scripts` to your maya pref directory: `\maya\2020\scripts\`.
* Copy all `plug-ins` to your maya pref directory: `\maya\2020\plug-ins\`.
#### In `userSetup.py` in YOUR MAYA PREF (NOT THE EXAMPLE FILE INCLUDED):
Add the following line:
```python
# Start AnimKit

from maya import cmds
if not cmds.about(batch=True):
    cmds.evalDeferred("import animkit_shelf; animkit_shelf.animkitshelf()", lowestPriority=True)
```

## AnimKit Utilities
#### AnimKit Installation Script → `install_animkit.py`
* Automatically one click solution install all scripts and icons to correct folder. (Windows only)
#### AnimKit Shelf → `animkit_shelf.py`
* Scalable and highly flexible shelf with button hierarchy shelf container written in Python 3.
#### AnimKit Wrapper → `animkit_wrapper.py`
* A wrapper for calling external fucntions like loading plug-ins to keep the shelf clean and tidy.

## AnimKit Tools
#### [Playblast+](https://github.com/Errrneist/AnimKit/blob/master/DOC/playblast_plus.md) → `animkit_playblast_plus_vp2.py`
* Provide functionality in playblasting AVI and MP4, with padding or without padding.
#### [iter++](https://github.com/Errrneist/AnimKit/blob/master/DOC/iter_pp.md) → `animkit_iter_pp.py`
* Provide one click solution to save iterations of maya scene, as well as current playblast of animation.
#### [render_cam+](https://github.com/Errrneist/AnimKit/blob/master/DOC/render_cam_plus.md) → `animkit_render_cam_plus.py`
* One click create a camera from current view called "render_cam"
#### [Graduator](https://github.com/Errrneist/AnimKit/blob/master/DOC/graduator.md) → `animkit_graduator.py`
* Removes student version info from file.
#### [Zoetrope](https://github.com/Errrneist/AnimKit/blob/master/DOC/zoetrope.md) → `animkit_zoetrope.py`
* Background one click script watermark free batch renderer for Arnold.

## Integrated Tools
> Tools and scripts that are free and avaliable to public.
#### [TweenMachine](https://github.com/boredstiff/tweenMachine) → `tweenMachine.py`
* The easiest way to create breakdown poses in Maya.

## External Tools 
> You will have to acquire them separately and add them to folders.
#### [Animschool Picker](https://www.animschool.com/pickerInfo.aspx) → `\plug-ins\AnimSchoolPicker.mll`
* Character picker for AnimSchool rigs.
#### [reParentPRO](https://gumroad.com/l/reParentPro) → `\scripts\reparent_pro_v158.mel`
* Tool for transfering animation from control to locator for polishing animation.

## Credits
* Some of the code are deeply modified and refactored from [University of Washington Animation Research Labs](http://arl.cs.washington.edu/about.html) shelf.

## License
[![forthebadge cc-sa](http://ForTheBadge.com/images/badges/cc-sa.svg)](https://creativecommons.org/licenses/by-sa/4.0)
