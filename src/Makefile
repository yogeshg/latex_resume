TARGETS = user-resume.pdf
EXISTING_TARGETS := $(strip $(foreach f,$(TARGETS),$(wildcard $(f))))

OUTDIR=./output
FLAGS=--output-directory=$(OUTDIR)

all: $(TARGETS)

%.pdf: %.tex *.tex
	pdflatex --output-directory=$(OUTDIR) $<
	cp $(OUTDIR)/$@ $@

setup:
	touch $(MD_FILES)
	mkdir -p $(OUTDIR)

about:
	@echo "Targets: " $(TARGETS)
	@echo "Existing Targets: " $(EXISTING_TARGETS)

clean:
ifneq ($(EXISTING_TARGETS),)
	rm $(EXISTING_TARGETS)
endif

