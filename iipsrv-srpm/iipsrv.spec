%global commit 61bfa65d686fd0c0242a3c0b183ef77fef7364a8
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%if 0%{?fedora} >= 18
%global with_systemd 1
%else
%global with_systemd 0
%endif
%{!?_initddir: %{expand: %%global _initddir %{_initrddir}}}

%if %{?fedora}%{?rhel} >= 5
%global useselinux 1
%else
%global useselinux 0
%endif

%global iipver 1.0

Name:           iipsrv
Version:        1.0.0
Release:        1.0%{?dist}
Summary:        Light-weight streaming for viewing and zooming of ultra high-resolution images

Group:          Applications/Multimedia
License:        GPLv3+
URL:            http://iipimage.sourceforge.net
Source0:        https://github.com/ruven/%{name}/archive/%{name}-%{iipver}.tar.gz
Source1:        %{name}-httpd.conf
Source2:        README.rpm
Source3:        %{name}-logrotate
Source10:       %{name}.service
Source11:       %{name}.initd
Source12:       %{name}.initd.conf
Patch0:         %{name}-remove-bundled-fcgi.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  zlib-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libtiff-devel
BuildRequires:  fcgi-devel
%if 0%{?rhel} != 5
BuildRequires:  lcms2-devel
%endif
BuildRequires:  libpng-devel
%if 0%{?fedora}
BuildRequires:  libmemcached-devel
%endif
%if %{with_systemd}
BuildRequires:  systemd-units
%endif
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
%if %{with_systemd}
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%else
Requires(post): chkconfig
Requires(preun): chkconfig
# for /sbin/service
Requires(preun): initscripts
Requires(postun): initscripts
%endif
Requires:       %{_sysconfdir}/logrotate.d

%if %{useselinux}
Requires(post):   /sbin/service
Requires(post):   /sbin/restorecon
Requires(post):   /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage
BuildRequires:  selinux-policy-devel, checkpolicy
%endif


%description
Light-weight streaming client-server system for the web-based viewing and
zooming of ultra high-resolution images. It is designed to be bandwidth
and memory efficient and usable even over a slow internet connection.

The system can handle both 8 and 16 bit images, CIELAB colorimetric images and
scientific imagery such as multispectral images. The fast streaming is
tile-based meaning the client only needs to download the portion of the whole
image that is visible on the screen of the user at their current viewing
resolution and not the entire image.
This makes it possible to view, navigate and zoom in real-time around
multi-gigapixel size images that would be impossible to download and
manipulate on the local machine. It also makes the system very scalable as
the number of image tile downloads will remain the same regardless of the
size of the source image. In addition, to reduce the bandwidth necessary even
further, the tiles sent back are dynamically JPEG compressed with a level of
compression that can be optimized for the available bandwidth by the client.


%package httpd-fcgi
Summary:         Apache HTTPD files for %{name}
Group:           Applications/Multimedia
Requires:        %{name} = %{version}-%{release}
Requires:        httpd
Requires:        mod_fcgid
%if %{with_systemd}
Requires(post):  systemd-units
%else
Requires(post):  initscripts
%endif
%if 0%{?rhel} != 5
#EL-5 does not handle noarch subpackages correctly
BuildArch:       noarch
%endif


%description httpd-fcgi
IIPImage server Apache/mod_fcgid files


%prep
%setup -q -n %{name}-%{name}-%{iipver}
%patch0 -p1
#fix man
sed -e "s/\.Iiipsrv/.I iipsrv/" -i man/%{name}.8
#specfific fixes for el5...
%if 0%{?rhel}  == 5
sed 's/AC_PROG_MAKE_SET/AC_PROG_MAKE_SET\
AC_PROG_RANLIB/' -i configure.in
mkdir m4
%endif
#remove bundled lib
%if 0%{?rhel}  == 5
#directives names has changed since pre ASF releases of mod_fcgid
#see http://httpd.apache.org/mod_fcgid/mod/mod_fcgid.html#upgrade
sed -i \
  -e 's/FcgidIdleTimeout/IdleTimeout/' \
  -e 's/FcgidMaxProcessesPerClass/DefaultMaxClassProcessCount/' \
  %{SOURCE1}
%endif


%build
./autogen.sh
%configure --with-fcgi-lib=%{_includedir} --with-kakadu=/usr/share/kakadu
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/
install -m 0644 -D -p %{SOURCE1} ${RPM_BUILD_ROOT}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p $RPM_BUILD_ROOT%{_libexecdir}/%{name}
install -m 0755 -D -p src/iipsrv.fcgi $RPM_BUILD_ROOT%{_libexecdir}/%{name}/%{name}.fcgi

cp %{SOURCE2} .

%if %{with_systemd}
#systemd stuff
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}/%{name}.service
%else
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/
install -m 0644 -D -p %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
#install initd script
mkdir -p $RPM_BUILD_ROOT%{_initddir}
install -m755 %{SOURCE11} $RPM_BUILD_ROOT%{_initddir}/%{name}
%endif

#log stuff
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}


%clean
rm -rf $RPM_BUILD_ROOT


%post httpd-fcgi
%if %{useselinux}
(
# File context
semanage fcontext -a -s system_u -t httpd_log_t -r s0 "%{_localstatedir}/log/%{name}(/.*)?"
# files created by app
restorecon -R %{_localstatedir}/log/%{name}
) &>/dev/null
%endif

%if %{with_systemd}
/bin/systemctl condrestart httpd.service
%else
/sbin/service condrestart httpd
%endif


%pre
%{_sbindir}/useradd -r -s /sbin/nologin %{name} 2> /dev/null || :


%preun
%if %{with_systemd}
%systemd_preun %{name}.service
%else
if [ $1 = 0 ]; then
    # Package removal, not upgrade
    service %{name} stop > /dev/null 2>&1 || :
    chkconfig --del %{name} || :
fi
%endif


%post
%if %{with_systemd}
%systemd_post %{name}.service
%else
if [ $1 -eq 1 ] ; then
    # Initial installation
    chkconfig --add %{name} || :
fi
%endif

%postun
%if %{with_systemd}
%systemd_postun_with_restart %{name}.service
%else
if [ $1 -ge 1 ]; then
    /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi
%endif


%postun httpd-fcgi
%if %{useselinux}
if [ "$1" -eq "0" ]; then
    # Remove the File Context
    (
    semanage fcontext -d "%{_localstatedir}/log/%{name}(/.*)?"
    ) &>/dev/null
fi
%endif
/sbin/service httpd condrestart > /dev/null 2>&1 || :


%files
%defattr(-,root,root,-)
%doc README AUTHORS ChangeLog TODO COPYING doc/* README.rpm
%{_libexecdir}/%{name}/%{name}.fcgi
%if %{with_systemd}
%{_unitdir}/%{name}.service
%else
%{_initddir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%endif
%{_mandir}/man8/%{name}.8.gz
%dir %{_localstatedir}/log/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}


%files httpd-fcgi
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf


%changelog
* Wed May 15 2019 Christophe Vanlancker <carroarmato0 AT inuits eu> - 1.0.0.git61bfa65
- Compile git checkout 61bfa65d6 with kakadu support

* Thu May 05 2016 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-6.0
- Update to final 1.0 release
- Add specific log directory and logrotate stuff
- Change default VERBOSITY, JPEG_QUALITY to better values
- Set SELinux contexts for log files when installing httpd-fcgi subpackage

* Fri May 24 2013 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-0.7.git0b63de7
- Fix license
- Set httpd-fcgi sub-package noarch (exept for EL5)
- Add missing BuilRequires
- Fix unconsistent scriplets
- Add missing SysV postun
- Add missing SysV Requires
- Add comment on service file on how to tune
- Add missing Requires on httpd-fcgi subpackage
- Remove bundled lib
- New mod_fcgid directives names (except for el5)

* Wed May 22 2013 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-0.6.git0b63de7
- Systemd configuration directives are now handled in unit file

* Sun May 19 2013 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-0.5.git0b63de7
- Add SysV service files

* Sun May 19 2013 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-0.4.git0b63de7
- Add iipsrv systemd service and user
- Remove Requires on mod_fcgi
- Fix service name for non fedora

* Sun May 19 2013 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-0.3.git0b63de7
- Remove strip and reactivate debuginfo package
- Use system fcgi and not bundeld one, remove -devel subpackage
- Do not install stuff in /var/www
- Create httpd-fcgi subpackage

* Sat May 18 2013 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-0.2.git0b63de7
- Specfile cleanup
- Replace %%define by %%global

* Sun May 05 2013 Johan  Cwiklinski <johan AT x-tnd DOT be> - 1.0.0-0.1.git0b63de7
- Rebuild from latest GIT snapshot

* Thu Apr 21 2011 Johan Cwiklinski <johan AT x-tnd DOT be> - 0.9.9-3.trashy
- memcached support (for Fedora only, does not compile on EL 5/6)

* Wed Apr 20 2011 Johan Cwiklinski <johan AT x-tnd DOT be> - 0.9.9-2.trashy
- Upgrade to 0.9.9

* Sat Jul 24 2010 Johan Cwiklinski <johan AT x-tnd DOT be> - 0.9.9-1.20100724
- Upgrade to latest SVN

* Wed Dec 23 2009 Johan Cwiklinski <johan AT x-tnd DOT be> - 0.9.9-1.20091202
- Upgrade to latest SVN

* Wed Dec 23 2009 Johan Cwiklinski <johan AT x-tnd DOT be> - 0.9.8-1.20090722
- Rebuild for F-12

* Mon Mar 30 2009 Johan Cwiklinski <johan AT x-tnd DOT be> - 0.9.8-1.20090331
- Initial packaging
