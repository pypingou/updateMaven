#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#
# Copyright 2012 Pierre-Yves Chibon <pingou@pingoured.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
# This program parses the html at the page [1], retrieves the name of the 
# package and their version.
# Then for each package it checks the version present in Fedora using the
# information available at [2].
# 
# Output looks like:
#  * maven-install-plugin is not up to date upstream: 2.3.1, Fedora: 2.3-7.fc14
#  * maven-jar-plugin is not up to date upstream: 2.3.1, Fedora: 2.3-3.fc14
#  * maven-repository-plugin is not up to date upstream: 2.3.1, Fedora: 2.3-2.fc14
#
# [1] http://svn.apache.org/repos/asf/maven/plugins/tags/
# [2] http://localhost/rpmphp/
#

if __name__ == "__main__":
    
    import urllib, re, json
    
    url = "http://svn.apache.org/repos/asf/maven/plugins/tags/"
    rpmphpurl = "http://rpms.famillecollet.com/rpmphp/zoom.php?"
    #rpmphpurl = "http://localhost/rpmphp/zoom.php?"
    
    f = urllib.urlopen(url)
    maven = f.read()
    packages = {}
    for line in maven.split("\n"):
        if "href" in line and "maven" in line:
            line = line.split('href="')[1]
            line = line.split('/')[0]
            pattern = re.match("(?P<name>[\w-]*)-(?P<version>[\.\d]+)-?(?P<extension>.*]?)", line)
            name = pattern.group("name")
            vers = pattern.group("version")
            exten = pattern.group("extension")
            if name in packages.keys():
                if vers >= packages[name][0]:
                    packages[name] = [vers, exten]
            else:
                packages[name] = [vers, exten]
            
    names = packages.keys()
    names.sort()
    for name in names:
        params = urllib.urlencode({'rpm': name, 'type': "json"})
        f = urllib.urlopen(rpmphpurl + params )
        rpm = f.read()
        if not "not found" in rpm:
            try:
               info = json.loads(rpm)
               for branch in info['branch']:
                   if 'devel' in branch.keys():
                       fvers = branch['devel']
               if fvers.split('-')[0] != packages[name][0]:
                   print "* %s is not up to date upstream: %s, Fedora: %s" %(
                   name, packages[name][0], fvers)
            except ValueError, ex:
               print ex, f, rpmphpurl + params

