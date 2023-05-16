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
