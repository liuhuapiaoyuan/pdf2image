Skip to content
Navigation Menu
Belval
pdf2image

Type / to search
Code
Issues
69
Pull requests
13
Discussions
Actions
Projects
Security
Insights
Owner avatar
pdf2image
Public
Belval/pdf2image
Go to file
t
Name		
Belval
Belval
Version 1.17.0
3bfb7f7
 · 
2 years ago
.circleci
Setup CircleCI to replace TravisCI
3 years ago
.github
Add documentation action
3 years ago
docs
Update overview.md to read pdf as binary
2 years ago
pdf2image
Fix issue when single_file is True and thread_count is greater than 1
2 years ago
tests
Adding ownerpw param (#208)
4 years ago
.codecov.yml
Ignore tests.py in code coverage
7 years ago
.gitignore
Add multithreading and update README.md
7 years ago
LICENSE
Initial commit
8 years ago
MANIFEST.in
Fix error when importing package
8 years ago
README.md
Minor README formatting
2 years ago
setup.cfg
Version 0.1
8 years ago
setup.py
Version 1.17.0
2 years ago
tests.py
Version 1.17.0
2 years ago
Repository files navigation
README
MIT license
pdf2image
CircleCI PyPI version codecov Downloads GitHub CI

A python (3.7+) module that wraps pdftoppm and pdftocairo to convert PDF to a PIL Image object

How to install
pip install pdf2image

Windows
Windows users will have to build or download poppler for Windows. I recommend @oschwartz10612 version which is the most up-to-date. You will then have to add the bin/ folder to PATH or use poppler_path = r"C:\path\to\poppler-xx\bin" as an argument in convert_from_path.

Mac
Mac users will have to install poppler.

Installing using Brew:

brew install poppler
Linux
Most distros ship with pdftoppm and pdftocairo. If they are not installed, refer to your package manager to install poppler-utils

Platform-independant (Using conda)
Install poppler: conda install -c conda-forge poppler
Install pdf2image: pip install pdf2image
How does it work?
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
Then simply do:

images = convert_from_path('/home/belval/example.pdf')
OR

images = convert_from_bytes(open('/home/belval/example.pdf', 'rb').read())
OR better yet

import tempfile

with tempfile.TemporaryDirectory() as path:
    images_from_path = convert_from_path('/home/belval/example.pdf', output_folder=path)
    # Do something here
images will be a list of PIL Image representing each page of the PDF document.

Here are the definitions:

convert_from_path(pdf_path, dpi=200, output_folder=None, first_page=None, last_page=None, fmt='ppm', jpegopt=None, thread_count=1, userpw=None, use_cropbox=False, strict=False, transparent=False, single_file=False, output_file=str(uuid.uuid4()), poppler_path=None, grayscale=False, size=None, paths_only=False, use_pdftocairo=False, timeout=600, hide_attributes=False)

convert_from_bytes(pdf_file, dpi=200, output_folder=None, first_page=None, last_page=None, fmt='ppm', jpegopt=None, thread_count=1, userpw=None, use_cropbox=False, strict=False, transparent=False, single_file=False, output_file=str(uuid.uuid4()), poppler_path=None, grayscale=False, size=None, paths_only=False, use_pdftocairo=False, timeout=600, hide_attributes=False)

What's new?
Allow users to hide attributes when using pdftoppm with hide_attributes (Thank you @StaticRocket)
Fix console opening on Windows (Thank you @OhMyAgnes!)
Add timeout parameter which raises PDFPopplerTimeoutError after the given number of seconds.
Add use_pdftocairo parameter which forces pdf2image to use pdftocairo. Should improve performance.
Fixed a bug where using pdf2image with multiple threads (but not multiple processes) would cause and exception
jpegopt parameter allows for tuning of the output JPEG when using fmt="jpeg" (-jpegopt in pdftoppm CLI) (Thank you @abieler)
pdfinfo_from_path and pdfinfo_from_bytes which expose the output of the pdfinfo CLI
paths_only parameter will return image paths instead of Image objects, to prevent OOM when converting a big PDF
size parameter allows you to define the shape of the resulting images (-scale-to in pdftoppm CLI)
size=400 will fit the image to a 400x400 box, preserving aspect ratio
size=(400, None) will make the image 400 pixels wide, preserving aspect ratio
size=(500, 500) will resize the image to 500x500 pixels, not preserving aspect ratio
grayscale parameter allows you to convert images to grayscale (-gray in pdftoppm CLI)
single_file parameter allows you to convert the first PDF page only, without adding digits at the end of the output_file
Allow the user to specify poppler's installation path with poppler_path
Performance tips
Using an output folder is significantly faster if you are using an SSD. Otherwise i/o usually becomes the bottleneck.
Using multiple threads can give you some gains but avoid more than 4 as this will cause i/o bottleneck (even on my NVMe SSD!).
If i/o is your bottleneck, using the JPEG format can lead to significant gains.
PNG format is pretty slow, this is because of the compression.
If you want to know the best settings (most settings will be fine anyway) you can clone the project and run python tests.py to get timings.
Limitations / known issues
A relatively big PDF will use up all your memory and cause the process to be killed (unless you use an output folder)
Sometimes fail read pdf signed using DocuSign, Solution for DocuSign issue.
About
A python module that wraps the pdftoppm utility to convert PDF to PIL Image object
 



 --

 使用上面的类库
 结合fastapi开发一个接口能够完成
 pdf转image的接口封装
 我需要接口齐全，并且严格按照最标准的，最精简的api设计模式。
 提供完善swagger文档
 