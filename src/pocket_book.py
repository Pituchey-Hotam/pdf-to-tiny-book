import io
# import os
from os import mkdir
from os.path import exists
from shutil import rmtree
from math import ceil, log, sqrt
from threading import Thread
from enum import Enum

from PyPDF2 import PdfFileReader, PdfFileWriter
from PySimpleGUI import theme, Button, Text, Input, InputText, FilesBrowse, Window, WIN_CLOSED, Image as guiImage

import pdfbooklet_new as pdfbooklet_new
from reportlab.lib.pagesizes import *
from reportlab.pdfgen import canvas
from ui_settings import *
from webUI import *


class PageSize(Enum):
    """
    An enum class for page size representation.
    The value of the page size is how many pages in this size
    fit in an A4 page.
    """

    A5 = 2
    A6 = 4
    A7 = 8

# -----------------------
#     pdf manipulation
# ------------------------

def extract_num_of_pages(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        number_of_pages = pdf.getNumPages()
    f.close()
    return number_of_pages


def split(path, name_of_split, sp, length, bind_method='s'):
    # length += (4-(length%4))*(length%4 > 0)
    pdf = PdfFileReader(path)
    output = f'{name_of_split}'
    pdf_writer = PdfFileWriter()

    for page in range(sp, sp + length):
        if page < pdf.getNumPages():
            pdf_writer.addPage(pdf.getPage(page))
        else:
            addBP(pdf_writer, page)
    if not bind_method == 's':
        pdf_writer.insertBlankPage(0)
        pdf_writer.addBlankPage()

    with open(output, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    output_pdf.close()


def addBP(pdfFileWriter, i):
    """The function add blank page with number of page in notebook
    :param i: number of page
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFontSize(20)
    can.drawString(A4[0] / 2, 10, str(i))
    can.save()
    packet.seek(0)
    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileWriter()
    existing_pdf.addBlankPage(A4[0], A4[1])
    # add the "watermark" (which is the new pdf) on the existing page
    existing_pdf.pages[0].merge_page(new_pdf.pages[0])
    pdfFileWriter.addPage(existing_pdf.pages[0])


def split_Even_Odd(path, name_of_split):
    pdf = PdfFileReader(path)
    output_ev = f'{name_of_split}_even.pdf'
    output_odd = f'{name_of_split}_odd.pdf'
    pdf_writer_ev = PdfFileWriter()
    pdf_writer_odd = PdfFileWriter()
    number_of_pages = extract_num_of_pages(path)
    number_of_pages_plusblank = 0  # int((4 - (number_of_pages / 2 % 4)) * (number_of_pages / 2 % 4 > 0))
    for page in range(number_of_pages + number_of_pages_plusblank):
        if page < number_of_pages:
            if page % 2 == 0:
                pdf_writer_odd.addPage(pdf.getPage(page))
            else:
                pdf_writer_ev.addPage(pdf.getPage(page))
        else:
            pdf_writer_ev.addBlankPage()
            pdf_writer_odd.addBlankPage()

    with open(output_ev, 'wb') as output_pdf:
        pdf_writer_ev.write(output_pdf)
    output_pdf.close()
    with open(output_odd, 'wb') as output_pdf:
        pdf_writer_odd.write(output_pdf)
    output_pdf.close()


def rotate(path, name_of_rotate, num_rot=3):
    pdf = PdfFileReader(path)
    number_of_pages = extract_num_of_pages(path)
    output = f'{name_of_rotate}'
    pdf_writer = PdfFileWriter()
    for page in range(number_of_pages):
        page_1 = pdf.getPage(page).rotateClockwise(90 * num_rot)
        pdf_writer.addPage(page_1)

    with open(output, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    output_pdf.close()


def merge_pdfs(paths, output):
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)
    out.close()


def merge_sort_pdfs(path1, path2, output):
    pdf_writer = PdfFileWriter()
    pdf1 = PdfFileReader(path1)
    pdf2 = PdfFileReader(path2)
    number_of_pages = extract_num_of_pages(path1)
    for page in range(number_of_pages):
        pdf_writer.addPage(pdf1.getPage(page))
        pdf_writer.addPage(pdf2.getPage(page))

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)
    out.close()


def pile_combine(file, path):
    tmp_num = extract_num_of_pages(file)
    split(file, path + 's1.pdf', 0, ceil(tmp_num / 2))
    split(file, path + 's2.pdf', ceil(tmp_num / 2), tmp_num)

    merge_sort_pdfs(path + 's1.pdf', path + 's2.pdf', file)


# ~~~~~~~~~~~~~~~~~
#     the final pdf maker ♪♫♪
# ~~~~~~~~~~~~~~~~~
def combineMethod(trash_file, num):
    odd_path = trash_file + '_odd_rotated' + num + '.pdf'
    even_path = trash_file + '_even_rotated' + num + '.pdf'
    pile_combine(odd_path, trash_file)
    pile_combine(even_path, trash_file)


def moreThan(trash_file, combine_method, eng, num=1):
    n = str(num)
    pev = str(num - 1)
    if pev == '0':
        pev = ''

    odd_path = trash_file + '_odd' + pev + '.pdf'
    even_path = trash_file + '_even' + pev + '.pdf'

    rotate(odd_path, trash_file + '_odd_rotated' + n + '.pdf')
    rotate(even_path, trash_file + '_even_rotated' + n + '.pdf')

    if combine_method == 'v':
        combineMethod(trash_file, n)

    odd_path = trash_file + '_odd' + n + '.pdf'
    even_path = trash_file + '_even' + n + '.pdf'

    pdfbooklet_new.pdfbooklet(trash_file + '_odd_rotated' + n + '.pdf', odd_path, booklet=0, eng=eng)
    if num % 2 == 0:
        eng = (eng == 0)
    pdfbooklet_new.pdfbooklet(trash_file + '_even_rotated' + n + '.pdf', even_path, booklet=0, eng=eng)

    return odd_path, even_path


def add_page_numbers(input_pdf, output_pdf):
    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    for page_number, page in enumerate(pdf_reader.pages, start=1):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.setFontSize(20)
        page_number_text = f"{page_number}"
        c.drawString(page.mediaBox.width / 2, 10, page_number_text)
        c.save()

        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        page.mergePage(new_pdf.pages[0])
        pdf_writer.addPage(page)

    with open(output_pdf, "wb") as output_file:
        pdf_writer.write(output_file)


def making_the_pdf(inputs, eng=0, pNumber=False, cutLines=True):
    if pNumber:
        add_page_numbers(inputs[0], inputs[0])
    inputs[0] = inputs[0].split(';')
    for inp in inputs[0]:
        inp = inp.replace('\\', '/')

        file_name = inp.split('/')[-1]
        old_path = inp[:-len(file_name) - 1] + '/'

        dir_path = old_path + 'trash ' + file_name[:-4]
        path = dir_path[:] + '/'  # argv[2]+'\\'
        if not exists(path):
            mkdir(path)

        file = old_path + file_name  # argv[1]+argv[2]+'.pdf'
        trash_file = path + file_name

        notebook_len = int(inputs[1])
        pages_per_sheet = int(inputs[2])
        bind_method = inputs[3]
        combine_method = inputs[4]
        eng = inputs[5]
        number_of_pages = extract_num_of_pages(file)

        paths = []
        if not bind_method == 's':
            notebook_len -= 2
        for i in range(int(number_of_pages / notebook_len) + (number_of_pages % notebook_len > 0)):
            name_trash_file = trash_file + str(i + 1)
            split(file, name_trash_file + '.pdf', i * notebook_len, notebook_len, bind_method)
            pdfbooklet_new.pdfbooklet(name_trash_file + '.pdf', name_trash_file + 'let.pdf', eng=eng)
            paths.append(name_trash_file + 'let.pdf')
        if pages_per_sheet == 2:
            path = old_path
            trash_file = path + file_name
        final_path = trash_file + '_merged.pdf'
        merge_pdfs(paths, output=final_path)

        if pages_per_sheet > 2:
            split_Even_Odd(final_path, trash_file)

            counter = 1
            while pages_per_sheet / (counter ** 2) > 1:
                # print(pages_per_sheet / (counter ** 2))
                # print(counter)
                odd_path, even_path = moreThan(trash_file, combine_method, eng, counter)
                counter += 1

            final_path = old_path + file_name[:-4] + ' ready to print.pdf'
            merge_sort_pdfs(odd_path, even_path, final_path)

        rmtree(dir_path, ignore_errors=False)
    if cutLines:
        add_dashed_cut_line(final_path, pages_per_sheet)


def add_dashed_cut_line(file, numP):
    pdf = PdfFileReader(file)
    output_pdf = PdfFileWriter()
    for i in range(len(pdf.pages)):
        packet = io.BytesIO()
        if log(numP, 2) % 2 == 0:
            can = canvas.Canvas(packet, pagesize=A4)
            cut_line_width, cut_line_height = A4  # Full width of the page # Full height of the page
        else:
            can = canvas.Canvas(packet, pagesize=(A4[1], A4[0]))
            cut_line_height, cut_line_width = A4  # Full width of the page # Full height of the page
        cut_line_x = 0  # X position for the horizontal cut line
        cut_line_y = 0  # Y position for the vertical cut line

        can.setStrokeColorRGB(0, 0, 0)  # Black color for the cut lines
        can.setDash(3, 3)  # Set dash pattern (3 units on, 3 units off)
        can.setLineWidth(2)
        if log(numP, 2) % 2 == 0:
            for j in range(1, int(sqrt(numP))):
                # Add horizontal cut line
                can.line(cut_line_x, j * cut_line_height / int(sqrt(numP)), cut_line_x + cut_line_width,
                         j * cut_line_height / int(sqrt(numP)))
                if j % 2 == 0:
                    # Add vertical cut line
                    can.line(j * cut_line_width / int(sqrt(numP)), cut_line_y, j * cut_line_width / int(sqrt(numP)),
                             cut_line_y + cut_line_height)
        else:
            y = int(sqrt(numP / 2))
            x = y * 2
            for j in range(1, y):
                # Add horizontal cut line
                can.line(cut_line_x, j * cut_line_height / y, cut_line_x + cut_line_width,
                         j * cut_line_height / y)
            for j in range(1, x):
                if j % 2 == 0:
                    can.line(j * cut_line_width / x, cut_line_y, j * cut_line_width / x,
                             cut_line_y + cut_line_height)
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        pdf.pages[i].merge_page(new_pdf.pages[0])
        output_pdf.addPage(pdf.pages[i])  # Add the modified page to the output
    with open(file, "wb") as output:
        output_pdf.write(output)


# ~~~~~~~~~~~~~~~~~
#     main ♪♫♪
# ~~~~~~~~~~~~~~~~~


def main(inputs):
    start = True
    while start:
        start = False
        th = Thread(target=making_the_pdf, args=[inputs, 1])
        th.start()

        win_wait_layout = [[Text(text="please wait, this may take a few minutes")]]
        window_wait = Window("thank U", win_wait_layout, size=(300, 50))

        while th.is_alive():
            window_wait.read(timeout=1)
            pass
        window_wait.close()

        win_end_layout = [[Text(text="your file is ready")],
                          [Text(text="have a nice day")],
                          [Button(button_text="Home page", key='-again-')]]
        window_end = Window("thank U", win_end_layout, size=(200, 100))

        while True:
            event, values = window_end.read()
            if event == WIN_CLOSED:
                break
            if event == '-again-':
                start = True
                break
        window_end.close()


if __name__ == '__main__':
    WEB_UI()
