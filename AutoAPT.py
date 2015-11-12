#!/usr/bin/env python

import apt
import apt_pkg
import platform
from optparse import OptionParser

class AutoAPT(object):
    """AutoAPT: a series of auto tests for package system"""

    def __init__(self):
        super(AutoAPT, self).__init__()

        (work_mode, with_filter) = self.usage()

        self.work_mode_map = {
            "CHECK_BROKEN": self.check_broken,
            "CHECK_INST_FILES": self.check_inst_files,
            "USAGE":self.usage,
        }

        # system platform
        self.pkg_arch = self.get_pkg_architecture()

        # construct cache
        self.pkg_cache = apt_pkg.Cache()
        self.apt_cache = apt.cache.Cache()

        # construct file filters
        self.file_filter = ["Deepin",]

        # if just check the pkgs in included by file_filter
        self.with_filter = with_filter
        self.filter_filenames = self.get_filter_filenames()

        # construct record files
        record_file_path = "record.rd"
        self.record_file = open(record_file_path, "w")

        # construct handle method
        self.work_mode_handler = self.work_mode_map.get(work_mode, self.usage)
        # run
        self.work_mode_handler()

    def get_pkg_architecture(self):
        sys_pf = platform.architecture()
        if sys_pf[0] == "64bit":
            return "amd64"
        elif sys_pf[0] == "32bit":
            return "i386"
        else:
            print "Unknow system platform.\n %s"%sys_pf[0]
            quit()

    def get_filter_filenames(self):
        pkg_file_list = []
        all_pkg_file_list = self.pkg_cache.file_list
        for pkg_file in all_pkg_file_list:
            if pkg_file.label in self.file_filter:
                pkg_file_list.append(pkg_file.filename)

        return pkg_file_list

    def package_filter(self, pkg_package):
        """
        package filter:
            return True: the package met the the filter conditions
            otherwise return False.

            check range:
            1, package file label should be included by file_filter
            2, it should be an not-installed package
        """
        version_list = pkg_package.version_list

        # get pkg version
        version = version_list[0]
        file_list = version.file_list

        # filter(ignore) the installed packages
        for f in file_list:
            if f[0].filename == "/var/lib/dpkg/status":
                return False

        # filter(ignore) the mismatching architecture packages
        if pkg_package.architecture != self.pkg_arch:
            return False

        # filter the package file
        file_name = file_list[0][0].filename
        if file_name in self.filter_filenames:
            return True

        return False

    def usage(self, **args):
        parser = OptionParser()
        parser.add_option("-m", metavar="[cb|cf] ", dest="check_mode", help="CHECK_MODE cb: check broken package. cf: check installed files of debs", type="string", action="store")

        parser.add_option("-f", dest="with_filter", action="store_true",help="filter packages")
        (options, args) = parser.parse_args()

        mode = None
        arg_mode = options.check_mode
        if arg_mode == "cb":
            mode = "CHECK_BROKEN"
        elif arg_mode == "cf":
            mode = "CHECK_INST_FILES"

        with_filter = options.with_filter
        if None in (mode, with_filter):
            parser.print_help()
            quit()

        return mode, with_filter


    def check_complete_virtual(self, pkg):
        if pkg.get_fullname() not in self.apt_cache:
            # meet a complete virtual pkg
            return False

        depend_list = self.get_all_dependency_list(pkg)
        for dep in depend_list:
            if len(dep.all_targets()) == 0:
                return False

        return True

    def get_all_dependency_list(self, pkg):
        depend_list = []
        for ver in pkg.version_list:
            for depends in ver.depends_list.values():
                for depend in depends:
                    depend_list.append(depend[0])

        return depend_list


    def check_broken(self):
        # all packages
        packages = self.pkg_cache.packages

        for p in packages:
            pkg_name = ""
            if self.pkg_arch == "i386":
                pkg_name = p.name
            else:
                pkg_name = p.get_fullname()

            #print "\npackage: %s"%pkg_name

            try:
                # get package
                if pkg_name not in self.apt_cache:
                    continue

                package = self.apt_cache[pkg_name]

                if self.with_filter:
                    if not self.package_filter(p):
                        #print "Not in the detection range, skip"
                        continue
                    else:
                        pass
                        #print "package: %s " %pkg_name
                        #quit()

                # get package name
                pkg_name = package.fullname

                # ckeck broken
                package.mark_install()

                #print "package: %s, through"%pkg_name

            except SystemError, e:
                print  "\n*** Package: %s not through *** \n error:[%s]" %(pkg_name, str(e))
                print self.apt_cache.broken_count
                if self.apt_cache.broken_count != 0:
                    self.record(pkg_name, str(e))
                    self.apt_cache.clear()

    def check_inst_files(self):
        print "check_installed_files"
        quit()

    def record(self, pkg_name, err):
        write_str = "Package: %s\nErrorInfo: %s\n\n" %(pkg_name, err)
        self.record_file.write(write_str)


if __name__ == '__main__':
    at = AutoAPT()
