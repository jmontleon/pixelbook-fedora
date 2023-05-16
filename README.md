# Fedora on Pixelbook

This process can be used to get Fedora installed on your Chromebook. **This process will destroy your data so make sure you have backups of anything you need. When you're done ChromeOS will not be bootable and your data will be wiped.** See the notes below for how to adapt them for [other distrbutions](#other-distributions).

What works and doesn't work:

| Component     | Status      |
| ------------- |-------------|
| Ambient Light Sensor | Mostly Working [Issue](https://github.com/jmontleon/pixelbook-fedora/issues/18)  |
| Audio | Working |
| Brightness | [Working](#Brightness) |
| Bluetooth | Working |
| Camera | Working |
| Keyboard | [Working](#Keyboard) |
| Orientation / Tablet Mode | [Working](#Orientation) |
| Suspend | Working |
| Touchpad | [Working](#Touchpad) |
| Touchscreen | [Working](#Touchscreen) |
| Wireless | Working |

## Requirements
- Google Pixelbook (2017) **The steps below will wipe your data and account settings.**
- [SuzyQable](https://www.sparkfun.com/products/14746)
- A second computer or a USB A to USB C adapter so you can plug the other end into the Pixelbook itself
- A willingness to patiently troubleshoot and diagnose issues. This is an advanced task and yields imperfect results. Many desktop environments, display managers, and configurations have not been tested fully, if at all, and may require additional work to make function. Most of the packages, scripts, and configs provided here are workarounds to known issues for which there are currently no proper fix or configuration.

- You should know how to perform these tasks or be ready to google them for troubleshooting purposes if something goes wrong:
    - Install, remove, and update packages on Fedora
    - Enable, disable, stop, and (re)start systemd services
    - Change runlevels using systemd, including from the GRUB menu using the kernel command line
    - Change display managers and / or desktops to determine if the problem is specific to one or all.
    - Enable wireless network connections with NetworkManager or systemd-networkd from the shell.
    - Install, configure, and run playbooks with ansible

## Unlocking the Pixelbook to install the Coreboot Firmware
**These steps will wipe your data and account settings. Do not proceed if you need data on your Chromebook.**
1. Press `ESC+Refresh+Power` on the Pixelbook
1. At the recovery screen press `CTRL-D`
1. Once you are certain your data is backed up you can confirm that you want to do this and proceed.
1. At this point your Chromebook will be powerwashed and your account and data removed so once it finished log back in

## Install Coreboot
1. All of the instructions for this process are at [mrchromebox.tech](https://mrchromebox.tech)
1. You must configure [Closed Case Debug](https://chromium.googlesource.com/chromiumos/third_party/hdctools/+/HEAD/docs/ccd.md), disable write protect, and enable firmware flashing.
1. To do all of this read, understand, and follow these [instructions](https://mrchromebox.tech/#devices).
1. Then use the [Firmware Utility Script](https://mrchromebox.tech/#fwscript) to install the UEFI firmware.
1. Do make a backup of the stock firmware and **ensure you do not lose it**.
1. If you ever want to go back to ChromeOS you can use the script to restore this backup firmware. **Don't lose it.**

## Update Coreboot
If you followed the instructions above you should be all set.  
  
If you skipped the instructions above because coreboot was already installed please ensure it is up to date. At least one [trace](https://github.com/jmontleon/pixelbook-fedora/issues/5#issuecomment-985623474) in dmesg was resolved by a firmware update.  
  
You may also encounter a [bug](https://bugzilla.kernel.org/show_bug.cgi?id=215269) that causes slow boots and hangs on shutdown if running coreboot versions prior to 4.16, which contains this [fix](https://review.coreboot.org/c/coreboot/+/61262).

## Install Fedora
1. Prepare a bootable [Fedora USB stick](https://fedoramagazine.org/make-fedora-usb-stick/)
1. Insert it into the Pixelbook and install it normally.

Once fedora is installed you may make use of the [ansible playbook](ansible/README.md) provided for configuration or continue following the instructions in this file.  

1. `sudo dnf -y copr enable jmontleon/pixelbook`
1. `sudo dnf -y update`

## Audio
By default audio will not work at all, but by copying topology and firmware files from a recovery image the speakers will work. With some additional configuration the microphone, headphone jack, and possibly other aspects work as well.

1. Download the latest eve recovery image from [chromiumdash.appspot.com/serving-builds](https://chromiumdash.appspot.com/serving-builds?deviceCategory=Chrome%20OS)
1. Unzip the file. As an example `unzip chromeos_13904.55.0_eve_recovery_stable-channel_mp-v2.bin.zip`
1. Create device maps `sudo kpartx -av chromeos_13904.55.0_eve_recovery_stable-channel_mp-v2.bin`
1. Mount the ChromeOS root filesystem `sudo mount -o ro /dev/mapper/loop0p3 /mnt`
1. Copy the files:
    1. `sudo cp /mnt/lib/firmware/9d71-GOOGLE-EVEMAX-0-tplg.bin /lib/firmware/`
    1. `sudo cp /mnt/lib/firmware/dsp_lib_dsm_core_spt_release.bin /lib/firmware/`
    1. `sudo cp /mnt/lib/firmware/intel/dsp_fw_C75061F3-F2B2-4DCC-8F9F-82ABB4131E66.bin /lib/firmware/intel`
    1. `sudo mkdir -p /opt/google/dsm/`
    1. `sudo cp /mnt/opt/google/dsm/dsmparam.bin /opt/google/dsm/dsmparam.bin`
1. Add audio packages `sudo dnf -y install pixelbook-alsa-ucm pixelbook-wireplumber pixelbook-scripts`
1. `systemctl --user --now enable pixelbook-acpi`
1. After rebooting you should have audio (Note: Some systems require 2 or occasionally 3 reboots. See the troubleshooting section for details)

## Brightness
1. `sudo dnf install pixelbook-udev && sudo dnf -y update`, if you haven't already.
1. Create `/etc/modprobe.d/i915.conf` with one line: `options i915 enable_dpcd_backlight=1`
1. `sudo dracut -f`
1. After rebooting the backlight should work.

## Keyboard

### Hotkeys / Capslock
1. `sudo dnf -y install pixelbook-udev`, if you haven't already.

### Backlight
1. `sudo dnf -y install pixelbook-scripts`
1. Add yourself to the input group: `sudo usermod -aG input $USER`
1. Set up a keyboard shortcut up to run `/usr/bin/pixelbook-keyboard-backlight` when you press `ctrl+space`.

## Orientation
1. `sudo dnf -y install pixelbook-udev pixelbook-scripts`, if you haven't already.
1. `sudo dnf -y update`, if you haven't already.
1. `edit /etc/acpi/events/powerconf and comment out the following two lines. This will prevent the power button from causing an immediate shutdown in Gnome.
```
event=button/power.*
action=/etc/acpi/actions/power.sh
```
1. `sudo systemctl --now enable acpid`
1. Gnome and KDE handle screen orientation automatically in tablet mode.
1. For others `systemctl --user --now enable pixelbook-display-orientation`
1. `systemctl --user --now enable pixelbook-acpi` will listen to tablet mode and audio jack related events and act accordingly

## Touchpad
A frequent complaint is that the touchpad does not work after reboot. If you encounter this you can install the pixelbook-touchpad-service as a workaround. This is a service that unloads and loads two kernel modules.
1. `sudo dnf -y install pixelbook-touchpad-service`
1. `sudo systemctl enable --now pixelbook-touchpad`

If you enable Tap to Click in Gnome or Xfce it will also enable Tap to Drag. To disable Tap to Drag you can do one of the following.
### Gnome:
1. `gsettings set org.gnome.desktop.peripherals.touchpad tap-and-drag false`

### Xfce
1. `sudo dnf -y install pixelbook-touchpad-tweak`

## Touchscreen
1. `sudo dnf -y install pixelbook-scripts`, if you haven't already.
1. `sudo usermod -aG input $USER`, if you haven't already
1. `sudo usermod -aG tty $USER`
1. Gnome and KDE have their own gesture logic. For Xfce and others `systemctl --user --now enable pixelbook-touchscreen-click`

## Excessive AER logging
Watching journalctl you'll note lots of logging about AER corrections. The pixelbook-aer package contains a workaround for this.
1. `sudo dnf -y install pixelbook-aer`
1. `sudo systemctl enable --now pixelbook-aer`

# Additional packages
A lot of common software is not available in Fedora, such as nvidia drivers and vlc. Fortunately a plethora of software is available from [RPM Fusion](https://rpmfusion.org/).

# Troubleshooting.
When rebooting users have observed sound continuing to fail and the mouse not working. If this happens, the problem is often remedied by rebooting via the Power+Refresh button or holding down the the power button until the system powers off and then using it to power on the system again. The touchpad section above contains a service that will mask the problem.  
  
5.16 introduced fixes to the display backlight.  
  
Audio has been a particularly problematic area at times. Make sure you're not using a known broken kernel.
- An audio issue was introduced in the 5.15.5 kernel and fixed in 5.17.0. At some point 5.15 LTS kernels were also fixed.
- In general 5.17.0 and above should work well although HDMI output has been broken since 5.17.0
- 6.0-6.0.9 were broken
- 6.1-6.1.12 were broken
- A proposed [patch](https://lore.kernel.org/regressions/060ebffd-6ecd-f2f7-6fdf-5e7b8c544d0a@linux.intel.com/T/#mfffab5d0c6cba4395d40ea7e853a925cad4c8d3d) for HDMI output is available but not yet in the kernel.
- There was one [issue](https://github.com/jmontleon/pixelbook-fedora/issues/56) report for the error `rt5514 i2c-10EC5514:00: Device with ID register e0220042 is not rt5514` appearing in dmesg and audio failing to work. The cause is unknown, but restoring ChromeOS and Reflashing the MrChromebox firmware appeared to resolve the issue.
  
Issues are welcome if you think you found something Pixelbook specific. Full logs, detailed explanations of steps taken, configuration performed, etc. are important. It is impossible to provide help with comments that simply state things aren't working as expected.

# Other distributions
For the most part nothing in this repo is distribution specific other than the availability of packages to simplify the install process. The primary adjustments you will need to be concerned about are listed below.

1. Reference [this PR](https://gitlab.com/cki-project/kernel-ark/-/merge_requests/1616/diffs) to see the kernel options that must be enabled for hardware support.
1. To match placement of configuration and scripts that are provided by packages look at the corresponding spec file. All sources are located in the [configs](https://github.com/jmontleon/pixelbook-fedora/tree/main/configs) and [scripts](https://github.com/jmontleon/pixelbook-fedora/tree/main/scripts) directories.
1. When a package is referenced, using the alsa ucm package as an example, note the [sources](https://github.com/jmontleon/pixelbook-fedora/blob/main/specs/pixelbook-alsa-ucm.spec#L6-L7) in the spec file and where they are [installed](https://github.com/jmontleon/pixelbook-fedora/blob/main/specs/pixelbook-alsa-ucm.spec#L21-L22) and manually do the same. Alsa is a special case in that 1.2.6 and above put these files in a conf.d directory. For older versions you'll probably need to move them one directory up.

If you would like to provide these packages in an AUR, PPA, or similar repo for other distributions for yourself and others please let me know and I will add them to the instructions.
