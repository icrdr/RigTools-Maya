import maya.cmds as cmds
import maya.OpenMaya as om
import functions


import utility
reload(functions)
reload(utility)

curvesInfo = [
    {"shape": [{"points": [[-3.000110939173828e-16, -0.7836116248912245, -0.7836116248912246], [6.78573232311091e-17, -6.785732323110915e-17, -1.1081941875543877], [3.9597584073715224e-16, 0.7836116248912245, -0.7836116248912244], [4.921370811114603e-16, 1.1081941875543881, -5.74489823752483e-17], [3.000110939173828e-16, 0.7836116248912245, 0.7836116248912245], [-6.785732323110912e-17, 1.1100856969603227e-16, 1.1081941875543884], [-3.9597584073715224e-16, -0.7836116248912245, 0.7836116248912244], [-4.921370811114603e-16, -1.1081941875543881, 1.511240500779959e-16], [-3.000110939173828e-16, -0.7836116248912245, -0.7836116248912246], [6.78573232311091e-17, -6.785732323110915e-17, -1.1081941875543877], [3.9597584073715224e-16, 0.7836116248912245, -0.7836116248912244]], "knot": [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], "degree": 3}], "name": "nurbsCircle1", "icon": "nurbsCircle1.png"},
    {"shape": [{"points": [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]], "knot": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0], "degree": 1}], "name": "fusiform", "icon": "fusiform.png"},
    {"shape": [{"points": [[-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [-1.0, -1.0, 1.0], [1.0, -1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [-1.0, -1.0, 1.0], [1.0, -1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0]], "knot": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0], "degree": 1}], "name": "cube", "icon": "cube.png"},
    {"shape": [{"points": [[0.0, 1.0, 0.0], [0.0, 0.0, 0.0]], "knot": [0.0, 1.0], "degree": 1}], "name": "line", "icon": "line.png"},
]

def autoFKIK(jnt_start, jnt_end, panel):
    # -------------------------------------------------------------------------------
    # create ik joint match render joint
    # -------------------------------------------------------------------------------
    ik_jnt_list = []

    jnt_i = jnt_end
    render_jnt_list = []

    while True:
        print("start: " + jnt_i)
        render_jnt_list.append(jnt_i)
        name = jnt_i.split("|")[-1]

        ik_jnt_i = cmds.duplicate(jnt_i, n=name+"_ik", parentOnly=1)[0]
        ik_jnt_list.append(ik_jnt_i)

        if jnt_i == jnt_start:
            print("end loop")
            break
        else:
            prt = utility.getPrt(jnt_i)
            if prt:
                jnt_i = prt
                print("end: " + jnt_i)
            else:
                break

    # reparent
    for inx in range(len(ik_jnt_list)):
        if inx < len(ik_jnt_list)-1:
            ik_jnt_list[inx] = cmds.parent(ik_jnt_list[inx], ik_jnt_list[inx+1])[0]
        else:
            if utility.getPrt(ik_jnt_list[inx]):
                ik_jnt_list[inx] = cmds.parent(ik_jnt_list[inx], w=1)[0]

    name = jnt_start.split("|")[-1]
    ikHandle = cmds.ikHandle(name=name+"_ikHandle",sj=ik_jnt_list[-1], ee=ik_jnt_list[0])[0]

    # -------------------------------------------------------------------------------
    # create ik ctls
    # -------------------------------------------------------------------------------
    
    radius1 = cmds.joint(jnt_end, q=1, radius=1)[0]
    
    ik_ctl = functions.createCurves(curvesInfo[2]['shape'], (0.26, 0.84, 1.0), name=name+"_ik_ctl")
    
    cmds.bakePartialHistory(ik_ctl, pc=1)
    cmds.matchTransform(ik_ctl, ikHandle)

    cmds.xform(ik_ctl, s=[radius1*3, radius1*3, radius1*3])
    functions.groupIt([ik_ctl])

    # Constraint
    cmds.select(ik_ctl)
    cmds.select(ikHandle, add=1)

    ik_constraint = cmds.parentConstraint(mo=1)[0]

    cmds.select(ik_ctl)
    cmds.select(ik_jnt_list[0], add=1)
    cmds.orientConstraint(mo=1)

    # -------------------------------------------------------------------------------
    # create pole ctls
    # -------------------------------------------------------------------------------
    ik_pole = functions.createCurves(curvesInfo[1]['shape'], (1.0, 0.1, 0.21), name=name+"_ik_pole")
    #cmds.bakePartialHistory(ik_pole, pc=1)

    middle_jnt = render_jnt_list[len(render_jnt_list)//2]
    radius2 = cmds.joint(middle_jnt, q=1, radius=1)[0]

    cmds.matchTransform(ik_pole, middle_jnt, pos=1)

    pole_vector = cmds.getAttr(ikHandle+'.poleVector')[0]
    pole_vector = utility.vectorMult(pole_vector, radius2*4)

    cmds.xform(ik_pole, r=1, ws=1, t=pole_vector)
    cmds.xform(ik_pole, s=[radius2, radius2, radius2])
    
    functions.groupIt([ik_pole])

    cmds.select(ik_pole)
    cmds.select(ikHandle, add=1)

    pole_constraint = cmds.poleVectorConstraint()[0]

    pole_help = functions.createCurves(curvesInfo[3]['shape'], (0.3, 0.3, 0.3), name=name+"_pole_help")
    shapes = utility.getShapes(pole_help)
    for shape in shapes:
        cmds.setAttr(shape+'.overrideDisplayType', 1)
    

    cmds.select(pole_help+'.cv[0]')
    pole_c1 = cmds.cluster(name=name+"_pole_c1")[1]

    cmds.select(pole_help+'.cv[1]')
    pole_c2 = cmds.cluster(name=name+"_pole_c2")[1]

    cmds.select(middle_jnt)
    cmds.select(pole_c1,add=1)
    cmds.pointConstraint(mo=0)

    cmds.select(ik_pole)
    cmds.select(pole_c2,add=1)
    cmds.pointConstraint(mo=0)
    # -------------------------------------------------------------------------------
    # create fk ctls
    # -------------------------------------------------------------------------------
    fk_ctl_list = []

    for inx in range(len(render_jnt_list)):
        name = render_jnt_list[inx].split("|")[-1]
        radius = cmds.joint(render_jnt_list[inx], q=1, radius=1)[0]

        fk_ctl = functions.createCurves(curvesInfo[0]['shape'], (1, 0.8, 0.0), name=name+"_fk_ctl")
        
        cmds.bakePartialHistory(fk_ctl, pc=1)
        fk_ctl_list.append(fk_ctl)
        cmds.matchTransform(fk_ctl, render_jnt_list[inx])
        print(radius)
        cmds.xform(fk_ctl, s=[radius*4, radius*4, radius*4])
        cmds.xform(fk_ctl, p=1, rotateOrder='xzy')

    for inx in range(len(fk_ctl_list)-1):
        fk_ctl_list[inx] = cmds.parent(fk_ctl_list[inx], fk_ctl_list[inx+1])[0]
    print(fk_ctl_list)
    functions.groupIt(fk_ctl_list)

    constraint_list = []

    for inx in range(len(render_jnt_list)):

        cmds.select(ik_jnt_list[inx])
        cmds.select(fk_ctl_list[inx], add=1)
        cmds.select(render_jnt_list[inx], add=1)

        constraint = cmds.parentConstraint(mo=1)[0]
        constraint_list.append(constraint)

    print("render jnt: ")
    print(render_jnt_list)
    print("ik jnt: ")
    print(ik_jnt_list)
    print("fk ctl: ")
    print(fk_ctl_list)
    print("constraints: ")
    print(constraint_list)

    # -------------------------------------------------------------------------------
    # connecting node
    # -------------------------------------------------------------------------------
    attr_name = name+'_FKIK'
    attr_full_name = panel + '.' + attr_name

    # check if it already has 'fkik'
    if cmds.attributeQuery(attr_name, node=panel, ex=1):
        cmds.addAttr(attr_full_name, k=1, e=1, ln=attr_name,
                     at="float", max=1.0, min=0.0)
    else:
        cmds.addAttr(panel, k=1, ln=attr_name, at="float", max=1.0, min=0.0)

    # set to 0
    cmds.setAttr(attr_full_name, 0)

    # clear old one
    range_node = cmds.listConnections(attr_full_name, d=1, s=0)

    if not range_node:
        range_node = cmds.shadingNode("setRange", au=1)
        cmds.connectAttr(attr_full_name, "%s.valueX" % range_node, f=1)
        cmds.connectAttr(attr_full_name, "%s.valueY" % range_node, f=1)
        cmds.setAttr("%s.oldMaxX" % range_node, 1.0)
        cmds.setAttr("%s.oldMaxY" % range_node, 1.0)
        cmds.setAttr("%s.maxX" % range_node, 1.0)
        cmds.setAttr("%s.minY" % range_node, 1.0)
    else:
        range_node = range_node[0]

    print(range_node)

    # connect node
    for inx, constraint in enumerate(constraint_list):

        ik_weight_name = constraint+"."+ik_jnt_list[inx]+"W0"
        fk_weight_name = constraint+"."+fk_ctl_list[inx]+"W1"
        fk_ctl_vis_name = fk_ctl_list[inx]+".visibility"

        cmds.connectAttr("%s.outValueX" % range_node, ik_weight_name, f=1)
        cmds.connectAttr("%s.outValueY" % range_node, fk_weight_name, f=1)
        cmds.connectAttr("%s.outValueY" % range_node, fk_ctl_vis_name, f=1)
    
    cmds.connectAttr("%s.outValueX" % range_node, ik_ctl+".visibility", f=1)
    cmds.connectAttr("%s.outValueX" % range_node, ik_pole+".visibility", f=1)
    cmds.connectAttr("%s.outValueX" % range_node, pole_help+".visibility", f=1)
    
    divide_node = cmds.shadingNode("multiplyDivide", au=1)
    clamp_node = cmds.shadingNode("clamp", au=1)

    distanceD = cmds.distanceDimension( sp=(0, 2, 2), ep=(1, 5, 6) )
    [loc1,loc2] = cmds.listConnections(distanceD, d=0, s=1)

    #cmds.matchTransform(loc1,ik_ctl)
    #loc1 = cmds.parent(loc1,ik_ctl)[0]
    #cmds.matchTransform(loc2,render_jnt_list[-1])
    #loc2 = cmds.parent(loc2,render_jnt_list[-1])[0]

    cmds.select(ik_ctl)
    cmds.select(loc1,add=1)
    cmds.pointConstraint(mo=0)

    cmds.select(ik_jnt_list[-1])
    cmds.select(loc2,add=1)
    cmds.pointConstraint(mo=0)
    

    originL = 0
    for inx in range(len(ik_jnt_list)-1):
        originL += cmds.getAttr("%s.translateX" % ik_jnt_list[inx])
    print(originL)

    cmds.setAttr("%s.operation" % divide_node, 2)
    cmds.setAttr("%s.input2X" % divide_node, originL)
    cmds.setAttr("%s.minR" % clamp_node, 1.0)
    cmds.setAttr("%s.maxR" % clamp_node, 10.0)
    cmds.connectAttr("%s.distance" % distanceD, "%s.input1X" % divide_node, f=1)
    cmds.connectAttr("%s.outputX" % divide_node, "%s.inputR" % clamp_node, f=1)

    for inx in range(len(ik_jnt_list)):
        cmds.connectAttr("%s.outputR" % clamp_node, "%s.scaleX" % ik_jnt_list[inx], f=1)


    misc_grp = cmds.ls("DoNotTouch")
    if not misc_grp:
        misc_grp = cmds.group(name="DoNotTouch",em=1)

    hide_list=[ikHandle,pole_c1,pole_c2,ik_jnt_list[-1],loc1,loc2,utility.getPrt(distanceD)]
    misc_list=[ikHandle,pole_help,pole_c1,ik_jnt_list[-1],pole_c2,loc1,loc2,utility.getPrt(distanceD)]
    
    for obj in hide_list:
        cmds.hide(obj)

    for obj in misc_list:
        cmds.parent(obj,misc_grp)
    
    utility.lockHideObj(fk_ctl_list,['tx','ty','tz','sx','sy','sz','v'])
    utility.lockHideObj([ik_pole],['rx','ry','rz','sx','sy','sz','v'])
    utility.lockHideObj([ik_ctl],['sx','sy','sz','v'])
    
    prt = utility.getPrt(jnt_start)
    if prt:
        cmds.select(prt)
        cmds.select(ik_jnt_list[-1], add=1)
        cmds.parentConstraint(mo=1)
    


def autoSplineFKIK(jnt_start, jnt_end, panel):
    ik_jnt_list = []

    jnt_i = jnt_end
    render_jnt_list = []

    while True:
        print("start: " + jnt_i)
        render_jnt_list.append(jnt_i)
        name = jnt_i.split("|")[-1]

        ik_jnt_i = cmds.duplicate(jnt_i, n=name+"_ik", parentOnly=1)[0]
        ik_jnt_list.append(ik_jnt_i)

        if jnt_i == jnt_start:
            print("end loop")
            break
        else:
            prt = utility.getPrt(jnt_i)
            if prt:
                jnt_i = prt
                print("end: " + jnt_i)
            else:
                break

    # reparent
    for inx in range(len(ik_jnt_list)):
        if inx < len(ik_jnt_list)-1:
            ik_jnt_list[inx] = cmds.parent(ik_jnt_list[inx], ik_jnt_list[inx+1])[0]
        else:
            if utility.getPrt(ik_jnt_list[inx]):
                ik_jnt_list[inx] = cmds.parent(ik_jnt_list[inx], w=1)[0]

    # -------------------------------------------------------------------------------
    # create splineIK
    # -------------------------------------------------------------------------------
    name = jnt_start.split("|")[-1]
    [spline_ikHandle,effector,spline_crv] = cmds.ikHandle(name=name+"_spline_ikHandle",sj=ik_jnt_list[-1], ee=ik_jnt_list[0], solver='ikSplineSolver')

    spline_crv = cmds.rename(spline_crv, name+'_spline_crv')

    # -------------------------------------------------------------------------------
    # create cluster jnt
    # -------------------------------------------------------------------------------
    CTL_COUNT = 3
    pr = 0.0
    cluster_jnt_list = []
    ik_ctl_list = []
    fk_ctl_list = []
    radius = cmds.joint(render_jnt_list[0], q=1, radius=1)[0]
    for i in range(CTL_COUNT):
        
        pos = cmds.pointOnCurve( spline_crv, pr=pr, p=1, top=1)
        tangent = cmds.pointOnCurve(spline_crv, pr=pr, t=1, top=1)
        
        pr = pr+1.0/(CTL_COUNT-1)

        cmds.select(cl=1)
        c_jnt = cmds.joint(name=name+"_c"+str(i)+"_jnt",p=pos)
        cluster_jnt_list.append(c_jnt)

        ik_ctl = functions.createCurves(curvesInfo[2]['shape'], (0.26, 0.84, 1.0), name=name+"_c"+str(i)+"_ik_ctl")
        ik_ctl_list.append(ik_ctl)
        cmds.xform(ik_ctl, t=pos, s=[radius*3,radius*3,radius*3])
        fk_ctl = functions.createCurves(curvesInfo[0]['shape'], (1, 0.8, 0.0), name=name+"_c"+str(i)+"_fk_ctl")
        fk_ctl_list.append(fk_ctl)
        WorldUpVector = utility.getVector(jnt_start)
        utility.vectorToRotate(fk_ctl, tangent, worldUp = WorldUpVector)
        cmds.xform(fk_ctl, t=pos, s=[radius*4,radius*4,radius*4])
        cmds.xform(fk_ctl, p=1, rotateOrder='xzy')
        
        print(tangent)
        print(pos)
    
    cluster_jnt_list = cluster_jnt_list[::-1]
    ik_ctl_list = ik_ctl_list[::-1]
    fk_ctl_list = fk_ctl_list[::-1]
    for inx in range(len(fk_ctl_list)-1):
        cmds.parent(fk_ctl_list[inx], fk_ctl_list[inx+1])
    
    functions.groupIt(ik_ctl_list)
    functions.groupIt(fk_ctl_list)

    # -------------------------------------------------------------------------------
    # constraint ik fk
    # -------------------------------------------------------------------------------
    constraint_list = []
    for inx in range(len(cluster_jnt_list)):

        cmds.select(ik_ctl_list[inx])
        cmds.select(fk_ctl_list[inx], add=1)
        cmds.select(cluster_jnt_list[inx], add=1)

        constraint = cmds.parentConstraint(mo=1)[0]
        constraint_list.append(constraint)
    
    WorldUpVector = utility.getVector(jnt_start)
    WorldUpVectorEnd = utility.getVector(jnt_end)

    cmds.setAttr("%s.dTwistControlEnable" % spline_ikHandle,True)
    cmds.setAttr("%s.dWorldUpType" % spline_ikHandle,4)
    cmds.setAttr("%s.dWorldUpVectorX" % spline_ikHandle, WorldUpVector[0])
    cmds.setAttr("%s.dWorldUpVectorY" % spline_ikHandle, WorldUpVector[1])
    cmds.setAttr("%s.dWorldUpVectorZ" % spline_ikHandle, WorldUpVector[2])
    cmds.setAttr("%s.dWorldUpVectorEndX" % spline_ikHandle, WorldUpVectorEnd[0])
    cmds.setAttr("%s.dWorldUpVectorEndY" % spline_ikHandle, WorldUpVectorEnd[1])
    cmds.setAttr("%s.dWorldUpVectorEndZ" % spline_ikHandle, WorldUpVectorEnd[2])
 
    cmds.connectAttr("%s.worldMatrix[0]" % cluster_jnt_list[-1], "%s.dWorldUpMatrix" % spline_ikHandle, f=1)
    cmds.connectAttr("%s.worldMatrix[0]" % cluster_jnt_list[0], "%s.dWorldUpMatrixEnd" % spline_ikHandle, f=1)


    # -------------------------------------------------------------------------------
    # connecting node
    # -------------------------------------------------------------------------------
    attr_name = name+'_FKIK'
    attr_full_name = panel + '.' + attr_name

    # check if it already has 'fkik'
    if cmds.attributeQuery(attr_name, node=panel, ex=1):
        cmds.addAttr(attr_full_name, k=1, e=1, ln=attr_name,
                     at="float", max=1.0, min=0.0)
    else:
        cmds.addAttr(panel, k=1, ln=attr_name, at="float", max=1.0, min=0.0)

    # set to 0
    cmds.setAttr(attr_full_name, 0)
    
    # clear old one
    range_node = cmds.listConnections(attr_full_name, d=1, s=0)

    if not range_node:
        range_node = cmds.shadingNode("setRange", au=1)
        cmds.connectAttr(attr_full_name, "%s.valueX" % range_node, f=1)
        cmds.connectAttr(attr_full_name, "%s.valueY" % range_node, f=1)
        cmds.setAttr("%s.oldMaxX" % range_node, 1.0)
        cmds.setAttr("%s.oldMaxY" % range_node, 1.0)
        cmds.setAttr("%s.maxX" % range_node, 1.0)
        cmds.setAttr("%s.minY" % range_node, 1.0)
    else:
        range_node = range_node[0]

    print(range_node)

    # connect node
    for inx, constraint in enumerate(constraint_list):

        ik_weight_name = constraint+"."+ik_ctl_list[inx]+"W0"
        fk_weight_name = constraint+"."+fk_ctl_list[inx]+"W1"
        ik_ctl_vis_name = ik_ctl_list[inx]+".visibility"
        fk_ctl_vis_name = fk_ctl_list[inx]+".visibility"

        cmds.connectAttr("%s.outValueX" % range_node, ik_weight_name, f=1)
        cmds.connectAttr("%s.outValueX" % range_node, ik_ctl_vis_name, f=1)
        cmds.connectAttr("%s.outValueY" % range_node, fk_weight_name, f=1)
        cmds.connectAttr("%s.outValueY" % range_node, fk_ctl_vis_name, f=1)

    crvInfo_node = cmds.shadingNode("curveInfo", au=1)
    divide_node = cmds.shadingNode("multiplyDivide", au=1)
    spline_crvShape = utility.getShapes(spline_crv)[0]
    cmds.connectAttr("%s.worldSpace[0]" % spline_crvShape, "%s.inputCurve" % crvInfo_node, f=1)

    originL = cmds.getAttr("%s.arcLength" % crvInfo_node)
    print(originL)

    cmds.setAttr("%s.operation" % divide_node, 2)
    cmds.setAttr("%s.input2X" % divide_node, originL)
    cmds.connectAttr("%s.arcLength" % crvInfo_node, "%s.input1X" % divide_node, f=1)

    for inx in range(len(ik_jnt_list)):
        cmds.connectAttr("%s.outputX" % divide_node, "%s.scaleX" % ik_jnt_list[inx], f=1)

    cmds.select(spline_crv)
    cmds.select(cluster_jnt_list,add=1)
    cmds.skinCluster(dr=1.0,maximumInfluences=2)
    
    for inx in range(len(ik_jnt_list)):
        cmds.select(ik_jnt_list[inx])
        cmds.select(render_jnt_list[inx],add=1)
        cmds.parentConstraint(mo=0)

    misc_grp = cmds.ls("DoNotTouch")
    if not misc_grp:
        misc_grp = cmds.group(name="DoNotTouch",em=1)

    hide_list=[spline_ikHandle,spline_crv,ik_jnt_list[-1]]
    hide_list.extend(cluster_jnt_list)    
    misc_list=[spline_ikHandle,spline_crv,ik_jnt_list[-1]]
    misc_list.extend(cluster_jnt_list)

    for obj in hide_list:
        cmds.hide(obj)

    for obj in misc_list:
        cmds.parent(obj,misc_grp)

    utility.lockHideObj(fk_ctl_list,['sx','sy','sz','v'])
    utility.lockHideObj(ik_ctl_list,['sx','sy','sz','v'])

    prt = utility.getPrt(jnt_start)
    if prt:
        cmds.select(prt)
        cmds.select(ik_jnt_list[-1], add=1)
        cmds.parentConstraint(mo=1)
    