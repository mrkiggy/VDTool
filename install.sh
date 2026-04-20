#!/bin/bash
echo Installing VDTool Requires sudo
echo Setup script that completes the pyinstaller compiling and installing for you.
echo VDTool can be launched in the terminal via the 'vdtool' command.
sudo pacman -Syu yt-dlp ffmpeg python3 tk
git clone https://github.com/mrkiggy/VDTool.git
cd VDTool
python3 -m venv venv
source venv/bin/activate
pip install pyinstaller pyqt6 pillow requests 
pyinstaller --onefile --windowed vdtool.py
sudo mv dist/vdtool /usr/local/bin
cd ..
echo cleaning...
rm -rf VDTool
echo Done!
