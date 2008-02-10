# $Id: Makefile 72 2007-06-08 13:03:26Z sfsetse $

PROG=shunit2

BIN_DIR=$(PWD)/bin
BUILD_DIR=$(PWD)/build
DIST_DIR=$(PWD)/dist
LIB_DIR=$(PWD)/lib
SHARE_DIR=$(PWD)/share
SRC_DIR=$(PWD)/src
TEST_DIR=$(PWD)/test
TMP_DIR=$(PWD)/tmp

DOCBOOK_BUILD_DIR=$(BUILD_DIR)/docbook
DOCBOOK_SHARE_DIR=$(SHARE_DIR)/docbook

DOCBOOK_SRC_DIR=$(SRC_DIR)/docbook
EXAMPLES_SRC_DIR=$(SRC_DIR)/examples
SHELL_SRC_DIR=$(SRC_DIR)/shell
TEST_SRC_DIR=$(SRC_DIR)/test

HTML_XSL=$(SHARE_DIR)/docbook/tldp-xsl/21MAR2004/html/tldp-one-page.xsl

all: build docs

build: build-prep
	cp -p $(SHELL_SRC_DIR)/$(PROG) $(BUILD_DIR)

build-clean:
	rm -fr $(BUILD_DIR)

build-prep:
	@mkdir -p $(BUILD_DIR)

docs: docs-transform-shelldoc docs-transform-docbook

docs-prep:
	@mkdir -p $(DOCBOOK_BUILD_DIR)
	@echo "Preparing documentation for parsing"
	@isoDate=`date "+%Y-%m-%d"`; \
	find $(DOCBOOK_SRC_DIR) -name "*.xml" |\
	while read f; do \
	  bn=`basename $$f`; \
	  sed -e "s/@@ISO_DATE@@/$$isoDate/g" $$f >$(DOCBOOK_BUILD_DIR)/$$bn; \
	done

docs-extract-shelldoc: docs-prep
	@echo "Extracting the ShellDoc"
	@$(BIN_DIR)/extractDocs.pl $(SHELL_SRC_DIR)/$(PROG) >$(BUILD_DIR)/$(PROG)_shelldoc.xml

docs-transform-shelldoc: docs-prep docs-extract-shelldoc
	@echo "Parsing the extracted ShellDoc"
	@xsltproc $(SHARE_DIR)/resources/shelldoc.xslt $(BUILD_DIR)/$(PROG)_shelldoc.xml >$(DOCBOOK_BUILD_DIR)/functions.xml

docs-transform-docbook: docs-docbook-prep docs-prep
	@echo "Parsing the documentation with DocBook"
	@xsltproc $(HTML_XSL) $(DOCBOOK_BUILD_DIR)/$(PROG).xml >$(BUILD_DIR)/$(PROG).html

docs-docbook-prep:
	@if [ ! -d "$(DOCBOOK_SHARE_DIR)/docbook-xml" \
	  -o ! -d "$(DOCBOOK_SHARE_DIR)/docbook-xsl" ]; \
	then \
	  echo "Preparing DocBook structure"; \
	  $(BIN_DIR)/docbookPrep.sh "$(DOCBOOK_SHARE_DIR)"; \
	fi

test: test-prep
	@echo "executing $(PROG) unit tests"
	( cd $(TEST_DIR); $(TEST_SRC_DIR)/run-test-suite )

test-clean:
	rm -fr $(TEST_DIR)

test-prep: build test-clean
	@mkdir -p $(TEST_DIR)
	cp -p $(TEST_SRC_DIR)/test* $(TEST_DIR)
	cp -p $(TEST_SRC_DIR)/run-test-suite $(TEST_DIR)
	cp -p $(BUILD_DIR)/$(PROG) $(TEST_DIR)

dist: dist-clean build docs
	@mkdir $(DIST_DIR)
	cp -p $(BUILD_DIR)/$(PROG) $(DIST_DIR)
	cp -p $(BUILD_DIR)/$(PROG).html $(DIST_DIR)

clean: build-clean test-clean
	rm -fr $(TMP_DIR)

dist-clean: clean
	rm -fr $(DIST_DIR)
