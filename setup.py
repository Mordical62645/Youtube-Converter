from cx_Freeze import setup, Executable
import os

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

assert os.path.isfile(os.path.join(current_dir, "main.py")), "Python script not found!"
assert os.path.isfile(os.path.join(current_dir, "icon.ico")), "Icon file not found!"

# FFmpeg files are in the ffmpeg-master-latest-win64-gpl-shared/bin directory
ffmpeg_dir = os.path.join(current_dir, "ffmpeg-master-latest-win64-gpl-shared", "bin")
additional_files = [
    (os.path.join(ffmpeg_dir, "ffmpeg.exe"), "ffmpeg.exe"), 
    (os.path.join(ffmpeg_dir, "ffprobe.exe"), "ffprobe.exe")
]

base = None
if os.name == 'nt':
    base = "Console" 

executables = [
    Executable(
        os.path.join(current_dir, "main.py"), 
        base=base,
        icon=os.path.join(current_dir, "icon.ico"))
]

setup(
    name="youtube_converter",
    version="1.5.0",
    description="Convert YouTube videos to mp3 and mp4!",
    options={
        "build_exe": {
            "includes": ["yt_dlp", "pydub"],
            "include_files": additional_files,
            "build_exe": "build_output"
        }
    },
    executables=executables
)
