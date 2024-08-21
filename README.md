# Boot iDevice with iBEC.img4 on Windows OS
This guide helps boot IOS with iBEC.img4 for checkm8 iOS devices on the Windows operating system. It has been tested with the downr1n downgrade tool and also when jailbreaking an iDevice using ./downr1n.sh --jailbreak.
## Installation
Ensure you have the latest version of Python installed. <br/>
### Step 1: Install the WMI Library
- You need to install the WMI library using pip. Run the following command in your terminal:
```bash
pip install WMI
```
### Step 2: Install iDeviceBoot
- Download the latest release of iDeviceBoot. <br/>
#### If you have downgraded your iDevice using downr1n:
1. Navigate to the downr1n/boot/ directory.
2. Locate your iDevice folder.
3. Copy your iDevice folder with its files.
4. In Windows, navigate to iDeviceBoot/tools/irecovery/boot/.
5. Paste the folder here (for example, it's `iPhone9,4` with its files).
### Step 3: Boot iDevice <br/>
1. Open the command prompt (cmd) with Administrator privileges.
2. Run the following command:
```bash
python main.py
```

# Thank
- Thanks to [edwin170](https://github.com/edwin170/) for helping me understand how [downr1n](https://github.com/edwin170/downr1n/) works.
- Thanks to [L1ghtmann](https://github.com/L1ghtmann/libimobiledevice/) who provided the compiled libimobiledevice tools.
- Thanks to [pbatard](https://github.com/pbatard/libwdi/) for wdi-simple.exe.
- Thanks to [0x7ff](https://github.com/0x7ff/gaster/) for gaster.
