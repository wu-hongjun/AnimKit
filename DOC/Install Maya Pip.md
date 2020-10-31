# Install Python pip for Maya 2020 on Windows 10
> [Hongjun Wu](hongjunwu.com) | October 30, 2020.

## Introduction
* As technical artists working with maya and python, there's always that moment when you just want to say "Oh man I wish I can use this external package from pip! But there's no way I can install package from pip into Maya!" 
* In my case, I wanted to install `ffmpeg-python` for a feature I am developing in my toolset. 
* Bummer! But now I think I found a solution.
* First of all, some main information on the Maya distribution of python:
    * Maya has its own independent python environment, namely, under `C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe`. 
    * If you open it up, on `Maya 2020` it is showing the following:
    ```
    Python 2.7.11 (default, Jul  1 2016, 02:08:48) [MSC v.1900 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    ```



## Preparation
* You will need to download this script called `get-pip.py`. (You can download it from [pypa.io](https://bootstrap.pypa.io/get-pip.py))
* Then, you will need to place this script into `C:\Program Files\Autodesk\Maya2020\bin`.

## Installation
* Open your Windows Powershell with Administrator(NOT mayapy.exe), and `cd` to the Maya `bin` directory we are working in, namely 
    > cd C:\Program Files\Autodesk\Maya2020\bin
    * Then if you type in `.\mayapy -m pip --version`, it should tell you there is no such thing called `pip`. Otherwise, you don't need this guide.
* Now that we are in the correct directory, run 
    > .\mayapy get-pip.py
* Python should now install pip on its own. To check the current version, do
    > .\mayapy -m pip --version
    * And you should get something like `pip 20.2.4 from C:\Program Files\Autodesk\Maya2020\Python\lib\site-packages\pip (python 2.7)`.
* With pip installed, now let's install some packages! I'll try to install the package `ffmpeg-python` which is what I want to install. Run
    > .\mayapy -m pip install ffmpeg-python
    * You should get something ending with `Successfully installed ffmpeg-python-0.2.0 future-0.18.2`.

## Moment of Truth
* Time to put our newly installed package into use! 
* Let's try import `ffmpeg-python` into the Maya Script Editor, which, according to their website, is
    > import ffmpeg
* Press the run button. If the script editor happily accepts this line, that means your newly installed package from pip is working!! Enjoy :)