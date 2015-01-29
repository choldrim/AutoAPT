#!/usr/bin/env python
# coding=utf-8

import apt
import apt_pkg


class CheckCompleteVitualPkg():
    def __init__(self):
        self.apt_cache = apt.Cache()
        self.pkg_cache = apt_pkg.Cache()

    def work(self):
        pkgs_set = set()
        count = 0
        for pkg in self.pkg_cache.packages:
            if pkg.get_fullname() not in self.apt_cache:
                print(pkg.get_fullname())
                dep_list = pkg.rev_depends_list
                for dep in dep_list:
                    count = count + 1
                    pkgs_set.add(dep.parent_pkg.get_fullname())
                
        print ("count:", count)
        print (len(pkgs_set))

        with open("complete.txt", "w+") as f:
            for pname in pkgs_set:
                f.write(pname + "\n")
                

if __name__ == "__main__":
    ccv = CheckCompleteVitualPkg()
    ccv.work()


