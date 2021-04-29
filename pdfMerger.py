#!/usr/bin/env python3

from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: ./pdfMerger.py <directory>")
        exit(1)

    bookDir = pathFileParse(sys.argv[1])


# given book directory, parse the following
# - directory name, which will become pdf name
# - path to odd page pdf
# - path to even page pdf
# - path to cover page pdf
# This func returns a dict with category as key, tuple as value. 
# First val in tuple is abs path to pdf. 
# Second val is whether pdf needs to be reversed
# {
# odd: ("/path/to/odd.pdf", <True/False>),
# even: ("/path/to/odd.pdf", <True/False>),
# cover: ("/path/to/odd.pdf", <True/False>)
# }
def pathFileParse(arg):
    bookDir = os.path.abspath(arg)
    fileList = [f for f in os.listdir(bookDir) if f.endswith("pdf")]

    # check if dir contains EXACTLY 3 files
    if len(fileList) != 3:
        print("supplied directory does not contain 3 files")
        exit(1)

    # prep return dictionary
    retDict = {}

    # check if dir contains "odd.pdf", "even.pdf", "cover.odf"
    oddExistCheck = False
    evenExistCheck = False
    coverExistCheck = False

    for f in fileList:
        if oddExistCheck == False and f.startswith("odd"):
            oddExistCheck = True
            path = bookDir + "/" + f
            if f == "odd.pdf":
                oddTup = (path, False)
            else:
                oddTup = (path, True)

        if evenExistCheck == False and f.startswith("even"):
            evenExistCheck = True
            path = bookDir + "/" + f
            if f == "even.pdf":
                evenTup = (path, False)
            else:
                evenTup = (path, True)

        if coverExistCheck == False and f.startswith("cover"):
            coverExistCheck = True
            path = bookDir + "/" + f
            if f == "cover.pdf":
                coverTup = (path, False)
            else:
                coverTup = (path, True)

    if oddExistCheck == False or evenExistCheck == False or coverExistCheck == False:
        print("Supplied directory does not contain all required files or have been misnamed")

    retDict["odd"] = oddTup
    retDict["even"] = evenTup
    retDict["cover"] = coverTup
    
    for k in retDict:
        print("{}:\t{}".format(k, str(retDict[k])))

    return retDict



if __name__ == "__main__":
    main()
