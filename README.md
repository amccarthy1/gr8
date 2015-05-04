# gr8
A course grading system built on django 1.7. Includes course enrollment, grading, scheduling, exporting/importing to/from Google Calendar, transcript generation, and other education-related features.

## Disclaimer
This application was developed as a part of a college course and is not to be taken as an alternative to an actual course management system. The developers of this project make no claims about the security of this product and take no responsibility for any damages that may result from its use. The creation of this application is purely for academic purposes, and this system is not intended for use in actual schools or colleges.

## Installation
Gr8 requires a working installation of Python 3.x with django 1.7 (this is most easily installed using pip). To install django 1.7 using pip, run:
`pip install django==1.7`

###Dependencies
Gr8 depends upon the following open libraries

#####ReportLab
ReportLab is a PDF generation library for python. Gr8 uses ReportLab to generate students' transcripts on-the-fly. To install reportlab, run `pip install reportlab`.

#####Google API
Gr8 makes use of Google Calendar, and uses the Google API for Python (available on Github) to connect to it. To install the API, run `pip install git+https://github.com/enorvelle/GoogleApiPython3x.git`

Note that in order for the Google Calendar functionality to work, you'll need to register the application with Google, and obtain a `client_secrets.json` file for the application. (Put this file in the `gr8/` directory