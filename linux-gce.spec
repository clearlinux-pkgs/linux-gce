#
# This is a special configuration of the Linux kernel, based on linux package
# for GCE Cloud support
# 
#

Name:           linux-gce
Version:        5.2.20
Release:        119
License:        GPL-2.0
Summary:        The Linux kernel for use in the GCE cloud
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.2.20.tar.xz
Source1:        config
Source2:        cmdline

%define ktarget  gce
%define kversion %{version}-%{release}.%{ktarget}

BuildRequires:  buildreq-kernel

Requires: systemd-bin
Requires: linux-gce-license = %{version}-%{release}

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#cve.start cve patches from 0001 to 009
Patch0001: CVE-2019-12379.patch
Patch0002: CVE-2019-12454.patch
Patch0003: CVE-2019-12455.patch
Patch0004: CVE-2019-12456.patch
#cve.end

#mainline: Mainline patches, upstream backport and fixes from 0051 to 0099
#mainline.end

#Serie.clr 01XX: Clear Linux patches
Patch0101: 0101-bootstats-add-printk-s-to-measure-boot-time-in-more-.patch
Patch0102: 0102-do-accept-in-LIFO-order-for-cache-efficiency.patch
Patch0103: 0103-e1000e-increase-pause-and-refresh-time.patch
Patch0104: 0104-give-rdrand-some-credit.patch
Patch0105: 0105-i8042-decrease-debug-message-level-to-info.patch
Patch0106: 0106-Increase-the-ext4-default-commit-age.patch
Patch0107: 0107-ipv4-tcp-allow-the-memory-tuning-for-tcp-to-go-a-lit.patch
Patch0108: 0108-ksm-wakeups.patch
Patch0109: 0109-locking-rwsem-spin-faster.patch
Patch0110: 0110-Migrate-some-systemd-defaults-to-the-kernel-defaults.patch
Patch0111: 0111-pci-pme-wakeups.patch
Patch0112: 0112-raid6-add-Kconfig-option-to-skip-raid6-benchmarking.patch
Patch0113: 0113-reduce-e1000e-boot-time-by-tightening-sleep-ranges.patch
Patch0114: 0114-silence-rapl.patch
Patch0115: 0115-smpboot-reuse-timer-calibration.patch
Patch0116: 0116-use-lfence-instead-of-rep-and-nop.patch
Patch0117: 0117-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch0118: 0118-zero-extra-registers.patch
Patch0119: 0119-config-no-Atom.patch
Patch0120: 0120-e1000e-change-default-policy.patch
Patch0121: 0121-fix-initcall-timestamps.patch
Patch0122: 0122-igb-no-runtime-pm-to-fix-reboot-oops.patch
Patch0123: 0123-init_task-faster-timerslack.patch
Patch0124: 0124-mm-reduce-vmstat-wakeups.patch
Patch0125: 0125-overload-on-wakeup.patch
Patch0126: 0126-time-ntp-fix-wakeups.patch
#Serie.end

#Serie1.name WireGuard
#Serie1.git  https://git.zx2c4.com/WireGuard
#Serie1.cmt  d8179bf1ed9ecf0c7f9a78ceb0566a7e7b2f4497
#Serie1.tag  0.0.20190702
Patch1001: 1001-WireGuard-fast-modern-secure-kernel-VPN-tunnel.patch
#Serie1.end

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel GCE extra files
Group:          kernel
Requires:       linux-gce-license = %{version}-%{release}

%description extra
Linux kernel extra files

%package license
Summary: license components for the linux package.
Group: Default

%description license
license components for the linux package.

%prep
%setup -q -n linux-5.2.20

#cve.patch.start cve patches
%patch0001 -p1
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1
#cve.patch.end

#mainline.patch.start Mainline patches, upstream backport and fixes
#mainline.patch.end

#Serie.patch.start Clear Linux patches
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
%patch0124 -p1
%patch0125 -p1
%patch0126 -p1
#Serie.patch.end

#Serie1.patch.start
%patch1001 -p1
#Serie1.patch.end

cp %{SOURCE1} .

%build
BuildKernel() {

    Target=$1
    Arch=x86_64
    ExtraVer="-%{release}.${Target}"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make O=${Target} -s mrproper
    cp config ${Target}/.config

    make O=${Target} -s ARCH=${Arch} olddefconfig
    make O=${Target} -s ARCH=${Arch} CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} %{?sparse_mflags}
}

BuildKernel %{ktarget}

%install

InstallKernel() {

    Target=$1
    Kversion=$2
    Arch=x86_64
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 ${Target}/.config    ${KernelDir}/config-${Kversion}
    install -m 644 ${Target}/System.map ${KernelDir}/System.map-${Kversion}
    install -m 644 ${Target}/vmlinux    ${KernelDir}/vmlinux-${Kversion}
    install -m 644 %{SOURCE2}           ${KernelDir}/cmdline-${Kversion}
    cp  ${Target}/arch/x86/boot/bzImage ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules
    make O=${Target} -s ARCH=${Arch} INSTALL_MOD_PATH=%{buildroot}/usr modules_install

    rm -f %{buildroot}/usr/lib/modules/${Kversion}/build
    rm -f %{buildroot}/usr/lib/modules/${Kversion}/source

    # Kernel default target link
    ln -s org.clearlinux.${Target}.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-${Target}
}

InstallKernel %{ktarget} %{kversion}

rm -rf %{buildroot}/usr/lib/firmware

mkdir -p %{buildroot}/usr/share/package-licenses/linux-gce
cp COPYING %{buildroot}/usr/share/package-licenses/linux-gce/COPYING
cp -a LICENSES/* %{buildroot}/usr/share/package-licenses/linux-gce

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
/usr/lib/kernel/org.clearlinux.%{ktarget}.%{version}-%{release}
/usr/lib/kernel/default-%{ktarget}
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}
/usr/lib/kernel/vmlinux-%{kversion}

%files license
%defattr(0644,root,root,0755)
/usr/share/package-licenses/linux-gce
