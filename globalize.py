import git
import datetime
import glob
import os

r = git.Repo('.')
remote_parts = r.remotes.origin.url[:-4].split('/')
uname = remote_parts[3]


def modify():
    """
        'ssn.py' currently scrapes the intranet and sets the base path to the current
        directory. 'modify', reads all the html files and replaces the base path (curr)
        with that of the repository's GH page URL (newpath).
    """
    curr = 'file://' + os.getcwd()
    newpath = 'https://' + uname + '.github.io/SSN-Intranet-Downloader'
    allhtmls = glob.glob('*/*/*.html') + glob.glob('*/*.html')
    for f in allhtmls:
        fl = open(f)
        content = fl.read()
        content = content.replace(curr, newpath)
        open(f, 'w').write(content)


def gitops(ghpagesbranch='master'):
    """
        Stages and commits all the changes inside CseElearnThirdYear to local repo.
        Pushes them to branch used to serve ghpages. (master, in my case)
        Make sure you set up GH Pages for your repo.
    """
    r.index.add(['CseElearnThirdYear/*'])
    r.index.commit('Added files - ' + str(datetime.datetime.now()))
    org = r.remotes.origin
    org.push(ghpagesbranch)


if __name__ == "__main__":
    modify()
    gitops()
