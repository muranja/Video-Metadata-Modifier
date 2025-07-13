#!/usr/bin/env python3
"""
Video Metadata Modifier Tool
A Python-based tool for modifying or stripping video file metadata using multiple techniques.
"""

import argparse
import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from mutagen.mp4 import MP4, MP4Tags

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lazy-loaded device profiles
def get_device_profiles() -> Dict[str, Dict[str, str]]:
    if not hasattr(get_device_profiles, 'cache'):
        get_device_profiles.cache = {
            "iPhone 14 Pro": {
                "make": "Apple", "model": "iPhone 14 Pro", "software": "iOS 16.0",
                "encoder": "HEVC (H.265)", "creation_tool": "iPhone 14 Pro back triple camera 6.86mm f/1.78"
            },
            "Samsung Galaxy S24 Ultra": {
                "make": "Samsung", "model": "SM-S928B", "software": "Android 14",
                "encoder": "HEVC (H.265)", "creation_tool": "Samsung Galaxy S24 Ultra"
            },
            "Google Pixel 9 Pro": {
                "make": "Google", "model": "Pixel 9 Pro", "software": "Android 15",
                "encoder": "HEVC (H.265)", "creation_tool": "Google Pixel 9 Pro"
            },
            "Samsung Galaxy Z Fold 6": {
                "make": "Samsung", "model": "SM-F956B", "software": "Android 14",
                "encoder": "HEVC (H.265)", "creation_tool": "Samsung Galaxy Z Fold 6"
            },
            "OnePlus Open": {
                "make": "OnePlus", "model": "CPH2517", "software": "Android 14",
                "encoder": "HEVC (H.265)", "creation_tool": "OnePlus Open"
            },
            "Xiaomi 15": {
                "make": "Xiaomi", "model": "2405CPH5DC", "software": "Android 15",
                "encoder": "HEVC (H.265)", "creation_tool": "Xiaomi 15"
            },
            "Huawei Mate 60 Pro": {
                "make": "Huawei", "model": "DCO-AL00", "software": "HarmonyOS 4.0",
                "encoder": "HEVC (H.265)", "creation_tool": "Huawei Mate 60 Pro"
            },
            "Sony Xperia 5 VI": {
                "make": "Sony", "model": "XQ-DQ74", "software": "Android 14",
                "encoder": "HEVC (H.265)", "creation_tool": "Sony Xperia 5 VI"
            },
            "Oppo Find N3": {
                "make": "Oppo", "model": "CPH2511", "software": "Android 13",
                "encoder": "HEVC (H.265)", "creation_tool": "Oppo Find N3"
            },
            "Vivo X100 Pro": {
                "make": "Vivo", "model": "V2303A", "software": "Android 14",
                "encoder": "HEVC (H.265)", "creation_tool": "Vivo X100 Pro"
            }
        }
    return get_device_profiles.cache

SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.3gp']

class VideoMetadataModifier:
    """Main class for video metadata modification and stripping operations."""
    _metadata_cache = {}

    def check_tools(self):
        """Check if required tools (ffmpeg, exiftool) are installed."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            logger.info("FFmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("FFmpeg is not installed or not accessible")
            raise RuntimeError("FFmpeg is required but not found. Please install FFmpeg.")
        try:
            subprocess.run(['exiftool', '-ver'], capture_output=True, check=True)
            logger.info("ExifTool is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("ExifTool not found. Some metadata features may be limited.")

    def validate_input_file(self, file_path: str) -> bool:
        """Validate that the input file exists and is a supported video format."""
        if not os.path.exists(file_path):
            logger.error(f"Input file does not exist: {file_path}")
            return False
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            logger.error(f"Unsupported file format: {file_ext}")
            return False
        return True

    def get_current_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract current metadata from video file with detailed parsing."""
        if file_path not in self._metadata_cache:
            try:
                cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', '-show_chapters', '-show_packets', file_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                metadata = json.loads(result.stdout)
                metadata['file_info'] = {
                    'file_name': Path(file_path).name,
                    'file_size': os.path.getsize(file_path) / (1024 * 1024),  # MB
                    'file_format': Path(file_path).suffix[1:].upper(),
                    'date_created': datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                    'date_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                }
                self._metadata_cache[file_path] = metadata
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to read metadata: {e}")
                self._metadata_cache[file_path] = {}
        return self._metadata_cache[file_path]

    def build_metadata_args(self, profile: Dict[str, str], custom_date: Optional[str] = None) -> List[str]:
        """Build metadata arguments for FFmpeg or ExifTool."""
        args = []
        for key, value in profile.items():
            args.extend(['-metadata', f'{key}={value}'])
        if custom_date:
            args.extend(['-metadata', f'creation_time={custom_date}'])
        return args

    def modify_metadata_mutagen(self, input_file: str, output_file: str, 
                              device_profile: Dict[str, str], custom_date: Optional[str] = None) -> bool:
        """Modify metadata using mutagen (limited to MP4)."""
        if Path(input_file).suffix.lower() != '.mp4':
            logger.warning("Mutagen supports only MP4 files. Skipping.")
            return False
        try:
            video = MP4(input_file)
            tags = video.tags if video.tags else MP4Tags()
            for key, value in device_profile.items():
                tags[key] = value
            if custom_date:
                tags['creation_time'] = custom_date
            video.save(output_file)
            logger.info(f"Metadata modified with mutagen. Output saved to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Mutagen error: {e}")
            return False

    def modify_metadata_exiftool(self, input_file: str, output_file: str, 
                               device_profile: Dict[str, str], custom_date: Optional[str] = None) -> bool:
        """Modify metadata using ExifTool."""
        try:
            cmd = ['exiftool', '-o', output_file] + [f'-{k}={v}' for k, v in device_profile.items()]
            if custom_date:
                cmd.append(f'-CreateDate={custom_date}')
                cmd.append(f'-ModifyDate={custom_date}')
            cmd.extend(['-overwrite_original', input_file])
            logger.info(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Metadata modified with ExifTool. Output saved to {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"ExifTool error: {e.stderr}")
            return False

    def modify_metadata_ffmpeg(self, input_file: str, output_file: str, 
                             device_profile: Dict[str, str], custom_date: Optional[str] = None) -> bool:
        """Modify video metadata using FFmpeg."""
        try:
            cmd = [
                'ffmpeg', '-i', input_file, '-c', 'copy', '-map_metadata', '0',
                *self.build_metadata_args(device_profile, custom_date), '-y', output_file
            ]
            logger.info(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Metadata successfully modified with FFmpeg. Output saved to {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return False

    def modify_metadata(self, input_file: str, output_file: str, 
                       device_profile: Dict[str, str], custom_date: Optional[str] = None, 
                       method: str = 'ffmpeg') -> bool:
        """Modify metadata using the specified method."""
        methods = {
            'mutagen': self.modify_metadata_mutagen,
            'exiftool': self.modify_metadata_exiftool,
            'ffmpeg': self.modify_metadata_ffmpeg
        }
        if method not in methods:
            logger.error(f"Unsupported method: {method}. Falling back to FFmpeg.")
            method = 'ffmpeg'
        return methods[method](input_file, output_file, device_profile, custom_date)

    def strip_metadata(self, input_file: str, output_file: str) -> bool:
        """Strip all metadata using FFmpeg (primary method)."""
        try:
            cmd = ['ffmpeg', '-i', input_file, '-c', 'copy', '-map_metadata', '-1', '-y', output_file]
            logger.info(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Metadata stripped. Output saved to {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return False

    def load_custom_profile(self, profile_path: str) -> Dict[str, str]:
        """Load custom device profile from JSON file."""
        try:
            with open(profile_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load custom profile: {e}")
            return {}

    def save_profile(self, profile: Dict[str, str], save_path: str) -> bool:
        """Save device profile to JSON file."""
        try:
            with open(save_path, 'w') as f:
                json.dump(profile, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return False

class VideoMetadataGUI:
    """Graphical user interface for the video metadata modifier."""
    
    def __init__(self):
        self.modifier = VideoMetadataModifier()
        self.modifier.check_tools()
        self.root = tk.Tk()
        self.setup_gui()
    
    def setup_gui(self):
        """Initialize the GUI components."""
        self.root.title("Video Metadata Modifier")
        self.root.geometry("800x600")
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input file
        ttk.Label(main_frame, text="Input Video File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_file_var = tk.StringVar()
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(input_frame, textvariable=self.input_file_var, width=50).grid(row=0, column=0)
        ttk.Button(input_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=1)
        
        # Device profile
        ttk.Label(main_frame, text="Device Profile:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.device_var = tk.StringVar()
        device_combo = ttk.Combobox(main_frame, textvariable=self.device_var, values=list(get_device_profiles().keys()))
        device_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        device_combo.bind('<<ComboboxSelected>>', self.on_device_selected)
        
        # Custom profile buttons
        profile_frame = ttk.Frame(main_frame)
        profile_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(profile_frame, text="Load Custom Profile", command=self.load_custom_profile).grid(row=0, column=0)
        ttk.Button(profile_frame, text="Save Current Profile", command=self.save_current_profile).grid(row=0, column=1)
        
        # Metadata preview
        ttk.Label(main_frame, text="Metadata Preview:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.metadata_text = tk.Text(main_frame, height=10, width=70)
        self.metadata_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Custom date
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.custom_date_var = tk.BooleanVar()
        ttk.Checkbutton(date_frame, text="Set custom creation date", variable=self.custom_date_var).grid(row=0, column=0)
        self.date_entry = ttk.Entry(date_frame, width=20)
        self.date_entry.grid(row=0, column=1)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Output file
        ttk.Label(main_frame, text="Output File:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar()
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(output_frame, textvariable=self.output_file_var, width=50).grid(row=0, column=0)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_file).grid(row=0, column=1)
        
        # Action and method selection
        self.action_var = tk.StringVar(value="modify")
        ttk.Radiobutton(main_frame, text="Modify Metadata", variable=self.action_var, value="modify").grid(row=6, column=0, pady=5)
        ttk.Radiobutton(main_frame, text="Strip Metadata", variable=self.action_var, value="strip").grid(row=6, column=1, pady=5)
        
        self.method_var = tk.StringVar(value="ffmpeg")
        ttk.Label(main_frame, text="Method:").grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(main_frame, text="FFmpeg", variable=self.method_var, value="ffmpeg").grid(row=7, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Mutagen", variable=self.method_var, value="mutagen").grid(row=8, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="ExifTool", variable=self.method_var, value="exiftool").grid(row=9, column=1, sticky=tk.W)
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Process Video", command=self.process_video)
        self.process_button.grid(row=10, column=1, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=11, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=12, column=1, sticky=tk.W, pady=5)
        
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_input_file(self):
        """Open file dialog to select input video file."""
        filetypes = [("Video files", " ".join(f"*{ext}" for ext in SUPPORTED_FORMATS)), ("All files", "*.*")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.input_file_var.set(filename)
            path = Path(filename)
            output_name = path.stem + "_processed" + path.suffix
            self.output_file_var.set(str(path.parent / output_name))

    def browse_output_file(self):
        """Open file dialog to select output location."""
        filetypes = [("Video files", " ".join(f"*{ext}" for ext in SUPPORTED_FORMATS)), ("All files", "*.*")]
        filename = filedialog.asksaveasfilename(filetypes=filetypes)
        if filename:
            self.output_file_var.set(filename)

    def on_device_selected(self, event):
        """Handle device profile selection."""
        device = self.device_var.get()
        if device in get_device_profiles():
            self.update_metadata_preview(get_device_profiles()[device])

    def update_metadata_preview(self, profile: Dict[str, str]):
        """Update the metadata preview text."""
        self.metadata_text.delete(1.0, tk.END)
        preview_text = "Selected Profile Metadata:\n\n"
        for key, value in profile.items():
            preview_text += f"{key.capitalize()}: {value}\n"
        self.metadata_text.insert(1.0, preview_text)

    def load_custom_profile(self):
        """Load custom device profile from JSON file."""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            profile = self.modifier.load_custom_profile(filename)
            if profile:
                self.update_metadata_preview(profile)
                self.device_var.set("Custom Profile")
                messagebox.showinfo("Success", "Custom profile loaded successfully!")

    def save_current_profile(self):
        """Save current profile to JSON file."""
        device = self.device_var.get()
        if device in get_device_profiles():
            filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if filename:
                if self.modifier.save_profile(get_device_profiles()[device], filename):
                    messagebox.showinfo("Success", "Profile saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to save profile.")

    def process_video(self):
        """Process the video based on selected action and method."""
        if not self.input_file_var.get() or not self.output_file_var.get():
            messagebox.showerror("Error", "Please select input and output files.")
            return

        if self.action_var.get() == "modify" and not self.device_var.get():
            messagebox.showerror("Error", "Please select a device profile for modification.")
            return

        if not self.modifier.validate_input_file(self.input_file_var.get()):
            messagebox.showerror("Error", "Invalid input file.")
            return

        def process_thread():
            self.progress.start()
            self.process_button.config(state='disabled')
            self.status_var.set("Processing...")

            success = False
            if self.action_var.get() == "modify":
                device = self.device_var.get()
                profile = get_device_profiles().get(device, {})
                if not profile and device != "Custom Profile":
                    self.status_var.set("Invalid device profile.")
                    return
                custom_date = self.date_entry.get() if self.custom_date_var.get() else None
                success = self.modifier.modify_metadata(
                    self.input_file_var.get(), self.output_file_var.get(), profile, custom_date, self.method_var.get()
                )
            elif self.action_var.get() == "strip":
                success = self.modifier.strip_metadata(self.input_file_var.get(), self.output_file_var.get())

            self.progress.stop()
            self.process_button.config(state='normal')
            if success:
                self.status_var.set("Processing completed successfully!")
                messagebox.showinfo("Success", f"Video {'metadata modified' if self.action_var.get() == 'modify' else 'metadata stripped'} successfully!")
            else:
                self.status_var.set("Processing failed.")
                messagebox.showerror("Error", f"Failed to {'modify' if self.action_var.get() == 'modify' else 'strip'} video metadata.")

        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

def main():
    """Main function for CLI interface."""
    parser = argparse.ArgumentParser(
        description="Modify or strip video metadata to simulate different devices using multiple methods.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python modify_video_metadata.py --input video.mp4 --device "iPhone 14 Pro" --output modified.mp4 --method ffmpeg
  python modify_video_metadata.py --input video.mp4 --strip --output stripped.mp4
  python modify_video_metadata.py --gui
        """
    )
    
    parser.add_argument("--input", help="Path to the input video file")
    parser.add_argument("--output", help="Path to save the modified video file")
    parser.add_argument("--device", choices=list(get_device_profiles().keys()), help="Device profile to apply")
    parser.add_argument("--custom-profile", help="Path to custom device profile JSON file")
    parser.add_argument("--custom-date", help="Custom creation date (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--strip", action="store_true", help="Strip all metadata from the video")
    parser.add_argument("--list-devices", action="store_true", help="List available device profiles")
    parser.add_argument("--gui", action="store_true", help="Launch graphical user interface")
    parser.add_argument("--show-metadata", help="Show current metadata of a video file")
    parser.add_argument("--method", choices=['ffmpeg', 'mutagen', 'exiftool'], default='ffmpeg', 
                       help="Method to modify metadata (default: ffmpeg)")

    args = parser.parse_args()

    if args.gui:
        try:
            gui = VideoMetadataGUI()
            gui.run()
        except Exception as e:
            logger.error(f"Failed to launch GUI: {e}")
            sys.exit(1)
        return

    if args.list_devices:
        print("Available device profiles:")
        for device in get_device_profiles():
            print(f"  - {device}")
        return

    if args.show_metadata:
        try:
            modifier = VideoMetadataModifier()
            modifier.check_tools()
            if modifier.validate_input_file(args.show_metadata):
                metadata = modifier.get_current_metadata(args.show_metadata)
                print(json.dumps(metadata, indent=2))
        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            sys.exit(1)
        return

    if not args.input or not args.output:
        parser.error("--input and --output are required for metadata modification or stripping")

    if args.strip and (args.device or args.custom_profile or args.custom_date):
        parser.error("--strip cannot be used with --device, --custom-profile, or --custom-date")

    if not args.strip and not args.device and not args.custom_profile:
        parser.error("Either --device, --custom-profile, or --strip must be specified")

    try:
        modifier = VideoMetadataModifier()
        modifier.check_tools()
        if not modifier.validate_input_file(args.input):
            sys.exit(1)

        if args.strip:
            success = modifier.strip_metadata(args.input, args.output)
        else:
            profile = modifier.load_custom_profile(args.custom_profile) if args.custom_profile else get_device_profiles().get(args.device, {})
            if not profile and not args.custom_profile:
                logger.error("Invalid device profile")
                sys.exit(1)
            success = modifier.modify_metadata(args.input, args.output, profile, args.custom_date, args.method)

        if success:
            print(f"Successfully {'stripped' if args.strip else 'modified'} metadata. Output saved to: {args.output}")
        else:
            print(f"Failed to {'strip' if args.strip else 'modify'} metadata.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()