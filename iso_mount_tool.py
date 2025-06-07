#!/usr/bin/env python3
import os
import sys
import subprocess
import hashlib
import re

# Base directory for ISO mounts in the user's home directory
# This ensures mount points are consistent and not lost on reboot (like /tmp would be).
BASE_MOUNT_DIR = os.path.join(os.path.expanduser("~"), ".iso_mounts")

def sanitize_filename(filename):
    """Sanitizes a filename to be safe for directory names."""
    filename = re.sub(r'[^\w.-]', '_', filename) # Replace non-alphanumeric/dot/dash with underscore
    filename = re.sub(r'_{2,}', '_', filename)    # Replace multiple underscores with single
    return filename.strip('_')                   # Remove leading/trailing underscores

def get_mount_point(iso_path):
    """Generates a consistent and unique mount point path for a given ISO."""
    # Get the base filename without extension
    iso_name = os.path.splitext(os.path.basename(iso_path))[0]
    
    # Create a short hash of the full path for uniqueness, handling potential conflicts
    path_hash = hashlib.sha256(iso_path.encode()).hexdigest()[:8] # Use first 8 chars

    # Combine sanitized name and hash for the mount directory
    mount_dir_name = sanitize_filename(f"{iso_name}_{path_hash}")
    
    return os.path.join(BASE_MOUNT_DIR, mount_dir_name)

def is_mounted(mount_point):
    """Checks if a given path is currently a mount point."""
    # Use os.path.ismount, which relies on stat() system call.
    # It returns True if the path is a mount point, False otherwise.
    return os.path.ismount(mount_point)

def mount_iso(iso_path):
    iso_path = os.path.abspath(iso_path)

    if not os.path.exists(iso_path):
        print(f"Error: ISO file not found at '{iso_path}'", file=sys.stderr)
        sys.exit(1)
    if not iso_path.lower().endswith(".iso"):
        print(f"Error: '{iso_path}' does not appear to be an ISO file.", file=sys.stderr)
        sys.exit(1)

    mount_point = get_mount_point(iso_path)

    if is_mounted(mount_point):
        print(f"Info: '{iso_path}' is already mounted at '{mount_point}'.")
        # If already mounted, open the directory for the user
        try:
            subprocess.Popen(['xdg-open', mount_point])
        except FileNotFoundError:
            print(f"Warning: 'xdg-open' not found. Cannot automatically open '{mount_point}'.")
        sys.exit(0) # Exit successfully if already mounted

    # Ensure base mount directory exists
    try:
        os.makedirs(BASE_MOUNT_DIR, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create base mount directory '{BASE_MOUNT_DIR}': {e}", file=sys.stderr)
        sys.exit(1)

    # Create specific mount point directory for this ISO
    try:
        os.makedirs(mount_point, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create mount directory '{mount_point}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Attempting to mount '{iso_path}' to '{mount_point}'...")
        # We assume `sudo` is configured to allow mount/umount passwordless for this script
        # If not, the user will be prompted for password by the calling terminal.
        subprocess.run(['mount', '-o', 'loop', iso_path, mount_point], check=True, text=True, capture_output=True)
        print(f"Successfully mounted '{iso_path}' at '{mount_point}'.")
        print("\n--- Next Steps ---")
        print(f"You can now access its contents in your file manager, or directly via: '{mount_point}'")
        print(f"To unmount, right-click the original ISO file again and select 'Unmount ISO'.")
        
        # Open the mounted directory in the file manager
        try:
            subprocess.Popen(['xdg-open', mount_point])
        except FileNotFoundError:
            print(f"Warning: 'xdg-open' not found. Cannot automatically open '{mount_point}'.")

    except subprocess.CalledProcessError as e:
        print(f"Error mounting ISO:\nStdOut: {e.stdout}\nStdErr: {e.stderr}", file=sys.stderr)
        # Clean up the created directory if mount fails and it's empty
        if os.path.exists(mount_point) and not os.listdir(mount_point):
            try:
                os.rmdir(mount_point)
                print(f"Cleaned up empty directory '{mount_point}' after failed mount.")
            except OSError as ex:
                print(f"Warning: Could not remove empty mount directory '{mount_point}': {ex}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'mount' command not found. Please ensure it is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)

def unmount_iso(iso_path):
    iso_path = os.path.abspath(iso_path)
    mount_point = get_mount_point(iso_path)

    if not os.path.exists(mount_point):
        print(f"Info: Mount point '{mount_point}' for '{iso_path}' does not exist.")
        sys.exit(0)

    if not is_mounted(mount_point):
        print(f"Info: '{iso_path}' (or its mount point '{mount_point}') is not currently mounted or is not a mount point.", file=sys.stderr)
        # Try to clean up the directory if it's there and empty, even if not mounted
        if os.path.exists(mount_point) and not os.listdir(mount_point):
            try:
                os.rmdir(mount_point)
                print(f"Cleaned up empty directory: '{mount_point}'")
            except OSError as e:
                print(f"Warning: Could not remove empty directory '{mount_point}': {e}", file=sys.stderr)
        sys.exit(0)

    try:
        print(f"Attempting to unmount '{mount_point}'...")
        subprocess.run(['umount', mount_point], check=True, text=True, capture_output=True)
        print(f"Successfully unmounted '{mount_point}'.")
        
        # Remove the now empty mount point directory
        if os.path.exists(mount_point) and not os.listdir(mount_point):
            try:
                os.rmdir(mount_point)
                print(f"Cleaned up mount directory: '{mount_point}'")
            except OSError as e:
                print(f"Warning: Could not remove empty directory '{mount_point}': {e}", file=sys.stderr)
        elif os.path.exists(mount_point):
            print(f"Warning: Mount directory '{mount_point}' is not empty after unmount, leaving it.")
            print("You may need to manually clean up its contents and remove it if it's no longer needed.")

    except subprocess.CalledProcessError as e:
        print(f"Error unmounting '{mount_point}':\nStdOut: {e.stdout}\nStdErr: {e.stderr}", file=sys.stderr)
        print("Ensure no files are open within the mounted directory and try again.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'umount' command not found. Please ensure it is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: iso_mount_tool.py <action> <iso_path>", file=sys.stderr)
        print("Actions: mount, unmount", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    iso_path = sys.argv[2]

    if action == "mount":
        mount_iso(iso_path)
    elif action == "unmount":
        unmount_iso(iso_path)
    else:
        print(f"Error: Unknown action '{action}'. Use 'mount' or 'unmount'.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()