from pymel.core import *
import time
import os
import shutil

class SaveIterationWindow():
    '''
    Provides a method of saving an iteration and adding notes
    '''

    def __init__(self):
        sn = sceneName()
        if sn == '':
            self.showErrorWindow("ERROR!\nThis scene is not saved yet.")
            return None
    
        if window('saveIter', q=1, exists=1):
            deleteUI('saveIter')
            
        win = window('saveIter', title = 'Save Iteration')
        panel = columnLayout(adj=1)
        text(label = "Iteration Notes")
        iterText = textField(alwaysInvokeEnterCommandOnReturn=True)
        
        textField(iterText, e=1, enterCommand = Callback(self.saveIteration, iterText, win))
        button(label = 'Save', c = Callback(self.saveIteration, iterText, win))
        
        showWindow(win)


    def saveIteration(self, iterField, win):
        '''
        Save iteration callback
        '''
        
        updateNotes = textField(iterField, q=1, text=1)
        sn = sceneName()
        dir = sn.parent
        name = os.path.basename(sn).split('.')[0]
        iterDir = os.path.join(dir, name+'_iterations')
        
        if not os.path.exists(iterDir): os.makedirs(iterDir)

        nextVerNum = self.getNextVersionNumber(iterDir)
        nextVerNumStr = "%(ver)03d" % {"ver":nextVerNum}
        
        nextVerFile = os.path.join(iterDir, name+"_v"+nextVerNumStr+".ma")
        
        notes = file(iterDir + "/iteration_notes.txt", mode = 'a')
        curTime = time.strftime("%a, %B %d %Y @ %H:%M:%S")
        notes.write('\r\n%s = %s :: %s'%(nextVerNumStr, curTime, updateNotes))
        notes.close()
               
        saveAs(sn, f=1, type = 'mayaAscii')
        shutil.copy(sn, nextVerFile)
        
        print ('Iteration saved to "'+nextVerFile+'"').replace('\\', '/')
        
        evalDeferred('from pymel.core import *;deleteUI("'+str(win)+'")') # Must defer UI deletion, otherwise it crashes Maya
        
        
        
    def getNextVersionNumber(self, iterDir):
        iterFiles = []
        items = os.listdir(iterDir)
        for item in items:
            if item.endswith('.ma') == True:
                iterFiles.append(item)
        nextVer = -1
        for f in iterFiles:
            name = os.path.basename(f).split('.')[0]
            itrVerStr = name.split('v')[-1]
            try:
                itrVer = int(itrVerStr)
                if itrVer > nextVer:
                    nextVer = itrVer
            except ValueError:
                continue
        nextVer += 1
        return nextVer
    

    def showErrorWindow(self, errorMessage):
        errW = window(t="!!!", w=150, h=100, sizeable=False)
        columnLayout( adjustableColumn=True, cal="center" )
        text( label=errorMessage, align="center")
        okayButton = button( label='Okay', command=Callback(errW.delete) )
        showWindow(errW)
        setFocus(okayButton)

def save_iteration_cmd(self):
    SaveIterationWindow()
    
# save_iteration_cmd()