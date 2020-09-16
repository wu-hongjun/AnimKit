######################################## Import ########################################
from PySide2 import QtCore
from PySide2 import QtWidgets

from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

import os
import shutil

######################################## Source ########################################
# Pyside 2 for Maya: https://www.patreon.com/posts/pyside2-for-maya-21014713

######################################## GUI ########################################
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class ShowDialog(QtWidgets.QDialog):

    def __init__(self, parent = maya_main_window()):
        super(ShowDialog, self).__init__(parent)

        self.setWindowTitle("AnimKit Rename Renders")
        self.setMinimumWidth(1280)
        self.setMinimumHeight(720)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # Delete Question Mark

        self.create_widgets()
        self.create_layouts()


    def create_widgets(self):
        # File Path
        self.filePathPrompt = QtWidgets.QLabel('Render Folder Path')
        self.filePath = QtWidgets.QFileDialog()
        self.filePath.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        # File Path Override
        self.fileOverridePrompt = QtWidgets.QLabel('Render Folder Path Override')
        self.fileOverride = QtWidgets.QLineEdit()

        # Scene Name 
        self.scenePrompt = QtWidgets.QLabel('Rendered Image Scene Name')
        self.scene = QtWidgets.QLineEdit()

        # Rename Folder Path
        self.folderPathPrompt = QtWidgets.QLabel('New Rename Folder Name')
        self.folderPath = QtWidgets.QLineEdit()
        self.folderPath.setText("renamed_renders")

        # File Format
        self.formatPrompt = QtWidgets.QLabel('File Format (.tif)')
        self.format = QtWidgets.QLineEdit()
        self.format.setText(".tif")

        # Frame Start & End
        self.frameStartPrompt = QtWidgets.QLabel('Start Frame')
        self.frameEndPrompt = QtWidgets.QLabel('End Frame')
        self.frameStart = QtWidgets.QSpinBox()
        self.frameStart.setRange(-1024, 1024)
        self.frameStart.setSingleStep(1)
        self.frameStart.setValue(-24)
        self.frameEnd = QtWidgets.QSpinBox()
        self.frameEnd.setRange(-1024, 1024)
        self.frameEnd.setSingleStep(1)
        self.frameEnd.setValue(0)

        # Padding
        self.paddingPrompt = QtWidgets.QLabel('Padding')
        self.padding = QtWidgets.QSpinBox()
        self.padding.setRange(0, 10)
        self.padding.setSingleStep(1)
        self.padding.setValue(4)

        # Start Button
        self.startButton = QtWidgets.QPushButton("Rename Start")
        self.startButton.setToolTip('Push this button to <b>start renaming!</b>')
        self.startButton.setDefault(True)
        self.startButton.clicked.connect(self.on_click)


    def create_layouts(self):
        
        main_layout = QtWidgets.QGridLayout(self)

        # File Path
        main_layout.addWidget(self.filePathPrompt, 0, 0)
        main_layout.addWidget(self.filePath, 0, 1, 1, 5)

        # File Path
        main_layout.addWidget(self.scenePrompt, 1, 0)
        main_layout.addWidget(self.scene, 1, 1)
        main_layout.addWidget(self.formatPrompt, 1, 2)
        main_layout.addWidget(self.format, 1, 3)
        main_layout.addWidget(self.folderPathPrompt, 1, 4)
        main_layout.addWidget(self.folderPath, 1, 5)

        # Render Start Frame & End Frame
        main_layout.addWidget(self.frameStartPrompt, 2, 0)
        main_layout.addWidget(self.frameStart, 2, 1)
        main_layout.addWidget(self.frameEndPrompt, 2, 2)
        main_layout.addWidget(self.frameEnd, 2, 3)

        # Padding
        main_layout.addWidget(self.paddingPrompt, 2, 4)
        main_layout.addWidget(self.padding, 2, 5)

        # File Override
        main_layout.addWidget(self.fileOverridePrompt, 3, 1)
        main_layout.addWidget(self.fileOverride, 3, 2, 1, 3)

        # Start Button
        main_layout.addWidget(self.startButton, 4, 2, 1, 3)

    ######################################## NUM LIST OPERATIONS ########################################
    def get_numList(self, num):
        '''
        Returns a broken down list of numbers with appropriate "-"
        '''
        isNeg = False
        
        if (num < 0):
            num = num * -1
            isNeg = True
            
        res = list(map(str, [int(x) for x in str(num)]))
        if(isNeg):
            res.insert(0, "-")
            
        return(res)

    def padding_format(self, number, padding):
        """
        Returns the correct padding of a number
        """
        if number >= 0:
            return ("%0" + str(padding) + "d") % number  # Positive + Zero Case
        else:
            number_list = self.get_numList(number)
            if len(number_list) > padding:
                raise Exception("[AnimKit Rename Renders] ERROR - number_list is larger than padding!!!")
            elif len(number_list) < padding:
                need_zeroes = padding - len(number_list)
                for x in range(0, need_zeroes):
                    number_list.insert(0, "0")
            
            return "".join(number_list)


    ######################################## MAIN OPERATION ########################################

    def on_click(self):
        scene_name = self.scene.text()
        seq_folder = self.filePath.directory().absolutePath() + "/"
        frameEnd = self.frameEnd.value()
        frameStart = self.frameStart.value()
        padding = self.padding.value()
        orig_format = self.format.text()
        folder_name = self.folderPath.text()

        # Check if override
        if self.fileOverride.text() != "":
            print("[AnimKit Rename Renders] Override detected: " + self.fileOverride.text())
            override_text = self.fileOverride.text()
            if not (override_text.endswith('\\') or override_text.endswith('/')):
                print("[AnimKit Rename Renders] File path does not end with a \\ or /. Adding a slash to the end of file path.")
                override_text = override_text + "\\"
            seq_folder = override_text
            print("[AnimKit Rename Renders] New file path: " + seq_folder)
        else:
            print("[AnimKit Rename Renders] No override detected. Proceed.")
            

        # Create temp folder
        temp_folder = seq_folder + folder_name
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.makedirs(temp_folder)

        # Make sequence list
        sequence_list = list(range(frameStart, frameEnd + 1, 1))  # Make Num List

        for index, value in enumerate(sequence_list):
            sequence_list[index] = scene_name + "_" + self.padding_format(value, padding) + orig_format
            
        # Copying everything into a new temp folder
        counter = 1
        for index, value in enumerate(sequence_list):
            source = seq_folder + value
            destination = temp_folder+ "/" + str(counter) + orig_format
            shutil.copyfile(source, destination) 
            percentage = int(100.0 * counter / len(sequence_list))
            print("[AnimKit Rename Renders] Image Process Progress: " + str(percentage) + "% [" + str(counter) + "/" + str(len(sequence_list)) + "].") # Just to see progress
            counter += 1



def rename_renders(self):
    d = ShowDialog()
    d.show()


# if __name__ == "__main__":

#     d = ShowDialog()
#     d.show()

