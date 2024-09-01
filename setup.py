from cx_Freeze import setup, Executable
import os

assert os.path.isfile("C:\\Users\\PC\\Documents\\Projects\\youtube_converter\\main.py"), "Python script not found!"
assert os.path.isfile("C:\\Users\\PC\\Documents\\Projects\\youtube_converter\\icon.ico"), "Icon file not found!"

additional_files = [("ffmpeg.exe", "ffmpeg.exe"), ("ffprobe.exe", "ffprobe.exe")]

base = None
if os.name == 'nt':
    base = "Console" 

executables = [
    Executable(
        "C:\\Users\\PC\\Documents\\Projects\\youtube_converter\\main.py", 
        base=base,
        icon="C:\\Users\\PC\\Documents\\Projects\\youtube_converter\\icon.ico")
]

setup(
    name="youtube_converter",
    version="1.0",
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
