
TEX=pdflatex
DOCNAME=thesis

all: thesis

thesis:
	$(TEX) $(DOCNAME).tex
	bibtex $(DOCNAME).aux
	$(TEX) $(DOCNAME).tex
	$(TEX) $(DOCNAME).tex

clean:
	rm -rf *.toc *.out *.lof *.pdf *.log *.lot *.aux *.bbl *.blg *.fls *.synctex.gz *.fdb_latexmk

.PHONY: thesis clean