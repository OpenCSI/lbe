# -*- coding: utf-8 -*-
print "checking for dependencies ..."
print "............................."
error = False

# Django
print "Django:",
try:
    import django
    if "1.4.6" <= django.get_version():
        print "         \033[92myes\033[0m (" + django.get_version() + ')'
    else:
        error = True
        print "         \033[91mno\033[0m (your version is outdated. Install the latest stable version for LBE)"
except BaseException:
    error = True
    print "         \033[91mno\033[0m (pip install Django)"

# South Migration
print "South migration:",
try:
    import south
    print "\033[92myes\033[0m"
except BaseException:
    error = True
    print "\033[91mno\033[0m (pip install south)"

# Mysql
print "Mysql:",
try:
    import _mysql
    print "          \033[92myes\033[0m"
except BaseException:
    error = True
    print "          \033[91mno\033[0m (pip install mysql-python)"

# Ldap
print "Ldap:",
try:
    import ldap
    print "           \033[92myes\033[0m"
except BaseException:
    error = True
    print "           \033[91mno\033[0m (pip install python-ldap)"

# MongoDB
print "MongoDB:",
try:
    import pymongo
    print "        \033[92myes\033[0m"
except BaseException:
    error = True
    print "        \033[91mno\033[0m (pip install pymongo)"

print "............................."
if not error:
    print "STATUS: \033[92mYou can launch LBE.\033[0m"
else:
    print "STATUS: \033[91mYou have errors by checking dependencies, please install them () before launching LBE.\033[0m"