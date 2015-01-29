#!/usr/bin/env python
# coding=utf-8

import apt
import apt_pkg


class CheckBroken():

    def __init__(self):
        self.apt_cache = apt.Cache()
        self.pkg_cache = apt_pkg.Cache()
        self.work()

    def work(self):
        pkg = self.pkg_cache["wput"]
        conflicts_list = self.get_all_conflicts_list(pkg)
        print(conflicts_list)

    def get_all_conflicts_list(self, pkg):
        conflicts_list = []
        for ver in pkg.version_list:
            conf_break_replace = []
            if "Conflicts" in ver.depends_list:
                conf_break_replace += ver.depends_list["Conflicts"]
            if "Breaks" in ver.depends_list:
                conf_break_replace += ver.depends_list["Breaks"]
            if "Replaces" in ver.depends_list:
                conf_break_replace += ver.depends_list["Replaces"]

            for dep in conf_break_replace:
                target_pkg = dep[0].target_pkg
                conflicts_list.append(target_pkg)
                conflicts_list = conflicts_list + \
                    self.get_rev_depends_list(target_pkg)
        return conflicts_list

    def get_rev_depends_list(self, pkg):
        rev_depends = [pkg, ]
        for dep in pkg.rev_depends_list:
            if dep.dep_type == "Depends":
                rev_depends.append(dep.parent_pkg)
                rev_depends.append(self.get_rev_depends_list(dep.parent_pkg))
        return rev_depends

if __name__ == "__main__":
    cb = CheckBroken()
