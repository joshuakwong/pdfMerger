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
        print("<<<<<<<<<<<<<<<              >>>>>>>>>>>>>>>")
        print("<<<<<<<<<<<<<<< pdfMerger.py >>>>>>>>>>>>>>>")
        print("<<<<<<<<<<<<<<<              >>>>>>>>>>>>>>>")
        print()

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


def interleaveList(first, second, cover):
    lenFirst = len(first)
    lenSecond = len(second)
    if lenFirst < lenSecond:
        debug(WARNING, "cannot interleave supplied list, len(first) < len(second)")
        debug(WARNING, "len(first)= {}, len(second)= {}".format(lenFirst, lenSecond))

    if lenFirst-lenSecond > 1:
        debug(WARNING, "cannot interleave supplied list, len(first) is longer than len(second)")
        debug(WARNING, "len(first)= {}, len(second)= {}, difference= {}".format(lenFirst, lenSecond, lenFirst-lenSecond))


    # home brew interleaving
    pagesList = []
    debug(INFO, "interleave odd and even pages")

    iF = 0
    iS = 0
    while iF < lenFirst or iS < lenSecond:
        if iF < lenFirst:
            pagesList.append(first[iF])
            iF += 1
        if iS < lenSecond:
            pagesList.append(second[iS])
            iS += 1

    if cover == None:
        if len(pagesList) != lenFirst + lenSecond:
            debug(WARNING, "interleave list error, lenght mismatch")

    else:
        pagesList.insert(0, cover[0])
        if cover[1] != None:
            pagesList.append(cover[1])
        if len(pagesList) != lenFirst + lenSecond + len(cover):
            debug(WARNING, "interleave list error, lenght mismatch")

    return pagesList


# pass pdf info Tuples to pdfReadToGenericList(pdfTup) and take the returned generic python list
# interleave odd and even page list, i.e. [odd1, even 1, odd2, even2, odd3, even3...]
# add pdf pages to pdfWriter in the following order:
# - front cover
# - interleaved odd and even pages
# - back cover
# save the final pdf in ./output/
def pdfOperation(keyInfo):
    baseDir = keyInfo["baseDir"]
    outputDir = baseDir[:baseDir.rfind("/")+1] + "output/"
    outPDF = open(outputDir + keyInfo["outPDF"], "wb")
    pdfWriter = PdfFileWriter()

    # read pdf pages into generic python lists, reverse if necessary
    oddList = pdfReadToGenericList(keyInfo["odd"])
    debug(INFO, "parsed odd pages file")
    evenList = pdfReadToGenericList(keyInfo["even"])
    debug(INFO, "parsed even pages file")
    coverList = pdfReadToGenericList(keyInfo["cover"])
    debug(INFO, "parsed cover pages file")

    # interleave odd number pages and even number pages
    # write to final pdf
    for page in interleaveList(oddList, evenList, coverList):
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
    oddPdfObj = keyInfo["odd"][0]
    evenPdfObj = keyInfo["even"][0]
    coverPdfObj = keyInfo["cover"][0]

    return (oddPdfObj.getNumPages(), evenPdfObj.getNumPages(), coverPdfObj.getNumPages())

# Sum all pdf len to get the correct final pdf len.
def checkPdfLen(keyInfo):
    tup = getAllPdfLen(keyInfo)

    return sum(tup)


# given book directory, parse the following
# - baseDir, which will become pdf name
# - PdfFileReader obj of odd page pdf
# - PdfFileReader obj of even page pdf
# - PdfFileReader obj of cover page pdf
# This func returns a dict with category as key, tuple or string as value. 
# First val in tuple is PdfFileReader obj of pdf. 
# Second val is whether pdf needs to be reversed
# {
# odd: (<PdfFileReader obj>, <True/False>),
# even: (<PdfFileReader obj>, <True/False>),
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

    # check if dir contains "odd.pdf", "even.pdf", "cover.odf"
    oddExistCheck = False
    evenExistCheck = False
    coverExistCheck = False

    for f in fileList:
        if oddExistCheck == False and f.startswith("odd"):
            oddExistCheck = True
            path = bookDir + "/" + f
            pdfObj = PdfFileReader(path)
            if f == "odd.pdf":
                oddTup = (pdfObj, False)
            else:
                oddTup = (pdfObj, True)

        if evenExistCheck == False and f.startswith("even"):
            evenExistCheck = True
            path = bookDir + "/" + f
            pdfObj = PdfFileReader(path)
            if f == "even.pdf":
                evenTup = (pdfObj, False)
            else:
                evenTup = (pdfObj, True)

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
    if (len(fileList) == 2) and (oddExistCheck == False or evenExistCheck == False):
        debug(WARNING, "Supplied directory has 2 files, does not contain req files have been misnamed")
        exit(1)

    # case with 3 files in dir
    if (len(fileList) == 3) and (oddExistCheck == False or evenExistCheck == False or coverExistCheck == False):
        debug(WARNING, "Supplied directory has 3 files, does not contain req files have been misnamed")
        exit(1)

    if len(fileList) == 2 and coverExistCheck == False:
        coverTup = (None, None)

    
    debug(INFO, "all files exists and are ready to be merged")

    # prep return dictionary
    keyInfo = {}
    keyInfo["odd"] = oddTup
    keyInfo["even"] = evenTup
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
