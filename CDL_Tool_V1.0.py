#Jimmy Qiu
import os
import re
import sys
import math
import time

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
fu = bmd.scriptapp('Fusion')
ui = app.UIManager
disp = bmd.UIDispatcher(ui)
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()

def getresolve(app='Resolve'):
    dr = bmd.scriptapp(app)
    return dr

def _exit(ev):
    disp.ExitLoop()

def this_timeline():
    return proj.GetCurrentTimeline()

def merge_two_dicts(x, y):
    z =x.copy()
    z.update(y)
    return z

def text_to_cdl(input_text):
    txt = input_text.split("*ASC_SAT ", 1)
    sat = txt[1]
    sop_txt = str(txt[0]).split("(", 3)
    slope = sop_txt[1].replace(")", '')
    offset = sop_txt[2].replace(")", '')
    power_parse = sop_txt[3].split(")", 1)
    power = power_parse[0]
    current_timelineitem = this_timeline().GetCurrentVideoItem()
    cdl_apply = current_timelineitem.SetCDL({"NodeIndex" : "1", "Slope" : slope, "Offset" : offset, "Power" : power, "Saturation" : sat})

def _apply_cdl(ev):
    cdl_txt = itm['cdl_input'].PlainText
    text_to_cdl(cdl_txt)

def _clear_cdl(ev):
    itm['cdl_input'].PlainText = ''

def main_ui(ui):
    window01 = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 7, "Weight": 1,},[
            ui.Label({ "ID": "asc_cdl_text","Text": "ASC CDL Text","Weight": 0}),
            ui.VGap({"Weight": 1}),
            ui.TextEdit({ "ID": "cdl_input","Weight": 3}),
        ]),
        ui.HGroup({"Spacing": 7, "Weight": 0,},[
            ui.VGap({"Weight": 2}),
            ui.Button({ "ID": "apply_cdl", "Text": "Apply","Weight": 0}),
            ui.Button({ "ID": "clear_cdl", "Text": "Clear","Weight": 0}),
        ])
        ])
    return window01

if __name__ == '__main__':

    window_01 = main_ui(ui)

    dlg = disp.AddWindow({ 
                        "WindowTitle": "CDL Tool V1.0", 
                        "ID": "MyWin", 
                        'WindowFlags': {
                              'Window': True,
                              'WindowStaysOnTopHint': True,
                               },
                        'Events': {
                              'ContextMenu': True,
                              'Close': True},
                        "Geometry": [ 
                                    800, 700, 
                                    500, 200
                         ],
                        },
    window_01)

    itm = dlg.GetItems()

    dlg.On.apply_cdl.Clicked = _apply_cdl
    dlg.On.clear_cdl.Clicked = _clear_cdl
    dlg.On.MyWin.Close = _exit

    dlg.Show()
    disp.RunLoop()
    dlg.Hide()

