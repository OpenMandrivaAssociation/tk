%define major %(echo %{version} |cut -d. -f1-2)
%define oldlibname %mklibname %{name} %{major}
%define libname %mklibname %{name}
%define devname %mklibname %{name} -d


%define dirname_ %{name}%(echo %{version}|cut -d. -f1-3)

Summary:	GUI toolkit for Tcl
Name:		tk
Version:	9.0.3
Release:	2
License:	BSD
Group:		System/Libraries
URL:		https://tcl.tk
Source0:        https://downloads.sourceforge.net/tcl/%{name}%{version}-src.tar.gz
Source1:	icons.tcl
Source2:	tk.rpmlintrc
Patch1:		https://src.fedoraproject.org/rpms/tk/raw/rawhide/f/tk-8.6.15-conf.patch
# Fixes gitk screaming about tk::svgFmt being undefined
Patch2:		tk-9.0.2-tk-svgFmt.patch
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
%{_datadir}/tk%{major}
%{_libdir}/%{name}%{major}
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
%{_libdir}/tkConfig.sh
%{_libdir}/libtk.so
%{_libdir}/*.a
%{_libdir}/pkgconfig/*.pc
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
	--disable-zipfs

# ^^^ --disable-zipfs is because including zipfs omits the
# expected files in %{_datadir}/%{name}%{major}

%make_build CFLAGS="%{optflags}" TK_LIBRARY="%{_datadir}/%{name}%{major}"
popd

%install
make install -C unix INSTALL_ROOT=%{buildroot} TK_LIBRARY=%{_datadir}/%{name}%{major}

ln -s wish%{major} %{buildroot}%{_bindir}/wish

# for linking with -l%%{name}
ln -s libtcl9%{name}%{major}.so %{buildroot}%{_libdir}/lib%{name}.so

mkdir -p %{buildroot}/%{_includedir}/%{name}-private/{generic/ttk,unix}
find generic unix -name "*.h" -exec cp -p '{}' %{buildroot}/%{_includedir}/%{name}-private/'{}' ';'
( cd %{buildroot}/%{_includedir}
  for i in *.h ; do
    [ -f %{buildroot}/%{_includedir}/%{name}-private/generic/$i ] && ln -sf ../../$i %{buildroot}/%{_includedir}/%{name}-private/generic ;
  done
)

# remove buildroot traces
sed -i -e "s|$PWD/unix|%{_libdir}|; s|$PWD|%{_includedir}/%{name}-private|" %{buildroot}/%{_libdir}/%{name}Config.sh
