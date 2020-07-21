# Zoetrope
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/Naereen/)
[![ForTheBadge powered-by-electricity](http://ForTheBadge.com/images/badges/powered-by-electricity.svg)](http://ForTheBadge.com)


<img align="right" src="https://github.com/Errrneist/AnimKit/blob/master/animkit/icons/animkit_zoetrope.png" alt="Zoetrope" width="100">


> Don't assume it is raining if you hear wind blowing. ——— [The Elder](https://hongjunwu.com/elder/).    
#### Developer: [@Errrneist](https://github.com/Errrneist/)
#### Don't forget to star this project if you like it ヽ(✿ﾟ▽ﾟ)ノ! 
#### Let me know if your studio needs a hand :)

## General Information
* Zoetrope script will create a `/renders` folder in the same directory as the maya scene file.
* Each render layer will be rendered in separate folders inside the `/renders` folder.

## Zoetrope API
#### `animkit_zoetrope.render_w_padding`
* Render all render layers into respective folders in `/render` with padding (the entire timeline).
#### `animkit_zoetrope.render_nopadding`
* Render all render layers into respective folders in `/render` without padding (only playback area of timeline).
#### `animkit_zoetrope.render_default_w_padding`
* Render only default (current) render layer into `/render/defaultRenderLayers` with padding (the entire timeline).
#### `animkit_zoetrope.render_default_nopadding`
* Render only default (current) render layer into `/render/defaultRenderLayers` without padding (only playback area of timeline).


## License
[![forthebadge cc-sa](http://ForTheBadge.com/images/badges/cc-sa.svg)](https://creativecommons.org/licenses/by-sa/4.0)
