# BibTeX Import

Given any reference search terms (title, author, doi, etc.) this script searches for the corresponding publication using the CrossRef API (or Google Books API) and downloads its BibTeX data. This BibTeX data is then automatically imported into BibDesk.  This script is a simplified version of my Alfred workflow, but doesn't require the powerpack.

Setup:

```bash
python setup.py install
chmod u+x bibteximport.command
```

In BibDesk preferences > General > Application Launch > Open File: select your main reference file so that it will be automatically opened when BibDesk is launched.

Usage:

From spotlight just start typing out bibteximport.command then press enter (or in the free version of Alfred start the command with open).  If you are specifically looking for a book then start your query with "book ".  If you don't like typing out bibteximport you can rename the file to something shorter.

