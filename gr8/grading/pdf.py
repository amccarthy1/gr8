from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from gr8.settings import FONT_DIR
from .models import Course, Profile, Term, Enrolled_In
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, SimpleDocTemplate, Spacer, Table, TableStyle
import reportlab.lib.colors as colors
import os
from gr8.settings import GRADE_SCALE, GRADE_PASSING

INCH = 72 # 1" = 72pt
MARGIN = INCH * 3 / 4 # 3/4" margins
PAGE_WIDTH, PAGE_HEIGHT = A4 # Store width and height so we can do the right math.
TITLE_SIZE = 24
SUBTITLE_SIZE = 12
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

class Line(Flowable):
    """
    Draws a horizontal line in a flowable.
    """

    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def __repr__(self):
        return "Line(w=%d,h=%d)" % (self.width, self.height)

    def draw(self):
        self.canv.line(0,self.height, self.width, self.height)


class Header(Flowable):
    """
    Draws a header containing Name, generated date, and other stuff.
    """
    def __init__(self, user, line_space=5):
        Flowable.__init__(self)
        self.line_space = line_space
        self.user = user
        self.height = TITLE_SIZE + SUBTITLE_SIZE + line_space
        self.width = CONTENT_WIDTH

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

        y -= self.line_space#add a space after the text and before the line.
        line = Line(self.width)
        line.drawOn(self.canv, x, y)

class CoursesTable(Flowable):
    """
    Display a table of course info and grades
    """

    def __init__(self, enrolled_ins):
        Flowable.__init__(self)
        self.enrolled_ins = enrolled_ins
        self.width = CONTENT_WIDTH
        self.header_size = 16
        self.text_size = 12
        self.top_padding = 3
        self.bottom_padding = 3
        self.top_header_padding = 3
        self.bottom_header_padding = 10
        self.border_width = 0.25
        #Calculate the height of the entire table 
        row_height = self.text_size + self.top_padding + self.bottom_padding
        self.height = row_height * len(enrolled_ins)
        self.height += self.header_size + self.top_header_padding + self.bottom_header_padding
        self.height += len(enrolled_ins) * self.border_width + 2#account for all borders (+2 = bottom and top)

    def __repr__(self):
        return "CourseTable(w=%d,h=%d)" % (self.width, self.height)

    def draw(self):
        #define the data grid
        data = [['Course Name', 'Code', 'Credits', 'Grade']]
        #add each course to the data
        for enrolled_in in self.enrolled_ins:
            row = []
            row.append(str(enrolled_in.course))
            row.append(str(enrolled_in.course.course_code))
            row.append(str(enrolled_in.course.course_code.credits))
            if enrolled_in.grade:
                row.append("%.2f" % enrolled_in.grade )
            else:
                row.append(str("NC"))#Not Complete (no grade was entered)
            data.append(row)

        #build the table
        #colWidths is an array of sizes for each column
        colWidths = [self.width/2] + [self.width/6] * 3
        table = Table(data,colWidths)
        #style the header differently
        table.setStyle(TableStyle([
            ('SIZE',(0,0),(-1,0),self.header_size),
            ('BOTTOMPADDING', (0,0),(-1,0),self.bottom_header_padding),
            ('TOPPADDING', (0,0),(-1,0), self.top_header_padding),
            ('BACKGROUND',(0,0),(-1,0), colors.Color(.5,.5,.5,1)),
            ('TEXTCOLOR', (0,0),(-1,0), colors.white),
            ('BOTTOMPADDING', (0,1),(-1,-1),self.bottom_padding),
            ('TOPPADDING', (0,1), (-1,-1), self.top_padding),
            ('INNERGRID', (0,0), (-1,-1), self.border_width, colors.black),
            ('BOX', (0,0), (-1,-1), self.border_width, colors.black)
            ]))
        table.wrapOn(self.canv, 0, 0)
        table.drawOn(self.canv, 0, 0)

class StatsTable(Flowable):
    """
    Display Statistics from a dictionary in a table.
    """

    def __init__(self, stats):
        Flowable.__init__(self)
        self.width = CONTENT_WIDTH
        self.stats = stats
        self.text_size = 12
        self.top_padding = 3
        self.bottom_padding = 3
        self.height = len(stats) * (self.text_size + self.top_padding + self.bottom_padding)

    def __repr__(self):
        return "StatTable(w=%d,h=%d)" % (self.width, self.height)

    def draw(self):
        #build the table
        table = Table(self.stats)
        table.setStyle(TableStyle([
            ('FONT', (0,0), (0,-1), 'PTSans-Bold'),
            ('SIZE',(0,0),(-1,-1),self.text_size),
            ('BOTTOMPADDING', (0,0),(-1,-1),self.bottom_padding),
            ('TOPPADDING', (0,0), (-1,-1), self.top_padding),
            ]))
        table.hAlign = 'RIGHT'
        table.wrapOn(self.canv,0,0)
        table.drawOn(self.canv,0,0)


class SemesterReport(Flowable):
    """
    Display Semester information, followed by course information for that
    semester.
    """

    def __init__(self, user, term):
        Flowable.__init__(self)
        self.width = CONTENT_WIDTH
        self.term_name_size = 18;#pts

        #get the semester information
        self.term_name = str(term)
        enrolled_ins = user.profile.get_enrolled_by_term(term)

        #initialize the courses table to be drawn
        self.courses_table = CoursesTable(enrolled_ins)
        self.stats_table = StatsTable(user.profile.get_term_stats(term))

        #calculate the height of this component
        self.height = self.term_name_size + self.courses_table.height + self.stats_table.height

    def __repr__(self):
        return "SemesterReport(w=%d,h=%d)" % (self.width, self.height)

    def draw(self):
        #initialize coordinates
        x = 0
        y = self.height

        #start drawing in black
        self.canv.setFillColorRGB(0,0,0)
        #write the semester title
        textobject = self.canv.beginText()
        y -= self.term_name_size
        textobject.setTextOrigin(x,y)
        textobject.setFont("PTSans-Regular", self.term_name_size)
        textobject.textLine(self.term_name)
        self.canv.drawText(textobject)

        #draw the table
        y -= self.courses_table.height
        self.courses_table.wrapOn(self.canv, x,y)
        self.courses_table.drawOn(self.canv, x,y)

        #draw the stats table
        y -= self.stats_table.height
        self.stats_table.wrapOn(self.canv,x,y)
        self.stats_table.drawOn(self.canv,x,y)

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
    spacer = Spacer(0,0.25 * INCH)

    #add components
    story.append(Header(request.user))
    for term in request.user.profile.get_terms_attended():
        story.append(spacer)
        story.append(SemesterReport(request.user, term))

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
