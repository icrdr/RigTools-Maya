import maya.cmds as cmds
import maya.OpenMaya as om
from functools import partial
import os, json, utility

reload(utility)

MAIN_PATH = os.path.dirname(__file__)+'/'
CURVE_PATH = MAIN_PATH + 'curves/'

def replaceCurves(originCurve, targetCurve):
    snapPivot(originCurve, targetCurve)

    targetShape = utility.getShapes(targetCurve)
    if targetShape:
        cmds.delete(targetShape)

    curveShapes = utility.getShapes(originCurve)
    for curveShape in curveShapes:
        cmds.parent(curveShape, targetCurve, r=1, s=1)

    originCurve = utility.unParentToWorld([originCurve])
    # delect
    cmds.delete(originCurve)

    cmds.select(targetCurve)


def mergeCurves(curves):
    curves = utility.unParentToWorld(curves)

    for curve in curves:
        cmds.makeIdentity(curve, a=1)
        cmds.bakePartialHistory(curve, pc=1)

    # set newTransform as first in selection
    groupTransform = curves[0]

    # get groupTransform
    grp = cmds.group(em=1)
    #cmds.matchTransform(grp, groupTransform)
    groupTransform = grp

    for curve in curves:
        # make sure curveShapes don't move
        cmds.makeIdentity(curve, a=1)

        # merge to groupTransform
        curveShapes = utility.getShapes(curve)
        for curveShape in curveShapes:
            cmds.parent(curveShape, groupTransform, r=1, s=1)

        # delect rest
        cmds.delete(curve)

    # center pivot and clear history
    cmds.xform(groupTransform, cp=1)
    cmds.bakePartialHistory(groupTransform, pc=1)
    cmds.select(groupTransform)

def groupIt(ctls, mode=0,*arg):
    
    if mode:
        ctls, SAVE_LIST = utility.unParentToWorld(ctls, parentChild=0, save=1, disconnect=1)
    else:
        ctls, SAVE_LIST = utility.unParentToWorld(ctls, parentChild=0, save=1, disconnect=0)
    print(SAVE_LIST)
    for inx, ctl in enumerate(ctls):
        # identity scale
        cmds.makeIdentity(ctl, a=1, s=1)
        # create group
        grp = cmds.group(em=1)

        # parent ctl to grp
        cmds.matchTransform(grp, ctl)
        ctls[inx] = cmds.parent(ctl, grp)[0]

    # reparent the grp
    ctls = utility.reparentToOrigin(SAVE_LIST, relatedObjs = ctls)

    group_list=[]
    # rename all
    uCtls = cmds.ls(ctls, uid=1)
    for uCtl in uCtls:
        ctl = cmds.ls(uCtl, l=1)[0]
        grp = utility.getPrt(ctl)

        ctl_name = ctl.split("|")[-1]
        grp = cmds.rename(grp, ctl_name+"_grp")
        group_list.append(grp)
    ctls = cmds.ls(uCtls, l=1)

    cmds.select(ctls)

    return group_list
    

def spaceSwitchSetup(targets, contained):
    contained_grp = utility.getPrt(contained)
    if not contained_grp or utility.getShapes(contained_grp):
        contained_grp = groupIt([contained])[0]

    select_list = []

    # check if it already parentconstrainted
    constraint = cmds.listConnections(
        "%s.translateX" % contained_grp, d=0, s=1)
    oldLoc = ''
    loc_name = contained.split("|")[-1].split(":")[-1] + '_loc'
    if constraint:
        constraint = constraint[0]

        loc_weight_name = cmds.listAttr(constraint, st=loc_name+"*", ud=1)
        print(loc_name)
        print(loc_weight_name)
        if loc_weight_name:
            target_name = cmds.listConnections(
                constraint+'.'+loc_weight_name[0], d=1, s=0, p=1)[0]
            target_name = target_name.replace(
                'targetWeight', 'targetTranslate')
            oldLoc = cmds.listConnections(target_name, d=0, s=1)[0]

    if not oldLoc:
        loc = cmds.spaceLocator(name=loc_name)[0]
        cmds.matchTransform(loc, contained_grp)
        contained_grp_prt = utility.getPrt(contained_grp)
        if contained_grp_prt:
            loc = cmds.parent(loc, contained_grp_prt)[0]

        cmds.setAttr("%s.v"%loc, 0)
        utility.fixedObj([loc])

        oldLoc = loc

    print(oldLoc)
    select_list.append(oldLoc)
    loc_name = oldLoc.split("|")[-1].split(":")[-1]
    print(loc_name)

    for target in targets:
        select_list.append(target)

    select_list.append(contained_grp)

    cmds.select(cl=1)
    for obj in select_list:
        cmds.select(obj, add=1)

    constraint = cmds.parentConstraint(mo=1)[0]

    target_list = cmds.listAttr(constraint, st="*W*", ud=1)
    print(target_list)

    # edit enum
    enumName = ''
    parentInx = 0
    for inx, target in enumerate(target_list):
        if loc_name == target[0:-2]:
            parentInx = inx
            enumName = enumName + ":origin"
        else:
            enumName = enumName + ":" + target[0:-2]

    enumName = enumName[1:]

    if cmds.attributeQuery('follow', node=contained, ex=1):
        # edit
        cmds.addAttr("%s.follow" % contained, k=1, e=1,
                     ln="follow", at="enum", en=enumName)
    else:
        # create
        cmds.addAttr(contained, k=1, ln="follow", at="enum", en=enumName)

    # set to parent as defualt
    cmds.setAttr("%s.follow" % contained, parentInx)

    condition_nodes = cmds.listConnections("%s.follow" % contained, d=1, s=0)
    # print(condition_nodes)
    if condition_nodes:
        for nodes in condition_nodes:
            cmds.delete(nodes)
    # connect node
    for inx, target in enumerate(target_list):
        condition_node = cmds.shadingNode("condition", au=1)

        cmds.connectAttr("%s.follow" % contained,
                         "%s.firstTerm" % condition_node, f=1)

        weight_name = constraint+"."+target

        cmds.connectAttr("%s.outColorR" % condition_node, weight_name, f=1)
        cmds.setAttr("%s.secondTerm" % condition_node, inx)
        cmds.setAttr("%s.operation" % condition_node, 1)
    
    cmds.select(contained)


def changeSpace(obj, inx, *arg):
    loc = cmds.spaceLocator()
    cmds.matchTransform(loc, obj)

    cmds.setAttr("%s.follow" % obj, inx)

    cmds.matchTransform(obj, loc)
    cmds.delete(loc)
    cmds.select(obj)


def saveTransform(obj):
    loc = cmds.ls("xLEAVEMEALONE")
    if loc:
        cmds.iconTextButton(
            'btnSaveLoadTransform',
            e=1,
            image='save_transform.png'
        )
        loc = cmds.ls("xLEAVEMEALONE")
        cmds.matchTransform(obj, loc)
        cmds.delete(loc)
        cmds.select(obj)
    else:
        cmds.iconTextButton(
            'btnSaveLoadTransform',
            e=1,
            image='load_transform.png'
        )
        loc = cmds.spaceLocator(name="xLEAVEMEALONE")[0]
        cmds.matchTransform(loc, obj)
        cmds.setAttr("%s.v"%loc, 0)
        utility.fixedObj([loc])
        cmds.select(obj)

def snapTransform(obj, tar):
    if '.vtx[' in tar:
        cmds.select(cl=1)
        cmds.select(tar)
        cmds.select(obj, add=1)
        constraint = cmds.pointOnPolyConstraint(mo=0)
        cmds.delete(constraint)
    else:
        cmds.matchTransform(obj, tar)
    
    cmds.select(obj)


def snapPivot(obj, tar):
    isVertex = False
    if '.vtx[' in tar:
        isVertex = True
        loc = cmds.spaceLocator()
        cmds.select(cl=1)
        cmds.select(tar)
        cmds.select(loc, add=1)
        constraint = cmds.pointOnPolyConstraint(mo=0)
        cmds.delete(constraint)
        tar = loc[0]

    objs, SAVE_LIST = utility.unParentToWorld([obj], parentChild=0, save=1, relatedObjs=[obj, tar])
    obj = objs[0]
    tar = objs[1]

    pivotT = cmds.xform(tar, q=1, ws=1, rp=1)

    obj = cmds.parent(obj, tar)

    cmds.makeIdentity(obj, a=1, t=1, r=1, s=1)
    cmds.xform(obj, ws=1, piv=pivotT)
    
    obj = cmds.parent(obj, w=1)

    # reparent
    utility.reparentToOrigin(SAVE_LIST)

    if isVertex:
        cmds.delete(tar)
    
    cmds.select(obj)


def polyToCurve(*args):
    cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=1)
    cmds.bakePartialHistory(pc=1)


def polyToCurveS(*args):
    cmds.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1)
    cmds.bakePartialHistory(pc=1)


def displayAll(*args):
    panel = cmds.getPanel(wf=1)
    print(panel)
    cmds.modelEditor(panel, e=1, alo=1)


def displayMeshCurve(*args):
    panel = cmds.getPanel(wf=1)
    print(panel)
    cmds.modelEditor(panel, e=1, alo=0)
    cmds.modelEditor(panel, e=1, pm=1, nc=1)


def displayMesh(*args):
    panel = cmds.getPanel(wf=1)
    print(panel)
    cmds.modelEditor(panel, e=1, alo=0)
    cmds.modelEditor(panel, e=1, pm=1)


def doToggleLocalAxis(objs, showOrHide):
    operateOn = cmds.checkBox("chbAllOrSelected", q=True, v=True)
    if operateOn == 1:
        # Hierarchy
        cmds.select(hi=True)
        objs = cmds.ls(sl=1)
    else:
        # Selected
        objs = cmds.ls(sl=1)

    for obj in objs:
        cmds.toggle(obj, localAxis=True, state=showOrHide)
    
    cmds.select(objs)


def zeroAll(objs):
    cmds.xform(objs, t=(0, 0, 0), ro=(0, 0, 0), s=(1, 1, 1))



def createCurves(shapes, color, name=""):
    list = []
    for shape in shapes:
        if name:
            crv = cmds.curve(
                n=name,
                p=shape['points'],
                d=shape['degree'],
                k=shape['knot']
            )
        else:
            crv = cmds.curve(
                p=shape['points'],
                d=shape['degree'],
                k=shape['knot']
            )
        list.append(crv)

    for x in range(len(list)-1):
        cmds.makeIdentity(list[x+1], apply=True, t=1, r=1, s=1, n=0)
        shapes = utility.getShapes(list[x+1])
        cmds.parent(shapes, list[0], add=1, s=1)
        cmds.delete(list[x+1])

    utility.applyColor(list[0], color)
    cmds.select(list[0])
    return list[0]


def applyCurvesColor(color, *args):
    sl = cmds.ls(sl=1)

    if len(sl) < 1:
        return False

    for curve in sl:
        shapes = utility.getShapes(curve)
        for shape in shapes:
            if cmds.objectType(shape, i='nurbsCurve'):
                utility.applyColor(curve, color)


def saveCurve(curve):
    shapes = utility.getShapes(curve)
    name = curve.split("|")[-1]
    info = {}
    info['name'] = name
    info['icon'] = name+'.png'
    info['shape'] = []
    for shape in shapes:
        curveInfo = cmds.shadingNode("curveInfo", au=1)
        cmds.connectAttr(shape+'.worldSpace[0]', curveInfo+'.inputCurve', f=1)
        shapeinfo = {
            'points': cmds.getAttr(curveInfo+'.cp[:]'),
            'degree': cmds.getAttr(shape+'.degree'),
            'knot': cmds.getAttr(curveInfo+'.knots[:]')
        }
        # print(cmds.getAttr(curveInfo+'.cp[:]'))
        # print(cmds.getAttr(shape+'.degree'))
        # print(cmds.getAttr(curveInfo+'.knots[:]'))
        cmds.delete(curveInfo)
        info['shape'].append(shapeinfo)
    cmds.select(curve)
    json_path = CURVE_PATH + '%s.json' % name
    img_path = CURVE_PATH + '%s.png' % name

    with open(json_path, 'w') as f:
        json.dump(info, f)

    window = cmds.window(w=120, h=131)
    cmds.paneLayout()
    panel = cmds.modelPanel()
    editor = cmds.modelPanel(panel, me=1, q=1)
    cmds.modelEditor(editor, e=1)
    cmds.modelEditor(editor, e=1, grid=0, hud=0,
                     manipulators=0, selectionHiliteDisplay=1)
    cmds.isolateSelect(panel, state=1)
    cmds.isolateSelect(panel, loadSelected=True)

    cmds.showWindow(window)
    cmds.setFocus(panel)
    cmds.viewFit(curve)
    cmds.refresh(cv=True, fe="png", fn=img_path)
    cmds.isolateSelect(panel, state=0)
    cmds.deleteUI(window)

    return info


def orientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp):
    firstPass = 0
    prevUpVector = [0, 0, 0]
    for eachJoint in jointsToOrient:
        childJoints = utility.getChl(eachJoint,type="joint")
        if childJoints:
            
            # Store the name in case when unparented it changes it's name.
            childJoints = cmds.parent(childJoints, w=1)
            print(childJoints)

            upDirRecalculated = [0,0,0]

            if guessUp == 0:
                # Not guess Up direction

                cmds.delete(cmds.aimConstraint(childJoints[0], eachJoint, w=1, o=(0, 0, 0), aim=aimAxis, upVector=upAxis, worldUpVector=worldUp, worldUpType="vector"))
                _freezeJointOrientation(eachJoint)
                childJoints = cmds.parent(childJoints, eachJoint)
            else:
                # Guess Up direction
                parentJoint = utility.getPrt(eachJoint,type="joint")
                if parentJoint:
                    posCurrentJoint = cmds.xform(eachJoint, q=True, ws=True, rp=True)
                    posParentJoint = cmds.xform(parentJoint, q=True, ws=True, rp=True)
                    tolerance = 0.0001

                    if (abs(posCurrentJoint[0] - posParentJoint[0]) <= tolerance and abs(posCurrentJoint[1] - posParentJoint[1]) <= tolerance and abs(posCurrentJoint[2] - posParentJoint[2]) <= tolerance):
                        aimChild = utility.getChl(childJoints[0],type="joint")
                        upDirRecalculated = _crossProduct(eachJoint, childJoints[0], aimChild[0])
                        cmds.delete(cmds.aimConstraint(childJoints[0], eachJoint, w=1, o=(0, 0, 0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
                    else:
                        upDirRecalculated = _crossProduct(parentJoint, eachJoint, childJoints[0])
                        cmds.delete(cmds.aimConstraint(childJoints[0], eachJoint, w=1, o=(0, 0, 0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
                else:
                    aimChild = utility.getChl(childJoints[0],type="joint")
                    upDirRecalculated = _crossProduct(eachJoint, childJoints[0], aimChild[0])
                    cmds.delete(cmds.aimConstraint(childJoints[0], eachJoint, w=1, o=(0, 0, 0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))

                dotProduct = utility.vectorDot(upDirRecalculated, prevUpVector)

                # For the next iteration
                prevUpVector = upDirRecalculated

                if firstPass > 0 and dotProduct <= 0.0:
                    # dotProduct
                    cmds.xform(eachJoint, r=1, os=1, ra=(
                        aimAxis[0] * 180.0, aimAxis[1] * 180.0, aimAxis[2] * 180.0))
                    prevUpVector[0] *= -1
                    prevUpVector[1] *= -1
                    prevUpVector[2] *= -1

                _freezeJointOrientation(eachJoint)
                childJoints = cmds.parent(childJoints, eachJoint)
        else:
            # Child joint. Use the same rotation as the parent.
            parentJoint = utility.getPrt(eachJoint,type="joint")
            if parentJoint != None:
                if len(parentJoint) > 0:
                    cmds.delete(cmds.orientConstraint(parentJoint, eachJoint, w=1, o=(0, 0, 0)))
                    _freezeJointOrientation(eachJoint)

        firstPass += 1
    
    cmds.select(jointsToOrient)


def _crossProduct(firstObj, secondObj, thirdObj):
    # We have 3 points in space so we have to calculate the vectors from
    # the secondObject (generally the middle joint and the one to orient)
    # to the firstObject and from the secondObject to the thirdObject.
    xformFirstObj = cmds.xform(firstObj, q=True, ws=True, rp=True)
    xformSecondObj = cmds.xform(secondObj, q=True, ws=True, rp=True)
    xformThirdObj = cmds.xform(thirdObj, q=True, ws=True, rp=True)

    vectorA = utility.vectorAdd(xformFirstObj, xformSecondObj, False)
    vectorB = utility.vectorAdd(xformThirdObj, xformSecondObj, False)
    return utility.vectorCross(vectorA, vectorB)


def _freezeJointOrientation(jointToOrient):
    cmds.joint(jointToOrient, e=True, zeroScaleOrient=True)
    cmds.makeIdentity(jointToOrient, apply=True, t=0, r=1, s=0, n=0)


def rotateOrder(jointsToOrient, aimAxis, upAxis):
    rotate_order = ''
    if upAxis == [1, 0, 0]:
        if aimAxis == [0, 1, 0]:
            rotate_order = 'yzx'
        else:
            rotate_order = 'zyx'

    elif upAxis == [0, 1, 0]:
        if aimAxis == [1, 0, 0]:
            rotate_order = 'xzy'
        else:
            rotate_order = 'zxy'

    else:
        if aimAxis == [1, 0, 0]:
            rotate_order = 'xyz'
        else:
            rotate_order = 'yxz'

    cmds.xform(jointsToOrient, p=1, rotateOrder=rotate_order)

def mirrorJoint(mirrorMode, mirrorPlane, aimAxis, upAxis, replace):
    if mirrorMode == 1:
        cmds.select(hi=True)
        uOrigin = cmds.ls(sl=1, uid=1)
        # print(uOrigin)
        origin = cmds.ls(uOrigin[0], l=1)[0]
        cmds.select(origin)
        mirrored = _mirrorJoint(mirrorPlane, True, replace)
        # print(mirrored)

        for inx, jnt in enumerate(mirrored):
            origin = cmds.ls(uOrigin[inx], l=1)[0]
            # print(origin)
            objUp = utility.getVector(origin, upAxis)
            if mirrorPlane == 1:
                objUp[0] = -objUp[0]
                objUp[1] = -objUp[1]
            elif mirrorPlane == 2:
                objUp[1] = -objUp[1]
                objUp[2] = -objUp[2]
            elif mirrorPlane == 3:
                objUp[0] = -objUp[0]
                objUp[2] = -objUp[2]

            print(objUp)
            orientJoint([jnt], aimAxis, upAxis, objUp, False)

    elif mirrorMode == 2:
        _mirrorJoint(mirrorPlane, True, replace)
    elif mirrorMode == 3:
        _mirrorJoint(mirrorPlane, False, replace)

def _mirrorJoint(mirrorPlane, behavior, replace):
    if mirrorPlane == 1:
        return cmds.mirrorJoint(mirrorXY=1, mirrorBehavior=behavior, searchReplace=replace)
    elif mirrorPlane == 2:
        return cmds.mirrorJoint(mirrorYZ=1, mirrorBehavior=behavior, searchReplace=replace)
    elif mirrorPlane == 3:
        return cmds.mirrorJoint(mirrorXZ=1, mirrorBehavior=behavior, searchReplace=replace)
