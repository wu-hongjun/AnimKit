# AnimKit
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/Naereen/)
[![ForTheBadge powered-by-electricity](http://ForTheBadge.com/images/badges/powered-by-electricity.svg)](http://ForTheBadge.com)


<img align="right" src="https://github.com/Errrneist/AnimKit/blob/master/IMG/animkit.png" alt="AnimKit" width="200">


> This code runs faster than the Hong Kong journists. ——— The Elder.    
#### Developer: [Hongjun Wu](https://hongjunwu.com/)
#### Don't forget to star this project if you like it ヽ(✿ﾟ▽ﾟ)ノ! 
#### Let me know if your studio or project needs a hand :)

## Demo
* Watch the full demo video to learn about all the features of AnimKit!

<a href="https://youtu.be/qPK8xrhlN6Q" rel="AnimKit" width="100">![Foo](https://github.com/Errrneist/AnimKit/blob/master/IMG/animkit_demo_video_thumbnail.png)</a>

* Here is a demo project I did using AnimKit.

<a href="https://github.com/Errrneist/Animation-Nutmeg_POTG" rel="AnimKit" width="100">![Foo](https://github.com/Errrneist/AnimKit/blob/master/IMG/animkit_demo_project_thumbnail.png)</a>

## Installation
#### Windows Automatic Installer: 
* Just run the animkit installation script `install_animkit.py`.
#### Windows & macOS & Linux Manually Install(Untested, let me know if it works):
* Copy all `icon` to your a sub folder of your maya pref directory: `\maya\2020\prefs\icons\animkit\`.
* Copy all `scripts` to your maya pref directory: `\maya\2020\scripts\`.
* Copy all `plug-ins` to your maya pref directory: `\maya\2020\plug-ins\`.
#### In `C:\Users\YOUR USER NAME\Documents\maya\scripts\userSetup.py` (Your maya pref) add the following line:
```python
# Load AnimKit

from maya import cmds
if not cmds.about(batch=True):
    cmds.evalDeferred("import animkit_shelf; animkit_shelf.animkitshelf()")
    
# Finished loading AnimKit.
```
#### Post Installation
* You should see `[AnimKit Shelf]: Successfully loaded all components of AnimKit!` in your script editor when you start Maya next time.

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

<a href="https://errrneist.github.io/AnimKit/videos/playblast_pp_demo.mp4" rel="AnimKit" width="100">![Foo](https://errrneist.github.io/AnimKit/videos/thumbnails/thumbnail_playblast_pp_demo.png)</a>

#### [iter++](https://github.com/Errrneist/AnimKit/blob/master/DOC/iter_pp.md) → `animkit_iter_pp.py`
* Provide one click solution to save iterations of maya scene, as well as current playblast of animation.

<a href="https://errrneist.github.io/AnimKit/videos/iter_pp_demo.mp4" rel="AnimKit" width="100">![Foo](https://errrneist.github.io/AnimKit/videos/thumbnails/thumbnail_iter_pp_demo.png)</a>

#### [Zoetrope](https://github.com/Errrneist/AnimKit/blob/master/DOC/zoetrope.md) → `animkit_zoetrope.py`
* Background one click script watermark free batch renderer for Arnold.

<a href="https://errrneist.github.io/AnimKit/videos/zoetrope_render_one_layer_demo.mp4" rel="AnimKit" width="100">![Foo](https://errrneist.github.io/AnimKit/videos/thumbnails/thumbnail_zoetrope_render_one_layer.png)</a>

<a href="https://errrneist.github.io/AnimKit/videos/zoetrope_smart_video_encoder_demo.mp4" rel="AnimKit" width="100">![Foo](https://errrneist.github.io/AnimKit/videos/thumbnails/thumbnail_zoetrope_smart_video_encoder.png)</a>

<a href="https://errrneist.github.io/AnimKit/videos/zoetrope_render_one_frame_demo.mp4" rel="AnimKit" width="100">![Foo](https://errrneist.github.io/AnimKit/videos/thumbnails/thumbnail_zoetrope_render_one_frame.png)</a>

#### Fix-it-Felix → `animkit_fix_it_felix.py`
* A collection of fixes for common problems.

<a href="https://errrneist.github.io/AnimKit/videos/fix_broken_nurbs.mp4" rel="AnimKit" width="100">![Foo](https://errrneist.github.io/AnimKit/videos/thumbnails/thumbnail_fix_broken_nurbs.png)</a>

<a href="https://errrneist.github.io/AnimKit/videos/make_render_cam_from_view.mp4" rel="AnimKit" width="100">![Foo](https://errrneist.github.io/AnimKit/videos/thumbnails/thumbnail_make_render_cam_from_view.png)</a>

## Integrated Tools
> Tools and scripts that are free and avaliable to public.
#### [TweenMachine](https://github.com/boredstiff/tweenMachine) → `tweenMachine.py`
* The easiest way to create breakdown poses in Maya.

## External Tools 
> You will have to acquire them separately and add them to folders as I am not allowed to redistribute them.
#### [Animschool Picker](https://www.animschool.com/pickerInfo.aspx) → `\plug-ins\AnimSchoolPicker.mll`
* Character picker for AnimSchool rigs.
#### [reParentPRO](https://gumroad.com/l/reParentPro) → `\scripts\reparent_pro_v158.mel`
* Tool for transfering animation from control to locator for polishing animation.

#### What if I don't have these tools and AnimKit failed to load?
* Go to `YOUR MAYA PREF\maya\2020\scripts\animkit_shelf.py` and at the end of the code delete respective sections. 

## Credits
* Some of the code are refactored from [University of Washington Animation Research Labs](http://arl.cs.washington.edu/about.html) shelf.

## License
[![forthebadge](https://forthebadge.com/images/badges/cc-nc-sa.svg)](https://forthebadge.com)
* You are welcome to use this script for non-commercial use. However, if you want to use for commercial please contact me.

## Donate
* If you think this is helpful and would like to buy me a coffee, you can do that using WechatPay/AliPay or Venmo!
<img align="middle" src="https://github.com/Errrneist/AnimKit/blob/master/IMG/donate.png" alt="donate">

