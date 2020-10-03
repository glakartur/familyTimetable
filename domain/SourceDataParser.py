#!/usr/bin/env python

from domain.Timeline import Timeline

class SourceDataParser:
    def __init__(self, fileName):
        self.timetable = {}
        self.days = []
        self.persons = []
        self.colors = {}
        self.subs = []

        with open(fileName, encoding="utf-8", mode="rt") as f:
            fileData = f.readlines()
            self._findColors(fileData)
            self._fillTimetable(fileData)
            self._findSubs(fileData)
        

    def loadTimetable(self):
        return self.timetable

    def getColors(self):
        return self.colors

    def getPersons(self):
        return self.persons

    def printAll(self):
        print(self.days)
        print(self.persons)
        print(self.colors)
        print(self.subs)

    def _lookForDay(self, line):
        if line[0:2] != "# ":
            return None
            
        day = line[2:].strip()
        if day not in self.days:
            self.days.append(day)

        return day

    def _lookForPerson(self, line):
        if line[0:3] != "## ":
            return None
        
        person = line[3:].strip()
        if person not in self.persons:
            self.persons.append(person)

        return person

    def _lookForTimeline(self, line):
        if line[0:2] != "* ":
            return None
        
        return line[2:]

    def _findDays(self, data):
        days = []
        for line in data:
            if line[0:2] != "# ":
                continue
            
            day = line[2:].strip()
            if day in days:
                continue
            days.append(day)

        self.days = days

    def _findPersons(self, data):
        persons = []
        for line in data:
            if line[0:3] != "## ":
                continue
            
            person = line[3:].strip()
            if person in persons:
                continue
            persons.append(person)
        self.persons = persons

    def _findColors(self, data):
        inBlock = False
        colors = {}
        for line in data:
            if line.strip() == "---" and line.startswith("-"):
                inBlock = not inBlock
                continue

            if line.startswith("h2."):
                person = line[3:line.find(":")].strip()
                color = line[line.find(":") + 1:].strip()

                colors[person] = color
        self.colors = colors

    def _findSubs(self, data):
        subs = []
        for line in data:
            if line.startswith("###### /"):
                sub = line[6:].strip()
                subs.append(sub)
        self.subs = subs

    def _fillTimetable(self, data):
        currentDay = None
        currentPerson = None

        for line in data:
            lineDay = self._lookForDay(line)
            if (lineDay):
                currentDay = lineDay
                currentPerson = None
                self.timetable[currentDay] = {}
                continue

            linePerson = self._lookForPerson(line)
            if (linePerson):
                currentPerson = linePerson
                self.timetable[currentDay][currentPerson] = []
                continue

            lineTimeline = self._lookForTimeline(line)
            if (lineTimeline):
                entry = Timeline(lineTimeline)
                self.timetable[currentDay][currentPerson].append(entry)
                
            if (line.startswith("---")):
                currentDay = None
                currentPerson = None


if __name__ == "__main__":
    pass