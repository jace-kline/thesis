
TEX=pdflatex
DOCNAME=thesis

all: thesis

thesis:
	$(TEX) $(DOCNAME).tex
	bibtex $(DOCNAME).aux
	$(TEX) $(DOCNAME).tex
	$(TEX) $(DOCNAME).tex

clean:
	rm -rf *.toc *.out *.lof *.pdf *.log *.lot *.aux

.PHONY: thesis clean