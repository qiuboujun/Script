#Jimmy Qiu
import os
import re
import sys
import datetime
from collections import Counter

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
tl = proj.GetCurrentTimeline()
timeline_name = tl.GetName()
flag_color = ['Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']


def getresolve(app='Resolve'):
    dr = bmd.scriptapp(app)
    return dr

def this_timeline():
    return proj.GetCurrentTimeline()

def merge_two_dicts(x, y):
    z =x.copy()
    z.update(y)
    return z

def run_fast_scandir(sub):
    subfolders = []
    if len(sub.GetSubFolderList()) != 0:
        for folder in sub.GetSubFolderList():
            subfolders.append(folder)

        for sub in list(subfolders):
            sf = run_fast_scandir(sub)
            subfolders.extend(sf)
    else:
        pass
    print(subfolders)
    return subfolders

def get_clip_list(folder_list):
    clip_list = []
    for folder in folder_list:
        clips = folder.GetClipList()
        if clips != None:
            clip_list.extend(clips)
    return clip_list

def check_clip_name(cliplist):
    clipname_dict = {}
    clipname_list = []
    clip_list = []
    for clip in cliplist:
        clipname = clip.GetName()
        clipdict = {clip:clipname}
        clipname_dict = merge_two_dicts(clipname_dict, clipdict)
        clipname_list.append(clipname)
    counts = Counter(clipname_list)
    for key in counts:
        if counts[key] >= 2:
            clip_item = [k for k,v in clipname_dict.items() if v == key]
            clip_list.extend(clip_item)
    print(clip_list)
    return clip_list

def apply_flag(color, cliplist):
    itm['RemoveFlag'].Enabled = False
    itm['ClipFlag'].Enabled = False 
    itm['ClipFlag'].Text = 'In Progress'
    for clip in cliplist:
        applyflag = clip.AddFlag(color)
    itm['RemoveFlag'].Enabled = True
    itm['ClipFlag'].Enabled = True
    itm['ClipFlag'].Text = 'Apply'
    return applyflag

def clear_flag(color, cliplist):
    itm['RemoveFlag'].Enabled = False
    itm['ClipFlag'].Enabled = False
    itm['RemoveFlag'].Text = 'In Progress'
    for clip in cliplist:
        clearflag = clip.ClearFlags(color)
    itm['RemoveFlag'].Enabled = True
    itm['ClipFlag'].Enabled = True
    itm['RemoveFlag'].Text = 'Clear'
    return clearflag

def _search_folder(ev):
    flag_color = itm['color_list'].CurrentText
    mediapool = proj.GetMediaPool()
    current_folder = mediapool.GetCurrentFolder()
    subfolder_list = run_fast_scandir(current_folder)
    if len(subfolder_list) == 0:
        subfolder_list = [current_folder]
    clip_list = get_clip_list(subfolder_list)
    clipname = check_clip_name(clip_list)
    applyflag = apply_flag(flag_color, clipname)
    print('done')

def _remove_search_folder(ev):
    flag_color = itm['color_list'].CurrentText
    mediapool = proj.GetMediaPool()
    current_folder = mediapool.GetCurrentFolder()
    subfolder_list = run_fast_scandir(current_folder)
    if len(subfolder_list) == 0:
        subfolder_list = [current_folder]
    clip_list = get_clip_list(subfolder_list)
    clipname = check_clip_name(clip_list)
    clearflag = clear_flag(flag_color, clipname)
    print('done')

def _exit(ev):
    disp.ExitLoop()

def main_ui(ui):
    window = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.Label({ "ID": "color","Text": "Flag Color: ", "Weight": 0}),
            ui.ComboBox({ "ID": "color_list","Weight": 1}),
            ui.VGap({"Weight": 1}),
            ui.Button({ "ID": "ClipFlag", "Text": "Apply","Weight": 0}),
            ui.Button({ "ID": "RemoveFlag", "Text": "Clear","Weight": 0}),
            ]),
        ])
    return window

if __name__ == '__main__':
    fu = bmd.scriptapp('Fusion')

    ui = fu.UIManager
    disp = bmd.UIDispatcher(ui)

    window_01 = main_ui(ui)

    dlg = disp.AddWindow({ 
                        "WindowTitle": "Flag Duplicated Clips V1.0", 
                        "ID": "MyWin", 
                        'WindowFlags': {
                              'Window': True,
                              'WindowStaysOnTopHint': True,
                               },
                        "Geometry": [ 
                                    600, 500, 
                                    530, 80
                         ], 
                        },
    window_01)

    itm = dlg.GetItems()

    itm['color_list'].AddItems(flag_color)
    dlg.On.ClipFlag.Clicked = _search_folder
    dlg.On.RemoveFlag.Clicked = _remove_search_folder
    dlg.On.MyWin.Close = _exit
    dlg.Show()
    disp.RunLoop()
    dlg.Hide()


