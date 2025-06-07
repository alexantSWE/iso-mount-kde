#!/bin/bash

# Define installation paths (must match install.sh)
INSTALL_DIR="$HOME/.local/bin"
KDE_SERVICE_MENUS_DIR="$HOME/.local/share/kservices5/ServiceMenus"

SCRIPT_NAME="iso_mount_tool.py"
SERVICE_FILE_NAME="iso_mount_service.desktop"

# Base directory for ISO mounts
BASE_MOUNT_DIR="$HOME/.iso_mounts"

# --- 1. Remove the Python script ---
echo "Removing $SCRIPT_NAME from $INSTALL_DIR..."
rm -f "$INSTALL_DIR/$SCRIPT_NAME"

# --- 2. Remove the KDE Service Menu file ---
echo "Removing $SERVICE_FILE_NAME from $KDE_SERVICE_MENUS_DIR..."
rm -f "$KDE_SERVICE_MENUS_DIR/$SERVICE_FILE_NAME"

# --- 3. Refresh KDE Service Menus ---
echo "Refreshing KDE service menus..."
kbuildsycoca5 --noincremental
echo "KDE service menus refreshed. You might need to log out and back in for changes to fully apply."

# --- 4. Inform about sudoers and mount directory ---
echo ""
echo "======================================================================="
echo "  UNINSTALLATION COMPLETE!"
echo "  Remember to manually remove the following line from your sudoers file"
echo "  if you added it during installation:"
echo ""
echo "     your_username ALL=(ALL) NOPASSWD: /usr/bin/mount, /usr/bin/umount"
echo ""
echo "  Also, the temporary mount points directory: '$BASE_MOUNT_DIR'"
echo "  was NOT automatically removed. You can delete it manually if empty:"
echo "    rmdir '$BASE_MOUNT_DIR'"
echo "  (Use 'rm -rf' if it contains files, but be careful!)"
echo "======================================================================="
echo ""