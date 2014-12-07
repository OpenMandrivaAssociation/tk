%define distname	%{name}%{version}-src.tar.gz
%define dirname_	%{name}%{version}

%define major		8.6
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d

Summary:	GUI toolkit for Tcl
Name:		tk
Version:	8.6.1
Release:	5
License:	BSD
Group:		System/Libraries
URL:		http://tcl.tk
Source0:	http://downloads.sourceforge.net/tcl/%{distname}
Source1:        icons.tcl
Source2:	tk.rpmlintrc
Patch0:		tk8.6.1-soname.patch
Patch1:		tk8.6b1-fix_Xft_linkage.patch
Requires:	%{libname} = %{version}-%{release}
#tcl requires tcl?
BuildRequires:	tcl-devel >= %{version}
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xft)
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(xscrnsaver)
BuildRequires:	chrpath
Provides:	%{_bindir}/wish

%description
Tk is a X Windows widget set designed to work closely with the tcl
scripting language. It allows you to write simple programs with full
featured GUIs in only a little more time then it takes to write a
text based interface. Tcl/Tk applications can also be run on Windows
and Macintosh platforms.

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n	%{libname}
Tk is a X Windows widget set designed to work closely with the tcl
scripting language. It allows you to write simple programs with full
featured GUI's in only a little more time then it takes to write a
text based interface. Tcl/Tk applications can also be run on Windows
and Macintosh platforms.

%package -n	%{develname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Requires:	pkgconfig(x11)
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{develname}
This package contains development files for %{name}.

%prep
%setup -q -n %{dirname_}
%patch0 -p1 -b .so
%patch1 -p1 -b .Xft
# Replace native icons.tcl - it contains  PNG data
# obtained using old libpng and has problems with new libpng
# The new one contains PNG data created using
# new libpng
cp -f %{SOURCE1} library

%build
pushd unix
    autoconf
    %configure2_5x \
	--enable-threads \
	--enable-64bit \
	--disable-rpath \
	--with-tcl=%{_libdir} \
	--includedir=%{_includedir}/tk%{version}
    %make TK_LIBRARY=%{_datadir}/%{name}%{majorver}

    cp libtk%{major}.so libtk%{major}.so.0
#    make test
popd

%install
rm -rf %{buildroot}

# If %{_libdir} is not %{_prefix}/lib, then define EXTRA_TCLLIB_FILES
# which contains actual non-architecture-dependent tcl code.
if [ "%{_libdir}" != "%{_prefix}/lib" ]; then
    EXTRA_TCLLIB_FILES="%{buildroot}%{_prefix}/lib/*"
fi

%makeinstall -C unix TK_LIBRARY=%{buildroot}%{_datadir}/%{name}%{major}

# create the arch-dependent dir
mkdir -p %{buildroot}%{_libdir}/%{name}%{major}

# fix libname
mv %{buildroot}%{_libdir}/libtk%{major}.so %{buildroot}%{_libdir}/libtk%{major}.so.0
ln -snf libtk%{major}.so.0 %{buildroot}%{_libdir}/libtk%{major}.so

# install all headers
install -d %{buildroot}%{_includedir}/tk%{version}/compat
install -d %{buildroot}%{_includedir}/tk%{version}/generic
install -d %{buildroot}%{_includedir}/tk%{version}/unix
install -m0644 compat/*.h %{buildroot}%{_includedir}/tk%{version}/compat/
install -m0644 generic/*.h %{buildroot}%{_includedir}/tk%{version}/generic/
install -m0644 unix/*.h %{buildroot}%{_includedir}/tk%{version}/unix/

# (tpg) compat issues
cp -f %{buildroot}%{_includedir}/tk%{version}/unix/tkUnixPort.h %{buildroot}%{_includedir}/tk%{version}/generic/

pushd %{buildroot}%{_bindir}
    ln -sf wish* wish
popd

pushd %{buildroot}%{_libdir}
cat > lib%{name}.so << EOF
/* GNU ld script
   We want -l%{name} to include the actual system library,
   which is lib%{name}%{major}.so.0  */
INPUT ( -l%{name}%{major} )
EOF
popd

# fix config script
perl -pi -e "s|-L`pwd`/unix\b|-L%{_libdir}|g" %{buildroot}%{_libdir}/tkConfig.sh
perl -pi -e "s|`pwd`/unix/lib|%{_libdir}/lib|g" %{buildroot}%{_libdir}/tkConfig.sh
perl -pi -e "s|`pwd`|%{_includedir}/tk%{version}|g" %{buildroot}%{_libdir}/tkConfig.sh

# and let it be found (we don't look in /usr/lib any more)
ln -s %{_libdir}/%{name}Config.sh %{buildroot}/%{_libdir}/%{name}%{major}/%{name}Config.sh

# Arrangements for lib64 platforms
echo "# placeholder" >> %{libname}.files
echo "# placeholder" >> %{develname}.files
if [[ "%{_lib}" != "lib" ]]; then
    mkdir -p %{buildroot}%{_prefix}/lib
    ln -s %{_libdir}/tkConfig.sh %{buildroot}%{_prefix}/lib/tkConfig.sh
    echo "%{_prefix}/lib/tkConfig.sh" >> %{develname}.files
fi

# (fc) make sure .so files are writable by root
chmod 755 %{buildroot}%{_libdir}/*.so*

# (tpg) nuke rpath
chrpath -d %{buildroot}%{_libdir}/libtk%{major}.so.0

%files
%{_bindir}/*
%{_libdir}/%{name}%{major}
%{_datadir}/%{name}%{major}
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_mandir}/mann/*

%files -n %{libname} -f %{libname}.files
%attr(0755,root,root) %{_libdir}/lib*.so.*

%files -n %{develname} -f %{develname}.files
%dir %{_includedir}/tk%{version}
%dir %{_includedir}/tk%{version}/compat
%dir %{_includedir}/tk%{version}/generic
%dir %{_includedir}/tk%{version}/unix
%attr(0644,root,root) %{_includedir}/tk%{version}/compat/*.h
%attr(0644,root,root) %{_includedir}/tk%{version}/generic/*.h
%attr(0644,root,root) %{_includedir}/tk%{version}/unix/*.h
%attr(0644,root,root) %{_includedir}/*.h
%attr(0755,root,root) %{_libdir}/*.so
%attr(0644,root,root) %{_libdir}/*.a
%attr(0755,root,root) %{_libdir}/tkConfig.sh
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%changelog
* Fri Apr 20 2012 Bernhard Rosenkraenzer <bero@bero.eu> 8.6-0.b2.1mdv2012.0
+ Revision: 792552
- 8.6b2

* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 8.6-0.b1.8
+ Revision: 670709
- mass rebuild

* Sat Jan 01 2011 Funda Wang <fwang@mandriva.org> 8.6-0.b1.7mdv2011.0
+ Revision: 626939
- tighten BR

* Thu Dec 09 2010 Jani Välimaa <wally@mandriva.org> 8.6-0.b1.6mdv2011.0
+ Revision: 617526
- fix linking with Xft

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 8.6-0.b1.5mdv2011.0
+ Revision: 608012
- rebuild

* Sun Jan 03 2010 Funda Wang <fwang@mandriva.org> 8.6-0.b1.4mdv2010.1
+ Revision: 486058
- build with thread support

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 8.6-0.b1.3mdv2010.0
+ Revision: 427383
- rebuild

* Thu Mar 05 2009 Frederic Crozat <fcrozat@mandriva.com> 8.6-0.b1.2mdv2009.1
+ Revision: 348795
- Explicitly provides /usr/bin/wish (Mdv bug #48458)

* Wed Dec 24 2008 Adam Williamson <awilliamson@mandriva.org> 8.6-0.b1.1mdv2009.1
+ Revision: 318173
- new release 8.6b1
- drop panic.patch (merged upstream)

* Fri Dec 05 2008 Adam Williamson <awilliamson@mandriva.org> 8.6-0.a3.1mdv2009.1
+ Revision: 310131
- add panic.patch from upstream CVS: fix build breaking error
- create prefix/lib on x86-64
- new locations: /usr/lib/tk8.6 and /usr/share/tk8.6
- drop libtk-devel provide, everything should use tk-devel now
- no need to conflict with tk8.4, it doesn't exist any more
- new release 8.6a3

* Wed Oct 15 2008 Frederik Himpe <fhimpe@mandriva.org> 8.5.5-1mdv2009.1
+ Revision: 294067
- update to new version 8.5.5

* Fri Aug 15 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.4-1mdv2009.0
+ Revision: 272388
- new release 8.5.4

* Mon Jul 07 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5.3-1mdv2009.0
+ Revision: 232455
- update to new version 8.5.3

* Tue Jun 24 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.2-1mdv2009.0
+ Revision: 228749
- rediff soname.patch
- new release 8.5.2

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 8.5.1-2mdv2009.0
+ Revision: 225772
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Feb 05 2008 Frederik Himpe <fhimpe@mandriva.org> 8.5.1-1mdv2008.1
+ Revision: 162831
- New upstream bugfix release (fixes security problem CVE-2008-0553)

* Sat Jan 12 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.0-1mdv2008.1
+ Revision: 149228
- correct devel obsolete
- replace rpath.patch with a configure option
- rediff soname.patch
- reorganize spec to follow Mandriva norms
- new release 8.5.0 final

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Sep 07 2007 Anssi Hannula <anssi@mandriva.org> 8.5a6-8mdv2008.0
+ Revision: 81990
- rebuild for new soname of tcl

* Fri Sep 07 2007 Anssi Hannula <anssi@mandriva.org> 8.5a6-7mdv2008.0
+ Revision: 81980
- rediff and reapply soname and rpath patches (fixes #31618)

* Wed Jun 20 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a6-6mdv2008.0
+ Revision: 41805
- update url
- handle nicely some stubborn files

* Wed Jun 20 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a6-5mdv2008.0
+ Revision: 41680
- fix build on x86_64
- own missing files
- nuke rpath
- provide a symlink for tkUnixPort.h
- new devel library policy

* Thu Jun 07 2007 Anssi Hannula <anssi@mandriva.org> 8.5a6-3mdv2008.0
+ Revision: 36207
- rebuild with correct optflags

* Tue Jun 05 2007 Jérôme Soyer <saispo@mandriva.org> 8.5a6-2mdv2008.0
+ Revision: 35821
- Add Conflicts

* Thu May 31 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a6-1mdv2008.0
+ Revision: 33191
- new version

* Thu May 03 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a5-3mdv2008.0
+ Revision: 21616
- correct requires

* Sun Apr 22 2007 Nicolas Lécureuil <nlecureuil@mandriva.com> 8.5a5-2mdv2008.0
+ Revision: 17092
- Fix Require ( close bug #30376)

* Fri Apr 20 2007 Jérôme Soyer <saispo@mandriva.org> 8.5a5-1mdv2008.0
+ Revision: 16128
- New release 8.5a5


* Mon Dec 18 2006 Nicolas Lécureuil <neoclust@mandriva.org> 8.4.14-1mdv2007.0
+ Revision: 98584
- New version 8.4.14
- Import tk

* Sat Apr 22 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.13-1mdk
- 8.4.13
- drop upstream patches; P2

* Tue Feb 14 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.12-1mdk
- 8.4.12
- added P2 to fix build with bash31

* Sun Jan 01 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-5mdk
- fix the tkConfig.sh file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-4mdk
- file the libtk.so file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-3mdk
- fix soname (P1) after looking at debian
- ship missing headers
- misc lib64 and spec file fixes

* Thu Dec 29 2005 Guillaume Rousse <guillomovitch@mandriva.org> 8.4.11-2mdk
- first release as a standalone package
- devel files in a devel package

