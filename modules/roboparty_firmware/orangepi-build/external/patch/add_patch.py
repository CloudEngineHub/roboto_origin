import os
import sys

# --- Default configuration (if no command line arguments provided) ---
# 1. Path to your local source file
LOCAL_SOURCE_FILE = "my-new-board.dts" 

# 2. Target path in the kernel source tree (Note: do not start with /)
# It should be the directory where the file will be created, OR the full path including filename.
KERNEL_TARGET_PATH = "arch/arm64/boot/dts/rockchip/my-new-board.dts"
# ----------------------------------------

def generate_create_file_patch(local_file_path, target_kernel_path):
    # Check if local file exists
    if not os.path.exists(local_file_path):
        print("Error: Local source file '{}' not found.".format(local_file_path))
        return

    # Generate output filename: original filename + .patch
    base_name = os.path.basename(local_file_path)
    output_patch_filename = "{}.patch".format(base_name)

    # If target_kernel_path looks like a directory (no extension matching source), append filename
    # This automatically fixes the issue where user only provides directory path
    if os.path.basename(target_kernel_path) != base_name:
         # simple heuristic: if target path doesn't end with source filename, append it
         # Check if it looks like a directory or just a mismatched name
         # We'll assume if the user typed a directory path, they want the file inside it
         
         # However, to be safe: let's ALWAYS ensure the target path ends with the filename
         # if the last part of target path is NOT the filename.
         if not target_kernel_path.endswith(base_name):
             # Ensure we don't double slash if user provided trailing slash
             if target_kernel_path.endswith('/'):
                  target_kernel_path = target_kernel_path + base_name
             else:
                  # If target path looks like a directory (not containing dot), assume directory
                  # Or strict mode: simply append.
                  target_kernel_path = "{}/{}".format(target_kernel_path, base_name)
             
             print("Note: Appended filename to target path: {}".format(target_kernel_path))

    # Read source file content
    try:
        with open(local_file_path, "r") as f:
            content = f.read()
    except Exception as e:
        print("Error reading file {}: {}".format(local_file_path, e))
        return

    lines = content.splitlines()
    
    # Construct Patch content
    # Header format for creating a new file
    patch_str = "--- /dev/null\n"
    patch_str += "+++ b/{}\n".format(target_kernel_path)
    
    line_count = len(lines)
    patch_str += "@@ -0,0 +1,{} @@\n".format(line_count)
    
    for line in lines:
        patch_str += "+{}\n".format(line)
        
    # Ensure newline at end of patch
    if not patch_str.endswith("\n"):
        patch_str += "\n"

    # Write Patch file
    try:
        with open(output_patch_filename, "w") as f:
            f.write(patch_str)
        
        print("Success! Patch file generated: {}".format(output_patch_filename))
        print("Source content from: {}".format(local_file_path))
        print("Target path in kernel: b/{}".format(target_kernel_path))
        
    except Exception as e:
        print("Error writing patch file: {}".format(e))

if __name__ == "__main__":
    # Support command line arguments: python add_patch.py <local_file> <kernel_target_path>
    if len(sys.argv) >= 3:
        LOCAL_SOURCE_FILE = sys.argv[1]
        KERNEL_TARGET_PATH = sys.argv[2]
    
    print("Generating patch from '{}' to create '{}'...".format(LOCAL_SOURCE_FILE, KERNEL_TARGET_PATH))
    generate_create_file_patch(LOCAL_SOURCE_FILE, KERNEL_TARGET_PATH)
