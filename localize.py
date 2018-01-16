import git
import datetime
import glob
import os

r = git.Repo('.')
remote_parts = r.remotes.origin.url[:-4].split('/')
uname = remote_parts[3]


def modify():
    """
        'master' uses GH pages repository URL as bas path.
        'modify', reads all the html files and replaces the repository's GH page URL (curr)
        with that of the base path (newpath).
    """
    curr = 'https://' + uname + '.github.io/SSN-Intranet-Downloader'
    newpath = 'file://' + os.getcwd()
    allhtmls = glob.glob('*/*/*.html') + glob.glob('*/*.html')
    for f in allhtmls:
        fl = open(f)
        content = fl.read()
        content = content.replace(curr, newpath)
        open(f, 'w').write(content)
    print "Path replaced in all files"


def gitops():
    """
        To stage, commit and push files to GH
    """
    r.index.add(['CseElearnThirdYear/*'])
    r.index.commit('Added files - ' + str(datetime.datetime.now()))
    org = r.remotes.origin
    org.push('local')


modify()
# gitops()
