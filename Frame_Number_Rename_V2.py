#!/usr/bin/env python3
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

##def _seconds(value):
#   if isinstance(value, str): #value seems to be a timestamp
#        _zip_ft = zip((3600, 60, 1, 1/framerate), value.split(':'))
#        return sum(f * float(t) for f, t in _zip_ft)
#    elif isinstance(value, (int, float)): #frames
#        return value / framerate
#    else:
#        return 0

#def _timecode(seconds):
#    return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
#           .format(h=round(seconds/3600),
#                   m=round(seconds/60%60),
#                   s=round(seconds%60),
#                   f=round((seconds-round(seconds))*framerate))

#def _frames(seconds):
#    return seconds * framerate

#def tc_to_frame(timecode, start=None):
#    return _frames(_seconds(timecode) - _seconds(start))

#def frame_to_tc(frames, start=None):
#    return _timecode(_seconds(frames) + _seconds(start))

def applypath():
    file_path = find_file_path()+"/"
    old_tc = itm['oldtctext'].Text
    new_tc = itm['newtctext'].Text
    print(file_path)
    renamed = []
# Frame padding digits
    for file in sorted(os.listdir(file_path), key=len):
        i = int(itm['framedigittext'].Text)
        if itm['extensiontext'].CurrentText == '.':
            new_val = re.findall('\.\d{%s}'% i, file)[-1]
        if itm['extensiontext'].CurrentText == '_':
            new_val = re.findall('\_\d{%s}'% i, file)[-1]
        new_output = (new_val if new_val else '')
        new_output_num = new_output[1:]
        #print(new_output_num)
        new_output = int(new_output_num)
        output_cal = new_output + (int(itm['newtctext'].Text) - int(itm['oldtctext'].Text))
        zero_filled_number = str(output_cal).zfill(i+5)
        os.rename(file_path+file, file_path+file.replace(str(new_output_num), str(zero_filled_number)))
    return file_path

def rename_zero():
    file_path = find_file_path()+"/"
    find = '.00000'
    replace = '.'
    for file in os.listdir(file_path):
       os.renames(file_path+file, file_path+file.replace(find, replace))
    find = '_00000'
    replace = '_'
    for file in os.listdir(file_path):
       os.renames(file_path+file, file_path+file.replace(find, replace))

def _rename(ev):
    _exit(ev)
    old_tc = itm['oldtctext'].Text
    new_tc = itm['newtctext'].Text
    if old_tc == new_tc:
        pass
    else:
        itm['rename'].Enabled = False
        itm['rename'].Text = 'In Progress'
        applypath()
        rename_zero()
        itm['rename'].Enabled = True
        itm['rename'].Text = 'Rename'

def _popup(ev):
    popitm['warningtext'].Text = "Are you sure you want to rename files in \n"+find_file_path()+" ?"
    popup.Show()
    disp.RunLoop()
    popup.Hide()


def main_ui(ui):
    window01 = ui.VGroup({"Spacing": 20,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "framedigit","Text": "Frame Padding Digits","Weight": 0}),
            ui.LineEdit({ "ID": "framedigittext","Weight": 0,"Text": ""}),
            ui.HGap(),
            ui.Label({ "ID": "extensionlabel","Text": "Extension Format","Weight": 0}),
            ui.ComboBox({ "ID": "extensiontext","Weight": 1}),
        ]),
        ui.HGroup({"Spacing": 15, "Weight": 0,},[ 
            ui.Label({ "ID": "oldtc","Text": "Old Start Frame Number"}),
            ui.LineEdit({ "ID": "oldtctext","Weight": 2,"Text": ""}),
            ui.HGap(),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.Label({ "ID": "newtc","Text": "New Start Frame Number"}),
            ui.LineEdit({ "ID": "newtctext","Weight": 2,"Text": ""}),
            ui.HGap(),
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
                        "WindowTitle": "Batch TC Rename Tool", 
                        "ID": "MyWin", 
                        "Geometry": [ 
                                    600, 600, 
                                    500, 185
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

extension_char = ['.', '_']
itm = dlg.GetItems()
popitm= popup.GetItems()
itm['extensiontext'].AddItems(extension_char)

dlg.On.rename.Clicked = _popup
dlg.On.MyWin.Close = _exit
popup.On.MyPop.Close = _exit
popup.On.nobutton.Clicked = _exit
popup.On.yesbutton.Clicked = _rename

dlg.Show()
disp.RunLoop()
dlg.Hide()


