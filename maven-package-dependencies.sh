#!/bin/sh
# Needed for second stage bootstrapping (first stage bootstrap is installing
# from the binary package): This script builds maven in online mode, creating
# a local repository with all the dependencies (including those that need to
# be built with maven).
#
# (c) 2020 Bernhard Rosenkraenzer <bero@lindev.ch>
# Released under the terms of the GPLv3
set -e
cd "`dirname $0`"
VERSION="`grep Version maven-jar-plugin.spec |cut -d: -f2- |xargs echo`"
MAJOR="`echo $VERSION |cut -d. -f1`"
[ -e maven-jar-plugin-$VERSION-source-release-src.zip ] || wget https://archive.apache.org/dist/maven/plugins/maven-jar-plugin-$VERSION-source-release.zip

unzip maven-jar-plugin-$VERSION-source-release.zip
rm -rf repository
export REPO=`pwd`/repository
cd maven-jar-plugin-$VERSION
mvn -Dmaven.repo.local=$REPO compile
mvn -Dmaven.repo.local=$REPO verify
mvn -Dmaven.repo.local=$REPO validate
mvn -Dmaven.repo.local=$REPO package
mvn -Dmaven.repo.local=$REPO install
mvn -Dmaven.repo.local=$REPO clean
# Let's download a plugin we want by pretending to use it (allowing to fail
# because we pass invalid parameters, given we don't actually want to install
# anything yet)
# Current version number can be found at
# https://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-install-plugin/
mvn -Dmaven.repo.local=$REPO org.apache.maven.plugins:maven-install-plugin:3.1.1:install-file || :
# Just to make sure we actually have everything
# (-o is offline mode)
mvn -o -Dmaven.repo.local=$REPO compile
mvn -o -Dmaven.repo.local=$REPO verify
mvn -o -Dmaven.repo.local=$REPO validate
mvn -o -Dmaven.repo.local=$REPO package
mvn -o -Dmaven.repo.local=$REPO install
mvn -o -Dmaven.repo.local=$REPO clean
mvn -o -Dmaven.repo.local=$REPO verify
cd ..
find repository
tar cf maven-jar-plugin-dependencies-$VERSION.tar repository
zstd --ultra -22 --rm -f maven-jar-plugin-dependencies-$VERSION.tar
rm -rf repository maven-jar-plugin-$VERSION

