import maya.cmds as cmds
import maya.OpenMaya as om
from functools import partial

def _mergeCurves(curves):                 
    for curve in curves:
        cmds.makeIdentity(curve, a=1)
        cmds.bakePartialHistory(curve, pc=1)
        
    #set newTransform as first in selection
    groupTransform = curves[0]
    
    #get groupTransform
    grp = cmds.group(em=1)
    #cmds.matchTransform(grp, groupTransform)
    groupTransform = grp
    
    for curve in curves: 
        #make sure curveShapes don't move
        cmds.makeIdentity(curve, a=1)  
    
        #merge to groupTransform
        curveShapes = cmds.listRelatives(curve, s=1, f=1)
        for curveShape in curveShapes:           
            cmds.parent(curveShape, groupTransform, r=1, s=1)
        
        #delect rest
        cmds.delete(curve)
    
    #connect Drawing Overrides
    curveShapes = cmds.listRelatives(groupTransform, s=1, f=1)
    for curveShape in curveShapes:
        if curveShape != curveShapes[0]:
            cmds.connectAttr("%s.drawOverride"%curveShapes[0], "%s.drawOverride"%curveShape, f=1)
        
    #center pivot and clear history
    cmds.xform(groupTransform, cp=1)
    cmds.bakePartialHistory(groupTransform, pc=1)
    cmds.select(groupTransform)
    

def _unparentAndStore(obj,saveList):
    attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "t", "r", "s"]
    
    #children is involed too
    hierarchy = [obj]
    children = cmds.listRelatives(obj, c=1, f=1, typ='transform')
    if children: hierarchy.extend(children)
    
    #print(obj + "'s item list need to be clear:")
    #print(hierarchy)
    
    #clear connection before unparent
    for item in hierarchy: 
        locked_attrs = []
        
        for attr in attrs:
            attr_name = "%s.%s"%(item, attr)
            
            #unlock locked transformtions
            if cmds.getAttr(attr_name, l=1):
                locked_attrs.append(attr)
                cmds.setAttr(attr_name, l=0)
                
            #delete transformtions'key
            cmds.cutKey(attr_name, cl=1, t=(), f=())
            
            #disconnect transformtions
            connect_s = cmds.listConnections(attr_name, d=0, s=1, p=1)
            if connect_s:
                connect_s = connect_s[0]
                cmds.disconnectAttr(connect_s, attr_name)
                
        if locked_attrs:
            saveList[1].update({cmds.ls(item, uid=1)[0]:locked_attrs})
            
        #unlimit transformtions
        cmds.transformLimits(item, etx=(0, 0), ety=(0, 0), etz=(0, 0), erx=(0, 0), ery=(0, 0), erz=(0, 0), esx=(0, 0), esy=(0, 0), esz=(0, 0))
        
    #if it has parent unparent it
    uObj = cmds.ls(obj, uid=1)[0]
    prt = cmds.listRelatives(obj, p=1, f=1)
    if prt:
        uPrt = cmds.ls(prt, uid=1)[0]
        saveList[0].update({uObj:uPrt})
        cmds.parent(obj, w=1)
            
    #if it has children unparent them
    obj = cmds.ls(uObj, l=1)[0]
    children = cmds.listRelatives(obj, c=1, f=1, typ='transform')
    if children:
        for child in children:
            uChild = cmds.ls(child, uid=1)[0]
            saveList[0].update({uChild:uObj})
            cmds.parent(child, w=1)
            
    return saveList

def _reparentFormStore(saveList):
    #reparent
    parentList = saveList[0]
    
    for uObj, uPrt in parentList.items():
        obj = cmds.ls(uObj, l=1)[0]
        prt = cmds.ls(uPrt, l=1)[0]
        grp = cmds.listRelatives(obj, p=1, f=1)
        
        if grp:
            cmds.parent(grp[0], prt)
        else:
            cmds.parent(obj, prt)
    
    #relock
    lockList = saveList[1] 
        
    for uObj, attrs in lockList.items():
        obj = cmds.ls(uObj, l=1)[0]
        for attr in attrs:
            cmds.setAttr("%s.%s"%(obj, attr), l=1)    

def _spaceSwitchSetup(objs):
    target = cmds.ls(sl=1, tl=1)[0]  
    print("target is: '%s'"%target)
     
    target_grp = cmds.listRelatives(target, p=1, f=1)
        
    target_grp = target_grp[0]
    constraint_list=[]
        
    #check if it has parent: add it first
    target_grp_prt = cmds.listRelatives(target_grp, p=1, f=1)
    if target_grp_prt:
        constraint_list.append(target_grp_prt[0])
    
    for obj in objs:
        if obj == target: 
            continue 
        constraint_list.append(obj)
        
    constraint_list.append(target_grp)
    print(constraint_list)
    
    cmds.select(cl=1)
    for obj in constraint_list:
        cmds.select(obj, add=1)
     
    constraint = cmds.parentConstraint(mo=1)[0]
    
    #create the enum attr
    enumName = ""
    
    if target_grp_prt:
        enumName = ":Parent"
        
    for obj in objs:
        if obj == target: 
            continue 
        enumName = enumName + ":" + obj.split(":")[-1].split("|")[-1]
    enumName = enumName[1:]
    
    print("enumName is: '%s'"%enumName)    
    if cmds.attributeQuery('follow', node=target, ex=1):
        cmds.addAttr("%s.follow"%target, k=1, e=1, ln="follow", at="enum", en=enumName )
    else:
        cmds.addAttr(target, k=1, ln="follow", at="enum", en=enumName )
    
    #connect node
    constraint_list = constraint_list[:-1]
    for inx, obj in enumerate(constraint_list):
        condition_node = cmds.shadingNode("condition", au=1);
        print(condition_node)
        cmds.connectAttr("%s.follow"%target, "%s.firstTerm"%condition_node, f=1)
        
        weight_name = "%s.%sW%d"%(constraint,obj.split(":")[-1].split("|")[-1],inx)
        print("weight name is: '%s'"%weight_name)
        
        cmds.connectAttr("%s.outColorR"%condition_node, weight_name, f=1)
        cmds.setAttr("%s.secondTerm"%condition_node, inx)
        cmds.setAttr("%s.operation"%condition_node, 1)

def _renameWindow(obj):
    if cmds.window('Renamer', ex=1):
        cmds.deleteUI('Renamer')
    obj = obj[0]
    print(obj)
    
    renamer = cmds.window('Renamer', t="Rename it and it's group", wh=(180, 80), s=0)
    
    cmds.columnLayout(adjustableColumn=True)
    cmds.textFieldGrp("Input", h=40, cw2=[0,180], w=10, l='input', pht="new name")
    cmds.button("Sure", h=40, w=180, l='Sure', c=partial(_renameIt, obj, renamer))
    cmds.showWindow(renamer)

def _renameIt(obj,win,*args):
    name_str = cmds.textFieldGrp("Input", q=1, tx=1)
    
    if name_str != "":    
        prt = cmds.listRelatives(obj, p=1, f=1)[0]  
          
        cmds.rename(obj, name_str)
        cmds.rename(prt, name_str+"_grp")
        cmds.deleteUI(win)  
        om.MGlobal.displayInfo("It works!") 
    else:
        om.MGlobal.displayError("Input anything, allright?")
    
def _groupIt(ctls):
    PARENT_LIST = {}
    LOOK_LIST = {}
    SAVE_LIST = [PARENT_LIST,LOOK_LIST]
    
    #get the UID of controllers
    uCtls = cmds.ls(ctls,uid=1)
    
    for uCtl in uCtls:
        """
        #delete _CTL to avoid over adding '_CTL'
        ctl = cmds.ls(uCtl, l=1)[0]
        ctl_name = cmds.ls(uCtl, o=1)[0].split("|")[-1].replace('_ctl', "")
        cmds.rename(ctl, ctl_name)
        """
    
        ctl = cmds.ls(uCtl, l=1)[0]
        #clear attrs'connection of all children before the operation.
        SAVE_LIST = _unparentAndStore(ctl, SAVE_LIST)  

    #print("parentList:")
    #print(SAVE_LIST[0])
    #print("lockList:")
    #print(SAVE_LIST[1])
  
    for uCtl in uCtls:
        ctl = cmds.ls(uCtl, l=1)[0]

        #freeze sacle if necessary
        cmds.makeIdentity(ctl, a=1, s=1)

        #create group
        grp = cmds.group(em=1)
    
        #parent ctl to grp
        cmds.matchTransform(grp, ctl)

        cmds.parent(ctl, grp)
   
        ctl = cmds.ls(uCtl, l=1)[0]
        #freeze transform
        cmds.makeIdentity(ctl, a=1)
        
    #reparent the grp
    _reparentFormStore(SAVE_LIST)
    
    #rename all
    for uCtl in uCtls:
        ctl = cmds.ls(uCtl,l=1)[0]
        grp = cmds.listRelatives(ctl, p=1, f=1)[0]
        
        ctl_name = cmds.ls(uCtl, o=1)[0].split("|")[-1]
        
        """
        #add _ctl
        cmds.rename(ctl, ctl_name+"_ctl")
        ctl_name = cmds.ls(uCtl, o=1)[0].split("|")[-1]
        """
        
        cmds.rename(grp, ctl_name+"_grp")

    print("it works")

def mergeCurves():
    try:
        sl = _checkIfselected()
        
        for curveShape in cmds.listRelatives(sl, s=1, f=1):
            if not cmds.objectType(curveShape, i='nurbsCurve'):
                raise Exception,"Bad selection! They need to be unparented!" 
        
        for curve in sl:
            if cmds.listRelatives(curve, p=1, f=1):
               raise Exception,"Bad selection! They need to be unparented!" 
            elif cmds.listRelatives(curve, c=1, typ='transform', f=1):
               raise Exception,"They must not having children!" 

        _mergeCurves(sl)    
    except Exception, err:
        om.MGlobal.displayError(err)
    else:
        om.MGlobal.displayInfo("It works!")

def groupIt():
    try:
        sl = _checkIfselected()
        _groupIt(sl)    
    except Exception, err:
        om.MGlobal.displayError(err)
    else:
        om.MGlobal.displayInfo("It works!")

def spaceSwitchSetup():
    try:
        sl = _checkIfselected()

        if len(sl) < 2:
            raise Exception,"At least 2 items are selected!"
        
        elif not cmds.listRelatives(cmds.ls(sl=1, tl=1)[0], p=1, f=1):
            raise Exception,"Target needs a group! Please group it first."

        _spaceSwitchSetup(sl)
    except Exception, err:
        om.MGlobal.displayError(err)
    else:
        om.MGlobal.displayInfo("It works!")

def _getPosition(obj):
    grp = cmds.group(em=1,name="xLEAVEMEALONE")
    cmds.matchTransform(grp, obj)
    cmds.setAttr("xLEAVEMEALONE.tx", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.ty", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.tz", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.rx", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.ry", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.rz", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.sx", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.sy", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.sz", l=1, cb=0, k=0)
    cmds.setAttr("xLEAVEMEALONE.v", 0 , l=1, cb=0, k=0)

def _setPosition(obj):
    grp = cmds.ls("xLEAVEMEALONE")
    cmds.matchTransform(obj, grp)
    cmds.delete(grp)

def matchTransform(): 
    try:  
        sl = _checkIfselected()
        if len(sl) == 1:
            grp = cmds.ls("xLEAVEMEALONE")
            if grp:
                _setPosition(sl[0])
                cmds.select(sl[0])
            else:
                _getPosition(sl[0])
                cmds.select(sl[0])
        elif len(sl) == 2:
            _getPosition(sl[1])
            _setPosition(sl[0])
            cmds.select(sl[0])
        else:
            raise Exception,"1 or 2 items are needed!"
    except Exception, err:
        om.MGlobal.displayError(err)
    else:
        om.MGlobal.displayInfo("It works!")

def renameIt():
    try:
        sl = _checkIfselected()
        if len(sl) >1:
            raise Exception,"Only 1 item is need!"

        prt = cmds.listRelatives(sl, p=1, f=1)
        if not prt: 
            raise Exception,"It don't have group"
        elif cmds.listRelatives(prt[0], c=1, s=1, f=1):
            raise Exception,"It's parent is not a group"

        _renameWindow(sl)
    except Exception, err:
        om.MGlobal.displayError(err)
    else:
        om.MGlobal.displayInfo("Input name now")

def polyToCurve():
    cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=1) 
    cmds.bakePartialHistory(pc=1)

def polyToCurveS():
    cmds.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1)  
    cmds.bakePartialHistory(pc=1)

def _checkIfselected():
    sl = cmds.ls(sl=1)
    if not sl:
        raise Exception,"nothing is selected!"
    return sl