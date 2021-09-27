#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from domain.timeline import Timeline
from domain.pdf_printer import PDFPrinter
from domain.source_data_parser import SourceDataParser

class main:
    def __init__(self):
        self.sourceFile = None
        self.destinationFile = None
        self.persons = []
        self.filter = []

    def process(self):
        self.readArgs()

        print ()
        print ("Source:", self.sourceFile)
        print ("Destination:", self.destinationFile)
        print ()
        print ("Processing...")

        reader = SourceDataParser(self.sourceFile)
        timetable = reader.loadTimetable()

        resultBuilder = PDFPrinter()

        for name, color in reader.getColors().items():
            resultBuilder.defineColor(name, color)
        
        if (len(self.filter) > 0):
            reader.filterPersons(self.filter)

        resultBuilder.printHeader(reader.getPersons())
        resultBuilder.printTimetable(timetable)
        resultBuilder.printNotes(reader.subs)

        resultBuilder.save(self.destinationFile)

        print ()
        print ("Done.")
        print ()


    def readArgs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--filter-persons", help="filters source persons", required=False)
        parser.add_argument("source", help="source data file (*.md)")
        parser.add_argument("destination", help="destination file (*.pdf)")

        # parser.print_help()    

        args = parser.parse_args()

        self.sourceFile = args.source
        self.destinationFile = args.destination
        if (args.filter_persons != None and len(args.filter_persons) > 0):
            self.filter = args.filter_persons.split(',')

        parser.print_help() 

if __name__ == "__main__":
    main().process()
