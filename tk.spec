%define major		8.5
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d

Summary:	Tk GUI toolkit for Tcl
Name:		tk
Version:	8.5.2
Release:	%mkrel 1
License:	BSD
Group:		System/Libraries
URL:		http://tcl.tk
Source0:	http://prdownloads.sourceforge.net/tcl/%{name}%{version}-src.tar.gz
Patch0:		tk-8.5.0-soname.patch
Requires:	%{libname} = %{version}-%{release}
BuildRequires:	tcl-devel >= %{version}
BuildRequires:	X11-devel
BuildRequires:	chrpath
Conflicts:	tk8.4-devel
Buildroot:	%{_tmppath}/%{name}-%{version}

%description
Tk is a X Windows widget set designed to work closely with the tcl
scripting language. It allows you to write simple programs with full
featured GUI's in only a little more time then it takes to write a
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
Requires:       libx11-devel
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname tk 8.5 -d}
Obsoletes:	%{mklibname tk 8.4 -d}

%description -n	%{develname}
This package contains development files for %{name}.

%prep
%setup -q -n %{name}%{version}
%patch0 -p1

%build
pushd unix
    autoconf
    %configure2_5x \
	--enable-gcc \
	--enable-threads \
	--enable-64bit \
	--disable-rpath \
	--with-tcl=%{_libdir} \
	--includedir=%{_includedir}/tk%{version}
    %make

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

%makeinstall -C unix

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

# Arrangements for lib64 platforms
echo "# placeholder" >> %{libname}.files
echo "# placeholder" >> %{develname}.files
if [[ "%{_lib}" != "lib" ]]; then
    ln -s %{_libdir}/tkConfig.sh %{buildroot}%{_prefix}/lib/tkConfig.sh
    echo "%{_prefix}/lib/tkConfig.sh" >> %{develname}.files
    echo "%{_libdir}/%{name}%{major}/pkgIndex.tcl" >> %{libname}.files
fi

# (fc) make sure .so files are writable by root
chmod 755 %{buildroot}%{_libdir}/*.so*

# (tpg) nuke rpath
chrpath -d %{buildroot}%{_libdir}/libtk%{major}.so.0

%if %mdkversion < 200900
%post -p /sbin/ldconfig -n %{libname}
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig -n %{libname}
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/*
%{_prefix}/lib/%{name}%{major}
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_mandir}/mann/*

%files -n %{libname} -f %{libname}.files
%defattr(-,root,root)
%attr(0755,root,root) %{_libdir}/lib*.so.*

%files -n %{develname} -f %{develname}.files
%defattr(-,root,root)
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

