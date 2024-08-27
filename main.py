import wx
import os
import subprocess
import time
import cv2
import locale
from locales import setup_locales, translate

VERSION = "0.1"

class SmoothSlider(wx.Panel):
    def __init__(self, parent, value=0, min_val=0, max_val=100):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.dragging = False

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        dc.SetBrush(wx.Brush(wx.LIGHT_GREY))
        dc.DrawRectangle(0, 0, self.GetSize().width, self.GetSize().height)
        dc.SetBrush(wx.Brush(wx.BLUE))
        width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.GetSize().width)
        dc.DrawRectangle(0, 0, width, self.GetSize().height)
        
        # Draw indicator
        indicator_pos = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.GetSize().width)
        dc.SetBrush(wx.Brush(wx.RED))
        dc.DrawCircle(indicator_pos, self.GetSize().height // 2, 5)

    def OnLeftDown(self, event):
        self.dragging = True
        self.CaptureMouse()
        self.OnMotion(event)

    def OnLeftUp(self, event):
        self.dragging = False
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMotion(self, event):
        if self.dragging:
            width = self.GetSize().width
            pos = event.GetPosition().x
            self.value = self.min_val + (self.max_val - self.min_val) * (pos / width)
            self.value = max(self.min_val, min(self.max_val, self.value))
            self.Refresh()
            wx.PostEvent(self, wx.PyCommandEvent(wx.EVT_SLIDER.typeId, self.GetId()))

    def SetValue(self, value):
        self.value = value
        self.Refresh()

    def GetValue(self):
        return self.value

class VideoTrimmerLayout(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.InitUI()

    def InitUI(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        main_sizer.Add(left_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)

    def create_left_panel(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # File selection
        file_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_video_label = wx.StaticText(panel, label=translate("Input Video:"))
        self.file_path_text = wx.TextCtrl(panel, style=wx.TE_READONLY)
        self.file_select_btn = wx.Button(panel, label=translate("Select Video"))
        file_select_sizer.Add(self.input_video_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        file_select_sizer.Add(self.file_path_text, 1, wx.EXPAND | wx.RIGHT, 5)
        file_select_sizer.Add(self.file_select_btn, 0)
        sizer.Add(file_select_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Output folder selection
        folder_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output_folder_label = wx.StaticText(panel, label=translate("Output Folder:"))
        self.output_folder_text = wx.TextCtrl(panel, style=wx.TE_READONLY)
        self.output_folder_btn = wx.Button(panel, label=translate("Select Folder"))
        folder_select_sizer.Add(self.output_folder_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        folder_select_sizer.Add(self.output_folder_text, 1, wx.EXPAND | wx.RIGHT, 5)
        folder_select_sizer.Add(self.output_folder_btn, 0)
        sizer.Add(folder_select_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Time slider and current time display
        slider_sizer = wx.BoxSizer(wx.VERTICAL)
        self.time_slider = SmoothSlider(panel, min_val=0, max_val=1000000)  # Changed to milliseconds
        self.time_slider.SetMinSize((300, 30))  # Set a minimum size for the slider
        slider_sizer.Add(self.time_slider, 0, wx.EXPAND | wx.ALL, 5)
        self.current_time_text = wx.StaticText(panel, label="00:00:00.000")
        slider_sizer.Add(self.current_time_text, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(slider_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Video duration display
        self.video_duration_text = wx.StaticText(panel, label=f"{translate('Source File Total Time:')} 00:00:00.000")
        sizer.Add(self.video_duration_text, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Preview button
        self.preview_btn = wx.Button(panel, label=translate("Preview at Selected Time"))
        sizer.Add(self.preview_btn, 0, wx.EXPAND | wx.ALL, 5)

        # Start and End time controls
        for label, attr in [("Start Time:", "start"), ("End Time:", "end")]:
            time_sizer = wx.BoxSizer(wx.HORIZONTAL)
            setattr(self, f"{attr}_time_label", wx.StaticText(panel, label=translate(label)))
            time_sizer.Add(getattr(self, f"{attr}_time_label"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            setattr(self, f"{attr}_time_text", wx.TextCtrl(panel))
            time_sizer.Add(getattr(self, f"{attr}_time_text"), 1, wx.EXPAND)
            setattr(self, f"{attr}_time_btn", wx.Button(panel, label=translate(f"Set {attr.capitalize()} Time")))
            time_sizer.Add(getattr(self, f"{attr}_time_btn"), 0, wx.LEFT, 5)
            sizer.Add(time_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Output file name
        output_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output_file_label = wx.StaticText(panel, label=translate("Output File Name:"))
        self.output_file_name_text = wx.TextCtrl(panel)
        output_name_sizer.Add(self.output_file_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        output_name_sizer.Add(self.output_file_name_text, 1, wx.EXPAND)
        sizer.Add(output_name_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Command output
        self.command_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.command_text, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.run_command_btn = wx.Button(panel, label=translate("Run Command"))
        self.add_to_batch_btn = wx.Button(panel, label=translate("Add Command to Batch"))
        button_sizer.Add(self.run_command_btn, 1, wx.RIGHT, 5)
        button_sizer.Add(self.add_to_batch_btn, 1)
        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        return panel

    def create_right_panel(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Batch list
        self.batch_list = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.batch_list.InsertColumn(0, translate('Seq'), width=50)
        self.batch_list.InsertColumn(1, translate('Command'), width=250)
        self.batch_list.InsertColumn(2, translate('Status'), width=100)
        sizer.Add(self.batch_list, 1, wx.EXPAND | wx.ALL, 5)

        # Batch control buttons
        self.run_batch_btn = wx.Button(panel, label=translate("Run Batch"))
        sizer.Add(self.run_batch_btn, 0, wx.EXPAND | wx.ALL, 5)

        self.delete_batch_btn = wx.Button(panel, label=translate("Delete Selected Batch"))
        sizer.Add(self.delete_batch_btn, 0, wx.EXPAND | wx.ALL, 5)

        # Add the new Clean Up Batch button
        self.cleanup_batch_btn = wx.Button(panel, label=translate("Clean Up Completed Batch"))
        sizer.Add(self.cleanup_batch_btn, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        return panel

class VideoTrimmerGUI(wx.Frame):
    def __init__(self, *args, **kw):
        super(VideoTrimmerGUI, self).__init__(*args, **kw, size=(1200, 600))
        self.current_video = None
        self.video_duration = 0
        self.cap = None
        self.output_folder = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.current_lang = 'tw'
        global translate
        translate = setup_locales(self.current_lang.lower())

        self.InitUI()
        self.batches = []
        self.is_updating_command = False
        self.preview_window_name = "Video Preview"
        cv2.namedWindow(self.preview_window_name, cv2.WINDOW_NORMAL)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.video_extensions = [
            "*.mp4", "*.avi", "*.mov", "*.mkv", "*.flv", "*.wmv", "*.webm",
            "*.m4v", "*.mpg", "*.mpeg", "*.3gp", "*.3g2", "*.mxf", "*.raw",
            "*.vob", "*.f4v", "*.mts", "*.m2ts", "*.ts", "*.divx", "*.xvid",
            "*.ogv", "*.dv", "*.qt", "*.asf", "*.amv", "*.m2v", "*.svi",
            "*.mxg", "*.nsv", "*.f4p", "*.f4a", "*.f4b"
        ]

    def InitUI(self):
        # Menu Bar
        menubar = wx.MenuBar()
        language_menu = wx.Menu()
        
        languages = [('English', 'en'), ('繁體中文', 'tw')]
        for lang_name, lang_code in languages:
            lang_item = language_menu.Append(wx.ID_ANY, lang_name)
            self.Bind(wx.EVT_MENU, lambda evt, lc=lang_code: self.on_language_change(lc), lang_item)
        
        menubar.Append(language_menu, translate("Language"))
        self.SetMenuBar(menubar)

        # Main layout
        self.layout = VideoTrimmerLayout(self)

        # Set default paths as the output folder inside the current directory
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        self.layout.output_folder_text.SetValue(default_path)
        self.output_folder = default_path

        # Bind events
        self.layout.file_select_btn.Bind(wx.EVT_BUTTON, self.on_file_select)
        self.layout.output_folder_btn.Bind(wx.EVT_BUTTON, self.on_output_folder_select)
        self.layout.time_slider.Bind(wx.EVT_SLIDER, self.on_time_slider_change)
        self.layout.preview_btn.Bind(wx.EVT_BUTTON, self.on_preview)
        self.layout.start_time_btn.Bind(wx.EVT_BUTTON, self.on_set_start_time)
        self.layout.end_time_btn.Bind(wx.EVT_BUTTON, self.on_set_end_time)
        self.layout.output_file_name_text.Bind(wx.EVT_TEXT, self.on_output_file_name_changed)
        self.layout.run_command_btn.Bind(wx.EVT_BUTTON, self.on_run_command)
        self.layout.add_to_batch_btn.Bind(wx.EVT_BUTTON, self.on_add_to_batch)
        self.layout.run_batch_btn.Bind(wx.EVT_BUTTON, self.on_run_batch)
        self.layout.delete_batch_btn.Bind(wx.EVT_BUTTON, self.on_delete_selected_batch)
        self.layout.cleanup_batch_btn.Bind(wx.EVT_BUTTON, self.on_cleanup_batch)

        self.SetTitle(f"{translate('Video Trimmer GUI')} v{VERSION}")
        self.Centre()

    def on_language_change(self, lang_code):
        self.current_lang = lang_code
        global translate
        translate = setup_locales(self.current_lang)
        self.refresh_ui()

    def refresh_ui(self):
        # Update frame title
        self.SetTitle(f"{translate('Video Trimmer GUI')} v{VERSION}")
        
        # Update static text labels
        self.layout.input_video_label.SetLabel(translate("Input Video:"))
        self.layout.output_folder_label.SetLabel(translate("Output Folder:"))
        self.layout.start_time_label.SetLabel(translate("Start Time:"))
        self.layout.end_time_label.SetLabel(translate("End Time:"))
        self.layout.output_file_label.SetLabel(translate("Output File Name:"))
        
        # Update button labels
        self.layout.preview_btn.SetLabel(translate("Preview at Selected Time"))
        self.layout.start_time_btn.SetLabel(translate("Set Start Time"))
        self.layout.end_time_btn.SetLabel(translate("Set End Time"))
        self.layout.run_command_btn.SetLabel(translate("Run Command"))
        self.layout.add_to_batch_btn.SetLabel(translate("Add Command to Batch"))
        self.layout.run_batch_btn.SetLabel(translate("Run Batch"))
        self.layout.delete_batch_btn.SetLabel(translate("Delete Selected Batch"))
        self.layout.cleanup_batch_btn.SetLabel(translate("Clean Up Batch"))
        self.layout.file_select_btn.SetLabel(translate("Select Video"))
        self.layout.output_folder_btn.SetLabel(translate("Select Folder"))
        self.layout.video_duration_text.SetLabel(f"{translate('Source File Total Time:')} {self.format_time(self.video_duration)}")


        col_list = [translate('Seq'), translate('Command'), translate('Status')]
        for i, text in enumerate(col_list):
            obj = wx.ListItem()
            obj.SetText(text)
            self.layout.batch_list.SetColumn(i, obj)


        # Update menu
        self.GetMenuBar().SetMenuLabel(0, translate("Language"))

        # Update preview window title
        cv2.setWindowTitle(self.preview_window_name, translate("Video Preview"))

        # Refresh the layout
        self.layout.Layout()
        self.Layout()

    def on_file_select(self, event):
        wildcard = f"{translate('Video files')} ({';'.join(self.video_extensions)})|{';'.join(self.video_extensions)}"
        with wx.FileDialog(self, translate("Select a video file"), wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.current_video = fileDialog.GetPath()
            self.layout.file_path_text.SetValue(self.current_video)

        if not self.current_video:
            return

        output_filename = os.path.splitext(os.path.basename(self.current_video))[0] + "_trimmed.mp4"
        output_path = os.path.join(self.output_folder, output_filename)
        self.layout.output_file_name_text.SetValue(output_filename)
        self.cap = cv2.VideoCapture(self.current_video)
        if not self.cap.isOpened():
            wx.MessageBox(translate("Failed to open the video file."), translate("Error"), wx.OK | wx.ICON_ERROR)
            return
        self.video_duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS) * 1000)  # Convert to milliseconds
        self.layout.time_slider.SetValue(0)
        self.layout.time_slider.max_val = self.video_duration
        self.layout.command_text.SetValue("")        
        self.layout.start_time_text.SetValue("")
        self.layout.end_time_text.SetValue("")
        self.layout.current_time_text.SetLabel(self.format_time(0))
        self.layout.video_duration_text.SetLabel(f"{translate('Source File Total Time:')} {self.format_time(self.video_duration)}")
        self.show_frame(0)

    def on_output_folder_select(self, event):
        with wx.DirDialog(self, translate("Select output folder"), style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.output_folder = dirDialog.GetPath()
            self.layout.output_folder_text.SetValue(self.output_folder)
            self.update_command()

    def on_output_file_name_changed(self, event):
        wx.CallAfter(self.update_command)
        event.Skip()

    def on_preview(self, event):
        if self.cap:
            selected_time = int(self.layout.time_slider.GetValue())
            self.show_frame(selected_time)

    def on_time_slider_change(self, event):
        selected_time = int(self.layout.time_slider.GetValue())
        formatted_time = self.format_time(selected_time)
        self.layout.current_time_text.SetLabel(formatted_time)
        self.show_frame(selected_time)

    def on_set_start_time(self, event):
        start_time = int(self.layout.time_slider.GetValue())
        formatted_time = self.format_time(start_time)
        self.layout.start_time_text.SetValue(formatted_time)
        self.update_command()

    def on_set_end_time(self, event):
        end_time = int(self.layout.time_slider.GetValue())
        formatted_time = self.format_time(end_time)
        self.layout.end_time_text.SetValue(formatted_time)
        self.update_command()

    def validate_time_format(self, time_str):
        try:
            time.strptime(time_str, '%H:%M:%S.%f')
            return True
        except ValueError:
            return False

    def format_time(self, milliseconds):
        seconds, ms = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"

    def parse_time(self, time_str):
        h, m, s = time_str.split(':')
        s, ms = s.split('.')
        return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

    def show_frame(self, time_milliseconds):
        if self.cap:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.cap.set(cv2.CAP_PROP_POS_MSEC, time_milliseconds)
            ret, frame = self.cap.read()
            if ret:
                height, width, _ = frame.shape
                aspect_ratio = width / height
                window_width = 1024
                window_height = int(window_width / aspect_ratio)
                frame_resized = cv2.resize(frame, (window_width, window_height))
                cv2.imshow(self.preview_window_name, frame_resized)
                cv2.waitKey(1)

    def update_command(self):
        try:
            if self.current_video:
                start_time = self.layout.start_time_text.GetValue()
                end_time = self.layout.end_time_text.GetValue()
                
                if not start_time or not end_time:
                    self.layout.command_text.SetValue("")
                    return

                start_milliseconds = self.parse_time(start_time)
                end_milliseconds = self.parse_time(end_time)
                
                if start_milliseconds >= end_milliseconds or end_milliseconds > self.video_duration:
                    wx.MessageBox(translate("Invalid time range."), translate("Error"), wx.OK | wx.ICON_ERROR)
                    self.layout.start_time_text.SetValue("00:00:00.000")
                    self.layout.end_time_text.SetValue(self.format_time(self.video_duration))
                    self.layout.command_text.SetValue("")
                    return

                output_file = os.path.join(self.output_folder, self.layout.output_file_name_text.GetValue())
                if not any(output_file.lower().endswith(ext[1:]) for ext in self.video_extensions):
                    wx.MessageBox(translate("Invalid output file format. Please use a supported video format."), translate("Error"), wx.OK | wx.ICON_ERROR)
                    return

                if not os.path.isabs(output_file):
                    output_file = os.path.join(self.output_folder, os.path.basename(output_file))                

                command = f"ffmpeg -i \"{self.current_video}\" -ss {self.parse_time(start_time)}ms -to {self.parse_time(end_time)}ms -c copy \"{output_file}\""
                self.layout.command_text.SetValue(command)
            
        except Exception as e:
            wx.MessageBox(f"{translate('Error during command generation:')} {str(e)}", translate('Error'), wx.OK | wx.ICON_ERROR)
            return
        finally:
            return
            
    def on_run_command(self, event):
        command = self.layout.command_text.GetValue()
        if command:
            try:
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                wx.MessageBox(translate('Trimming complete!'), translate('Info'), wx.OK | wx.ICON_INFORMATION)
            except subprocess.CalledProcessError as e:
                wx.MessageBox(f"{translate('Error during trimming:')} {e.stderr}", translate('Error'), wx.OK | wx.ICON_ERROR)

    def on_add_to_batch(self, event):
        command = self.layout.command_text.GetValue()
        if command:
            self.add_batch(command)

    def add_batch(self, command):
        seq = len(self.batches) + 1
        self.batches.append({'seq': seq, 'command': command, 'status': translate('Not Run')})
        index = self.layout.batch_list.InsertItem(self.layout.batch_list.GetItemCount(), str(seq))
        self.layout.batch_list.SetItem(index, 1, command)
        self.layout.batch_list.SetItem(index, 2, translate('Not Run'))

    def on_run_batch(self, event):
        for i, batch in enumerate(self.batches):
            batch['status'] = translate('Running')
            self.layout.batch_list.SetItem(i, 2, translate('Running'))
            try:
                subprocess.run(batch['command'], shell=True, check=True)
                batch['status'] = translate('Done')
                self.layout.batch_list.SetItem(i, 2, translate('Done'))
            except subprocess.CalledProcessError:
                batch['status'] = translate('Failed')
                self.layout.batch_list.SetItem(i, 2, translate('Failed'))
            wx.Yield()

    def on_delete_selected_batch(self, event):
        selected = self.layout.batch_list.GetFirstSelected()
        while selected != -1:
            self.layout.batch_list.DeleteItem(selected)
            del self.batches[selected]
            selected = self.layout.batch_list.GetFirstSelected()

    def on_cleanup_batch(self, event):
        # Create a new list with only the non-completed items
        new_batches = [batch for batch in self.batches if batch['status'] != translate('Done')]
        
        # Clear the list control
        self.layout.batch_list.DeleteAllItems()
        
        # Repopulate the list control and update self.batches
        self.batches = []
        for i, batch in enumerate(new_batches, start=1):
            batch['seq'] = i
            self.add_batch(batch['command'])

        wx.MessageBox(translate('Completed batch items have been removed.'), translate('Info'), wx.OK | wx.ICON_INFORMATION)

    def on_close(self, event):
        cv2.destroyAllWindows()
        event.Skip()

def main():
    app = wx.App(False)
    frame = VideoTrimmerGUI(None)
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()