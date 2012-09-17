#!/usr/bin/env python
import os
import sys
# avoid problem for encoding to utf-8.
reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lbe.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
