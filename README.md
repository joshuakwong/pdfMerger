# pdfMerger

## usage:
``` sh
./pdfMerger.py <inputDir1> <inputDir2> <inputDir3>...
```

### input directory format
```
inputDir
|-> odd.pdf
|-> even.pdf
|-> cover.pdf
```

### output
Output to same level of input directory, in a directory named `output`
```
pdfMerger.py

inputDir1
|-> odd.pdf
|-> even.pdf
|-> cover.pdf

inputDir2
|-> odd.pdf
|-> even.pdf
|-> cover.pdf

inputDir3
|-> odd.pdf
|-> even.pdf
|-> cover.pdf

output
|-> Input Directory 1.pdf
|-> Input Directory 2.pdf
|-> Input Directory 3.pdf

```
