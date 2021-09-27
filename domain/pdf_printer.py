#!/usr/bin/env python

import os
from fpdf import FPDF
from .size import Size

class Color:
    WHITE = tuple([255, 255, 255])
    BLACK = tuple([0, 0, 0])
    LIGHT_GREY = tuple([178, 178, 178])

class PDFPrinter:
    PAGE_FORMAT = 'A4'
    UNIT = 'mm'
    MARGIN = 10
    CONTENT_WIDTH = 297 - 2 * MARGIN
    CONTENT_HEIGHT = 210 - 2 * MARGIN
    HEADER_HEIGHT = 30
    NOTES_HEIGHT = 17
    TABLE_HEIGHT = CONTENT_HEIGHT - HEADER_HEIGHT - NOTES_HEIGHT
    FONT_S = 7
    FONT_XS = 6.5

    def __init__(self):
        self.colors = {}
        self.timelinesCount = None
        self.fontSize = 12
        self.textColor = Color.WHITE
        
        self.pdf = FPDF(orientation = 'L', unit = PDFPrinter.UNIT, format = PDFPrinter.PAGE_FORMAT) 
        self.pdf.add_font('regular', '', os.path.join('fonts', 'ubuntu', 'Ubuntu-B.ttf'), uni=True)
        self.pdf.add_font('condensed', '', os.path.join('fonts', 'roboto', 'RobotoCondensed-Regular.ttf'), uni=True)
        self.pdf.add_font('italic', '', os.path.join('fonts', 'roboto', 'RobotoCondensed-Bold.ttf'), uni=True)
        self.pdf.set_font("regular", size = self.fontSize) 
        self.pdf.add_page() 
        self.pdf.set_margins(PDFPrinter.MARGIN, PDFPrinter.MARGIN, PDFPrinter.MARGIN)

        self.uglyMeasure = FPDF(orientation = 'L', unit = PDFPrinter.UNIT, format = PDFPrinter.PAGE_FORMAT) 
        self.uglyMeasure.add_font('regular', '', os.path.join('fonts', 'ubuntu', 'Ubuntu-B.ttf'), uni=True)
        self.uglyMeasure.add_font('condensed', '', os.path.join('fonts', 'roboto', 'RobotoCondensed-Regular.ttf'), uni=True)
        self.uglyMeasure.add_font('italic', '', os.path.join('fonts', 'roboto', 'RobotoCondensed-Bold.ttf'), uni=True)
        self.uglyMeasure.set_font("regular", size = self.fontSize) 
        self.uglyMeasure.add_page() 

    def defineColor(self, key, color):
        hex = color.lstrip('#')
        self.colors[key.lower()] = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

    def printHeader(self, names):
        self.timelinesCount = len(names)
        boxWidth = PDFPrinter.CONTENT_WIDTH / self.timelinesCount

        boxPos = 0
        for name in names:
            color = self.colors[name.lower()]
            x = PDFPrinter.MARGIN + boxWidth * boxPos
            y = PDFPrinter.MARGIN
            w = boxWidth
            h = 7

            self._box(x, y, w, h, color = color, lineColor = Color.BLACK, lineWidth = 0.1)
            self._text(x, y, w, h, text = name, color = self.textColor, font = 'regular', size = self.fontSize)

            boxPos += 1

    def printTimetable(self, timetable):
        colCount = len(timetable.keys())
        colWidth = PDFPrinter.CONTENT_WIDTH / colCount

        tablePositionY = 30
        tableHeight = PDFPrinter.TABLE_HEIGHT + 1
        tableHeaderHeight = 7
        timelineRowHeight = tableHeight - tableHeaderHeight
        timelineRowPositionY = tablePositionY + tableHeaderHeight

        timeBlockWidth = (colWidth - 2) / self.timelinesCount
        timeWindow = self._findTimeWindow(timetable)
        yPerMin = (timelineRowHeight - 2) / (timeWindow["toTime"] - timeWindow["fromTime"])

        colNo = 0
        for key, schedules in timetable.items():
            x = PDFPrinter.MARGIN + colWidth * colNo

            self._box(x = x, y = tablePositionY, w = colWidth, h = tableHeaderHeight, color = Color.LIGHT_GREY, lineColor = Color.BLACK, lineWidth=0.2)
            self._text(x = x, y = tablePositionY, w = colWidth, h = tableHeaderHeight, text = key, color = Color.BLACK, font = 'regular', size = self.fontSize)
            self._box(x = x, y = timelineRowPositionY, w = colWidth, h = timelineRowHeight, color = None, lineColor = Color.BLACK, lineWidth=0.2)

            self._drawTimeblocks(schedules, areaWidth = timeBlockWidth, areaPositionX = x, areaPositionY = timelineRowPositionY + 0.8, 
                    scaleY = yPerMin, timeWindowStart = timeWindow["fromTime"])

            colNo += 1

    def _drawTimeblocks(self, schedules, areaWidth, areaPositionX, areaPositionY, scaleY, timeWindowStart):
        timeBlockNo = 0

        for person, timelines in schedules.items():
            blockColor = self.colors[person.lower()]
            blockPositionX = areaPositionX + areaWidth * timeBlockNo + 0.5 * timeBlockNo + 0.5

            for timeline in timelines:
                fromTimePosY = scaleY * (self._timeToInt(timeline.fromTime) - timeWindowStart) + 0.4
                blockPositionY = areaPositionY + fromTimePosY
                blockHeight = scaleY * (self._timeToInt(timeline.toTime) - timeWindowStart) - fromTimePosY

                self._box(x = blockPositionX, y = blockPositionY, w = areaWidth, h = blockHeight, color = blockColor, lineColor = None)

                if (timeline.kind == "~"):
                    self._drawLeftLines(x = blockPositionX, y = blockPositionY, w = areaWidth, h = blockHeight)
                elif (timeline.kind == "d"):
                    self._drawTwoRightLines(x = blockPositionX, y = blockPositionY, w = areaWidth, h = blockHeight)
                elif (timeline.kind == "e"):
                    self._drawEmptyRightCorner(x = blockPositionX, y = blockPositionY, w = areaWidth, h = blockHeight)
                    

                self._drawTimeblockLabels(areaX = blockPositionX, areaY = blockPositionY, areaW = areaWidth, areaH = blockHeight, 
                    timeline = timeline, backColor = blockColor)

            timeBlockNo += 1

    def _drawLeftLines(self, x, y, w, h):
        hw = h / w

        posX = x
        posXM = x + w
        posY = y
        posYM = y + h
        jump = 3
        while (posXM > x): 
            posX += jump
            posXM -= jump
            posY += jump * hw
            posYM -= jump * hw

            if jump == 2:
                jump = 0.5
            else:
                jump = 2

            if (posX < x + w and posY < y + h):
                self._line(posX, y, x, posY, Color.WHITE, lineWidth = 0.2)
            if (posXM > x and posYM > y):
                self._line(posXM, y + h, x + w, posYM, Color.WHITE, lineWidth = 0.2)


    def _drawTwoRightLines(self, x, y, w, h):
        hw = h / w

        posX = x
        posXM = x + w
        posY = y
        posYM = y + h
        jump = 2
        for _ in range(4): 
            posX += jump
            posXM -= jump
            posY += jump * hw
            posYM -= jump * hw

            # if jump == 2:
            #     jump = 0.7
            # else:
            #     jump = 2

            if (posX < x + w and posY < y + h):
                self._line(posX, y + h, x, posYM, Color.WHITE, lineWidth = 0.3)
            if (posXM > x and posYM > y):
                self._line(posXM, y, x + w, posY, Color.WHITE, lineWidth = 0.3)

    def _drawEmptyRightCorner(self, x, y, w, h):
        hw = h / w

        posX = x
        posXM = x + w
        posY = y
        posYM = y + h
        jump = 1
        for p in range(9): 
            posX += jump
            posXM -= jump
            posY += jump * hw
            posYM -= jump * hw

            if p > 5:
                jump = 1
            else:
                jump = 0.2

            if (posX < x + w and posY < y + h):
                self._line(posX, y + h, x, posYM, Color.WHITE, lineWidth = 0.2)
            if (posXM > x and posYM > y):
                self._line(posXM, y, x + w, posY, Color.WHITE, lineWidth = 0.2)

    def _drawTimeblockLabels(self, areaX, areaY, areaW, areaH, timeline, backColor):
        label = []
        if (timeline.name):
            label.append(timeline.name.upper())
        for component in timeline.components:
            label.append(component.upper())

        if (label):
            self._textBlock(x = areaX, y = areaY, w = areaW, h = areaH, textLines = label, 
                    color = Color.WHITE, font = 'condensed', size = PDFPrinter.FONT_XS, align = 'C', backColor = backColor)
        if (timeline.fromTime):
            textSize = self._measure(text = timeline.fromTime, font = 'italic', size = PDFPrinter.FONT_S)
            self._text(x = areaX, y = areaY - 1, w = areaW / 2, h = textSize.y, text = timeline.fromTime, 
                    color = Color.WHITE, font = 'italic', size = PDFPrinter.FONT_S, align = 'L', backColor = backColor)
        if (timeline.toTime):
            textSize = self._measure(text = timeline.toTime, font = 'italic', size = PDFPrinter.FONT_S)
            self._text(x = areaX + areaW / 2, y = areaY + areaH - textSize.y + 1, w = areaW / 2, h = textSize.y, text = timeline.toTime, 
                    color = Color.WHITE, font = 'italic', size = PDFPrinter.FONT_S, align = 'R', backColor = backColor)

    def printNotes(self, notes):
        x = PDFPrinter.MARGIN
        y = PDFPrinter.MARGIN + PDFPrinter.HEADER_HEIGHT + PDFPrinter.TABLE_HEIGHT
        w = PDFPrinter.CONTENT_WIDTH
        h = 5

        for note in notes:
            y += h
            self._text(x, y, w, 0, text = note, color = Color.BLACK, font = 'regular', size = self.fontSize, align = 'L')

    def save(self, fileName):
        self.pdf.output(fileName)

    def _measure(self, text, font, size):
        self.uglyMeasure.set_font(font, size = size) 
        self.uglyMeasure.set_xy(0, 0)
        self.uglyMeasure.write(size / 2.83 , txt = text)
        sizeX = self.uglyMeasure.get_x()
        self.uglyMeasure.write(size / 2.83 , txt = "\n")
        sizeY = self.uglyMeasure.get_y()
        
        result = Size(sizeX, sizeY)
        return result
        
    def _text(self, x, y, w, h, text, color, font, size, align = 'C', backColor = None):
        self.pdf.set_text_color(color[0], color[1], color[2])
        self.pdf.set_font(font, size = size) 
        self.pdf.set_xy(x, y)
        fillBackground = False
        if (backColor):
            self.pdf.set_fill_color(backColor[0], backColor[1], backColor[2])
            fillBackground = True
        self.pdf.cell(w, h, txt = text, ln = 1, align = align, fill = fillBackground)

    def _textBlock(self, x, y, w, h, textLines, color, font, size, align = 'C', backColor = None):
        textH = 0
        texts = []
        for line in textLines:
            textSize = self._measure(text = line, font = font, size = size)
            textSize.y += 1
            textH += textSize.y

            texts.append({ "txt": line, "height":  textSize.y })

        self.pdf.set_text_color(color[0], color[1], color[2])
        self.pdf.set_font(font, size = size) 

        posY = y + (h - textH) / 2

        fillBackground = False
        if (backColor):
            self.pdf.set_fill_color(backColor[0], backColor[1], backColor[2])
            fillBackground = True

        for line in texts:
            self.pdf.set_xy(x, posY)
            self.pdf.cell(w, line["height"], txt = line["txt"], align = align, fill = fillBackground)

            posY += line["height"]

    def _box(self, x, y, w, h, color, lineColor, lineWidth = 0):
        style = ''

        if (lineColor):
            self.pdf.set_line_width(lineWidth)
            self.pdf.set_draw_color(lineColor[0], lineColor[1], lineColor[2])
            style += 'D'

        if (color):
            self.pdf.set_fill_color(color[0], color[1], color[2])
            style += 'F'

        self.pdf.rect(x, y, w, h, style)

    def _line(self, x1, y1, x2, y2, color, lineWidth):
        self.pdf.set_line_width(lineWidth)
        self.pdf.set_draw_color(color[0], color[1], color[2])

        self.pdf.line(x1, y1, x2, y2)

    def _findTimeWindow(self, timetable):
        minTime = self._timeToInt("24:00")
        maxTime = self._timeToInt("00:00")

        for daySchedule in timetable.values():
            for personalSchedule in daySchedule.values():
                for schedule in personalSchedule:
                    f = self._timeToInt(schedule.fromTime)
                    t = self._timeToInt(schedule.toTime)

                    minTime = min(minTime, f, t)
                    maxTime = max(maxTime, f, t)

        return { "fromTime": minTime, "toTime": maxTime }

    def _timeToInt(self, str):
        parts = str.split(':')
        return int(parts[0]) * 60 + int(parts[1])

if __name__ == "__main__":
    pass