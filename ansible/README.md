# Setup Fedora on Pixelbook

This is an ansible playbook to automate running commands from https://github.com/jmontleon/pixelbook-fedora

# Requirements

`sudo dnf -y install ansible-core ansible-collection-community-general ansible-collection-ansible-posix`

# Warning
This playbook makes modifications to your system. Ensure you have a backup before proceeding.

# Usage

`ansible-playbook -K playbook.yml`

# Abbreviated configuration

## Keyboard

### Capslock

#### Xfce
1. Configure a keyboard shortcut for SuperL to run `xdotool key Caps_Lock`

#### Gnome
1. Run at login or automate `xmodmap -e 'keysym Super_L = Caps_Lock'`
1. Run at login or automate `xmodmap -e 'keysym Super_R = Super_L'`

### Backlight
1. Set up a keyboard shortcut up to run `/usr/bin/pixelbook-keyboard-backlight` when you press `ctrl+space`.

### Orientation

#### Gnome
No action required for orientation

#### Xfce and Others
1. `pixelbook-display-orientation` script is available that can be set to start at login.

#### All
1. `/usr/bin/pixelbook-disable-tablet-touchpad` script is available to run automatically at login to work around the touchpad not turning off automatically in tablet mode in all DE, including Gnome.

## Touchpad
If you enable Tap to Click in Gnome or Xfce it will also enable Tap to Drag. To disable Tap to Drag you can do one of the following.

### Gnome:
This may be handled by the `pixelbook-touchpad-tweak` package, but if it's not run the following command
1. `gsettings set org.gnome.desktop.peripherals.touchpad tap-and-drag false`

## Touchscreen
1. Configure `/usr/bin/pixelbook-touchscreen-click` to run automatically at login
1. Reboot and you should be able to click, double click, and right click (two finger tap) using the touchscreen.
