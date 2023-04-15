resolve = Resolve()
pm = resolve:GetProjectManager()
proj = pm:GetCurrentProject()
settings = proj:GetSetting()
local ui = app.UIManager
local disp = bmd.UIDispatcher(ui)
local width,height = 500,270

--proj:SetSetting('videoMonitorFormat', value)
function _monitorformat()
	currentformat = "'"..itm.videoformat.CurrentText.."'"
	print(currentformat)
	currentformattext = "proj:SetSetting('videoMonitorFormat', "..currentformat..')\n'
end

--proj:SetSetting('videoMonitorUse444SDI', use444)
function _sdi444()
	 print('[Checkbox] ' .. tostring(itm.sdi444.Checked))
	 local sdi444check = itm.sdi444.Checked
	 if sdi444check == true then
	 	use444 = "'"..'1'.."'"
	 	print(use444)
	 else
		use444 = "'"..'0'.."'"
	 	print(use444)
	 end
	print(use444)
	currentsdi444text = "proj:SetSetting('videoMonitorUse444SDI', "..use444..')\n'
end

function _stereosdi()
	 print('[Checkbox] ' .. tostring(itm.stereosdi.Checked))
	 local stereosdicheck = itm.stereosdi.Checked
	 if stereosdicheck == true then
	 	dualsdi = "'"..'1'.."'"
	 	print(dualsdi)
	 else
	    dualsdi = "'"..'0'.."'"
	 	print(dualsdi)
	 end
	print(dualsdi)
	currentstereosditext = "proj:SetSetting('videoMonitorUseStereoSDI', "..dualsdi..')\n'
end

--proj:SetSetting('videoMonitorSDIConfiguration', sdilink)
function _sdilink()
	currentsdilink = "'"..itm.sdilink.CurrentText.."'"
	print(currentsdilink)
	currentsdilinktext = "proj:SetSetting('videoMonitorSDIConfiguration', "..currentsdilink..')\n'
end

--proj:SetSetting('videoDataLevels', datalevel)
function _datalevel()
	currentdatalevel = "'"..itm.datalevel.CurrentText.."'"
	print(currentdatalevel)
	currentdataleveltext = "proj:SetSetting('videoDataLevels', "..currentdatalevel..')\n'
end

--proj:SetSetting('videoMonitorBitDepth', bitdepth)
function _bitdepth()
	currentbitdepth = "'"..itm.bitdepth.CurrentText.."'"
	print(currentbitdepth)
	currentbitdepthtext = "proj:SetSetting('videoMonitorBitDepth', "..currentbitdepth..')\n'
end

function _hdmimetadata()
	hdmimetadata = tostring(0)
	--proj:SetSetting('videoMonitorUseHDROverHDMI', hdmimetadata)
end

function _set()
	_monitorformat()
	_stereosdi()
	_sdilink()
	_sdi444()
	_datalevel()
	_bitdepth()
	script_text = head..currentformattext..currentsdi444text..currentstereosditext..currentsdilinktext..currentdataleveltext..currentbitdepthtext
end

function _export_script()
    _set()
    request_filename()
    if bad_ending == 1 then
        return
    end
    path = request_dir()
    print(path)
    if path == nil then
        return
    end
    print(script_text)
    file_name = get_filename..'.lua'
    full_path = path..file_name
    export_file = io.open(full_path, 'w')
    export_file:write(script_text)
    export_file:close()
end

function request_dir()
    selected_path = fu:RequestDir()
    return selected_path
end

function _export_name()
    get_filename = fileitm.filename_edit.Text
    print(get_filename)
    disp:ExitLoop()
    bad_ending = 0
end

function request_filename()
    request = disp:AddWindow({ 
                        WindowTitle = 'Enter Export File Name', 
                        ID = 'fileWin', 
     Geometry = {1000, 700, 450, 85},
    
     ui:VGroup
     {
       ID = 'root_request', Spacing = 10, Weight = 0,
       ui:HGroup {
       	Spacing = 10, Weight = 0,
	       ui:Label{
	         ID = 'filename_label',
	         Weight = 0,
	         Text = 'File name: ', 
	       },
	       ui:LineEdit{
	         ID = 'filename_edit',
	         Weight = 3
	       },
       },
       ui:HGroup {
       	Spacing = 10, Weight = 0,
	       ui:VGap{
	       	 Weight = 1
	       },
	       ui:Button{
	         ID = 'yes',
	         Weight = 0,
	         Text = 'Yes', 
	       },
	       ui:Button{
	         ID = 'no',
	         Weight = 0,
	         Text = 'No', 
	       },
       },
      },
   })

    fileitm = request:GetItems()

    function request.On.yes.Clicked(ev)
        _export_name()
    end

    function request.On.no.Clicked(ev)
        bad_ending = 1
        disp:ExitLoop()
    end

    function request.On.fileWin.Close(ev)
        bad_ending = 1
        disp:ExitLoop()
    end

    request:Show()
    disp:RunLoop()
    request:Hide()
end

format = {'HD 1080p 23.976', 'UHD 2160p 23.976'}
link = {'single_link', 'dual_link', 'quad_link'}
level = {'Video', 'Full'}
depth = {'8', '10', '12'}
head = 'resolve = Resolve()\npm = resolve:GetProjectManager()\nproj = pm:GetCurrentProject()\n'

 win = disp:AddWindow({
     ID = 'videomonitor',
     WindowTitle = 'Project Setting Generator',
     Geometry = {100, 100, width, height},

     ui:VGroup
     {
       ID = 'root', Spacing = 15, Weight = 0,
       -- Add your GUI elements here:
       ui:HGroup {
       	Spacing = 40, Weight = 0,
	       -- Video Format
	       ui:Label{
	         ID = 'videoformatlabel',
	         Weight = 0,
	         Text = 'Video format', 
	         Alignment = {AlignLeft = true, AlignTop = true},
	       },
	       ui:ComboBox{
	         ID = 'videoformat',
	         Weight = 1
	       },
	       ui:HGap{
	       	 Weight = 2
	       },
       },
       ui:HGroup {
       	Spacing = 50, Weight = 0,
	       -- SDI 444
	       ui:Label{
	         ID = 'sdi444label',
	         Weight = 1,
	         Text = 'Use 4:4:4 SDI', 
	         Alignment = {AlignLeft = true, AlignTop = true},
	       },
	       ui:CheckBox{
	         ID = 'sdi444',
	         Weight = 1,
	         Alignment = {AlignRight = true, AlignTop = true},
	       },
       },
       ui:HGroup {
       	Spacing = 50, Weight = 0,
	       -- Flag color
	       ui:Label{
	         ID = 'dualsdilabel',
	         Weight = 1,
	         Text = 'Use dual outputs on SDI', 
	         Alignment = {AlignLeft = true, AlignTop = true},
	       },
	       ui:CheckBox{
	         ID = 'stereosdi',
	         Weight = 1,
	         Alignment = {AlignRight = true, AlignTop = true},
	       },
       },
       ui:HGroup {
       	Spacing = 15, Weight = 0,
	       -- SDI Link
	       ui:Label{
	         ID = 'sdiconfig',
	         Weight = 0,
	         Text = 'SDI configuration', 
	         Alignment = {AlignLeft = true, AlignTop = true},
	       },
	       ui:ComboBox{
	         ID = 'sdilink',
	         Weight = 1
	       },
	       ui:HGap{
	       	 Weight = 2
	       },
       },
       ui:HGroup {
       	Spacing = 50, Weight = 0,
	       -- Data Level
	       ui:Label{
	         ID = 'datalevellabel',
	         Weight = 0,
	         Text = 'Data levels', 
	         Alignment = {AlignLeft = true, AlignTop = true},
	       },
	       ui:ComboBox{
	         ID = 'datalevel',
	         Weight = 1
	       },
	       ui:HGap{
	       	 Weight = 2
	       },
       },
       ui:HGroup {
       	Spacing = 25, Weight = 0,
	       -- Bit Depth
	       ui:Label{
	         ID = 'bitdepthlabel',
	         Weight = 0,
	         Text = 'Video bit depth', 
	         Alignment = {AlignLeft = true, AlignTop = true},
	       },
	       ui:ComboBox{
	         ID = 'bitdepth',
	         Weight = 0
	       },
	       ui:HGap{
	       	 Weight = 2
	       },
       },
       ui:HGroup {
       	Spacing = 25, Weight = 0,
       ui:HGap{ weight = 0},
       -- button
       ui:Button { Text = "Generate", ID = "Generate", Weight = 0 },
       },
      },
   })

   itm = win:GetItems()
   itm.videoformat:AddItems(format)
   itm.sdilink:AddItems(link)
   itm.datalevel:AddItems(level)
   itm.bitdepth:AddItems(depth)

   function win.On.Generate.Clicked(ev)
      _export_script()
   end

    -- The window was closed
   function win.On.videomonitor.Close(ev)
      disp:ExitLoop()
   end

   win:Show()
   disp:RunLoop()
   win:Hide()
