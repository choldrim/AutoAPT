#!/usr/bin/env python
# coding=utf-8

import apt
import apt_pkg

class CheckBroken():
    def __init__(self):
        self.apt_cache = apt.Cache()
        self.pkg_cache = apt_pkg.Cache()

    def work(self, pkg):
        pass


    def get_all_conflicts_list(self, pkg):
        conflicts_list = []
        for ver in pkg.version_list:
            for depends in ver.depends_list.values():
                for depend in depends:
                    conflicts_list.append(depend[0])
        return depend_list

    def get_rev_depends_list(self, pkg):
        rev_depends = [pkg, ]
        for dep in pkg.rev_depends_list:
            rev_depends.append(dep.parent_pkg)
            rev_depends.append(self.get_rev_depends_list(dep.parent_pkg))
        return rev_depends
