
TEX=pdflatex
DOCNAME=thesis
DOCNAME_SCITEPRESS=thesis-scitepress

all: thesis thesis-scitepress

thesis-scitepress:
	$(TEX) $(DOCNAME_SCITEPRESS).tex
	bibtex $(DOCNAME_SCITEPRESS).aux
	$(TEX) $(DOCNAME_SCITEPRESS).tex
	$(TEX) $(DOCNAME_SCITEPRESS).tex

thesis:
	$(TEX) $(DOCNAME).tex
	bibtex $(DOCNAME).aux
	$(TEX) $(DOCNAME).tex
	$(TEX) $(DOCNAME).tex

clean:
	rm -rf *.toc *.out *.lof *.pdf *.log *.lot *.aux *.bbl *.blg *.fls *.synctex.gz *.fdb_latexmk

.PHONY: thesis clean