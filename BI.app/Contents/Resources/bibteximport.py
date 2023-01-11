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
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def runAppleScript(script):
    osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = osa.communicate(script)
    return output.strip(), error.strip()


def quoteAppleScript(string):
    return string.replace('\\', '\\\\').replace('"', '\\"')


def getquery(default):

    ascommand = """
    set the query to display dialog "Crossref Search" default answer "{0}" with icon note buttons {{"Cancel", "Search"}} default button "Search"
    """.format(default)

    # run applescript
    result, error = runAppleScript(ascommand)

    # check if cancelled
    if 'canceled' in error:
        exit()

    # parse result
    query = result.split(':')[2].strip()

    return query


def crossrefsearch(query):

    # Use crossref metadata search (beta) to get the DOI
    params = {'query.bibliographic': query, 'rows': str(NENTRIES)}
    r = requests.get('https://api.crossref.org/works', params=params)
    items = r.json()["message"]["items"]

    # write results in XML format for Alfred
    citations = []
    dois = []
    for i in items:
        doi = i['DOI']
        author = ""
        if 'author' in i:
            for a in i['author']:
                if 'given' in a and 'family' in a:
                    author += a['given'] + ' ' + a['family'] + ', '
        journal = ""
        if 'container-title' in i:
            journal = i['container-title'][0]
        subtitle = author + journal
        title = i['title'][0]

        citations.append(title + ", " + subtitle)
        dois.append(doi)

    idx = presentoptions(citations)
        
    if idx is None:
        return False, None
    else:
        doi = dois[idx]
        bibtex = getbibtexfromdoi(doi)
        return True, bibtex
        

    # # Use crossref metadata search (beta) to get the DOI
    # params = {'q': query, 'rows': str(NENTRIES)}
    # r = requests.get('http://search.crossref.org/dois', params=params)

    # # grab results
    # citations = []
    # dois = []
    # for j in r.json():
    #     print(j)
    #     doi = j['doi']  #.split('dx.doi.org/')[1]
    #     citation = j['fullCitation']

    #     # strip out html tag for italic
    #     citation = citation.replace('<i>', '').replace('</i>', '')

    #     citations.append(citation)  #citation.encode("utf-8"))
    #     dois.append(doi)

    # idx = presentoptions(citations)

    # if idx is None:
    #     return False, None
    # else:
    #     doi = dois[idx]
    #     bibtex = getbibtexfromdoi(doi)
    #     return True, bibtex


def presentoptions(citations):


    ascommand = """
    tell application "System Events"
        activate
        try
    """
    # print(citations[0])
    N = min(len(citations), NENTRIES)
    ascommand += "set mychoice to (choose from list {\"" + citations[0] + "\""
    for i in range(1, N):
        ascommand += ", \"" + quoteAppleScript(citations[i]) + "\""
    ascommand += """} with prompt "Which Reference?" default items "None" OK button name {"Select"} cancel button name {"Go Back"})
        end try
    end tell
    """

    # run applescript
    result, error = runAppleScript(ascommand)

    if result == 'false':
        return None
    else:
        idx = citations.index(result)
        return idx




def getbibtexfromdoi(doi):

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
        runAppleScript(""" display alert "BibTeX Not Available" """)
        return False

    # convert to latex format (e.g., & -> \&)
    for key in unicode_to_latex.keys():
        bibtex = bibtex.replace(key, unicode_to_latex[key])

    # encode
    # bibtex = bibtex.encode('utf-8')

    # replace cite-key to allow bibtex to generate own
    bibtex = re.sub('{.*?,', '{cite-key,', bibtex, count=1)

    # open BibDesk (opens a document if you have this set in BibTeX preferences)
    p = subprocess.Popen(['open', '-a', 'BibDesk'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
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

    return True


def gbooksearch(query):

    params = {'q': query, 'maxResults': NENTRIES, 'fields': 'items(volumeInfo(title,subtitle,authors,publisher,publishedDate,industryIdentifiers))'}

    # search on google books
    r = requests.get('https://www.googleapis.com/books/v1/volumes', params=params)
    r.encoding = 'utf-8'

    resultlist = []
    bibtexlist = []

    for item in r.json()['items']:
        info = item['volumeInfo']

        title = ''
        authors = ''
        publisher = ''
        publishedDate = ''
        year = ''
        month = ''
        isbn = ''
        infoString = ''

        if 'title' in info:
            title = info['title']

        if 'subtitle' in info:
            title += ": " + info['subtitle']

        if 'authors' in info:
            authors = ' and '.join(info['authors'])
            infoString = ', '.join(info['authors'])

        if 'publishedDate' in info:
            publishedDate = info['publishedDate']
            entries = publishedDate.split('-')
            year = entries[0]
            infoString += ', ' + year
            if len(entries) > 1:
                month = MONTHS[int(entries[1]) - 1]

        if 'publisher' in info:
            publisher = info['publisher']
            infoString += ', ' + publisher

        if 'industryIdentifiers' in info:
            for idnt in info['industryIdentifiers']:
                if idnt['type'] == 'ISBN_10':
                    isbn = idnt['identifier']

        bibtex = u"""@book{{{},
        Title = {{{}}},
        Publisher = {{{}}},
        Year = {{{}}},
        Author = {{{}}},
        Month = {{{}}},
        ISBN = {{{}}}
        }}
        """.format('cite-key', title, publisher, year, authors, month, isbn)

        resultlist.append((title + ', ' + infoString).encode('utf-8'))
        bibtexlist.append(bibtex.encode('utf-8'))

    idx = presentoptions(resultlist)

    if idx is None:
        return False, None
    else:
        return True, bibtexlist[idx]









if __name__ == '__main__':

    # get doi
    success = False
    query = ''

    while not success:
        query = getquery(query)

        if query.startswith('book '):
            success, bibtex = gbooksearch(query)
        elif query.endswith('!'):
            doi = query[:-1]
            bibtex = getbibtexfromdoi(doi)
            success = True
        else:
            success, bibtex = crossrefsearch(query)

        if success:
            success = importBibTeXIntoBibDesk(bibtex)


