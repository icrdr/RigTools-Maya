import shelf
import main
import orientJoint

#reload(main)
#reload(orientJoint)
#reload(shelf)

class customShelf(shelf._shelf):
    def build(self):
        self.addButon("Edge 2 Curves", icon="polyEdgeToCurves.png", command=main.polyToCurve, doubleCommand=main.polyToCurveS)
        self.addButon("Merge Curves", icon="smoothCurve.png", command=main.mergeCurves)
        self.addButon("Match Transform", icon="snapTogetherTool.png", command=main.matchTransform, doubleCommand=main.matchPivot)
        self.addButon("Group Tt", icon="group.png", command=main.groupIt)
        self.addButon("Space Switch Setup", icon="parent.png", command=main.spaceSwitchSetup)
        self.addButon("Joint Orient", icon="orientJoint.png", command=orientJoint.orientJointsWindow)
        self.addSeparator()
        self.addButon("Save or load Transform", icon="locator.png", command=main.saveTransform)
        self.addButon("Rename It", icon="quickRename.png", command=main.renameIt)
        self.addSeparator()
        p = self.addMenu("Toggle Display", icon="hsClearView.png")
        self.addMenuItem(p, "Display All", command=main.displayAll)
        self.addMenuItem(p, "Mesh and Curve Only ", command=main.displayMeshCurve)
        self.addMenuItem(p, "Mesh Only ", command=main.displayMesh)
        self.addButon("Toggle LocalAxis", icon="out_buttonManip.png", command=main.showSelectedLocalAxis, doubleCommand=main.hideSelectedLocalAxis)

def start():
    customShelf(name="RigTools")