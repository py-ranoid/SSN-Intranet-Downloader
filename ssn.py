from bs4 import BeautifulSoup
import urllib2
import urllib
import os
import sys
import argparse
from urlparse import urljoin
import re

#   Setting Argument parsing for command line inputs
parser = argparse.ArgumentParser()
parser.add_argument(
    "-b", "--branch", help="Branch ID. 5 for CSE. 9 for IT", type=int)
parser.add_argument("-y", "--year", help="Year. 1/2/3/4", type=int)
parser.add_argument(
    "-s", "--sem", help="Semester. 1 - Odd / 2 - Even", type=int)
parser.add_argument("-p", "--path", help="Path to store files",
                    type=str, default=os.getcwd())
args = parser.parse_args()
URLOpen = urllib.URLopener()
raw_primeurl = None
folder_name = None


def dirCheck(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


# Function to return HTML parsed by BeautifulSoup
def inasoup(url):
    page_html = urllib2.urlopen(url).read()
    return BeautifulSoup(page_html, "html.parser")


ANALYICS = """
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-103678083-3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'UA-103678083-3');
  ga('send', 'pageview', location);
</script>
"""
#   Function to download files


def DownloadFiles(file_refs, folderpath, types):
    errlog = []
    progress = 0
    totalprog = len(file_refs)
    local_links = {}
    for i in file_refs:
        link = sanitize(str(i))
        #   Checks if link extension satisfies given list of extensions
        if link.endswith(types):
            linktext = file_refs[i][1]
            tabtext = file_refs[i][0]
            #   linktext - Href text from page html
            #   tabtext  - Topic related text from table row
            if linktext:
                fl = link.split('/')[-1]
                flname, flext = os.path.splitext(fl)
                if tabtext is None:
                    fname = linktext + ' (' + flname + ')' + flext
                else:
                    fname = tabtext + ' - ' + linktext + \
                        ' (' + flname + ')' + flext
            else:
                fl = link.split('/')[-1]
                flname, flext = os.path.splitext(fl)
                if tabtext is None:
                    fname = fl
                else:
                    fname = tabtext + ' (' + flname + ')' + flext

            # Replacing / in filenames with - to avoid directory issues in Linux Filesystem
            fname = '-'.join(fname.split('/'))

            #       Declare filepath
            fpath = os.path.join(folderpath, fname)
            try:
                local_links[i] = fpath
                if not os.path.exists(fpath):
                    # print "Downloading", link.ljust(100),fname
                    URLOpen.retrieve(link, fpath)
            except IOError, e:
                #   Make list of files that were not found
                if e[1] == 404:
                    errlog.append(i)
                else:
                    pass

        # Progress bar to indicate download status
        progress += 1
        percentage = 100 * progress / totalprog
        sys.stdout.write('\r')
        sys.stdout.flush()
        sys.stdout.write("Progress : [%-50s] %d%%" %
                         ('=' * (percentage / 2), percentage))

    # Prints new line after status bar
    print
    #   Print list of files that were not found
    for errlink in errlog:
        print 'Error 404 :', errlink, 'not found'

    # Returns dictionary mapping URLs to local addresses
    return local_links


#   Function to return absolute URL by adding base URL
def sanitize(url):
    # type: (object) -> object
    return urljoin('http://www.ssn.net', url)


#   Function to list references and accept choice
def getVal(sites, message, value=None):
    if value is None:
        for i, x in enumerate(sites):
            print str(i + 1).ljust(3), ':', x.text
        value = input(message)
    return value - 1


#   Function to fetch Subject/Branch URL
def getSubURL(mainurl):
    sub_list = inasoup(mainurl).find_all('ul')[1]
    all_sites = sub_list.find_all('a', attrs={'class': 'twikiLink'})
    subject_id = getVal(all_sites, 'Subject >> ', args.branch)
    return sanitize(all_sites[subject_id].get('href')), subject_id


#   Function to fetch Primary URL
def getPrimeURL(url, subject_id):
    if subject_id == 4:
        table = inasoup(url).find('table', attrs={'width': "790"})
        all_sites = table.find_all('a', attrs={'class': 'twikiLink'})
        year_id = getVal(all_sites, 'Year >> ', args.year)
        return all_sites[year_id].get('href')
    else:
        if args.sem:
            sem_id = args.sem - 1
        else:
            sem_id = input('0:  Odd Semester\n1:  Even Semester\nSemester >> ')
        return sanitize(
            ['/twiki/bin/view/ItIntranet/ItOddSem2016', '/twiki/bin/view/ItIntranet/FirstYearEven2016-17'][sem_id])


# Function to fetch Primary table
def getPrimeTab(url, subject_id):
    if subject_id == 4:
        all_tables = inasoup(url).find_all('table', attrs={'width': "790"})
        if args.sem:
            sem_id = args.sem
        else:
            sem_id = input('1:  Odd Semester\n2:  Even Semester\nSemester >> ')
        sub_tables = all_tables[sem_id].find_all('td')[5:]
    else:

        all_tables = inasoup(url).find_all('td')
        year_table = all_tables[0].find_all('a')
        year_sites = []
        for index, year_ref in enumerate(year_table):
            year_link = year_ref.get('href')
            if year_link not in year_sites:
                year_sites.append(link)
                if index in [1, 2, 3, 4] and not args.year:
                    print str(index).ljust(3) + ':' + year_ref.text.split('\n')[0]
        if args.sem:
            prime_url = sanitize(year_sites[args.sem])
        else:
            prime_url = sanitize(year_sites[input('Year >> ')])
        if not url == prime_url:
            all_tables = inasoup(prime_url).find_all('td')
        sub_tables = all_tables[6:8]

    all_subjects = []
    for sub_index in [0, 1]:
        all_subjects.append(sub_tables[sub_index].find_all('a'))
    return all_subjects


# noinspection PyBroadException
def getTableRefs(tabs):
    refs = {}
    #   tab - Table row
    #   Adding all links that can be found in tables
    for tab in tabs:
        try:
            chap = []
            for c in tab.find_all('td'):
                if not c.find('a'):
                    chap.append(str(c.text).strip())
            chap = ' '.join(chap)
            #   chap    - Title of chapter as per table row
            #   ref     - All links in current table row
            for file_ref in tab.find_all('a'):
                refs[file_ref.get('href')] = [chap, file_ref.text]
        except:
            pass
    return refs


#   Get links of all subject pages
def getSubjectLinks(path):
    global raw_primeurl, folder_name
    main_url = 'http://www.ssn.net/twiki/bin/view/SsnIntranet/SsnElearning'
    subject_url, subject_id = getSubURL(main_url)

    if subject_id in [4, 8]:
        raw_primeurl = getPrimeURL(subject_url, subject_id)
        primeurl = sanitize(raw_primeurl)
        prime_table = getPrimeTab(primeurl, subject_id)

        folder_name = primeurl.split('/')[-1]
        path = os.path.join(path, folder_name)
        dirCheck(path)
        all_links = [{}, {}]

        #   Iterating over sections (A/B)
        for sec in [0, 1]:

            #   Iterating over links in section table
            for ref in prime_table[sec]:
                link = str(ref.get('href'))
                title = str(ref.text)
                all_links[sec][link] = title

        return all_links, path

    else:
        print 'Cannot download sujects other than :\n5. Computer Science and Engineering \n9. Information Technology'
        exit(0)


# Get links of all files
def getFileLinks(subject_link):
    soup = inasoup(subject_link)

    #   Finding all links present in table rows
    tabs = soup.find_all('tr', attrs={'class': 'twikiTableEven'}) \
        + soup.find_all('tr', attrs={'class': 'twikiTableOdd'})
    refs = getTableRefs(tabs)

    #   Adding links besides table rows
    content = soup.find('div', attrs={'class': 'patternContent'})
    try:
        for l in content.find_all('a'):
            #   Checks if link has been discovered
            if l.get('href') is not None and l.get('href') not in refs:
                refs[l.get('href')] = [None, l.text]
    except AttributeError:
        print 'No links found in', subject_link
        return

    return refs


# Create a HTML clone of Primary page with local addresses instead of URLs
def createPrimeHTML(subfiles, path):
    global folder_name, raw_primeurl
    prime_url = sanitize(raw_primeurl)
    prime_fname = folder_name + '.html'
    prime_fname = os.path.join(path, prime_fname)
    with open(prime_fname, 'w') as html_file:
        html = urllib2.urlopen(prime_url).read()
        for i in subfiles:
            html = html.replace(i, 'file://' + subfiles[i])
        html_file.write(dropSideBar(html))


def dropSideBar(html):
    sp = BeautifulSoup(html, "html.parser")
    sidebar = re.findall(
        '<div id="patternLeftBar">(?:[\n]|.)*<!-- /patternLeftBar-->', html)
    if sidebar:
        # print "Sidebar dropped"
        return html.replace(sidebar[0], '')
    else:
        # print "Sidebar not Found"
        return html


def main():
    # Setting path to current directory if not mentioned in arguments
    root_path = args.path
    dirCheck(root_path)

    name, path = getSubjectLinks(root_path)

    subject_fpaths = {}

    for section in [0, 1]:

        #   section - 0 for A, 1 for B
        #   secpath - Path of section folder

        if section == 0:
            secpath = os.path.join(path, 'A')
        else:
            secpath = os.path.join(path, 'B')
        dirCheck(secpath)

        #   rawlink - links of all subjects
        for rawlink in name[section]:

            link = sanitize(rawlink)
            print '\n--- Scraping', link
            subname = name[section][rawlink]
            file_links = getFileLinks(link)

            if file_links:
                folder_path = os.path.join(secpath, subname)
                dirCheck(folder_path)
                replacements = DownloadFiles(
                    file_links, folder_path, ('pdf', 'ppt', 'doc', 'pptx', 'docx'))
            else:
                #   If file_links is empty
                print 'No links found.'

            # Create a HTML clone of Subject page with local addresses instead of URLs
            htmlfname = subname + '.html'
            html_fpath = os.path.join(secpath, htmlfname)
            with open(html_fpath, 'w') as htmlfile:
                #   Get HTML of page
                html = urllib2.urlopen(link).read()
                #   Replace URLs with local addresses
                for i in replacements:
                    html = html.replace(i, 'file://' + replacements[i])
                html = html.replace(raw_primeurl, 'file://' + html_fpath)
                reduced = dropSideBar(html)
                htmlfile.write(reduced)
                subject_fpaths[rawlink] = html_fpath
    createPrimeHTML(subject_fpaths, path)


if __name__ == '__main__':
    main()
