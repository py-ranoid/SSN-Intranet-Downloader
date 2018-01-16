# SSN Intranet Downloader
#### *Python Script to download all files for CSE/IT  given year &amp;  semester from the intranet and hence generate a local copy of the webpages.*

### Requirements
* Python 2.7
* bs4 ([Beautiful Soup library](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup))

Options | Help
--------|-----------
-b | **Branch**. 5 for *CSE*. 9 for *IT*
-y | **Year**.  1 / 2 / 3 / 4
-s | **Semester**. 1 - *Odd* / 2 - *Even*
-p | **Path** to download files to

### Example
To run the script. (***Input using prompts)***

	python ssn.py

To download 2nd year CSE even semester files in current path

	 python ssn.py -b 5 -y 2 -s 2

To download 3rd year IT odd semester files in /home/MyComputer

	 python ssn.py -b 9 -y 3 -s 1 -p /home/MyComputer


- Progress bar to indicate download status of each subject
- Renames files based on headings/ link text from pages.  
- Updates downloaded files every time script is run. Does not overwrite prexisting files.

# Browsing the Intranet locally

Remove existing folder. Copy folder from master. Change GH paths to local ones.

	git checkout local
	rm -rf CseElearnThirdYear
	python localize.py
