#!/usr/bin/env python3

from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import sys
import re

# PyPDF2 documentation
# https://pythonhosted.org/PyPDF2/

INFO = 0
SUCCESS = 1
WARNING = 2
BOLD = 3
DEBUG = True

def main():
    if len(sys.argv) < 2:
        debug(WARNING, "Usage: ./pdfMerger.py <directory>")
        exit(1)

    i = 1
    while i < len(sys.argv):
        print()
        print("============================================")
        print("<<<<<<<<<<<<<<<              >>>>>>>>>>>>>>>")
        print("<<<<<<<<<<<<<<< pdfMerger.py >>>>>>>>>>>>>>>")
        print("<<<<<<<<<<<<<<<              >>>>>>>>>>>>>>>")
        print("============================================")

        keyInfo = pathFileParse(sys.argv[i])
        pdfOperation(keyInfo)
        i += 1


# given a pdf info Tuple
# read the pdf using the pdfObj
# get pages from pdfObj and put it in a generic python list
# reverse the list if necessary
def pdfReadToGenericList(pdfTup):
    pdfObj, revBool = pdfTup
    if pdfObj == None:
        return None

    pdfGenList = []
    pdfLen = pdfObj.numPages
    
    i = 0
    while i < pdfLen:
        page = pdfObj.getPage(i)
        pdfGenList.append(page)
        i += 1
    
    if revBool == True:
        pdfGenList.reverse()

    if len(pdfGenList) != pdfLen:
        debug(WARNING, "pdfReadToGenericList FAIL, generic list len != pdf len")
        exit(1)

    return pdfGenList


def interleaveList(a, b, cover):
    lenA= len(a)
    lenB= len(b)
    if lenA < lenB:
        debug(WARNING, "cannot interleave supplied list, len(a) < len(b)")
        debug(WARNING, "len(a)= {}, len(b)= {}".format(lenA, lenB))

    if lenA-lenB > 1:
        debug(WARNING, "cannot interleave supplied list, len(a) is longer than len(b)")
        debug(WARNING, "len(a)= {}, len(b)= {}, difference= {}".format(lenA, lenB, lenA-lenB))


    # home brew interleaving
    pagesList = []
    debug(INFO, "interleave a and b pages")

    iF = 0
    iS = 0
    while iF < lenA or iS < lenB:
        if iF < lenA:
            pagesList.append(a[iF])
            iF += 1
        if iS < lenB:
            pagesList.append(b[iS])
            iS += 1

    if cover == None:
        if len(pagesList) != lenA + lenB:
            debug(WARNING, "interleave list error, lenght mismatch")

    else:
        pagesList.insert(0, cover[0])
        if len(cover) == 2:
            pagesList.append(cover[1])
        if len(pagesList) != lenA + lenB + len(cover):
            debug(WARNING, "interleave list error, lenght mismatch")

    return pagesList


# pass pdf info Tuples to pdfReadToGenericList(pdfTup) and take the returned generic python list
# interleave a and b page list, i.e. [a1, b 1, a2, b2, a3, b3...]
# add pdf pages to pdfWriter in the following order:
# - front cover
# - interleaved a and b pages
# - back cover
# save the final pdf in ./output/
def pdfOperation(keyInfo):
    baseDir = keyInfo["baseDir"]
    outputDir = baseDir[:baseDir.rfind("/")+1] + "output/"
    outPDF = open(outputDir + keyInfo["outPDF"], "wb")
    pdfWriter = PdfFileWriter()

    # read pdf pages into generic python lists, reverse if necessary
    aList = pdfReadToGenericList(keyInfo["a"])
    debug(INFO, "parsed a pages file")
    bList = pdfReadToGenericList(keyInfo["b"])
    debug(INFO, "parsed b pages file")
    coverList = pdfReadToGenericList(keyInfo["cover"])
    debug(INFO, "parsed cover pages file")

    # interleave a number pages and b number pages
    # write to final pdf
    for page in interleaveList(aList, bList, coverList):
        pdfWriter.addPage(page)

    pdfWriter.write(outPDF)
    
    # size check, if pdf file has 0 bytes then something is wrong, or it is in testing mode
    size = outPDF.tell()
    if size == 0:
        outPDF.close()
        os.remove(outputDir + keyInfo["outPDF"])
        debug(WARNING, "final PDF is 0 bytes, please check")
    else: 
        outPDF.close()
        debug(SUCCESS, "final PDF passed size check")


def getAllPdfLen(keyInfo):
    aPdfObj = keyInfo["a"][0]
    bPdfObj = keyInfo["b"][0]
    coverPdfObj = keyInfo["cover"][0]

    return (aPdfObj.getNumPages(), bPdfObj.getNumPages(), coverPdfObj.getNumPages())

# Sum all pdf len to get the correct final pdf len.
def checkPdfLen(keyInfo):
    tup = getAllPdfLen(keyInfo)

    return sum(tup)


# given book directory, parse the following
# - baseDir, which will become pdf name
# - PdfFileReader obj of a page pdf
# - PdfFileReader obj of b page pdf
# - PdfFileReader obj of cover page pdf
# This func returns a dict with category as key, tuple or string as value. 
# First val in tuple is PdfFileReader obj of pdf. 
# Second val is whether pdf needs to be reversed
# {
# a: (<PdfFileReader obj>, <True/False>),
# b: (<PdfFileReader obj>, <True/False>),
# cover: (<PdfFileReader obj>, <True/False>),
# baseDir: "<baseDir>"
# outpdfName: "<dirname.pdf>"
# }
def pathFileParse(arg):
    debug(BOLD, "current book: {}".format(unCamelCase(arg)))
    bookDir = os.path.abspath(arg)
    fileList = [f for f in os.listdir(bookDir) if f.endswith("pdf")]
    

    # check if dir contains EXACTLY 3 files
    if len(fileList) != 2 and len(fileList) != 3: 
        debug(WARNING, "supplied directory does not contain 2 or 3 files")
        exit(1)

    # check if dir contains "a.pdf", "b.pdf", "cover.odf"
    aExistCheck = False
    bExistCheck = False
    coverExistCheck = False

    for f in fileList:
        if aExistCheck == False and f.startswith("a"):
            aExistCheck = True
            path = bookDir + "/" + f
            pdfObj = PdfFileReader(path)
            if f == "a.pdf":
                aTup = (pdfObj, False)
            else:
                aTup = (pdfObj, True)

        if bExistCheck == False and f.startswith("b"):
            bExistCheck = True
            path = bookDir + "/" + f
            pdfObj = PdfFileReader(path)
            if f == "b.pdf":
                bTup = (pdfObj, False)
            else:
                bTup = (pdfObj, True)

        # only check for cover if there are 3 files in dir, e.g. Answer key booklet
        if (len(fileList) == 3) and coverExistCheck == False and f.startswith("cover"):
            coverExistCheck = True
            path = bookDir + "/" + f
            pdfObj = PdfFileReader(path)
            if f == "cover.pdf":
                coverTup = (pdfObj, False)
            else:
                coverTup = (pdfObj, True)

    # case with 2 files in dir
    if (len(fileList) == 2) and (aExistCheck == False or bExistCheck == False):
        debug(WARNING, "Supplied directory has 2 files, does not contain req files have been misnamed")
        exit(1)

    # case with 3 files in dir
    if (len(fileList) == 3) and (aExistCheck == False or bExistCheck == False or coverExistCheck == False):
        debug(WARNING, "Supplied directory has 3 files, does not contain req files have been misnamed")
        exit(1)

    if len(fileList) == 2 and coverExistCheck == False:
        coverTup = (None, None)

    
    debug(INFO, "all files exists and are ready to be merged")

    # prep return dictionary
    keyInfo = {}
    keyInfo["a"] = aTup
    keyInfo["b"] = bTup
    keyInfo["cover"] = coverTup
    keyInfo["baseDir"] = bookDir
    keyInfo["outPDF"] = unCamelCase(arg.replace("./", "")) + ".pdf"
    
    debug(INFO, keyInfo)

    return keyInfo


# un-camelCase a string so that it's easier for humans to read
def unCamelCase(string):
    string = re.sub(r"([A-Z])", r" \1", string)
    string = re.sub(r"([0-9]+)", r" \1", string)
    string = string.title()

    return string


def debug(mType, msg):
    if DEBUG == False:
        return
    if mType == INFO:
        sign = "[*] "
    elif mType == WARNING:
        sign = '\033[31m'+"[-] "
    elif mType == SUCCESS:
        sign = '\033[92m'+"[+] "
    elif mType == BOLD:
        sign = '\033[1m'+"[+] "
    else:
        sign = "[ ] "

    if type(msg) == str:
        print(sign+msg)
    if type(msg) == dict:
        print()
        print(sign+"printing dictionary")
        for k in msg:
            print("    {}:  {}".format(k, str(msg[k])))
        print()
    print('\033[0m', end="")

        
if __name__ == "__main__":
    main()
