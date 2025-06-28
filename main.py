import sys
import os
import re
import time
import shutil
import yt_dlp as ytdlp
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

console = Console()

# Handle pydub import with Python 3.13 compatibility
try:
    from pydub import AudioSegment
except ImportError as e:
    if "audioop" in str(e) or "pyaudioop" in str(e):
        # For Python 3.13+, we'll use ffmpeg directly instead of pydub
        AudioSegment = None
        console.print("[yellow]Warning: pydub not fully compatible with Python 3.13. Using ffmpeg directly for audio conversion.[/yellow]")
    else:
        raise e

os.system("mode con: cols=125")  

# Progress hook class for yt-dlp
class ProgressHook:
    def __init__(self, progress, task_id):
        self.progress = progress
        self.task_id = task_id
        self.last_update = 0
        
    def __call__(self, d):
        if d['status'] == 'downloading':
            # Update progress bar
            if 'total_bytes' in d and d['total_bytes']:
                downloaded = d.get('downloaded_bytes', 0)
                total = d['total_bytes']
                percentage = (downloaded / total) * 100
                
                # Update every 0.5 seconds to avoid spam
                current_time = time.time()
                if current_time - self.last_update >= 0.5:
                    self.progress.update(self.task_id, completed=percentage, total=100)
                    self.last_update = current_time
                    
        elif d['status'] == 'finished':
            self.progress.update(self.task_id, completed=100, total=100)
            self.progress.update(self.task_id, description="[green]Download completed![/green]")

def get_resource_path(resource_name):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, resource_name)

# Try different possible ffmpeg paths
def find_ffmpeg():
    if getattr(sys, 'frozen', False):
        # When frozen (executable), ffmpeg files are in the same directory as the exe
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
        ffprobe_path = os.path.join(base_path, 'ffprobe.exe')
    else:
        # When running from source, first check root directory, then nested directory
        base_path = os.path.dirname(__file__)
        
        # First try root directory
        ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
        ffprobe_path = os.path.join(base_path, 'ffprobe.exe')
        
        # If not found in root, try nested directory
        if not os.path.exists(ffmpeg_path):
            ffmpeg_path = os.path.join(base_path, 'ffmpeg-master-latest-win64-gpl-shared', 'bin', 'ffmpeg.exe')
            ffprobe_path = os.path.join(base_path, 'ffmpeg-master-latest-win64-gpl-shared', 'bin', 'ffprobe.exe')
    
    # Verify the files exist
    if not os.path.exists(ffmpeg_path):
        console.print(f"[bold red]Error: FFmpeg not found at {ffmpeg_path}[/bold red]")
        return None, None
    if not os.path.exists(ffprobe_path):
        console.print(f"[bold red]Error: FFprobe not found at {ffprobe_path}[/bold red]")
        return None, None
    
    console.print(f"[green]Found FFmpeg at: {ffmpeg_path}[/green]")
    console.print(f"[green]Found FFprobe at: {ffprobe_path}[/green]")
    
    return ffmpeg_path, ffprobe_path

ffmpeg_path, ffprobe_path = find_ffmpeg()

if AudioSegment is not None and ffmpeg_path and ffprobe_path:
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.avconv = ffmpeg_path
    if hasattr(AudioSegment, 'ffprobe'):
        AudioSegment.ffprobe = ffprobe_path

home = os.path.expanduser("~")
download_path = os.path.join(home, "Downloads")

def sanitize_filename(filename):
    # Check if filename contains non-English characters (including Korean, Chinese, etc.)
    # This regex matches any character that's not a basic Latin letter, digit, or common punctuation
    if re.search(r'[^\x00-\x7F]', filename):
        # If it contains non-ASCII characters, use timestamp format
        from datetime import datetime
        timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        return f"YouTubeConvertedFile_{timestamp}"
    else:
        # If it's ASCII-only, just remove Windows-invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Remove extra whitespace and replace with single space
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        # Limit length to avoid path issues
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized

def conv_MP3():
    import subprocess
    
    # Check if ffmpeg is available
    if not ffmpeg_path:
        console.print("[bold red]Error: FFmpeg not found. Cannot convert to MP3.[/bold red]")
        return options_()
    
    while True:
        link = console.input("[bold green]link: ")
        if link.startswith("https://www.youtube.com/watch?v=") or link.startswith("https://youtu.be/"):
            # Extract just the video ID to avoid playlist downloads
            if "&list=" in link:
                # Remove playlist parameters
                video_id = link.split("&list=")[0]
                console.print(f"[yellow]Extracting video from playlist: {video_id}[/yellow]")
            else:
                video_id = link
            
            # Create progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                # Create task for download
                task = progress.add_task("[cyan]Downloading...", total=100)
                progress_hook = ProgressHook(progress, task)
                
                options = {
                    'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio/best',
                    'outtmpl': os.path.join(download_path, "%(title)s.%(ext)s"),
                    'compat_opts': ['filename-sanitization'],
                    'noplaylist': True,
                    'ffmpeg_location': ffmpeg_path,
                    'ffprobe_location': ffprobe_path,
                    'no_warnings': True,
                    'quiet': True,
                    'progress_hooks': [progress_hook]
                }

                try:
                    console.print(f"[yellow]Using FFmpeg at: {ffmpeg_path}[/yellow]")
                    console.print(f"[yellow]Using FFprobe at: {ffprobe_path}[/yellow]")
                    with ytdlp.YoutubeDL(options) as ydl:
                        info_dict = ydl.extract_info(video_id, download=False)
                        video_title = info_dict.get('title', 'Unknown Title')

                        sanitized_title = sanitize_filename(video_title)
                        
                        # Update task description with video title
                        progress.update(task, description=f"[cyan]Downloading: {sanitized_title[:50]}...")

                        # Download the file
                        ydl.download([video_id])
                        
                        # Look for the downloaded file more robustly
                        downloaded_file = None
                        possible_extensions = ['.webm', '.mp4', '.m4a', '.opus']
                        
                        # First try exact match with sanitized title
                        for ext in possible_extensions:
                            test_path = os.path.join(download_path, f"{sanitized_title}{ext}")
                            if os.path.exists(test_path):
                                downloaded_file = test_path
                                break
                        
                        # If not found, search for files containing the sanitized title
                        if not downloaded_file:
                            for file in os.listdir(download_path):
                                file_path = os.path.join(download_path, file)
                                if os.path.isfile(file_path):
                                    file_lower = file.lower()
                                    title_lower = sanitized_title.lower()
                                    # Check if file contains the title and has a valid extension
                                    if any(file_lower.endswith(ext) for ext in possible_extensions) and title_lower in file_lower:
                                        downloaded_file = file_path
                                        break
                        
                        # If still not found, try to find the most recent file with valid extension
                        if not downloaded_file:
                            recent_files = []
                            for file in os.listdir(download_path):
                                file_path = os.path.join(download_path, file)
                                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in possible_extensions):
                                    recent_files.append((file_path, os.path.getctime(file_path)))
                            
                            if recent_files:
                                # Sort by creation time (most recent first)
                                recent_files.sort(key=lambda x: x[1], reverse=True)
                                downloaded_file = recent_files[0][0]
                                console.print(f"[yellow]Using most recent downloaded file: {os.path.basename(downloaded_file)}[/yellow]")
                        
                        if downloaded_file:
                            # Create a safe filename for the MP3 output
                            safe_filename = sanitize_filename(video_title)
                            mp3_file_path = os.path.join(download_path, f"{safe_filename}.mp3")
                            
                            # Check if MP3 already exists
                            if os.path.exists(mp3_file_path):
                                console.print(f"[yellow]MP3 file already exists: {mp3_file_path}[/yellow]")
                                stat = os.stat(mp3_file_path)
                            else:
                                # Add conversion progress task
                                conv_task = progress.add_task("[blue]Converting to MP3...", total=100)
                                progress.update(conv_task, completed=0)
                                
                                console.print(f"[blue]Converting {os.path.basename(downloaded_file)} to MP3...[/blue]")
                                result = subprocess.run([
                                    ffmpeg_path, '-i', downloaded_file, 
                                    '-acodec', 'libmp3lame', '-ab', '192k', 
                                    mp3_file_path, '-y'
                                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                                
                                # Update conversion progress
                                progress.update(conv_task, completed=100)
                                
                                # Check if MP3 was created and is nonzero size
                                if os.path.exists(mp3_file_path) and os.path.getsize(mp3_file_path) > 0:
                                    os.remove(downloaded_file)  # Remove original file
                                    # Set creation and modification time to now
                                    now = time.time()
                                    os.utime(mp3_file_path, (now, now))
                                    stat = os.stat(mp3_file_path)
                                else:
                                    console.print(f"[yellow]FFmpeg conversion failed, using fallback method...[/yellow]")
                                    console.print(f"[yellow]FFmpeg stdout: {result.stdout}[/yellow]")
                                    console.print(f"[yellow]FFmpeg return code: {result.returncode}[/yellow]")
                                    
                                    # If ffmpeg fails, check if the downloaded file is already an audio file
                                    file_ext = os.path.splitext(downloaded_file)[1].lower()
                                    if file_ext in ['.m4a', '.mp3', '.aac', '.ogg', '.wav']:
                                        # Rename the audio file to .mp3
                                        mp3_file_path = os.path.splitext(downloaded_file)[0] + '.mp3'
                                        os.rename(downloaded_file, mp3_file_path)
                                        console.print(f"[green]Successfully converted to MP3: {os.path.basename(mp3_file_path)}[/green]")
                                        
                                        # Update file timestamps to current time
                                        now = time.time()
                                        os.utime(mp3_file_path, (now, now))
                                        stat = os.stat(mp3_file_path)
                                    else:
                                        console.print(f"[yellow]Original file kept at: {downloaded_file}[/yellow]")
                                        continue
                            
                            console.print()
                            panel_content = f"[bold green]Title:[/bold green]\t\t\t{sanitized_title}\n"
                            panel_content += f"[bold blue]DOWNLOADED:[/bold blue]\t\t{sanitized_title}\n"
                            panel_content += f"[bold green]Creation time:[/bold green]\t\t{time.ctime(stat.st_ctime)}\n"
                            panel_content += f"[bold green]Modification time:[/bold green]\t{time.ctime(stat.st_mtime)}\n"
                            panel_content += f"[bold green]Path:[/bold green] {mp3_file_path}\n"

                            console.print(Panel.fit(panel_content, title="DOWNLOAD INFO", style="bold cyan"))
                        else:
                            console.print(f"[bold red]Error:[/bold red] Downloaded file not found. Check Downloads folder for: {sanitized_title}")

                except Exception as e:
                    console.print(f"[bold red]An error occurred:[/bold red] {e}")

            main()
        
        elif link == '0':
            return options_()
            
        else:
            console.print("[bold red]Invalid link[/bold red]")
            continue

def conv_MP4():
    import subprocess
    
    # Check if ffmpeg is available
    if not ffmpeg_path:
        console.print("[bold red]Error: FFmpeg not found. Cannot convert to MP4.[/bold red]")
        return options_()
    
    while True:
        link = console.input("[bold green]link: ")
        if link.startswith("https://www.youtube.com/watch?v=") or link.startswith("https://youtu.be/"):
            # Extract just the video ID to avoid playlist downloads
            if "&list=" in link:
                # Remove playlist parameters
                video_id = link.split("&list=")[0]
                console.print(f"[yellow]Extracting video from playlist: {video_id}[/yellow]")
            else:
                video_id = link
            
            # Create progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                # Create task for download
                task = progress.add_task("[cyan]Downloading...", total=100)
                progress_hook = ProgressHook(progress, task)
                
                options = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': os.path.join(download_path, "%(title)s.%(ext)s"),
                    'compat_opts': ['filename-sanitization'],
                    'noplaylist': True,
                    'ffmpeg_location': ffmpeg_path,
                    'ffprobe_location': ffprobe_path,
                    'no_warnings': True,
                    'quiet': True,
                    'progress_hooks': [progress_hook]
                }

                try:
                    console.print(f"[yellow]Using FFmpeg at: {ffmpeg_path}[/yellow]")
                    console.print(f"[yellow]Using FFprobe at: {ffprobe_path}[/yellow]")
                    with ytdlp.YoutubeDL(options) as ydl:
                        info_dict = ydl.extract_info(video_id, download=False)
                        video_title = info_dict.get('title', 'Unknown Title')
                        sanitized_title = sanitize_filename(video_title)
                        
                        # Update task description with video title
                        progress.update(task, description=f"[cyan]Downloading: {sanitized_title[:50]}...")
                        
                        # Download the file
                        ydl.download([video_id])
                        
                        # Look for the downloaded MP4 file more robustly
                        video_file_path = None
                        
                        # First try exact match with sanitized title
                        safe_filename = sanitize_filename(video_title)
                        exact_path = os.path.join(download_path, f"{safe_filename}.mp4")
                        if os.path.exists(exact_path):
                            video_file_path = exact_path
                        else:
                            # Search for files containing the title
                            for file in os.listdir(download_path):
                                file_path = os.path.join(download_path, file)
                                if os.path.isfile(file_path) and file.lower().endswith('.mp4'):
                                    file_lower = file.lower()
                                    title_lower = video_title.lower()
                                    if title_lower in file_lower:
                                        video_file_path = file_path
                                        break
                            
                            # If still not found, use most recent MP4 file
                            if not video_file_path:
                                recent_mp4_files = []
                                for file in os.listdir(download_path):
                                    file_path = os.path.join(download_path, file)
                                    if os.path.isfile(file_path) and file.lower().endswith('.mp4'):
                                        recent_mp4_files.append((file_path, os.path.getctime(file_path)))
                                
                                if recent_mp4_files:
                                    recent_mp4_files.sort(key=lambda x: x[1], reverse=True)
                                    video_file_path = recent_mp4_files[0][0]
                                    console.print(f"[yellow]Using most recent MP4 file: {os.path.basename(video_file_path)}[/yellow]")

                        if video_file_path and os.path.exists(video_file_path):
                            # Add processing task
                            proc_task = progress.add_task("[blue]Processing file...", total=100)
                            progress.update(proc_task, completed=50)
                            
                            # Copy file to update timestamps
                            temp_file_path = video_file_path + "_temp"
                            with open(video_file_path, "rb") as src_file:
                                with open(temp_file_path, "wb") as dst_file:
                                    shutil.copyfileobj(src_file, dst_file)

                            os.remove(video_file_path)
                            os.rename(temp_file_path, video_file_path)

                            current_time = time.time()
                            os.utime(video_file_path, (current_time, current_time))
                            
                            progress.update(proc_task, completed=100)

                            stat = os.stat(video_file_path)
                            console.print()
                            console.print(Panel.fit(
                                f"[bold green]Title:[/bold green]\t\t\t{safe_filename}\n"
                                f"[bold blue]DOWNLOADED:[/bold blue]\t\t{safe_filename}\n"
                                f"[bold green]Creation time:[/bold green]\t\t{time.ctime(stat.st_ctime)}\n"
                                f"[bold green]Modification time:[/bold green]\t{time.ctime(stat.st_mtime)}\n"
                                f"[bold green]Path:[/bold green] {video_file_path}\n",
                                title="DOWNLOAD INFO", style="bold cyan"
                            ))
                        else:
                            console.print(f"[bold red]Error:[/bold red] Video file not found. Check Downloads folder for MP4 files.")

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