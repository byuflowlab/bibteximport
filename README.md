# BibTeX Import

*Mac only*: Although the code is Python, its functionality depends on BibDesk and AppleScript.

Given any reference search terms (title, author, doi, etc.) this script searches for the corresponding publication using the CrossRef API (or Google Books API) and downloads its BibTeX data. This BibTeX data is then automatically imported into BibDesk.  This script is a simplified version of my Alfred workflow, but doesn't require the powerpack.

### Setup:

```bash
python setup.py install
```

In BibDesk preferences > General > Application Launch > Open File: select your main reference file so that it will be automatically opened when BibDesk is launched.

### Usage:

From spotlight (or free version of Alfred) just start typing BI.app and press enter when it pops up.  If you are specifically looking for a book then start your query with "book ".  

