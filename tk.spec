%define distname %{name}%{version}-src.tar.gz
%define dirname_ %{name}%{version}
%define major %(echo %{version} |cut -d. -f1-2)
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	GUI toolkit for Tcl
Name:		tk
Version:	8.6.10
Release:	1
License:	BSD
Group:		System/Libraries
URL:		http://tcl.tk
Source0:	http://downloads.sourceforge.net/tcl/%{distname}
Source1:	icons.tcl
Source2:	tk.rpmlintrc
Patch0:		https://src.fedoraproject.org/rpms/tk/raw/master/f/tk-8.6.10-make.patch
Patch1:		https://src.fedoraproject.org/rpms/tk/raw/master/f/tk-8.6.10-conf.patch
Patch2:		https://src.fedoraproject.org/rpms/tk/raw/master/f/tk-8.6.7-no-fonts-fix.patch
Patch3:		tk8.6b1-fix_Xft_linkage.patch
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

%description -n %{libname}
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

%description -n %{develname}
This package contains development files for %{name}.

%prep
%autosetup -n %{dirname_} -p1

# Replace native icons.tcl - it contains  PNG data
# obtained using old libpng and has problems with new libpng
# The new one contains PNG data created using
# new libpng
cp -f %{SOURCE1} library

%build
cd unix
    autoconf
    %configure \
	--enable-threads \
	--enable-64bit \
	--disable-rpath \
	--with-tcl=%{_libdir} \
	--includedir=%{_includedir}/tk%{version}

    %make_build CFLAGS="%{optflags}" TK_LIBRARY="%{_datadir}/%{name}%{major}"

    cp libtk%{major}.so libtk%{major}.so.0
cd -

%install

# If %{_libdir} is not %{_prefix}/lib, then define EXTRA_TCLLIB_FILES
# which contains actual non-architecture-dependent tcl code.
if [ "%{_libdir}" != "%{_prefix}/lib" ]; then
    EXTRA_TCLLIB_FILES="%{buildroot}%{_prefix}/lib/*"
fi

%make_install -C unix INSTALL_ROOT=%{buildroot} TK_LIBRARY="%{_datadir}/%{name}%{major}"

# create the arch-dependent dir
mkdir -p %{buildroot}%{_libdir}/%{name}%{major}

ln -s wish%{major} %{buildroot}%{_bindir}/wish

# fix libname
mv %{buildroot}%{_libdir}/libtk%{major}.so %{buildroot}%{_libdir}/libtk%{major}.so.0
ln -snf libtk%{major}.so.0 %{buildroot}%{_libdir}/libtk%{major}.so

# for linking with -l%%{name}
ln -s lib%{name}%{major}.so %{buildroot}%{_libdir}/lib%{name}.so

# install all headers
install -d %{buildroot}%{_includedir}/tk%{version}/compat
install -d %{buildroot}%{_includedir}/tk%{version}/generic
install -d %{buildroot}%{_includedir}/tk%{version}/unix
install -m0644 compat/*.h %{buildroot}%{_includedir}/tk%{version}/compat/
install -m0644 generic/*.h %{buildroot}%{_includedir}/tk%{version}/generic/
install -m0644 unix/*.h %{buildroot}%{_includedir}/tk%{version}/unix/

# (tpg) compat issues
cp -f %{buildroot}%{_includedir}/tk%{version}/unix/tkUnixPort.h %{buildroot}%{_includedir}/tk%{version}/generic/

mkdir -p %{buildroot}/%{_includedir}/%{name}-private/{generic/ttk,unix}
find generic unix -name "*.h" -exec cp -p '{}' %{buildroot}/%{_includedir}/%{name}-private/'{}' ';'
( cd %{buildroot}/%{_includedir}
  for i in *.h ; do
    [ -f %{buildroot}/%{_includedir}/%{name}-private/generic/$i ] && ln -sf ../../$i %{buildroot}/%{_includedir}/%{name}-private/generic ;
  done
)

# fix config script
sed -i -e "s|$(pwd)/unix|%{_libdir}|; s|$(pwd)|%{_includedir}/%{name}-private|" %{buildroot}%{_libdir}/%{name}Config.sh

# and let it be found (we don't look in /usr/lib any more)
ln -s %{_libdir}/%{name}Config.sh %{buildroot}/%{_libdir}/%{name}%{major}/%{name}Config.sh

# Arrangements for lib64 platforms
if [ "%{_lib}" != "lib" ]; then
    mkdir -p %{buildroot}%{_prefix}/lib
    ln -s %{_libdir}/tkConfig.sh %{buildroot}%{_prefix}/lib/tkConfig.sh
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

%files -n %{libname}
%{_libdir}/lib*%{major}.so.0*

%files -n %{develname}
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
%if "%{_libdir}" != "%{_prefix}/lib"
%{_prefix}/lib/tkConfig.sh
%endif
%{_libdir}/pkgconfig/*.pc
