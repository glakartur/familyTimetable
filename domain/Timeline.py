#!/usr/bin/env python

class Timeline:
    def __init__(self, text):
        self.mode = None
        self.kind = 'N'
        self.fromTime = None
        self.toTime = None
        self.name = None

        if (text):
            self.parse(text)

    def parse(self, text):
        text = text.strip()
        if (text.startswith("? ")):
            self.mode = text[0:text.find(" ")].strip()
            text = text[text.find(" ") + 1:].strip()
        if (text.startswith("[")):
            self.kind = text[1:text.find("]")].strip()
            text = text[text.find("]") + 1:].strip()
        self.fromTime = text[0:text.find("-")].strip()
        text = text[text.find("-") + 1:].strip()
        if (text.find(" ") > 0):
            self.toTime = text[0:text.find(" ")].strip()
            self.name = text[text.find(" "):].strip()
        else:
            self.toTime = text.strip()
            self.name = None



if __name__ == "__main__":
    pass