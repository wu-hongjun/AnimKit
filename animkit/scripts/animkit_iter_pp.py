from pymel.core import *
import time
import os
import shutil
import animkit_playblast_plus_vp2

class SaveIterationWindow():
    '''
    Provides a method of saving an iteration and adding notes
    '''

    def __init__(self, playblast=False):
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
        
        textField(iterText, e=1, enterCommand = Callback(self.saveIteration, iterText, win, playblast))
        button(label = 'Save', c = Callback(self.saveIteration, iterText, win, playblast))
        
        showWindow(win)


    def saveIteration(self, iterField, win, playblast=False):
        '''
        Save iteration callback
        '''
        
        updateNotes = textField(iterField, q=1, text=1)
        sn = sceneName()
        dir = sn.parent
        print("dir: ", dir)
        name = os.path.basename(sn).split('.')[0]
        iterDir = os.path.join(dir, name+'_iterations')
        
        if not os.path.exists(iterDir): os.makedirs(iterDir)

        nextVerNum = self.getNextVersionNumber(iterDir)
        nextVerNumStr = "%(ver)03d" % {"ver":nextVerNum}
        
        nextVerFile = os.path.join(iterDir, name+"_v"+nextVerNumStr+".ma")

        # Playblast code
        if(playblast):
            nextVerName = os.path.join(name+"_v"+nextVerNumStr)
            print("nextVarName", nextVerName)
            nextVerDir = os.path.join(iterDir, name+"_v"+nextVerNumStr+"playblast")
            if not os.path.exists(nextVerDir): os.makedirs(nextVerDir)
            animkit_playblast_plus_vp2.vp2_mp4_playblast_ipp_nopadding(new_name=nextVerName)
            animkit_playblast_plus_vp2.vp2_mp4_playblast_ipp_padding(new_name=nextVerName)

            pb_npd_dir = os.path.join(dir, nextVerName+"_nopadding.mp4").replace('\\', '/')
            print("pb_npd_dir: ", pb_npd_dir)
            pb_pd_dir = os.path.join(dir, nextVerName+"_w_padding.mp4").replace('\\', '/')
            print("pb_pd_dir: ", pb_pd_dir)

            shutil.move(pb_npd_dir, nextVerDir)
            shutil.move(pb_pd_dir, nextVerDir)

        
        notes = file(iterDir + "/iteration_notes.txt", mode = 'a')
        curTime = time.strftime("%a, %B %d %Y @ %H:%M:%S")
        notes.write('\r\n%s = %s :: %s'%(nextVerNumStr, curTime, updateNotes))
        notes.close()
               
        saveAs(sn, f=1, type = 'mayaAscii')
        shutil.copy(sn, nextVerFile)
        print("nextVerFile", nextVerFile)
        
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
    
    def playblast_iteration():
        return True

def save_iteration(self):
    SaveIterationWindow()
    
def save_iteration_with_playblast(self):
    SaveIterationWindow(playblast=True)

# save_iteration_cmd()