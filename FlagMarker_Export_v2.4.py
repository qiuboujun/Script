#Jimmy Qiu
import os
import re
import sys
import datetime

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
marker_color = ['All','Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']
flag_color = ['All','Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']

def getresolve(app='Resolve'):
    dr = bmd.scriptapp(app)
    return dr

def this_timeline():
    return proj.GetCurrentTimeline()

def read_all_marker():
    mks = this_timeline().GetMarkers()
    print(mks)
    return mks

def merge_two_dicts(x, y):
    z =x.copy()
    z.update(y)
    return z

def read_timeline_startTC():
    tc = this_timeline().GetStartFrame()
    return tc

def get_flag(item, flag):
    frameid = item.GetStart() - read_timeline_startTC()
    flagdict = {frameid:flag}
    return flagdict

def read_all_clip_marker():
    trackcount = this_timeline().GetTrackCount("video")
    markerdict= dict()
    for i in range(1, trackcount + 1):
        TimelineItem = this_timeline().GetItemListInTrack("video", i)
        for item in TimelineItem:
            mks = item.GetMarkers()
            for mk_frameId in mks:
                item.UpdateMarkerCustomData(mk_frameId, 'test')
            mks = item.GetMarkers()
            try:
                markerdict = merge_two_dicts(markerdict,mks)
            except AttributeError:
                continue
    print(markerdict)
    return markerdict

def read_all_flag():
    trackcount = this_timeline().GetTrackCount("video")
    CompFlagDict = dict()
    for i in range(1, trackcount + 1):
        TimelineItem = this_timeline().GetItemListInTrack("video", i)
        for item in TimelineItem:
            flag = item.GetFlagList()
            enable_check = item.GetClipEnabled()
            if enable_check != True:
                continue
            if flag != []:
                flagdict = get_flag(item, flag)
                try:
                    CompFlagDict = merge_two_dicts(CompFlagDict,flagdict)
                except AttributeError:
                    continue
    CompFlagDict = OrderedDict(sorted(CompFlagDict.items()))
    ##print(CompFlagDict)
    return CompFlagDict

def bool_test(num):
    if int(num) == 1:
        num = True
    if int(num) == 0:
        num = False
    return num

def read_flag_color(color_filter):
    start_tc = read_timeline_startTC()
    AllFlags = read_all_flag()
    AllFlags = OrderedDict(sorted(AllFlags.items()))
    i = 0
    timeline_name = tl.GetName()
    timestamp = str(get_timestamp())
    flag_comp = "TITLE: " + timeline_name + "\n" + "FCM: NON-DROP FRAME\n" + 'TIME: ' + timestamp + '\n\n'
    for flag_frameId in AllFlags:
        flag_color = AllFlags[flag_frameId]
        if color_filter in str(flag_color) or color_filter == 'All':
             i= i + 1
             color = str(flag_color)
             flag_id = str(i).zfill(3)
             clip_in = str(frames_to_timecode(int(flag_frameId)+start_tc, 23.98, False))
             tl.SetCurrentTimecode(clip_in)
             clip_out = str(frames_to_timecode(tl.GetCurrentVideoItem().GetEnd(), 23.98, False))
             flag_ColoristNotes = ''
             flag_sendto = ''
             flag_ReviewersNotes = ''
             flag_ColoristReviewed = ''
             flag_parse = flag_id + "         TC: " + clip_in + "    " + clip_out + " "+ "  \n" + "*Flag Color: " + color
             if itm['add_clipname'].Checked == True:
                 flag_clipname = tl.GetCurrentVideoItem().GetName()
                 flag_parse = flag_parse + "\n" + "*Clip name: " + flag_clipname
             if itm['add_coloristreviewed'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Reviewed') != '':
                     reviewed = tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Reviewed')
                     if bool_test(reviewed) == True:
                         flag_ColoristReviewed= '\n*Colorist Reviewed: ' + str('Yes')
                 flag_parse = flag_parse + str(flag_ColoristReviewed)
             if itm['add_ColoristNotes'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Notes') != '':
                     flag_ColoristNotes = '\n*Colorist Notes: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Notes')
                 flag_parse = flag_parse + str(flag_ColoristNotes)
             if itm['add_sendto'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Send to') != '':
                     flag_sendto = '\n*Send To: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Send to')
                 flag_parse = flag_parse + str(flag_sendto)
             if itm['add_ReviewersNotes'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Reviewers Notes') != '':
                     flag_ReviewersNotes = '\n*Reviewers Notes: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Reviewers Notes')
                 flag_parse = flag_parse + str(flag_ReviewersNotes)
             flag_comp = flag_comp + flag_parse + "\n\n"
    print(flag_comp)
    return flag_comp

def frames_to_timecode(total_frames, frame_rate, drop):     ##credits to Manne Ohrstrom and Shotgun Software Inc.
    """
    Method that converts frames to SMPTE timecode.
    
    :param total_frames: Number of frames
    :param frame_rate: frames per second
    :param drop: true if time code should drop frames, false if not
    :returns: SMPTE timecode as string, e.g. '01:02:12:32' or '01:02:12;32'
    """
    if drop and frame_rate not in [29.97, 59.94]:
        raise NotImplementedError("Time code calculation logic only supports drop frame "
                                  "calculations for 29.97 and 59.94 fps.")

    # for a good discussion around time codes and sample code, see
    # http://andrewduncan.net/timecodes/

    # round fps to the nearest integer
    # note that for frame rates such as 29.97 or 59.94,
    # we treat them as 30 and 60 when converting to time code
    # then, in some cases we 'compensate' by adding 'drop frames',
    # e.g. jump in the time code at certain points to make sure that
    # the time code calculations are roughly right.
    #
    # for a good explanation, see
    # https://documentation.apple.com/en/finalcutpro/usermanual/index.html#chapter=D%26section=6
    fps_int = int(round(frame_rate))

    if drop:
        # drop-frame-mode
        # add two 'fake' frames every minute but not every 10 minutes
        #
        # example at the one minute mark:
        #
        # frame: 1795 non-drop: 00:00:59:25 drop: 00:00:59;25
        # frame: 1796 non-drop: 00:00:59:26 drop: 00:00:59;26
        # frame: 1797 non-drop: 00:00:59:27 drop: 00:00:59;27
        # frame: 1798 non-drop: 00:00:59:28 drop: 00:00:59;28
        # frame: 1799 non-drop: 00:00:59:29 drop: 00:00:59;29
        # frame: 1800 non-drop: 00:01:00:00 drop: 00:01:00;02
        # frame: 1801 non-drop: 00:01:00:01 drop: 00:01:00;03
        # frame: 1802 non-drop: 00:01:00:02 drop: 00:01:00;04
        # frame: 1803 non-drop: 00:01:00:03 drop: 00:01:00;05
        # frame: 1804 non-drop: 00:01:00:04 drop: 00:01:00;06
        # frame: 1805 non-drop: 00:01:00:05 drop: 00:01:00;07
        #
        # example at the ten minute mark:
        #
        # frame: 17977 non-drop: 00:09:59:07 drop: 00:09:59;25
        # frame: 17978 non-drop: 00:09:59:08 drop: 00:09:59;26
        # frame: 17979 non-drop: 00:09:59:09 drop: 00:09:59;27
        # frame: 17980 non-drop: 00:09:59:10 drop: 00:09:59;28
        # frame: 17981 non-drop: 00:09:59:11 drop: 00:09:59;29
        # frame: 17982 non-drop: 00:09:59:12 drop: 00:10:00;00
        # frame: 17983 non-drop: 00:09:59:13 drop: 00:10:00;01
        # frame: 17984 non-drop: 00:09:59:14 drop: 00:10:00;02
        # frame: 17985 non-drop: 00:09:59:15 drop: 00:10:00;03
        # frame: 17986 non-drop: 00:09:59:16 drop: 00:10:00;04
        # frame: 17987 non-drop: 00:09:59:17 drop: 00:10:00;05

        # calculate number of drop frames for a 29.97 std NTSC
        # workflow. Here there are 30*60 = 1800 frames in one
        # minute

        FRAMES_IN_ONE_MINUTE = 1800 - 2

        FRAMES_IN_TEN_MINUTES = (FRAMES_IN_ONE_MINUTE * 10) - 2

        ten_minute_chunks = total_frames / FRAMES_IN_TEN_MINUTES
        one_minute_chunks = total_frames % FRAMES_IN_TEN_MINUTES

        ten_minute_part = 18 * ten_minute_chunks
        one_minute_part = 2 * ((one_minute_chunks - 2) / FRAMES_IN_ONE_MINUTE)

        if one_minute_part < 0:
            one_minute_part = 0

        # add extra frames
        total_frames += ten_minute_part + one_minute_part

        # for 60 fps drop frame calculations, we add twice the number of frames
        if fps_int == 60:
            total_frames = total_frames * 2

        # time codes are on the form 12:12:12;12
        smpte_token = ";"

    else:
        # time codes are on the form 12:12:12:12
        smpte_token = ":"

    # now split our frames into time code
    hours = int(total_frames / (3600 * fps_int))
    minutes = int(total_frames / (60 * fps_int) % 60)
    seconds = int(total_frames / fps_int % 60)
    frames = int(total_frames % fps_int)
    return "%02d:%02d:%02d%s%02d" % (hours, minutes, seconds, smpte_token, frames) # usage example print frames_to_timecode(123214, 24, False)

def sortid(elem):
    return elem[0]

def read_marker_color(color_filter):
    start_tc = read_timeline_startTC()
    all_marker = read_all_marker()
    all_marker = OrderedDict(sorted(all_marker.items()))
    i = 0
    timeline_name = tl.GetName()
    timestamp = str(get_timestamp())
    marker_comp = "TITLE: " + timeline_name + "\n" + "FCM: NON-DROP FRAME\n" + 'TIME: ' + timestamp + '\n\n'
    for mk_frameId in all_marker:
        marker_list = []
        mk = all_marker[mk_frameId]
        color = str(mk['color'])
        duration = int(mk['duration'])
        note = str(mk['note'])
        name = str(mk['name'])
        customData = mk['customData']
        if color == color_filter or color_filter == 'All':
             i= i + 1
             marker_list = [mk_frameId, color, duration, note, name, customData]
             marker_id = str(i).zfill(3)
             marker_color = str(marker_list[1])
             marker_in = str(frames_to_timecode(int(marker_list[0])+start_tc, 23.98, False))
             tl.SetCurrentTimecode(marker_in)
             marker_tc = str(frames_to_timecode(tl.GetCurrentVideoItem().GetEnd(), 23.98, False))
             marker_name = str(marker_list[4])
             marker_note = str(marker_list[3])
             marker_sendto = ''
             marker_ColoristNotes = ''
             marker_ReviewersNotes = ''
             marker_ColoristReviewed = ''
             marker_parse = marker_id + "         TC: " + marker_in + "    " + marker_tc + " "+ "  \n" + "|Marker Color: " + marker_color + " |Marker Name: " + marker_name + " |Marker Notes: " + marker_note
             if itm['add_clipname'].Checked == True:
                 marker_clipname = tl.GetCurrentVideoItem().GetName()
                 marker_parse = marker_parse + "\n" + "*Clip name: " + marker_clipname
             if itm['add_coloristreviewed'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Reviewed') != '':
                     reviewed = tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Reviewed')
                     if bool_test(reviewed) == True:
                         marker_ColoristReviewed = '\n*Colorist Reviewed: ' + str('Yes')
                 marker_parse = marker_parse + str(marker_ColoristReviewed)
             if itm['add_ColoristNotes'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Notes') != '':
                     marker_ColoristNotes = '\n*Colorist Notes: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Colorist Notes')
                 marker_parse = marker_parse + str(marker_ColoristNotes)
             if itm['add_sendto'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Send to') != '':
                     marker_sendto = '\n*Send To: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Send to')
                 marker_parse = marker_parse + str(marker_sendto)
             if itm['add_Description'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Description') != '':
                     marker_description = '\n*Description: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Description')
                 marker_parse = marker_parse + str(marker_description)
             if itm['add_Comments'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Comments') != '':
                     marker_comments = '\n*Comments: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Comments')
                 marker_parse = marker_parse + str(marker_comments)
             if itm['add_vfx_notes'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('VFX Notes') != '':
                     marker_vfx_notes = '\n*VFX Notes: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('VFX Notes')
                 marker_parse = marker_parse + str(marker_vfx_notes)
             if itm['add_good_take'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Good Take') != '':
                     good_take = tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Good Take')
                     if bool_test(good_take) == True:
                         marker_good_take = '\n*Good Take: ' + str('Yes')
                 marker_parse = marker_parse + str(marker_good_take)
             if itm['add_continuity_reviewed'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Continuity Reviewed') != '':
                     continuity_reviewed = tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Continuity Reviewed')
                     if bool_test(continuity_reviewed) == True:
                         marker_continuity_reviewed = '\n*Continuity Reviewed: ' + str('Yes')
                 marker_parse = marker_parse + str(marker_continuity_reviewed)
             if itm['add_ReviewersNotes'].Checked == True:
                 if tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Reviewers Notes') != '':
                     marker_ReviewersNotes = '\n*Reviewers Notes: ' + tl.GetCurrentVideoItem().GetMediaPoolItem().GetMetadata('Reviewers Notes')
                 marker_parse = marker_parse + str(marker_ReviewersNotes)
             marker_comp = marker_comp + marker_parse + "\n\n"
    print(marker_comp)
    return marker_comp

def _export_marker(ev):
    color = itm['color_list'].CurrentText
    request_filename(ev)
    global get_filename, bad_ending
    if bad_ending == True:
        return
    path = request_dir(ev)
    if path == None:
        return
    edl_text = read_marker_color(color)
    print(get_filename)
    file_name = get_filename + '.edl'
    with open(os.path.join(path, file_name), "w") as file1:
        file1.write(edl_text)
        file1.close()
        print("EDL exported to " + path)

def _export_flag(ev):
    color = itm['color_list'].CurrentText
    request_filename(ev)
    global get_filename, bad_ending
    if bad_ending == 1:
        return
    path = request_dir(ev)
    if path == None:
        return
    edl_text = read_flag_color(color)
    print(get_filename)
    file_name = get_filename + '.edl'
    with open(os.path.join(path, file_name), "w") as file1:
        file1.write(edl_text)
        file1.close()
        print("EDL exported to " + path)

def _export_name(ev):
    global get_filename, fileitm, bad_ending
    get_filename = fileitm['filename_edit'].Text
    print(get_filename)
    disp.ExitLoop()
    bad_ending = 0
    return get_filename

def request_dir(ev):
    selected_path = fu.RequestDir()
    return selected_path

def get_timestamp():
    ts = datetime.datetime.now()
    return ts

def request_filename(ev):
    global fileitm
    window_02 = file_save_ui(ui)

    request = disp.AddWindow({ 
                        "WindowTitle": "Enter Export File Name", 
                        "ID": "fileWin", 
                        "Geometry": [ 
                                    1000, 700, 
                                    450, 85
                         ], 
                        },
    window_02)

    fileitm = request.GetItems()
    request.On.yes.Clicked = _export_name
    request.On.no.Clicked = _exit
    request.On.fileWin.Close = _exit
    request.Show()
    disp.RunLoop()
    request.Hide()

def _exit(ev):
    global bad_ending
    disp.ExitLoop()
    bad_ending = 1

def main_ui(ui):
    window = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.Label({ "ID": "color","Text": "Color Filter: "}),
            ui.ComboBox({ "ID": "color_list","Weight": 2}),
            ui.Button({ "ID": "ClipFlag", "Text": "Export Flag","Weight": 0}),
            ui.Button({ "ID": "TimelineMarker", "Text": "Export Marker","Weight": 0}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.VGroup({"Spacing": 10, "Weight": 1},[
                ui.CheckBox({ "Text": 'Include ClipName', "ID": 'add_clipname',"Weight": 1}),
                ui.CheckBox({ "Text": 'Include SendTo', "ID": 'add_sendto',"Weight": 1}),
                ui.CheckBox({ "Text": 'Include Reviewers Notes', "ID": 'add_ReviewersNotes',"Weight": 1}),
                ui.CheckBox({ "Text": 'Include Colorist Reviewed', "ID": 'add_coloristreviewed',"Weight": 1}),
            ]),
            ui.VGroup({"Spacing": 10, "Weight": 1},[
                ui.CheckBox({ "Text": 'Include Colorist Notes', "ID": 'add_ColoristNotes',"Weight": 1}),
                ui.CheckBox({ "Text": 'Include Description', "ID": 'add_Description',"Weight": 1}),
                ui.CheckBox({ "Text": 'Include Comments', "ID": 'add_Comments',"Weight": 1}),
                ui.CheckBox({ "Text": 'Include VFX Notes', "ID": 'add_vfx_notes',"Weight": 1}),
            ]),
            ui.VGroup({"Spacing": 10, "Weight": 1},[
                ui.CheckBox({ "Text": 'Include Good Take', "ID": 'add_good_take',"Weight": 1}),
                ui.CheckBox({ "Text": 'Include Continuity Reviewed', "ID": 'add_continuity_reviewed',"Weight": 1}),
                ui.HGap({"Weight": 2}),
            ]),
        ])
        ])
    return window

def file_save_ui(ui):
    window = ui.VGroup({"Spacing": 10,},[
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.Label({ "ID": "filename_label","Text": "File name: ", "Weight": 1}),
            ui.LineEdit({ "ID": "filename_edit","Weight": 3}),
        ]),
        ui.HGroup({"Spacing": 10, "Weight": 0,},[
            ui.VGap(),
            ui.Button({ "ID": "yes", "Text": "Yes","Weight": 0}),
            ui.Button({ "ID": "no", "Text": "No","Weight": 0}),
        ])
        ])
    return window

if __name__ == '__main__':
    fu = bmd.scriptapp('Fusion')

    ui = fu.UIManager
    disp = bmd.UIDispatcher(ui)

    window_01 = main_ui(ui)

    dlg = disp.AddWindow({ 
                        "WindowTitle": "FlagMarker Export V2.4", 
                        "ID": "MyWin", 
                        "Geometry": [ 
                                    600, 500, 
                                    630, 190
                         ], 
                        },
    window_01)

    itm = dlg.GetItems()

    itm['color_list'].AddItems(marker_color)
    dlg.On.TimelineMarker.Clicked = _export_marker
    dlg.On.ClipFlag.Clicked = _export_flag
    dlg.On.MyWin.Close = _exit
    dlg.Show()
    disp.RunLoop()
    dlg.Hide()

