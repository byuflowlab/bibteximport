# BibTeX Import

Given any reference search terms (title, author, doi, etc.) this script searches for the corresponding publication using the CrossRef API and downloads its BibTeX data. This BibTeX data is then automatically imported into BibDesk.  This script is a simplified version of my Alfred workflow, but doesn't require the powerpack.

Install:

```bash
python setup.py install
chmod u+x bibteximport.command
```

Use:

From spotlight just start typing out bibteximport.command then press enter (or rename it to something shorter and more convenient)

