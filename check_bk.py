#!/usr/bin/env python
# coding=utf-8

import apt
import apt_pkg


class CheckBroken():

    def __init__(self):
        self.apt_cache = apt.Cache()
        self.pkg_cache = apt_pkg.Cache()
        self.work()

    def init_sys(self):
        self.apt_cache = apt.Cache()
        self.pkg_cache = apt_pkg.Cache()

    def work(self):
        pkg_index = 0
        confirm = False
        #for pkg in self.pkg_cache.packages:
        while True:
            pkg = self.pkg_cache.packages[pkg_index]
            print(pkg.get_fullname())
            depcache = apt_pkg.DepCache(self.pkg_cache)
            depcache.mark_install(pkg)
            conflicts_ver_list = self.get_all_conflicts_ver_list(pkg)
            for ver in conflicts_ver_list:
                if depcache.is_auto_installed(ver.parent_pkg):
                    if confirm:
                        print("\nCatch broken pkg:\n %s\n\nbecause the follow marked-auto-install pkg, but it is a conflicted pkg:\n %s\n."%(pkg.get_fullname(), ver.parent_pkg.get_fullname()))
                        quit()
                    else:
                        print("need to confirm...")
                        self.init_sys()
                        confirm = True
                        continue
            confirm = False
            pkg_index += 1
        print("\nfinish CheckBroken!")

    def get_all_conflicts_ver_list(self, pkg):
        conflicts_ver_list = []
        for ver in pkg.version_list:
            conf_break_replace = []
            if "Conflicts" in ver.depends_list:
                conf_break_replace += ver.depends_list["Conflicts"]
            if "Breaks" in ver.depends_list:
                conf_break_replace += ver.depends_list["Breaks"]
            if "Replaces" in ver.depends_list:
                conf_break_replace += ver.depends_list["Replaces"]

            for dep in conf_break_replace:
                targets = dep[0].all_targets()  # get satisfied versions
                for target_ver in targets:
                    conflicts_ver_list += self.get_rev_depends_ver_list(target_ver)
        return conflicts_ver_list

    def get_rev_depends_ver_list(self, ver):
        rev_ver_depends = [ver, ]
        pointer = 0
        while True:
            if pointer >= len(rev_ver_depends):
                break
            ver = rev_ver_depends[pointer]
            for dep in ver.parent_pkg.rev_depends_list:
                if dep.dep_type == "Depends" and \
                   not self.check_ver_exit(rev_ver_depends, dep.parent_ver):
                    rev_ver_depends.append(dep.parent_ver)
                    print("===", dep.parent_ver.parent_pkg.get_fullname())
            pointer += 1
            if pointer > 1000:
                print("rev-depends may be wrong.")
                break
        return rev_ver_depends

        for dep in ver.parent_pkg.rev_depends_list:
            if dep.dep_type == "Depends":
                rev_ver_depends.append(dep.parent_ver)
                rev_ver_depends += self.get_rev_depends_ver_list(dep.parent_ver)
        return rev_ver_depends

    def check_ver_exit(self, ver_list, ver):
        for v in ver_list:
            if v.parent_pkg.get_fullname() == ver.parent_pkg.get_fullname() and \
               v.parent_pkg.architecture == ver.parent_pkg.architecture and \
               v.ver_str == ver.ver_str:
                return True
        return False


if __name__ == "__main__":
    cb = CheckBroken()
