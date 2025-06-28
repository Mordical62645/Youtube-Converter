# YouTube Converter

A YouTube converter made by yours truly, Symbio <3

## Features

- Download YouTube Videos 
- Convert them to MP3 or MP4
- Console-based executable
- Rich console interface with colored output
- Automatic file cleanup and timestamp management

## Prerequisites

For Windows users, the native Media Player may have compatibility issues with MP4 audio. It is highly recommended to use VLC Media Player as an alternative or as the default media player.

## Installation

### Option 1: Run from Source
1. Clone or download this repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.\.venv\Scripts\Activate.ps1`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r reqs.txt`
5. Run the application: `python main.py`

### Option 2: Build Executable
1. Follow Option 1 steps 1-4
2. Build the executable: `python setup.py build`
3. The executable will be created in the `build_output` directory
4. Run `build_output/main.exe`

## Usage

### Choose from the options:

#### [1]: Convert to MP3

- After selecting this option, paste the link of the YouTube video you wish to download.
- The video will be downloaded and automatically converted to MP3 format.
- The original downloaded file will be removed after successful conversion.

#### [2]: Convert to MP4

- After selecting this option, paste the link of the YouTube video you wish to download.
- The video will be downloaded in the best available quality and merged to MP4 format.

#### [3]: Info

- Choosing this option will show the author's social media profiles.

#### [0]: Return or Quit

- Choosing this option in OPTIONS will terminate the program.
- Choosing this option during the link input will return you to the OPTIONS menu.

## Development History & Troubleshooting

This project encountered several challenges during development that were successfully resolved:

### 1. Python Environment Issues
**Problem**: VS Code couldn't recognize the `py` command on Windows.
**Solution**: Used `python` instead of `py` for running scripts. Created a virtual environment (`.venv`) to manage dependencies properly.

### 2. Python 3.13 Compatibility Issues
**Problem**: The `pydub` library failed to import due to the removal of the `audioop` module in Python 3.13.
**Solution**: Implemented a fallback mechanism that uses ffmpeg directly when pydub is not available, ensuring compatibility with Python 3.13+.

### 3. Playlist Download Issues
**Problem**: YouTube playlist links were downloading entire playlists instead of single videos.
**Solution**: Modified the code to extract only the video ID from playlist links and added `noplaylist: True` to yt-dlp options.

### 4. Age-Restricted Video Access
**Problem**: Age-restricted videos couldn't be downloaded due to lack of authentication.
**Solution**: Initially added support for cookies.txt files, but later removed this feature per user preference to ignore age-restricted videos.

### 5. FFmpeg Path Issues
**Problem**: yt-dlp couldn't find ffmpeg for merging video and audio streams.
**Solution**: Updated the ffmpeg path to point to the correct local directory and added proper path resolution for both development and frozen executable scenarios.

### 6. Executable Build Issues
**Problem**: The setup.py file had hardcoded paths that wouldn't work on different systems.
**Solution**: Updated setup.py to use relative paths and dynamic path resolution, ensuring the executable can be built and run on any system.

### 7. FFmpeg Integration in Executable
**Problem**: When building the executable, ffmpeg files were placed in the root directory, but the code was looking for them in nested directories.
**Solution**: Implemented a `find_ffmpeg()` function that detects whether the application is running as a frozen executable or from source, and adjusts the ffmpeg path accordingly.

### 8. Git Repository Management
**Problem**: Large files and virtual environment were being tracked by Git, making the repository unnecessarily large.
**Solution**: Created a comprehensive .gitignore file and removed large files from Git tracking while keeping them in the working directory.

## Technical Details

- **Dependencies**: yt-dlp, rich, pydub (optional), ffmpeg
- **Python Version**: Compatible with Python 3.8+ (tested with Python 3.13)
- **Platform**: Windows (primary), but should work on other platforms with ffmpeg installed
- **Build Tool**: cx_Freeze for creating standalone executables

## Possible Issues

- Duplicate downloads will overwrite existing files. This may be either beneficial or problematic.
- Windows Media Player may have compatibility issues with MP4 audio (see Prerequisites for alternative media players).
- Special characters are removed from filenames during generation.
- **Age-restricted videos and audios cannot be downloaded** - YouTube requires authentication for age-restricted content, which this application does not support.
- Some YouTube videos may have signature extraction warnings, which are known YouTube-side issues and don't affect functionality.

## Support

- Facebook: Tonyo Tecson
- GitHub: Mordical62645
- SoundCloud: Symbio (Marco Tecson)
- YouTube: SymbioSymbioo [Djinno Studios]

Buy me a coffee? [Ko-fi](https://ko-fi.com/symbiotonyo)

Other methods: [Ko-fi](https://ko-fi.com/i/IZ8Z812EG6M)