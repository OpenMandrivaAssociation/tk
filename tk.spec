%define major %(echo %{version} |cut -d. -f1-2)
%define oldlibname %mklibname %{name} %{major}
%define libname %mklibname %{name}
%define devname %mklibname %{name} -d


%define dirname_ %{name}%(echo %{version}|cut -d. -f1-3)

Summary:	GUI toolkit for Tcl
Name:		tk
Version:	8.6.12
Release:	1
License:	BSD
Group:		System/Libraries
URL:		https://tcl.tk
Source0:        https://downloads.sourceforge.net/tcl/%{name}%{version}-src.tar.gz
Source1:	icons.tcl
Source2:	tk.rpmlintrc
Patch0:		https://src.fedoraproject.org/rpms/tk/raw/rawhide/f/tk-8.6.12-make.patch
Patch1:		https://src.fedoraproject.org/rpms/tk/raw/rawhide/f/tk-8.6.12-conf.patch
# # https://core.tcl-lang.org/tk/tktview/dccd82bdc70dc25bb6709a6c14880a92104dda43
Patch3:		https://src.fedoraproject.org/rpms/tk/raw/rawhide/f/tk-8.6.10-font-sizes-fix.patch
Patch4:		tk8.6b1-fix_Xft_linkage.patch
Requires:	%{libname} = %{EVRD}
BuildRequires:	tcl-devel >= %(echo %{version} |cut -d. -f1-3)
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

%files
%{_bindir}/wish*
%{_libdir}/%{name}%{major}
%{_datadir}/%{name}%{major}
%exclude %{_datadir}/%{name}%{major}/tkAppInit.c
%{_mandir}/man1/*
%{_mandir}/mann/*

#--------------------------------------------------------------------

%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries
Obsoletes:	%{oldlibname} < %{EVRD}

%description -n %{libname}
Tk is a X Windows widget set designed to work closely with the tcl
scripting language. It allows you to write simple programs with full
featured GUI's in only a little more time then it takes to write a
text based interface. Tcl/Tk applications can also be run on Windows
and Macintosh platforms.

%files -n %{libname}
%{_libdir}/lib*%{major}.so

#--------------------------------------------------------------------

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	pkgconfig(x11)
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
This package contains development files for %{name}.

%files -n %{devname}
%{_includedir}/*.h
%dir %{_includedir}/tk-private
%{_includedir}/tk-private/*
%{_libdir}/libtk.so
%{_libdir}/*.a
%{_libdir}/tkConfig.sh
%if "%{_libdir}" != "%{_prefix}/lib"
%{_prefix}/lib/tkConfig.sh
%endif
%{_libdir}/pkgconfig/*.pc
%{_datadir}/%{name}%{major}/tkAppInit.c
%{_mandir}/man3/*

#--------------------------------------------------------------------

%prep
%autosetup -p1 -n %{name}%{version}

# Replace native icons.tcl - it contains  PNG data
# obtained using old libpng and has problems with new libpng
# The new one contains PNG data created using
# new libpng
cp -f %{SOURCE1} library

%build
pushd unix
%config_update
autoconf
%configure \
	--enable-threads \
%ifnarch %{ix86}
	--enable-64bit \
%endif
	--disable-rpath \
	--with-tcl=%{_libdir}

%make_build CFLAGS="%{optflags}" TK_LIBRARY="%{_datadir}/%{name}%{major}"
popd

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

# for linking with -l%%{name}
ln -s lib%{name}%{major}.so %{buildroot}%{_libdir}/lib%{name}.so

mkdir -p %{buildroot}%{_includedir}/%{name}-private/{generic/ttk,unix}
find generic unix -name "*.h" -exec cp -p '{}' %{buildroot}%{_includedir}/%{name}-private/'{}' ';'
( cd %{buildroot}/%{_includedir}
  for i in $(ls -1 *.h) ; do
    [ -f %{buildroot}%{_includedir}/%{name}-private/generic/$i ] && ln -sf ../../$i %{buildroot}%{_includedir}/%{name}-private/generic ;
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
chrpath -d %{buildroot}%{_libdir}/libtk%{major}.so

