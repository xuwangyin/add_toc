#!/usr/bin/env python
# coding:utf-8

import sys
import os

class Heading:
    def __init__(self, level, headingsIdx, headingLinesIdx, headingString):
        self.level = level
        self.headingsIdx = headingsIdx
        self.headingLinesIdx = headingLinesIdx
        self.headingString = headingString
    def __repr__(self):
        return "level: " + str(self.level) + "--> content: " + self.headingString
    def __str__(self):
        start = self.headingString.find('>')
        end = self.headingString.rfind('<')
        return self.headingString[start + 1 : end]
# return self.headingString.rstrip('\n')


def parseAllHeadings(headingLines):
    headingTag = '<h'
    headingNum = 0
    for headingLinesIdx, headingLine in enumerate(headingLines):
        find = headingLine.find(headingTag)
        if find != -1:
            headingLevelIdx = find + 2
            headingLevel = int(headingLine[headingLevelIdx])
            yield Heading(headingLevel, headingNum, headingLinesIdx, headingLine)
            headingNum += 1


def directSubheadings(topHeading, headings):
    """ given the heading, reture all of its *direct* subheadings"""
    topLevel = topHeading.level
    directSubLevel = topLevel + 1
    for heading in headings[topHeading.headingsIdx + 1 : ]:
        if heading.level == directSubLevel:
            yield heading
        elif heading.level == topLevel:
            break
        else:
            continue

class HeadingTree:
    def __init__(self, topHeading, directSubheadingTrees):
        self.topHeading = topHeading
        self.directSubheadingTrees = directSubheadingTrees
    def __repr__(self):
        treeStr = str(self.topHeading) + '\n'
        for directSubheadingTree in self.directSubheadingTrees:
            directSubheadingTreeStr = ''
            for line in str(directSubheadingTree).split('\n'):
                # ignore '\n'
                if (len(line) > 1):
                    directSubheadingTreeStr += '|  ' + line + '\n'
            treeStr += directSubheadingTreeStr
        return treeStr

    def generateHref(self, prefix, order):
        # assert isinstance(prefix, str)
        # assert isinstance(order, int)
        if prefix == None:
            self.href = '#1'
        else:
            self.href = prefix + '_' + str(order)
        for idx, directSubheadingTree in enumerate(self.directSubheadingTrees):
            directSubheadingTree.generateHref(self.href, idx + 1)

    def addIDtoHeadingLines(self, lines):
        idString = 'id="' + self.href[1:] + '"'
        headingLine = lines[self.topHeading.headingLinesIdx]
        closeTagIdx = headingLine.find('>')
        lines[self.topHeading.headingLinesIdx] = headingLine[ : closeTagIdx] + ' ' + idString + headingLine[closeTagIdx : ]
        for directSubheadingTree in self.directSubheadingTrees:
            directSubheadingTree.addIDtoHeadingLines(lines)


    def generateTableOfContents(self):
        toc = ''
        toc += '<ul>\n'
        toc += '<li><a href="' + self.href + '">' + str(self.topHeading) + '</a></li>\n'
        for directSubheadingTree in self.directSubheadingTrees:
            toc += directSubheadingTree.generateTableOfContents()
        toc += '</ul>\n'
        return toc

def getHeadingTree(topHeading, allHeadings):
    assert(isinstance(allHeadings, list))
    directSubheadingTrees = [getHeadingTree(heading, allHeadings) for heading in directSubheadings(topHeading, allHeadings)]
    return HeadingTree(topHeading, directSubheadingTrees)


def main():
    if len(sys.argv) <= 2:
        print('Usage: {0} src dst'.format(sys.argv[0]))
        raise SystemExit

    header = '''
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'>
</head>
'''

    footer = '''
</html>
'''

    src = file(sys.argv[1], 'r')
    dst = file(sys.argv[2], 'w')

    lines= src.readlines()
    allHeadings = list(parseAllHeadings(lines))
    headingTree = getHeadingTree(allHeadings[0], allHeadings)
    headingTree.generateHref(prefix=None, order=0)
    toc =  headingTree.generateTableOfContents()
    headingTree.addIDtoHeadingLines(lines)

    dst.write(header)
    style = """
<style>
div.toc {
position:fixed;
right: 0;
top: 20%;
margin-right:10px;
border: 1px solid #AAA;
background-color: #F9F9F9;
padding: 5px;
font-size: 95%;}
</style>\n'
"""
    dst.write(style)
    dst.write('<div class="toc">\n')
    dst.write(toc)
    dst.write('</div>')
    dst.writelines(lines)
    dst.write(footer)

    dst.close()
    src.close()

if __name__ =='__main__':
    main()
