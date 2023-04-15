#!/usr/bin/env python3
#Jimmy Qiu

import re, math
import sys
import imp
import os
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

regex = False
note_check = False
name_check = False
marker_color = ['Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']
marker_color_filter = ['All','Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']
framerate = 23.976
def _exit(ev):
    disp.ExitLoop()

def getresolve(app='Resolve'):
    dr = bmd.scriptapp(app)
    return dr

def this_pj():
    pj_manager = getresolve().GetProjectManager()
    current_pj = pj_manager.GetCurrentProject()
    return current_pj

def this_timeline():
    return this_pj().GetCurrentTimeline()

def frame_to_index(i):
    lenth = len(str(max(read_all_marker().keys())))
    b = int(math.pow(10, int(lenth)))
    o = str(b+int(i))[1:]
    return o

def read_all_marker():
    mks = this_timeline().GetMarkers()
    return mks

def read_timeline_startTC():
    tc = this_timeline().GetStartFrame()
    print(tc)
    return tc

def merge_two_dicts(x, y):
    z =x.copy()
    z.update(y)
    return z

start_up = read_all_marker()

def add_markers(frameId, color, name, note, duration, customData=''):
    o = this_timeline().AddMarker(frameId, color, name, note, duration, customData)
    return o

def del_markers(by, frameNum, color):
    if by is 'frame':
        o = this_timeline().DeleteMarkerAtFrame(frameNum)
    elif by is 'color':
        o = this_timeline().DeleteMarkersByColor(color)
    else:
        o = False
    return o

def replace_marker(type, mk_frameId, color, name, note, duration, customData):
    del_markers(type, mk_frameId, color)
    add_markers(mk_frameId, color, name, note, duration, customData)

def replace_marker_tc(type, mk_frameId, new_frameId, color, name, note, duration, customData):
    del_markers(type, mk_frameId, color)
    add_markers(new_frameId, color, name, note, duration, customData)

def edit_marker(type, before, after):
    pattern = re.compile(str(before))
    all_marker = read_all_marker()
    for mk_frameId in all_marker:
        mk = all_marker[mk_frameId]
        color = str(mk['color'])
        duration = int(mk['duration'])
        note = str(mk['note'])
        name = str(mk['name'])
        customData = mk['customData']
        before_color = itm['color_a'].CurrentText
        after_color = itm['color_b'].CurrentText
        filter_color = itm['color_filter'].CurrentText
        pattern_colornote = re.compile(str(itm['notes_a'].Text))
        pattern_colorname = re.compile(str(itm['name_a'].Text))
        if type is 'color':
            if before==color:
                if ((itm['filter_notes'].Checked == True) and (itm['filter_name'].Checked == True)):
                    if str(itm['notes_a'].Text) in note:
                        if str(itm['name_a'].Text) in name:                 
                            del_markers('frame', mk_frameId, color)
                            add_markers(mk_frameId, after, name, note, duration, customData)
                if ((itm['filter_notes'].Checked == True) and (itm['filter_name'].Checked == False)):
                    if str(itm['notes_a'].Text) in note:
                        del_markers('frame', mk_frameId, color)
                        add_markers(mk_frameId, after, name, note, duration, customData)
                if ((itm['filter_notes'].Checked == False) and (itm['filter_name'].Checked == True)): 
                    if str(itm['name_a'].Text) in name:
                        del_markers('frame', mk_frameId, color)
                        add_markers(mk_frameId, after, name, note, duration, customData)
                if ((itm['filter_notes'].Checked == False) and (itm['filter_name'].Checked == False)): 
                        del_markers('frame', mk_frameId, color)
                        add_markers(mk_frameId, after, name, note, duration, customData)
            else:
                pass
        elif type is 'name':
            if itm['regexbox'].Checked == True:
                if re.search(pattern, name) is not None:
                    if filter_color==color or filter_color == 'All':
                       new_name = re.sub(pattern, after, name)
                       replace_marker('frame', mk_frameId, color, new_name, note, duration, customData)
                    else:
                        pass
                else:
                    pass
            else:
                if itm['regexbox'].Checked == True:
                  new_name = name.replace(before, after)
                  replace_marker('frame', mk_frameId, color, new_name, note, duration, customData)
                else:
                    if filter_color==color:
                      new_name = name.replace(before, after)
                      replace_marker('frame', mk_frameId, color, new_name, note, duration, customData)
                    else:
                        pass
        elif type is 'note':
            if itm['regexbox'].Checked == True:
                if re.search(pattern, note) is not None:
                    if filter_color==color or filter_color == 'All':
                       new_note = re.sub(pattern, after, note, flags=re.DOTALL)
                       replace_marker('frame', mk_frameId, color, name, new_note, duration, customData)
                    else:
                        pass
                else:
                    pass
            else:
                if itm['regexbox'].Checked == False:
                   if before == '':
                       if note == '':
                           new_note = re.sub('.*', after, note)
                           replace_marker('frame', mk_frameId, color, name, new_note, duration, customData)
                   else:
                       new_note = note.replace(before, after)
                       replace_marker('frame', mk_frameId, color, name, new_note, duration, customData)
                else:
                   if filter_color==color:
                      if before == '':
                          new_note = re.sub(r'^\s*$', after, note)
                          replace_marker('frame', mk_frameId, color, name, new_note, duration, customData)
                      else:
                          new_note = note.replace(before, after)
                          replace_marker('frame', mk_frameId, color, name, new_note, duration, customData)
                   else:
                      pass
        else:
            pass
        print(color, duration, note, name, customData)

def _edit_color(ev):
    before = itm['color_a'].CurrentText
    after = itm['color_b'].CurrentText
    if before==after:
        pass
    else:
        itm['edit_color'].Enabled = False
        itm['edit_color'].Text = 'take a break'
        edit_marker('color', before, after)
        itm['edit_color'].Enabled = True
        itm['edit_color'].Text = 'Replace'
    

def _edit_notes(ev):
    global regex
    before = itm['notes_a'].Text
    after = itm['notes_b'].Text
    if before==after:
        pass
    else:
        itm['edit_notes'].Enabled = False
        itm['edit_notes'].Text = 'Loading'
        edit_marker('note', before, after)
        itm['edit_notes'].Enabled = True
        itm['edit_notes'].Text = 'Change'
    if itm['regexbox'].Checked == True:
        itm['notes_a'].PlaceholderText = 'Regex'
        itm['name_a'].PlaceholderText = 'Regex'
    else:
        itm['name_a'].PlaceholderText = ''
        itm['notes_a'].PlaceholderText = ''

def _regexcheck(ev):
    if itm['regexbox'].Checked == True:
        itm['notes_a'].PlaceholderText = 'Regex'
        itm['name_a'].PlaceholderText = 'Regex'
    else:
        itm['name_a'].PlaceholderText = ''
        itm['notes_a'].PlaceholderText = ''

def _edit_name(ev):
    global regex
    before = itm['name_a'].Text
    after = itm['name_b'].Text
    if before==after:
        regex = bool(1-regex)
        pass
    else:
        itm['edit_name'].Enabled = False
        itm['edit_name'].Text = 'Loading'
        edit_marker('name', before, after)
        itm['edit_name'].Enabled = True
        itm['edit_name'].Text = 'Change'
    if itm['regexbox'].Checked == True:
        itm['notes_a'].PlaceholderText = 'Regex'
        itm['name_a'].PlaceholderText = 'Regex'
    else:
        itm['name_a'].PlaceholderText = ''
        itm['notes_a'].PlaceholderText = ''

def _del_by_color(ev):
    targ = itm['color_filter'].CurrentText
    all_marker = read_all_marker()
    for mk_frameId in all_marker:
        mk = all_marker[mk_frameId]
        note = str(mk['note'])
        name = str(mk['name'])
        if ((itm['filter_notes'].Checked == True) and (itm['filter_name'].Checked == True)):
            if str(itm['notes_a'].Text) in note:
                if str(itm['name_a'].Text) in name:                 
                    del_markers('color', mk_frameId, targ)
        if ((itm['filter_notes'].Checked == True) and (itm['filter_name'].Checked == False)):
            if str(itm['notes_a'].Text) in note:
                    del_markers('color', mk_frameId, targ)
        if ((itm['filter_notes'].Checked == False) and (itm['filter_name'].Checked == True)): 
            if str(itm['name_a'].Text) in name:
                    del_markers('color', mk_frameId, targ)
        if ((itm['filter_notes'].Checked == False) and (itm['filter_name'].Checked == False)): 
                    del_markers('color', mk_frameId, targ)

def _recover(ev):
    current = read_all_marker()
    for frameID in current:
        del_markers('frame', frameID, '')
    
    for mk_frameId in start_up:
        mk = start_up[mk_frameId]
        color = str(mk['color'])
        duration = int(mk['duration'])
        note = str(mk['note'])
        name = str(mk['name'])
        customData = mk['customData']
        o = add_markers(mk_frameId, color, name, note, duration, customData)

def get_nearest_less_element(d, k):
    k = int(k)
    nearest = max(key for key in map(int, d.keys()) if key <= k)
    return nearest

def get_all_timeline_items():
    TimelineConca = []
    TimelineDict = dict()
    trackcount = this_timeline().GetTrackCount("video")
    for i in range(1, trackcount + 1):
        TimelineItem = this_timeline().GetItemListInTrack("video", i)
        TimelineConca = TimelineConca + TimelineItem
    for item in TimelineConca:
        frameID = item.GetStart()
        TimelineDictItem = {frameID: item}
        TimelineDict = merge_two_dicts(TimelineDict, TimelineDictItem)
    TimelineDict = OrderedDict(sorted(TimelineDict.items()))
    return TimelineDict

def _move_middle_clip(ev):
    all_marker = read_all_marker()
    all_marker = OrderedDict(sorted(all_marker.items()))
    TimelineDict = get_all_timeline_items()
    start_tc = read_timeline_startTC()
    filter_color = moveitm['tc_color_filter'].CurrentText
    moveitm['edit_middle_clip'].Enabled = False
    for mk_frameId in all_marker:
        mk = all_marker[mk_frameId]
        color = str(mk['color'])
        duration = int(mk['duration'])
        note = str(mk['note'])
        name = str(mk['name'])
        customData = mk['customData']
        if filter_color == color or filter_color == 'All' and duration < int(2):
            frame = mk_frameId + start_tc
            nearest = get_nearest_less_element(TimelineDict, frame)
            clip_in = TimelineDict[nearest].GetStart()
            clip_out = TimelineDict[nearest].GetEnd()
            new_framId = int(clip_in + (clip_out - clip_in)/2 - start_tc)
            replace_marker_tc('frame', mk_frameId, new_framId, color, name, note, duration, customData)
    moveitm['edit_middle_clip'].Enabled = True
    _exit(ev)

def _seconds(value):
    if isinstance(value, str):
        _zip_ft = zip((3600, 60, 1, 1/framerate), value.split(':'))
        return sum(f * float(t) for f,t in _zip_ft)
    elif isinstance(value, (int, float)):
        return value / framrate
    else:
        return 0

def _display_text_to_tc(ev):
    input_text_before = moveitm['custom_offset_text'].Text
    if (len(input_text_before) % 2) != 0:
        if input_text_before[0] != '0':
            input_text_before = '0'+input_text_before
    else:
        if len(input_text_before) > 2 and input_text_before[0] == '0':
            input_text_before = input_text_before[1:]
    input_text = re.sub('[^0-9 \n\.]', '', input_text_before)
    output_text = ':'.join(input_text[i:i+2] for i in range(0, len(input_text), 2))
    print(output_text)
    if len(output_text) == 13 and output_text[-2] == ':':
        output_text = output_text[:-2]
    print(output_text) 
    moveitm['custom_offset_text'].Text = output_text

def _timecode(seconds):
    return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
        .format(h=int(seconds/3600),
                m=int(seconds/60%60),
                s=int(seconds%60),
                f=round((seconds - int(seconds))*framerate))

def _frames(seconds):
    return seconds * framerate

def timecode_to_frames(timecode, start=None):
    if (timecode.find('-') != -1):
        result = -int(round(_frames(_seconds(timecode) - _seconds(start))))
    else:
        result = int(round(_frames(_seconds(timecode) - _seconds(start))))
    return result

def rejoined(src, sep='-', _split = re.compile('..').findall):
    return sep.join(_split(src))

def num_to_timecode(number):
    if int(number) >= 0:
        zero_filled_number = str(number).zfill(8)
        new_number = rejoined(zero_filled_number, sep=':')
    if int(number) < 0:
        number = abs(int(number))
        zero_filled_number = str(number).zfill(8)
        new_number = '-'+rejoined(zero_filled_number, sep=':')
    return new_number

def _update_tc_text(ev):
    input_text = moveitm['custom_offset_text'].Text
    if (input_text.count(':') == 4):
        process_tc = input_text
    else:
        input_text = input_text.translate(None, ':.,')
        process_tc = num_to_timecode(input_text)
    moveitm['custom_offset_text'].Text = process_tc

def _timecode_text_to_tc(ev):
    input_text = moveitm['custom_offset_text'].Text
    if (input_text.count(':') == 4):
        process_tc = input_text
    else:
        input_text = input_text.translate(None, ':.,')
        process_tc = num_to_timecode(input_text)
    moveitm['custom_offset_text'].Text = process_tc
    moveitm['custom_offset_text'].Enabled = False
    moveitm['edit_user_input'].Enabled = False
    _move_custom_offset(ev)
    moveitm['custom_offset_text'].Text = ''
    moveitm['custom_offset_text'].Enabled = True
    moveitm['edit_user_input'].Enabled = True
    moveitm['custom_offset_text'].Text = ''
    _exit(ev)

def _move_custom_offset(ev):
    all_marker = read_all_marker()
    all_marker = OrderedDict(sorted(all_marker.items()))
    TimelineDict = get_all_timeline_items()
    start_tc = read_timeline_startTC()
    filter_color = moveitm['tc_color_filter'].CurrentText
    for mk_frameId in all_marker:
        mk = all_marker[mk_frameId]
        color = str(mk['color'])
        duration = int(mk['duration'])
        note = str(mk['note'])
        name = str(mk['name'])
        customData = mk['customData']
        if filter_color == color or filter_color == 'All':
            offset = timecode_to_frames(moveitm['custom_offset_text'].Text)
            new_framId = mk_frameId + offset
            replace_marker_tc('frame', mk_frameId, new_framId, color, name, note, duration, customData)

def _move_tc(ev):
    global move_tc, moveitm
    move_tc = disp.AddWindow({ 
                        "WindowTitle": "Edit Marker TC", 
                        "ID": "moveWin",
                        'WindowFlags': {
                              'Window': True,
                              'WindowStaysOnTopHint': True,
                               }, 
                        "Geometry": [ 
                                    800, 300, 
                                    480, 100
                         ],
                        },
    window_02)

    moveitm = move_tc.GetItems()
    moveitm['tc_color_filter'].AddItems(marker_color_filter)

    move_tc.On.edit_middle_clip.Clicked = _move_middle_clip
    move_tc.On.edit_user_input.Clicked = _timecode_text_to_tc
    move_tc.On.custom_offset_text.TextEdited = _display_text_to_tc
    move_tc.On.custom_offset_text.EditingFinished = _update_tc_text
    move_tc.On.moveWin.Close = _exit

    move_tc.Show()
    disp.RunLoop()
    move_tc.Hide()

def main_ui(ui):
    window = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "color","Text": "Before"}),
            ui.ComboBox({ "ID": "color_a","Weight": 4}),
            ui.Label({ "ID": "color1","Text": "After"}),
            ui.ComboBox({ "ID": "color_b","Weight": 4}),
            ui.Button({ "ID": "edit_color", "Text": "Replace","Weight": 0}),
            ui.Button({ "ID": "move_tc", "Text": "Move","Weight": 0}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "notes","Text": "Notes"}),
            ui.LineEdit({ "ID": "notes_a","Weight": 4}),
            ui.CheckBox({ "Text": 'Filter', "ID": 'filter_notes',"Weight": 1}),
            ui.LineEdit({ "ID": "notes_b","Weight": 4}),
            ui.Button({ "ID": "edit_notes", "Text": "Change","Weight": 0}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "name","Text": "Name"}),
            ui.LineEdit({ "ID": "name_a","Weight": 4}),
            ui.CheckBox({ "Text": 'Filter', "ID": 'filter_name',"Weight": 1}),
            ui.LineEdit({ "ID": "name_b","Weight": 4}),
            ui.Button({ "ID": "edit_name", "Text": "Change","Weight": 0}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.CheckBox({ "Text": 'Regular Expression', "ID": 'regexbox', "Weight": 0}),
            ui.Label({ "ID": "filtercolor","Text": "Color Filter:","Weight": 0}),
            ui.ComboBox({ "ID": "color_filter","Weight": 0}),
            ui.Label({ "ID": "tips","Text": "Tips: regular expression for any character .*"}),
            ui.Button({ "ID": "del_by_color", "Text": "Delete","Weight": 0}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
        ui.Button({ "ID": "recover","Text": "Reset Changes","Weight": 1}),
        ])
        ])
    return window

def timecode_ui(ui):
    window02 = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.Label({ "ID": "tc_filtercolor","Text": "Color Filter:","Weight": 0}),
            ui.ComboBox({ "ID": "tc_color_filter","Weight": 1}),
            ui.VGap({"Weight": 1}),
            ui.Button({ "ID": "edit_middle_clip", "Text": "Move to center of the clip","Weight": 0}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[ 
            ui.Label({ "ID": "tc_custom_text","Text": "Offset Timecode:","Weight": 0}),
            ui.LineEdit({ "ID": "custom_offset_text","Weight": 1, "PlaceholderText": "00:00:00:00", "MaxLength": 12, "Alignment": {"AlignRight": True}, 'Events': {'EditingFinished': True, 'TextEdited': True}}),
            ui.VGap({"Weight": 2}),
            ui.Button({ "ID": "edit_user_input", "Text": "Move with custom offset","Weight": 0}),
        ])
        ])
    return window02

fu = bmd.scriptapp('Fusion')

ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

window_01 = main_ui(ui)
window_02 = timecode_ui(ui)

dlg = disp.AddWindow({ 
                        "WindowTitle": "Marker Editor V3.5", 
                        "ID": "MyWin", 
                        'WindowFlags': {
                              'Window': True,
                              'WindowStaysOnTopHint': True,
                               },
                        "Geometry": [ 
                                    600, 600, 
                                    700, 180
                         ], 
                        },
window_01)

itm = dlg.GetItems()

itm['color_a'].AddItems(marker_color)
itm['color_b'].AddItems(marker_color)
itm['color_filter'].AddItems(marker_color_filter)

dlg.On.edit_color.Clicked = _edit_color
dlg.On.edit_name.Clicked = _edit_name
dlg.On.edit_notes.Clicked = _edit_notes
dlg.On.del_by_color.Clicked = _del_by_color
dlg.On.recover.Clicked = _recover
dlg.On.regexbox.Clicked = _regexcheck
dlg.On.move_tc.Clicked = _move_tc

dlg.On.MyWin.Close = _exit
dlg.Show()
disp.RunLoop()
dlg.Hide()
