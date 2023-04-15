#Created by Jimmy Qiu
#Please create an unique bin for the file you wish to rename. Please be aware it can only rename files within the same folder path.
import os
import sys
import imp
import re

def GetResolve():
    try:
    # The PYTHONPATH needs to be set correctly for this import statement to work.
    # An alternative is to import the DaVinciResolveScript by specifying absolute path (see ExceptionHandler logic)
        import DaVinciResolveScript as bmd
    except ImportError:
        if sys.platform.startswith("darwin"):
            expectedPath="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            import os
            expectedPath=os.getenv('PROGRAMDATA') + "\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\"
        elif sys.platform.startswith("linux"):
            expectedPath="/opt/resolve/Developer/Scripting/Modules/"

        # check if the default path has it...
        print("Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
        try:
            import imp
            bmd = imp.load_source('DaVinciResolveScript', expectedPath+"DaVinciResolveScript.py")
        except ImportError:
            # No fallbacks ... report error:
            print("Unable to find module DaVinciResolveScript - please ensure that the module DaVinciResolveScript is discoverable by python")
            print("For a default DaVinci Resolve installation, the module is expected to be located in: "+expectedPath)
            sys.exit()

    return bmd.scriptapp("Resolve")

resolve = GetResolve()
lib = "/opt/resolve/libs/Fusion/fusionscript.so"
bmd = imp.load_dynamic('fusionscript', lib)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
ms = resolve.GetMediaStorage()
mp = proj.GetMediaPool()

def _exit(ev):
    disp.ExitLoop()

def getresolve(app='Resolve'):
    dr = bmd.scriptapp(app)
    return dr

def find_file_path():
    currentfolder = mp.GetCurrentFolder()
    mediapoolitem = currentfolder.GetClipList()
    mediapool_item = mediapoolitem[0]
    media_item = mediapool_item.GetClipProperty('File Path')
    print(media_item)
    file_path = os.path.dirname(os.path.abspath(media_item))
    return file_path

def applypath():
    file_path = find_file_path()+"/"
    find = itm['findtext'].Text
    replace = itm['replacetext'].Text
    print(file_path)
    for file in os.listdir(file_path):
       os.renames(file_path+file, file_path+file.replace(find, replace))
    return file_path
	
def _rename(ev):
    find = itm['findtext'].Text
    replace = itm['replacetext'].Text
    if find == replace:
        pass
    else:
        itm['rename'].Enabled = False
        itm['rename'].Text = 'In Progress'
        applypath()
        itm['rename'].Enabled = True
        itm['rename'].Text = 'Rename'
    _exit(ev)

def _popup(ev):
    popitm['warningtext'].Text = "Are you sure you want to rename files in \n"+find_file_path()+" ?"
    popup.Show()
    disp.RunLoop()
    popup.Hide()

def main_ui(ui):
    window01 = ui.VGroup({"Spacing": 20,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "find","Text": "Find"}),
            ui.LineEdit({ "ID": "findtext","Weight": 4,"Text": ""}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "replace","Text": "Replace"}),
            ui.LineEdit({ "ID": "replacetext","Weight": 4,"Text": ""}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.HGap(),
            ui.Button({ "ID": "rename", "Text": "Rename","Weight": 0}),
        ]),
        ])
    return window01

def warning_ui(ui):
    window02 = ui.VGroup({"Spacing": 50,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "warningtext","Text": " "}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.HGap(),
            ui.Button({ "ID": "yesbutton", "Text": "Yes","Weight": 0}),
            ui.Button({ "ID": "nobutton", "Text": "No","Weight": 0}),
        ]),
        ])
    return window02

fu = bmd.scriptapp('Fusion')

ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

window_01 = main_ui(ui)
window_02 = warning_ui(ui)

dlg = disp.AddWindow({ 
                        "WindowTitle": "Batch Rename Tool", 
                        "ID": "MyWin", 
                        "Geometry": [ 
                                    600, 600, 
                                    500, 135
                         ], 
                        },
window_01)

popup = disp.AddWindow({ 
                        "WindowTitle": "Warning", 
                        "ID": "MyPop", 
                        "Geometry": [ 
                                    1000, 1000, 
                                    1000, 135
                         ], 
                        },
window_02)

itm = dlg.GetItems()
popitm= popup.GetItems()

dlg.On.rename.Clicked = _popup
dlg.On.MyWin.Close = _exit
popup.On.MyPop.Close = _exit
popup.On.nobutton.Clicked = _exit
popup.On.yesbutton.Clicked = _rename
dlg.Show()
disp.RunLoop()
dlg.Hide()

