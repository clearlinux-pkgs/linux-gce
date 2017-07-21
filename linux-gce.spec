#
# note to self: Linus releases need to be named 4.x.0 not 4.x or various
# things break
#

Name:           linux-gce
Version:        4.12.3
Release:        35
License:        GPL-2.0
Summary:        The Linux kernel for use in the GCE cloud
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.12.3.tar.xz
Source1:        config
Source2:        cmdline

%define kversion %{version}-%{release}.gce

BuildRequires:  bash >= 2.03
BuildRequires:  bc
BuildRequires:  binutils-dev
BuildRequires:  elfutils-dev
BuildRequires:  make >= 3.78
BuildRequires:  openssl-dev
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  kmod
BuildRequires:  lz4


# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#    000X: cve, bugfixes patches

#    00XY: Mainline patches, upstream backports

# Serie    01XX: Clear Linux patches
Patch0101: 0101-i8042-decrease-debug-message-level-to-info.patch
Patch0102: 0102-init-do_mounts-recreate-dev-root.patch
Patch0103: 0103-Increase-the-ext4-default-commit-age.patch
Patch0104: 0104-silence-rapl.patch
Patch0105: 0105-pci-pme-wakeups.patch
Patch0106: 0106-ksm-wakeups.patch
Patch0107: 0107-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch0108: 0108-init_task-faster-timerslack.patch
Patch0109: 0109-overload-on-wakeup.patch
Patch0110: 0110-bootstats-add-printk-s-to-measure-boot-time-in-more-.patch
Patch0111: 0111-fix-initcall-timestamps.patch
Patch0112: 0112-smpboot-reuse-timer-calibration.patch
Patch0113: 0113-raid6-add-Kconfig-option-to-skip-raid6-benchmarking.patch
Patch0114: 0114-reduce-e1000e-boot-time-by-tightening-sleep-ranges.patch
Patch0115: 0115-give-rdrand-some-credit.patch
Patch0116: 0116-e1000e-change-default-policy.patch
Patch0117: 0117-ipv4-tcp-allow-the-memory-tuning-for-tcp-to-go-a-lit.patch
Patch0118: 0118-igb-no-runtime-pm-to-fix-reboot-oops.patch
Patch0119: 0119-tweak-perfbias.patch
Patch0120: 0120-e1000e-increase-pause-and-refresh-time.patch
Patch0121: 0121-time-ntp-fix-wakeups.patch
Patch0122: 0122-mm-reduce-vmstat-wakeups.patch
Patch0123: 0123-config-no-Atom.patch


%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel extra files
Group:          kernel

%description extra
Linux kernel extra files

%prep
%setup -q -n linux-4.12.3

#     000X  cve, bugfixes patches

#     00XY  Mainline patches, upstream backports

#     01XX  Clear Linux patches
%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0106 -p1
%patch0107 -p1
%patch0108 -p1
%patch0109 -p1
%patch0110 -p1
%patch0111 -p1
%patch0112 -p1
%patch0113 -p1
%patch0114 -p1
%patch0115 -p1
%patch0116 -p1
%patch0117 -p1
%patch0118 -p1
%patch0119 -p1
%patch0120 -p1
%patch0121 -p1
%patch0122 -p1
%patch0123 -p1


cp %{SOURCE1} .

%build
BuildKernel() {
    MakeTarget=$1

    Arch=x86_64
    ExtraVer="-%{release}.gce"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make -s mrproper
    cp config .config

    make -s ARCH=$Arch oldconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch %{?sparse_mflags}
}

BuildKernel bzImage

%install

InstallKernel() {
    KernelImage=$1

    Arch=x86_64
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 .config    ${KernelDir}/config-${KernelVer}
    install -m 644 System.map ${KernelDir}/System.map-${KernelVer}
    install -m 644 %{SOURCE2} ${KernelDir}/cmdline-${KernelVer}
    cp  $KernelImage ${KernelDir}/org.clearlinux.gce.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.gce.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules/$KernelVer
    make -s ARCH=$Arch INSTALL_MOD_PATH=%{buildroot}/usr modules_install KERNELRELEASE=$KernelVer

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source

    # Erase some modules index
    for i in alias ccwmap dep ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols usbmap softdep devname
    do
        rm -f %{buildroot}/usr/lib/modules/${KernelVer}/modules.${i}*
    done
    rm -f %{buildroot}/usr/lib/modules/${KernelVer}/modules.*.bin
}

InstallKernel arch/x86/boot/bzImage

rm -rf %{buildroot}/usr/lib/firmware

# Recreate modules indices
depmod -a -b %{buildroot}/usr %{kversion}

ln -s org.clearlinux.gce.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-gce

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
/usr/lib/kernel/org.clearlinux.gce.%{version}-%{release}
/usr/lib/kernel/default-gce
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}

