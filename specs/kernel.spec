# All Global changes to build and install go here.
# Per the below section about __spec_install_pre, any rpm
# environment changes that affect %%install need to go
# here before the %%install macro is pre-built.

# Disable LTO in userspace packages.
%global _lto_cflags %{nil}

# Option to enable compiling with clang instead of gcc.
%bcond_with toolchain_clang

%if %{with toolchain_clang}
%global toolchain clang
%endif

# Compile the kernel with LTO (only supported when building with clang).
%bcond_with clang_lto

%if %{with clang_lto} && %{without toolchain_clang}
{error:clang_lto requires --with toolchain_clang}
%endif

# Cross compile on copr for arm
# See https://bugzilla.redhat.com/1879599
%if 0%{?_with_cross_arm:1}
%global _target_cpu armv7hl
%global _arch arm
%global _build_arch arm
%global _with_cross    1
%endif

# The kernel's %%install section is special
# Normally the %%install section starts by cleaning up the BUILD_ROOT
# like so:
#
# %%__spec_install_pre %%{___build_pre}\
#     [ "$RPM_BUILD_ROOT" != "/" ] && rm -rf "${RPM_BUILD_ROOT}"\
#     mkdir -p `dirname "$RPM_BUILD_ROOT"`\
#     mkdir "$RPM_BUILD_ROOT"\
# %%{nil}
#
# But because of kernel variants, the %%build section, specifically
# BuildKernel(), moves each variant to its final destination as the
# variant is built.  This violates the expectation of the %%install
# section.  As a result we snapshot the current env variables and
# purposely leave out the removal section.  All global wide changes
# should be added above this line otherwise the %%install section
# will not see them.
%global __spec_install_pre %{___build_pre}

# At the time of this writing (2019-03), RHEL8 packages use w2.xzdio
# compression for rpms (xz, level 2).
# Kernel has several large (hundreds of mbytes) rpms, they take ~5 mins
# to compress by single-threaded xz. Switch to threaded compression,
# and from level 2 to 3 to keep compressed sizes close to "w2" results.
#
# NB: if default compression in /usr/lib/rpm/redhat/macros ever changes,
# this one might need tweaking (e.g. if default changes to w3.xzdio,
# change below to w4T.xzdio):
#
# This is disabled on i686 as it triggers oom errors

%ifnarch i686
%define _binary_payload w3T.xzdio
%endif

Summary: The Linux kernel

# Set released_kernel to 1 when the upstream source tarball contains a
#  kernel release. (This includes prepatch or "rc" releases.)
# Set released_kernel to 0 when the upstream source tarball contains an
#  unreleased kernel development snapshot.
%global released_kernel 1

# Set debugbuildsenabled to 1 to build separate base and debug kernels
#  (on supported architectures). The kernel-debug-* subpackages will
#  contain the debug kernel.
# Set debugbuildsenabled to 0 to not build a separate debug kernel, but
#  to build the base kernel using the debug configuration. (Specifying
#  the --with-release option overrides this setting.)
%define debugbuildsenabled 1

%global distro_build 300

%if 0%{?fedora}
%define secure_boot_arch x86_64
%else
%define secure_boot_arch x86_64 aarch64 s390x ppc64le
%endif

# Signing for secure boot authentication
%ifarch %{secure_boot_arch}
%global signkernel 1
%else
%global signkernel 0
%endif

# Sign modules on all arches
%global signmodules 1

# Compress modules only for architectures that build modules
%ifarch noarch
%global zipmodules 0
%else
%global zipmodules 1
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
# for parallel xz processes, replace with 1 to go back to single process
%global zcpu `nproc --all`
%endif

# define buildid .local


%if 0%{?fedora}
%define primary_target fedora
%else
%define primary_target rhel
%endif

# The kernel tarball/base version
%define kversion 5.14

%define rpmversion 5.14.9
%define patchversion 5.14
%define pkgrelease 300

# This is needed to do merge window version magic
%define patchlevel 14

# allow pkg_release to have configurable %%{?dist} tag
%define specrelease 301.pixelbook%{?buildid}%{?dist}

%define pkg_release %{specrelease}

# libexec dir is not used by the linker, so the shared object there
# should not be exported to RPM provides
%global __provides_exclude_from ^%{_libexecdir}/kselftests

# The following build options are enabled by default, but may become disabled
# by later architecture-specific checks. These can also be disabled by using
# --without <opt> in the rpmbuild command, or by forcing these values to 0.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel PAE (only valid for ARM (lpae))
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-zfcpdump (s390 specific kernel for zfcpdump)
%define with_zfcpdump  %{?_without_zfcpdump:  0} %{?!_without_zfcpdump:  1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
%define with_cross_headers   %{?_without_cross_headers:   0} %{?!_without_cross_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# bpf tool
%define with_bpftool   %{?_without_bpftool:   0} %{?!_without_bpftool:   1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-abi-stablelists
%define with_kernel_abi_stablelists %{?_without_kernel_abi_stablelists: 0} %{?!_without_kernel_abi_stablelists: 1}
# internal samples and selftests
%define with_selftests %{?_without_selftests: 0} %{?!_without_selftests: 1}
#
# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the pae kernel (--with paeonly):
%define with_paeonly   %{?_with_paeonly:      1} %{?!_with_paeonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}
# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}
# Temporarily disable kabi checks until RC.
%define with_kabichk 0
# Control whether we perform a compat. check against DUP ABI.
%define with_kabidupchk %{?_with_kabidupchk:  1} %{?!_with_kabidupchk:   0}
#
# Control whether to run an extensive DWARF based kABI check.
# Note that this option needs to have baseline setup in SOURCE300.
%define with_kabidwchk %{?_without_kabidwchk: 0} %{?!_without_kabidwchk: 1}
%define with_kabidw_base %{?_with_kabidw_base: 1} %{?!_with_kabidw_base: 0}
#
# Control whether to install the vdso directories.
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
#
# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}
#
# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}
#
# build a release kernel on rawhide
%define with_release   %{?_with_release:      1} %{?!_with_release:      0}

# verbose build, i.e. no silent rules and V=1
%define with_verbose %{?_with_verbose:        1} %{?!_with_verbose:      0}

#
# check for mismatched config options
%define with_configchecks %{?_without_configchecks:        0} %{?!_without_configchecks:        1}

#
# gcov support
%define with_gcov %{?_with_gcov:1}%{?!_with_gcov:0}

#
# ipa_clone support
%define with_ipaclones %{?_without_ipaclones: 0} %{?!_without_ipaclones: 1}

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

%if 0%{?fedora}
# Kernel headers are being split out into a separate package
%define with_headers 0
%define with_cross_headers 0
# no ipa_clone for now
%define with_ipaclones 0
# no stablelist
%define with_kernel_abi_stablelists 0
# Fedora builds these separately
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
# selftests turns on bpftool
%define with_selftests 0
%endif

%if %{with_verbose}
%define make_opts V=1
%else
%define make_opts -s
%endif

%if %{with toolchain_clang}
%global clang_make_opts HOSTCC=clang CC=clang
%if %{with clang_lto}
%global clang_make_opts %{clang_make_opts} LD=ld.lld HOSTLD=ld.lld AR=llvm-ar NM=llvm-nm HOSTAR=llvm-ar HOSTNM=llvm-nm LLVM_IAS=1
%endif
%global make_opts %{make_opts} %{clang_make_opts}
# clang does not support the -fdump-ipa-clones option
%global with_ipaclones 0
%endif

# turn off debug kernel and kabichk for gcov builds
%if %{with_gcov}
%define with_debug 0
%define with_kabichk 0
%define with_kabidupchk 0
%define with_kabidwchk 0
%define with_kabidw_base 0
%define with_kernel_abi_stablelists 0
%endif

# turn off kABI DWARF-based check if we're generating the base dataset
%if %{with_kabidw_base}
%define with_kabidwchk 0
%endif

# kpatch_kcflags are extra compiler flags applied to base kernel
# -fdump-ipa-clones is enabled only for base kernels on selected arches
%if %{with_ipaclones}
%ifarch x86_64 ppc64le
%define kpatch_kcflags -fdump-ipa-clones
%else
%define with_ipaclones 0
%endif
%endif

%define make_target bzImage
%define image_install_path boot

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define KVERREL_RE %(echo %KVERREL | sed 's/+/[+]/g')
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if 0%{!?nopatches:1}
%define nopatches 0
%endif

%if %{with_vanilla}
%define nopatches 1
%endif

%if %{with_release}
%define debugbuildsenabled 1
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug
# Needed because we override almost everything involving build-ids
# and debuginfo generation. Currently we rely on the old alldebug setting.
%global _build_id_links alldebug

# kernel PAE is only built on ARMv7
%ifnarch armv7hl
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_pae 0
%define with_debug 0
%define with_vdso_install 0
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%define with_kernel_abi_stablelists 0
%define with_selftests 0
%define with_cross 0
%define with_cross_headers 0
%define with_ipaclones 0
%endif

# if requested, only build pae kernel
%if %{with_paeonly}
%define with_up 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_up 0
%define with_vdso_install 0
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%define with_kernel_abi_stablelists 0
%define with_selftests 0
%define with_cross 0
%define with_cross_headers 0
%define with_ipaclones 0
%endif

# turn off kABI DUP check and DWARF-based check if kABI check is disabled
%if !%{with_kabichk}
%define with_kabidupchk 0
%define with_kabidwchk 0
%endif

%if %{with_vdso_install}
%define use_vdso 1
%endif

# selftests require bpftool to be built
%if %{with_selftests}
%define with_bpftool 1
%endif

%ifnarch noarch
%define with_kernel_abi_stablelists 0
%endif

# Overrides for generic default options

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define doc_build_fail true
%endif

%if 0%{?fedora}
# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_cross_headers 0
%define with_tools 0
%define with_perf 0
%define with_bpftool 0
%define with_selftests 0
%define with_debug 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# sparse blows up on ppc
%ifnarch ppc64le
%define with_sparse 0
%endif

# zfcpdump mechanism is s390 only
%ifnarch s390x
%define with_zfcpdump 0
%endif

%if 0%{?fedora}
# This is not for Fedora
%define with_zfcpdump 0
%endif

# Per-arch tweaks

%ifarch i686
%define asmarch x86
%define hdrarch i386
%define all_arch_configs kernel-%{version}-i?86*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define use_vdso 0
%define all_arch_configs kernel-%{version}-ppc64le*.config
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define kernel_image arch/s390/boot/bzImage
%define vmlinux_decompressor arch/s390/boot/compressed/vmlinux
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define skip_nonpae_vdso 1
%define asmarch arm
%define hdrarch arm
%define make_target bzImage
%define kernel_image arch/arm/boot/zImage
# http://lists.infradead.org/pipermail/linux-arm-kernel/2012-March/091404.html
%define kernel_mflags KALLSYMS_EXTRA_PASS=1
# we only build headers/perf/tools on the base arm arches
# just like we used to only build them on i386 for x86
%ifnarch armv7hl
%define with_headers 0
%define with_cross_headers 0
%endif
# These currently don't compile on armv7
%define with_selftests 0
%endif

%ifarch aarch64
%define all_arch_configs kernel-%{version}-aarch64*.config
%define asmarch arm64
%define hdrarch arm64
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}
%define with_configchecks 0
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%if 0%{?fedora}
%define nobuildarches i386
%else
%define nobuildarches i386 i686 %{arm}
%endif

%ifarch %nobuildarches
# disable BuildKernel commands
%define with_up 0
%define with_debug 0
%define with_pae 0
%define with_zfcpdump 0

%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%define with_selftests 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%if 0%{?fedora}
%define cpupowerarchs %{ix86} x86_64 ppc64le %{arm} aarch64
%else
%define cpupowerarchs i686 x86_64 ppc64le aarch64
%endif

%if 0%{?use_vdso}

%if 0%{?skip_nonpae_vdso}
%define _use_vdso 0
%else
%define _use_vdso 1
%endif

%else
%define _use_vdso 0
%endif

# If build of debug packages is disabled, we need to know if we want to create
# meta debug packages or not, after we define with_debug for all specific cases
# above. So this must be at the end here, after all cases of with_debug or not.
%define with_debug_meta 0
%if !%{debugbuildsenabled}
%if %{with_debug}
%define with_debug_meta 1
%endif
%define with_debug 0
%endif


#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  coreutils, systemd >= 203-2, /usr/bin/kernel-install
%define initrd_prereq  dracut >= 027


Name: kernel
License: GPLv2 and Redistributable, no modification permitted
URL: https://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
%if 0%{?fedora}
ExclusiveArch: noarch x86_64 s390x %{arm} aarch64 ppc64le
%else
ExclusiveArch: noarch i386 i686 x86_64 s390x %{arm} aarch64 ppc64le
%endif
ExclusiveOS: Linux
%ifnarch %{nobuildarches}
Requires: kernel-core-uname-r = %{KVERREL}
Requires: kernel-modules-uname-r = %{KVERREL}
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod, patch, bash, coreutils, tar, git-core, which
BuildRequires: bzip2, xz, findutils, gzip, m4, perl-interpreter, perl-Carp, perl-devel, perl-generators, make, diffutils, gawk
BuildRequires: gcc, binutils, redhat-rpm-config, hmaccalc, bison, flex, gcc-c++
BuildRequires: net-tools, hostname, bc, elfutils-devel
BuildRequires: dwarves
BuildRequires: python3-devel
BuildRequires: gcc-plugin-devel
%ifnarch %{nobuildarches} noarch
BuildRequires: bpftool
%endif
%if %{with_headers}
BuildRequires: rsync
%endif
%if %{with_doc}
BuildRequires: xmlto, asciidoc, python3-sphinx, python3-sphinx_rtd_theme
%endif
%if %{with_sparse}
BuildRequires: sparse
%endif
%if %{with_perf}
BuildRequires: zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison flex xz-devel
BuildRequires: audit-libs-devel
BuildRequires: java-devel
BuildRequires: libbpf-devel
BuildRequires: libbabeltrace-devel
BuildRequires: libtraceevent-devel
%ifnarch %{arm} s390x
BuildRequires: numactl-devel
%endif
%ifarch aarch64
BuildRequires: opencsd-devel >= 1.0.0
%endif
%endif
%if %{with_tools}
BuildRequires: gettext ncurses-devel
BuildRequires: libcap-devel libcap-ng-devel
%ifnarch s390x
BuildRequires: pciutils-devel
%endif
%endif
%if %{with_bpftool}
BuildRequires: python3-docutils
BuildRequires: zlib-devel binutils-devel
%endif
%if %{with_selftests}
BuildRequires: clang llvm
%ifnarch %{arm}
BuildRequires: numactl-devel
%endif
BuildRequires: libcap-devel libcap-ng-devel rsync libmnl-devel
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
BuildConflicts: rpm < 4.13.0.1-19
BuildConflicts: dwarves < 1.13
# Most of these should be enabled after more investigation
%undefine _include_minidebuginfo
%undefine _find_debuginfo_dwz_opts
%undefine _unique_build_ids
%undefine _unique_debug_names
%undefine _unique_debug_srcs
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%global _find_debuginfo_opts -r
%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1
%endif
%if %{with_kabidwchk} || %{with_kabidw_base}
BuildRequires: kabi-dw
%endif

%if %{signkernel}%{signmodules}
BuildRequires: openssl openssl-devel
%if %{signkernel}
%ifarch x86_64 aarch64
BuildRequires: nss-tools
BuildRequires: pesign >= 0.10-4
%endif
%endif
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%define cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%define __strip %{_build_arch}-linux-gnu-strip
%endif

# These below are required to build man pages
%if %{with_perf}
BuildRequires: xmlto
%endif
%if %{with_perf} || %{with_tools}
BuildRequires: asciidoc
%endif

%if %{with toolchain_clang}
BuildRequires: clang
%endif

%if %{with clang_lto}
BuildRequires: llvm
BuildRequires: lld
%endif

# Because this is the kernel, it's hard to get a single upstream URL
# to represent the base without needing to do a bunch of patching. This
# tarball is generated from a src-git tree. If you want to see the
# exact git commit you can run
#
# xzcat -qq ${TARBALL} | git get-tar-commit-id
Source0: linux-5.14.9.tar.xz

Source1: Makefile.rhelver


# Name of the packaged file containing signing key
%ifarch ppc64le
%define signing_key_filename kernel-signing-ppc.cer
%endif
%ifarch s390x
%define signing_key_filename kernel-signing-s390.cer
%endif

Source8: x509.genkey.rhel
Source9: x509.genkey.fedora

%if %{?released_kernel}

Source10: redhatsecurebootca5.cer
Source11: redhatsecurebootca1.cer
Source12: redhatsecureboot501.cer
Source13: redhatsecureboot301.cer
Source14: secureboot_s390.cer
Source15: secureboot_ppc.cer

%define secureboot_ca_1 %{SOURCE10}
%define secureboot_ca_0 %{SOURCE11}
%ifarch x86_64 aarch64
%define secureboot_key_1 %{SOURCE12}
%define pesign_name_1 redhatsecureboot501
%define secureboot_key_0 %{SOURCE13}
%define pesign_name_0 redhatsecureboot301
%endif
%ifarch s390x
%define secureboot_key_0 %{SOURCE14}
%define pesign_name_0 redhatsecureboot302
%endif
%ifarch ppc64le
%define secureboot_key_0 %{SOURCE15}
%define pesign_name_0 redhatsecureboot303
%endif

# released_kernel
%else

Source10: redhatsecurebootca4.cer
Source11: redhatsecurebootca2.cer
Source12: redhatsecureboot401.cer
Source13: redhatsecureboot003.cer

%define secureboot_ca_1 %{SOURCE10}
%define secureboot_ca_0 %{SOURCE11}
%define secureboot_key_1 %{SOURCE12}
%define pesign_name_1 redhatsecureboot401
%define secureboot_key_0 %{SOURCE13}
%define pesign_name_0 redhatsecureboot003

# released_kernel
%endif

Source22: mod-extra.list.rhel
Source16: mod-extra.list.fedora
Source17: mod-denylist.sh
Source18: mod-sign.sh
Source79: parallel_xz.sh

Source80: filter-x86_64.sh.fedora
Source81: filter-armv7hl.sh.fedora
Source82: filter-i686.sh.fedora
Source83: filter-aarch64.sh.fedora
Source86: filter-ppc64le.sh.fedora
Source87: filter-s390x.sh.fedora
Source89: filter-modules.sh.fedora

Source90: filter-x86_64.sh.rhel
Source91: filter-armv7hl.sh.rhel
Source92: filter-i686.sh.rhel
Source93: filter-aarch64.sh.rhel
Source96: filter-ppc64le.sh.rhel
Source97: filter-s390x.sh.rhel
Source99: filter-modules.sh.rhel
%define modsign_cmd %{SOURCE18}

Source20: kernel-aarch64-rhel.config
Source21: kernel-aarch64-debug-rhel.config
Source30: kernel-ppc64le-rhel.config
Source31: kernel-ppc64le-debug-rhel.config
Source32: kernel-s390x-rhel.config
Source33: kernel-s390x-debug-rhel.config
Source34: kernel-s390x-zfcpdump-rhel.config
Source35: kernel-x86_64-rhel.config
Source36: kernel-x86_64-debug-rhel.config

Source37: kernel-aarch64-fedora.config
Source38: kernel-aarch64-debug-fedora.config
Source39: kernel-armv7hl-fedora.config
Source40: kernel-armv7hl-debug-fedora.config
Source41: kernel-armv7hl-lpae-fedora.config
Source42: kernel-armv7hl-lpae-debug-fedora.config
Source43: kernel-i686-fedora.config
Source44: kernel-i686-debug-fedora.config
Source45: kernel-ppc64le-fedora.config
Source46: kernel-ppc64le-debug-fedora.config
Source47: kernel-s390x-fedora.config
Source48: kernel-s390x-debug-fedora.config
Source49: kernel-x86_64-fedora.config
Source50: kernel-x86_64-debug-fedora.config



Source51: generate_all_configs.sh

Source52: process_configs.sh
Source56: update_scripts.sh
Source57: generate_crashkernel_default.sh

Source54: mod-internal.list

Source100: rheldup3.x509
Source101: rhelkpatch1.x509

Source200: check-kabi

Source201: Module.kabi_aarch64
Source202: Module.kabi_ppc64le
Source203: Module.kabi_s390x
Source204: Module.kabi_x86_64

Source210: Module.kabi_dup_aarch64
Source211: Module.kabi_dup_ppc64le
Source212: Module.kabi_dup_s390x
Source213: Module.kabi_dup_x86_64

Source300: kernel-abi-stablelists-%{rpmversion}-%{distro_build}.tar.bz2
Source301: kernel-kabi-dw-%{rpmversion}-%{distro_build}.tar.bz2

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config
Source2002: kvm_stat.logrotate

# Some people enjoy building customized kernels from the dist-git in Fedora and
# use this to override configuration options. One day they may all use the
# source tree, but in the mean time we carry this to support the legacy workflow
Source3000: merge.pl
Source3001: kernel-local
Source3003: Patchlist.changelog

Source4000: README.rst
Source4001: rpminspect.yaml
Source4002: gating.yaml

## Patches needed for building this package
Patch0: reversed-drm-i915-dp-Don-t-use-DPCD-backlights-that-need-PWM-enable-disable.patch
%if !%{nopatches}

Patch1: patch-%{patchversion}-redhat.patch
%endif

# empty final patch to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch

# END OF PATCH DEFINITIONS

%description
The kernel meta package

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:+%{1}}\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20150904-56.git6ebf5d57\
Requires(preun): systemd >= 200\
Conflicts: xfsprogs < 4.3.0-1\
Conflicts: xorg-x11-drv-vmmouse < 13.0.99\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}


%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package headers
Summary: Header files for the Linux kernel for use by glibc
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package cross-headers
Summary: Header files for the Linux kernel for use by cross-glibc
%description cross-headers
Kernel-cross-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
cross-glibc package.


%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Provides: installonlypkg(kernel)
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Requires: bzip2
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|.*%%{_libdir}/libperf-jvmti.so(\.debug)?|XXX' -o perf-debuginfo.list}

%package -n python3-perf
Summary: Python bindings for apps which will manipulate perf events
%description -n python3-perf
The python3-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%package -n python3-perf-debuginfo
Summary: Debug information for package perf python bindings
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python3-perf-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{python3_sitearch}/perf.*so(\.debug)?|XXX' -o python3-perf-debuginfo.list}

# with_perf
%endif

%if %{with_tools}
%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
License: GPLv2
%ifarch %{cpupowerarchs}
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: kernel-tools-libs = %{version}-%{release}
%endif
%define __requires_exclude ^%{_bindir}/python
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
%ifarch %{cpupowerarchs}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
%endif
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|.*%%{_bindir}/lsgpio(\.debug)?|.*%%{_bindir}/gpio-hammer(\.debug)?|.*%%{_bindir}/gpio-event-mon(\.debug)?|.*%%{_bindir}/gpio-watch(\.debug)?|.*%%{_bindir}/iio_event_monitor(\.debug)?|.*%%{_bindir}/iio_generic_buffer(\.debug)?|.*%%{_bindir}/lsiio(\.debug)?|.*%%{_bindir}/intel-speed-select(\.debug)?|.*%%{_bindir}/page_owner_sort(\.debug)?|.*%%{_bindir}/slabinfo(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

# with_tools
%endif

%if %{with_bpftool}

%package -n bpftool
Summary: Inspection and simple manipulation of eBPF programs and maps
License: GPLv2
%description -n bpftool
This package contains the bpftool, which allows inspection and simple
manipulation of eBPF programs and maps.

%package -n bpftool-debuginfo
Summary: Debug information for package bpftool
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n bpftool-debuginfo
This package provides debug information for the bpftool package.

%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_sbindir}/bpftool(\.debug)?|XXX' -o bpftool-debuginfo.list}

# with_bpftool
%endif

%if %{with_selftests}

%package selftests-internal
Summary: Kernel samples and selftests
License: GPLv2
Requires: binutils, bpftool, iproute-tc, nmap-ncat, python3
%description selftests-internal
Kernel sample programs and selftests.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_libexecdir}/(ksamples|kselftests)/.*|XXX' -o selftests-debuginfo.list}

# with_selftests
%endif

%if %{with_gcov}
%package gcov
Summary: gcov graph and source files for coverage data collection.
%description gcov
kernel-gcov includes the gcov graph and source files for gcov coverage collection.
%endif

%package -n kernel-abi-stablelists
Summary: The Red Hat Enterprise Linux kernel ABI symbol stablelists
AutoReqProv: no
%description -n kernel-abi-stablelists
The kABI package contains information pertaining to the Red Hat Enterprise
Linux kernel ABI, including lists of kernel symbols that are needed by
external Linux kernel modules, and a yum plugin to aid enforcement.

%if %{with_kabidw_base}
%package kernel-kabidw-base-internal
Summary: The baseline dataset for kABI verification using DWARF data
Group: System Environment/Kernel
AutoReqProv: no
%description kernel-kabidw-base-internal
The package contains data describing the current ABI of the Red Hat Enterprise
Linux kernel, suitable for the kabi-dw tool.
%endif

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
# Explanation of the find_debuginfo_opts: We build multiple kernels (debug
# pae etc.) so the regex filters those kernels appropriately. We also
# have to package several binaries as part of kernel-devel but getting
# unique build-ids is tricky for these userspace binaries. We don't really
# care about debugging those so we just filter those out and remove it.
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
%description %{?1:%{1}-}debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*\/usr\/src\/kernels/.*|XXX' -o ignored-debuginfo.list -p '/.*/%%{KVERREL_RE}%{?1:[+]%{1}}/.*|/.*%%{KVERREL_RE}%{?1:\+%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package [-m] <subpackage> <pretty-name>
#
%define kernel_devel_package(m) \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
Requires(pre): findutils\
Requires: findutils\
Requires: perl-interpreter\
Requires: openssl-devel\
Requires: elfutils-libelf-devel\
Requires: bison\
Requires: flex\
Requires: make\
Requires: gcc\
%if %{-m:1}%{!-m:0}\
Requires: kernel-devel-uname-r = %{KVERREL}\
%endif\
%description %{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates an empty kernel-<subpackage>-devel-matched package that
# requires both the core and devel packages locked on the same version.
#	%%kernel_devel_matched_package [-m] <subpackage> <pretty-name>
#
%define kernel_devel_matched_package(m) \
%package %{?1:%{1}-}devel-matched\
Summary: Meta package to install matching core and devel packages for a given %{?2:%{2} }kernel\
Requires: kernel%{?1:-%{1}}-devel = %{version}-%{release}\
Requires: kernel%{?1:-%{1}}-core = %{version}-%{release}\
%description %{?1:%{1}-}devel-matched\
This meta package is used to install matching core and devel packages for a given %{?2:%{2} }kernel.\
%{nil}

#
# kernel-<variant>-ipaclones-internal package
#
%define kernel_ipaclones_package() \
%package %{?1:%{1}-}ipaclones-internal\
Summary: *.ipa-clones files generated by -fdump-ipa-clones for kernel%{?1:-%{1}}\
Group: System Environment/Kernel\
AutoReqProv: no\
%description %{?1:%{1}-}ipaclones-internal\
This package provides *.ipa-clones files.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules-internal package.
#	%%kernel_modules_internal_package <subpackage> <pretty-name>
#
%define kernel_modules_internal_package() \
%package %{?1:%{1}-}modules-internal\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-internal-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-modules-internal-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-modules-internal = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-internal-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-internal\
This package provides kernel modules for the %{?2:%{2} }kernel package for Red Hat internal usage.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules-extra package.
#	%%kernel_modules_extra_package [-m] <subpackage> <pretty-name>
#
%define kernel_modules_extra_package(m) \
%package %{?1:%{1}-}modules-extra\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-modules-extra = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
%if %{-m:1}%{!-m:0}\
Requires: kernel-modules-extra-uname-r = %{KVERREL}\
%endif\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-extra\
This package provides less commonly used kernel modules for the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules package.
#	%%kernel_modules_package [-m] <subpackage> <pretty-name>
#
%define kernel_modules_package(m) \
%package %{?1:%{1}-}modules\
Summary: kernel modules to match the %{?2:%{2}-}core kernel\
Provides: kernel%{?1:-%{1}}-modules-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-modules-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-modules = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
%if %{-m:1}%{!-m:0}\
Requires: kernel-modules-uname-r = %{KVERREL}\
%endif\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules\
This package provides commonly used kernel modules for the %{?2:%{2}-}core kernel package.\
%{nil}

#
# this macro creates a kernel-<subpackage> meta package.
#	%%kernel_meta_package <subpackage>
#
%define kernel_meta_package() \
%package %{1}\
summary: kernel meta-package for the %{1} kernel\
Requires: kernel-%{1}-core-uname-r = %{KVERREL}+%{1}\
Requires: kernel-%{1}-modules-uname-r = %{KVERREL}+%{1}\
Provides: installonlypkg(kernel)\
%description %{1}\
The meta-package for the %{1} kernel\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] [-m] <subpackage>
#
%define kernel_variant_package(n:m) \
%package %{?1:%{1}-}core\
Summary: %{variant_summary}\
Provides: kernel-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
%if %{-m:1}%{!-m:0}\
Requires: kernel-core-uname-r = %{KVERREL}\
%endif\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%{expand:%%kernel_devel_matched_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%if %{-m:0}%{!-m:1}\
%{expand:%%kernel_modules_internal_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %{?1:%{1}}}\
%endif\
%{nil}

# Now, each variant package.

%if %{with_pae}
%define variant_summary The Linux kernel compiled for Cortex-A15
%kernel_variant_package lpae
%description lpae-core
This package includes a version of the Linux kernel with support for
Cortex-A15 devices with LPAE and HW virtualisation support
%endif

%if %{with_zfcpdump}
%define variant_summary The Linux kernel compiled for zfcpdump usage
%kernel_variant_package zfcpdump
%description zfcpdump-core
The kernel package contains the Linux kernel (vmlinuz) for use by the
zfcpdump infrastructure.
# with_zfcpdump
%endif

%define variant_summary The Linux kernel compiled with extra debugging enabled
%if !%{debugbuildsenabled}
%kernel_variant_package -m debug
%else
%kernel_variant_package debug
%endif
%description debug-core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

# And finally the main -core package

%define variant_summary The Linux kernel
%kernel_variant_package
%description core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.

%if %{with_ipaclones}
%kernel_ipaclones_package
%endif

%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME}.spec ; then
    if [ "${patch:0:8}" != "patch-5." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz)  gunzip  < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.xz)  unxz    < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

%setup -q -n kernel-5.14.9 -c
mv linux-5.14.9 linux-%{KVERREL}

cd linux-%{KVERREL}
cp -a %{SOURCE1} .
ApplyOptionalPatch reversed-drm-i915-dp-Don-t-use-DPCD-backlights-that-need-PWM-enable-disable.patch
%if !%{nopatches}

ApplyOptionalPatch patch-%{patchversion}-redhat.patch
%endif

ApplyOptionalPatch linux-kernel-test.patch

# END OF PATCH APPLICATIONS

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl
mv COPYING COPYING-%{version}-%{release}

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# Mangle /usr/bin/python shebangs to /usr/bin/python3
# Mangle all Python shebangs to be Python 3 explicitly
# -p preserves timestamps
# -n prevents creating ~backup files
# -i specifies the interpreter for the shebang
# This fixes errors such as
# *** ERROR: ambiguous python shebang in /usr/bin/kvm_stat: #!/usr/bin/python. Change it to python3 (or python2) explicitly.
# We patch all sources below for which we got a report/error.
pathfix.py -i "%{__python3} %{py3_shbang_opts}" -p -n \
	tools/kvm/kvm_stat/kvm_stat \
	scripts/show_delta \
	scripts/diffconfig \
	scripts/bloat-o-meter \
	scripts/jobserver-exec \
	tools \
	Documentation \
	scripts/clang-tools

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
fi
mkdir configs
cd configs

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/kernel-*.config .
cp %{SOURCE51} .
# merge.pl
cp %{SOURCE3000} .
# kernel-local
cp %{SOURCE3001} .
VERSION=%{version} ./generate_all_configs.sh %{primary_target} %{debugbuildsenabled}

# Merge in any user-provided local config option changes
%ifnarch %nobuildarches
for i in %{all_arch_configs}
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE3001} $i.tmp > $i
  rm $i.tmp
done
%endif

# enable GCOV kernel config options if gcov is on
%if %{with_gcov}
for i in *.config
do
  sed -i 's/# CONFIG_GCOV_KERNEL is not set/CONFIG_GCOV_KERNEL=y\nCONFIG_GCOV_PROFILE_ALL=y\n/' $i
done
%endif

%if %{with clang_lto}
for i in *aarch64*.config *x86_64*.config; do
  sed -i 's/# CONFIG_LTO_CLANG_THIN is not set/CONFIG_LTO_CLANG_THIN=y/' $i
  sed -i 's/CONFIG_LTO_NONE=y/# CONFIG_LTO_NONE is not set/' $i
done
%endif

# Add DUP and kpatch certificates to system trusted keys for RHEL
%if 0%{?rhel}
%if %{signkernel}%{signmodules}
openssl x509 -inform der -in %{SOURCE100} -out rheldup3.pem
openssl x509 -inform der -in %{SOURCE101} -out rhelkpatch1.pem
cat rheldup3.pem rhelkpatch1.pem > ../certs/rhel.pem
%ifarch s390x ppc64le
openssl x509 -inform der -in %{secureboot_ca_0} -out secureboot.pem
cat secureboot.pem >> ../certs/rhel.pem
%endif
for i in *.config; do
  sed -i 's@CONFIG_SYSTEM_TRUSTED_KEYS=""@CONFIG_SYSTEM_TRUSTED_KEYS="certs/rhel.pem"@' $i
done
%endif
%endif

cp %{SOURCE52} .
OPTS=""
%if %{with_configchecks}
	OPTS="$OPTS -w -n -c"
%endif
%if %{with clang_lto}
for opt in %{clang_make_opts}; do
  OPTS="$OPTS -m $opt"
done
%endif
./process_configs.sh $OPTS kernel %{rpmversion}

cp %{SOURCE56} .
RPM_SOURCE_DIR=$RPM_SOURCE_DIR ./update_scripts.sh %{primary_target}

# end of kernel config
%endif

cd ..
# # End of Configs stuff

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -delete >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -delete >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

# Note we need to disable these flags for cross builds because the flags
# from redhat-rpm-config assume that host == target so target arch
# flags cause issues with the host compiler.
%if !%{with_cross}
%define build_hostcflags  %{?build_cflags}
%define build_hostldflags %{?build_ldflags}
%endif

%define make %{__make} %{?cross_opts} %{?make_opts} HOSTCFLAGS="%{?build_hostcflags}" HOSTLDFLAGS="%{?build_hostldflags}"

InitBuildVars() {
    # Initialize the kernel .config file and create some variables that are
    # needed for the actual build process.

    Variant=$1

    # Pick the right kernel config file
    Config=kernel-%{version}-%{_target_cpu}${Variant:+-${Variant}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Variant:++${Variant}}

    KernelVer=%{version}-%{release}.%{_target_cpu}${Variant:++${Variant}}

    # make sure EXTRAVERSION says what we want it to say
    # Trim the release if this is a CI build, since KERNELVERSION is limited to 64 characters
    ShortRel=$(perl -e "print \"%{release}\" =~ s/\.pr\.[0-9A-Fa-f]{32}//r")
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -${ShortRel}.%{_target_cpu}${Variant:++${Variant}}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    # if we are post rc1 this should match anyway so this won't matter
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{patchlevel}/' Makefile

    %{make} %{?_smp_mflags} mrproper
    cp configs/$Config .config

    %if %{signkernel}%{signmodules}
    cp $RPM_SOURCE_DIR/x509.genkey certs/.
    %endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    KCFLAGS="%{?kcflags}"

    # add kpatch flags for base kernel
    if [ "$Variant" == "" ]; then
        KCFLAGS="$KCFLAGS %{?kpatch_kcflags}"
    fi
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    DoVDSO=$3
    Variant=$4
    InstallName=${5:-vmlinuz}

    DoModules=1
    if [ "$Variant" = "zfcpdump" ]; then
	    DoModules=0
    fi

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    InitBuildVars $Variant

    echo BUILDING A KERNEL FOR ${Variant} %{_target_cpu}...

    %{make} ARCH=$Arch olddefconfig >/dev/null

    # This ensures build-ids are unique to allow parallel debuginfo
    perl -p -i -e "s/^CONFIG_BUILD_SALT.*/CONFIG_BUILD_SALT=\"%{KVERREL}\"/" .config
    %{make} ARCH=$Arch KCFLAGS="$KCFLAGS" WITH_GCOV="%{?with_gcov}" %{?_smp_mflags} $MakeTarget %{?sparse_mflags} %{?kernel_mflags}
    if [ $DoModules -eq 1 ]; then
	%{make} ARCH=$Arch KCFLAGS="$KCFLAGS" WITH_GCOV="%{?with_gcov}" %{?_smp_mflags} modules %{?sparse_mflags} || exit 1
    fi

    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif

%ifarch %{arm} aarch64
    %{make} ARCH=$Arch dtbs INSTALL_DTBS_PATH=$RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    %{make} ARCH=$Arch dtbs_install INSTALL_DTBS_PATH=$RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    cp -r $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/dtb
    find arch/$Arch/boot/dts -name '*.dtb' -type f -delete
%endif

    # Start installing the results
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/config
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/System.map

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/lib/modules/$KernelVer/zImage.stub-$KernelVer || :
    fi

    %if %{signkernel}
    if [ "$KernelImage" = vmlinux ]; then
        # We can't strip and sign $KernelImage in place, because
        # we need to preserve original vmlinux for debuginfo.
        # Use a copy for signing.
        $CopyKernel $KernelImage $KernelImage.tosign
        KernelImage=$KernelImage.tosign
        CopyKernel=cp
    fi

    # Sign the image if we're using EFI
    # aarch64 kernels are gziped EFI images
    KernelExtension=${KernelImage##*.}
    if [ "$KernelExtension" == "gz" ]; then
        SignImage=${KernelImage%.*}
    else
        SignImage=$KernelImage
    fi

    %ifarch x86_64 aarch64
    %pesign -s -i $SignImage -o vmlinuz.tmp -a %{secureboot_ca_0} -c %{secureboot_key_0} -n %{pesign_name_0}
    %pesign -s -i vmlinuz.tmp -o vmlinuz.signed -a %{secureboot_ca_1} -c %{secureboot_key_1} -n %{pesign_name_1}
    rm vmlinuz.tmp
    %endif
    %ifarch s390x ppc64le
    if [ -x /usr/bin/rpm-sign ]; then
	rpm-sign --key "%{pesign_name_0}" --lkmsign $SignImage --output vmlinuz.signed
    elif [ $DoModules -eq 1 ]; then
	chmod +x scripts/sign-file
	./scripts/sign-file -p sha256 certs/signing_key.pem certs/signing_key.x509 $SignImage vmlinuz.signed
    else
	mv $SignImage vmlinuz.signed
    fi
    %endif

    if [ ! -s vmlinuz.signed ]; then
        echo "pesigning failed"
        exit 1
    fi
    mv vmlinuz.signed $SignImage
    if [ "$KernelExtension" == "gz" ]; then
        gzip -f9 $SignImage
    fi
    # signkernel
    %endif

    $CopyKernel $KernelImage \
                $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    cp $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/$InstallName

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;
    cp $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac $RPM_BUILD_ROOT/lib/modules/$KernelVer/.vmlinuz.hmac

    if [ $DoModules -eq 1 ]; then
	# Override $(mod-fw) because we don't want it to install any firmware
	# we'll get it from the linux-firmware package and we don't want conflicts
	%{make} %{?_smp_mflags} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT %{?_smp_mflags} modules_install KERNELRELEASE=$KernelVer mod-fw=
    fi

%if %{with_gcov}
    # install gcov-needed files to $BUILDROOT/$BUILD/...:
    #   gcov_info->filename is absolute path
    #   gcno references to sources can use absolute paths (e.g. in out-of-tree builds)
    #   sysfs symlink targets (set up at compile time) use absolute paths to BUILD dir
    find . \( -name '*.gcno' -o -name '*.[chS]' \) -exec install -D '{}' "$RPM_BUILD_ROOT/$(pwd)/{}" \;
%endif

    # add an a noop %%defattr statement 'cause rpm doesn't like empty file list files
    echo '%%defattr(-,-,-)' > ../kernel${Variant:+-${Variant}}-ldsoconf.list
    if [ $DoVDSO -ne 0 ]; then
        %{make} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
        if [ -s ldconfig-kernel.conf ]; then
             install -D -m 444 ldconfig-kernel.conf \
                $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
	     echo /etc/ld.so.conf.d/kernel-$KernelVer.conf >> ../kernel${Variant:+-${Variant}}-ldsoconf.list
        fi

        rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
    fi

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # CONFIG_KERNEL_HEADER_TEST generates some extra files in the process of
    # testing so just delete
    find . -name *.h.s -delete
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ ! -e Module.symvers ]; then
        touch Module.symvers
    fi
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
    cp $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz $RPM_BUILD_ROOT/lib/modules/$KernelVer/symvers.gz

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Variant ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Variant $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        # for now, don't keep it around.
        rm $RPM_BUILD_ROOT/Module.kabi
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidupchk}
    echo "**** kABI DUP checking is enabled in kernel SPEC file. ****"
    if [ -e $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Variant ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Variant $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        # for now, don't keep it around.
        rm $RPM_BUILD_ROOT/Module.kabi
    else
        echo "**** NOTE: Cannot find DUP reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidw_base}
    # Don't build kabi base for debug kernels
    if [ "$Variant" != "zfcpdump" -a "$Variant" != "debug" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf

        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/stablelists
        tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/stablelists

        echo "**** GENERATING DWARF-based kABI baseline dataset ****"
        chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
        $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
            "$RPM_BUILD_ROOT/kabi-dwarf/stablelists/kabi-current/kabi_stablelist_%{_target_cpu}" \
            "$(pwd)" \
            "$RPM_BUILD_ROOT/kabidw-base/%{_target_cpu}${Variant:+.${Variant}}" || :

        rm -rf $RPM_BUILD_ROOT/kabi-dwarf
    fi
%endif

%if %{with_kabidwchk}
    if [ "$Variant" != "zfcpdump" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf
        if [ -d "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}" ]; then
            mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/stablelists
            tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/stablelists

            echo "**** GENERATING DWARF-based kABI dataset ****"
            chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
                "$RPM_BUILD_ROOT/kabi-dwarf/stablelists/kabi-current/kabi_stablelist_%{_target_cpu}" \
                "$(pwd)" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}.tmp" || :

            echo "**** kABI DWARF-based comparison report ****"
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh compare \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}.tmp" || :
            echo "**** End of kABI DWARF-based comparison report ****"
        else
            echo "**** Baseline dataset for kABI DWARF-BASED comparison report not found ****"
        fi

        rm -rf $RPM_BUILD_ROOT/kabi-dwarf
    fi
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/tracing
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/spdxcheck.py

    # Files for 'make scripts' to succeed with kernel-devel.
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/security/selinux/include
    cp -a --parents security/selinux/include/classmap.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents security/selinux/include/initial_sid_to_string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/include/tools
    cp -a --parents tools/include/tools/be_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/tools/le_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # Files for 'make prepare' to succeed with kernel-devel.
    cp -a --parents tools/include/linux/compiler* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/linux/types.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/build/Build.include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/build/Build $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/build/fixdep.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/sync-check.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/bpf/resolve_btfids $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    cp --parents security/selinux/include/policycap_names.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents security/selinux/include/policycap.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    cp -a --parents tools/include/asm-generic $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/linux $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/uapi/asm $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/uapi/asm-generic $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/uapi/linux $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/vdso $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/scripts/utilities.mak $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/lib/subcmd $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/lib/*.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/*.[ch] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/Build $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/include/objtool/*.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/lib/bpf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/lib/bpf/Build $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    if [ -f tools/objtool/objtool ]; then
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
    fi
    if [ -f tools/objtool/fixdep ]; then
      cp -a tools/objtool/fixdep $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
    fi
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    if [ -f arch/%{asmarch}/kernel/module.lds ]; then
      cp -a --parents arch/%{asmarch}/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    find $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
%ifarch ppc64le
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # arch/arm64/include/asm/xen references arch/arm
    cp -a --parents arch/arm/include/asm/xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    # arch/arm64/include/asm/opcodes.h references arch/arm
    cp -a --parents arch/arm/include/asm/opcodes.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    # include the machine specific headers for ARM variants, if available.
%ifarch %{arm}
    if [ -d arch/%{asmarch}/mach-${Variant}/include ]; then
      cp -a --parents arch/%{asmarch}/mach-${Variant}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    # include a few files for 'make prepare'
    cp -a --parents arch/arm/tools/gen-mach-types $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/arm/tools/mach-types $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/

%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
%ifarch i686 x86_64
    # files for 'make prepare' to succeed with kernel-devel
    cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_32.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_64.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_common.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/purgatory.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/stack.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/setup-x86_64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/entry64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/ctype.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/

    cp -a --parents scripts/syscalltbl.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents scripts/syscallhdr.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/

    cp -a --parents tools/arch/x86/include/asm $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/arch/x86/include/uapi/asm $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/objtool/arch/x86/lib $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/arch/x86/lib/ $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/arch/x86/tools/gen-insn-attr-x86.awk $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/objtool/arch/x86/ $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

%endif
    # Clean up intermediate tools files
    find $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h

    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    eu-readelf -n vmlinux | grep "Build ID" | awk '{print $NF}' > vmlinux.id
    cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    if [ -n "%{vmlinux_decompressor}" ]; then
	    eu-readelf -n  %{vmlinux_decompressor} | grep "Build ID" | awk '{print $NF}' > vmlinux.decompressor.id
	    # Without build-id the build will fail. But for s390 the build-id
	    # wasn't added before 5.11. In case it is missing prefer not
	    # packaging the debuginfo over a build failure.
	    if [ -s vmlinux.decompressor.id ]; then
		    cp vmlinux.decompressor.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.decompressor.id
		    cp %{vmlinux_decompressor} $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer/vmlinux.decompressor
	    fi
    fi
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
        LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking \
      'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
    collect_modules_list block \
      'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm \
      'drm_open|drm_init'
    collect_modules_list modesetting \
      'drm_crtc_init'

    # detect missing or incorrect license tags
    ( find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name '*.ko' | xargs /sbin/modinfo -l | \
        grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' ) && exit 1

    remove_depmod_files()
    {
        # remove files that will be auto generated by depmod at rpm -i time
        pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
            rm -f modules.{alias,alias.bin,builtin.alias.bin,builtin.bin} \
                  modules.{dep,dep.bin,devname,softdep,symbols,symbols.bin}
        popd
    }

    remove_depmod_files

    # Identify modules in the kernel-modules-extras package
    %{SOURCE17} $RPM_BUILD_ROOT lib/modules/$KernelVer $RPM_SOURCE_DIR/mod-extra.list
    # Identify modules in the kernel-modules-extras package
    %{SOURCE17} $RPM_BUILD_ROOT lib/modules/$KernelVer %{SOURCE54} internal

    #
    # Generate the kernel-core and kernel-modules files lists
    #

    # Copy the System.map file for depmod to use, and create a backup of the
    # full module tree so we can restore it after we're done filtering
    cp System.map $RPM_BUILD_ROOT/.
    pushd $RPM_BUILD_ROOT
    mkdir restore
    cp -r lib/modules/$KernelVer/* restore/.

    # don't include anything going into kernel-modules-extra in the file lists
    xargs rm -rf < mod-extra.list
    # don't include anything going int kernel-modules-internal in the file lists
    xargs rm -rf < mod-internal.list

    if [ $DoModules -eq 1 ]; then
	# Find all the module files and filter them out into the core and
	# modules lists.  This actually removes anything going into -modules
	# from the dir.
	find lib/modules/$KernelVer/kernel -name *.ko | sort -n > modules.list
	cp $RPM_SOURCE_DIR/filter-*.sh .
	./filter-modules.sh modules.list %{_target_cpu}
	rm filter-*.sh

	# Run depmod on the resulting module tree and make sure it isn't broken
	depmod -b . -aeF ./System.map $KernelVer &> depmod.out
	if [ -s depmod.out ]; then
	    echo "Depmod failure"
	    cat depmod.out
	    exit 1
	else
	    rm depmod.out
	fi
    else
	# Ensure important files/directories exist to let the packaging succeed
	echo '%%defattr(-,-,-)' > modules.list
	echo '%%defattr(-,-,-)' > k-d.list
	mkdir -p lib/modules/$KernelVer/kernel
	# Add files usually created by make modules, needed to prevent errors
	# thrown by depmod during package installation
	touch lib/modules/$KernelVer/modules.order
	touch lib/modules/$KernelVer/modules.builtin
    fi

    remove_depmod_files

    # Go back and find all of the various directories in the tree.  We use this
    # for the dir lists in kernel-core
    find lib/modules/$KernelVer/kernel -mindepth 1 -type d | sort -n > module-dirs.list

    # Cleanup
    rm System.map
    cp -r restore/* lib/modules/$KernelVer/.
    rm -rf restore
    popd

    # Make sure the files lists start with absolute paths or rpmbuild fails.
    # Also add in the dir entries
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/k-d.list > ../kernel${Variant:+-${Variant}}-modules.list
    sed -e 's/^lib*/%dir \/lib/' %{?zipsed} $RPM_BUILD_ROOT/module-dirs.list > ../kernel${Variant:+-${Variant}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules.list >> ../kernel${Variant:+-${Variant}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/mod-extra.list >> ../kernel${Variant:+-${Variant}}-modules-extra.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/mod-internal.list >> ../kernel${Variant:+-${Variant}}-modules-internal.list

    # Cleanup
    rm -f $RPM_BUILD_ROOT/k-d.list
    rm -f $RPM_BUILD_ROOT/modules.list
    rm -f $RPM_BUILD_ROOT/module-dirs.list
    rm -f $RPM_BUILD_ROOT/mod-extra.list
    rm -f $RPM_BUILD_ROOT/mod-internal.list

%if %{signmodules}
    if [ $DoModules -eq 1 ]; then
	# Save the signing keys so we can sign the modules in __modsign_install_post
	cp certs/signing_key.pem certs/signing_key.pem.sign${Variant:++${Variant}}
	cp certs/signing_key.x509 certs/signing_key.x509.sign${Variant:++${Variant}}
    fi
%endif

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir

    # This is going to create a broken link during the build, but we don't use
    # it after this point.  We need the link to actually point to something
    # when kernel-devel is installed, and a relative link doesn't work across
    # the F17 UsrMove feature.
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

%ifnarch armv7hl
    # Generate vmlinux.h and put it to kernel-devel path
    bpftool btf dump file vmlinux format c > $RPM_BUILD_ROOT/$DevelDir/vmlinux.h
%endif

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -delete

    # Generate crashkernel default config
    %{SOURCE57} "$KernelVer" "$Arch" "$RPM_BUILD_ROOT"

    # Red Hat UEFI Secure Boot CA cert, which can be used to authenticate the kernel
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer
    %ifarch x86_64 aarch64
       install -m 0644 %{secureboot_ca_0} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca-20200609.cer
       install -m 0644 %{secureboot_ca_1} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca-20140212.cer
       ln -s kernel-signing-ca-20200609.cer $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer
    %else
       install -m 0644 %{secureboot_ca_0} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer
    %endif
    %ifarch s390x ppc64le
    if [ $DoModules -eq 1 ]; then
	if [ -x /usr/bin/rpm-sign ]; then
	    install -m 0644 %{secureboot_key_0} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	else
	    install -m 0644 certs/signing_key.x509.sign${Variant:++${Variant}} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer
	    openssl x509 -in certs/signing_key.pem.sign${Variant:++${Variant}} -outform der -out $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	    chmod 0644 $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	fi
    fi
    %endif

%if %{with_ipaclones}
    MAXPROCS=$(echo %{?_smp_mflags} | sed -n 's/-j\s*\([0-9]\+\)/\1/p')
    if [ -z "$MAXPROCS" ]; then
        MAXPROCS=1
    fi
    if [ "$Variant" == "" ]; then
        mkdir -p $RPM_BUILD_ROOT/$DevelDir-ipaclones
        find . -name '*.ipa-clones' | xargs -i{} -r -n 1 -P $MAXPROCS install -m 644 -D "{}" "$RPM_BUILD_ROOT/$DevelDir-ipaclones/{}"
    fi
%endif

}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVERREL}


%if %{with_debug}
BuildKernel %make_target %kernel_image %{_use_vdso} debug
%endif

%if %{with_zfcpdump}
BuildKernel %make_target %kernel_image %{_use_vdso} zfcpdump
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image %{use_vdso} lpae
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image %{_use_vdso}
%endif

%ifnarch noarch i686
%if !%{with_debug} && !%{with_zfcpdump} && !%{with_pae} && !%{with_up}
# If only building the user space tools, then initialize the build environment
# and some variables so that the various userspace tools can be built.
InitBuildVars
%endif
%endif

%ifarch aarch64
%global perf_build_extra_opts CORESIGHT=1
%endif
%global perf_make \
  %{__make} %{?make_opts} EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{?cross_opts} -C tools/perf V=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 LIBBPF_DYNAMIC=1 LIBTRACEEVENT_DYNAMIC=1 %{?perf_build_extra_opts} prefix=%{_prefix} PYTHON=%{__python3}
%if %{with_perf}
# perf
# make sure check-headers.sh is executable
chmod +x tools/perf/check-headers.sh
%{perf_make} DESTDIR=$RPM_BUILD_ROOT all
%endif

%global tools_make \
  %{make} CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{?make_opts}

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
%{tools_make} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false DEBUG=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    %{tools_make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   %{tools_make}
   popd
   pushd tools/power/x86/turbostat
   %{tools_make}
   popd
   pushd tools/power/x86/intel-speed-select
   %{make}
   popd
%endif
%endif
pushd tools/thermal/tmon/
%{tools_make}
popd
pushd tools/iio/
%{tools_make}
popd
pushd tools/gpio/
%{tools_make}
popd
# build VM tools
pushd tools/vm/
%{tools_make} slabinfo page_owner_sort
popd
%endif

if [ -f $DevelDir/vmlinux.h ]; then
  RPM_VMLINUX_H=$DevelDir/vmlinux.h
fi

%global bpftool_make \
  %{__make} EXTRA_CFLAGS="${RPM_OPT_FLAGS}" EXTRA_LDFLAGS="%{__global_ldflags}" DESTDIR=$RPM_BUILD_ROOT %{?make_opts} VMLINUX_H="${RPM_VMLINUX_H}" V=1
%if %{with_bpftool}
pushd tools/bpf/bpftool
%{bpftool_make}
popd
%endif

%if %{with_selftests}
# Unfortunately, samples/bpf/Makefile expects that the headers are installed
# in the source tree. We installed them previously to $RPM_BUILD_ROOT/usr
# but there's no way to tell the Makefile to take them from there.
%{make} %{?_smp_mflags} headers_install
%{make} %{?_smp_mflags} ARCH=$Arch V=1 M=samples/bpf/

# Prevent bpf selftests to build bpftool repeatedly:
export BPFTOOL=$(pwd)/tools/bpf/bpftool/bpftool

pushd tools/testing/selftests
# We need to install here because we need to call make with ARCH set which
# doesn't seem possible to do in the install section.
%{make} %{?_smp_mflags} ARCH=$Arch V=1 TARGETS="bpf livepatch net net/forwarding net/mptcp netfilter tc-testing" SKIP_TARGETS="" INSTALL_PATH=%{buildroot}%{_libexecdir}/kselftests VMLINUX_H="${RPM_VMLINUX_H}" install

# 'make install' for bpf is broken and upstream refuses to fix it.
# Install the needed files manually.
for dir in bpf bpf/no_alu32 bpf/progs; do
	# In ARK, the rpm build continues even if some of the selftests
	# cannot be built. It's not always possible to build selftests,
	# as upstream sometimes dependens on too new llvm version or has
	# other issues. If something did not get built, just skip it.
	test -d $dir || continue
	mkdir -p %{buildroot}%{_libexecdir}/kselftests/$dir
	find $dir -maxdepth 1 -type f \( -executable -o -name '*.py' -o -name settings -o \
		-name 'btf_dump_test_case_*.c' -o \
		-name '*.o' -exec sh -c 'readelf -h "{}" | grep -q "^  Machine:.*BPF"' \; \) -print0 | \
	xargs -0 cp -t %{buildroot}%{_libexecdir}/kselftests/$dir || true
done
popd
export -n BPFTOOL
%endif

%if %{with_doc}
# Make the HTML pages.
%{__make} PYTHON=/usr/bin/python3 htmldocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "variant" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that variant.  3) We
# grab the arch and invoke mod-sign.sh command to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Don't sign modules for the zfcpdump variant as it is monolithic.

%define __modsign_install_post \
  if [ "%{signmodules}" -eq "1" ]; then \
    if [ "%{with_pae}" -ne "0" ]; then \
       %{modsign_cmd} certs/signing_key.pem.sign+lpae certs/signing_key.x509.sign+lpae $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+lpae/ \
    fi \
    if [ "%{with_debug}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+debug certs/signing_key.x509.sign+debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+debug/ \
    fi \
    if [ "%{with_up}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign certs/signing_key.x509.sign $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/ \
    fi \
  fi \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs -P%{zcpu} xz; \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%endif

%endif

# We don't want to package debuginfo for self-tests and samples but
# we have to delete them to avoid an error messages about unpackaged
# files.
# Delete the debuginfo for kernel-devel files
%define __remove_unwanted_dbginfo_install_post \
  if [ "%{with_selftests}" -ne "0" ]; then \
    rm -rf $RPM_BUILD_ROOT/usr/lib/debug/usr/libexec/ksamples; \
    rm -rf $RPM_BUILD_ROOT/usr/lib/debug/usr/libexec/kselftests; \
  fi \
  rm -rf $RPM_BUILD_ROOT/usr/lib/debug/usr/src; \
%{nil}

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__remove_unwanted_dbginfo_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVERREL}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}-%{pkgrelease}

# copy the source over
mkdir -p $docdir
tar -h -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# with_doc
%endif

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
%{__make} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) -delete

%endif

%if %{with_cross_headers}
%if 0%{?fedora}
HDR_ARCH_LIST='arm arm64 powerpc s390 x86'
%else
HDR_ARCH_LIST='arm64 powerpc s390 x86'
%endif
mkdir -p $RPM_BUILD_ROOT/usr/tmp-headers

for arch in $HDR_ARCH_LIST; do
	mkdir $RPM_BUILD_ROOT/usr/tmp-headers/arch-${arch}
	%{__make} ARCH=${arch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr/tmp-headers/arch-${arch} headers_install
done

find $RPM_BUILD_ROOT/usr/tmp-headers \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) -delete

# Copy all the architectures we care about to their respective asm directories
for arch in $HDR_ARCH_LIST ; do
	mkdir -p $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include
	mv $RPM_BUILD_ROOT/usr/tmp-headers/arch-${arch}/include/* $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/
done

rm -rf $RPM_BUILD_ROOT/usr/tmp-headers
%endif

%if %{with_kernel_abi_stablelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/
mkdir -p $INSTALL_KABI_PATH

# install kabi releases directories
tar xjvf %{SOURCE300} -C $INSTALL_KABI_PATH
# with_kernel_abi_stablelists
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT lib=%{_lib} install-bin
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace

# For both of the below, yes, this should be using a macro but right now
# it's hard coded and we don't actually want it anyway right now.
# Whoever wants examples can fix it up!

# remove examples
rm -rf %{buildroot}/usr/lib/perf/examples
rm -rf %{buildroot}/usr/lib/perf/include

# python-perf extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
mkdir -p %{buildroot}/%{_mandir}/man1
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man

# remove any tracevent files, eg. its plugins still gets built and installed,
# even if we build against system's libtracevent during perf build (by setting
# LIBTRACEEVENT_DYNAMIC=1 above in perf_make macro). Those files should already
# ship with libtraceevent package.
rm -rf %{buildroot}%{_libdir}/traceevent
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
%{make} -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif
%ifarch x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   %{tools_make} DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   %{tools_make} DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/intel-speed-select
   %{tools_make} CFLAGS+="-D_GNU_SOURCE -Iinclude" DESTDIR=%{buildroot} install
   popd
%endif
pushd tools/thermal/tmon
%{tools_make} INSTALL_ROOT=%{buildroot} install
popd
pushd tools/iio
%{tools_make} DESTDIR=%{buildroot} install
popd
pushd tools/gpio
%{tools_make} DESTDIR=%{buildroot} install
popd
install -m644 -D %{SOURCE2002} %{buildroot}%{_sysconfdir}/logrotate.d/kvm_stat
pushd tools/kvm/kvm_stat
%{__make} INSTALL_ROOT=%{buildroot} install-tools
%{__make} INSTALL_ROOT=%{buildroot} install-man
install -m644 -D kvm_stat.service %{buildroot}%{_unitdir}/kvm_stat.service
popd
# install VM tools
pushd tools/vm/
install -m755 slabinfo %{buildroot}%{_bindir}/slabinfo
install -m755 page_owner_sort %{buildroot}%{_bindir}/page_owner_sort
popd
%endif

if [ -f $DevelDir/vmlinux.h ]; then
  RPM_VMLINUX_H=$DevelDir/vmlinux.h
fi

%if %{with_bpftool}
pushd tools/bpf/bpftool
%{bpftool_make} prefix=%{_prefix} bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} install doc-install
popd
%endif

%if %{with_selftests}
pushd samples
install -d %{buildroot}%{_libexecdir}/ksamples
# install bpf samples
pushd bpf
install -d %{buildroot}%{_libexecdir}/ksamples/bpf
find -type f -executable -exec install -m755 {} %{buildroot}%{_libexecdir}/ksamples/bpf \;
install -m755 *.sh %{buildroot}%{_libexecdir}/ksamples/bpf
# test_lwt_bpf.sh compiles test_lwt_bpf.c when run; this works only from the
# kernel tree. Just remove it.
rm %{buildroot}%{_libexecdir}/ksamples/bpf/test_lwt_bpf.sh
install -m644 *_kern.o %{buildroot}%{_libexecdir}/ksamples/bpf || true
install -m644 tcp_bpf.readme %{buildroot}%{_libexecdir}/ksamples/bpf
popd
# install pktgen samples
pushd pktgen
install -d %{buildroot}%{_libexecdir}/ksamples/pktgen
find . -type f -executable -exec install -m755 {} %{buildroot}%{_libexecdir}/ksamples/pktgen/{} \;
find . -type f ! -executable -exec install -m644 {} %{buildroot}%{_libexecdir}/ksamples/pktgen/{} \;
popd
popd
# install drivers/net/mlxsw selftests
pushd tools/testing/selftests/drivers/net/mlxsw
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/drivers/net/mlxsw/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/drivers/net/mlxsw/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/drivers/net/mlxsw/{} \;
popd
# install drivers/net/netdevsim selftests
pushd tools/testing/selftests/drivers/net/netdevsim
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/drivers/net/netdevsim/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/drivers/net/netdevsim/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/drivers/net/netdevsim/{} \;
popd
# install net/forwarding selftests
pushd tools/testing/selftests/net/forwarding
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/net/forwarding/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/net/forwarding/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/net/forwarding/{} \;
popd
# install net/mptcp selftests
pushd tools/testing/selftests/net/mptcp
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/net/mptcp/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/net/mptcp/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/net/mptcp/{} \;
popd
# install tc-testing selftests
pushd tools/testing/selftests/tc-testing
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/tc-testing/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/tc-testing/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/tc-testing/{} \;
popd
# install livepatch selftests
pushd tools/testing/selftests/livepatch
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/livepatch/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/livepatch/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/livepatch/{} \;
popd
# install netfilter selftests
pushd tools/testing/selftests/netfilter
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/netfilter/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/netfilter/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/netfilter/{} \;
popd
%endif

###
### clean
###

###
### scripts
###

%if %{with_tools}
%post -n kernel-tools-libs
/sbin/ldconfig

%postun -n kernel-tools-libs
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
# Note we don't run hardlink if ostree is in use, as ostree is
# a far more sophisticated hardlink implementation.
# https://github.com/projectatomic/rpm-ostree/commit/58a79056a889be8814aa51f507b2c7a4dccee526
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/bin/hardlink -a ! -e /run/ostree-booted ] \
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:+%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f > /dev/null\
     done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-extra package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_extra_post [<subpackage>]
#
%define kernel_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-internal package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_internal_post [<subpackage>]
#
%define kernel_modules_internal_post() \
%{expand:%%post %{?1:%{1}-}modules-internal}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-internal}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_post [<subpackage>]
#
%define kernel_modules_post() \
%{expand:%%post %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1:%{1}-}core}\
%if 0%{!?fedora:1}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%endif\
/bin/kernel-install add %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_post %{?-v*}}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
%{expand:%%kernel_modules_internal_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*:%{-v*}-}core}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1:%{1}-}core}\
/bin/kernel-install remove %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%if %{with_pae}
%kernel_variant_preun lpae
%kernel_variant_post -v lpae -r (kernel|kernel-smp)
%endif

%if %{with_debug}
%kernel_variant_preun debug
%kernel_variant_post -v debug
%endif

%if %{with_zfcpdump}
%kernel_variant_preun zfcpdump
%kernel_variant_post -v zfcpdump
%endif

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
/usr/include/*
%endif

%if %{with_cross_headers}
%files cross-headers
/usr/*-linux-gnu/include/*
%endif

%if %{with_kernel_abi_stablelists}
%files -n kernel-abi-stablelists
/lib/modules/kabi-*
%endif

%if %{with_kabidw_base}
%ifarch x86_64 s390x ppc64 ppc64le aarch64
%files kernel-kabidw-base-internal
%defattr(-,root,root)
/kabidw-base/%{_target_cpu}/*
%endif
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}-%{pkgrelease}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}-%{pkgrelease}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}-%{pkgrelease}
%endif

%if %{with_perf}
%files -n perf
%{_bindir}/perf
%{_libdir}/libperf-jvmti.so
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_datadir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KVERREL}/tools/perf/Documentation/examples.txt
%{_docdir}/perf-tip/tips.txt

%files -n python3-perf
%{python3_sitearch}/*

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo

%files -f python3-perf-debuginfo.list -n python3-perf-debuginfo
%endif
# with_perf
%endif

%if %{with_tools}
%ifnarch %{cpupowerarchs}
%files -n kernel-tools
%else
%files -n kernel-tools -f cpupower.lang
%{_bindir}/cpupower
%{_datadir}/bash-completion/completions/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%{_bindir}/intel-speed-select
%endif
# cpupowerarchs
%endif
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%{_bindir}/gpio-watch
%{_mandir}/man1/kvm_stat*
%{_bindir}/kvm_stat
%{_unitdir}/kvm_stat.service
%config(noreplace) %{_sysconfdir}/logrotate.d/kvm_stat
%{_bindir}/page_owner_sort
%{_bindir}/slabinfo

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n kernel-tools-libs-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif
# with_tools
%endif

%if %{with_bpftool}
%files -n bpftool
%{_sbindir}/bpftool
%{_sysconfdir}/bash_completion.d/bpftool
%{_mandir}/man8/bpftool-cgroup.8.gz
%{_mandir}/man8/bpftool-gen.8.gz
%{_mandir}/man8/bpftool-iter.8.gz
%{_mandir}/man8/bpftool-link.8.gz
%{_mandir}/man8/bpftool-map.8.gz
%{_mandir}/man8/bpftool-prog.8.gz
%{_mandir}/man8/bpftool-perf.8.gz
%{_mandir}/man8/bpftool.8.gz
%{_mandir}/man8/bpftool-net.8.gz
%{_mandir}/man8/bpftool-feature.8.gz
%{_mandir}/man8/bpftool-btf.8.gz
%{_mandir}/man8/bpftool-struct_ops.8.gz

%if %{with_debuginfo}
%files -f bpftool-debuginfo.list -n bpftool-debuginfo
%defattr(-,root,root)
%endif
%endif

%if %{with_selftests}
%files selftests-internal
%{_libexecdir}/ksamples
%{_libexecdir}/kselftests
%endif

# empty meta-package
%ifnarch %nobuildarches noarch
%files
%endif

%if %{with_gcov}
%ifarch x86_64 s390x ppc64le aarch64
%files gcov
%{_builddir}
%endif
%endif

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <use_vdso> <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{2}\
%{expand:%%files -f kernel-%{?3:%{3}-}core.list %{?1:-f kernel-%{?3:%{3}-}ldsoconf.list} %{?3:%{3}-}core}\
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING-%{version}-%{release}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/%{?-k:%{-k*}}%{!?-k:vmlinuz}\
%ghost /%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/.vmlinuz.hmac \
%ghost /%{image_install_path}/.vmlinuz-%{KVERREL}%{?3:+%{3}}.hmac \
%ifarch %{arm} aarch64\
/lib/modules/%{KVERREL}%{?3:+%{3}}/dtb \
%ghost /%{image_install_path}/dtb-%{KVERREL}%{?3:+%{3}} \
%endif\
%attr(0600, root, root) /lib/modules/%{KVERREL}%{?3:+%{3}}/System.map\
%ghost %attr(0600, root, root) /boot/System.map-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/symvers.gz\
/lib/modules/%{KVERREL}%{?3:+%{3}}/config\
%ghost %attr(0600, root, root) /boot/symvers-%{KVERREL}%{?3:+%{3}}.gz\
%ghost %attr(0600, root, root) /boot/initramfs-%{KVERREL}%{?3:+%{3}}.img\
%ghost %attr(0644, root, root) /boot/config-%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}/kernel\
/lib/modules/%{KVERREL}%{?3:+%{3}}/build\
/lib/modules/%{KVERREL}%{?3:+%{3}}/source\
/lib/modules/%{KVERREL}%{?3:+%{3}}/updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/weak-updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/crashkernel.default\
%{_datadir}/doc/kernel-keys/%{KVERREL}%{?3:+%{3}}\
%if %{1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/vdso\
%endif\
/lib/modules/%{KVERREL}%{?3:+%{3}}/modules.*\
%{expand:%%files -f kernel-%{?3:%{3}-}modules.list %{?3:%{3}-}modules}\
%{expand:%%files %{?3:%{3}-}devel}\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?3:+%{3}}\
%{expand:%%files %{?3:%{3}-}devel-matched}\
%{expand:%%files -f kernel-%{?3:%{3}-}modules-extra.list %{?3:%{3}-}modules-extra}\
%config(noreplace) /etc/modprobe.d/*-blacklist.conf\
%{expand:%%files -f kernel-%{?3:%{3}-}modules-internal.list %{?3:%{3}-}modules-internal}\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?3}.list %{?3:%{3}-}debuginfo}\
%endif\
%endif\
%if %{?3:1} %{!?3:0}\
%{expand:%%files %{3}}\
%endif\
%endif\
%{nil}

%kernel_variant_files %{_use_vdso} %{with_up}
%kernel_variant_files %{_use_vdso} %{with_debug} debug
%if %{with_debug_meta}
%files debug
%files debug-core
%files debug-devel
%files debug-devel-matched
%files debug-modules
%files debug-modules-extra
%endif
%kernel_variant_files %{use_vdso} %{with_pae} lpae
%kernel_variant_files %{_use_vdso} %{with_zfcpdump} zfcpdump

%define kernel_variant_ipaclones(k:) \
%if %{1}\
%if %{with_ipaclones}\
%{expand:%%files %{?2:%{2}-}ipaclones-internal}\
%defattr(-,root,root)\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?2:+%{2}}-ipaclones\
%endif\
%endif\
%{nil}

%kernel_variant_ipaclones %{with_up}

# plz don't put in a version string unless you're going to tag
# and build.
#
#
%changelog
* Thu Sep 30 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.9-0]
- Revert "block, bfq: honor already-setup queue merges" (Jens Axboe)

* Mon Sep 27 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.8-0]
- thermal/drivers/int340x: Do not set a wrong tcc offset on resume (Antoine Tenart)

* Wed Sep 22 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.7-0]
- Add Fedora 34 and 33 to release_targets (Justin M. Forbes)
- Strip [redhat] entries from changelog (Justin M. Forbes)

* Sat Sep 18 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.6-0]
- Fix changelog generation (Justin M. Forbes)
- Clean up changelog (Justin M. Forbes)
- ACPI: PM: s2idle: Run both AMD and Microsoft methods if both are supported (Mario Limonciello)
- Don't tag a release as [redhat] (Justin M. Forbes)
- Fixes for changelog that I think will help with the next stable bump (Justin M. Forbes)

* Thu Sep 16 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.5-0]
- kernel-5.14.5-0 (Justin M. Forbes)

* Wed Sep 15 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.4-0]
- kernel-5.14.4-0 (Justin M. Forbes)
- Build kernel-doc for Fedora (Justin M. Forbes)

* Wed Sep 08 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.3-0]
- kernel-5.14.3-0 (Justin M. Forbes)
- Revert "team: mark team driver as deprecated" (Justin M. Forbes)

* Fri Sep 03 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.2-0]
- kernel-5.14.2-0 (Justin M. Forbes)
- Setup for building fedora-5.14 branch (Justin M. Forbes)

* Mon Aug 30 2021 Justin M. Forbes <jforbes@fedoraproject.org> [5.14.1-0]
- kernel-5.14.1-0 (Justin M. Forbes)
- iwlwifi Add support for ax201 in Samsung Galaxy Book Flex2 Alpha (Justin M. Forbes)
- arm64: use common CONFIG_MAX_ZONEORDER for arm kernel (Mark Salter)
- Create Makefile.variables for a single point of configuration change (Justin M. Forbes)
- Clean up changelog (Justin M. Forbes)
- ACPI: PM: s2idle: Run both AMD and Microsoft methods if both are supported (Mario Limonciello)
- Don't tag a release as [redhat] (Justin M. Forbes)
- Fixes for changelog that I think will help with the next stable bump (Justin M. Forbes)
- Build kernel-doc for Fedora (Justin M. Forbes)
- Revert "team: mark team driver as deprecated" (Justin M. Forbes)
- Setup for building fedora-5.14 branch (Justin M. Forbes)
- iwlwifi Add support for ax201 in Samsung Galaxy Book Flex2 Alpha (Justin M. Forbes)
- arm64: use common CONFIG_MAX_ZONEORDER for arm kernel (Mark Salter)
- Create Makefile.variables for a single point of configuration change (Justin M. Forbes)
- rpmspec: drop traceevent files instead of just excluding them from files list (Herton R. Krzesinski) [1967640]
- redhat/config: Enablement of CONFIG_PAPR_SCM for PowerPC (Gustavo Walbon) [1962936]
- Attempt to fix Intel PMT code (David Arcari)
- CI: Enable realtime branch testing (Veronika Kabatova)
- CI: Enable realtime checks for c9s and RHEL9 (Veronika Kabatova)
- ark: wireless: enable all rtw88 pcie wirless variants (Peter Robinson)
- wireless: rtw88: move debug options to common/debug (Peter Robinson)
- fedora: minor PTP clock driver cleanups (Peter Robinson)
- common: x86: enable VMware PTP support on ark (Peter Robinson)
- arm64: dts: rockchip: Disable CDN DP on Pinebook Pro (Matthias Brugger)
- arm64: dts: rockchip: Setup USB typec port as datarole on (Dan Johansen)
- xfs: drop experimental warnings for bigtime and inobtcount (Bill O'Donnell) [1995321]
- Disable liquidio driver on ark/rhel (Herton R. Krzesinski) [1993393]
- More Fedora config updates (Justin M. Forbes)
- Fedora config updates for 5.14 (Justin M. Forbes)
- CI: Rename ARK CI pipeline type (Veronika Kabatova)
- CI: Finish up c9s config (Veronika Kabatova)
- CI: Update ppc64le config (Veronika Kabatova)
- CI: use more templates (Veronika Kabatova)
- Filter updates for aarch64 (Justin M. Forbes)
- increase CONFIG_NODES_SHIFT for aarch64 (Chris von Recklinghausen) [1890304]
- redhat: configs: Enable CONFIG_WIRELESS_HOTKEY (Hans de Goede)
- redhat/configs: Update CONFIG_NVRAM (Desnes A. Nunes do Rosario) [1988254]
- common: serial: build in SERIAL_8250_LPSS for x86 (Peter Robinson)
- powerpc: enable CONFIG_FUNCTION_PROFILER (Diego Domingos) [1831065]
- crypto: rng - Override drivers/char/random in FIPS mode (Herbert Xu)
- random: Add hook to override device reads and getrandom(2) (Herbert Xu)
- redhat/configs: Disable Soft-RoCE driver (Kamal Heib)
- redhat/configs/evaluate_configs: Update help output (Prarit Bhargava)
- redhat/configs: Double MAX_LOCKDEP_CHAINS (Justin M. Forbes)
- fedora: configs: Fix WM5102 Kconfig (Hans de Goede)
- powerpc: enable CONFIG_POWER9_CPU (Diego Domingos) [1876436]
- redhat/configs: Fix CONFIG_VIRTIO_IOMMU to 'y' on aarch64 (Eric Auger) [1972795]
- filter-modules.sh: add more sound modules to filter (Jaroslav Kysela)
- redhat/configs: sound configuration cleanups and updates (Jaroslav Kysela)
- common: Update for CXL (Compute Express Link) configs (Peter Robinson)
- redhat: configs: disable CRYPTO_SM modules (Herton R. Krzesinski) [1990040]
- Remove fedora version of the LOCKDEP_BITS, we should use common (Justin M. Forbes)
- Re-enable sermouse for x86 (rhbz 1974002) (Justin M. Forbes)
- Fedora 5.14 configs round 1 (Justin M. Forbes)
- redhat: add gating configuration for centos stream/rhel9 (Herton R. Krzesinski)
- x86: configs: Enable CONFIG_TEST_FPU for debug kernels (Vitaly Kuznetsov) [1988384]
- redhat/configs: Move CHACHA and POLY1305 to core kernel to allow BIG_KEYS=y (root) [1983298]
- kernel.spec: fix build of samples/bpf (Jiri Benc)
- Enable OSNOISE_TRACER and TIMERLAT_TRACER (Jerome Marchand) [1979379]
- rpmspec: switch iio and gpio tools to use tools_make (Herton R. Krzesinski) [1956988]
- configs/process_configs.sh: Handle config items with no help text (Patrick Talbert)
- fedora: sound config updates for 5.14 (Peter Robinson)
- fedora: Only enable FSI drivers on POWER platform (Peter Robinson)
- The CONFIG_RAW_DRIVER has been removed from upstream (Peter Robinson)
- fedora: updates for 5.14 with a few disables for common from pending (Peter Robinson)
- fedora: migrate from MFD_TPS68470 -> INTEL_SKL_INT3472 (Peter Robinson)
- fedora: Remove STAGING_GASKET_FRAMEWORK (Peter Robinson)
- Fedora: move DRM_VMWGFX configs from ark -> common (Peter Robinson)
- fedora: arm: disabled unused FB drivers (Peter Robinson)
- fedora: don't enable FB_VIRTUAL (Peter Robinson)
- redhat/configs: Double MAX_LOCKDEP_ENTRIES (Waiman Long) [1940075]
- rpmspec: fix verbose output on kernel-devel installation (Herton R. Krzesinski) [1981406]
- Build Fedora x86s kernels with bytcr-wm5102 (Marius Hoch)
- Deleted redhat/configs/fedora/generic/x86/CONFIG_FB_HYPERV (Patrick Lang)
- rpmspec: correct the ghost initramfs attributes (Herton R. Krzesinski) [1977056]
- rpmspec: amend removal of depmod created files to include modules.builtin.alias.bin (Herton R. Krzesinski) [1977056]
- configs: remove duplicate CONFIG_DRM_HYPERV file (Patrick Talbert)
- CI: use common code for merge and release (Don Zickus)
- rpmspec: add release string to kernel doc directory name (Jan Stancek)
- redhat/configs: Add CONFIG_INTEL_PMT_CRASHLOG (Michael Petlan) [1880486]
- redhat/configs: Add CONFIG_INTEL_PMT_TELEMETRY (Michael Petlan) [1880486]
- redhat/configs: Add CONFIG_MFD_INTEL_PMT (Michael Petlan) [1880486]
- redhat/configs: enable CONFIG_BLK_DEV_ZONED (Ming Lei) [1638087]
- Add --with clang_lto option to build the kernel with Link Time Optimizations (Tom Stellard)
- common: disable DVB_AV7110 and associated pieces (Peter Robinson)
- Fix fedora-only config updates (Don Zickus)
- Fedor config update for new option (Justin M. Forbes)
- redhat/configs: Enable stmmac NIC for x86_64 (Mark Salter)
- all: hyperv: use the DRM driver rather than FB (Peter Robinson)
- all: hyperv: unify the Microsoft HyperV configs (Peter Robinson)
- all: VMWare: clean up VMWare configs (Peter Robinson)
- Update CONFIG_ARM_FFA_TRANSPORT (Patrick Talbert)
- CI: Handle all mirrors (Veronika Kabatova)
- Turn on CONFIG_STACKTRACE for s390x zfpcdump kernels (Justin M. Forbes)
- arm64: switch ark kernel to 4K pagesize (Mark Salter)
- Disable AMIGA_PARTITION and KARMA_PARTITION (Prarit Bhargava) [1802694]
- all: unify and cleanup i2c TPM2 modules (Peter Robinson)
- redhat/configs: Set CONFIG_VIRTIO_IOMMU on aarch64 (Eric Auger) [1972795]
- redhat/configs: Disable CONFIG_RT_GROUP_SCHED in rhel config (Phil Auld)
- redhat/configs: enable KEXEC_SIG which is already enabled in RHEL8 for s390x and x86_64 (Coiby Xu) [1976835]
- rpmspec: do not BuildRequires bpftool on noarch (Herton R. Krzesinski)
- redhat/configs: disable {IMA,EVM}_LOAD_X509 (Bruno Meneguele) [1977529]
- redhat: add secureboot CA certificate to trusted kernel keyring (Bruno Meneguele)
- redhat/configs: enable IMA_ARCH_POLICY for aarch64 and s390x (Bruno Meneguele)
- redhat/configs: Enable CONFIG_MLXBF_GIGE on aarch64 (Alaa Hleihel) [1858599]
- common: enable STRICT_MODULE_RWX everywhere (Peter Robinson)
- COMMON_CLK_STM32MP157_SCMI is bool and selects COMMON_CLK_SCMI (Justin M. Forbes)
- kernel.spec: Add kernel{,-debug}-devel-matched meta packages (Timothée Ravier)
- Turn off with_selftests for Fedora (Justin M. Forbes)
- Don't build bpftool on Fedora (Justin M. Forbes)
- Fix location of syscall scripts for kernel-devel (Justin M. Forbes)
- fedora: arm: Enable some i.MX8 options (Peter Robinson)
- Enable Landlock for Fedora (Justin M. Forbes)
- Filter update for Fedora aarch64 (Justin M. Forbes)
- rpmspec: only build debug meta packages where we build debug ones (Herton R. Krzesinski)
- rpmspec: do not BuildRequires bpftool on nobuildarches (Herton R. Krzesinski)
- redhat/configs: Consolidate CONFIG_HMC_DRV in the common s390x folder (Thomas Huth) [1976270]
- redhat/configs: Consolidate CONFIG_EXPOLINE_OFF in the common folder (Thomas Huth) [1976270]
- redhat/configs: Move CONFIG_HW_RANDOM_S390 into the s390x/ subfolder (Thomas Huth) [1976270]
- redhat/configs: Disable CONFIG_HOTPLUG_PCI_SHPC in the Fedora settings (Thomas Huth) [1976270]
- redhat/configs: Remove the non-existent CONFIG_NO_BOOTMEM switch (Thomas Huth) [1976270]
- redhat/configs: Compile the virtio-console as a module on s390x (Thomas Huth) [1976270]
- redhat/configs: Enable CONFIG_S390_CCW_IOMMU and CONFIG_VFIO_CCW for ARK, too (Thomas Huth) [1976270]
- Revert "Merge branch 'ec_fips' into 'os-build'" (Vladis Dronov) [1947240]
- Fix typos in fedora filters (Justin M. Forbes)
- More filtering for Fedora (Justin M. Forbes)
- Fix Fedora module filtering for spi-altera-dfl (Justin M. Forbes)
- Fedora 5.13 config updates (Justin M. Forbes)
- fedora: cleanup TCG_TIS_I2C_CR50 (Peter Robinson)
- fedora: drop duplicate configs (Peter Robinson)
- More Fedora config updates for 5.13 (Justin M. Forbes)
- redhat/configs: Enable needed drivers for BlueField SoC on aarch64 (Alaa Hleihel) [1858592 1858594 1858596]
- redhat: Rename mod-blacklist.sh to mod-denylist.sh (Prarit Bhargava)
- redhat/configs: enable CONFIG_NET_ACT_MPLS (Marcelo Ricardo Leitner)
- configs: Enable CONFIG_DEBUG_KERNEL for zfcpdump (Jiri Olsa)
- kernel.spec: Add support to use vmlinux.h (Don Zickus)
- spec: Add vmlinux.h to kernel-devel package (Jiri Olsa)
- Turn off DRM_XEN_FRONTEND for Fedora as we had DRM_XEN off already (Justin M. Forbes)
- Fedora 5.13 config updates pt 3 (Justin M. Forbes)
- all: enable ath11k wireless modules (Peter Robinson)
- all: Enable WWAN and associated MHI bus pieces (Peter Robinson)
- spec: Enable sefltests rpm build (Jiri Olsa)
- spec: Allow bpf selftest/samples to fail (Jiri Olsa)
- bpf, selftests: Disable tests that need clang13 (Toke Høiland-Jørgensen)
- kvm: Add kvm_stat.service file and kvm_stat logrotate config to the tools (Jiri Benc)
- kernel.spec: Add missing source files to kernel-selftests-internal (Jiri Benc)
- kernel.spec: selftests: add net/forwarding to TARGETS list (Jiri Benc)
- kernel.spec: selftests: add build requirement on libmnl-devel (Jiri Benc)
- kernel.spec: add action.o to kernel-selftests-internal (Jiri Benc)
- kernel.spec: avoid building bpftool repeatedly (Jiri Benc)
- kernel.spec: selftests require python3 (Jiri Benc)
- kernel.spec: skip selftests that failed to build (Jiri Benc)
- kernel.spec: fix installation of bpf selftests (Jiri Benc)
- redhat: fix samples and selftests make options (Jiri Benc)
- kernel.spec: enable mptcp selftests for kernel-selftests-internal (Jiri Benc)
- kernel.spec: Do not export shared objects from libexecdir to RPM Provides (Jiri Benc)
- kernel.spec: add missing dependency for the which package (Jiri Benc)
- kernel.spec: add netfilter selftests to kernel-selftests-internal (Jiri Benc)
- kernel.spec: move slabinfo and page_owner_sort debuginfo to tools-debuginfo (Jiri Benc)
- kernel.spec: package and ship VM tools (Jiri Benc)
- configs: enable CONFIG_PAGE_OWNER (Jiri Benc)
- kernel.spec: add coreutils (Jiri Benc)
- kernel.spec: add netdevsim driver selftests to kernel-selftests-internal (Jiri Benc)
- redhat/Makefile: Clean out the --without flags from the baseonly rule (Jiri Benc)
- kernel.spec: Stop building unnecessary rpms for baseonly builds (Jiri Benc)
- kernel.spec: disable more kabi switches for gcov build (Jiri Benc)
- kernel.spec: Rename kabi-dw base (Jiri Benc)
- kernel.spec: Fix error messages during build of zfcpdump kernel (Jiri Benc)
- kernel.spec: perf: remove bpf examples (Jiri Benc)
- kernel.spec: selftests should not depend on modules-internal (Jiri Benc)
- kernel.spec: build samples (Jiri Benc)
- kernel.spec: tools: sync missing options with RHEL 8 (Jiri Benc)
- redhat/configs: nftables: Enable extra flowtable symbols (Phil Sutter)
- redhat/configs: Sync netfilter options with RHEL8 (Phil Sutter)
- Fedora 5.13 config updates pt 2 (Justin M. Forbes)
- Move CONFIG_ARCH_INTEL_SOCFPGA up a level for Fedora (Justin M. Forbes)
- fedora: enable the Rockchip rk3399 pcie drivers (Peter Robinson)
- Fedora 5.13 config updates pt 1 (Justin M. Forbes)
- Fix version requirement from opencsd-devel buildreq (Justin M. Forbes)
- configs/ark/s390: set CONFIG_MARCH_Z14 and CONFIG_TUNE_Z15 (Philipp Rudo) [1876435]
- configs/common/s390: Clean up CONFIG_{MARCH,TUNE}_Z* (Philipp Rudo)
- configs/process_configs.sh: make use of dummy-tools (Philipp Rudo)
- configs/common: disable CONFIG_INIT_STACK_ALL_{PATTERN,ZERO} (Philipp Rudo)
- configs/common/aarch64: disable CONFIG_RELR (Philipp Rudo)
- redhat/config: enable STMICRO nic for RHEL (Mark Salter)
- redhat/configs: Enable ARCH_TEGRA on RHEL (Mark Salter)
- redhat/configs: enable IMA_KEXEC for supported arches (Bruno Meneguele)
- redhat/configs: enable INTEGRITY_SIGNATURE to all arches (Bruno Meneguele)
- configs: enable CONFIG_LEDS_BRIGHTNESS_HW_CHANGED (Benjamin Tissoires)
- RHEL: disable io_uring support (Jeff Moyer)
- all: Changing CONFIG_UV_SYSFS to build uv_sysfs.ko as a loadable module. (Frank Ramsay)
- Enable NITRO_ENCLAVES on RHEL (Vitaly Kuznetsov)
- Update the Quick Start documentation (David Ward)
- redhat/configs: Set PVPANIC_MMIO for x86 and PVPANIC_PCI for aarch64 (Eric Auger) [1961178]
- Enable CONFIG_BPF_UNPRIV_DEFAULT_OFF (Jiri Olsa)
- configs/common/s390: disable CONFIG_QETH_{OSN,OSX} (Philipp Rudo) [1903201]
- team: mark team driver as deprecated (Hangbin Liu) [1945477]
- Make CRYPTO_EC also builtin (Simo Sorce) [1947240]
- Do not hard-code a default value for DIST (David Ward)
- Override %%{debugbuildsenabled} if the --with-release option is used (David Ward)
- Improve comments in SPEC file, and move some option tests and macros (David Ward)
- configs: enable CONFIG_EXFAT_FS (Pavel Reichl) [1943423]
- Revert s390x/zfcpdump part of a9d179c40281 and ecbfddd98621 (Vladis Dronov)
- Embed crypto algos, modes and templates needed in the FIPS mode (Vladis Dronov) [1947240]
- configs: Add and enable CONFIG_HYPERV_TESTING for debug kernels (Mohammed Gamal)
- mm/cma: mark CMA on x86_64 tech preview and print RHEL-specific infos (David Hildenbrand) [1945002]
- configs: enable CONFIG_CMA on x86_64 in ARK (David Hildenbrand) [1945002]
- rpmspec: build debug-* meta-packages if debug builds are disabled (Herton R. Krzesinski)
- UIO: disable unused config options (Aristeu Rozanski) [1957819]
- ARK-config: Make amd_pinctrl module builtin (Hans de Goede)
- rpmspec: revert/drop content hash for kernel-headers (Herton R. Krzesinski)
- rpmspec: fix check that calls InitBuildVars (Herton R. Krzesinski)
- fedora: enable zonefs (Damien Le Moal)
- redhat: load specific ARCH keys to INTEGRITY_PLATFORM_KEYRING (Bruno Meneguele)
- redhat: enable INTEGRITY_TRUSTED_KEYRING across all variants (Bruno Meneguele)
- redhat: enable SYSTEM_BLACKLIST_KEYRING across all variants (Bruno Meneguele)
- redhat: enable INTEGRITY_ASYMMETRIC_KEYS across all variants (Bruno Meneguele)
- Remove unused boot loader specification files (David Ward)
- redhat/configs: Enable mlx5 IPsec and TLS offloads (Alaa Hleihel) [1869674 1957636]
- Force DWARF4 because crash does not support DWARF5 yet (Justin M. Forbes)
- common: disable Apple Silicon generally (Peter Robinson)
- cleanup Intel's FPGA configs (Peter Robinson)
- common: move PTP KVM support from ark to common (Peter Robinson)
- Enable CONFIG_DRM_AMDGPU_USERPTR for everyone (Justin M. Forbes)
- redhat: add initial rpminspect configuration (Herton R. Krzesinski)
- fedora: arm updates for 5.13 (Peter Robinson)
- fedora: Enable WWAN and associated MHI bits (Peter Robinson)
- Update CONFIG_MODPROBE_PATH to /usr/sbin (Justin Forbes)
- Fedora set modprobe path (Justin M. Forbes)
- Keep sctp and l2tp modules in modules-extra (Don Zickus)
- Fix ppc64le cross build packaging (Don Zickus)
- Fedora: Make amd_pinctrl module builtin (Hans de Goede)
- Keep CONFIG_KASAN_HW_TAGS off for aarch64 debug configs (Justin M. Forbes)
- New configs in drivers/bus (Fedora Kernel Team)
- RHEL: Don't build KVM PR module on ppc64 (David Gibson) [1930649]
- Flip CONFIG_USB_ROLE_SWITCH from m to y (Justin M. Forbes)
- Set valid options for CONFIG_FW_LOADER_USER_HELPER (Justin M. Forbes)
- Clean up CONFIG_FB_MODE_HELPERS (Justin M. Forbes)
- Turn off CONFIG_VFIO for the s390x zfcpdump kernel (Justin M. Forbes)
- Delete unused CONFIG_SND_SOC_MAX98390 pending-common (Justin M. Forbes)
- Update pending-common configs, preparing to set correctly (Justin M. Forbes)
- Update fedora filters for surface (Justin M. Forbes)
- Build CONFIG_CRYPTO_ECDSA inline for s390x zfcpdump (Justin M. Forbes)
- Replace "flavour" where "variant" is meant instead (David Ward)
- Drop the %%{variant} macro and fix --with-vanilla (David Ward)
- Fix syntax of %%kernel_variant_files (David Ward)
- Change description of --without-vdso-install to fix typo (David Ward)
- Config updates to work around mismatches (Justin M. Forbes)
- CONFIG_SND_SOC_FSL_ASOC_CARD selects CONFIG_MFD_WM8994 now (Justin M. Forbes)
- wireguard: disable in FIPS mode (Hangbin Liu) [1940794]
- Enable mtdram for fedora (rhbz 1955916) (Justin M. Forbes)
- Remove reference to bpf-helpers man page (Justin M. Forbes)
- Fedora: enable more modules for surface devices (Dave Olsthoorn)
- Fix Fedora config mismatch for CONFIG_FSL_ENETC_IERB (Justin M. Forbes)
- hardlink is in /usr/bin/ now (Justin M. Forbes)
- Ensure CONFIG_KVM_BOOK3S_64_PR stays on in Fedora, even if it is turned off in RHEL (Justin M. Forbes)
- Set date in package release from repository commit, not system clock (David Ward)
- Use a better upstream tarball filename for snapshots (David Ward)
- Don't create empty pending-common files on pending-fedora commits (Don Zickus)
- Add redhat/configs/pending-common/generic/s390x/zfcpdump/CONFIG_NETFS_SUPPORT (Justin M. Forbes)
- Create ark-latest branch last for CI scripts (Don Zickus)
- Replace /usr/libexec/platform-python with /usr/bin/python3 (David Ward)
- Turn off ADI_AXI_ADC and AD9467 which now require CONFIG_OF (Justin M. Forbes)
- Export ark infrastructure files (Don Zickus)
- docs: Update docs to reflect newer workflow. (Don Zickus)
- Use upstream/master for merge-base with fallback to master (Don Zickus)
- Fedora: Turn off the SND_INTEL_BYT_PREFER_SOF option (Hans de Goede)
- filter-modules.sh.fedora: clean up "netprots" (Paul Bolle)
- filter-modules.sh.fedora: clean up "scsidrvs" (Paul Bolle)
- filter-*.sh.fedora: clean up "ethdrvs" (Paul Bolle)
- filter-*.sh.fedora: clean up "driverdirs" (Paul Bolle)
- filter-*.sh.fedora: remove incorrect entries (Paul Bolle)
- filter-*.sh.fedora: clean up "singlemods" (Paul Bolle)
- filter-modules.sh.fedora: drop unused list "iiodrvs" (Paul Bolle)
- Update mod-internal to fix depmod issue (Nico Pache)
- Turn on CONFIG_VDPA_SIM_NET (rhbz 1942343) (Justin M. Forbes)
- New configs in drivers/power (Fedora Kernel Team)
- Turn on CONFIG_NOUVEAU_DEBUG_PUSH for debug configs (Justin M. Forbes)
- Turn off KFENCE sampling by default for Fedora (Justin M. Forbes)
- Fedora config updates round 2 (Justin M. Forbes)
- New configs in drivers/soc (Jeremy Cline)
- filter-modules.sh: Fix copy/paste error 'input' (Paul Bolle)
- Update module filtering for 5.12 kernels (Justin M. Forbes)
- Fix genlog.py to ensure that comments retain "%%" characters. (Mark Mielke)
- New configs in drivers/leds (Fedora Kernel Team)
- Limit CONFIG_USB_CDNS_SUPPORT to x86_64 and arm in Fedora (David Ward)
- Fedora: Enable CHARGER_GPIO on aarch64 too (Peter Robinson)
- Fedora config updates (Justin M. Forbes)
- configs: enable CONFIG_WIREGUARD in ARK (Hangbin Liu) [1613522]
- Remove duplicate configs acroos fedora, ark and common (Don Zickus)
- Combine duplicate configs across ark and fedora into common (Don Zickus)
- common/ark: cleanup and unify the parport configs (Peter Robinson)
- iommu/vt-d: enable INTEL_IDXD_SVM for both fedora and rhel (Jerry Snitselaar)
- REDHAT: coresight: etm4x: Disable coresight on HPE Apollo 70 (Jeremy Linton)
- configs/common/generic: disable CONFIG_SLAB_MERGE_DEFAULT (Rafael Aquini)
- Remove _legacy_common_support (Justin M. Forbes)
- redhat/mod-blacklist.sh: Fix floppy blacklisting (Hans de Goede)
- New configs in fs/pstore (CKI@GitLab)
- New configs in arch/powerpc (Fedora Kernel Team)
- configs: enable BPF LSM on Fedora and ARK (Ondrej Mosnacek)
- configs: clean up LSM configs (Ondrej Mosnacek)
- New configs in drivers/platform (CKI@GitLab)
- New configs in drivers/firmware (CKI@GitLab)
- New configs in drivers/mailbox (Fedora Kernel Team)
- New configs in drivers/net/phy (Justin M. Forbes)
- Update CONFIG_DM_MULTIPATH_IOA (Augusto Caringi)
- New configs in mm/Kconfig (CKI@GitLab)
- New configs in arch/powerpc (Jeremy Cline)
- New configs in arch/powerpc (Jeremy Cline)
- New configs in drivers/input (Fedora Kernel Team)
- New configs in net/bluetooth (Justin M. Forbes)
- New configs in drivers/clk (Fedora Kernel Team)
- New configs in init/Kconfig (Jeremy Cline)
- redhat: allow running fedora-configs and rh-configs targets outside of redhat/ (Herton R. Krzesinski)
- all: unify the disable of goldfish (android emulation platform) (Peter Robinson)
- common: minor cleanup/de-dupe of dma/dmabuf debug configs (Peter Robinson)
- common/ark: these drivers/arches were removed in 5.12 (Peter Robinson)
- Correct kernel-devel make prepare build for 5.12. (Paulo E. Castro)
- redhat: add initial support for centos stream dist-git sync on Makefiles (Herton R. Krzesinski)
- redhat/configs: Enable CONFIG_SCHED_STACK_END_CHECK for Fedora and ARK (Josh Poimboeuf) [1856174]
- CONFIG_VFIO now selects IOMMU_API instead of depending on it, causing several config mismatches for the zfcpdump kernel (Justin M. Forbes)
- Turn off weak-modules for Fedora (Justin M. Forbes)
- redhat: enable CONFIG_FW_LOADER_COMPRESS for ARK (Herton R. Krzesinski) [1939095]
- Fedora: filters: update to move dfl-emif to modules (Peter Robinson)
- drop duplicate DEVFREQ_GOV_SIMPLE_ONDEMAND config (Peter Robinson)
- efi: The EFI_VARS is legacy and now x86 only (Peter Robinson)
- common: enable RTC_SYSTOHC to supplement update_persistent_clock64 (Peter Robinson)
- generic: arm: enable SCMI for all options (Peter Robinson)
- fedora: the PCH_CAN driver is x86-32 only (Peter Robinson)
- common: disable legacy CAN device support (Peter Robinson)
- common: Enable Microchip MCP251x/MCP251xFD CAN controllers (Peter Robinson)
- common: Bosch MCAN support for Intel Elkhart Lake (Peter Robinson)
- common: enable CAN_PEAK_PCIEFD PCI-E driver (Peter Robinson)
- common: disable CAN_PEAK_PCIEC PCAN-ExpressCard (Peter Robinson)
- common: enable common CAN layer 2 protocols (Peter Robinson)
- ark: disable CAN_LEDS option (Peter Robinson)
- Fedora: Turn on SND_SOC_INTEL_SKYLAKE_HDAUDIO_CODEC option (Hans de Goede)
- Fedora: enable modules for surface devices (Dave Olsthoorn)
- Turn on SND_SOC_INTEL_SOUNDWIRE_SOF_MACH for Fedora again (Justin M. Forbes)
- common: fix WM8804 codec dependencies (Peter Robinson)
- Build SERIO_SERPORT as a module (Peter Robinson)
- input: touchscreen: move ELO and Wacom serial touchscreens to x86 (Peter Robinson)
- Sync serio touchscreens for non x86 architectures to the same as ARK (Peter Robinson)
- Only enable SERIO_LIBPS2 on x86 (Peter Robinson)
- Only enable PC keyboard controller and associated keyboard on x86 (Peter Robinson)
- Generic: Mouse: Tweak generic serial mouse options (Peter Robinson)
- Only enable PS2 Mouse options on x86 (Peter Robinson)
- Disable bluetooth highspeed by default (Peter Robinson)
- Fedora: A few more general updates for 5.12 window (Peter Robinson)
- Fedora: Updates for 5.12 merge window (Peter Robinson)
- Fedora: remove dead options that were removed upstream (Peter Robinson)
- redhat: remove CONFIG_DRM_PANEL_XINGBANGDA_XBD599 (Herton R. Krzesinski)
- New configs in arch/powerpc (Fedora Kernel Team)
- Turn on CONFIG_PPC_QUEUED_SPINLOCKS as it is default upstream now (Justin M. Forbes)
- Update pending-common configs to address new upstream config deps (Justin M. Forbes)
- rpmspec: ship gpio-watch.debug in the proper debuginfo package (Herton R. Krzesinski)
- Removed description text as a comment confuses the config generation (Justin M. Forbes)
- New configs in drivers/dma-buf (Jeremy Cline)
- Fedora: ARMv7: build for 16 CPUs. (Peter Robinson)
- Fedora: only enable DEBUG_HIGHMEM on debug kernels (Peter Robinson)
- process_configs.sh: fix find/xargs data flow (Ondrej Mosnacek)
- Fedora config update (Justin M. Forbes)
- fedora: minor arm sound config updates (Peter Robinson)
- Fix trailing white space in redhat/configs/fedora/generic/CONFIG_SND_INTEL_BYT_PREFER_SOF (Justin M. Forbes)
- Add a redhat/rebase-notes.txt file (Hans de Goede)
- Turn on SND_INTEL_BYT_PREFER_SOF for Fedora (Hans de Goede)
- CI: Drop MR ID from the name variable (Veronika Kabatova)
- redhat: add DUP and kpatch certificates to system trusted keys for RHEL build (Herton R. Krzesinski)
- The comments in CONFIG_USB_RTL8153_ECM actually turn off CONFIG_USB_RTL8152 (Justin M. Forbes)
- Update CKI pipeline project (Veronika Kabatova)
- Turn off additional KASAN options for Fedora (Justin M. Forbes)
- Rename the master branch to rawhide for Fedora (Justin M. Forbes)
- Makefile targets for packit integration (Ben Crocker)
- Turn off KASAN for rawhide debug builds (Justin M. Forbes)
- New configs in arch/arm64 (Justin Forbes)
- Remove deprecated Intel MIC config options (Peter Robinson)
- redhat: replace inline awk script with genlog.py call (Herton R. Krzesinski)
- redhat: add genlog.py script (Herton R. Krzesinski)
- kernel.spec.template - fix use_vdso usage (Ben Crocker)
- Turn off vdso_install for ppc (Justin M. Forbes)
- Remove bpf-helpers.7 from bpftool package (Jiri Olsa)
- New configs in lib/Kconfig.debug (Fedora Kernel Team)
- Turn off CONFIG_VIRTIO_CONSOLE for s390x zfcpdump (Justin M. Forbes)
- New configs in drivers/clk (Justin M. Forbes)
- Keep VIRTIO_CONSOLE on s390x available. (Jakub Čajka)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- Fedora 5.11 config updates part 4 (Justin M. Forbes)
- Fedora 5.11 config updates part 3 (Justin M. Forbes)
- Fedora 5.11 config updates part 2 (Justin M. Forbes)
- Update internal (test) module list from RHEL-8 (Joe Lawrence) [1915073]
- Fix USB_XHCI_PCI regression (Justin M. Forbes)
- fedora: fixes for ARMv7 build issue by disabling HIGHPTE (Peter Robinson)
- all: s390x: Increase CONFIG_PCI_NR_FUNCTIONS to 512 (#1888735) (Dan Horák)
- Fedora 5.11 configs pt 1 (Justin M. Forbes)
- redhat: avoid conflict with mod-blacklist.sh and released_kernel defined (Herton R. Krzesinski)
- redhat: handle certificate files conditionally as done for src.rpm (Herton R. Krzesinski)
- specfile: add %%{?_smp_mflags} to "make headers_install" in tools/testing/selftests (Denys Vlasenko)
- specfile: add %%{?_smp_mflags} to "make samples/bpf/" (Denys Vlasenko)
- Run MR testing in CKI pipeline (Veronika Kabatova)
- Reword comment (Nicolas Chauvet)
- Add with_cross_arm conditional (Nicolas Chauvet)
- Redefines __strip if with_cross (Nicolas Chauvet)
- fedora: only enable ACPI_CONFIGFS, ACPI_CUSTOM_METHOD in debug kernels (Peter Robinson)
- fedora: User the same EFI_CUSTOM_SSDT_OVERLAYS as ARK (Peter Robinson)
- all: all arches/kernels enable the same DMI options (Peter Robinson)
- all: move SENSORS_ACPI_POWER to common/generic (Peter Robinson)
- fedora: PCIE_HISI_ERR is already in common (Peter Robinson)
- all: all ACPI platforms enable ATA_ACPI so move it to common (Peter Robinson)
- all: x86: move shared x86 acpi config options to generic (Peter Robinson)
- All: x86: Move ACPI_VIDEO to common/x86 (Peter Robinson)
- All: x86: Enable ACPI_DPTF (Intel DPTF) (Peter Robinson)
- All: enable ACPI_BGRT for all ACPI platforms. (Peter Robinson)
- All: Only build ACPI_EC_DEBUGFS for debug kernels (Peter Robinson)
- All: Disable Intel Classmate PC ACPI_CMPC option (Peter Robinson)
- cleanup: ACPI_PROCFS_POWER was removed upstream (Peter Robinson)
- All: ACPI: De-dupe the ACPI options that are the same across ark/fedora on x86/arm (Peter Robinson)
- Enable the vkms module in Fedora (Jeremy Cline)
- Fedora: arm updates for 5.11 and general cross Fedora cleanups (Peter Robinson)
- Add gcc-c++ to BuildRequires (Justin M. Forbes)
- Update CONFIG_KASAN_HW_TAGS (Justin M. Forbes)
- fedora: arm: move generic power off/reset to all arm (Peter Robinson)
- fedora: ARMv7: build in DEVFREQ_GOV_SIMPLE_ONDEMAND until I work out why it's changed (Peter Robinson)
- fedora: cleanup joystick_adc (Peter Robinson)
- fedora: update some display options (Peter Robinson)
- fedora: arm: enable TI PRU options (Peter Robinson)
- fedora: arm: minor exynos plaform updates (Peter Robinson)
- arm: SoC: disable Toshiba Visconti SoC (Peter Robinson)
- common: disable ARCH_BCM4908 (NFC) (Peter Robinson)
- fedora: minor arm config updates (Peter Robinson)
- fedora: enable Tegra 234 SoC (Peter Robinson)
- fedora: arm: enable new Hikey 3xx options (Peter Robinson)
- Fedora: USB updates (Peter Robinson)
- fedora: enable the GNSS receiver subsystem (Peter Robinson)
- Remove POWER_AVS as no longer upstream (Peter Robinson)
- Cleanup RESET_RASPBERRYPI (Peter Robinson)
- Cleanup GPIO_CDEV_V1 options. (Peter Robinson)
- fedora: arm crypto updates (Peter Robinson)
- CONFIG_KASAN_HW_TAGS for aarch64 (Justin M. Forbes)
- Fedora: cleanup PCMCIA configs, move to x86 (Peter Robinson)
- New configs in drivers/rtc (Fedora Kernel Team)
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK_BYREF_ALL (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_GCC_PLUGINS on ARK (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_KASAN on Fedora (Josh Poimboeuf) [1856176]
- New configs in init/Kconfig (Fedora Kernel Team)
- build_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- genspec.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- mod-blacklist.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Enable Speakup accessibility driver (Justin M. Forbes)
- New configs in init/Kconfig (Fedora Kernel Team)
- Fix fedora config mismatch due to dep changes (Justin M. Forbes)
- New configs in drivers/crypto (Jeremy Cline)
- Remove duplicate ENERGY_MODEL configs (Peter Robinson)
- This is selected by PCIE_QCOM so must match (Justin M. Forbes)
- drop unused BACKLIGHT_GENERIC (Peter Robinson)
- Remove cp instruction already handled in instruction below. (Paulo E. Castro)
- Add all the dependencies gleaned from running `make prepare` on a bloated devel kernel. (Paulo E. Castro)
- Add tools to path mangling script. (Paulo E. Castro)
- Remove duplicate cp statement which is also not specific to x86. (Paulo E. Castro)
- Correct orc_types failure whilst running `make prepare` https://bugzilla.redhat.com/show_bug.cgi?id=1882854 (Paulo E. Castro)
- redhat: ark: enable CONFIG_IKHEADERS (Jiri Olsa)
- Add missing '$' sign to (GIT) in redhat/Makefile (Augusto Caringi)
- Remove filterdiff and use native git instead (Don Zickus)
- New configs in net/sched (Justin M. Forbes)
- New configs in drivers/mfd (CKI@GitLab)
- New configs in drivers/mfd (Fedora Kernel Team)
- New configs in drivers/firmware (Fedora Kernel Team)
- Temporarily backout parallel xz script (Justin M. Forbes)
- redhat: explicitly disable CONFIG_IMA_APPRAISE_SIGNED_INIT (Bruno Meneguele)
- redhat: enable CONFIG_EVM_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM_ATTR_FSUUID on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM in all arches and flavors (Bruno Meneguele)
- redhat: enable CONFIG_IMA_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: set CONFIG_IMA_DEFAULT_HASH to SHA256 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_SECURE_AND_OR_TRUSTED_BOOT (Bruno Meneguele)
- redhat: enable CONFIG_IMA_READ_POLICY on ARK (Bruno Meneguele)
- redhat: set default IMA template for all ARK arches (Bruno Meneguele)
- redhat: enable CONFIG_IMA_DEFAULT_HASH_SHA256 for all flavors (Bruno Meneguele)
- redhat: disable CONFIG_IMA_DEFAULT_HASH_SHA1 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_ARCH_POLICY for ppc and x86 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_MODSIG (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_BOOTPARAM (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE (Bruno Meneguele)
- redhat: enable CONFIG_INTEGRITY for aarch64 (Bruno Meneguele)
- kernel: Update some missing KASAN/KCSAN options (Jeremy Linton)
- kernel: Enable coresight on aarch64 (Jeremy Linton)
- Update CONFIG_INET6_ESPINTCP (Justin Forbes)
- New configs in net/ipv6 (Justin M. Forbes)
- fedora: move CONFIG_RTC_NVMEM options from ark to common (Peter Robinson)
- configs: Enable CONFIG_DEBUG_INFO_BTF (Don Zickus)
- fedora: some minor arm audio config tweaks (Peter Robinson)
- Ship xpad with default modules on Fedora and RHEL (Bastien Nocera)
- Fedora: Only enable legacy serial/game port joysticks on x86 (Peter Robinson)
- Fedora: Enable the options required for the Librem 5 Phone (Peter Robinson)
- Fedora config update (Justin M. Forbes)
- Fedora config change because CONFIG_FSL_DPAA2_ETH now selects CONFIG_FSL_XGMAC_MDIO (Justin M. Forbes)
- redhat: generic  enable CONFIG_INET_MPTCP_DIAG (Davide Caratti)
- Fedora config update (Justin M. Forbes)
- Enable NANDSIM for Fedora (Justin M. Forbes)
- Re-enable CONFIG_ACPI_TABLE_UPGRADE for Fedora since upstream disables this if secureboot is active (Justin M. Forbes)
- Ath11k related config updates (Justin M. Forbes)
- Fedora config updates for ath11k (Justin M. Forbes)
- Turn on ATH11K for Fedora (Justin M. Forbes)
- redhat: enable CONFIG_INTEL_IOMMU_SVM (Jerry Snitselaar)
- More Fedora config fixes (Justin M. Forbes)
- Fedora 5.10 config updates (Justin M. Forbes)
- Fedora 5.10 configs round 1 (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Allow kernel-tools to build without selftests (Don Zickus)
- Allow building of kernel-tools standalone (Don Zickus)
- redhat: ark: disable CONFIG_NET_ACT_CTINFO (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_TEQL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_SFB (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_QFQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PLUG (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PIE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_HHF (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DSMARK (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DRR (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CODEL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CHOKE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CBQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_ATM (Davide Caratti)
- redhat: ark: disable CONFIG_NET_EMATCH and sub-targets (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_TCINDEX (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP6 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_ROUTE4 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_BASIC (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SKBMOD (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SIMP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_NAT (Davide Caratti)
- arm64/defconfig: Enable CONFIG_KEXEC_FILE (Bhupesh Sharma) [1821565]
- redhat/configs: Cleanup CONFIG_CRYPTO_SHA512 (Prarit Bhargava)
- New configs in drivers/mfd (Fedora Kernel Team)
- Fix LTO issues with kernel-tools (Don Zickus)
- Point pathfix to the new location for gen_compile_commands.py (Justin M. Forbes)
- configs: Disable CONFIG_SECURITY_SELINUX_DISABLE (Ondrej Mosnacek)
- [Automatic] Handle config dependency changes (Don Zickus)
- configs/iommu: Add config comment to empty CONFIG_SUN50I_IOMMU file (Jerry Snitselaar)
- New configs in kernel/trace (Fedora Kernel Team)
- Fix Fedora config locations (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- configs: enable CONFIG_CRYPTO_CTS=y so cts(cbc(aes)) is available in FIPS mode (Vladis Dronov) [1855161]
- Partial revert: Add master merge check (Don Zickus)
- Update Maintainers doc to reflect workflow changes (Don Zickus)
- WIP: redhat/docs: Update documentation for single branch workflow (Prarit Bhargava)
- Add CONFIG_ARM64_MTE which is not picked up by the config scripts for some reason (Justin M. Forbes)
- Disable Speakup synth DECEXT (Justin M. Forbes)
- Enable Speakup for Fedora since it is out of staging (Justin M. Forbes)
- Modify patchlist changelog output (Don Zickus)
- process_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- generate_all_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- redhat/self-test: Initial commit (Ben Crocker)
- KEYS: Make use of platform keyring for module signature verify (Robert Holmes)
- Input: rmi4 - remove the need for artificial IRQ in case of HID (Benjamin Tissoires)
- ARM: tegra: usb no reset (Peter Robinson)
- arm: make CONFIG_HIGHPTE optional without CONFIG_EXPERT (Jon Masters)
- Add option of 13 for FORCE_MAX_ZONEORDER (Peter Robinson)
- s390: Lock down the kernel when the IPL secure flag is set (Jeremy Cline)
- efi: Lock down the kernel if booted in secure boot mode (David Howells)
- efi: Add an EFI_SECURE_BOOT flag to indicate secure boot mode (David Howells)
- security: lockdown: expose a hook to lock the kernel down (Jeremy Cline)
- Make get_cert_list() use efi_status_to_str() to print error messages. (Peter Jones)
- Add efi_status_to_str() and rework efi_status_to_err(). (Peter Jones)
- arm: aarch64: Drop the EXPERT setting from ARM64_FORCE_52BIT (Jeremy Cline)
- iommu/arm-smmu: workaround DMA mode issues (Laura Abbott)
- ipmi: do not configure ipmi for HPE m400 (Laura Abbott) [1670017]
- ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter)
- Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter)
- acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- Stop merging ark-patches for release (Don Zickus)
- Fix path location for ark-update-configs.sh (Don Zickus)
- Combine Red Hat patches into single patch (Don Zickus)
- New configs in drivers/misc (Jeremy Cline)
- New configs in drivers/net/wireless (Justin M. Forbes)
- New configs in drivers/phy (Fedora Kernel Team)
- New configs in drivers/tty (Fedora Kernel Team)
- Set SquashFS decompression options for all flavors to match RHEL (Bohdan Khomutskyi)
- configs: Enable CONFIG_ENERGY_MODEL (Phil Auld)
- New configs in drivers/pinctrl (Fedora Kernel Team)
- Update CONFIG_THERMAL_NETLINK (Justin Forbes)
- Separate merge-upstream and release stages (Don Zickus)
- Re-enable CONFIG_IR_SERIAL on Fedora (Prarit Bhargava)
- Create Patchlist.changelog file (Don Zickus)
- Filter out upstream commits from changelog (Don Zickus)
- Merge Upstream script fixes (Don Zickus)
- kernel.spec: Remove kernel-keys directory on rpm erase (Prarit Bhargava)
- Add mlx5_vdpa to module filter for Fedora (Justin M. Forbes)
- Add python3-sphinx_rtd_theme buildreq for docs (Justin M. Forbes)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- dist-merge-upstream: Checkout known branch for ci scripts (Don Zickus)
- kernel.spec: don't override upstream compiler flags for ppc64le (Dan Horák)
- Fedora config updates (Justin M. Forbes)
- Fedora confi gupdate (Justin M. Forbes)
- mod-sign.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Swap how ark-latest is built (Don Zickus)
- Add extra version bump to os-build branch (Don Zickus)
- dist-release: Avoid needless version bump. (Don Zickus)
- Add dist-fedora-release target (Don Zickus)
- Remove redundant code in dist-release (Don Zickus)
- Makefile.common rename TAG to _TAG (Don Zickus)
- Fedora config change (Justin M. Forbes)
- Fedora filter update (Justin M. Forbes)
- Config update for Fedora (Justin M. Forbes)
- enable PROTECTED_VIRTUALIZATION_GUEST for all s390x kernels (Dan Horák)
- redhat: ark: enable CONFIG_NET_SCH_TAPRIO (Davide Caratti)
- redhat: ark: enable CONFIG_NET_SCH_ETF (Davide Caratti)
- More Fedora config updates (Justin M. Forbes)
- New config deps (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- First half of config updates for Fedora (Justin M. Forbes)
- Updates for Fedora arm architectures for the 5.9 window (Peter Robinson)
- Merge 5.9 config changes from Peter Robinson (Justin M. Forbes)
- Add config options that only show up when we prep on arm (Justin M. Forbes)
- Config updates for Fedora (Justin M. Forbes)
- fedora: enable enery model (Peter Robinson)
- Use the configs/generic config for SND_HDA_INTEL everywhere (Peter Robinson)
- Enable ZSTD compression algorithm on all kernels (Peter Robinson)
- Enable ARM_SMCCC_SOC_ID on all aarch64 kernels (Peter Robinson)
- iio: enable LTR-559 light and proximity sensor (Peter Robinson)
- iio: chemical: enable some popular chemical and partical sensors (Peter Robinson)
- More mismatches (Justin M. Forbes)
- Fedora config change due to deps (Justin M. Forbes)
- CONFIG_SND_SOC_MAX98390 is now selected by SND_SOC_INTEL_DA7219_MAX98357A_GENERIC (Justin M. Forbes)
- Config change required for build part 2 (Justin M. Forbes)
- Config change required for build (Justin M. Forbes)
- Fedora config update (Justin M. Forbes)
- Add ability to sync upstream through Makefile (Don Zickus)
- Add master merge check (Don Zickus)
- Replace hardcoded values 'os-build' and project id with variables (Don Zickus)
- redhat/Makefile.common: Fix MARKER (Prarit Bhargava)
- gitattributes: Remove unnecesary export restrictions (Prarit Bhargava)
- Add new certs for dual signing with boothole (Justin M. Forbes)
- Update secureboot signing for dual keys (Justin M. Forbes)
- fedora: enable LEDS_SGM3140 for arm configs (Peter Robinson)
- Enable CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG (Justin M. Forbes)
- redhat/configs: Fix common CONFIGs (Prarit Bhargava)
- redhat/configs: General CONFIG cleanups (Prarit Bhargava)
- redhat/configs: Update & generalize evaluate_configs (Prarit Bhargava)
- fedora: arm: Update some meson config options (Peter Robinson)
- redhat/docs: Add Fedora RPM tagging date (Prarit Bhargava)
- Update config for renamed panel driver. (Peter Robinson)
- Enable SERIAL_SC16IS7XX for SPI interfaces (Peter Robinson)
- s390x-zfcpdump: Handle missing Module.symvers file (Don Zickus)
- Fedora config updates (Justin M. Forbes)
- redhat/configs: Add .tmp files to .gitignore (Prarit Bhargava)
- disable uncommon TCP congestion control algorithms (Davide Caratti)
- Add new bpf man pages (Justin M. Forbes)
- Add default option for CONFIG_ARM64_BTI_KERNEL to pending-common so that eln kernels build (Justin M. Forbes)
- redhat/Makefile: Add fedora-configs and rh-configs make targets (Prarit Bhargava)
- redhat/configs: Use SHA512 for module signing (Prarit Bhargava)
- genspec.sh: 'touch' empty Patchlist file for single tarball (Don Zickus)
- Fedora config update for rc1 (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- redhat/Makefile.common: fix RPMKSUBLEVEL condition (Ondrej Mosnacek)
- redhat/Makefile: silence KABI tar output (Ondrej Mosnacek)
- One more Fedora config update (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix PATCHLEVEL for merge window (Justin M. Forbes)
- Change ark CONFIG_COMMON_CLK to yes, it is selected already by other options (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- More module filtering for Fedora (Justin M. Forbes)
- Update filters for rnbd in Fedora (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix up module filtering for 5.8 (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- More Fedora config work (Justin M. Forbes)
- RTW88BE and CE have been extracted to their own modules (Justin M. Forbes)
- Set CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK for Fedora (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Arm64 Use Branch Target Identification for kernel (Justin M. Forbes)
- Change value of CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix configs for Fedora (Justin M. Forbes)
- Add zero-commit to format-patch options (Justin M. Forbes)
- Copy Makefile.rhelver as a source file rather than a patch (Jeremy Cline)
- Move the sed to clear the patch templating outside of conditionals (Justin M. Forbes)
- Match template format in kernel.spec.template (Justin M. Forbes)
- Break out the Patches into individual files for dist-git (Justin M. Forbes)
- Break the Red Hat patch into individual commits (Jeremy Cline)
- Fix update_scripts.sh unselective pattern sub (David Howells)
- Add cec to the filter overrides (Justin M. Forbes)
- Add overrides to filter-modules.sh (Justin M. Forbes)
- redhat/configs: Enable CONFIG_SMC91X and disable CONFIG_SMC911X (Prarit Bhargava) [1722136]
- Include bpftool-struct_ops man page in the bpftool package (Jeremy Cline)
- Add sharedbuffer_configuration.py to the pathfix.py script (Jeremy Cline)
- Use __make macro instead of make (Tom Stellard)
- Sign off generated configuration patches (Jeremy Cline)
- Drop the static path configuration for the Sphinx docs (Jeremy Cline)
- redhat: Add dummy-module kernel module (Prarit Bhargava)
- redhat: enable CONFIG_LWTUNNEL_BPF (Jiri Benc)
- Remove typoed config file aarch64CONFIG_SM_GCC_8150 (Justin M. Forbes)
- Add Documentation back to kernel-devel as it has Kconfig now (Justin M. Forbes)
- Copy distro files rather than moving them (Jeremy Cline)
- kernel.spec: fix 'make scripts' for kernel-devel package (Brian Masney)
- Makefile: correct help text for dist-cross-<arch>-rpms (Brian Masney)
- redhat/Makefile: Fix RHEL8 python warning (Prarit Bhargava)
- redhat: Change Makefile target names to dist- (Prarit Bhargava)
- configs: Disable Serial IR driver (Prarit Bhargava)
- Fix "multiple %%files for package kernel-tools" (Pablo Greco)
- Introduce a Sphinx documentation project (Jeremy Cline)
- Build ARK against ELN (Don Zickus)
- Drop the requirement to have a remote called linus (Jeremy Cline)
- Rename 'internal' branch to 'os-build' (Don Zickus)
- Only include open merge requests with "Include in Releases" label (Jeremy Cline)
- Package gpio-watch in kernel-tools (Jeremy Cline)
- Exit non-zero if the tag already exists for a release (Jeremy Cline)
- Adjust the changelog update script to not push anything (Jeremy Cline)
- Drop --target noarch from the rh-rpms make target (Jeremy Cline)
- Add a script to generate release tags and branches (Jeremy Cline)
- Set CONFIG_VDPA for fedora (Justin M. Forbes)
- Add a README to the dist-git repository (Jeremy Cline)
- Provide defaults in ark-rebase-patches.sh (Jeremy Cline)
- Default ark-rebase-patches.sh to not report issues (Jeremy Cline)
- Drop DIST from release commits and tags (Jeremy Cline)
- Place the buildid before the dist in the release (Jeremy Cline)
- Sync up with Fedora arm configuration prior to merging (Jeremy Cline)
- Disable CONFIG_PROTECTED_VIRTUALIZATION_GUEST for zfcpdump (Jeremy Cline)
- Add RHMAINTAINERS file and supporting conf (Don Zickus)
- Add a script to test if all commits are signed off (Jeremy Cline)
- Fix make rh-configs-arch (Don Zickus)
- Sync up Fedora configs from the first week of the merge window (Jeremy Cline)
- Migrate blacklisting floppy.ko to mod-blacklist.sh (Don Zickus)
- kernel packaging: Combine mod-blacklist.sh and mod-extra-blacklist.sh (Don Zickus)
- kernel packaging: Fix extra namespace collision (Don Zickus)
- mod-extra.sh: Rename to mod-blacklist.sh (Don Zickus)
- mod-extra.sh: Make file generic (Don Zickus)
- Fix a painfully obvious YAML syntax error in .gitlab-ci.yml (Jeremy Cline)
- Add in armv7hl kernel header support (Don Zickus)
- Disable all BuildKernel commands when only building headers (Don Zickus)
- Drop any gitlab-ci patches from ark-patches (Jeremy Cline)
- Build the srpm for internal branch CI using the vanilla tree (Jeremy Cline)
- Pull in the latest ARM configurations for Fedora (Jeremy Cline)
- Fix xz memory usage issue (Neil Horman)
- Use ark-latest instead of master for update script (Jeremy Cline)
- Move the CI jobs back into the ARK repository (Jeremy Cline)
- Sync up ARK's Fedora config with the dist-git repository (Jeremy Cline)
- Pull in the latest configuration changes from Fedora (Jeremy Cline)
- configs: enable CONFIG_NET_SCH_CBS (Marcelo Ricardo Leitner)
- Drop configuration options in fedora/ that no longer exist (Jeremy Cline)
- Set RH_FEDORA for ARK and Fedora (Jeremy Cline)
- redhat/kernel.spec: Include the release in the kernel COPYING file (Jeremy Cline)
- redhat/kernel.spec: add scripts/jobserver-exec to py3_shbang_opts list (Jeremy Cline)
- redhat/kernel.spec: package bpftool-gen man page (Jeremy Cline)
- distgit-changelog: handle multiple y-stream BZ numbers (Bruno Meneguele)
- redhat/kernel.spec: remove all inline comments (Bruno Meneguele)
- redhat/genspec: awk unknown whitespace regex pattern (Bruno Meneguele)
- Improve the readability of gen_config_patches.sh (Jeremy Cline)
- Fix some awkward edge cases in gen_config_patches.sh (Jeremy Cline)
- Update the CI environment to use Fedora 31 (Jeremy Cline)
- redhat: drop whitespace from with_gcov macro (Jan Stancek)
- configs: Enable CONFIG_KEY_DH_OPERATIONS on ARK (Ondrej Mosnacek)
- configs: Adjust CONFIG_MPLS_ROUTING and CONFIG_MPLS_IPTUNNEL (Laura Abbott)
- New configs in lib/crypto (Jeremy Cline)
- New configs in drivers/char (Jeremy Cline)
- Turn on BLAKE2B for Fedora (Jeremy Cline)
- kernel.spec.template: Clean up stray *.h.s files (Laura Abbott)
- Build the SRPM in the CI job (Jeremy Cline)
- New configs in net/tls (Jeremy Cline)
- New configs in net/tipc (Jeremy Cline)
- New configs in lib/kunit (Jeremy Cline)
- Fix up released_kernel case (Laura Abbott)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- New configs in drivers/ptp (Jeremy Cline)
- New configs in drivers/nvme (Jeremy Cline)
- New configs in drivers/net/phy (Jeremy Cline)
- New configs in arch/arm64 (Jeremy Cline)
- New configs in drivers/crypto (Jeremy Cline)
- New configs in crypto/Kconfig (Jeremy Cline)
- Add label so the Gitlab to email bridge ignores the changelog (Jeremy Cline)
- Temporarily switch TUNE_DEFAULT to y (Jeremy Cline)
- Run config test for merge requests and internal (Jeremy Cline)
- Add missing licensedir line (Laura Abbott)
- redhat/scripts: Remove redhat/scripts/rh_get_maintainer.pl (Prarit Bhargava)
- configs: Take CONFIG_DEFAULT_MMAP_MIN_ADDR from Fedra (Laura Abbott)
- configs: Turn off ISDN (Laura Abbott)
- Add a script to generate configuration patches (Laura Abbott)
- Introduce rh-configs-commit (Laura Abbott)
- kernel-packaging: Remove kernel files from kernel-modules-extra package (Prarit Bhargava)
- configs: Enable CONFIG_DEBUG_WX (Laura Abbott)
- configs: Disable wireless USB (Laura Abbott)
- Clean up some temporary config files (Laura Abbott)
- configs: New config in drivers/gpu for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/powerpc for v5.4-rc1 (Jeremy Cline)
- configs: New config in crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/usb for v5.4-rc1 (Jeremy Cline)
- AUTOMATIC: New configs (Jeremy Cline)
- Skip ksamples for bpf, they are broken (Jeremy Cline)
- configs: New config in fs/erofs for v5.4-rc1 (Jeremy Cline)
- configs: New config in mm for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/md for v5.4-rc1 (Jeremy Cline)
- configs: New config in init for v5.4-rc1 (Jeremy Cline)
- configs: New config in fs/fuse for v5.4-rc1 (Jeremy Cline)
- merge.pl: Avoid comments but do not skip them (Don Zickus)
- configs: New config in drivers/net/ethernet/pensando for v5.4-rc1 (Jeremy Cline)
- Update a comment about what released kernel means (Laura Abbott)
- Provide both Fedora and RHEL files in the SRPM (Laura Abbott)
- kernel.spec.template: Trim EXTRAVERSION in the Makefile (Laura Abbott)
- kernel.spec.template: Add macros for building with nopatches (Laura Abbott)
- kernel.spec.template: Add some macros for Fedora differences (Laura Abbott)
- kernel.spec.template: Consolodate the options (Laura Abbott)
- configs: Add pending direcory to Fedora (Laura Abbott)
- kernel.spec.template: Don't run hardlink if rpm-ostree is in use (Laura Abbott)
- configs: New config in net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/phy for v5.4-rc1 (Jeremy Cline)
- configs: Increase x86_64 NR_UARTS to 64 (Prarit Bhargava) [1730649]
- configs: turn on ARM64_FORCE_52BIT for debug builds (Jeremy Cline)
- kernel.spec.template: Tweak the python3 mangling (Laura Abbott)
- kernel.spec.template: Add --with verbose option (Laura Abbott)
- kernel.spec.template: Switch to using %%install instead of %%__install (Laura Abbott)
- kernel.spec.template: Make the kernel.org URL https (Laura Abbott)
- kernel.spec.template: Update message about secure boot signing (Laura Abbott)
- kernel.spec.template: Move some with flags definitions up (Laura Abbott)
- kernel.spec.template: Update some BuildRequires (Laura Abbott)
- kernel.spec.template: Get rid of %%clean (Laura Abbott)
- configs: New config in drivers/char for v5.4-rc1 (Jeremy Cline)
- configs: New config in net/sched for v5.4-rc1 (Jeremy Cline)
- configs: New config in lib for v5.4-rc1 (Jeremy Cline)
- configs: New config in fs/verity for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/aarch64 for v5.4-rc4 (Jeremy Cline)
- configs: New config in arch/arm64 for v5.4-rc1 (Jeremy Cline)
- Flip off CONFIG_ARM64_VA_BITS_52 so the bundle that turns it on applies (Jeremy Cline)
- New configuration options for v5.4-rc4 (Jeremy Cline)
- Correctly name tarball for single tarball builds (Laura Abbott)
- configs: New config in drivers/pci for v5.4-rc1 (Jeremy Cline)
- Allow overriding the dist tag on the command line (Laura Abbott)
- Allow scratch branch target to be overridden (Laura Abbott)
- Remove long dead BUILD_DEFAULT_TARGET (Laura Abbott)
- Amend the changelog when rebasing (Laura Abbott)
- configs: New config in drivers/platform for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/pinctrl for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/wireless for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/ethernet/mellanox for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hid for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/dma-buf for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in block for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/cpuidle for v5.4-rc1 (Jeremy Cline)
- redhat: configs: Split CONFIG_CRYPTO_SHA512 (Laura Abbott)
- redhat: Set Fedora options (Laura Abbott)
- Set CRYPTO_SHA3_*_S390 to builtin on zfcpdump (Jeremy Cline)
- configs: New config in drivers/edac for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/firmware for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hwmon for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/iio for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/mmc for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/tty for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/bus for v5.4-rc1 (Jeremy Cline)
- Add option to allow mismatched configs on the command line (Laura Abbott)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/pci for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/soc for v5.4-rc1 (Jeremy Cline)
- gitlab: Add CI job for packaging scripts (Major Hayden)
- Speed up CI with CKI image (Major Hayden)
- Disable e1000 driver in ARK (Neil Horman)
- configs: Fix the pending default for CONFIG_ARM64_VA_BITS_52 (Jeremy Cline)
- configs: Turn on OPTIMIZE_INLINING for everything (Jeremy Cline)
- configs: Set valid pending defaults for CRYPTO_ESSIV (Jeremy Cline)
- Add an initial CI configuration for the internal branch (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- Sync up the ARK build scripts (Jeremy Cline)
- Sync up the Fedora Rawhide configs (Jeremy Cline)
- Sync up the ARK config files (Jeremy Cline)
- configs: Adjust CONFIG_FORCE_MAX_ZONEORDER for Fedora (Laura Abbott)
- configs: Add README for some other arches (Laura Abbott)
- configs: Sync up Fedora configs (Laura Abbott)
- [initial commit] Add structure for building with git (Laura Abbott)
- [initial commit] Red Hat gitignore and attributes (Laura Abbott)
- [initial commit] Add changelog (Laura Abbott)
- [initial commit] Add makefile (Laura Abbott)
- [initial commit] Add files for generating the kernel.spec (Laura Abbott)
- [initial commit] Add rpm directory (Laura Abbott)
- [initial commit] Add files for packaging (Laura Abbott)
- [initial commit] Add kabi files (Laura Abbott)
- [initial commit] Add scripts (Laura Abbott)
- [initial commit] Add configs (Laura Abbott)
- [initial commit] Add Makefiles (Laura Abbott)

# The following bit is important for automation so please do not remove
# END OF CHANGELOG

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
