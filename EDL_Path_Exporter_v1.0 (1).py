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

def getresolve(app='Resolve'):
    dr = bmd.scriptapp(app)
    return dr

def this_timeline():
    return proj.GetCurrentTimeline()

def merge_two_dicts(x, y):
    z =x.copy()
    z.update(y)
    return z

def get_track_timeline_items(track_id):
    TimelineDict = dict()
    TimelineItem = this_timeline().GetItemListInTrack("video", int(track_id))
    for item in TimelineItem:
        enable_check = item.GetClipEnabled()
        if enable_check == True:
            try:
                item_name = item.GetMediaPoolItem().GetClipProperty('Reel Name')
                if item_name != '':
                    TimelineDictItem = {item_name: item}
                    print(TimelineDictItem)
                    TimelineDict = merge_two_dicts(TimelineDict, TimelineDictItem)
            except Exception:
                sys.exc_clear()
    TimelineDict = OrderedDict(sorted(TimelineDict.items()))
    return TimelineDict

def _test(ev):
    track_id = itm['track_list'].CurrentText
    selected_path = fu.RequestDir()
    clip_list = get_track_timeline_items(track_id)
    timeline_to_edl(selected_path, clip_list)

def timeline_to_edl(path, item_list):
    tl = proj.GetCurrentTimeline()
    file_name = path+'filepath.edl'
    print(file_name)
    timelinename = tl.GetName()
    export = tl.Export(file_name, resolve.EXPORT_EDL)
    last_line = None
    track_id = itm['track_list'].CurrentText
    with open(file_name, 'r') as original, open(path+timelinename+'_V'+track_id+'.edl', 'w+') as new:
        original_list = original.readlines()
        writing = False
        for line in original_list:
            if line != "\n" and line != "\r\n" and line != "\r" and line != "\r\n\r\n" and line != "\n\n":
                writing = True
            else:
                writing = False
                if last_line != None:
                    #lines = new.readlines()
                    #lines = lines[:-1]
                    for clip in item_list:
                        if clip in last_line:
                            timeline_item = item_list[clip]
                            file_path = timeline_item.GetMediaPoolItem().GetClipProperty('File Path')
                            file_path_parent = os.path.dirname(file_path)
                            if file_path != '':
                                new.write("DLEDL: PATH: "+file_path_parent+"\n")
                                new.write("DLEDL: EDIT:0 ORIGIN: "+file_path)
                                new.write('\n')
                                #print(file_path)
            if writing:
                if 'V     C' in line:
                    line = "\r\n" + line
                new.write(line)
                #print(line)
            if 'V     C' in line:
                last_line = line
    os.remove(file_name)

def _exit(ev):
    disp.ExitLoop()

def main_ui(ui):
    window = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.Label({ "ID": "color","Text": "Track Num: ", "Weight": 0}),
            ui.ComboBox({ "ID": "track_list","Weight": 1}),
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
                        "WindowTitle": "Export EDL with Path V1.0", 
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
    itm['track_list'].AddItems(track_id)
    dlg.On.export.Clicked = _test
    dlg.On.cancel.Clicked = _exit
    dlg.On.MyWin.Close = _exit
    dlg.Show()
    disp.RunLoop()
    dlg.Hide()


