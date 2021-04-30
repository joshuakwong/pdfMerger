# pdfMerger

A tool for document merging. If you only have a scanner feeder that can only scan one side at a time this is for you. 

tl;dr this is how it works
``` 
pdf1=['p1', 'p3', 'p5', 'p7', 'p9']
pdf2=['p2', 'p4', 'p6', 'p8', 'p10']

merged=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10']
```

## usage:

``` sh
./pdfMerger.py <inputDir1> <inputDir2> <inputDir3>...
```

Put 2-3 pdfs in a directory, inside the directory, name the pdf with the page that comes first `a.pdf`, the other one `b.pdf`. Add another one called `cover.pdf` if you doc or book has a cover.

If you have to resolve to this tool, there is a great chance that one of your original pdfs are in reverse order. In order to reverse the input pdf, simply add `-r` right before `.pdf`. 

For example
```
a.pdf = ['p1', 'p3', 'p5', 'p7', 'p9']
b-r.pdf = ['p10', 'p8', 'p6', 'p4', 'p2']

merged=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10']
```

Another example
```
a-r.pdf = ['p9', 'p7', 'p5', 'p3', 'p1']
b-r.pdf = ['p10', 'p8', 'p6', 'p4', 'p2']

merged=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10']
```

### error?
It won't work if your feeder jammed and there are couple of pages missing, it was a bug, but then I made it a feature.
This script checks input pdf lengths before processing, it allows
```
len("a.pdf") == len("b.pdf")
len("a.pdf") - len("b.pdf") == 1
```

It won't allow
```
len("a.pdf") < len("b.pdf")
```


### input directory format
```
inputDir
|-> a.pdf
|-> b.pdf
|-> cover.pdf
```

### output
Output to same level of input directory, in a directory named `output`
```
pdfMerger.py

foo
|-> a.pdf
|-> b.pdf
|-> cover.pdf

bar
|-> a.pdf
|-> b-r.pdf
|-> cover.pdf

baz
|-> a-r.pdf
|-> b.pdf
|-> cover.pdf

output
|-> foo.pdf
|-> bar.pdf
|-> baz.pdf

```
