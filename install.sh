#!/bin/bash

# Define installation paths
INSTALL_DIR="$HOME/.local/bin"
KDE_SERVICE_MENUS_DIR="$HOME/.local/share/kservices5/ServiceMenus" # For Plasma 5 & 6 (kservices6 is often symlinked)

SCRIPT_NAME="iso_mount_tool.py"
SERVICE_TEMPLATE_NAME="iso_mount_service.desktop.template"
SERVICE_FILE_NAME="iso_mount_service.desktop"

SCRIPT_SOURCE="./$SCRIPT_NAME"
SERVICE_TEMPLATE_SOURCE="./$SERVICE_TEMPLATE_NAME"

# --- 1. Create directories if they don't exist ---
echo "Creating necessary directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$KDE_SERVICE_MENUS_DIR"

# --- 2. Copy the Python script ---
echo "Copying $SCRIPT_NAME to $INSTALL_DIR..."
cp "$SCRIPT_SOURCE" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
echo "$SCRIPT_NAME is now executable."

# --- 3. Generate and copy the KDE Service Menu file ---
echo "Generating $SERVICE_FILE_NAME..."
ACTUAL_SCRIPT_PATH="$INSTALL_DIR/$SCRIPT_NAME"
sed "s|{SCRIPT_PATH}|$ACTUAL_SCRIPT_PATH|g" "$SERVICE_TEMPLATE_SOURCE" > "$KDE_SERVICE_MENUS_DIR/$SERVICE_FILE_NAME"
echo "KDE service menu file created at $KDE_SERVICE_MENUS_DIR/$SERVICE_FILE_NAME"

# --- 4. Refresh KDE Service Menus ---
echo "Refreshing KDE service menus..."
kbuildsycoca5 --noincremental
# For older KDE versions or if the above doesn't work, try a full restart of Plasma or logout/login.
echo "KDE service menus refreshed. You might need to log out and back in for changes to fully apply."

# --- 5. Instructions for passwordless sudo ---
echo ""
echo "======================================================================="
echo "  INSTALLATION COMPLETE!"
echo "  For a smooth experience without password prompts, you need to allow"
echo "  'mount' and 'umount' commands to be run by your user without a password."
echo ""
echo "  WARNING: Modifying sudoers grants powerful permissions. Proceed with"
echo "           caution. Only do this if you understand the security implications."
echo ""
echo "  To do this:"
echo "  1. Run: sudo visudo"
echo "  2. Add the following line to the end of the file (replace 'your_username' with your actual username):"
echo ""
echo "     your_username ALL=(ALL) NOPASSWD: /usr/bin/mount, /usr/bin/umount"
echo ""
echo "     (This allows your user to run mount and umount commands directly without password.)"
echo ""
echo "  Alternatively, if you prefer to be prompted for your password every time,"
echo "  you can skip the sudoers modification. The script will simply ask for it."
echo "======================================================================="
echo ""
echo "To test: Right-click an .iso file in Dolphin/Files. You should see an 'ISO Tools' submenu."