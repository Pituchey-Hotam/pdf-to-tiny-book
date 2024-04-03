import os
from uuid import uuid4
from datetime import datetime
import csv
from dataclasses import dataclass
from math import log2
import threading

from io import BytesIO
from src.pocket_book import making_the_pdf
from flask import Flask, render_template, request, redirect, send_file, url_for
from pathlib import Path

prod = 0

class Self_page:
    def __init__(self, function_name, language):
        self.self_function=function_name
        self.self_lang=language

class PdfFormQuestions:
    def __init__(self, page_types, merge_types, book_languages):
        self.page_types = page_types
        self.merge_types = merge_types
        self.book_languages = book_languages

@dataclass
class Book:
    filename: str
    timestamp: str
    name: str
    author: str
    language: str
    genre: str
    era: str
    pages_per_sheet: int


ENGLISH_TEXT = [
    "Booklet Project",
    "Choose a file",
    "Enter the number of pages in each booklet (In multiples of 4. the standard is 32): ",
    "Gluing",
    "Sewing",
    "Book's Size",
    "Create Booklet",
    "Hebrew",
    "English",
    "Book's language",
    "Booklet options",
    "Add cut lines?",
    "Add page numbering?",
    "Can we save the result PDF for other user?",
    "Contributing Book",
    "Book's Name",
    "Author's Name",
    "Book's Genre",
    "Book's Era",
    "small pages in normal page",
    "Advanced Settings",
    "Show advanced settings",
    "Book creation process",
    "Large books (more than 64 pages) will be printed in more than one booklets that need to be glued or sewed together.",
    "It can be done in 2 ways:",
    "Gluing: the program will leave a blank page at the end and start of each booklet, so they can be glued together.",
    "Sewing: sewing all the booklets to one book using a needle and a thread.",
    "Video tutorial",
    "Number of pages in each booklet",
    "It is recommened to print large books in more than one booklet.",
    "The program defined automatically how many pages each booklet will have, but here we can define it manually. Please enter a number that is divided by 4.",
    'Found a bug or problem? Tell us at',
    'Please don\'t upload files guarded by copyrights',
    "regular page size",
    "half of an A4 page",
    "quarter of an A4 page",
    "eigth of an A4 page",
    "sixteenth of an A4 page"
]

HEBREW_TEXT = [
    "ספרי כיס",
    "בחר קובץ",
    "הכנס את מספר העמודים בכל מחברת (בכפולות של 4, הסטנדרט הוא 32)",
    "מודבק",
    "תפור",
    "גודל ספר",
    "צור ספר כיס",
    "עברית",
    "אנגלית",
    "באיזו שפה הספר?",
    "אופציות הדפסה נוספות",
    "האם להוסיף קווי חיתוך?",
    "האם להוסיף מספרי עמודים? (זמנית לא עובד)",# todo: להוסיף שאלה האם מספרי העמודים יהיו בספרות או באותיות(האותיות רק בעברית)
    "האם אנחנו יכולים להציע את הספרון לעוד משתמשים?",
    "הוספת ספר למאגר",
    "שם הספר",
    "שם המחבר",
    "תחום עיסוק של הספר",
    "תקופת חיבור הספר",
    "עמודים קטנים בעמוד רגיל",
    "הגדרות מיוחדות",
    'הצג הגדרות מתקדמות',
    'אופן יצירת הספר',
    'ספרים שאורכם מעל 64 עמודים יודפסו במספר מחברות שיש צורך לחבר אותן לספר אחד.',
    'ניתן לעשות זאת בשתי דרכים: ',
    'הדבקה: התוכנה תשאיר עמוד ריק בתחילת וסוף כל מחברת, כך שניתן להדביק בקלות את המחברות אחת לשנייה. ',
    'תפירה: תפירת המחברות לספר אחד ע"י חוט ומחט - חיבור מעט חזק יותר, אך קשה יותר להכנה.',
    'סרטון הדרכה',
    'מספר עמודים בכל מחברת',
    'ספרים שאורכם מעל 64 עמודים מומלץ להדפיס במספר מחברות שיש צורך לחבר אותן לספר אחד.',
    'התוכנה מגדירה באופן אוטומטי כמה עמודים יהיו בכל מחברת, אך כאן ניתן להגדיר גם באופן ידני מספר עמודים למחברת. יש להזין מספר שמתחלק ב4.',
    'מצאתם בעיה? דברו איתנו!',
    'נא לא להעלות קבצים המוגנים בזכויות יוצרים!',
    "גודל דף סטנדרטי",
    "חצי דף A4",
    "רבע דף A4",
    "שמינית דף A4",
    "אחד חלקי שש עשרה מדף A4"]

EN_HOME_TEXT = [
    "Welcome",
    "Video Title",
    "Create your own PDF Booklet",
    "Community Created Booklets",
    "Do you want to print a pocket book from the web?",
    "",
    "Using this program you can print fast and easily any document you'll want in a personally-tailored pocket book edition.",
    "How the Program Works?",
    "Organize the text for printing in a single big PDF document",
    "Please note that as the book gets smaller, the text in the document should be larger",
    "Choose the book's size, number of pagesg and other settings",
    "Click \'Create Booklet\' and download the pdf file",
    "Print, Cut and Connect the pages to a book following the instructions",
    "Start reading!"
]

HE_HOME_TEXT = [
    'ברוכים הבאים',
    'סרטון תדמית',
    'התחילו עכשיו!',
    'ספרונים של אחרים',
    'רוצה להדפיס ספר מהאינטרנט במהדורת כיס?',
    'כתבת סיכומים על הלימוד ורוצה לעשות חזרות בקלות?',
    'בעזרת התוכנה תוכל להדפיס בקלות ובמהירות כל מסמך שתרצה במהדורת כיס מותאמת אישית!',
    'איך התוכנה עובדת?',
    'מסדרים את כל הטקסט להדפסה במסמך אחד מסודר ומעלים לאתר כקובץ PDF',
    'חשוב לשים לב שככל שמדפיסים ספרון בגודל קטן יותר, כך צריך להגדיל את גודל הכתב',
    'בוחרים את גודל הספר, מספר העמודים ועוד הגדרות חשובות',
    'לוחצים \'צור ספר כיס\' ומקבלים קובץ pdf מוכן להדפסה',
    'מדפיסים, גוזרים, ומחברים את הדפים לספר כיס לפי ההוראות',
    'מתחילים ללמוד:)'
]

EN_CARDS = [
    'Community Created Booklets',
    'Book\'s / Author\'s Name:',
    "Book's Era",
    "Book's Genre",
    "Author",
    "Language",
    "Genre",
    "Era",
    "Book\'s Size",
    'Download!',
    "Search Filters",
    "Hebrew",
    "English"
]

HE_CARDS = [
    'קבצים שיצרו אחרים',
    'שם הספר / המחבר:',
    "תחום עיסוק של הספר",
    "תקופת חיבור הספר",
    "מחבר",
    "שפה",
    "תחום",
    "תקופה",
    "גודל ספר",
    'הורדה!',
    "מסננים",
    "עברית",
    "אנגלית"

]

SFO_OPTIONS = {'eras': ['תנ"ך', 'תנאים', 'אמוראים', 'גאונים', 'ראשונים', 'אחרונים'],
        'genres': ['תנ"ך', 'מקורות תנאיים', 'תלמוד ועיון', 'הלכה', 'מחשבה', 'מוסר', 'היסטוריה', 'מנייני מצוות', 'קבלה', 'חסידות', 'ספרות חול']}

class PdfFormText:
    # this class is the text container for the web page after language choice
    def __init__(self, language):
        if language == "english":
            text = ENGLISH_TEXT
            self.language_format = ["en", "ltr"]
            self.booklet_parameters = "Booklet parameters"
        else:
            text = HEBREW_TEXT
            self.language_format = ["he", "rtl"]
            self.booklet_parameters = "נתוני ספר כיס"
        self.page_header, self.choose_flie_header = text[0], text[1]
        self.inst_pages = text[2]
        self.merge_types = [text[3], text[4]]
        self.page_type_title = text[5]
        self.submit_text = text[6]
        self.languges = [text[7], text[8]]
        self.language_header = text[9]
        self.booklet_options = text[10]
        self.cut_lines = text[11]
        self.page_numbering = text[12]
        self.page_type_explanation = [text[19], text[33], text[34], text[35], text[36], text[37]]

        self.save_for_others = text[13]
        self.sfo_title = text[14]
        self.sfo_book_name = text[15]
        self.sfo_author = text[16]
        self.sfo_genre = text[17]
        self.sfo_era = text[18]
        self.sfo_copyright = text[32]

        self.advanced_header = [text[20], text[21]]
        self.merge_explain = [text[22], text[23], text[24], text[25], text[26], text[27]]
        self.inst_pages_explain = [text[28], text[29], text[30]]

        self.footer_text = [text[31]]

        self.sfo_options = SFO_OPTIONS

if not prod:
    USER_FILES_PATH = './user_files/'
    DB_PATH = './books_db/'
if prod:
    USER_FILES_PATH = '/home/pitucheyhotam/user_files/'
    DB_PATH = '/home/pitucheyhotam/books_db/'

TITLE = 'ספרי כיס | Pocket Book'

def find_new_pdf(original_name):
    original_name_part = Path(original_name).stem
    list_dir = os.listdir(USER_FILES_PATH)
    files = [file for file in list_dir if original_name_part in file and original_name!=file]
    return files[0]

def delete_files(original_name):
    original_name_part = original_name.split('.')[0]
    list_dir = os.listdir(USER_FILES_PATH)  # get the original and other new file
    files = [file for file in list_dir if original_name_part in file]
    for file in files:
        os.remove(USER_FILES_PATH + file)


def get_book_db():
    with open(DB_PATH + 'index.csv', 'r', encoding='utf-8') as index_file:
        # Choosing new name for storting the file (adding uuid to mitigate duplicates)
        reader = csv.reader(index_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        reader.__next__() # Skip headers
        books = []
        for row in reader:
            if len(row) == 0: continue # Empty line in csv file

            try:
                books.append(Book(*row)) # Unpacks row, can be changed if Book object data isn't identical to index.csv data.
            except:
                continue

        return books


def save_to_db(file, book_name, author, book_lang, era, genre, pages_per_sheet):
    with open(DB_PATH + 'index.csv', 'a', encoding='utf-8', newline='') as index_file:
        # Choosing new name for storting the file (adding uuid to mitigate duplicates)
        # filename = Path(file.filename).stem + '-' + str(uuid4())[:5] + Path(file.filename).suffix
        filename = book_name + '-' + str(uuid4())[:5] + Path(file.filename).suffix
        file.filename=filename
        file.save(DB_PATH + filename)

        writer = csv.writer(index_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow([filename, datetime.now(), book_name, author, book_lang, era, genre, pages_per_sheet])

making_threads_queue = {}
def make_pdf_file(inputs, page_numbering_bool, cut_lines_bool):
    making_the_pdf(inputs, eng=0, page_Numbers=page_numbering_bool, cutLines=cut_lines_bool)


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main_url():
    return redirect("/he/home/")

@app.route("/<string:language>/home/", methods=['GET', 'POST'])
def home(language):
    if language=='he':
        form_text = PdfFormText('hebrew')
        home_text = HE_HOME_TEXT
    else:
        form_text = PdfFormText('english')
        home_text = EN_HOME_TEXT
    page = Self_page('home',language)
    return render_template("home.html", Title=TITLE,
                            form_text=form_text, home_text=home_text, self_page=page)


@app.route("/<string:language>/past_books/", methods=['GET', 'POST'])
def past_books(language):
    if request.method == 'POST':
        filename = request.form.get('file_name')
        with open(DB_PATH + filename, "rb") as fh:
            buf = BytesIO(fh.read())
        return send_file(buf, as_attachment=True, mimetype="text/plain", download_name=filename)

    if language=='he':
        form_text = PdfFormText('hebrew')
        cards_text = HE_CARDS
    else:
        form_text = PdfFormText('english')
        cards_text = EN_CARDS

    books = get_book_db()
    page = Self_page('past_books',language)
    return render_template("past_books.html", Title=TITLE,
                            form_text=form_text, cards_text=cards_text, self_page=page,
                            books=books, sfo_options = SFO_OPTIONS, int=int, log2=log2)

@app.route("/<string:language>/create_pdf_form", methods=['GET', 'POST'])
def main_site_page(language):
    if language=='he':
        form_text = PdfFormText('hebrew')
    else:
        form_text = PdfFormText('english')
    merge_types = form_text.merge_types
    book_languages = form_text.languges
    pages_type = ['A4', 'A5', 'A6', 'A7', 'A8', 'A9']
    form_data = PdfFormQuestions(pages_type, merge_types, book_languages)
    page = Self_page('main_site_page',language)
    return render_template("full_form.html", Title=TITLE, form_data=form_data, form_text=form_text, self_page=page)

@app.route("/<string:language>/creating/<string:uuid>", methods=['GET'])
def creating(language, uuid):
    if language=='he':
        form_text = PdfFormText('hebrew')
    else:
        form_text = PdfFormText('english')

    page = Self_page('creating',language)

    return render_template("creating.html", Title=TITLE, form_text=form_text, self_page=page, uuid=uuid)

@app.route('/<string:url_language>/download', methods=['GET', 'POST'])  # download - this function doesn't represent any web page
# it's opening a new tab to download the output file and then closes it.
def download(url_language):
    user_files = USER_FILES_PATH
    if request.method == 'POST':
        pdf_file = request.files['file']
        try:  # recomendeation to use type instead of try. I dont understand who to implement without crash...
            number_of_pages_booklet = int(request.form['pages'])
            number_of_pages_sheet = int(request.form['pages_per_sheet'])
        except:
            print('error in number of pages or in number of pages per sheet')
            return

        merge_type = request.form['pdf_merge_type']
        language = request.form['book_lang']
        # future data for usage...
        # page_type = request.form['page_size']
        cut_lines = request.form.get('cut_lines')
        save_for_others = request.form.get('save_for_others')
        if cut_lines == 'cut_lines':
            cut_lines_bool = True
        else:
            cut_lines_bool = False

        page_numbering = request.form.get('page_numbering')
        if page_numbering == 'page_numbering':
            page_numbering_bool = True
        else:
            page_numbering_bool = False

        if merge_type == 'gluing' or merge_type == 'מודבק':
            merge_type_text = ''
        else:
            merge_type_text = 's'

        if language=='עברית' or language=='Hebrew':
            language_num = 0
        else:
            language_num = 1

        if 1:  # not clear when to use this option... until now only used with 'v' option...
            combine_method = 'v'
        else:
            combine_method = ''  # ?

        if save_for_others:
            book_name = request.form.get('sfo_book_name')
            author = request.form.get('sfo_author')
            genre = request.form.get('sfo_genre')
            era = request.form.get('sfo_era')

            pages_per_sheets = number_of_pages_sheet # Using user's pages per sheet choice
            book_lang = language_num # Using user's book's language choice

            # save_to_db(pdf_file, "חוטב עצים ושואב מים", "הרא\"ש קטן", book_lang, "אחרונים", "מוסר", 2)
            save_to_db(pdf_file, book_name, author, book_lang, genre, era, pages_per_sheets)
            pdf_file.seek(0) # After saving once need to seek to start

        pdf_file.save(user_files + pdf_file.filename)  # physically saves the file at current path of python!

        # create the new pdf
        inputs = [user_files + pdf_file.filename, number_of_pages_booklet, number_of_pages_sheet,
                    merge_type_text, combine_method, language_num]
        
        make_pdf_thread = threading.Thread(target=make_pdf_file, args=(inputs, page_numbering_bool, cut_lines_bool,))
        make_pdf_thread.start()
        thread_uuid = uuid4().hex
        making_threads_queue[thread_uuid] = {'file_name': pdf_file.filename, 'thread': make_pdf_thread}
    
        print(url_language)
        return redirect(f'/{url_language}/creating/{thread_uuid}')


@app.route('/finished/<string:uuid>')
def finished(uuid):
    making_thread = making_threads_queue.get(uuid, None)

    if not making_thread:
        return {'code': 1, 'desc': "file doesn't exists."}

    thread_finished = not making_thread['thread'].is_alive()
    return {'code': 0 if thread_finished else 2, 'desc': 'file is ready' if thread_finished else 'file isn\'t ready'}


@app.route('/get_file/<string:uuid>', methods=['GET'])
def get_file(uuid):
    making_thread = making_threads_queue.get(uuid, None)

    if not making_thread:
        return {'code': 1, 'desc': "file doesn't exists."}

    thread = making_thread['thread']
    filename = find_new_pdf(making_thread['file_name'])

    if thread and not thread.is_alive():
        with open(USER_FILES_PATH + filename, "rb") as fh:
            buf = BytesIO(fh.read())
        delete_files(making_thread['file_name'])

        making_threads_queue.pop(uuid)
        return send_file(buf, as_attachment=True, mimetype="text/plain", download_name=filename)
    else:
        return {'code': 2, 'desc': "file isn't ready."}
        

if __name__ == '__main__':
    # "192.168.154.195" - example of current IP that might change and required for testing on
    # other devices, "127.0.0.1" - self IP for basic coding
    # debug=True - only before production to make working easy

    # app.run(host="192.168.154.195", port=8000, debug=True)
    app.run(host="127.0.0.1", port=8000, debug=True)
    # pass
