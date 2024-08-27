# Video Trimmer GUI

Video Trimmer GUI is a simple application that allows users to trim video files using a graphical interface. It leverages FFmpeg for video processing and provides an easy-to-use interface for selecting start and end times for video trimming.

## Version

Current version: 0.1

## Requirements

- Python 3.7+
- wxPython 4.2.0+
- OpenCV-Python 4.7.0+
- FFmpeg (standalone executable)

## Installation

1. Clone this repository or download the source code.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Place a standalone `ffmpeg.exe` in the same directory as the main script.

## Basic Workflow

1. **Select File**: Click the "Select Video" button to choose the video file you want to trim.

2. **Preview**: Use the slider to control the preview window. The video frame at the selected time will be displayed.

3. **Set Start and End Times**: When you find the content you want to use as the start or end time in the preview window, use the relevant "Set Start Time" or "Set End Time" button to mark the time.

4. **Generate Trimming Command**: Once both start and end times are selected, the trimming command will be automatically generated.

5. **Execute Trimming**:
   - For a single video file: Use the "Run Command" button to execute the trimming operation.
   - For multiple files: Use the batch interface to schedule multiple trimming commands that should be processed.

## Limitations

- The application requires a standalone `ffmpeg.exe` to be placed in the same directory as the program.
- The preview functionality may be slower for high-resolution videos.
- The application currently supports a limited number of video formats. Check the supported extensions in the file selection dialog.
- Batch processing is sequential and may take a long time for multiple large video files.

## Language Support

The application supports English and Traditional Chinese (繁體中文). You can switch languages from the menu bar.

## Contributing

Contributions to improve Video Trimmer GUI are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). To view a copy of this license, visit https://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

Copyright (c) 2023 kuarcis

You are free to use, share, and adapt this work for non-commercial purposes, as long as you give appropriate credit to kuarcis and indicate if changes were made. For commercial use, please contact the author for permission.
