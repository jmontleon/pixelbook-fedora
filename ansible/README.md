# Setup Fedora on Pixelbook

A basic ansible playbook for running the commands from https://github.com/jmontleon/pixelbook-fedora

Optionally setup passwordless sudo to make life a bit easier and make you enter your password a few less times (Google it if you don't know how to do this)

*WARNING*: Before running this script, and for your own protection, make sure you have a backup of your files and/or a disk image of your Pixelbook via something like CloneZilla in case something goes wrong while running this setup.

```
sudo dnf update

./run-ansible.sh
```


