import maya.cmds as cmds
import maya.OpenMaya as om
from functools import partial
import os
'''====================================================================================================================

SIGNATURE:
    extractToWorld(objs, relatedObjs, reparent):

DESCRIPTION:
    unparent target object to the world
 
REQUIRES:


RETURNS:
    Nothing

===================================================================================================================='''
def getPrt(obj,type=''):
    if type:
        prt = cmds.listRelatives(obj, p=1, type=type, pa=1)
    else:
        prt = cmds.listRelatives(obj, p=1, pa=1)
    if prt:
        return prt[0]
    else:
        return None
def getShapes(obj):
    shapes = cmds.listRelatives(obj, s=1, pa=1)
    if shapes:
        return shapes
    else:
        return None
def getChl(obj,type=''):
    if type:
        children = cmds.listRelatives(obj, c=1, type=type, pa=1)
    else:
        children = cmds.listRelatives(obj, c=1, pa=1)
    if children:
        return children
    else:
        return None
    
def unParentToWorld(objs, withChild=False, parentChild=True, save=False, disconnect=True, relatedObjs=[]):
    attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "t", "r", "s"]
    saveList = [{},{}]
    
    #-------------------------------------------------------------------------------
    # save the uid
    #-------------------------------------------------------------------------------
    if relatedObjs:
        uRelatedObjs = cmds.ls(relatedObjs, uid=1)
    uObjs = cmds.ls(objs, uid=1)

    #-------------------------------------------------------------------------------
    # clear connection before unparent
    #-------------------------------------------------------------------------------
    if save:
        for obj in objs:
            locked_attrs = []
            for attr in attrs:
                attr_name = "%s.%s"%(obj, attr)
        
                #unlock locked transformtions
                if cmds.getAttr(attr_name, l=1):
                    locked_attrs.append(attr)
                    cmds.setAttr(attr_name, l=0)
            
                #delete transformtions'key
                cmds.cutKey(attr_name, cl=1, t=(), f=())

                if disconnect:
                    #disconnect transformtions
                    connect_s = cmds.listConnections(attr_name, d=0, s=1, p=1)
                    if connect_s:
                        connect_s = connect_s[0]
                        cmds.disconnectAttr(connect_s, attr_name)
                
            if locked_attrs:
                saveList[1].update({cmds.ls(item, uid=1)[0]:locked_attrs})
        
            #unlimit transformtions
            cmds.transformLimits(
                obj, 
                etx=(0, 0), ety=(0, 0), etz=(0, 0), 
                erx=(0, 0), ery=(0, 0), erz=(0, 0), 
                esx=(0, 0), esy=(0, 0), esz=(0, 0)
            )

            items = [obj]
            if not withChild:
                children = getChl(obj, type='transform')
                if children: items.extend(children)

            for item in items: 
                prt = getPrt(item)
                if prt:
                    saveList[0].update({cmds.ls(item, uid=1)[0]:cmds.ls(prt, uid=1)[0]})
    
    #-------------------------------------------------------------------------------
    # parent chrldren to the world or to origin parent
    #-------------------------------------------------------------------------------
    if not withChild:
        for obj in objs:
            prt = getPrt(obj)
            children = getChl(obj, type='transform')
            if children:
                for child in children:
                    if prt and parentChild:
                        cmds.parent(child, prt)
                    else:
                        cmds.parent(child, w=1)

    #update name
    objs = cmds.ls(uObjs, l=1)

    #-------------------------------------------------------------------------------
    # unparent to the world
    #-------------------------------------------------------------------------------
    for obj in objs:
        prt = getPrt(obj)
        if prt:
            cmds.parent(obj, w=1)

    #load from uid
    objs = cmds.ls(uObjs, l=1)
    if save and relatedObjs:
        relatedObjs = cmds.ls(uRelatedObjs, l=1)
        return relatedObjs, saveList
    if not save and relatedObjs:
        relatedObjs = cmds.ls(uRelatedObjs, l=1)
        return relatedObjs
    if save and not relatedObjs:
        return objs, saveList
    else:
        return objs

def reparentToOrigin(saveList, relatedObjs=[]):
    if relatedObjs:
        uRelatedObjs = cmds.ls(relatedObjs, uid=1)

    #reparent
    parentList = saveList[0]
    obj_list = []
    for uObj, uPrt in parentList.items():
        obj = cmds.ls(uObj, l=1)
        prt = cmds.ls(uPrt, l=1)
        if obj and prt:
            obj = obj[0]
            prt = prt[0]
            grp = getPrt(obj)
            obj_list.append(obj)
            if grp:
                cmds.parent(grp, prt)
            else:
                cmds.parent(obj, prt)
    
    #relock
    lockList = saveList[1] 
        
    for uObj, attrs in lockList.items():
        obj = cmds.ls(uObj, l=1)
        if obj:
            for attr in attrs:
                cmds.setAttr("%s.%s"%(obj[0], attr), l=1)
    
    if relatedObjs:
        relatedObjs = cmds.ls(uRelatedObjs, l=1)
        return relatedObjs
    else:
        return obj_list


def vectorAdd(a,b,add=True):
    c = [0,0,0]

    if add:
        c[0] = a[0] + b[0]
        c[1] = a[1] + b[1]
        c[2] = a[2] + b[2]
    else:
        c[0] = a[0] - b[0]
        c[1] = a[1] - b[1]
        c[2] = a[2] - b[2]

    return c

def vectorCross(a,b):
    c = [0,0,0]
    
    c[0] = a[1]*b[2] - a[2]*b[1]
    c[1] = a[2]*b[0] - a[0]*b[2]
    c[2] = a[0]*b[1] - a[1]*b[0]

    return c

def vectorDot(a,b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vectorMult(a,b):
    c = [0,0,0]

    c[0] = a[0]*b
    c[1] = a[1]*b
    c[2] = a[2]*b

    return c

def vectorToRotate(obj, vector, aim=[1,0,0], up=[0,1,0], worldUp=[0,1,0]):
    grp = cmds.group(em=1)
    cmds.matchTransform(grp, obj)
    grp = cmds.parent(grp, obj)
    cmds.xform(grp, r=1, t=vector)
    grp = cmds.parent(grp, w=1)
    cmds.delete(
        cmds.aimConstraint(
            grp, obj, w=1, o=(0, 0, 0), 
            aim=aim, upVector=up, 
            worldUpVector=worldUp, 
            worldUpType="vector"
        )
    )
    cmds.delete(grp)

def getVector(obj, up=[0,1,0]):
    grp = cmds.group(em=1)
    #parent ctl to grp
    cmds.matchTransform(grp, obj)
    grp = cmds.parent(grp, obj)
    
    cmds.xform(grp, r=1, t=up)
    grpT = cmds.xform(grp, q=1, ws=1, t=1)
    objT = cmds.xform(obj, q=1, ws=1, t=1)
    cmds.delete(grp)
    return vectorAdd(grpT, objT, False)

def sRGBtoLinear(rgb):
    linear = (pow(rgb[0], 1/2.2),pow(rgb[1], 1/2.2),pow(rgb[2], 1/2.2))
    return linear

def LineartosRGB(linear):
    rgb = (pow(linear[0], 2.2),pow(linear[1], 2.2),pow(linear[2], 2.2))
    return rgb

def applyColor(objs,color,*args):
    shapes = getShapes(objs)
    for shape in shapes:
        cmds.setAttr("%s.overrideEnabled"%shape, 1)
        cmds.setAttr("%s.overrideRGBColors"%shape, 1)
        cmds.setAttr("%s.overrideColorR"%shape, color[0])
        cmds.setAttr("%s.overrideColorG"%shape, color[1])
        cmds.setAttr("%s.overrideColorB"%shape, color[2])

def lockHideObj(objs,attrs,*args):
    for obj in objs:
        for attr in attrs:
            attr_name = "%s.%s"%(obj, attr)
            #print(attr_name)
            cmds.setAttr(attr_name, l=1, cb=0, k=0)
        

def fixedObj(objs):
    f = partial(lockHideObj,objs,['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])
    f()

def getFileList(filePath, ext='',sort='name'):
    dir_list = os.listdir(filePath)
    
    if not dir_list:
        return []

    if ext:
        file_list = []
        for dir in dir_list:
            if os.path.splitext(dir)[1] == "."+ext:
                file_list.append(dir)
        dir_list = file_list

    if not dir_list:
        return []

    if sort == 'name':
        dir_list.sort()
    if sort == 'create':
        dir_list = sorted(dir_list,  key=lambda x: os.path.getctime(os.path.join(filePath, x)))
    if sort == 'modify':
        dir_list = sorted(dir_list,  key=lambda x: os.path.getmtime(os.path.join(filePath, x)))

    return dir_list

def getType(obj):
    type_ = cmds.objectType(obj)
    if type_ == 'transform':
        shape = getShapes(obj)[0]
        if shape: type_ = cmds.objectType(shape)
    return type_


def checkSelection(checklist, order=True, log=True):
    sl = cmds.ls(sl=1)
    info = 'Select '
    for i, item in enumerate(checklist):
        if item[1] == item[2] == 1 or item[0]=='any':
            type_name = item[0]
        else:
            type_name = item[0]+'s'

        if i != 0:
            info += 'than select '
        if item[1] == item[2]:
            info += "{} {}, ".format(item[1], type_name)
        elif item[2] == 0:
            info += "at least {} {}, ".format(item[1], type_name)
        else:
            info += "{}~{} {}, ".format(item[1], item[2], type_name)

    info = info[:-2]
    info += '.'

    if not sl:
        check = False

    check = True
    if order:
        count = 0
        for item in checklist:
            count += item[1]

        if len(sl) < count:
            check = False

        if not _checkSelection(sl, checklist): check = False
        if not _checkSelection(sl[::-1], checklist[::-1]): check = False
    else:
        sl_type_list = []
        for i in range(len(sl)):
            list_index = -1
            for j in range(len(sl_type_list)):
                if getType(sl[i]) == sl_type_list[j][0]: list_index = j
            
            if list_index < 0:
                sl_type_list.append([getType(sl[i]),1])
            else:
                sl_type_list[list_index][1] += 1
                
        if len(sl_type_list) != len(checklist):
            check = False
        for i in range(len(sl_type_list)):
            list_index = -1
            for j in range(len(sl_type_list)):
                if getType(sl[i]) == sl_type_list[j][0]: list_index = j
                
            if list_index <0 :
                check = False
            elif checklist[list_index][1] !=0 and sl_type_list[i][1] < checklist[list_index][1]:
                check = False
            elif checklist[list_index][2] !=0 and sl_type_list[i][1] > checklist[list_index][2]:
                check = False
    if check:
        return sl
    else:
        if log: om.MGlobal.displayError(info)
        return False
        

def _checkSelection(sl, checklist):
    check = True
    for i in range(len(sl)):
        i_check = True
        c_max = 0
        count = 0
        while True:
            count += checklist[c_max][1]
            if count>=i+1 or c_max+1 >= len(checklist):
                break
            else:
                c_max += 1
        
        c_min = 0
        count = 0
        while True: 
            count += checklist[c_min][2]
            if count>=i+1 or checklist[c_min][2]==0:
                break
            elif c_min+1 >= len(checklist):
                i_check = False
                break
            else:
                c_min += 1
        
        if not i_check:
            check = False

            continue
            
        i_check = False
        for type_ in checklist[c_min:c_max+1][0]:
            if type_ == getType(sl[i]) or type_=='any': i_check = True
         
        if not i_check:
            check = False
            
    return check

def detectConnect(objs):
    attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "t", "r", "s"]
    hasConnect = False
    for obj in objs:
        for attr in attrs:
            attr_name = "%s.%s"%(obj, attr)
            list = cmds.listConnections(attr_name)
            if list: hasConnect=True
    
    return hasConnect