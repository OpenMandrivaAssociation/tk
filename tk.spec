%define distname %{name}%{version}-src.tar.gz
%define dirname_ %{name}%{version}
%define major %(echo %{version} |cut -d. -f1-2)
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	GUI toolkit for Tcl
Name:		tk
Version:	8.6.8
Release:	1
License:	BSD
Group:		System/Libraries
URL:		http://tcl.tk
Source0:	http://downloads.sourceforge.net/tcl/%{distname}
Source1:	icons.tcl
Source2:	tk.rpmlintrc
Patch0:		tk8.6.1-soname.patch
Patch1:		tk8.6b1-fix_Xft_linkage.patch
Requires:	%{libname} = %{EVRD}
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

%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n	%{libname}
Tk is a X Windows widget set designed to work closely with the tcl
scripting language. It allows you to write simple programs with full
featured GUI's in only a little more time then it takes to write a
text based interface. Tcl/Tk applications can also be run on Windows
and Macintosh platforms.

%package -n %{develname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{EVRD}
Requires:	%{libname} = %{EVRD}
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
    %configure \
	--enable-threads \
	--enable-64bit \
	--disable-rpath \
	--with-tcl=%{_libdir} \
	--includedir=%{_includedir}/tk%{version}

    %make CFLAGS="%{optflags}" TK_LIBRARY=%{_datadir}/%{name}%{majorver}

    cp libtk%{major}.so libtk%{major}.so.0
#    make test
popd

%install

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
%{_libdir}/lib*%{major}.so.0*

%files -n %{develname} -f %{develname}.files
%dir %{_includedir}/tk%{version}
%dir %{_includedir}/tk%{version}/compat
%dir %{_includedir}/tk%{version}/generic
%dir %{_includedir}/tk%{version}/unix
%{_includedir}/tk%{version}/compat/*.h
%{_includedir}/tk%{version}/generic/*.h
%{_includedir}/tk%{version}/unix/*.h
%{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/tkConfig.sh
%{_libdir}/pkgconfig/*.pc
