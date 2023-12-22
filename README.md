AI generated tool, took me 20 minutes to write this project...

This is made for my custom needs, in case anyone else is interested, I'm making it open-source.
I'm not planning to make it generic, this is not a new open-source project. I'm just sharing what I'm using.
Fork the code or clone it, the code is pretty simple.


# What is this?
a simple python script
- input: url of the release
- output: a text file, consisting of:
  - issues closed after the date of the given release
  - PR's merged after he date of the given release


# How to run?
- run `pip3 install requests`
- run `python3 ./release_notes_template.py`
- enter the url of the previous release
- the template release notes will be put under `summary.txt` file


