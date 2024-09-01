import sys
import os
import re
import time
import shutil
import yt_dlp as ytdlp
from pydub import AudioSegment
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

console = Console()

os.system("mode con: cols=125")  

def get_resource_path(resource_name):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)

    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, resource_name)

ffmpeg_path = get_resource_path('ffmpeg.exe')
ffprobe_path = get_resource_path('ffprobe.exe')

AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.avconv = ffmpeg_path
if hasattr(AudioSegment, 'ffprobe'):
    AudioSegment.ffprobe = ffprobe_path

home = os.path.expanduser("~")
download_path = os.path.join(home, "Downloads")

def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    return sanitized

def conv_MP3():
    while True:
        link = console.input("[bold green]link: ")
        if link.startswith("https://www.youtube.com/watch?v=") or link.startswith("https://youtu.be/"):
            options = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_path, "%(title)s.%(ext)s"),
                'compat_opts': ['filename-sanitization']
            }

            try:
                with ytdlp.YoutubeDL(options) as ydl:
                    info_dict = ydl.extract_info(link, download=False)
                    video_title = info_dict.get('title', 'Unknown Title')

                    sanitized_title = sanitize_filename(video_title)

                    audio_file_path = os.path.join(download_path, f"{sanitized_title}.webm")
                    
                    ydl.download([link])
                    
                    mp3_file_path = os.path.splitext(audio_file_path)[0] + ".mp3"

                    if os.path.exists(audio_file_path):
                        audio = AudioSegment.from_file(audio_file_path, format="webm")
                        audio.export(mp3_file_path, format="mp3")

                        os.remove(audio_file_path)
                        
                        stat = os.stat(mp3_file_path)
                        
                        console.print()
                        panel_content = f"[bold green]Title:[/bold green]\t\t\t{sanitized_title}\n"
                        panel_content += f"[bold blue]DOWNLOADED:[/bold blue]\t\t{sanitized_title}\n"
                        panel_content += f"[bold green]Creation time:[/bold green]\t\t{time.ctime(stat.st_ctime)}\n"
                        panel_content += f"[bold green]Modification time:[/bold green]\t{time.ctime(stat.st_mtime)}\n"
                        panel_content += f"[bold green]Path:[/bold green] {mp3_file_path}\n"

                        console.print(Panel.fit(panel_content, title="DOWNLOAD INFO", style="bold cyan"
                        ))

                    else:
                        console.print(f"[bold red]Error:[/bold red] Audio file not found at {audio_file_path}")

            except Exception as e:
                console.print(f"[bold red]An error occurred:[/bold red] {e}")

            main()
        
        elif link == '0':
            return options_()
            
        else:
            console.print("[bold red]Invalid link[/bold red]")
            continue

def conv_MP4():
    while True:
        link = console.input("[bold green]link: ")
        if link.startswith("https://www.youtube.com/watch?v=") or link.startswith("https://youtu.be/"):
            options = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(download_path, "%(title)s.%(ext)s"),
                'merge_output_format': 'mp4',
                'compat_opts': ['filename-sanitization']  
            }

            try:
                with ytdlp.YoutubeDL(options) as ydl:
                    info_dict = ydl.extract_info(link, download=True)
                    video_title = sanitize_filename(info_dict.get('title', 'Unknown Title'))
                    video_file_path = os.path.join(download_path, f"{video_title}.mp4")

                    if os.path.exists(video_file_path):
                        temp_file_path = video_file_path + "_temp"
                        with open(video_file_path, "rb") as src_file:
                            with open(temp_file_path, "wb") as dst_file:
                                shutil.copyfileobj(src_file, dst_file)

                        os.remove(video_file_path)

                        os.rename(temp_file_path, video_file_path)

                        current_time = time.time()
                        os.utime(video_file_path, (current_time, current_time))

                        stat = os.stat(video_file_path)
                        console.print()
                        console.print(Panel.fit(
                            f"[bold green]Title:[/bold green]\t\t\t{video_title}\n"
                            f"[bold blue]DOWNLOADED:[/bold blue]\t\t{video_title}\n"
                            f"[bold green]Creation time:[/bold green]\t\t{time.ctime(stat.st_ctime)}\n"
                            f"[bold green]Modification time:[/bold green]\t{time.ctime(stat.st_mtime)}\n"
                            f"[bold green]Path:[/bold green] {video_file_path}\n",
                            title="DOWNLOAD INFO", style="bold cyan"
                        ))
                    else:
                        console.print(f"[bold red]Error:[/bold red] Video file not found at {video_file_path}")

            except Exception as e:
                console.print(f"[bold red]An error occurred:[/bold red] {e}")

            main()
        
        elif link == '0':
            return options_()
            
        else:
            console.print("[bold red]Invalid link[/bold red]")
            continue
        
def info():
    console.print(Panel.fit(
        "[bold green]Facebook: \t\t[bold blue]Tonyo Tecson\n"
        "[bold green]GitHub: \t\t[bold blue]SymbioSymbioSymbio (Mordical62645)\n"
        "[bold green]SoundCloud: \t\t[bold blue]Symbio (Marco Tecson)\n"
        "[bold green]YouTube: \t\t[bold blue]SymbioSymbioo[Djinno Studios]\n"
        "\n"
        "[bold cyan]Accepting donations (I'm broke. I'm basically eating only peanuts to live T^T):\n"
        "[bold green]Buy me a coffee? \t[bold blue][link=https://ko-fi.com/symbiotonyo]https://ko-fi.com/symbiotonyo[/link]\n"
        "[bold green]Other methods: \t\t[bold blue][link=https://ko-fi.com/i/IZ8Z812EG6M]https://ko-fi.com/i/IZ8Z812EG6M[/link]\n",

        title="HIT ME UP!", style="bold cyan"
    ))

    while True:
        choice = console.input("[bold green]Enter 0 to go back to the main menu: ")
        if choice == "0":
            main()
            break
        else:
            console.print("[bold red]Invalid input. Please enter 0 to go back to the main menu.[/bold red]")
    
def main():
    console.print()
    console.print(Panel.fit(
        "[bold white] __ __   ___   __ __  ______  __ __  ____     ___         __   ___   ____   __ __    ___  ____  ______    ___  ____  \n"
        "|  T  T /   \\ |  T  T|      T|  T  T|    \\   /  _]       /  ] /   \\ |    \\ |  T  |  /  _]|    \\|      T  /  _]|    \\ \n"
        "|  |  |Y     Y|  |  ||      ||  |  ||  o  ) /  [_       /  / Y     Y|  _  Y|  |  | /  [_ |  D  )      | /  [_ |  D  )\n"
        "|  ~  ||  O  ||  |  |l_j  l_j|  |  ||     TY    _]     /  /  |  O  ||  |  ||  |  |Y    _]|    /l_j  l_jY    _]|    / \n"
        "l___, ||     ||  :  |  |  |  |  :  ||  O  ||   [_     /   \\_ |     ||  |  |l  :  !|   [_ |    \\  |  |  |   [_ |    \\ \n"
        "|     !l     !l     |  |  |  l     ||     ||     T    \\     |l     !|  |  | \\   / |     T|  .  Y |  |  |     T|  .  Y\n"
        "l____/  \\___/  \\__,_j  l__j   \\__,_jl_____jl_____j     \\____j \\___/ l__j__j  \\_/  l_____jl__j\\_j l__j  l_____jl__j\\_j\n"
        "\n"
        "-by yours truly: [bold blue]Symbio (Marco Tecson)",
        
        title="MAIN MENU", style="bold red"
    ))    
    options_()  

def options_():
    console.print()
    console.print(Panel.fit(
        "[bold green][1]: Convert to MP3\n"
        "[bold green][2]: Convert to MP4\n"
        "[bold green][3]: Info\n"
        "[bold red][0]: Return or Quit",
        title="OPTIONS", style="bold cyan"
    ))
    while True:
        user_input = console.input("[bold green]Enter your choice: ")
        if user_input == "1":
            conv_MP3()
        elif user_input == "2":
            conv_MP4()
        elif user_input == "3":
            info()
        elif user_input == "0":
            sys.exit()
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

if __name__ == "__main__":
    main()
