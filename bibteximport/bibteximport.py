#!/usr/bin/env python
# encoding: utf-8
"""
Author: Andrew Ning
"""

import subprocess
import requests
from unicode_to_latex import unicode_to_latex
import re


NENTRIES = 10


def runAppleScript(script):
    osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = osa.communicate(script)
    return output.strip(), error.strip()


def quoteAppleScript(string):
    return string.replace('\\', '\\\\').replace('"', '\\"')


def search(default):

    ascommand = """
    set thequery to display dialog "Crossref Search" default answer "{0}" with icon note buttons {{"Cancel", "Search"}} default button "Search"
    """.format(default)

    # run applescript
    result, error = runAppleScript(ascommand)

    # check if cancelled
    if 'canceled' in error:
        exit()

    # parse result
    query = result.split(':')[2].strip()

    # Use crossref metadata search (beta) to get the DOI
    params = {'q': query, 'rows': str(NENTRIES)}
    r = requests.get('http://search.crossref.org/dois', params=params)

    # grab results
    citations = []
    dois = []
    for j in r.json():
        doi = j['doi'].split('dx.doi.org/')[1]
        citation = j['fullCitation']

        # strip out html tag for italic
        citation = citation.replace('<i>', '').replace('</i>', '')

        citations.append(citation.encode("utf-8"))
        dois.append(doi)


    ascommand = """
    tell application "System Events"
        activate
        try
    """
    ascommand += "set mychoice to (choose from list {\"" + citations[0] + "\""
    for i in range(1, NENTRIES):
        ascommand += ", \"" + quoteAppleScript(citations[i]) + "\""
    ascommand += """} with prompt "Which Reference?" default items "None" OK button name {"Select"} cancel button name {"Go Back"})
        end try
    end tell
    """

    # run applescript
    result, error = runAppleScript(ascommand)

    if result == 'false':
        return None, query
    else:
        idx = citations.index(result)
        return dois[idx], query




def getbibtex(doi):

    # fix escaped chars
    doi = doi.replace('\\', '')

    # use REST API (see http://crosscite.org/cn/)
    headers = {'Accept': 'application/x-bibtex'}
    r = requests.post('http://dx.doi.org/' + doi, headers=headers)

    # extract bibtex
    r.encoding = 'utf-8'
    bibtex = r.text
    bibtex = bibtex.replace('&amp;', '&')
    bibtex = bibtex.strip()

    return bibtex


def importBibTeXIntoBibDesk(bibtex):

    # check if valid BibTeX
    if bibtex[0] != '@':
        print 'BibTeX Not Available'
        exit()

    # convert to latex format (e.g., & -> \&)
    for key in unicode_to_latex.keys():
        bibtex = bibtex.replace(key, unicode_to_latex[key])

    # encode
    bibtex = bibtex.encode('utf-8')

    # replace cite-key to allow bibtex to generate own
    bibtex = re.sub('{.*?,', '{cite-key,', bibtex, count=1)

    # open BibDesk (opens a document if you have this set in BibTeX preferences)
    p = subprocess.Popen(['open', '-a', 'BibDesk'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate()

    # applescript to import into BibDesk
    script = '''
    if exists application "BibDesk" then
        tell application "BibDesk"
            activate
            if (count of documents) > 0 then
                tell document 1
                    import from "{0}"
                end tell
            end if
        end tell
    end if
    '''.format(quoteAppleScript(bibtex))

    runAppleScript(script)



if __name__ == '__main__':

    # get doi
    doi = None
    default = ''
    while doi is None:
        doi, default = search(default)

    # get bibtex
    bibtex = getbibtex(doi)

    # import
    importBibTeXIntoBibDesk(bibtex)


