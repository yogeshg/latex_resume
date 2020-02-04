TARGETS = $(patsubst %.tex,%.pdf,$(wildcard user-*.tex))
EXISTING_TARGETS := $(strip $(foreach f,$(TARGETS),$(wildcard $(f))))

MD_FILES := acad.md courses.md jobs.md por.md projects.md publications.md skills.md
TEX_FILES := acad.tex courses.tex jobs.tex por.tex projects.tex publications.tex skills.tex

CMD=pdflatex
OUTDIR=./output
FLAGS=--output-directory=$(OUTDIR)

all: $(TARGETS)

%.pdf: %.tex $(TEX_FILES)
	pdflatex --output-directory=$(OUTDIR) $<
	cp $(OUTDIR)/$@ $@

%.txt: %.tex $(TEX_FILES)
	pandoc -f latex -t plain $< > $@

%.tex: %.md
	python latex_resume.py get-markdown $< $@

setup:
	touch $(MD_FILES)
	mkdir -p output

about:
	@echo "Targets: " $(TARGETS)
	@echo "Existing Targets: " $(EXISTING_TARGETS)
	@echo "Tex Targets: " $(TEX_FILES)


clean:
ifneq ($(EXISTING_TARGETS),)
	rm $(EXISTING_TARGETS)
endif

