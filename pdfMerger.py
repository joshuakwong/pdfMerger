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
    print("<<<<<<<<<<<<<<<              >>>>>>>>>>>>>>>")
    print("<<<<<<<<<<<<<<< pdfMerger.py >>>>>>>>>>>>>>>")
    print("<<<<<<<<<<<<<<<              >>>>>>>>>>>>>>>")
    print()

    if len(sys.argv) != 2:
        debug(WARNING, "Usage: ./pdfMerger.py <directory>")
        exit(1)

    keyInfo = pathFileParse(sys.argv[1])
    pdfOperation(keyInfo)
    debug(SUCCESS, "EXITING PEACEFULLY")


# given a pdf info Tuple
# read the pdf using the pdfObj
# get pages from pdfObj and put it in a generic python list
# reverse the list if necessary
def pdfReadToGenericList(pdfTup):
    pdfGenList = []
    pdfObj, revBool = pdfTup
    pdfLen = pdfObj.numPages
    
    i = 0
    while i < pdfLen:
        page = pdfObj.getPage(i)
        pdfGenList.append(page)
        i += 1
    
    if revBool == True:
        pdfGenList.reverse()

    return pdfGenList


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
    # add front cover, then interleaved odd and even pages, finally back cover
    # write to final pdf
    oddEven = [p for pair in zip(oddList, evenList) for p in pair]
    debug(INFO, "interlaced odd and even pages")
    pdfWriter.addPage(coverList[0])
    for p in oddEven:
        pdfWriter.addPage(p)
    pdfWriter.addPage(coverList[1])
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

    # page number check, if len of 3 files combined is less than list, then something is wrong
    lenFromList = len(oddEven) + 2
    sumPdfLen = checkPdfLen(keyInfo)
    if lenFromList == sumPdfLen:
        debug(SUCCESS, "final PDF page num check, 3 files combined= {}, listLen+2= {}".format(sumPdfLen, lenFromList))
    else:
        debug(WARNING, "final PDF len mismatch, please check")
        exit(1)
    

# Sum all pdf len to get the correct final pdf len.
def checkPdfLen(keyInfo):
    oddPdfObj = keyInfo["odd"][0]
    evenPdfObj = keyInfo["even"][0]
    coverPdfObj = keyInfo["cover"][0]

    sumPdfLen = oddPdfObj.getNumPages() + evenPdfObj.getNumPages() + coverPdfObj.getNumPages()
    return sumPdfLen


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
    if len(fileList) != 3: 
        debug(WARNING, "supplied directory does not contain 3 files")
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

        if coverExistCheck == False and f.startswith("cover"):
            coverExistCheck = True
            path = bookDir + "/" + f
            pdfObj = PdfFileReader(path)
            if f == "cover.pdf":
                coverTup = (pdfObj, False)
            else:
                coverTup = (pdfObj, True)

    if oddExistCheck == False or evenExistCheck == False or coverExistCheck == False:
        debug(WARNING, "Supplied directory does not contain all required files or have been misnamed")
    
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
