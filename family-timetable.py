#!/usr/bin/env python

import argparse
from domain.SourceDataParser import SourceDataParser
from domain.PDFPrinter import PDFPrinter
from domain.Timeline import Timeline

class main:
    def __init__(self):
        self.sourceFile = None
        self.destinationFile = None
        self.persons = []

    def process(self):
        self.readArgs()

        print ("Source:", self.sourceFile)
        print ("Destination", self.destinationFile)
        print ()
        print ("Processing...")

        reader = SourceDataParser(self.sourceFile)
        timetable = reader.loadTimetable()

        resultBuilder = PDFPrinter()

        for name, color in reader.getColors().items():
            resultBuilder.defineColor(name, color)
        
        resultBuilder.printHeader(reader.getPersons())
        resultBuilder.printTimetable(timetable)
        resultBuilder.printNotes(reader.subs)

        resultBuilder.save(self.destinationFile)


    def readArgs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("source", help="source data file (*.md)")
        parser.add_argument("destination", help="destination file (*.pdf)")

        # parser.print_help()    

        args = parser.parse_args()
        self.sourceFile = args.source
        self.destinationFile = args.destination

if __name__ == "__main__":
    main().process()
