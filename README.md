# Fedora on Pixelbook

This process can be used to get Fedora installed on your Chromebook. This process will destroy your data so make sure you have backups of anything you need. When you're done ChromeOS will not be bootable and your data will be wiped.

What works and doesn't work:

| Component     | Status      |
| ------------- |-------------|
| Audio | [Working](#Audio) |
| Backlight / Brightness | [Poor](#Brightness) |
| Bluetooth | Working |
| Camera | Working |
| Keyboard | [Working](#Keyboard) |
| Sleep | Working |
| Touchpad | [Working](#Touchpad) |
| Touchscreen | [Working](#Touchscreen) |
| Wireless | Working |

## Required Hardware
- Google Pixelbook
- [SuzyQable](https://www.sparkfun.com/products/14746)
- A second computer or a USB A to USB C adapter so you can plug the other end into the Pixelbook itself

## Unlocking the Pixelbook to install the Coreboot Firmware
**These steps will wipe your data and account settings. Do not proceed if you need data on your Chromebook.**
- Press `ESC+Refresh+Power` on the Pixelbook
- At the recovery screen press `CTRL-D`
- Once you are certain your data is backed up you can confirm that you want to do this and proceed.
- At this point your Chromebook will be powerwashed and your account and data removed so once it finished log back in

## Install Coreboot
- All of the instructions for this process are at [mrchromebox.tech](https://mrchromebox.tech)
- You must open the clode-case debugging capabilities, disable write protect, and enable firmware flashing.
- To do all of this read, understand, and follow these [instructions](https://mrchromebox.tech/#devices).
- Then use the [Firmware Utility Script](https://mrchromebox.tech/#fwscript) to install the UEFI firmware.
- Do make a backup of the stock firmware and **ensure you do not lose it**.
- If you ever want to go back to ChromeOS you can use the script to restore this backup firmware. **Don't lose it.**

## Install Fedora
- Prepare a bootable [Fedora USB stick](https://fedoramagazine.org/make-fedora-usb-stick/)
- Insert it into the Pixelbook and install it normally.
- `sudo dnf copr enable jmontleon/pixelbook`

## Audio
- By default audio will not work at all.
- To enable it we need to copy some files off a recovery image. With some additional fixes the Internal mic will work as well.
- Download the latest eve recovery image from [cros-updates-serving.appspot.com](https://cros-updates-serving.appspot.com/)
- Unzip the file. As an example `unzip chromeos_13904.55.0_eve_recovery_stable-channel_mp-v2.bin.zip`
- Create device maps `sudo kpartx -av chromeos_13904.55.0_eve_recovery_stable-channel_mp-v2.bin`
- Mount the ChromeOS root filesystem `sudo mount -o ro /dev/mapper/loop0p3 /mnt`
- Copy the files:
  - `sudo cp /mnt/lib/firmware/9d71-GOOGLE-EVEMAX-0-tplg.bin /lib/firmware/`
  - `sudo cp /mnt/lib/firmware/dsp_lib_dsm_core_spt_release.bin /lib/firmware/`
  - `sudo cp /mnt/lib/firmware/intel/dsp_fw_C75061F3-F2B2-4DCC-8F9F-82ABB4131E66.bin /lib/firmware/intel`
  - `sudo mkdir -p /opt/google/dsm/`
  - `sudo cp /mnt/opt/google/dsm/dsmparam.bin /opt/google/dsm/dsmparam.bin`
- Replace pipewire with pulseaudio, otherwise the mic produces only noise `sudo dnf swap --allowerasing pipewire-pulseaudio pulseaudio`. [Pipeiwire Issue](https://gitlab.freedesktop.org/pipewire/pipewire/-/issues/1452)
- Add the ucm2 profile `sudo dnf -y install pixelbook-alsa-ucm`
- After rebooting you should have audio

## Brightness
The brightness only has two states, full or off. The backlight can be set with xrandr. To get something resembling brightness adustment we'll start in this section and finish up in the keyboard section.

- `sudo usermod -aG video $USER`
- `sudo dnf install pixelbook-scripts pixelbook-udev`  

## Keyboard

### Hotkeys
- `sudo dnf -y install pixelbook-udev` if you haven't already

### Screen Orientation
- `sudo dnf -y install pixelbook-udev` if you haven't already
- `sudo dnf -y update kernel` to get a pixelbook kernel with the sensor modules enabled.
- reboot
- Gnome handles orientation automatically. For others a script `pixelbook-display-orientation` is available in the `pixelbook-scripts` package that can be set to autostart. 

### Capslock
To use the Search key as a Capslock:
- `sudo dnf -y install xdotool`
- Configure a keyboard shortcut for SuperL to run `xdotool key Caps_Lock`

### Display backlight
Create keyboard shortcuts for the brightnessup and brightnessdown keys to instead run `/usr/bin/pixelbook-display-backlight --increase` and `/usr/bin/pixelbook-display-backlight --decrease` using the brightnessup and brightnessdown keys. Complete the keyboard section and reboot for this to function.

### Keyboard Backlight
- `sudo dnf -y install pixelbook-scripts` if you haven't already
- Add yourself to the input group: `sudo usermod -aG input $USER`
Set up a keyboard shortcut up to run `/usr/bin/pixelbook-keyboard-backlight` when you press `ctrl+space`.

## Touchpad
I like Tapping to click and no tapping to drag. While this can be enabled in the Xfce touchpad settings I was unable to disable tapping to drag. To disable it I created an xorg.conf file as root and rebooted. 

- If you want the same tweak run `sudo dnf -y install pixelbook-touchpad-tweak`

## Touchscreen
- Install the dependencies: `sudo dnf -y install pixebolbook-scripts` if you haven't already
- Add yourself to the input group if you haven't already: `sudo usermod -aG input $USER`
- Configure `/usr/bin/pixelbook-touchscreen-click` to run automatically at login 
- Reboot and you should be able to click, double click, and right click (two finger tap) using the touchscreen.
