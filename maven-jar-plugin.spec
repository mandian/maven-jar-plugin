#{?_javapackages_macros:%_javapackages_macros}

# Bootstrap2 builds this plugin from source, but uses binary
# downloads of various libraries used by it that often need
# to be built with maven.  Refer to the package-dependencies
# script to see where the binaries come from.
%bcond_without bootstrap2

%{?!_javadir:%global _javadir %{_datadir}/java}

Summary:	Maven JAR Plugin
Name:		maven-jar-plugin
Version:	3.3.0
Release:	1
License:	ASL 2.0
Group:		Development/Java
URL:		https://maven.apache.org/plugins/maven-jar-plugin/
Source0:	https://archive.apache.org/dist/maven/plugins/%{name}/%{version}/%{name}-%{version}-source-release.zip
%if %{with bootstrap2}
# Generated from Source1000
Source3:	%{name}-dependencies-%{version}.tar.zst
Source1000:	maven-package-dependencies.sh
%endif

# Some classes from maven-artifact come in maven-core, added a dep in pom.xml
#Patch0:	 %{name}-maven-core-dep.patch

BuildRequires:	javapackages-tools
BuildRequires:	jdk-current

%if ! %{with bootstrap2}
BuildRequires:	maven-local
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(org.apache.maven.plugin-testing:maven-plugin-testing-harness)
BuildRequires:	mvn(org.apache.maven.plugin-tools:maven-plugin-annotations)
BuildRequires:	mvn(org.apache.maven.plugins:maven-plugin-plugin)
BuildRequires:	mvn(org.apache.maven.plugins:maven-plugins:pom:)
BuildRequires:	mvn(org.apache.maven.shared:file-management)
BuildRequires:	mvn(org.apache.maven:maven-archiver)
BuildRequires:	mvn(org.apache.maven:maven-artifact)
BuildRequires:	mvn(org.apache.maven:maven-compat)
BuildRequires:	mvn(org.apache.maven:maven-core)
BuildRequires:	mvn(org.apache.maven:maven-model)
BuildRequires:	mvn(org.apache.maven:maven-plugin-api)
BuildRequires:	mvn(org.codehaus.plexus:plexus-utils)
%endif

#Provides:	maven2-plugin-jar = %{version}-%{release}
#Obsoletes:	maven2-plugin-jar <= 0:2.0.8

BuildArch: noarch

%description
Builds a Java Archive (JAR) file from the compiled
project classes and resources.

%files -f .mfiles
%doc LICENSE NOTICE

#-----------------------------------------------------------------------

%if ! %{with bootstrap2}
%package javadoc
Summary:	Javadoc for %{name}
Requires:	jpackage-utils

%description javadoc
API documentation for %{name}.

%files javadoc
%doc LICENSE NOTICE
%{_javadocdir}/%{name}
%endif

#-----------------------------------------------------------------------

%prep
%autosetup -p1

%if %{with bootstrap2}
cd ..
tar xf %{S:3}
cd -
%endif

# System version of maven-jar-plugin should be used, not reactor version
%if ! %{with bootstrap2}
%pom_xpath_inject pom:pluginManagement/pom:plugins "<plugin><artifactId>maven-jar-plugin</artifactId><version>SYSTEM</version></plugin>"
%endif

%build
%if ! %{with bootstrap2}
%mvn_build
# -- -Dproject.build.sourceEncoding=UTF-8
%else
. %{_sysconfdir}/profile.d/90java.sh
#mvn_build -- -Dmaven.repo.local=$(pwd)/../repository
mvn -o -Dmaven.repo.local=$(pwd)/../repository -Dproject.build.sourceEncoding=UTF-8 compile
mvn -o -Dmaven.repo.local=$(pwd)/../repository -Dproject.build.sourceEncoding=UTF-8 verify
mvn -o -Dmaven.repo.local=$(pwd)/../repository -Dproject.build.sourceEncoding=UTF-8 validate
%endif

%install
%if ! %{with bootstrap2}
%mvn_install
%else
. %{_sysconfdir}/profile.d/90java.sh
rm -f .mfiles
#mvn -o -Dmaven.repo.local=$(pwd)/../repository -Dproject.build.sourceEncoding=UTF-8 install

# jar
install -dm 0755 %{buildroot}%{_javadir}/%{name}/
install -pm 0644 target/%{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}/%{name}.jar
echo "%{_javadir}/%{name}/%{name}.jar" >> .mfiles

# pom
install -dm 0755 %{buildroot}%{_datadir}/maven-poms/%{name}/
install -pm 0644 pom.xml %{buildroot}%{_datadir}/maven-poms/%{name}/%{name}.pom
echo "%{_datadir}/maven-poms/%{name}/%{name}.pom" >> .mfiles

# metadata
install -dm 0755 %{buildroot}%{_datadir}/maven-metadata/
python /usr/share/java-utils/maven_depmap.py \
	%{buildroot}%{_datadir}/maven-metadata/%{name}.xml \
	%{buildroot}%{_datadir}/maven-poms/%{name}/%{name}.pom \
	%{buildroot}%{_javadir}/%{name}/%{name}.jar
#install -pm 0644 pom.xml %{buildroot}%{_datadir}/maven-metadata/%{name}.xml
echo "%{_datadir}/maven-metadata/%{name}.xml" >> .mfiles
%endif

