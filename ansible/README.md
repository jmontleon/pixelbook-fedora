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

By default the leftmeta key is configured as capslock. If you'd like to leave it as (or change it to) leftmeta:
`ansible-playbook -K playbook.yml -e leftmeta=leftmeta`

Other valid values aside from `leftmeta` are also acceptable.

You can revert either change by omitting the extra var. You can also combine as many extra vars as you want, for example:
brightnessdown`ansible-playbook -K playbook.yml -e leftmeta=leftmeta -e sound_server=pulseaudio`
