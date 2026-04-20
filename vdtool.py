#!/usr/bin/env python3
"""
VDTool - Advanced Multimedia Converter & Downloader (PyQt6 Edition)
Features:
  - Video Converter with batch support
  - Audio Converter with batch support
  - Audio Extractor from videos with batch support
  - Image Converter with batch support
  - Metadata Editor/Viewer with BATCH support
  - GIF Creator with compression options
  - Media Downloader (video/audio/playlist) using yt-dlp

Dependencies: PyQt6, pillow, yt-dlp, ffmpeg (system)
"""

import sys
import os
import json
import shutil
import subprocess
import threading
import queue
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QListWidget,
    QProgressBar, QTabWidget, QFrame, QFileDialog, QMessageBox,
    QSlider, QCheckBox, QSpinBox, QGroupBox, QSplitter, QDialog,
    QRadioButton, QButtonGroup, QScrollArea, QSizePolicy, QListWidgetItem,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon


# =============================================================================
# STYLE SHEET - Modern Dark Theme
# =============================================================================
DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #3a3a5e;
    border-radius: 8px;
    margin-top: 12px;
    padding: 15px;
    background-color: #16213e;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: #00d4ff;
    font-weight: bold;
}

QPushButton {
    background-color: #0f3460;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #1a5276;
}

QPushButton:pressed {
    background-color: #0a2647;
}

QPushButton:disabled {
    background-color: #2a2a4e;
    color: #6a6a8e;
}

QPushButton#primaryButton {
    background-color: #e94560;
    font-size: 14px;
    min-height: 35px;
}

QPushButton#primaryButton:hover {
    background-color: #ff6b6b;
}

QComboBox {
    background-color: #16213e;
    border: 1px solid #3a3a5e;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #00d4ff;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    border: 1px solid #3a3a5e;
    selection-background-color: #0f3460;
}

QLineEdit, QTextEdit {
    background-color: #16213e;
    border: 1px solid #3a3a5e;
    border-radius: 6px;
    padding: 8px 12px;
    color: #eaeaea;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #00d4ff;
}

QListWidget {
    background-color: #16213e;
    border: 1px solid #3a3a5e;
    border-radius: 6px;
    padding: 5px;
}

QListWidget::item {
    padding: 6px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #0f3460;
}

QListWidget::item:hover {
    background-color: #1a3a5e;
}

QProgressBar {
    background-color: #16213e;
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560, stop:1 #00d4ff);
    border-radius: 8px;
}

QTabWidget::pane {
    border: 1px solid #3a3a5e;
    border-radius: 8px;
    background-color: #16213e;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f3460;
    color: #aaaaaa;
    padding: 12px 16px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background-color: #16213e;
    color: #00d4ff;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #1a3a5e;
}

QSlider::groove:horizontal {
    background-color: #3a3a5e;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #00d4ff;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560, stop:1 #00d4ff);
    border-radius: 3px;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #3a3a5e;
    background-color: #16213e;
}

QCheckBox::indicator:checked {
    background-color: #00d4ff;
    border-color: #00d4ff;
}

QSpinBox, QDoubleSpinBox {
    background-color: #16213e;
    border: 1px solid #3a3a5e;
    border-radius: 6px;
    padding: 6px 10px;
    color: #eaeaea;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #00d4ff;
}

QScrollBar:vertical {
    background-color: #16213e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #3a3a5e;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a4a6e;
}

QLabel#titleLabel {
    font-size: 28px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#subtitleLabel {
    font-size: 14px;
    color: #7a7a9e;
}

QLabel#statusLabel {
    color: #00d4ff;
    font-weight: bold;
}

QFrame#separator {
    background-color: #3a3a5e;
    max-height: 1px;
}
"""


# =============================================================================
# WORKER THREADS
# =============================================================================
class ConversionWorker(QThread):
    """Worker thread for file conversions."""
    progress = pyqtSignal(int, int)  # current, total
    log_message = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    
    def __init__(self, task_type: str, files: List[str], options: dict, output_dir: Path):
        super().__init__()
        self.task_type = task_type
        self.files = files
        self.options = options
        self.output_dir = output_dir
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
    
    def run(self):
        if self.task_type == "video":
            self._convert_videos()
        elif self.task_type == "audio":
            self._convert_audio()
        elif self.task_type == "extract":
            self._extract_audio()
        elif self.task_type == "image":
            self._convert_images()
        elif self.task_type == "gif":
            self._create_gifs()
    
    def _convert_videos(self):
        total = len(self.files)
        out_fmt = self.options.get("format", "mp4")
        quality = self.options.get("quality", "Original")
        speed = self.options.get("speed", "medium")
        
        crf = None
        if "18" in quality:
            crf = "18"
        elif "23" in quality:
            crf = "23"
        elif "28" in quality:
            crf = "28"
        
        for i, filepath in enumerate(self.files):
            if self._cancelled:
                break
            
            self.log_message.emit(f"Converting: {os.path.basename(filepath)}")
            self.progress.emit(i, total)
            
            inp = Path(filepath)
            out = self.output_dir / f"{inp.stem}.{out_fmt}"
            
            cmd = ["ffmpeg", "-y", "-i", str(inp)]
            
            if crf:
                cmd.extend(["-c:v", "libx264", "-crf", crf, "-preset", speed])
            else:
                cmd.extend(["-c:v", "copy"])
            
            cmd.extend(["-c:a", "aac", str(out)])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_message.emit(f"Saved: {out.name}")
                else:
                    self.log_message.emit(f"Error: {result.stderr[:100]}")
            except Exception as e:
                self.log_message.emit(f"Error: {str(e)}")
        
        self.progress.emit(total, total)
        self.finished_signal.emit(f"Done! Converted {total} videos.")
    
    def _convert_audio(self):
        total = len(self.files)
        out_fmt = self.options.get("format", "mp3")
        bitrate = self.options.get("bitrate", "192k")
        samplerate = self.options.get("samplerate", "Original")
        
        for i, filepath in enumerate(self.files):
            if self._cancelled:
                break
            
            self.log_message.emit(f"Converting: {os.path.basename(filepath)}")
            self.progress.emit(i, total)
            
            inp = Path(filepath)
            out = self.output_dir / f"{inp.stem}.{out_fmt}"
            
            cmd = ["ffmpeg", "-y", "-i", str(inp)]
            cmd.extend(["-b:a", bitrate])
            
            if samplerate != "Original":
                cmd.extend(["-ar", samplerate])
            
            cmd.append(str(out))
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_message.emit(f"Saved: {out.name}")
                else:
                    self.log_message.emit(f"Error: {result.stderr[:100]}")
            except Exception as e:
                self.log_message.emit(f"Error: {str(e)}")
        
        self.progress.emit(total, total)
        self.finished_signal.emit(f"Done! Converted {total} audio files.")
    
    def _extract_audio(self):
        total = len(self.files)
        out_fmt = self.options.get("format", "mp3")
        bitrate = self.options.get("bitrate", "256k")
        
        for i, filepath in enumerate(self.files):
            if self._cancelled:
                break
            
            self.log_message.emit(f"Extracting: {os.path.basename(filepath)}")
            self.progress.emit(i, total)
            
            inp = Path(filepath)
            out = self.output_dir / f"{inp.stem}.{out_fmt}"
            
            cmd = ["ffmpeg", "-y", "-i", str(inp), "-vn", "-b:a", bitrate, str(out)]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_message.emit(f"Saved: {out.name}")
                else:
                    self.log_message.emit(f"Error: {result.stderr[:100]}")
            except Exception as e:
                self.log_message.emit(f"Error: {str(e)}")
        
        self.progress.emit(total, total)
        self.finished_signal.emit(f"Done! Extracted {total} audio tracks.")
    
    def _convert_images(self):
        from PIL import Image
        
        total = len(self.files)
        out_fmt = self.options.get("format", "png").lower()
        quality = self.options.get("quality", 95)
        do_resize = self.options.get("resize", False)
        target_w = self.options.get("width")
        target_h = self.options.get("height")
        maintain_ratio = self.options.get("maintain_ratio", True)
        
        for i, filepath in enumerate(self.files):
            if self._cancelled:
                break
            
            self.log_message.emit(f"Converting: {os.path.basename(filepath)}")
            self.progress.emit(i, total)
            
            try:
                img = Image.open(filepath)
                
                if do_resize and (target_w or target_h):
                    orig_w, orig_h = img.size
                    
                    if maintain_ratio:
                        if target_w and target_h:
                            ratio = min(target_w / orig_w, target_h / orig_h)
                            new_size = (int(orig_w * ratio), int(orig_h * ratio))
                        elif target_w:
                            ratio = target_w / orig_w
                            new_size = (target_w, int(orig_h * ratio))
                        else:
                            ratio = target_h / orig_h
                            new_size = (int(orig_w * ratio), target_h)
                    else:
                        new_size = (target_w or orig_w, target_h or orig_h)
                    
                    img = img.resize(new_size, Image.LANCZOS)
                
                inp = Path(filepath)
                out = self.output_dir / f"{inp.stem}.{out_fmt}"
                
                if out_fmt in ["jpg", "jpeg"] and img.mode in ["RGBA", "P"]:
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
                    img = background
                
                if out_fmt in ["jpg", "jpeg"]:
                    img.save(out, quality=quality, optimize=True)
                elif out_fmt == "png":
                    img.save(out, optimize=True)
                elif out_fmt == "webp":
                    img.save(out, quality=quality)
                elif out_fmt == "ico":
                    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                    img.save(out, sizes=sizes)
                else:
                    img.save(out)
                
                self.log_message.emit(f"Saved: {out.name}")
                
            except Exception as e:
                self.log_message.emit(f"Error: {str(e)}")
        
        self.progress.emit(total, total)
        self.finished_signal.emit(f"Done! Converted {total} images.")
    
    def _create_gifs(self):
        """Create GIFs from video files with detailed options."""
        total = len(self.files)
        
        # Extract options
        fps = self.options.get("fps", 15)
        width = self.options.get("width", 480)
        start_time = self.options.get("start_time", 0)
        duration = self.options.get("duration", 0)  # 0 = full video
        colors = self.options.get("colors", 256)
        dither = self.options.get("dither", "sierra2_4a")
        loop = self.options.get("loop", 0)  # 0 = infinite
        optimize = self.options.get("optimize", True)
        
        for i, filepath in enumerate(self.files):
            if self._cancelled:
                break
            
            self.log_message.emit(f"Creating GIF: {os.path.basename(filepath)}")
            self.progress.emit(i, total)
            
            inp = Path(filepath)
            out = self.output_dir / f"{inp.stem}.gif"
            palette_file = self.output_dir / f"{inp.stem}_palette.png"
            
            try:
                # Build filter string
                filters = f"fps={fps},scale={width}:-1:flags=lanczos"
                
                if optimize:
                    # Two-pass method for better quality
                    # Pass 1: Generate palette
                    palette_filters = f"{filters},palettegen=max_colors={colors}:stats_mode=diff"
                    
                    cmd1 = ["ffmpeg", "-y", "-i", str(inp)]
                    if start_time > 0:
                        cmd1.extend(["-ss", str(start_time)])
                    if duration > 0:
                        cmd1.extend(["-t", str(duration)])
                    cmd1.extend(["-vf", palette_filters, str(palette_file)])
                    
                    result1 = subprocess.run(cmd1, capture_output=True, text=True)
                    if result1.returncode != 0:
                        self.log_message.emit(f"Palette error: {result1.stderr[:80]}")
                        continue
                    
                    # Pass 2: Create GIF using palette
                    gif_filters = f"{filters},paletteuse=dither={dither}"
                    
                    cmd2 = ["ffmpeg", "-y"]
                    if start_time > 0:
                        cmd2.extend(["-ss", str(start_time)])
                    if duration > 0:
                        cmd2.extend(["-t", str(duration)])
                    cmd2.extend([
                        "-i", str(inp),
                        "-i", str(palette_file),
                        "-lavfi", f"{filters}[x];[x][1:v]paletteuse=dither={dither}",
                        "-loop", str(loop),
                        str(out)
                    ])
                    
                    result2 = subprocess.run(cmd2, capture_output=True, text=True)
                    
                    # Clean up palette
                    if palette_file.exists():
                        palette_file.unlink()
                    
                    if result2.returncode == 0:
                        # Report file size
                        size_kb = out.stat().st_size / 1024
                        self.log_message.emit(f"Saved: {out.name} ({size_kb:.1f} KB)")
                    else:
                        self.log_message.emit(f"Error: {result2.stderr[:80]}")
                
                else:
                    # Single-pass method (faster, lower quality)
                    cmd = ["ffmpeg", "-y", "-i", str(inp)]
                    if start_time > 0:
                        cmd.extend(["-ss", str(start_time)])
                    if duration > 0:
                        cmd.extend(["-t", str(duration)])
                    cmd.extend([
                        "-vf", f"{filters},split[s0][s1];[s0]palettegen=max_colors={colors}[p];[s1][p]paletteuse=dither={dither}",
                        "-loop", str(loop),
                        str(out)
                    ])
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        size_kb = out.stat().st_size / 1024
                        self.log_message.emit(f"Saved: {out.name} ({size_kb:.1f} KB)")
                    else:
                        self.log_message.emit(f"Error: {result.stderr[:80]}")
                    
            except Exception as e:
                self.log_message.emit(f"Error: {str(e)}")
        
        self.progress.emit(total, total)
        self.finished_signal.emit(f"Done! Created {total} GIFs.")


class DownloadWorker(QThread):
    """Worker thread for media downloads."""
    progress = pyqtSignal(int, int)
    log_message = pyqtSignal(str)
    status_update = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    
    def __init__(self, urls: List[str], options: dict, output_dir: Path):
        super().__init__()
        self.urls = urls
        self.options = options
        self.output_dir = output_dir
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
    
    def run(self):
        download_type = self.options.get("type", "Video + Audio")
        quality = self.options.get("quality", "Best")
        is_playlist = self.options.get("playlist", False)
        embed_thumb = self.options.get("thumbnail", True)
        embed_subs = self.options.get("subtitles", False)
        playlist_start = self.options.get("playlist_start")
        playlist_end = self.options.get("playlist_end")
        
        total = len(self.urls)
        
        for i, url in enumerate(self.urls):
            if self._cancelled:
                break
            
            self.log_message.emit(f"Downloading: {url[:60]}...")
            self.status_update.emit(f"Downloading {i+1}/{total}...")
            self.progress.emit(i, total)
            
            cmd = ["yt-dlp"]
            
            if is_playlist:
                cmd.extend(["-o", str(self.output_dir / "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s")])
            else:
                cmd.extend(["-o", str(self.output_dir / "%(title)s.%(ext)s")])
            
            if is_playlist:
                if playlist_start:
                    cmd.extend(["--playlist-start", str(playlist_start)])
                if playlist_end:
                    cmd.extend(["--playlist-end", str(playlist_end)])
            else:
                cmd.append("--no-playlist")
            
            if "Audio Only" in download_type:
                cmd.extend(["-x"])
                if "MP3" in download_type:
                    cmd.extend(["--audio-format", "mp3", "--audio-quality", "0"])
                elif "WAV" in download_type:
                    cmd.extend(["--audio-format", "wav"])
                elif "FLAC" in download_type:
                    cmd.extend(["--audio-format", "flac"])
            else:
                if quality == "Best":
                    cmd.extend(["-f", "bestvideo+bestaudio/best"])
                else:
                    height = quality.replace("p", "")
                    cmd.extend(["-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"])
                cmd.extend(["--merge-output-format", "mp4"])
            
            if embed_thumb:
                cmd.append("--embed-thumbnail")
            if embed_subs:
                cmd.extend(["--embed-subs", "--sub-langs", "en,en.*"])
            
            cmd.extend(["--newline", "--progress"])
            cmd.append(url)
            
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in iter(process.stdout.readline, ""):
                    if self._cancelled:
                        process.terminate()
                        break
                    line = line.strip()
                    if line:
                        if "[download]" in line and "%" in line:
                            match = re.search(r"(\d+\.?\d*)%", line)
                            if match:
                                pct = float(match.group(1)) / 100
                                self.progress.emit(int((i + pct) * 100), total * 100)
                        elif "Destination" in line or "Merging" in line:
                            self.log_message.emit(line[:80])
                
                process.wait()
                
                if process.returncode == 0:
                    self.log_message.emit("Downloaded successfully!")
                else:
                    self.log_message.emit("Download may have had issues")
                    
            except Exception as e:
                self.log_message.emit(f"Error: {str(e)}")
        
        self.progress.emit(total * 100, total * 100)
        self.finished_signal.emit(f"Done! Downloaded {total} item(s).")


# =============================================================================
# MAIN APPLICATION
# =============================================================================
class VDToolWindow(QMainWindow):
    """Main application window."""
    
    VIDEO_FORMATS = ["mp4", "mkv", "avi", "mov", "webm", "flv", "wmv", "mpeg"]
    AUDIO_FORMATS = ["mp3", "wav", "aac", "flac", "ogg", "m4a", "wma"]
    IMAGE_FORMATS = ["png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff", "ico"]
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("VDTool - Multimedia Converter & Downloader")
        self.setMinimumSize(1100, 750)
        self.resize(1200, 800)
        
        # Output directory
        self.output_dir = Path.home() / "Downloads" / "VDTool"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Workers
        self.current_worker = None
        
        # File lists
        self.video_files: List[str] = []
        self.audio_files: List[str] = []
        self.extract_files: List[str] = []
        self.image_files: List[str] = []
        self.metadata_files: List[str] = []
        self.gif_files: List[str] = []
        
        # Metadata
        self.current_metadata = {}
        
        # Check dependencies
        self.check_dependencies()
        
        # Build UI
        self.setup_ui()
    
    def check_dependencies(self):
        """Check for required system tools."""
        self.ffmpeg_ok = shutil.which("ffmpeg") is not None
        self.ffprobe_ok = shutil.which("ffprobe") is not None
        self.ytdlp_ok = shutil.which("yt-dlp") is not None
        
        missing = []
        if not self.ffmpeg_ok:
            missing.append("ffmpeg")
        if not self.ffprobe_ok:
            missing.append("ffprobe")
        if not self.ytdlp_ok:
            missing.append("yt-dlp")
        
        if missing:
            QMessageBox.warning(
                self,
                "Missing Dependencies",
                f"The following tools are not installed:\n{', '.join(missing)}\n\n"
                "Some features may not work properly."
            )
    
    def setup_ui(self):
        """Build the main user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        title_section = QVBoxLayout()
        title_label = QLabel("VDTool")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("Multimedia Converter & Downloader")
        subtitle_label.setObjectName("subtitleLabel")
        title_section.addWidget(title_label)
        title_section.addWidget(subtitle_label)
        
        header.addLayout(title_section)
        header.addStretch()
        
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn)
        
        main_layout.addLayout(header)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(sep)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_video_tab(), "Video Converter")
        self.tabs.addTab(self.create_audio_tab(), "Audio Converter")
        self.tabs.addTab(self.create_extractor_tab(), "Audio Extractor")
        self.tabs.addTab(self.create_image_tab(), "Image Converter")
        self.tabs.addTab(self.create_gif_tab(), "GIF Creator")
        self.tabs.addTab(self.create_metadata_tab(), "Metadata")
        self.tabs.addTab(self.create_downloader_tab(), "Downloader")
        main_layout.addWidget(self.tabs, 1)
        
        # Log area
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        log_layout.addWidget(self.log_text)
        main_layout.addWidget(log_group)
    
    # =========================================================================
    # VIDEO CONVERTER TAB
    # =========================================================================
    def create_video_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # File selection group
        file_group = QGroupBox("Input Files")
        file_layout = QVBoxLayout(file_group)
        
        self.video_list = QListWidget()
        self.video_list.setMinimumHeight(150)
        file_layout.addWidget(self.video_list)
        
        btn_row = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_video_files)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_video_folder)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: (self.video_list.clear(), self.video_files.clear()))
        
        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        file_layout.addLayout(btn_row)
        
        layout.addWidget(file_group)
        
        # Options group
        opt_group = QGroupBox("Conversion Options")
        opt_layout = QHBoxLayout(opt_group)
        
        opt_layout.addWidget(QLabel("Format:"))
        self.video_format_combo = QComboBox()
        self.video_format_combo.addItems(self.VIDEO_FORMATS)
        self.video_format_combo.setCurrentText("mp4")
        opt_layout.addWidget(self.video_format_combo)
        
        opt_layout.addSpacing(20)
        opt_layout.addWidget(QLabel("Quality:"))
        self.video_quality_combo = QComboBox()
        self.video_quality_combo.addItems(["Original", "High (CRF 18)", "Medium (CRF 23)", "Low (CRF 28)"])
        opt_layout.addWidget(self.video_quality_combo)
        
        opt_layout.addSpacing(20)
        opt_layout.addWidget(QLabel("Speed:"))
        self.video_speed_combo = QComboBox()
        self.video_speed_combo.addItems(["ultrafast", "superfast", "fast", "medium", "slow"])
        self.video_speed_combo.setCurrentText("medium")
        opt_layout.addWidget(self.video_speed_combo)
        
        opt_layout.addStretch()
        layout.addWidget(opt_group)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.video_progress = QProgressBar()
        self.video_progress.setTextVisible(True)
        progress_layout.addWidget(self.video_progress)
        
        self.video_status = QLabel("Ready")
        self.video_status.setObjectName("statusLabel")
        self.video_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.video_status)
        
        layout.addLayout(progress_layout)
        
        # Convert button
        self.video_convert_btn = QPushButton("Convert Videos")
        self.video_convert_btn.setObjectName("primaryButton")
        self.video_convert_btn.clicked.connect(self.convert_videos)
        layout.addWidget(self.video_convert_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        return tab
    
    def add_video_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.mpeg)"
        )
        for f in files:
            if f not in self.video_files:
                self.video_files.append(f)
                self.video_list.addItem(f)
    
    def add_video_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for ext in self.VIDEO_FORMATS:
                for f in Path(folder).glob(f"*.{ext}"):
                    if str(f) not in self.video_files:
                        self.video_files.append(str(f))
                        self.video_list.addItem(str(f))
    
    def convert_videos(self):
        if not self.video_files:
            QMessageBox.warning(self, "No Files", "Please add video files to convert.")
            return
        
        options = {
            "format": self.video_format_combo.currentText(),
            "quality": self.video_quality_combo.currentText(),
            "speed": self.video_speed_combo.currentText()
        }
        
        self.start_conversion("video", self.video_files.copy(), options,
                              self.video_progress, self.video_status, self.video_convert_btn)
    
    # =========================================================================
    # AUDIO CONVERTER TAB
    # =========================================================================
    def create_audio_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # File selection
        file_group = QGroupBox("Input Files")
        file_layout = QVBoxLayout(file_group)
        
        self.audio_list = QListWidget()
        self.audio_list.setMinimumHeight(150)
        file_layout.addWidget(self.audio_list)
        
        btn_row = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_audio_files)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_audio_folder)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: (self.audio_list.clear(), self.audio_files.clear()))
        
        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        file_layout.addLayout(btn_row)
        
        layout.addWidget(file_group)
        
        # Options
        opt_group = QGroupBox("Conversion Options")
        opt_layout = QHBoxLayout(opt_group)
        
        opt_layout.addWidget(QLabel("Format:"))
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(self.AUDIO_FORMATS)
        self.audio_format_combo.setCurrentText("mp3")
        opt_layout.addWidget(self.audio_format_combo)
        
        opt_layout.addSpacing(20)
        opt_layout.addWidget(QLabel("Bitrate:"))
        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems(["64k", "128k", "192k", "256k", "320k"])
        self.audio_bitrate_combo.setCurrentText("192k")
        opt_layout.addWidget(self.audio_bitrate_combo)
        
        opt_layout.addSpacing(20)
        opt_layout.addWidget(QLabel("Sample Rate:"))
        self.audio_samplerate_combo = QComboBox()
        self.audio_samplerate_combo.addItems(["Original", "44100", "48000", "96000"])
        opt_layout.addWidget(self.audio_samplerate_combo)
        
        opt_layout.addStretch()
        layout.addWidget(opt_group)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.audio_progress = QProgressBar()
        progress_layout.addWidget(self.audio_progress)
        
        self.audio_status = QLabel("Ready")
        self.audio_status.setObjectName("statusLabel")
        self.audio_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.audio_status)
        
        layout.addLayout(progress_layout)
        
        # Convert button
        self.audio_convert_btn = QPushButton("Convert Audio")
        self.audio_convert_btn.setObjectName("primaryButton")
        self.audio_convert_btn.clicked.connect(self.convert_audio)
        layout.addWidget(self.audio_convert_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        return tab
    
    def add_audio_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files", "",
            "Audio Files (*.mp3 *.wav *.aac *.flac *.ogg *.m4a *.wma)"
        )
        for f in files:
            if f not in self.audio_files:
                self.audio_files.append(f)
                self.audio_list.addItem(f)
    
    def add_audio_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for ext in self.AUDIO_FORMATS:
                for f in Path(folder).glob(f"*.{ext}"):
                    if str(f) not in self.audio_files:
                        self.audio_files.append(str(f))
                        self.audio_list.addItem(str(f))
    
    def convert_audio(self):
        if not self.audio_files:
            QMessageBox.warning(self, "No Files", "Please add audio files to convert.")
            return
        
        options = {
            "format": self.audio_format_combo.currentText(),
            "bitrate": self.audio_bitrate_combo.currentText(),
            "samplerate": self.audio_samplerate_combo.currentText()
        }
        
        self.start_conversion("audio", self.audio_files.copy(), options,
                              self.audio_progress, self.audio_status, self.audio_convert_btn)
    
    # =========================================================================
    # AUDIO EXTRACTOR TAB
    # =========================================================================
    def create_extractor_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # File selection
        file_group = QGroupBox("Video Files")
        file_layout = QVBoxLayout(file_group)
        
        self.extract_list = QListWidget()
        self.extract_list.setMinimumHeight(150)
        file_layout.addWidget(self.extract_list)
        
        btn_row = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_extract_files)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_extract_folder)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: (self.extract_list.clear(), self.extract_files.clear()))
        
        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        file_layout.addLayout(btn_row)
        
        layout.addWidget(file_group)
        
        # Options
        opt_group = QGroupBox("Extraction Options")
        opt_layout = QHBoxLayout(opt_group)
        
        opt_layout.addWidget(QLabel("Output Format:"))
        self.extract_format_combo = QComboBox()
        self.extract_format_combo.addItems(["mp3", "wav", "aac", "flac", "ogg"])
        self.extract_format_combo.setCurrentText("mp3")
        opt_layout.addWidget(self.extract_format_combo)
        
        opt_layout.addSpacing(20)
        opt_layout.addWidget(QLabel("Bitrate:"))
        self.extract_bitrate_combo = QComboBox()
        self.extract_bitrate_combo.addItems(["128k", "192k", "256k", "320k"])
        self.extract_bitrate_combo.setCurrentText("256k")
        opt_layout.addWidget(self.extract_bitrate_combo)
        
        opt_layout.addStretch()
        layout.addWidget(opt_group)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.extract_progress = QProgressBar()
        progress_layout.addWidget(self.extract_progress)
        
        self.extract_status = QLabel("Ready")
        self.extract_status.setObjectName("statusLabel")
        self.extract_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.extract_status)
        
        layout.addLayout(progress_layout)
        
        # Extract button
        self.extract_btn = QPushButton("Extract Audio")
        self.extract_btn.setObjectName("primaryButton")
        self.extract_btn.clicked.connect(self.extract_audio)
        layout.addWidget(self.extract_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        return tab
    
    def add_extract_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.mpeg)"
        )
        for f in files:
            if f not in self.extract_files:
                self.extract_files.append(f)
                self.extract_list.addItem(f)
    
    def add_extract_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for ext in self.VIDEO_FORMATS:
                for f in Path(folder).glob(f"*.{ext}"):
                    if str(f) not in self.extract_files:
                        self.extract_files.append(str(f))
                        self.extract_list.addItem(str(f))
    
    def extract_audio(self):
        if not self.extract_files:
            QMessageBox.warning(self, "No Files", "Please add video files to extract audio from.")
            return
        
        options = {
            "format": self.extract_format_combo.currentText(),
            "bitrate": self.extract_bitrate_combo.currentText()
        }
        
        self.start_conversion("extract", self.extract_files.copy(), options,
                              self.extract_progress, self.extract_status, self.extract_btn)
    
    # =========================================================================
    # IMAGE CONVERTER TAB
    # =========================================================================
    def create_image_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # File selection
        file_group = QGroupBox("Input Files")
        file_layout = QVBoxLayout(file_group)
        
        self.image_list = QListWidget()
        self.image_list.setMinimumHeight(120)
        file_layout.addWidget(self.image_list)
        
        btn_row = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_image_files)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_image_folder)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: (self.image_list.clear(), self.image_files.clear()))
        
        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        file_layout.addLayout(btn_row)
        
        layout.addWidget(file_group)
        
        # Format and quality options
        opt_group = QGroupBox("Output Options")
        opt_layout = QHBoxLayout(opt_group)
        
        opt_layout.addWidget(QLabel("Format:"))
        self.image_format_combo = QComboBox()
        self.image_format_combo.addItems(self.IMAGE_FORMATS)
        self.image_format_combo.setCurrentText("png")
        opt_layout.addWidget(self.image_format_combo)
        
        opt_layout.addSpacing(20)
        opt_layout.addWidget(QLabel("Quality:"))
        self.image_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.image_quality_slider.setRange(10, 100)
        self.image_quality_slider.setValue(95)
        self.image_quality_slider.setFixedWidth(150)
        opt_layout.addWidget(self.image_quality_slider)
        
        self.image_quality_label = QLabel("95%")
        self.image_quality_slider.valueChanged.connect(
            lambda v: self.image_quality_label.setText(f"{v}%")
        )
        opt_layout.addWidget(self.image_quality_label)
        
        opt_layout.addStretch()
        layout.addWidget(opt_group)
        
        # Resize options
        resize_group = QGroupBox("Resize Options")
        resize_layout = QHBoxLayout(resize_group)
        
        self.resize_check = QCheckBox("Enable Resize")
        resize_layout.addWidget(self.resize_check)
        
        resize_layout.addSpacing(20)
        resize_layout.addWidget(QLabel("Width:"))
        self.image_width_spin = QSpinBox()
        self.image_width_spin.setRange(0, 10000)
        self.image_width_spin.setSpecialValueText("auto")
        resize_layout.addWidget(self.image_width_spin)
        
        resize_layout.addSpacing(10)
        resize_layout.addWidget(QLabel("Height:"))
        self.image_height_spin = QSpinBox()
        self.image_height_spin.setRange(0, 10000)
        self.image_height_spin.setSpecialValueText("auto")
        resize_layout.addWidget(self.image_height_spin)
        
        resize_layout.addSpacing(20)
        self.maintain_ratio_check = QCheckBox("Maintain Aspect Ratio")
        self.maintain_ratio_check.setChecked(True)
        resize_layout.addWidget(self.maintain_ratio_check)
        
        resize_layout.addStretch()
        layout.addWidget(resize_group)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.image_progress = QProgressBar()
        progress_layout.addWidget(self.image_progress)
        
        self.image_status = QLabel("Ready")
        self.image_status.setObjectName("statusLabel")
        self.image_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.image_status)
        
        layout.addLayout(progress_layout)
        
        # Convert button
        self.image_convert_btn = QPushButton("Convert Images")
        self.image_convert_btn.setObjectName("primaryButton")
        self.image_convert_btn.clicked.connect(self.convert_images)
        layout.addWidget(self.image_convert_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        return tab
    
    def add_image_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Image Files", "",
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tiff *.ico)"
        )
        for f in files:
            if f not in self.image_files:
                self.image_files.append(f)
                self.image_list.addItem(f)
    
    def add_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for ext in self.IMAGE_FORMATS:
                for f in Path(folder).glob(f"*.{ext}"):
                    if str(f) not in self.image_files:
                        self.image_files.append(str(f))
                        self.image_list.addItem(str(f))
    
    def convert_images(self):
        if not self.image_files:
            QMessageBox.warning(self, "No Files", "Please add image files to convert.")
            return
        
        options = {
            "format": self.image_format_combo.currentText(),
            "quality": self.image_quality_slider.value(),
            "resize": self.resize_check.isChecked(),
            "width": self.image_width_spin.value() if self.image_width_spin.value() > 0 else None,
            "height": self.image_height_spin.value() if self.image_height_spin.value() > 0 else None,
            "maintain_ratio": self.maintain_ratio_check.isChecked()
        }
        
        self.start_conversion("image", self.image_files.copy(), options,
                              self.image_progress, self.image_status, self.image_convert_btn)
    
    # =========================================================================
    # GIF CREATOR TAB
    # =========================================================================
    def create_gif_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # File selection
        file_group = QGroupBox("Video Files")
        file_layout = QVBoxLayout(file_group)
        
        self.gif_list = QListWidget()
        self.gif_list.setMinimumHeight(100)
        file_layout.addWidget(self.gif_list)
        
        btn_row = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_gif_files)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_gif_folder)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: (self.gif_list.clear(), self.gif_files.clear()))
        
        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        file_layout.addLayout(btn_row)
        
        layout.addWidget(file_group)
        
        # Basic options
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QHBoxLayout(basic_group)
        
        basic_layout.addWidget(QLabel("FPS:"))
        self.gif_fps_spin = QSpinBox()
        self.gif_fps_spin.setRange(1, 60)
        self.gif_fps_spin.setValue(15)
        self.gif_fps_spin.setToolTip("Frames per second (lower = smaller file)")
        basic_layout.addWidget(self.gif_fps_spin)
        
        basic_layout.addSpacing(20)
        basic_layout.addWidget(QLabel("Width:"))
        self.gif_width_spin = QSpinBox()
        self.gif_width_spin.setRange(50, 1920)
        self.gif_width_spin.setValue(480)
        self.gif_width_spin.setSuffix(" px")
        self.gif_width_spin.setToolTip("Output width (height auto-scales)")
        basic_layout.addWidget(self.gif_width_spin)
        
        basic_layout.addSpacing(20)
        basic_layout.addWidget(QLabel("Loop:"))
        self.gif_loop_spin = QSpinBox()
        self.gif_loop_spin.setRange(0, 100)
        self.gif_loop_spin.setValue(0)
        self.gif_loop_spin.setSpecialValueText("Infinite")
        self.gif_loop_spin.setToolTip("0 = loop forever")
        basic_layout.addWidget(self.gif_loop_spin)
        
        basic_layout.addStretch()
        layout.addWidget(basic_group)
        
        # Timing options
        timing_group = QGroupBox("Timing (optional - leave at 0 for full video)")
        timing_layout = QHBoxLayout(timing_group)
        
        timing_layout.addWidget(QLabel("Start Time:"))
        self.gif_start_spin = QDoubleSpinBox()
        self.gif_start_spin.setRange(0, 9999)
        self.gif_start_spin.setValue(0)
        self.gif_start_spin.setSuffix(" sec")
        self.gif_start_spin.setDecimals(1)
        timing_layout.addWidget(self.gif_start_spin)
        
        timing_layout.addSpacing(20)
        timing_layout.addWidget(QLabel("Duration:"))
        self.gif_duration_spin = QDoubleSpinBox()
        self.gif_duration_spin.setRange(0, 9999)
        self.gif_duration_spin.setValue(0)
        self.gif_duration_spin.setSuffix(" sec")
        self.gif_duration_spin.setSpecialValueText("Full video")
        self.gif_duration_spin.setDecimals(1)
        timing_layout.addWidget(self.gif_duration_spin)
        
        timing_layout.addStretch()
        layout.addWidget(timing_group)
        
        # Compression options
        compress_group = QGroupBox("Compression & Quality")
        compress_layout = QVBoxLayout(compress_group)
        
        compress_row1 = QHBoxLayout()
        compress_row1.addWidget(QLabel("Colors:"))
        self.gif_colors_combo = QComboBox()
        self.gif_colors_combo.addItems(["256", "128", "64", "32", "16"])
        self.gif_colors_combo.setToolTip("Fewer colors = smaller file, lower quality")
        compress_row1.addWidget(self.gif_colors_combo)
        
        compress_row1.addSpacing(20)
        compress_row1.addWidget(QLabel("Dithering:"))
        self.gif_dither_combo = QComboBox()
        self.gif_dither_combo.addItems([
            "sierra2_4a",    # Good balance
            "floyd_steinberg",  # Classic, good quality
            "bayer:bayer_scale=3",  # Ordered, retro look
            "none"           # No dithering, banding
        ])
        self.gif_dither_combo.setToolTip("Dithering algorithm for color reduction")
        compress_row1.addWidget(self.gif_dither_combo)
        
        compress_row1.addStretch()
        compress_layout.addLayout(compress_row1)
        
        compress_row2 = QHBoxLayout()
        self.gif_optimize_check = QCheckBox("Two-pass optimization (better quality, slower)")
        self.gif_optimize_check.setChecked(True)
        self.gif_optimize_check.setToolTip("Uses palette generation for better colors")
        compress_row2.addWidget(self.gif_optimize_check)
        compress_row2.addStretch()
        compress_layout.addLayout(compress_row2)
        
        layout.addWidget(compress_group)
        
        # Size estimation info
        info_label = QLabel("Tip: For smaller files, reduce FPS, width, colors, or duration")
        info_label.setStyleSheet("color: #7a7a9e; font-style: italic;")
        layout.addWidget(info_label)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.gif_progress = QProgressBar()
        progress_layout.addWidget(self.gif_progress)
        
        self.gif_status = QLabel("Ready")
        self.gif_status.setObjectName("statusLabel")
        self.gif_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.gif_status)
        
        layout.addLayout(progress_layout)
        
        # Create button
        self.gif_create_btn = QPushButton("Create GIFs")
        self.gif_create_btn.setObjectName("primaryButton")
        self.gif_create_btn.clicked.connect(self.create_gifs)
        layout.addWidget(self.gif_create_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        return tab
    
    def add_gif_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.mpeg)"
        )
        for f in files:
            if f not in self.gif_files:
                self.gif_files.append(f)
                self.gif_list.addItem(os.path.basename(f))
    
    def add_gif_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for ext in self.VIDEO_FORMATS:
                for f in Path(folder).glob(f"*.{ext}"):
                    if str(f) not in self.gif_files:
                        self.gif_files.append(str(f))
                        self.gif_list.addItem(f.name)
    
    def create_gifs(self):
        if not self.gif_files:
            QMessageBox.warning(self, "No Files", "Please add video files to convert to GIF.")
            return
        
        options = {
            "fps": self.gif_fps_spin.value(),
            "width": self.gif_width_spin.value(),
            "start_time": self.gif_start_spin.value(),
            "duration": self.gif_duration_spin.value(),
            "colors": int(self.gif_colors_combo.currentText()),
            "dither": self.gif_dither_combo.currentText(),
            "loop": self.gif_loop_spin.value(),
            "optimize": self.gif_optimize_check.isChecked()
        }
        
        self.start_conversion("gif", self.gif_files.copy(), options,
                              self.gif_progress, self.gif_status, self.gif_create_btn)
    
    # =========================================================================
    # METADATA TAB (with batch support)
    # =========================================================================
    def create_metadata_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # File selection - batch support
        file_group = QGroupBox("Media Files (Batch Support)")
        file_layout = QVBoxLayout(file_group)
        
        self.metadata_list = QListWidget()
        self.metadata_list.setMinimumHeight(80)
        self.metadata_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.metadata_list.itemClicked.connect(self._on_metadata_item_clicked)
        file_layout.addWidget(self.metadata_list)
        
        btn_row = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_metadata_files)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_metadata_folder)
        clear_btn = QPushButton("Clear List")
        clear_btn.clicked.connect(lambda: (self.metadata_list.clear(), self.metadata_files.clear()))
        
        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        file_layout.addLayout(btn_row)
        
        layout.addWidget(file_group)
        
        # Batch edit section
        batch_group = QGroupBox("Batch Edit Tags (applied to selected files)")
        batch_layout = QVBoxLayout(batch_group)
        
        # Common tags grid
        tags_row1 = QHBoxLayout()
        tags_row1.addWidget(QLabel("Artist:"))
        self.batch_artist = QLineEdit()
        self.batch_artist.setPlaceholderText("Leave empty to keep original")
        tags_row1.addWidget(self.batch_artist)
        
        tags_row1.addSpacing(20)
        tags_row1.addWidget(QLabel("Album:"))
        self.batch_album = QLineEdit()
        self.batch_album.setPlaceholderText("Leave empty to keep original")
        tags_row1.addWidget(self.batch_album)
        batch_layout.addLayout(tags_row1)
        
        tags_row2 = QHBoxLayout()
        tags_row2.addWidget(QLabel("Year:"))
        self.batch_year = QLineEdit()
        self.batch_year.setPlaceholderText("e.g. 2024")
        self.batch_year.setMaximumWidth(100)
        tags_row2.addWidget(self.batch_year)
        
        tags_row2.addSpacing(20)
        tags_row2.addWidget(QLabel("Genre:"))
        self.batch_genre = QComboBox()
        self.batch_genre.setEditable(True)
        self.batch_genre.addItems([
            "", "Rock", "Pop", "Hip-Hop", "Jazz", "Classical", "Electronic",
            "R&B", "Country", "Metal", "Indie", "Alternative", "Folk", "Blues",
            "Reggae", "Soul", "Punk", "Disco", "House", "Techno", "Ambient"
        ])
        tags_row2.addWidget(self.batch_genre)
        
        tags_row2.addSpacing(20)
        tags_row2.addWidget(QLabel("Album Artist:"))
        self.batch_album_artist = QLineEdit()
        tags_row2.addWidget(self.batch_album_artist)
        batch_layout.addLayout(tags_row2)
        
        tags_row3 = QHBoxLayout()
        tags_row3.addWidget(QLabel("Comment:"))
        self.batch_comment = QLineEdit()
        tags_row3.addWidget(self.batch_comment)
        batch_layout.addLayout(tags_row3)
        
        # Auto-number tracks checkbox
        self.auto_track_numbers = QCheckBox("Auto-number tracks based on list order")
        batch_layout.addWidget(self.auto_track_numbers)
        
        layout.addWidget(batch_group)
        
        # Metadata display for selected file
        info_group = QGroupBox("File Information (click a file to view)")
        info_layout = QVBoxLayout(info_group)
        
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(120)
        info_layout.addWidget(self.metadata_text)
        
        layout.addWidget(info_group)
        
        # Action buttons
        btn_row = QHBoxLayout()
        
        apply_btn = QPushButton("Apply Tags to Selected")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.apply_batch_metadata)
        btn_row.addWidget(apply_btn)
        
        export_btn = QPushButton("Export to JSON")
        export_btn.clicked.connect(self.export_metadata)
        btn_row.addWidget(export_btn)
        
        clear_meta_btn = QPushButton("Clear Metadata from Selected")
        clear_meta_btn.clicked.connect(self.clear_file_metadata)
        btn_row.addWidget(clear_meta_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Progress for batch operations
        self.metadata_progress = QProgressBar()
        self.metadata_progress.setVisible(False)
        layout.addWidget(self.metadata_progress)
        
        return tab
    
    def add_metadata_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Media Files", "",
            "All Media (*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac *.m4a *.ogg *.aac *.wma)"
        )
        for f in files:
            if f not in self.metadata_files:
                self.metadata_files.append(f)
                self.metadata_list.addItem(os.path.basename(f))
    
    def add_metadata_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            extensions = ["mp3", "wav", "flac", "m4a", "ogg", "aac", "wma", "mp4", "mkv", "avi", "mov"]
            for ext in extensions:
                for f in Path(folder).glob(f"*.{ext}"):
                    if str(f) not in self.metadata_files:
                        self.metadata_files.append(str(f))
                        self.metadata_list.addItem(f.name)
    
    def _on_metadata_item_clicked(self, item):
        """When a file is clicked, show its metadata."""
        idx = self.metadata_list.row(item)
        if 0 <= idx < len(self.metadata_files):
            self._read_single_metadata(self.metadata_files[idx])
    
    def _read_single_metadata(self, filepath: str):
        """Read metadata from a single file and display it."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            filepath
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.current_metadata = data
                
                lines = []
                lines.append(f"File: {os.path.basename(filepath)}")
                lines.append("-" * 40)
                
                if "format" in data:
                    fmt = data["format"]
                    duration = float(fmt.get('duration', 0))
                    mins, secs = divmod(duration, 60)
                    lines.append(f"Duration: {int(mins)}:{int(secs):02d}")
                    
                    size = int(fmt.get('size', 0))
                    lines.append(f"Size: {size / 1024 / 1024:.2f} MB")
                    
                    if "tags" in fmt:
                        lines.append("\nCurrent Tags:")
                        for key, value in fmt["tags"].items():
                            lines.append(f"  {key}: {value}")
                
                self.metadata_text.setPlainText("\n".join(lines))
            else:
                self.metadata_text.setPlainText(f"Error reading: {result.stderr[:200]}")
        except Exception as e:
            self.metadata_text.setPlainText(f"Error: {str(e)}")
    
    def read_metadata(self):
        """Read metadata for selected file."""
        selected = self.metadata_list.selectedItems()
        if selected:
            idx = self.metadata_list.row(selected[0])
            if 0 <= idx < len(self.metadata_files):
                self._read_single_metadata(self.metadata_files[idx])
    
    def apply_batch_metadata(self):
        """Apply metadata tags to all selected files."""
        selected_items = self.metadata_list.selectedItems()
        if not selected_items:
            if self.metadata_files:
                reply = QMessageBox.question(
                    self, "Apply to All?",
                    f"No files selected. Apply tags to all {len(self.metadata_files)} files?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                indices = list(range(len(self.metadata_files)))
            else:
                QMessageBox.warning(self, "No Files", "Please add files first.")
                return
        else:
            indices = [self.metadata_list.row(item) for item in selected_items]
        
        # Gather tag values
        artist = self.batch_artist.text().strip()
        album = self.batch_album.text().strip()
        year = self.batch_year.text().strip()
        genre = self.batch_genre.currentText().strip()
        album_artist = self.batch_album_artist.text().strip()
        comment = self.batch_comment.text().strip()
        auto_track = self.auto_track_numbers.isChecked()
        
        if not any([artist, album, year, genre, album_artist, comment, auto_track]):
            QMessageBox.warning(self, "No Tags", "Please enter at least one tag to apply.")
            return
        
        self.metadata_progress.setVisible(True)
        self.metadata_progress.setMaximum(len(indices))
        self.metadata_progress.setValue(0)
        
        success_count = 0
        for i, idx in enumerate(indices):
            filepath = self.metadata_files[idx]
            self.metadata_progress.setValue(i)
            
            inp = Path(filepath)
            out = inp.parent / f"{inp.stem}_tagged{inp.suffix}"
            
            cmd = ["ffmpeg", "-y", "-i", str(inp)]
            
            if artist:
                cmd.extend(["-metadata", f"artist={artist}"])
            if album:
                cmd.extend(["-metadata", f"album={album}"])
            if year:
                cmd.extend(["-metadata", f"date={year}"])
            if genre:
                cmd.extend(["-metadata", f"genre={genre}"])
            if album_artist:
                cmd.extend(["-metadata", f"album_artist={album_artist}"])
            if comment:
                cmd.extend(["-metadata", f"comment={comment}"])
            if auto_track:
                track_num = i + 1
                cmd.extend(["-metadata", f"track={track_num}/{len(indices)}"])
            
            cmd.extend(["-c", "copy", str(out)])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    os.replace(str(out), str(inp))
                    success_count += 1
                    self.log(f"Tagged: {inp.name}")
                else:
                    self.log(f"Error tagging {inp.name}: {result.stderr[:50]}")
                    if out.exists():
                        out.unlink()
            except Exception as e:
                self.log(f"Error: {str(e)}")
        
        self.metadata_progress.setValue(len(indices))
        self.metadata_progress.setVisible(False)
        
        QMessageBox.information(
            self, "Complete",
            f"Successfully tagged {success_count}/{len(indices)} files."
        )
    
    def export_metadata(self):
        if not self.current_metadata:
            QMessageBox.warning(self, "No Data", "Please click a file to read its metadata first.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Metadata", "", "JSON Files (*.json)"
        )
        if filepath:
            with open(filepath, "w") as f:
                json.dump(self.current_metadata, f, indent=2)
            self.log(f"Exported metadata to: {filepath}")
            QMessageBox.information(self, "Exported", f"Metadata saved to:\n{filepath}")
    
    def clear_file_metadata(self):
        selected_items = self.metadata_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select files to clear metadata from.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm",
            f"This will remove all metadata from {len(selected_items)} file(s). Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        indices = [self.metadata_list.row(item) for item in selected_items]
        
        for idx in indices:
            filepath = self.metadata_files[idx]
            inp = Path(filepath)
            out = inp.parent / f"{inp.stem}_clean{inp.suffix}"
            
            cmd = ["ffmpeg", "-y", "-i", str(inp), "-map_metadata", "-1", "-c", "copy", str(out)]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    os.replace(str(out), str(inp))
                    self.log(f"Cleared metadata: {inp.name}")
                else:
                    self.log(f"Error: {result.stderr[:80]}")
            except Exception as e:
                self.log(f"Error: {str(e)}")
        
        QMessageBox.information(self, "Done", f"Cleared metadata from {len(indices)} file(s).")
    
    # =========================================================================
    # DOWNLOADER TAB
    # =========================================================================
    def create_downloader_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # URL input
        url_group = QGroupBox("URL Input")
        url_layout = QVBoxLayout(url_group)
        
        url_layout.addWidget(QLabel("Single URL:"))
        self.download_url = QLineEdit()
        self.download_url.setPlaceholderText("https://youtube.com/watch?v=... or playlist URL")
        url_layout.addWidget(self.download_url)
        
        url_layout.addWidget(QLabel("Batch URLs (one per line):"))
        self.batch_urls = QTextEdit()
        self.batch_urls.setMaximumHeight(80)
        url_layout.addWidget(self.batch_urls)
        
        layout.addWidget(url_group)
        
        # Options
        opt_group = QGroupBox("Download Options")
        opt_layout = QHBoxLayout(opt_group)
        
        opt_layout.addWidget(QLabel("Type:"))
        self.download_type_combo = QComboBox()
        self.download_type_combo.addItems([
            "Video + Audio", "Audio Only (MP3)", "Audio Only (WAV)", "Audio Only (FLAC)"
        ])
        opt_layout.addWidget(self.download_type_combo)
        
        opt_layout.addSpacing(20)
        opt_layout.addWidget(QLabel("Quality:"))
        self.download_quality_combo = QComboBox()
        self.download_quality_combo.addItems(["Best", "1080p", "720p", "480p", "360p"])
        opt_layout.addWidget(self.download_quality_combo)
        
        opt_layout.addStretch()
        layout.addWidget(opt_group)
        
        # Playlist options
        playlist_group = QGroupBox("Playlist & Extras")
        playlist_layout = QHBoxLayout(playlist_group)
        
        self.is_playlist_check = QCheckBox("Download as Playlist")
        playlist_layout.addWidget(self.is_playlist_check)
        
        playlist_layout.addSpacing(20)
        playlist_layout.addWidget(QLabel("Start:"))
        self.playlist_start_spin = QSpinBox()
        self.playlist_start_spin.setRange(0, 9999)
        self.playlist_start_spin.setSpecialValueText("-")
        playlist_layout.addWidget(self.playlist_start_spin)
        
        playlist_layout.addWidget(QLabel("End:"))
        self.playlist_end_spin = QSpinBox()
        self.playlist_end_spin.setRange(0, 9999)
        self.playlist_end_spin.setSpecialValueText("-")
        playlist_layout.addWidget(self.playlist_end_spin)
        
        playlist_layout.addSpacing(30)
        self.embed_thumb_check = QCheckBox("Embed Thumbnail")
        self.embed_thumb_check.setChecked(True)
        playlist_layout.addWidget(self.embed_thumb_check)
        
        self.embed_subs_check = QCheckBox("Embed Subtitles")
        playlist_layout.addWidget(self.embed_subs_check)
        
        playlist_layout.addStretch()
        layout.addWidget(playlist_group)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.download_progress = QProgressBar()
        progress_layout.addWidget(self.download_progress)
        
        self.download_status = QLabel("Ready")
        self.download_status.setObjectName("statusLabel")
        self.download_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.download_status)
        
        layout.addLayout(progress_layout)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("primaryButton")
        self.download_btn.clicked.connect(self.start_download)
        btn_row.addWidget(self.download_btn)
        
        info_btn = QPushButton("Get Info")
        info_btn.clicked.connect(self.get_video_info)
        btn_row.addWidget(info_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        layout.addStretch()
        return tab
    
    def get_video_info(self):
        url = self.download_url.text().strip()
        if not url:
            QMessageBox.warning(self, "No URL", "Please enter a URL.")
            return
        
        self.download_status.setText("Fetching info...")
        
        def fetch_info():
            cmd = ["yt-dlp", "--dump-json", "--no-playlist", url]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    title = info.get("title", "Unknown")
                    duration = info.get("duration", 0)
                    mins, secs = divmod(duration, 60)
                    uploader = info.get("uploader", "Unknown")
                    
                    self.log(f"Title: {title}")
                    self.log(f"Duration: {int(mins)}:{int(secs):02d}")
                    self.log(f"Uploader: {uploader}")
                    self.download_status.setText(f"Ready: {title[:50]}...")
                else:
                    self.log(f"Error: {result.stderr[:100]}")
                    self.download_status.setText("Error fetching info")
            except Exception as e:
                self.log(f"Error: {str(e)}")
                self.download_status.setText("Error")
        
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def start_download(self):
        if not self.ytdlp_ok:
            QMessageBox.critical(self, "Missing Dependency", "yt-dlp is not installed.")
            return
        
        single_url = self.download_url.text().strip()
        batch_text = self.batch_urls.toPlainText().strip()
        
        urls = []
        if single_url:
            urls.append(single_url)
        if batch_text:
            urls.extend([u.strip() for u in batch_text.split("\n") if u.strip()])
        
        if not urls:
            QMessageBox.warning(self, "No URL", "Please enter at least one URL.")
            return
        
        options = {
            "type": self.download_type_combo.currentText(),
            "quality": self.download_quality_combo.currentText(),
            "playlist": self.is_playlist_check.isChecked(),
            "thumbnail": self.embed_thumb_check.isChecked(),
            "subtitles": self.embed_subs_check.isChecked(),
            "playlist_start": self.playlist_start_spin.value() if self.playlist_start_spin.value() > 0 else None,
            "playlist_end": self.playlist_end_spin.value() if self.playlist_end_spin.value() > 0 else None
        }
        
        self.download_btn.setEnabled(False)
        self.download_progress.setValue(0)
        
        self.current_worker = DownloadWorker(urls, options, self.output_dir)
        self.current_worker.progress.connect(
            lambda c, t: self.download_progress.setValue(int(c * 100 / t) if t > 0 else 0)
        )
        self.current_worker.log_message.connect(self.log)
        self.current_worker.status_update.connect(self.download_status.setText)
        self.current_worker.finished_signal.connect(self._on_download_finished)
        self.current_worker.start()
    
    def _on_download_finished(self, message: str):
        self.download_status.setText(message)
        self.download_btn.setEnabled(True)
        self.log(f"Output directory: {self.output_dir}")
    
    # =========================================================================
    # SETTINGS
    # =========================================================================
    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setFixedSize(450, 300)
        layout = QVBoxLayout(dialog)
        
        # Output directory
        dir_group = QGroupBox("Output Directory")
        dir_layout = QVBoxLayout(dir_group)
        
        dir_entry = QLineEdit(str(self.output_dir))
        dir_layout.addWidget(dir_entry)
        
        dir_btn_row = QHBoxLayout()
        
        def browse_dir():
            folder = QFileDialog.getExistingDirectory(dialog, "Select Output Directory")
            if folder:
                dir_entry.setText(folder)
        
        def save_dir():
            self.output_dir = Path(dir_entry.text())
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"Output directory set to: {self.output_dir}")
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(browse_dir)
        dir_btn_row.addWidget(browse_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(save_dir)
        dir_btn_row.addWidget(save_btn)
        
        dir_btn_row.addStretch()
        dir_layout.addLayout(dir_btn_row)
        
        layout.addWidget(dir_group)
        
        # Open output folder button
        open_btn = QPushButton("Open Output Folder")
        open_btn.clicked.connect(lambda: subprocess.run(
            ["xdg-open" if os.name != "nt" else "explorer", str(self.output_dir)]
        ))
        layout.addWidget(open_btn)
        
        layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def start_conversion(self, task_type: str, files: List[str], options: dict,
                         progress_bar: QProgressBar, status_label: QLabel, button: QPushButton):
        """Start a conversion worker."""
        button.setEnabled(False)
        progress_bar.setValue(0)
        status_label.setText("Starting...")
        
        self.current_worker = ConversionWorker(task_type, files, options, self.output_dir)
        self.current_worker.progress.connect(
            lambda c, t: progress_bar.setValue(int(c * 100 / t) if t > 0 else 0)
        )
        self.current_worker.log_message.connect(self.log)
        self.current_worker.finished_signal.connect(
            lambda msg: self._on_conversion_finished(msg, status_label, button)
        )
        self.current_worker.start()
    
    def _on_conversion_finished(self, message: str, status_label: QLabel, button: QPushButton):
        status_label.setText(message)
        button.setEnabled(True)
        self.log(f"Output directory: {self.output_dir}")


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    
    window = VDToolWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
