TARGETS = $(patsubst %.tex,%.pdf,$(wildcard user-*.tex))
EXISTING_TARGETS := $(strip $(foreach f,$(TARGETS),$(wildcard $(f))))

CMD=pdflatex
OUTDIR=./output
FLAGS=--output-directory=$(OUTDIR)

all: $(TARGETS)

%.pdf: %.tex *.tex
	pdflatex --output-directory=$(OUTDIR) $<
	cp $(OUTDIR)/$@ $@

%.txt: %.tex *.tex
	pandoc -f latex -t plain $< > $@

%.md: %.tex *.tex
	pandoc -f latex -t markdown $< > $@

about:
	@echo "Targets: " $(TARGETS)
	@echo "Existing Targets: " $(EXISTING_TARGETS)

clean:
ifneq ($(EXISTING_TARGETS),)
	rm $(EXISTING_TARGETS)
endif

