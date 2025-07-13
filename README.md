# Video-Metadata-Modifier
Below is a well-structured README file for the provided `got` Python script, which is a Video Metadata Modifier Tool. The README includes an overview, features, installation instructions, usage examples, and other relevant details to help users understand and use the tool effectively.

---

# Video Metadata Modifier Tool

A Python-based tool for modifying or stripping video file metadata using multiple techniques (FFmpeg, ExifTool, and Mutagen). The tool supports both a command-line interface (CLI) and a graphical user interface (GUI) for ease of use. It allows users to apply device-specific metadata profiles, strip metadata, or load custom profiles to simulate different devices.

## Features

- **Modify Metadata**: Apply device-specific metadata profiles (e.g., iPhone 14 Pro, Samsung Galaxy S24 Ultra) to video files.
- **Strip Metadata**: Remove all metadata from video files using FFmpeg.
- **Multiple Methods**: Supports metadata modification using FFmpeg, ExifTool, and Mutagen (for MP4 files).
- **Supported Formats**: Works with common video formats (`.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.3gp`).
- **GUI Interface**: User-friendly graphical interface built with Tkinter for selecting files, profiles, and actions.
- **CLI Interface**: Flexible command-line interface for automation and scripting.
- **Custom Profiles**: Load and save custom device profiles in JSON format.
- **Metadata Preview**: View current or applied metadata in the GUI or CLI.
- **Custom Date Support**: Set custom creation dates for metadata.
- **Device Profiles**: Predefined profiles for popular devices (e.g., iPhone, Samsung, Google Pixel, etc.).

## Requirements

- **Python**: Version 3.6 or higher.
- **Dependencies**:
  - `mutagen`: For MP4 metadata modification.
  - `tkinter`: For the GUI (usually included with Python).
- **External Tools**:
  - **FFmpeg**: Required for metadata modification and stripping.
  - **ExifTool**: Optional, enhances metadata modification capabilities (some features limited without it).
- **Operating System**: Compatible with Windows, macOS, and Linux.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/video-metadata-modifier.git
   cd video-metadata-modifier
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install mutagen
   ```

3. **Install FFmpeg**:
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) or install via a package manager like Chocolatey (`choco install ffmpeg`).
   - **macOS**: Install via Homebrew (`brew install ffmpeg`).
   - **Linux**: Install via your package manager (e.g., `sudo apt install ffmpeg` on Ubuntu).

4. **Install ExifTool (Optional)**:
   - **Windows**: Download from [ExifTool website](https://exiftool.org/) and add to PATH.
   - **macOS**: Install via Homebrew (`brew install exiftool`).
   - **Linux**: Install via your package manager (e.g., `sudo apt install libimage-exiftool-perl` on Ubuntu).

5. **Verify Installation**:
   Run the script with the `--list-devices` flag to ensure dependencies are correctly installed:
   ```bash
   python modify_video_metadata.py --list-devices
   ```

## Usage

### Command-Line Interface (CLI)

Run the script using `python modify_video_metadata.py` with appropriate arguments.

#### Examples

1. **Modify Metadata with a Device Profile**:
   Apply an iPhone 14 Pro metadata profile to a video:
   ```bash
   python modify_video_metadata.py --input video.mp4 --device "iPhone 14 Pro" --output modified.mp4 --method ffmpeg
   ```

2. **Strip Metadata**:
   Remove all metadata from a video:
   ```bash
   python modify_video_metadata.py --input video.mp4 --strip --output stripped.mp4
   ```

3. **Use a Custom Profile**:
   Load a custom device profile from a JSON file:
   ```bash
   python modify_video_metadata.py --input video.mp4 --custom-profile custom.json --output modified.mp4
   ```

4. **Set a Custom Creation Date**:
   Modify metadata with a specific creation date:
   ```bash
   python modify_video_metadata.py --input video.mp4 --device "Samsung Galaxy S24 Ultra" --custom-date "2023-01-01 12:00:00" --output modified.mp4
   ```

5. **View Metadata**:
   Display metadata of a video file:
   ```bash
   python modify_video_metadata.py --show-metadata video.mp4
   ```

6. **List Available Device Profiles**:
   ```bash
   python modify_video_metadata.py --list-devices
   ```

7. **Launch GUI**:
   Start the graphical interface:
   ```bash
   python modify_video_metadata.py --gui
   ```

### Graphical User Interface (GUI)

1. Launch the GUI:
   ```bash
   python modify_video_metadata.py --gui
   ```

2. **GUI Features**:
   - **Select Input/Output Files**: Use the "Browse" buttons to choose input and output video files.
   - **Choose Device Profile**: Select from predefined device profiles or load a custom profile.
   - **Preview Metadata**: View the selected profile’s metadata in the preview window.
   - **Set Custom Date**: Enable and enter a custom creation date if needed.
   - **Choose Action**: Select "Modify Metadata" or "Strip Metadata".
   - **Select Method**: Choose between FFmpeg, Mutagen, or ExifTool for metadata modification.
   - **Process Video**: Click "Process Video" to execute the selected action.
   - **Progress Bar**: Displays processing status.
   - **Save/Load Profiles**: Save the current profile to a JSON file or load a custom profile.

### Custom Profile Format

Custom profiles are JSON files with metadata key-value pairs. Example:
```json
{
  "make": "Custom Device",
  "model": "Custom Model",
  "software": "Custom OS",
  "encoder": "HEVC (H.265)",
  "creation_tool": "Custom Camera"
}
```

## Supported Device Profiles

The tool includes predefined profiles for the following devices:
- iPhone 14 Pro
- Samsung Galaxy S24 Ultra
- Google Pixel 9 Pro
- Samsung Galaxy Z Fold 6
- OnePlus Open
- Xiaomi 15
- Huawei Mate 60 Pro
- Sony Xperia 5 VI
- Oppo Find N3
- Vivo X100 Pro

## Notes

- **FFmpeg is Required**: The tool will not function without FFmpeg installed.
- **ExifTool Limitations**: If ExifTool is not installed, some metadata modification features may be unavailable.
- **Mutagen Limitations**: Mutagen only supports MP4 files for metadata modification.
- **Thread Safety**: The GUI uses threading to prevent freezing during processing.
- **File Validation**: The tool checks for valid input files and supported formats before processing.

## Troubleshooting

- **FFmpeg/ExifTool Not Found**: Ensure both tools are installed and added to your system’s PATH.
- **Unsupported File Format**: Verify the input file is one of the supported formats (`.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.3gp`).
- **GUI Issues**: Ensure Tkinter is properly installed with your Python distribution.
- **Permission Errors**: Run the script with appropriate permissions if accessing restricted directories.

## Contributing

Contributions are welcome! Please submit pull requests or issues to the [GitHub repository](https://github.com/yourusername/video-metadata-modifier).

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FFmpeg](https://ffmpeg.org/), [ExifTool](https://exiftool.org/), and [Mutagen](https://mutagen.readthedocs.io/).
- Thanks to the open-source community for providing these powerful tools.

---

**Note**: Replace `https://github.com/yourusername/video-metadata-modifier` with the actual repository URL if you host this project. If you need additional sections (e.g., changelog, FAQs) or specific formatting, let me know!
