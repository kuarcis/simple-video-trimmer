# Video Trimmer GUI
<img width="30%" alt="screenshot" src="https://github.com/user-attachments/assets/a36b95c4-b65a-41c7-9152-238986125288">

Video Trimmer GUI is a simple application that allows users to trim video files using a graphical interface. It leverages FFmpeg for video processing and provides an easy-to-use interface for selecting start and end times for video trimming.

## Version

Current version: 0.2

## Requirements


- Python 3.7+
- wxPython 4.2.0+
- ffmpeg-python
- FFmpeg, FFprobe, and FFplay executables

## Installation

1. Clone this repository or download the source code.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Place the FFmpeg, FFprobe, and FFplay executables in the same directory as the main script.

## Basic Workflow

1. **Select File**: Click the "Select Video" button to choose the video file you want to trim.

2. **Preview**: Use the "Toggle Preview" button to open/close the preview window. The slider controls the current time position.

3. **Set Start and End Times**: When you find the content you want to use as the start or end time, use the relevant "Set Start Time" or "Set End Time" button to mark the time.

4. **Generate Trimming Command**: Once both start and end times are selected, the trimming command will be automatically generated.

5. **Execute Trimming**:
   - For a single video file: Use the "Run Command" button to execute the trimming operation.
   - For multiple files: Use the "Add Command to Batch" button to add the current command to the batch list, then use "Run Batch" to process all commands.

## Features

- Live preview of video frames
- Precise time selection using a custom slider
- Batch processing for multiple trimming operations
- Multi-language support (English and Traditional Chinese)

## Supported File Formats

The supported file formats are determined by FFmpeg's capabilities. This includes a wide range of video formats such as MP4, AVI, MOV, MKV, and many others.

## Language Support

The application supports English and Traditional Chinese (繁體中文). You can switch languages from the Language menu in the menu bar.

## Limitations

- The application requires FFmpeg, FFprobe, and FFplay executables to be placed in the same directory as the program.

## Contributing

Contributions to improve Video Trimmer GUI are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). To view a copy of this license, visit https://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

Copyright (c) 2024 kuarcis

You are free to use, share, and adapt this work for non-commercial purposes, as long as you give appropriate credit to kuarcis and indicate if changes were made. For commercial use, please contact the author for permission.
