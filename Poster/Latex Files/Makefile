TARGETS = main

TEXFILES = $(wildcard *.tex) $(wildcard tables/*.tex) $(wildcard *.cls) $(wildcard figures/*.pdf) $(wildcard *.bib)
PDFS = $(addsuffix .pdf,$(TARGETS))

all: $(PDFS)

%.pdf: $(TEXFILES) 
	pdflatex $*.tex
	bibtex $*
	pdflatex $*.tex
	pdflatex $*.tex

camera: $(PDFS)
	gs -dNOPAUSE -dBATCH -dPDFSETTINGS=/prepress -sDEVICE=pdfwrite -dEmbedAllFonts=true -sOutputFile=$@.pdf -f $<

clean:
	/bin/rm -f $(PDFS) *.dvi *.aux *.ps *~ *.log *.out *.lot *.lof *.toc *.blg *.bbl *.cb *.cb2 url.sty
