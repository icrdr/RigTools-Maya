import maya.cmds as cmds
import maya.OpenMaya as om
from functools import partial

import os, json

import utility, functions, autoRig

reload(utility)
reload(functions)
reload(autoRig)

MAIN_PATH = os.path.dirname(__file__)+'/'
CURVE_PATH = MAIN_PATH + 'curves/'

cmds.evalDeferred("""icrdrTools.interface._popupMenu()""")

def addSeparator():
    return cmds.separator(en=1, w=12, h=35, vis=1, m=1, po=0, ebg=0, hr=0, st="shelf")

def _null():
    pass

class toolWindow(object):
    def __init__(self, name, title='', dockable=False):
        self.name = name
        self.title = title
        self.dockable = dockable

        self.minimizeButton = False
        self.maximizeButton = False
        
        self.initWindow()


    def build(self, window_):
        pass

    def initWindow(self):
        if self.dockable:
            if cmds.workspaceControl(self.name, q=True, exists=True):
                cmds.deleteUI(self.name, control=True)
            self.window = cmds.workspaceControl(self.name, label=self.title, retain=False, vcc=self._applyWindowSet)

        else:
            if cmds.window(self.name, q=True, exists=True):
                cmds.deleteUI(self.name, control=True)
            self.window = cmds.window(self.name, t=self.title, mnb=self.minimizeButton, mxb=self.maximizeButton)

    def run(self):
        self.build(self.window)
        cmds.showWindow(self.window)

    def setWindow(self, width=100, height=1, sizable=False, minimizeButton=False, maximizeButton=False):
        self.minimizeButton = minimizeButton
        self.maximizeButton = maximizeButton
        if self.dockable:
            cmds.workspaceControl(self.window, e=True, resizeWidth=width, resizeHeight=height)
        else:
            cmds.window(self.window, e=True, w=width, h=height, s=sizable, mnb=self.minimizeButton, mxb=self.maximizeButton)

    def _applyWindowSet(self, *args):
        if cmds.window(self.name, q=True, exists=True):
            cmds.window(self.name, e=True, mnb=self.minimizeButton, mxb=self.maximizeButton, topLeftCorner=(300,1000))


    def __str__(self):
        return self.name

class choiceWindow(toolWindow):
    def __init__(self, name, title='', info_text='?', c1_text='1', c2_text='2', command1=_null, command2=_null):
        super(choiceWindow, self).__init__(name, title)
        self.infoText = info_text
        self.c1_text = c1_text
        self.c2_text = c2_text
        self.command1 = command1
        self.command2 = command2

    def build(self, window_):
        cmds.window(window_, edit=True, width=220, minimizeButton=0, maximizeButton=0)
        form = cmds.formLayout(p=window_)
        colmain = cmds.columnLayout(p=form, columnAttach=(
            'both', 10), rowSpacing=10, columnWidth=220)

        cmds.text(
            label=self.infoText,
            align='left',
            wordWrap=1
        )

        cmds.rowLayout(p=colmain, numberOfColumns=2, columnWidth2=(
            100, 100), columnAttach=[(1, 'both', 0), (2, 'both', 0)])

        cmds.button("btnOverride", l=self.c1_text,
                    h=30, c=self.doChoice1)

        cmds.button("btnKeep", l=self.c2_text,
                    h=30, c=self.doChoice2)

        cmds.formLayout(
            form,
            edit=True,
            attachForm=[
                (colmain, 'top', 10),
                (colmain, 'bottom', 10)
            ],
        )

    def doChoice1(self, *args):
        self.command1()
        cmds.deleteUI(self.window)

    def doChoice2(self, *args):
        self.command2()
        cmds.deleteUI(self.window)

def makeChoice(title='Make Choice', info_text='?', c1_text='1', c2_text='2', command1=_null, command2=_null, *args):
    choice_window = choiceWindow(
        "makeSureWindow",
        title,
        info_text,
        c1_text,
        c2_text,
        command1,
        command2,
    )
    choice_window.run()

def makeSure(info, command, *args):
    f = partial(
        makeChoice,
        "Sure?",
        info, 
        'Sure', 
        'Cancel', 
        command)
    f()

'''====================================================================================================================

MainShelf

===================================================================================================================='''
class mainShelfWindow(toolWindow):
    def build(self, window_):
        self.setWindow(216,200)
        form = cmds.formLayout(p=window_)
        shelf = cmds.shelfLayout(h=47, w=47, cellWidthHeight=[42, 42])

        cmds.iconTextButton(
            label="zero all transformation",
            image="zero_all.png",
            command=self._zeroAll
        )
        """
        cmds.iconTextButton(
            "btnSaveLoadTransform",
            label="Save or load Transform",
            statusBarMessage="Save or load selected object's transform.",
            image="save_transform.png",
            command=functions.saveTransform
        )
        """
        cmds.iconTextButton(
            label="Toggle Display",
            statusBarMessage="Display only meshes and curves or not.",
            image="display_mesh.png"
        )

        p = cmds.popupMenu(b=1)

        cmds.menuItem(
            parent=p,
            label="Display All",
            command=functions.displayAll
        )

        cmds.menuItem(
            parent=p,
            label="Mesh and Curve Only ",
            command=functions.displayMeshCurve
        )

        cmds.menuItem(
            parent=p,
            label="Mesh Only ",
            command=functions.displayMesh
        )

        cmds.iconTextButton(
            label="Control Curves",
            statusBarMessage="Create curves",
            image="control_curves.png",
            command=self._createCrv,
        )

        cmds.iconTextButton(
            label="Merge Curves",
            statusBarMessage="Merge selected curves' shape into one object.",
            image="smoothCurve.png",
            command=self._mergeCurves,
            doubleClickCommand=self._replaceCurves
        )

        cmds.iconTextButton(
            label="Snap Transform",
            statusBarMessage="Snap one object to the other.",
            image="snapTogetherTool.png",
            command=self._snapTransform,
            doubleClickCommand=self._snapPivot
        )

        cmds.iconTextButton(
            label="Group Tt",
            statusBarMessage="Group the every selected object at same position, than transfer items' transformation to it's group.",
            image="group_it.png",
            command=self._groupIt
        )

        cmds.iconTextButton(
            label="Space Switch Setup",
            statusBarMessage="Create a space switching system form selection.",
            image="parent.png",
            command=self._spaceSwitchSetup
        )

        cmds.iconTextButton(
            label="Joint Orient",
            statusBarMessage="Orient Joint to custom world up.",
            image="orientJoint.png",
            command=self._orientJoint
        )

        cmds.iconTextButton(
            label="Mirror Orient",
            statusBarMessage="Better than default.",
            image="kinMirrorJoint_S.png",
            command=self._mirrorJoint
        )

        cmds.iconTextButton(
            label="Auto FKIK",
            statusBarMessage="Auto build FKIK switch system.",
            image="auto_fkik.png",
            command=self._autoFKIK
        )

        cmds.iconTextButton(
            label="Auto SplineFKIK",
            statusBarMessage="Auto build SplineFKIK switch system.",
            image="auto_spline_fkik.png",
            command=self._autoSplineFKIK
        )

        cmds.formLayout(
            form,
            edit=True,
            attachForm=(
                (shelf, 'top', 0),
                (shelf, 'left', 0),
                (shelf, 'bottom', 0),
                (shelf, 'right', 0))
        )
    def _zeroAll(self, *args):
        sl = utility.checkSelection([('any',1,0)])
        if sl: functions.zeroAll(sl)

    def _replaceCurves(self, *args):
        sl = utility.checkSelection([('nurbsCurve',2,2)])
        if sl: functions.replaceCurves(sl[0], sl[1])

    def _mergeCurves(self, *args):
        sl = utility.checkSelection([('nurbsCurve',2,0)])
        if sl: functions.mergeCurves(sl)

    def _groupIt(self, *args):
        sl = utility.checkSelection([('any',1,0)])
        if sl:
            if utility.detectConnect(sl):
                makeChoice(
                    "Warning",
                    "Detected that transformation has connections, break them will change behavior, keep them may cause object shifting, so what's your choice?",
                    "Break them",
                    "Keep them",
                    partial(functions.groupIt,sl,1),
                    partial(functions.groupIt,sl,0)
                )

            else:
                functions.groupIt(sl, 1)

    def _spaceSwitchSetup(self, *args):
        sl = utility.checkSelection([('any',2,0)])
        if sl: functions.spaceSwitchSetup(sl[0:-1], sl[-1])

    def _snapTransform(self, *args):
        sl = utility.checkSelection([('any',2,0)])
        if sl: functions.snapTransform(sl[0], sl[1])

    def _snapPivot(self, *args):
        sl = utility.checkSelection([('any',2,0)])
        if sl: functions.snapPivot(sl[0], sl[1])

    def _autoFKIK(self, *args):
        sl = utility.checkSelection([('joint',2,2),('any',1,1)])
        if sl: autoRig.autoFKIK(sl[0], sl[1], sl[2])

    def _autoSplineFKIK(self, *args):
        sl = utility.checkSelection([('joint',2,2),('any',1,1)])
        if sl: autoRig.autoSplineFKIK(sl[0], sl[1], sl[2])

    def _orientJoint(self, *args):
        orient_jnt_Window = orientJntWindow('OrientJointsWindow','Orient Joints Window')
        orient_jnt_Window.run()

    def _mirrorJoint(self, *args):
        mirror_jnt_Window = mirrorJntWindow('mirrorJointsWindow','Mirror Joints Window')
        mirror_jnt_Window.run()

    def _createCrv(self, *args):
        create_crv_Window = createCrvWindow('createCurveWindow','Create Curve Window',True)
        create_crv_Window.run()

'''====================================================================================================================

popupMenu

===================================================================================================================='''
def _followMenu(menu, obj, target_list):
    for inx, target in enumerate(target_list):
        cmds.menuItem(p=menu, l=target, c=partial(
            functions.changeSpace, obj, inx))


def _choiceMenu(menu, parent):
    if cmds.popupMenu('icrdrPopup', ex=1):
        cmds.popupMenu('icrdrPopup', e=1, deleteAllItems=1)
    sl = cmds.ls(sl=1)
    if not sl:
        return

    if len(sl) == 1 and cmds.attributeQuery('follow', node=sl[0], ex=1):
        target_list = cmds.attributeQuery('follow', node=sl[0], listEnum=1)
        target_list = target_list[0].split(':')
        # print(target_list)
        if target_list:
            _followMenu(menu, sl[0], target_list)


def _popupMenu():
    if cmds.popupMenu('icrdrPopup', ex=1):
        cmds.deleteUI('icrdrPopup')
    icrdrPopup = cmds.popupMenu(
        'icrdrPopup', mm=1, b=1, aob=1, ctl=1, alt=1, sh=0, p="viewPanes", pmc=_choiceMenu)



'''====================================================================================================================

createCurvesWindow

===================================================================================================================='''
class createCrvWindow(toolWindow):
    colorPalette = [
        (1.0, 0.1, 0.21),
        (1.0, 0.25, 0.22),
        (0.91, 0.55, 0.32),
        (1, 0.8, 0.0),
        (0.6, 1.0, 0.0),
        (0.3, 1.0, 0.37),
        (0.26, 0.84, 1.0),
        (0.18, 0.41, 1.0),
        (0.38, 0.2, 1.0),
        (0.85, 0.26, 1.0),
        (0.9, 0.9, 0.9),
        (0.8, 0.8, 0.8),
        (0.5, 0.5, 0.5),
        (0.1, 0.1, 0.1),
    ]
    def build(self, window_):
        self.setWindow(width=230, sizable=0)
        form = cmds.formLayout(p=window_)

        colmain = cmds.columnLayout(p=form, columnAttach=(
            'both', 10), rowSpacing=10, columnWidth=230)
        #cmds.button("setColor", l="Set Curve Color", h=30, ann="Set Curve Color", command=functions.applyColor)

        cmds.canvas('colorDisplay', rgbValue=utility.sRGBtoLinear(
            self.colorPalette[0]), width=210, height=30, pressCommand=self._editColor)

        palette = cmds.gridLayout(numberOfColumns=7, cellWidthHeight=(30, 30))
        for inx, colr in enumerate(self.colorPalette):
            colr = utility.sRGBtoLinear(colr)
            name = 'colorPalette'+str(inx)
            cmds.canvas(name, width=30, height=30, rgbValue=colr,
                        pressCommand=partial(self._selectColor, name))

        shelf = cmds.shelfLayout(p=colmain, backgroundColor=(
            0.185, 0.185, 0.185), cellWidthHeight=(66, 66), spacing=3, w=210, h=210)

        def addCurveBtn():
            sl = utility.checkSelection([('nurbsCurve',1,1)])
            if sl:
                functions.saveCurve(sl[0])
                button_list = cmds.shelfLayout(shelf, q=1, childArray=1)[1:]
                #print(button_list)
                for btn in button_list:
                    cmds.deleteUI(btn)
                
                listAllCurve()

        def deleteCurveBtn(btnName, *args):
            curveName = btnName[4:]
            jsonFile = curveName + ".json"
            imageFile = curveName + ".png"
            os.remove(CURVE_PATH+jsonFile)
            os.remove(CURVE_PATH+imageFile)
            cmds.deleteUI(btnName)

        cmds.iconTextButton(
            'btnSaveCurve',
            image='add_new.svg',
            command=addCurveBtn,
        )

        def listAllCurve():
            curvesInfo = []
            curvesJson = utility.getFileList(CURVE_PATH, ext='json', sort='create')
            for file in curvesJson:
                with open(CURVE_PATH+file, 'r') as f:
                    data = json.load(f)
                    curvesInfo.append(data)

            for info in curvesInfo:
                cmds.iconTextButton(
                    'btn_' + info['name'],
                    st='iconAndTextVertical',
                    scaleIcon=1,
                    # backgroundColor=(0.32,0.52,0.65),
                    parent=shelf,
                    image=CURVE_PATH + info['icon'],
                    label=info['name'],
                    command=partial(
                        self._createCurves,
                        info['shape']
                    ),
                )
                p = cmds.popupMenu(b=3)
                cmds.menuItem(
                    p=p,
                    l='import',
                    c=partial(
                        self._createCurves,
                        info['shape']
                    ))
                infoText = 'Do you want to delete "' + \
                    info['name']+'"? This action is not undoable.'
                command = partial(
                    deleteCurveBtn,
                    'btn_' + info['name']
                )
                cmds.menuItem(
                    p=p,
                    l='delete',
                    c=partial(
                        makeSure,
                        infoText,
                        command
                    )
                )
        listAllCurve()

        cmds.formLayout(
            form,
            edit=True,
            attachForm=[
                (colmain, 'top', 10),
                (colmain, 'bottom', 10),
            ],
        )

    def _editColor(self):
        color = utility.LineartosRGB(cmds.canvas('colorDisplay', q=1, rgbValue=1))
        cmds.colorEditor(rgb=color)
        if cmds.colorEditor(query=True, result=True):
            rgbV = cmds.colorEditor(query=True, rgb=True)
            rgbV = utility.sRGBtoLinear(rgbV)
            cmds.canvas('colorDisplay', e=1, rgbValue=rgbV)
            functions.applyCurvesColor(utility.LineartosRGB(rgbV))
        else:
            print('Editor was dismissed')

    def _selectColor(self, name, *args):
        rgbV = cmds.canvas(name, q=1, rgbValue=1)
        cmds.canvas('colorDisplay', e=1, rgbValue=rgbV)
        functions.applyCurvesColor(utility.LineartosRGB(rgbV))

    def _createCurves(self, shapes, *args):
        color = utility.LineartosRGB(cmds.canvas('colorDisplay', q=1, rgbValue=1))
        functions.createCurves(shapes, color)

'''====================================================================================================================

orientJointsWindow

===================================================================================================================='''
class orientJntWindow(toolWindow):
    def build(self, window_):
        self.setWindow(width=540, sizable=0)
        form = cmds.formLayout(p=window_)

        colmain = cmds.columnLayout(p=form, columnAttach=(
            'both', 10), rowSpacing=10, columnWidth=540)
        col1 = cmds.columnLayout(columnAttach=('both', 0),
                                rowSpacing=0, columnWidth=520)
        row1 = cmds.rowLayout(p=col1, numberOfColumns=1,
                            columnWidth1=350, columnAttach=[(1, 'both', 0)])
        cmds.radioButtonGrp("rbgAim", l="Primary Axis: ", nrb=3, la3=(
            "X", "Y", "Z"), sl=1, cw4=(190, 50, 50, 50), changeCommand=self._upChange)

        row2 = cmds.rowLayout(p=col1, numberOfColumns=2, columnWidth2=(
            350, 170), columnAttach=[(1, 'both', 0), (2, 'both', 0)])
        cmds.radioButtonGrp("rbgUp", l="Secondary Axis: ", nrb=3, la3=(
            "X", "Y", "Z"), sl=2, cw4=(190, 50, 50, 50), changeCommand=self._aimChange)
        cmds.checkBox("chbReverseUp", l="Reverse")

        row3 = cmds.rowLayout(p=col1, numberOfColumns=2, columnWidth2=(
            350, 170), columnAttach=[(1, 'both', 0), (2, 'both', 0)])
        cmds.floatFieldGrp("rbgWorldUp", l="Secondary Axis World Orientation: ",
                        nf=3, v1=0.0, v2=1.0, v3=0.0, cw4=(190, 50, 50, 50), pre=2)
        cmds.button("btnSetWorldUp", l="Set from selected object",
                    h=20, c=self._setWorldUp)

        col2 = cmds.columnLayout(p=colmain, columnAttach=(
            'left', 190), rowSpacing=0, columnWidth=520, adjustableColumn=True)
        cmds.checkBox("chbAllOrSelected",
                    l="Orient children of selected joints", v=1)
        cmds.checkBox("chbGuess", l="Guess Up Direction", v=0,
                    offCommand=self._enableWorldOrient, onCommand=self._disableWorldOrient)

        row4 = cmds.rowLayout(p=colmain, numberOfColumns=2, columnWidth2=(
            260, 260), columnAttach=[(1, 'both', 0), (2, 'both', 0)])
        cmds.button("btnShowLocalAxis", l="Show LocalAxis",
                    h=30, c=self._showSelectedLocalAxis)
        cmds.button("btnHideLocalAxis", l="Hide LocalAxis",
                    h=30, c=self._hideSelectedLocalAxis)

        col3 = cmds.columnLayout(p=colmain, columnAttach=(
            'both', 0), rowSpacing=0, columnWidth=520)
        cmds.button("btnOrientJoints", l="Orient Joints", h=30,
                    c=self._orientJointsUI, ann="Orient Joints")

        cmds.formLayout(
            form,
            edit=True,
            attachForm=[
                (colmain, 'top', 10),
                (colmain, 'bottom', 10)
            ],
        )

    def _disableWorldOrient(self, *args):
        cmds.button("btnSetWorldUp", e=1, en=0)
        cmds.floatFieldGrp("rbgWorldUp", e=1, en=0)


    def _enableWorldOrient(self, *args):
        cmds.button("btnSetWorldUp", e=1, en=1)
        cmds.floatFieldGrp("rbgWorldUp", e=1, en=1)


    def _aimChange(self, *args):
        aimSelected = cmds.radioButtonGrp("rbgAim", q=True, sl=True)
        upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)
        if aimSelected == upSelected:
            aimSelected = aimSelected + 1
            if aimSelected > 2:
                aimSelected = 0
            cmds.radioButtonGrp("rbgAim", e=1, sl=aimSelected)

    def _upChange(self, *args):
        aimSelected = cmds.radioButtonGrp("rbgAim", q=True, sl=True)
        upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)
        if aimSelected == upSelected:
            upSelected = upSelected + 1
            if upSelected > 2:
                upSelected = 0
            cmds.radioButtonGrp("rbgUp", e=1, sl=upSelected)

    def _showSelectedLocalAxis(self, *args):
        sl = utility.checkSelection([('any',1,0)])
        if sl: functions.doToggleLocalAxis(sl, 1)

    def _hideSelectedLocalAxis(self, *args):
        sl = utility.checkSelection([('any',1,0)])
        if sl: functions.doToggleLocalAxis(sl, 0)

    def _orientJointsUI(self, *args):
        sl = utility.checkSelection([('joint',1,0)])
        if sl:
            aimSelected = cmds.radioButtonGrp("rbgAim", q=True, sl=True)
            upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)

            upReverse = cmds.checkBox("chbReverseUp", q=True, v=True)

            worldUp = [0, 0, 0]
            worldUp[0] = cmds.floatFieldGrp("rbgWorldUp", q=True, v1=True)
            worldUp[1] = cmds.floatFieldGrp("rbgWorldUp", q=True, v2=True)
            worldUp[2] = cmds.floatFieldGrp("rbgWorldUp", q=True, v3=True)

            operateOn = cmds.checkBox("chbAllOrSelected", q=True, v=True)
            guessUp = cmds.checkBox("chbGuess", q=True, v=True)

            aimAxis = [0, 0, 0]
            upAxis = [0, 0, 0]

            aimAxis[aimSelected - 1] = 1

            if upReverse == 1:
                upAxis[upSelected - 1] = -1
            else:
                upAxis[upSelected - 1] = 1

            if operateOn == 1:
                # Hierarchy
                cmds.select(hi=True)
                jointsToOrient = cmds.ls(typ="joint", sl=1)
            else:
                # Selected
                jointsToOrient = cmds.ls(typ="joint", sl=1)
            # print(jointsToOrient)

            functions.orientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp)
            functions.rotateOrder(jointsToOrient, aimAxis, upAxis)

    def _setWorldUp(self, *args):
        sl = utility.checkSelection([('any',1,0)])
        if sl:
            upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)
            upReverse = cmds.checkBox("chbReverseUp", q=True, v=True)
            upAxis = [0, 0, 0]
            if upReverse == 1:
                upAxis[upSelected - 1] = -1
            else:
                upAxis[upSelected - 1] = 1

            objVector = utility.getVector(sl[0], upAxis)
            cmds.floatFieldGrp("rbgWorldUp", e=1, v1=objVector[0])
            cmds.floatFieldGrp("rbgWorldUp", e=1, v2=objVector[1])
            cmds.floatFieldGrp("rbgWorldUp", e=1, v3=objVector[2])
            cmds.select(sl, r=True)



'''====================================================================================================================

mirrorJointsWindow

===================================================================================================================='''
class mirrorJntWindow(toolWindow):
    def build(self, window_):
        self.setWindow(width=540, sizable=0)

        form = cmds.formLayout(p=window_)
        colmain = cmds.columnLayout(p=form, columnAttach=(
            'both', 10), rowSpacing=10, columnWidth=540)
        col1 = cmds.columnLayout(columnAttach=('both', 0),
                                rowSpacing=0, columnWidth=520)
        cmds.radioButtonGrp("rbgPlane", l="Mirror across: ", nrb=3, la3=(
            "XY", "YZ", "XZ"), sl=2, cw4=(160, 80, 80, 80))

        cmds.radioButtonGrp("rbgMode", l="Mirror function: ", nrb=3, la3=(
            "Align Axis", "Behavior", "Orientation"), sl=2, cw4=(160, 80, 80, 80), changeCommand=self._toggleMode)

        cmds.radioButtonGrp("rbgAim1", l="Primary Axis: ", nrb=3, en=0, la3=(
            "X", "Y", "Z"), sl=1, cw4=(160, 80, 80, 80), changeCommand=self._upChange1)

        cmds.radioButtonGrp("rbgUp1", l="Secondary Axis: ", nrb=3, en=0, la3=(
            "X", "Y", "Z"), sl=2, cw4=(160, 80, 80, 80), changeCommand=self._aimChange1)

        col2 = cmds.columnLayout(p=colmain, columnAttach=(
            'left', 0), rowSpacing=0, columnWidth=520, adjustableColumn=True)
        cmds.textFieldGrp("txtSearch", cw2=(160, 0),
                        l='Search for: ', adjustableColumn2=2)
        cmds.textFieldGrp("txtReplace", cw2=(160, 0),
                        l='Replace with: ', adjustableColumn2=2)

        row1 = cmds.rowLayout(p=colmain, numberOfColumns=1,
                            adjustableColumn=1, w=520, columnAttach=[(1, 'both', 0)])
        cmds.button("btnMirrorJoints", l="Mirror Joints", h=30,
                    c=self._mirrorJointUI, ann="Mirror Joints")

        cmds.formLayout(
            form,
            edit=True,
            attachForm=[
                (colmain, 'top', 10),
                (colmain, 'bottom', 10)
            ],
        )


    def _aimChange1(self, *args):
        aimSelected = cmds.radioButtonGrp("rbgAim1", q=True, sl=True)
        upSelected = cmds.radioButtonGrp("rbgUp1", q=True, sl=True)
        if aimSelected == upSelected:
            aimSelected = aimSelected + 1
            if aimSelected > 2:
                aimSelected = 0
            cmds.radioButtonGrp("rbgAim1", e=1, sl=aimSelected)


    def _upChange1(self, *args):
        aimSelected = cmds.radioButtonGrp("rbgAim1", q=True, sl=True)
        upSelected = cmds.radioButtonGrp("rbgUp1", q=True, sl=True)
        if aimSelected == upSelected:
            upSelected = upSelected + 1
            if upSelected > 2:
                upSelected = 0
            cmds.radioButtonGrp("rbgUp1", e=1, sl=upSelected)


    def _toggleMode(self, *args):
        mirrorMode = cmds.radioButtonGrp("rbgMode", q=1, sl=1)
        if mirrorMode == 1:
            cmds.radioButtonGrp("rbgAim1", e=1, en=1)
            cmds.radioButtonGrp("rbgUp1", e=1, en=1)
        else:
            cmds.radioButtonGrp("rbgAim1", e=1, en=0)
            cmds.radioButtonGrp("rbgUp1", e=1, en=0)

    def _mirrorJointUI(self, *args):
        aimSelected = cmds.radioButtonGrp("rbgAim1", q=1, sl=1)
        upSelected = cmds.radioButtonGrp("rbgUp1", q=1, sl=1)
        mirrorPlane = cmds.radioButtonGrp("rbgPlane", q=1, sl=1)
        mirrorMode = cmds.radioButtonGrp("rbgMode", q=1, sl=1)
        searchStr = cmds.textFieldGrp("txtSearch", q=1, tx=1)
        replaceStr = cmds.textFieldGrp("txtReplace", q=1, tx=1)
        replace = (searchStr, replaceStr)

        aimAxis = [0, 0, 0]
        upAxis = [0, 0, 0]

        aimAxis[aimSelected - 1] = 1
        upAxis[upSelected - 1] = 1

        functions.mirrorJoint(mirrorMode, mirrorPlane, aimAxis, upAxis, replace)