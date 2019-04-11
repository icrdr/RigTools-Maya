# Maya-RigTools
a simple rigging tools in maya.
![](https://github.com/icrdr/Maya-RigTools/raw/master/img/0.png)

## Instructions
a simple tool-kit for rigging in maya. Those tools merged commonly used sequential-operation into one click button. 
It makes rigging much more convenit.
</br>

![](https://github.com/icrdr/Maya-RigTools/raw/master/img/1.png)
#### Edge 2 Curves
Single click: create curves from polygon's edge with 1 degree.
Double click: create curves from polygon's edge with 3 degree.
</br>
</br>

![](https://github.com/icrdr/Maya-RigTools/raw/master/img/2.png)
#### Merge Curves
Merge selected curves' shape into one object.
</br>
</br>

![](https://github.com/icrdr/Maya-RigTools/raw/master/img/3.png)
#### Group It
Group the every selected items at same position, than transfer items' transformation to it's group. 
</br>
</br>

![](https://github.com/icrdr/Maya-RigTools/raw/master/img/4.png)
#### Space Switch Setup
Create a space switching system form selection.
Select order: Target1, Target2, ..., Controller.
</br>
</br>

![](https://github.com/icrdr/Maya-RigTools/raw/master/img/5.png)
#### Match Transform
Select 1 item: Save or load transformation.
Select 2 items: Transfer the first selected item's transformation to the second.
</br>
</br>

![](https://github.com/icrdr/Maya-RigTools/raw/master/img/6.png)
#### Rename It
rename both item's group and itself.
</br>

## How to install
1. Simply put folder **'rigTools'** under **'Script Path'**
**Script Path:**
- Windows: <drive>:\Documents and Settings\<username>\MyDocuments\maya\<Version>\scripts
- Mac OS X: ~/Library/Preferences/Autodesk/maya/<version>/scripts.
- Linux: ~/maya/<version>/scripts.

2. Edit **'userSetup.py'** under **'Script Path'**
```python
import maya.cmds as cmds
from rigTools import install

cmds.evalDeferred("install.start()")
```
Add it at last line.
**Or simply put the offered 'userSetup.py' into 'Script Path'**: