# Setup Fedora on Pixelbook

This is an ansible playbook to automate running commands from https://github.com/jmontleon/pixelbook-fedora

# Requirements

`sudo dnf -y install ansible-core ansible-collection-community-general ansible-collection-ansible-posix`

# Warning
This playbook makes modifications to your system. Ensure you have a backup before proceeding.

# Usage

`ansible-playbook -K playbook.yml`

If you'd like (to continue) to use pulseaudio:
`ansible-playbook -K playbook.yml -e sound_server=pulseaudio`

# Abbreviated configuration

## Keyboard

### Capslock

#### Xfce
1. Configure a keyboard shortcut for SuperL to run `xdotool key Caps_Lock`

#### Gnome
1. Run at login or automate `xmodmap -e 'keysym Super_L = Caps_Lock'`
1. Run at login or automate `xmodmap -e 'keysym Super_R = Super_L'`
