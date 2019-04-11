import shelf
import main
#reload(main)

class customShelf(shelf._shelf):
    def build(self):
        global WPs
        self.addButon("Edge 2 Curves", icon="polyEdgeToCurves.png", command=main.polyToCurve, doubleCommand=main.polyToCurveS)
        self.addButon("Merge Curves", icon="smoothCurve.png", command=main.mergeCurves)
        self.addButon("Group Tt", icon="group.png", command=main.groupIt)
        self.addButon("Space Switch Setup", icon="parent.png", command=main.spaceSwitchSetup)
        self.addSeparator()
        self.addButon("Match Transform", icon="displaceToPolygons.png", command=main.matchTransform, doubleCommand=main.matchTransform)
        self.addButon("Rename It", icon="text.png", command=main.renameIt)

def start():
    customShelf(name="RigTools")