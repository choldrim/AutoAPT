#!/usr/bin/env python
# coding=utf-8

import apt
import apt_pkg
import sqlite3

class AutoSoftwareCenter(object):
    """
    AutoSoftwareCenter
       Auto check the package sync between software center and official base
        this must be run in a machine with a official source_list
    """

    def __init__(self):
        self.apt_cache = apt.cache.Cache()
        self.pkg_cache = apt_pkg.Cache()
        self.databases = {"desktop2014.db":("package",), "software.db":("software",)}
        self.recordFile = open("deepin-software-center_missed_pkgs.rd", "w")
        self.unmetPkgs = set()

    def check_database(self):
        for dbName in self.databases:
            conn = sqlite3.connect(dbName)
            cursor = conn.cursor()
            for tableName in self.databases[dbName]:
                sql = "select pkg_name from %s;"%tableName
                cursor.execute(sql)
                pkgNames = cursor.fetchall()
                print len(pkgNames)
                for pkgName in pkgNames:
                    pkgName = pkgName[0]
                    if pkgName not in self.apt_cache:
                        # check if there is 32bit pkg
                        if not pkgName.endswith(":i386"):
                            if pkgName + ":i386" in self.apt_cache:
                                continue
                        print pkgName
                        self.unmetPkgs.add(pkgName)
        for name in self.unmetPkgs:
            self.record(name)
        self.recordFile.close()
        

    def record(self, pkgName):
        data = "%s\n"%pkgName
        self.recordFile.write(data)
       
if __name__ == "__main__":
    asc = AutoSoftwareCenter()
    asc.check_database()

