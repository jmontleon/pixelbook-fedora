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
  - `sudo cp /mnt//opt/google/dsm/dsmparam.bin /opt/google/dsm/dsmparam.bin`
- Replace pipewire with pulseaudio, otherwise the mic produces only noise `sudo dnf swap --allowerasing pipewire-pulseaudio pulseaudio`
- As root:
```
cat << EOF > /usr/share/alsa/ucm2/kbl-r5514-5663-/kbl-r5514-5663-.conf
Syntax 4

SectionUseCase."HiFi" {
	File "HiFi.conf"
	Comment "Default"
}
EOF
```

```
cat << EOF > /usr/share/alsa/ucm2/kbl-r5514-5663-/HiFi.conf
SectionVerb {
        EnableSequence [
                cdev "hw:kblr55145663max"

                cset "name='codec1_out mo hs_pb_in mi Switch' on"
                cset "name='Left DAI Sel Mux' Left"
                cset "name='Right DAI Sel Mux' Right"
                cset "name='Left Speaker Volume' 3"
                cset "name='Right Speaker Volume' 3"
                cset "name='Left Digital Volume' 60"
                cset "name='Right Digital Volume' 60"
                cset "name='Left Spk Switch' on"
                cset "name='Right Spk Switch' on"
                cset "name='Left Boost Output Voltage' 0"
                cset "name='Right Boost Output Voltage' 0"
                cset "name='Left Current Limit' 7"
                cset "name='Right Current Limit' 7"
                cset "name='Headphone Playback Volume' 16"
                cset "name='Headset Mic Switch' off"
                cset "name='DMIC Switch' on"
                cset "name='STO1 ADC MIXL ADC1 Switch' on"
                cset "name='Pin5-Port0 Mux' 2"
                cset "name='Pin5-Port1 Mux' 2"
                cset "name='Pin5-Port2 Mux' 2"
                cset "name='Pin6-Port0 Mux' 1"
                cset "name='Pin6-Port1 Mux' 1"
                cset "name='Pin6-Port2 Mux' 1"
                cset "name='Pin7-Port0 Mux' 3"
                cset "name='Pin7-Port1 Mux' 3"
                cset "name='Pin7-Port2 Mux' 3"
                cset "name='ADC Capture Volume' 35"
                cset "name='ADC1 Capture Volume' 55"
                cset "name='ADC2 Capture Volume' 55"
                cset "name='DAC L Mux' STO DAC MIXL"
                cset "name='DAC R Mux' STO DAC MIXR"
                cset "name='STO1 DAC MIXL DAC L Switch' on"
                cset "name='STO1 DAC MIXR DAC R Switch' on"
                cset-tlv "name='spk_pb_in dsm 0 dsm_params params' /opt/google/dsm/dsmparam.bin"
        ]
}

SectionDevice."Speaker" {
	Comment "Speaker"

	Value {
		PlaybackPCM "hw:kblr55145663max,0"
		DspName "speaker_eq"
	}
}

SectionDevice."Headphones" {
	Comment "Headphones"

        Value {
                PlaybackPCM "hw:kblr55145663max,2"
                MixerName "DAC"
                JackDev "kbl-r5514-5663-max Headset Jack"

	}

	EnableSequence [
		cset "name='Headphone Jack Switch' on"
	]

	DisableSequence [
		cset "name='Headphone Jack Switch' off"
	]
}

SectionDevice."Internal Mic" {
	Comment "Internal Microphone"

	Value {
		CapturePCM "hw:kblr55145663max,4"
		CaptureChannelMap "2 3 0 1 -1 -1 -1 -1 -1 -1 -1"
		MixerName "ADC2"
		DefaultNodeGain "2700"
		CaptureChannels "4"
	}

	EnableSequence [
		cset "name='Sto1 ADC MIXL DMIC Switch' on"
		cset "name='Sto1 ADC MIXR DMIC Switch' on"
		cset "name='Sto2 ADC MIXL DMIC Switch' on"
		cset "name='Sto2 ADC MIXR DMIC Switch' on"
	]

	DisableSequence [
		cset "name='Sto1 ADC MIXL DMIC Switch' off"
		cset "name='Sto1 ADC MIXR DMIC Switch' off"
		cset "name='Sto2 ADC MIXL DMIC Switch' off"
		cset "name='Sto2 ADC MIXR DMIC Switch' off"
	]
}

SectionDevice."Mic" {
	Comment "Headset Microphone"

	Value {
		CapturePCM "hw:kblr55145663max,1"
		JackDev "kbl-r5514-5663-max Headset Jack"
	}

	EnableSequence [
		cset "name='Headset Mic Switch' on"
	]

	DisableSequence [
		cset "name='Headset Mic Switch' off"
	]
}

SectionDevice."HDMI1" {
	Comment "HDMI 1"

        Value {
                PlaybackPCM "hw:kblr55145663max,6"
                JackDev "kbl-r5514-5663-max HDMI/DP,pcm=6 Jack"
        }
}

SectionDevice."HDMI2" {
	Comment "HDMI 2"

        Value {
                PlaybackPCM "hw:kblr55145663max,7"
                JackDev "kbl-r5514-5663-max HDMI/DP,pcm=7 Jack"
        }
}
EOF
```

- Reboot. Hopefully audio from your speakers should work. Start with a low volume setting. It is very loud.

## Brightness
The brightness only has two states, full or off. The backlight can be set with xrandr. To get something that felt mostly OK I used this script:

- `sudo usermod -aG video $USER`
- Add udev rules to give the video group access to modify brightness. This file will also do the same for the keyboard leds using the input group. The rest of the setup for that will be covered in the keyboard section below.

As root:
```
cat << EOF > /etc/udev/rules.d/backlights.rules
ACTION=="add", SUBSYSTEM=="backlight", KERNEL=="intel_backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness"
ACTION=="add", SUBSYSTEM=="backlight", KERNEL=="intel_backlight", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"

ACTION=="add", SUBSYSTEM=="leds", RUN+="/bin/chgrp -R input /sys%p", RUN+="/bin/chmod -R g+w /sys%p"
ACTION=="change", SUBSYSTEM=="leds", ENV{TRIGGER}!="none", RUN+="/bin/chgrp -R input /sys%p", RUN+="/bin/chmod -R g+w /sys%p"
EOF
```

Create this script
```
mkdir -p ~/bin
cat << EOF > ~/bin/backlight.sh
#!/bin/bash

max=10
step=1
file=/tmp/brightness

case "$1" in
    -i|--increase) ((val = +step));;
    -d|--decrease) ((val = -step));;
esac

if !((val)); then
    echo "Increase or decrease screen brightness"
    echo "Usage: ${0##*/} --increase | --decrease"
    exit
fi

if [ ! -f /tmp/brightness ]; then
  echo 10 > /tmp/brightness
fi

read -r cur < "$file"
((val = cur + val))

if ((val <   0)); then ((val =   0)); fi
if ((val > max)); then ((val = max)); fi

printf '%d' "$val" > "$file"

if [ "$val" -eq "0" ]; then
  echo "0" > /sys/class/backlight/intel_backlight/brightness
else
  echo "1500" > /sys/class/backlight/intel_backlight/brightness
fi

xrandr --output eDP-1 --brightness $(echo - | awk "{ print $val / 10 }")
EOF
chmod +x ~/bin/backlight.sh
```

I then created keyboard shortcuts for the brightnessup and brightnessdown keys to instead run `backlight.sh --increase` and `backlight.sh --decrease` using the brightnessup and brightnessdown keys. Complete the keyboard section and reboot for this to function.

## Keyboard

### Hotkeys
- As root:
```
cat << EOF > /lib/udev/hwdb.d/61-eve-keyboard.hwdb
# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Distributed under the terms of the GNU General Public License v2
#
# Special keyboard mapping for Eve project. The keyboard has extra
# "Assistant" and "Hamburger" keys.
#
evdev:atkbd:dmi:bvn*:bvr*:bd*:svnGoogle:pnEve:pvr*
# KEYBOARD_KEY_5d=controlpanel
 KEYBOARD_KEY_d8=rightmeta
 KEYBOARD_KEY_db=leftmeta
 KEYBOARD_KEY_3b=back
 KEYBOARD_KEY_3c=f5
 KEYBOARD_KEY_3d=f11
 KEYBOARD_KEY_3e=print
 KEYBOARD_KEY_3f=brightnessdown
 KEYBOARD_KEY_40=brightnessup
 KEYBOARD_KEY_41=playpause
 KEYBOARD_KEY_42=mute
 KEYBOARD_KEY_43=volumedown
 KEYBOARD_KEY_44=volumeup
EOF
```
- `systemd-hwdb update`

### Capslock
To use the Search key as a Capslock:
- `sudo dnf -y install xdotool`
- Configure a keyboard shortcut for SuperL to run `xdotool key Caps_Lock`

### Backlight
For the keyboard backlight I created another script and set a shortcut up to run it when I press `ctrl+space`.
- Ensure you set up the udev rules in the Backlight/Brightness section for the display.
- Create the script
```
mkdir -p ~/bin
cat << EOF > ~/bin/keyboard-backlight.sh
#!/bin/bash

file=/sys/class/leds/chromeos\:\:kbd_backlight/brightness

read -r cur < "$file"

if [ "$cur" -eq "0" ]; then
  printf '%d' "50" > "$file"
elif [ "$cur" -eq "100" ]; then
  printf '%d' "0" > "$file"
else
  printf '%d' "100" > "$file"
fi
EOF
chmod +x ~/bin/keyboard-backlight.sh
```

## Touchpad
I like Tapping to click and no tapping to drag. While this can be enabled in the Xfce touchpad settings I was unable to disable tapping to drag. To disable it I created an xorg.conf file as root and rebooted.

```
cat << EOF > /etc/X11/xorg.conf.d/99-libinput-custom-config.conf
Section "InputClass"
        Identifier "TouchPad"
        MatchIsTouchpad "on"
        MatchDevicePath "/dev/input/event*"
        Option "Tapping" "on"
        Option "TappingDrag" "off"
        Option "TappingDragLock" "off"
        Driver "libinput"
EndSection
EOF
```

## Touchscreen
- `sudo dnf -y install xinput`
- `sudo usermod -aG input $username`
- Download and install the RPMS for python-evdev and python-pynput in this repo or `pip3 install --user pynput`
- Create the python script:
```
mkdir -p ~/bin
cat << EOF > ~/bin/clickfix.py
#!/bin/python3

from evdev import InputDevice
import time
from pynput.mouse import Button, Controller
from threading import Timer
import subprocess

dev = InputDevice('/dev/input/event4')
m = Controller()
lasttime = time.time()
rlasttime = time.time()
originaltime = lasttime
oldclickx = 0
oldclicky = 0


for event in dev.read_loop():

    if event.type == 3 and event.code == 47 and event.value == 1:
        rclicktime = time.time()
        if (rclicktime - rlasttime) < .5:
            rlasttime = rclicktime
        else:
            print("Two Finger tap.")
            subprocess.check_call(['xinput', '--disable', 'WCOM50C1:00 2D1F:5143'])
            m.click(Button.right, 1)
            subprocess.check_call(['xinput', '--enable', 'WCOM50C1:00 2D1F:5143'])
            rlasttime = rclicktime

    elif event.type == 1 and event.code == 330 and event.value == 1:
        clicktime = time.time()
        clickx, clicky = m.position
        if (clicktime - lasttime) < .5 and (abs(clickx - oldclickx) < 20) and (abs(clicky - oldclicky) < 20):
            print("Double click.")
            subprocess.check_call(['xinput', '--disable', 'WCOM50C1:00 2D1F:5143'])
            m.click(Button.left, 2)
            subprocess.check_call(['xinput', '--enable', 'WCOM50C1:00 2D1F:5143'])
            lasttime = originaltime
        else:
            lasttime = clicktime
        oldclickx = clickx
        oldclicky = clicky
EOF
chmod +x ~/bin/clickfix.py
```

- Configure the script to autostart at login.
- Reboot and you should be able to click, double click, and right click (two finger tap) using the touchscreen.
