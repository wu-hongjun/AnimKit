from pymel import *
import os
import random
import pymel.core.animation as annie
import scene_manager.gui as gui
import scene_manager.methods as meth
from scene_manager import metaCore as meta

def updatePanel(panel, directoryName, fileLocation, bigImagefileLocation, bigImageButton, largeIconSize):
	largeIconSize = int(largeIconSize)
	text = bigImagefileLocation.split('/')[-1].split('.')[0]
	bigImageButton = iconTextButton(bigImageButton, e=1, al = 'center', i1=bigImagefileLocation, label = text, st= "iconOnly", en=True)
	iconTextButton(bigImageButton, e=1, dcc= lambda *args: chooseFile(directoryName, fileLocation))
	setParent(panel)
	
def chooseFile(fileName, poseLibraryPath):
	print 'here!'
	print fileName
	char = meta.getMetaRoot(ls(sl=1)[0])
	print char
	charName = char.getCharacterName()
	print charName
	namespace = ":".join(ls(sl=1)[0].name().split(":")[:-1])
	print namespace
	pose = meth.Pose().readXML('%s%s/poses/%s.xml'%(poseLibraryPath,charName,fileName))
	pose.goToPose(namespace)
	
class PoseLibWindow():
	def __init__(self):
		
		self.smallIconSize = 150
		self.largeIconSize = 400
		self.numberOfImageColumns = 6
		self.fileDepth = 9
		
		self.poseLibraryPath = 'O:/unix/projects/instr/capstone1/nebbish_production/rigs/characters/pose_library/'
		
		self.window = None
		self.currentImage = None
		self.listPanel = None
		self.scrollPanel = None
		self.bigImageButton = None
		self.bigImageHolder = None
		
		self.currentLibrary = 'Nebbish'
		
		#delete the window if it already exists
		if(window('PoseLibWindow', exists=1)):
			deleteUI('PoseLibWindow')
			
		#main window
		self.window = window('PoseLibWindow', title = "Awesome!!!", s= False)
		
		#main
		self.mainPanel = columnLayout("body", columnAlign = "center", cw = 300)
		
		#row layout for next 4 buttons
		optionsPanel = rowLayout(nc = 4, cw4 = [50,50,50,50])
		#create buttons
		saveButton = button(label = 'Save', w = 50, h = 20, c = lambda *args: self.saveFunc())
		deleteButton = button(label = 'Delete',w = 50, h = 20, c = lambda *args: self.deleteFunc())
		#selectButton = button(label = 'Select',w = 50, h = 20, c = lambda *args: self.selectFunc())
		listButton = button(label = 'List',w = 50, h = 20, c = lambda *args: self.listFunc())
		setParent(self.mainPanel)
		
		self.bigImageHolder = columnLayout('bigPictureHolder_micheal',  w = self.largeIconSize, h = self.largeIconSize, cal = 'center')
		self.bigImageButton = iconTextButton(al = 'center', w = self.largeIconSize, h = self.largeIconSize)
		#setParent(self.bigImageHolder)
		
		#files in Nebbish folder
		path = self.poseLibraryPath + 'Nebbish'
		files = os.listdir(path + '/poses')
		#.xml check MICHAEL
		amount = len(files)
		
		self.scrollPanel = scrollLayout(
		mcw = self.smallIconSize, h = self.smallIconSize * 1.5, w = self.smallIconSize * self.numberOfImageColumns + 30)
		self.listFunc()
		
		self.window.setWidth(self.smallIconSize * self.numberOfImageColumns + 60)
		showWindow(self.window)

	def listFunc(self):
		setParent(self.mainPanel)
		if not self.listPanel == None:
			deleteUI(self.listPanel)
		
		try:
			char = meta.getMetaRoot(ls(sl=1)[0])
			self.currentLibrary = char.getCharacterName()
		except:
			self.currentLibrary = 'Nebbish'
		
		path = self.poseLibraryPath + self.currentLibrary
		pathExist = os.path.exists(path)
		
		if not pathExist:
			print 'No poses saved'		
		else:
			#files in Nebbish folder
			files = os.listdir(path + '/poses')
			#.xml check MICHAEL
			amount = len(files)
			
			setParent(self.scrollPanel)
			self.listPanel = rowColumnLayout(nc = self.numberOfImageColumns)
			for a in range(self.numberOfImageColumns):
				self.listPanel.columnWidth((a + 1, self.smallIconSize))
			
			for a in files:
				splitName = a.split('.')
				name = splitName[0]
				if os.path.exists(path + '/pose_images/small/' + name + 'small.bmp'):
					fileLocation = path + '/pose_images/large/' + name + '.bmp'
					imageLocation = path + '/poses/' + name + '.xml'
					button1 = iconTextButton(st = 'iconAndTextCentered', l=name, al = 'center', w = self.smallIconSize, h = self.smallIconSize,
					i = path + '/pose_images/small/' + name + 'small.bmp', 
					c = eval("lambda *args: updatePanel( '"+self.bigImageHolder+"'  , '"+name+"' , '"+self.poseLibraryPath+"', '" + path +  "/pose_images/large/" +name+ "large.bmp', '"+self.bigImageButton+"','"+str(self.largeIconSize)+"')" ))
					#iconTextButton(button1, e=1, dcc= eval("lambda *args: chooseFile('"+name+"', '"+self.poseLibraryPath+"')")) # if double click to select pose
				else:
					button1 = iconTextButton(bgc = (1, .5, .5), st = "textOnly",  w = self.smallIconSize, al = 'center', h = self.smallIconSize, label = name, 
					c = eval("lambda *args: updatePanel( '"+self.bigImageHolder+"'  , '"+name+"' , '"+self.poseLibraryPath+"', '" + path +  "/pose_images/large/" +name+ "large.bmp', '"+self.bigImageButton+"','"+str(self.largeIconSize)+"')" ))
					#iconTextButton(button1, e=1, dcc= eval("lambda *args: chooseFile('"+name+"', '"+self.poseLibraryPath+"')"))  # if double click to select pose
			self.scrollPanel.setHeight(1)
			self.scrollPanel.setHeight(self.smallIconSize * 1.5)
			
	def setCurrentPose(self, pose):
		self.CurrentPose = pose
	
	def saveFunc(self):
		if(window('SaveLibWindow', exists=1)):
			deleteUI('SaveLibWindow')
		
		#save window
		saveWindow = window('SaveLibWindow', title = "Save")
		savePanel = columnLayout("body", adj = 1, columnAlign = "center")
		
		text(label = "Save Here")
		iterText = textField()
		textField(iterText, e=1, enterCommand = lambda *args: self.saveFile(iterText, saveWindow))
		button(label = 'click to save', c = lambda *args: self.saveFile(iterText, saveWindow))
		
		window(saveWindow, e=1, w=200, h=200)
		showWindow(saveWindow)
		
	def saveFile(self, iterText, saveWindow):
		fileName = textField(iterText, q=1, text=1)
		sel = ls(sl=1)
		funnyQuote = random.random() < .2
		if funnyQuote:
			confirmDialog( title= 'Really?', message= 'Oh come on you can do better than that!  Do you really want to save THIS pose?', button= ['yes', 'no'])
		
		allAnims = confirmDialog( title= 'Confirm' ,message= 'All anims or just selected?' ,button= ['ALL!', 'ONLY SELECTED!'] ,defaultButton= 'ONLY SELECTED!' ,cancelButton= 'ONLY SELECTED!!' ,dismissString= 'ONLY SELECTED!');
		
		lastSelection = ls(sl=1)
		char = meta.getMetaRoot(lastSelection[0])
		charName = char.getCharacterName()
		
		
		path = self.poseLibraryPath + charName
		pathExist = os.path.exists(path)
		
		#create folder of object if it does not exist
		if not pathExist:
			os.mkdir(path)
			os.mkdir(path + '/poses')
			os.mkdir(path + '/pose_images')
			os.mkdir(path + '/pose_images/large')
			os.mkdir(path + '/pose_images/small')
			
		charNamespace = meth.getNamespace(ls(sl=1)[0])
		
		list = []
		
		#saving a pose
		if allAnims == 'ALL!':
			if charName == 'Nebbish':
				allChars = meta.getMetaNodesOfType('CharacterRig')
				for x in allChars:
					if meta.getNamespace(x) == charNamespace and x.characterName.get() == 'Nebbish_Face':
						list = meta.fromNetworkToObject(x).getAllAnims()
					
			#anims = []
			#map(lambda x: anims.append(x), char.getAllAnims())
			#anims.remove(char.getTopCon())
			map(lambda x: list.append(x), char.getAllAnims())
			list.remove(char.getTopCon())
			select(list)
		else:
			list = lastSelection
			
			
			
		path = self.poseLibraryPath + charName
		posePath = path + '/poses/' + fileName + '.xml'
		imagePath = path + '/pose_images'
		pathExist = os.path.exists(posePath)
		
		if pathExist:
			result = confirmDialog( title= 'Confirm' ,message= 'File already exist. Overwrite?' ,button= ['YES. DO IT!', 'NO WAY JOSE!'] ,defaultButton= 'YES. DO IT!' ,cancelButton= 'NO WAY JOSE!' ,dismissString= 'NO WAY JOSE!');
			if result == 'YES. DO IT!':	
				self.savePoseToXML(fileName, path, list, lastSelection)
			else:
				select(lastSelection)
				
		else:
			self.savePoseToXML(fileName, path, list, lastSelection)
		deleteUI('SaveLibWindow')
		
		self.listFunc()
		
		
	def savePoseToXML(self, fileName, path, list, lastSelection):
		#path for xml file
		posePath = path + '/poses/' + fileName + '.xml'
		#path for image file
		imagePath = path + '/pose_images'
		
		characterList = []
		for a in list:
			tempChar = meta.getMetaRoot(a, 'CharacterRig')
			if not tempChar in characterList:
				characterList.append(tempChar)
			
		
		pose = meth.Pose().create(fileName, ls(sl=1))
		pose.saveToXML(posePath)
		renderGlobs = PyNode("defaultRenderGlobals")
		currentFormat = renderGlobs.imageFormat.get()
		renderGlobs.imageFormat.set(20)
		smallPath = imagePath + '/small/'
		largePath = imagePath + '/large/'
		#char = meta.getMetaRoot(ls(sl=1)[0], 'CharacterRig')
		oldVal = .5
		topCon = None
		oldConnect = None
		for a in characterList:
			print 'entered'
			topCon = a.getTopCon()
			oldVal = topCon.animOpacity.get()
			oldConnect = topCon.animOpacity.listConnections(source = 1,d=0, p =1)

			if oldConnect:
				disconnectAttr(oldConnect[0], topCon.animOpacity)
				print "breaking"
			topCon.animOpacity.set(1)
		#sel = ls(sl=1)
		select(cl=1)
		playblast(frame = annie.getCurrentTime(), w = self.smallIconSize, h = self.smallIconSize, format='image', viewer=False, fo=True, f = smallPath + fileName + 'small', p = 100)
		playblast(frame = annie.getCurrentTime(), w = self.largeIconSize, h = self.largeIconSize, format='image', viewer=False, fo=True, f = largePath + fileName + 'large', p = 100)
		select(lastSelection)
		#topCon.animOpacity.set(oldVal)
		if oldConnect:
			connectAttr(oldConnect[0], topCon.animOpacity, f=1)
			print "connecting"
		else:
			topCon.animOpacity.set(oldVal)
		
		#hacked. assumes image is named with .0000.bmp
		try:
			os.rename(smallPath + fileName + 'small' +'.0000.bmp', smallPath + fileName + 'small.bmp')
			os.rename(largePath + fileName + 'large' + '.0000.bmp', largePath + fileName + 'large.bmp')
			os.chmod(smallPath + fileName + 'small.bmp', stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
			os.chmod(largePath + fileName + 'large.bmp', stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
			renderGlobs.imageFormat.set(currentFormat)
		except:
			print "playblast pose failed"

		
	def deleteFunc(self):		
		allAnims = confirmDialog( title= 'Confirm' ,message= 'Are you sure you want to delete this file?' ,button= ['Yes =)', 'No =('] ,defaultButton= 'No =(' ,cancelButton= 'No =(' ,dismissString= 'No =(')
		if allAnims =='Yes =)':
			if self.bigImageButton.getImage() != None:
				creature = self.bigImageButton.getImage().split('/')[self.fileDepth]
				file = self.bigImageButton.getImage().split('/')[-1].split('large')[0]
				
				xmlPath = self.poseLibraryPath + creature + '/poses/' + file + '.xml'
				smallPath = self.poseLibraryPath + creature + '/pose_images/small/' + file + 'small.bmp'
				largePath = self.poseLibraryPath + creature + '/pose_images/large/' + file + 'large.bmp'
				if os.path.exists(xmlPath):
					os.remove(xmlPath)
				if os.path.exists(smallPath):
					os.remove(smallPath)
				if os.path.exists(largePath):
					os.remove(largePath)
				self.listFunc()
				iconTextButton(self.bigImageButton, e=1, en=False, i= "");
			else:
				print 'Unable to delete image. Ask Michael for Help'
	#deprecated
	'''	
	def selectFunc(self):
		if(window('SelectLibWindow', exists=1)):
			deleteUI('SelectLibWindow')
			
		#save window
		selectWindow = window('SelectLibWindow', title = "Select")
		selectPanel = columnLayout("body", adj = 1, columnAlign = "center")
		
		text(label = "Type in file name")
		iterText = textField()
		textField(iterText, e=1, enterCommand = lambda *args: self.selFile(iterText, selectWindow))
		button(label = 'click to open', c = lambda *args: self.selFile(iterText, selectWindow))
		
		window(selectWindow, e=1, w=200, h=200)
		showWindow(selectWindow)
		
		
	def selFile(self, iterText, selectWindow):
		fileName = textField(iterText, q=1, text=1)
	
		#select a pose
		char = meta.getMetaRoot(ls(sl=1)[0])
		charName = char.getCharacterName()
		char.selectAllAnims()
		pose = meth.Pose().readXML('%s%s/poses/%s.xml'%(self.poseLibraryPath,charName,fileName))
		pose.goToPose()
		deleteUI(selectWindow)
	'''	
		
		
		