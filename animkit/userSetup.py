# start animkit
from maya import cmds

if not cmds.about(batch=True):
    cmds.evalDeferred("import animkit_shelf; animkit_shelf.animkitshelf()")

# end animkit