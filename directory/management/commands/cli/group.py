# -*- coding: utf-8 -*-
import django
from directory.models import LBEGroup, LBEScript, LBEObjectTemplate, LBEGroupInstance
from services.group import GroupInstanceHelper


class CLIGroup(object):
    def __init__(self):
        self.group = None
        self.script = None
        self.objectTemplate = None

    def _setGroupName(self):
        while 1:
            self.group.displayName = raw_input("\033[34mEnter a group name:\033[0m ")
            try:
                LBEGroup.objects.get(displayName__iexact=self.group.displayName)
                print "\033[31mThe group name already exists!\033[0m"
            except BaseException:
                if self.group.displayName:
                    return


    def _setObjectTemplate(self):
        objectsTemplate = LBEObjectTemplate.objects.all()
        number = 0
        choice = ''
        for object in objectsTemplate:
            print '(' + str(object.id) + ') ' + object.name
            number += 1
            if number == 10:
                choice = raw_input("\033[34mSelect the ID or enter key to go one:\033[0m ")
                if choice is '':
                    number = 0
                try:
                    choice = int(choice)
                    self.objectTemplate = LBEObjectTemplate.objects.get(id=choice)
                    return
                except BaseException: # not a integer value or non object
                    number = 0
        if not choice.__class__ == int:
            while 1:
                try:
                    choice = int(raw_input("\033[34mEnter the ID Object:\033[0m "))
                    self.objectTemplate = LBEObjectTemplate.objects.get(id=choice)
                    return
                except BaseException:
                    pass

    def _setScript(self):
        scripts = LBEScript.objects.all()
        number = 0
        choice = ''
        for script in scripts:
            print '(' + str(script.id) + ') ' + script.name + ' file: ' + str(script.fileUpload)
            number += 1
            if number == 10:
                choice = raw_input("\033[34mSelect the ID or enter key to go one:\033[0m ")
                if choice is '':
                    number = 0
                try:
                    choice = int(choice)
                    self.script = LBEScript.objects.get(id=choice)
                    return
                except BaseException: # not a integer value or non object
                    number = 0
        if not choice.__class__ == int:
            while 1:
                try:
                    choice = int(raw_input("\033[34mEnter the ID Script:\033[0m "))
                    self.script = LBEScript.objects.get(id=choice)
                    return
                except BaseException:
                    pass

    def viewGroup(self):
        print '  The new Group:'
        print 'Name: ' + self.group.displayName
        print 'Object Reference: ' + self.group.objectTemplate.name
        print 'Script Reference: ' + self.group.script.name

    def create(self):
        print "In order to create a new group, we need some information."
        self.group = LBEGroup()
        self.group.name = "groups"
        self._setGroupName()
        print "---------------------------------------------------------"
        print "Enter the ID of the Object Template:"
        self._setObjectTemplate()
        print "---------------------------------------------------------"
        print "Enter the ID of script for the group:"
        self._setScript()
        print "---------------------------------------------------------"
        print "-                        \033[33mWARNING\033[0m                        -"
        print "---------------------------------------------------------"
        self.group.objectTemplate = self.objectTemplate
        self.group.script = self.script
        self.viewGroup()
        choice = raw_input("Do you want to create the new group? [Y/n]\033[0m")
        if choice == 'n':
            return False
        self.group.synced_at = django.utils.timezone.now()
        groupHelper = GroupInstanceHelper(self.group, LBEGroupInstance(self.group))
        groupHelper.createTemplate()
        self.group.save()
        print "\033[32mGroup Saved!\033[0m"
        return True