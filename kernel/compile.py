import os
import platform
import subprocess
import sys

def compile_kernel():
    # Determine OS
    system = platform.system()
    
    # Paths
    kernel_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(kernel_dir, "diary_kernel.c")
    
    if system == "Windows":
        output_file = os.path.join(kernel_dir, "diary_kernel.dll")
        # Try gcc first (MinGW)
        try:
            print("Attempting compilation with gcc...")
            subprocess.check_call(["gcc", "-shared", "-o", output_file, source_file, "-I", kernel_dir])
            print(f"Successfully compiled to {output_file}")
            return output_file
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("gcc not found or failed.")
            
        # Try cl (MSVC)
        try:
            print("Attempting compilation with cl (MSVC)...")
            # This requires running from Developer Command Prompt
            subprocess.check_call(["cl", "/LD", source_file, "/Fe:", output_file, "/I", kernel_dir])
            print(f"Successfully compiled to {output_file}")
            return output_file
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("cl not found or failed.")
            
    else:
        # Linux/MacOS
        output_file = os.path.join(kernel_dir, "diary_kernel.so")
        try:
            print("Attempting compilation with gcc...")
            subprocess.check_call(["gcc", "-shared", "-o", output_file, "-fPIC", source_file, "-I", kernel_dir])
            print(f"Successfully compiled to {output_file}")
            return output_file
        except subprocess.CalledProcessError:
            print("gcc failed.")

    print("Compilation failed. Please ensure you have a C compiler (gcc or cl) installed and in your PATH.")
    return None

if __name__ == "__main__":
    compile_kernel()
