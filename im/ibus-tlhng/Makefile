# only really known to work on ubuntu, if you're using anything else, hopefully
# it should at least give you a clue how to install it by hand

PREFIX ?= /usr
SYSCONFDIR ?= /etc
DATADIR ?= $(PREFIX)/share
DESTDIR ?=

PYTHON ?= /usr/bin/python3

all: tlhng.xml

tlhng.xml: tlhng.xml.in
	sed -e "s:@PYTHON@:$(PYTHON):g;" \
	    -e "s:@DATADIR@:$(DATADIR):g" $< > $@

install: all
	install -m 0755 -d $(DESTDIR)$(DATADIR)/ibus-tlhng $(DESTDIR)$(DATADIR)/ibus/component
	install -m 0644 Hol.svg $(DESTDIR)$(DATADIR)/ibus-tlhng
	install -m 0644 mapping.json $(DESTDIR)$(DATADIR)/ibus-tlhng
	install -m 0644 ibus.py $(DESTDIR)$(DATADIR)/ibus-tlhng
	install -m 0644 tlhng.xml $(DESTDIR)$(DATADIR)/ibus/component

uninstall:
	rm -f $(DESTDIR)$(DATADIR)/ibus-tlhng/Hol.svg
	rm -f $(DESTDIR)$(DATADIR)/ibus-tlhng/mapping.json
	rm -f $(DESTDIR)$(DATADIR)/ibus-tlhng/ibus.py
	rmdir $(DESTDIR)$(DATADIR)/ibus-tlhng
	rm -f $(DESTDIR)$(DATADIR)/ibus/component/tlhng.xml

clean:
	rm -f tlhng.xml
	rm -f config.py
