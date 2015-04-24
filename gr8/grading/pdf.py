from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from gr8.settings import FONT_DIR
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, SimpleDocTemplate, Spacer
import os

INCH = 72 # 1" = 72pt
MARGIN = INCH * 3 / 4 # 3/4" margins
PAGE_WIDTH, PAGE_HEIGHT = A4 # Store width and height so we can do the right math.
TITLE_SIZE = 24
SUBTITLE_SIZE = 12

class Header(Flowable):
    """
    Draws a header containing Name, generated date, and other stuff.
    """
    def __init__(self, user, line_space=5):
        Flowable.__init__(self)
        self.line_space = line_space
        self.user = user
        self.height = TITLE_SIZE + SUBTITLE_SIZE + 2*line_space + 1
        self.width = PAGE_WIDTH - 2 * MARGIN

    def __repr__(self):
        return "Header(w=%d,h=%d)" % (self.width, self.height)

    def draw(self):
        x = 0
        y = self.height
        name = self.user.first_name + " " + self.user.last_name
        self.canv.setFillColorRGB(0, 0, 0)
        date = timezone.now().strftime("%m/%d/%Y")
        textobject = self.canv.beginText()
        y -= TITLE_SIZE # Measured from bottom of text, not top.
        textobject.setTextOrigin(x, y)
        textobject.setFont("PTSans-Regular", TITLE_SIZE)
        textobject.textLine(name)
        self.canv.drawText(textobject)
        # Unofficial Transcript
        textobject = self.canv.beginText()
        y -= SUBTITLE_SIZE # Measured from bottom of text, not top.
        textobject.setTextOrigin(x, y)
        textobject.setFont("PTSans-Italic", SUBTITLE_SIZE)
        self.canv.setFillColorRGB(0.5, 0.5, 0.5)
        textobject.textLine("Unofficial Transcript - Generated on %s" % date)
        self.canv.drawText(textobject)

        y -= self.line_space
        self.canv.line(x, y, self.width, y)
        y -= self.line_space

@login_required
def render_transcript(request):
    """
    Render all the components for the transcipt in order and render the
    response.
    """
    #create the filename from the user and timestamp
    timestamp = timezone.now().strftime("%m-%d-%Y")
    filename = "%s-%s.pdf" % (request.user.username, timestamp)

    #initialize the stuff.
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment;filename=' + filename
    story = []
    doc = SimpleDocTemplate(response, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN)
    spacer = Spacer(0,0,0.25 * INCH)

    #add components
    story.append(Header(request.user))
    #story.append(spacer)

    doc.build(story)

    return response

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
