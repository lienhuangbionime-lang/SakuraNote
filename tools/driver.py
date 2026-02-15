import ctypes
import os
import time
import subprocess
import sys

# Define DiaryMarker Structure
class DiaryMarker(ctypes.Structure):
    _fields_ = [
        ("text_offset", ctypes.c_uint32),
        ("text_len", ctypes.c_uint32),
        ("media_index", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
        ("created_at", ctypes.c_uint64),
        ("mood", ctypes.c_uint8),
        ("flags", ctypes.c_uint8),
        ("link_id", ctypes.c_uint16),
        ("padding", ctypes.c_uint32),
    ]

class LifeOS:
    def __init__(self):
        self.kernel_path = os.path.abspath("kernel")
        self.data_path = os.path.abspath("data")
        
        # Ensure data directory exists
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            
        # Define library path
        if os.name == 'nt':
            self.lib_path = os.path.join(self.kernel_path, "diary_kernel.dll")
        else:
            self.lib_path = os.path.join(self.kernel_path, "diary_kernel.so")
            
        # Run compilation
        print("Compiling Kernel...")
        compile_script = os.path.join(self.kernel_path, "compile.py")
        subprocess.check_call([sys.executable, compile_script])
        
        if not os.path.exists(self.lib_path):
            raise RuntimeError("Kernel compilation failed. Library file not found.")
            
        # Load Library
        self.lib = ctypes.CDLL(self.lib_path)
        
        # Define function signatures
        self.lib.write_index.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(DiaryMarker)]
        self.lib.write_index.restype = ctypes.c_int
        
        self.index_file = os.path.join(self.data_path, "life.index").encode('utf-8')
        self.text_file = os.path.join(self.data_path, "life.text")

    def log_diary(self, day_index, text, mood=0):
        # 1. Append text to life.text
        text_bytes = text.encode('utf-8')
        text_len = len(text_bytes)
        
        # Open in append binary mode to get offset
        with open(self.text_file, "ab+") as f:
            # Move to end to gauge offset
            # Note: ab+ usually positions at end, but better be sure for ftell
            f.seek(0, 2) 
            text_offset = f.tell()
            f.write(text_bytes)
            
        # 2. Prepare C Structure
        marker = DiaryMarker()
        marker.text_offset = text_offset
        marker.text_len = text_len
        marker.media_index = 0
        marker.reserved = 0
        marker.created_at = int(time.time())
        marker.mood = mood
        marker.flags = 1 # TEXT
        marker.link_id = 0
        marker.padding = 0
        
        # 3. Call C Kernel
        result = self.lib.write_index(self.index_file, day_index, ctypes.byref(marker))
        
        return result
