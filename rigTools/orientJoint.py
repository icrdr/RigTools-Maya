import maya.cmds as cmds
import maya.OpenMaya as om


def orientJointsWindow(* args):
	if cmds.window('OrientJointsWindow', ex=1):
		cmds.deleteUI('OrientJointsWindow')
		
	cmds.window("OrientJointsWindow", t=("Orient Joint More Options"), wh=(600, 300), s=0)
	form = cmds.formLayout()

	col = cmds.columnLayout(p=form, columnAttach=('both', 10), rowSpacing=0, columnWidth=600)

	row1 = cmds.rowLayout(p=col, numberOfColumns=1, columnWidth1=350, columnAttach=[(1, 'both', 0)])
	cmds.radioButtonGrp("rbgAim", l="Primary Axis: ", nrb=3, la3=("X","Y","Z"), sl=1, cw4=(190,50,50,50), changeCommand=_upChange, p=row1)

	row2 = cmds.rowLayout(p=col, numberOfColumns=2, columnWidth2=(350, 100), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
	cmds.radioButtonGrp("rbgUp", l="Secondary Axis: ", nrb=3, la3=("X","Y","Z"), sl=2, cw4=(190,50,50,50), changeCommand=_aimChange, p=row2)
	cmds.checkBox("chbReverseUp", l="Reverse",p=row2)
	
	row3 = cmds.rowLayout(p=col, numberOfColumns=2, columnWidth2=(350, 250), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
	cmds.floatFieldGrp("rbgWorldUp", l="Secondary Axis World Orientation: ", nf=3, v1=0.0, v2=1.0, v3=0.0, cw4=(190,50,50,50), pre=2, p=row3)
	cmds.button("btnSetWorldUp", l="Set from selected object", h=20, c=_setWorldUp, p=row3)

	cmds.separator("sep1", style="double", h=10, p=col)

	col1 = cmds.columnLayout(p=col, columnAttach=('left', 190), rowSpacing=0, columnWidth=580, adjustableColumn=True)
	cmds.checkBox("chbAllOrSelected", l="Orient children of selected joints", v=1, p=col1)				
	cmds.checkBox("chbGuess", l="Guess Up Direction", v=0, p=col1, offCommand=_enableWorldOrient, onCommand=_disableWorldOrient)

	cmds.separator("sep2", style="double", h=10, p=col)

	row3 = cmds.rowLayout(p=form, numberOfColumns=1, adjustableColumn=1, w=600, columnAttach=[(1, 'both', 10)] )
	cmds.button("btnOrientJoints", l="Orient Joints", h=30, c=_orientJointsUI, ann="Orient Joints", p=row3)

	cmds.formLayout(
		form, 
		edit=True, 
		attachForm=[
			(col, 'top', 10), 
			(row3, 'bottom', 10)
			],
	)
	cmds.showWindow("OrientJointsWindow")

# ====================================================================================================================
#
# SIGNATURE:
#	_orientJointsUI(* args)
#
# DESCRIPTION:
# 	Manage the options selected in the interface and 
# 	calls the actual orientJoint method.
# 
# REQUIRES:
# 	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def _orientJointsUI(* args):
	aimSelected = cmds.radioButtonGrp("rbgAim", q=True, sl=True)
	upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)

	upReverse = cmds.checkBox("chbReverseUp", q=True, v=True)

	worldUp = [0,0,0]
	worldUp[0] = cmds.floatFieldGrp("rbgWorldUp", q=True, v1=True)
	worldUp[1] = cmds.floatFieldGrp("rbgWorldUp", q=True, v2=True)
	worldUp[2] = cmds.floatFieldGrp("rbgWorldUp", q=True, v3=True)

	operateOn = cmds.checkBox("chbAllOrSelected", q=True, v=True)
	guessUp = cmds.checkBox("chbGuess", q=True, v=True)

	aimAxis = [0,0,0]
	upAxis = [0,0,0]

	aimAxis[aimSelected - 1] = 1

	if upReverse == 1:
		upAxis[upSelected - 1] = -1
	else:
		upAxis[upSelected - 1] = 1

	sl = cmds.ls(typ="joint", sl=1)
	
	try:
		if len(sl) < 1:
			raise Exception, "USAGE: Select at least one joint to orient."

		if operateOn == 1:
			#Hierarchy
			cmds.select(hi=True)
			jointsToOrient = cmds.ls(typ="joint", sl=1)
		else:
			#Selected
			jointsToOrient = cmds.ls(typ="joint", sl=1)
		
		cmds.undoInfo(ock=True)
		_doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp)
		cmds.select(sl, r=True)
		cmds.undoInfo(cck=True)

	except Exception, err:
		om.MGlobal.displayError(err)
	else:
		om.MGlobal.displayInfo("SUCCEED!")
		
# ====================================================================================================================
#
# SIGNATURE:
#	_doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp)
#
# DESCRIPTION:
# 	Does the actual joint orientation.
# 
# REQUIRES:
#	jointsToOrient - List of joints to orient.
# 	aimAxis - Aim axis for the joint orient.
# 	upAxis - Up axis for the joint orient.
# 	worldUp - World Up for the joint orient.
# 	guessUp - If selected will calculate the correct Up axis.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def _doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp):
	firstPass = 0
	prevUpVector = [0,0,0]
	for eachJoint in jointsToOrient:
		childJoint = cmds.listRelatives(eachJoint, type="joint", c=True) 
		if childJoint != None:
			if len(childJoint) > 0:

				childNewName = cmds.parent(childJoint, w=True)	#Store the name in case when unparented it changes it's name.

				if guessUp == 0:
					#Not guess Up direction
					
					cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=worldUp, worldUpType="vector"))
					_freezeJointOrientation(eachJoint)
					cmds.parent(childNewName, eachJoint)
				else:
					if guessUp == 1:
						#Guess Up direction
						

						parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True) 
						if parentJoint != None :
							if len(parentJoint) > 0:
								posCurrentJoint = cmds.xform(eachJoint, q=True, ws=True, rp=True)
								posParentJoint = cmds.xform(parentJoint, q=True, ws=True, rp=True)
								tolerance = 0.0001

								if (abs(posCurrentJoint[0] - posParentJoint[0]) <= tolerance and abs(posCurrentJoint[1] - posParentJoint[1]) <= tolerance and abs(posCurrentJoint[2] - posParentJoint[2]) <= tolerance):
									aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True) 
									upDirRecalculated = _crossProduct(eachJoint, childNewName[0], aimChild[0])
									cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
								else:
									upDirRecalculated = _crossProduct(parentJoint, eachJoint, childNewName[0])
									cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
							else:
								aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True) 
								upDirRecalculated = _crossProduct(eachJoint, childNewName[0], aimChild[0])
						else:
							aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True) 
							upDirRecalculated = _crossProduct(eachJoint, childNewName[0], aimChild[0])
							cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))

				



					dotProduct = upDirRecalculated[0] * prevUpVector[0] + upDirRecalculated[1] * prevUpVector[1] + upDirRecalculated[2] * prevUpVector[2]

					#For the next iteration
					prevUpVector = upDirRecalculated

					if firstPass > 0 and  dotProduct <= 0.0:
						#dotProduct
						cmds.xform(eachJoint, r=1, os=1, ra=(aimAxis[0] * 180.0, aimAxis[1] * 180.0, aimAxis[2] * 180.0))
						prevUpVector[0] *= -1
						prevUpVector[1] *= -1
						prevUpVector[2] *= -1
		
					_freezeJointOrientation(eachJoint)
					cmds.parent(childNewName, eachJoint)




			else:
				#Child joint. Use the same rotation as the parent.
				if len(childJoint) == 0:
					parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True) 
					if parentJoint != None :
						if len(parentJoint) > 0:
							cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint, w=1, o=(0,0,0)))
							_freezeJointOrientation(eachJoint)
		else:
			#Child joint. Use the same rotation as the parent.
			parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True) 
			if parentJoint != None :
				if len(parentJoint) > 0:
					cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint, w=1, o=(0,0,0)))
					_freezeJointOrientation(eachJoint)			

	

		firstPass += 1



# ====================================================================================================================
#
# SIGNATURE:
#	_crossProduct(firstObj, secondObj, thirdObj)
#
# DESCRIPTION:
# 	Calculates the dot product among 3 joints forming 2 vectors.
# 
# REQUIRES:
#	firstObj - First object to the Cross Product.
# 	secondObj - Second object to the Cross Product.
# 	thirdObj - Third object to the Cross Product.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def _crossProduct(firstObj, secondObj, thirdObj):
	#We have 3 points in space so we have to calculate the vectors from 
	#the secondObject (generally the middle joint and the one to orient)
	#to the firstObject and from the secondObject to the thirdObject.

	xformFirstObj = cmds.xform(firstObj, q=True, ws=True, rp=True)
	xformSecondObj = cmds.xform(secondObj, q=True, ws=True, rp=True)
	xformThirdObj = cmds.xform(thirdObj, q=True, ws=True, rp=True)

	#B->A so A-B.
	firstVector = [0,0,0]
	firstVector[0] = xformFirstObj[0] - xformSecondObj[0];
	firstVector[1] = xformFirstObj[1] - xformSecondObj[1];
	firstVector[2] = xformFirstObj[2] - xformSecondObj[2];

	#B->C so C-B.
	secondVector = [0,0,0]
	secondVector[0] = xformThirdObj[0] - xformSecondObj[0];
	secondVector[1] = xformThirdObj[1] - xformSecondObj[1];
	secondVector[2] = xformThirdObj[2] - xformSecondObj[2];

	#THE MORE YOU KNOW - 3D MATH
	#========================================
	#Cross Product u x v:
	#(u2v3-u3v2, u3v1-u1v3, u1v2-u2v1)
	crossProductResult = [0,0,0]
	crossProductResult[0] = firstVector[1]*secondVector[2] - firstVector[2]*secondVector[1]
	crossProductResult[1] = firstVector[2]*secondVector[0] - firstVector[0]*secondVector[2]
	crossProductResult[2] = firstVector[0]*secondVector[1] - firstVector[1]*secondVector[0]

	return crossProductResult

# ====================================================================================================================
#
# SIGNATURE:
#	_freezeJointOrientation(jointToOrient)
#
# DESCRIPTION:
# 	Freezes the joint orientation.
# 
# REQUIRES:
#	jointToOrient - Joint to orient.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def _freezeJointOrientation(jointToOrient):
	cmds.joint(jointToOrient, e=True, zeroScaleOrient=True)
	cmds.makeIdentity(jointToOrient, apply=True, t=0, r=1, s=0, n=0)

# ====================================================================================================================
#
# SIGNATURE:
#	worldUpX(* args)
#
# DESCRIPTION:
# 	Sets and 1.0 on the X world Up Field.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def _setWorldUp(* args):
	try:
		sl = cmds.ls(sl=1)

		if len(sl) < 1:
			raise Exception,"USAGE: Select one object."

		obj = sl[0]
		grp = cmds.group(em=1)
    
    	#parent ctl to grp
		cmds.matchTransform(grp, obj)
		cmds.parent(grp, obj)
		cmds.setAttr(grp+'.translateY', 1)

		grpT = cmds.xform(grp, q=1, ws=1, t=1)
		objT = cmds.xform(obj, q=1, ws=1, t=1)

		cmds.delete(grp)

		X = om.MVector(grpT[0], grpT[1], grpT[2])
		Y = om.MVector(objT[0], objT[1], objT[2])
		Z = X-Y
		Z = Z.normal()
		
		cmds.floatFieldGrp("rbgWorldUp", e=1, v1=Z.x)
		cmds.floatFieldGrp("rbgWorldUp", e=1, v2=Z.y)
		cmds.floatFieldGrp("rbgWorldUp", e=1, v3=Z.z)

		cmds.select(sl, r=True)

	except Exception, err:
		om.MGlobal.displayError(err)
	else:
		om.MGlobal.displayInfo("SUCCEED!")

def _disableWorldOrient(* args):
	cmds.button("btnSetWorldUp", e=1, en=0)
	cmds.floatFieldGrp("rbgWorldUp", e=1, en=0)

def _enableWorldOrient(* args):
	cmds.button("btnSetWorldUp", e=1, en=1)
	cmds.floatFieldGrp("rbgWorldUp", e=1, en=1)

def _aimChange(* args):
	aimSelected = cmds.radioButtonGrp("rbgAim", q=True, sl=True)
	upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)
	if aimSelected == upSelected:
		aimSelected = aimSelected + 1
		if aimSelected > 2:
			aimSelected = 0
		cmds.radioButtonGrp("rbgAim", e=1, sl=aimSelected)

def _upChange(* args):
	aimSelected = cmds.radioButtonGrp("rbgAim", q=True, sl=True)
	upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)
	if aimSelected == upSelected:
		upSelected = upSelected + 1
		if upSelected > 2:
			upSelected = 0
		cmds.radioButtonGrp("rbgUp", e=1, sl=upSelected)