from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from django.utils import timezone
from reportlab.pdfbase import pdfmetrics
from gr8.settings import FONT_DIR
import os

inch = 72 # 1" = 72pt
margin = inch * 3 / 4 # 3/4" margins
width, height = A4 # Store width and height so we can do the right math.
timestamp = None
TITLE_SIZE = 24
SUBTITLE_SIZE = 12

def render_transcript(request):
    timestamp = timezone.now()
    #TODO render the actual transcript
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment;filename="%s-%s.pdf"' % (request.user.username, timestamp.strftime("%m-%d-%Y"))

    p = canvas.Canvas(response, pagesize=A4)
    # Draw the transcript's header at the top of the first page
    x = margin
    y = height - margin
    x, y = draw_header(p, request.user, x, y)

    p.showPage()
    p.save()
    return response

def draw_header(can, user, x, y):
    """
    Draws the header, and returns the position at which the next part of the document should be written
    """
    # TODO Add logo to top right corner
    # TODO Account for page changes
    name = user.first_name + " " + user.last_name
    can.setFillColorRGB(0, 0, 0)
    date = timezone.now().strftime("%m/%d/%Y")
    textobject = can.beginText()
    y -= TITLE_SIZE # Measured from bottom of text, not top.
    textobject.setTextOrigin(x, y)
    textobject.setFont("PTSans-Regular", TITLE_SIZE)
    textobject.textLine(name)
    can.drawText(textobject)
    # Unofficial Transcript
    textobject = can.beginText()
    y -= SUBTITLE_SIZE # Measured from bottom of text, not top.
    textobject.setTextOrigin(x, y)
    textobject.setFont("PTSans-Italic", SUBTITLE_SIZE)
    can.setFillColorRGB(0.5, 0.5, 0.5)
    textobject.textLine("Unofficial Transcript - Generated on %s" % date)
    can.drawText(textobject)
    y -= 5
    can.line(x, y, width-margin, y)
    y -= 5
    return (x, y)

# Gets called on server startup
# NOTE: Django has hooks for this in 1.7, but not 1.6
def init_pdf_fonts():
    """
    Load and register all fonts in the Font directory.
    NOTE: Fonts are not loaded on the fly, and as such, the server needs to be
    restarted in order to load new fonts.
    """
    # Iterate through all .afm files in the font directory
    for f in filter(lambda f: f.endswith('.afm'), os.listdir(FONT_DIR)):
        base_name = f[:-4] # trim off .afm
        afm = os.path.join(FONT_DIR, base_name + '.afm')
        pfb = os.path.join(FONT_DIR, base_name + '.pfb')
        
        print("Loading font %r " % base_name, end="", flush=True)
        print("." * (50 - len(base_name)), end="", flush=True)
        try:
            justFace = pdfmetrics.EmbeddedType1Face(afm, pfb)
            pdfmetrics.registerTypeFace(justFace)

            justFont = pdfmetrics.Font(base_name, base_name, 'WinAnsiEncoding')
            pdfmetrics.registerFont(justFont)
            print(" SUCCESS")
        except:
            print(" FAILURE")
