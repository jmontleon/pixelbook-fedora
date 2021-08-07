# Kernel
Kernel SRPMS are too large to upload to githubm but they are available from Copr. With the Copr repo enabled you can download the latest kernel SRPM with `sudo dnf download --source kernel`


There are only a few changes involved for making these:
1. Added a populated kernel-local with the chromeos / cros_ec modules enabled
1. Backed out a [commit](https://gitlab.freedesktop.org/drm/intel/-/issues/3680) that broke the backlight.
1. Updated filter-modules.sh.fedora in order to satisfy the depmod tests.
1. The kernel.spec changes to facilitate the patch and differentiating the kernel from the official kernel.

All changed files should be included here.
