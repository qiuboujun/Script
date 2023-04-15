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
track_id = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']
clip_color = ['','Orange','Apricot','Yellow','Lime','Olive','Green','Teal','Navy','Blue','Purple','Violet','Pink','Tan','Beige','Brown','Chocolate']

def getresolve(app='Resolve'):
    dr = bmd.scriptapp(app)
    return dr

def this_timeline():
    return proj.GetCurrentTimeline()

def merge_two_dicts(x, y):
    z =x.copy()
    z.update(y)
    return z

def get_track_timeline_items(track_id, clip_color):
    TimelineDict = dict()
    TimelineItem = this_timeline().GetItemListInTrack("video", int(track_id))
    for item in TimelineItem:
        enable_check = item.GetClipEnabled()
        if enable_check == True:
            try:
                item_name = item.GetMediaPoolItem().GetClipProperty('Reel Name')
                item_color = item.GetClipColor()
                if item_name != '' and item_color == clip_color:
                    TimelineDictItem = {item_name: item}
                    print(TimelineDictItem)
                    TimelineDict = merge_two_dicts(TimelineDict, TimelineDictItem)
            except Exception:
                sys.exc_clear()
    TimelineDict = OrderedDict(sorted(TimelineDict.items()))
    return TimelineDict

def _test(ev):
    track_id = itm['track_list'].CurrentText
    clip_color = itm['clipcolor_list'].CurrentText
    selected_path = fu.RequestDir()
    itm['export'].Enabled = False
    itm['export'].Text = 'In Progress'
    clip_list = get_track_timeline_items(track_id, clip_color)
    timeline_to_edl(selected_path, clip_list)
    itm['export'].Enabled = True
    itm['export'].Text = 'Export'

def timeline_to_edl(path, item_list):
    tl = proj.GetCurrentTimeline()
    file_name = path+'filepath.edl'
    print(file_name)
    timelinename = tl.GetName()
    export = tl.Export(file_name, resolve.EXPORT_EDL)
    last_line = None
    clip_color = itm['clipcolor_list'].CurrentText
    track_id = itm['track_list'].CurrentText
    with open(file_name, 'r') as original, open(path+timelinename+'_V'+track_id+'.edl', 'w+') as new:
        original_list = original.readlines()
        new.write("CLIP COLOR: "+clip_color+"\r\n")
        writing = False
        for line in original_list:
            if last_line != None:
                for clip in item_list:
                    if 'V     C' in line:
                        if clip in line:
                            writing = True
                    else:
                        if clip in last_line:
                            writing = True
            if writing:
                if 'V     C' in line:
                    line = "\r\n" + line
                new.write(line)
                #print(line)
            if 'V     C' in line:
                last_line = line
            writing = False
    os.remove(file_name)

def _exit(ev):
    disp.ExitLoop()

def main_ui(ui):
    window = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.Label({ "ID": "color","Text": "Track Number ", "Weight": 0}),
            ui.ComboBox({ "ID": "track_list","Weight": 1}),
            ui.VGap({"Weight": 1}),
            ui.Label({ "ID": "clip_text","Text": "Clip Color ", "Weight": 0}),
            ui.ComboBox({ "ID": "clipcolor_list","Weight": 1}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.VGap({"Weight": 1}),
            ui.Button({ "ID": "export", "Text": "Export","Weight": 0}),
            ui.Button({ "ID": "cancel", "Text": "Cancel","Weight": 0}),
        ]),
        ])
    return window

if __name__ == '__main__':
    fu = bmd.scriptapp('Fusion')

    ui = fu.UIManager
    disp = bmd.UIDispatcher(ui)

    window_01 = main_ui(ui)

    dlg = disp.AddWindow({ 
                        "WindowTitle": "Export Clip Color EDL V1.0", 
                        "ID": "MyWin", 
                        'WindowFlags': {
                              'Window': True,
                              'WindowStaysOnTopHint': True,
                               },
                        "Geometry": [ 
                                    600, 500, 
                                    350, 80
                         ], 
                        },
    window_01)

    itm = dlg.GetItems()
    itm['track_list'].AddItems(track_id)
    itm['clipcolor_list'].AddItems(clip_color)
    dlg.On.export.Clicked = _test
    dlg.On.cancel.Clicked = _exit
    dlg.On.MyWin.Close = _exit
    dlg.Show()
    disp.RunLoop()
    dlg.Hide()


