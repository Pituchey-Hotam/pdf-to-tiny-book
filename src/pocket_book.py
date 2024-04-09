import io
import os
from os import mkdir
from os.path import exists
from shutil import rmtree
from math import ceil, log, sqrt
from enum import Enum
# from hebrew_numbers import int_to_gematria
from PyPDF2 import PdfFileReader, PdfFileWriter

import src.pdfbooklet_new as pdfbooklet_new
from reportlab.lib.pagesizes import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont


# pdfmetrics.registerFont(TTFont('Hebrew', 'David.ttf'))


# from web_ui import *


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
    with open(pdf_path, "rb") as f:
        pdf = PdfFileReader(f)
        number_of_pages = pdf.getNumPages()
    f.close()
    return number_of_pages


def split(path, name_of_split, sp, length, bind_method="s", numbersP=False):
    # length += (4-(length%4))*(length%4 > 0)
    pdf = PdfFileReader(path)
    output = f"{name_of_split}"
    pdf_writer = PdfFileWriter()

    for page in range(sp, sp + length):
        if page < pdf.getNumPages():
            pdf_writer.addPage(pdf.getPage(page))
        else:
            addBP(pdf_writer, page, numbersP)
    if not bind_method == "s":
        pdf_writer.insertBlankPage(0)
        pdf_writer.addBlankPage()

    with open(output, "wb") as output_pdf:
        pdf_writer.write(output_pdf)
    output_pdf.close()


def addBP(pdfFileWriter, i, numbersP, letters=True):  # todo:
    """The function add blank page with number of page in notebook
    :param i: number of page
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFontSize(15)
    # if letters:
    #     can.setFont("Hebrew", 15)
    #     page_number_text = int_to_gematria(i + 1, False).replace('יה','טו').replace('יו','טז')
    #     print(page_number_text)
    #     page_number_text = ''.join(
    #         [page_number_text[len(page_number_text) - j - 1] for j in range(len(page_number_text))])
    #     can.drawString(A4[0] / 2, 10, page_number_text.encode("utf-8"))
    # else:
    can.drawString(A4[0] / 2, 10, str(i + 1))
    can.save()
    packet.seek(0)
    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileWriter()
    existing_pdf.addBlankPage(A4[0], A4[1])
    # add the "watermark" (which is the new pdf) on the existing page
    if numbersP:
        existing_pdf.pages[0].merge_page(new_pdf.pages[0])
    pdfFileWriter.addPage(existing_pdf.pages[0])


def split_Even_Odd(path, name_of_split):
    pdf = PdfFileReader(path)
    output_ev = f"{name_of_split}_even0.pdf"
    output_odd = f"{name_of_split}_odd0.pdf"
    pdf_writer_ev = PdfFileWriter()
    pdf_writer_odd = PdfFileWriter()
    number_of_pages = extract_num_of_pages(path)
    number_of_pages_plusblank = (
        0  # int((4 - (number_of_pages / 2 % 4)) * (number_of_pages / 2 % 4 > 0))
    )
    for page in range(number_of_pages + number_of_pages_plusblank):
        if page < number_of_pages:
            if page % 2 == 0:
                pdf_writer_odd.addPage(pdf.getPage(page))
            else:
                pdf_writer_ev.addPage(pdf.getPage(page))
        else:
            pdf_writer_ev.addBlankPage()
            pdf_writer_odd.addBlankPage()

    with open(output_ev, "wb") as output_pdf:
        pdf_writer_ev.write(output_pdf)
    output_pdf.close()
    with open(output_odd, "wb") as output_pdf:
        pdf_writer_odd.write(output_pdf)
    output_pdf.close()


def rotate(path, name_of_rotate, num_rot=3):
    pdf = PdfFileReader(path)
    number_of_pages = extract_num_of_pages(path)
    output = f"{name_of_rotate}"
    pdf_writer = PdfFileWriter()
    for page in range(number_of_pages):
        page_1 = pdf.getPage(page).rotateClockwise(90 * num_rot)
        pdf_writer.addPage(page_1)

    with open(output, "wb") as output_pdf:
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
    with open(output, "wb") as out:
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
    with open(output, "wb") as out:
        pdf_writer.write(out)
    out.close()


def pile_combine(file, path):
    tmp_num = extract_num_of_pages(file)
    split(file, path + "s1.pdf", 0, ceil(tmp_num / 2))
    split(file, path + "s2.pdf", ceil(tmp_num / 2), tmp_num)
    merge_sort_pdfs(path + "s1.pdf", path + "s2.pdf", file)


# ~~~~~~~~~~~~~~~~~
#     the final pdf maker ♪♫♪
# ~~~~~~~~~~~~~~~~~
def combineMethod(trash_file, num):
    odd_path = trash_file + "_odd_rotated" + num + ".pdf"
    even_path = trash_file + "_even_rotated" + num + ".pdf"
    pile_combine(odd_path, trash_file)
    pile_combine(even_path, trash_file)


def moreThan(trash_file, combine_method, eng, num=1):
    n = str(num)
    pev = str(num - 1)

    odd_path = trash_file + "_odd" + pev + ".pdf"
    even_path = trash_file + "_even" + pev + ".pdf"

    rotate(odd_path, trash_file + "_odd_rotated" + n + ".pdf")
    rotate(even_path, trash_file + "_even_rotated" + n + ".pdf")

    if combine_method == "v":
        combineMethod(trash_file, n)

    odd_path = trash_file + "_odd" + n + ".pdf"
    even_path = trash_file + "_even" + n + ".pdf"

    pdfbooklet_new.pdfbooklet(
        trash_file + "_odd_rotated" + n + ".pdf", odd_path, booklet=0, eng=eng
    )
    if num % 2 == 0:
        eng = eng == 0  # assign True/False value
    pdfbooklet_new.pdfbooklet(
        trash_file + "_even_rotated" + n + ".pdf", even_path, booklet=0, eng=eng
    )
    os.remove(trash_file + "_odd_rotated" + n + ".pdf")
    os.remove(trash_file + "_even_rotated" + n + ".pdf")
    return odd_path, even_path


def add_page_numbers(input_pdf, output_pdf, letters=True):  # todo:
    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    for page_number, page in enumerate(pdf_reader.pages, start=1):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.setFontSize(15)
        page_number_text = f"{page_number}"
        # if letters:
        #     c.setFont("Hebrew", 15)
        #     page_number_text = int_to_gematria(page_number_text, False).replace('יה','טו').replace('יו','טז')
        #     print(page_number_text)
        #     page_number_text = ''.join(
        #         [page_number_text[len(page_number_text) - i - 1] for i in range(len(page_number_text))])
        #     c.drawString(page.mediaBox.width / 2, 10, page_number_text.encode("utf-8"))
        # else:
        c.drawString(page.mediaBox.width / 2, 10, page_number_text)
        c.save()

        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        page.mergePage(new_pdf.pages[0])
        pdf_writer.addPage(page)

    with open(output_pdf, "wb") as output_file:
        pdf_writer.write(output_file)


def making_the_pdf(inputs, eng=0, page_Numbers=False, cutLines=True):
    if page_Numbers:
        add_page_numbers(inputs[0], inputs[0])
    inputs[0] = inputs[0].split(";")
    for input in inputs[0]:
        input = input.replace("\\", "/")

        file_name = input.split("/")[-1]
        old_path = input[: -len(file_name) - 1] + "/"

        dir_path = old_path + "trash " + file_name[:-4]
        path = dir_path[:] + "/"  # argv[2]+'\\'
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

        if number_of_pages < 64:
            if not notebook_len % 4 == 0:
                notebook_len = number_of_pages + (4 - (number_of_pages % 4))
            else:
                notebook_len = number_of_pages
        paths = []
        if not bind_method == "s":
            notebook_len -= 2

        for i in range(int(number_of_pages / notebook_len)):
            name_trash_file = trash_file + str(i + 1)
            split(
                file,
                name_trash_file + ".pdf",
                i * notebook_len,
                notebook_len,
                bind_method, page_Numbers
            )
            pdfbooklet_new.pdfbooklet(
                name_trash_file + ".pdf", name_trash_file + "let.pdf", eng=eng
            )
            os.remove(name_trash_file + ".pdf")
            paths.append(name_trash_file + "let.pdf")
        if (number_of_pages % notebook_len > 0):
            i = number_of_pages // notebook_len
            name_trash_file = trash_file + str(i + 1)
            n = number_of_pages % notebook_len
            if not bind_method == "s":
                n += 2
            nl = n
            if not n % 4 == 0:
                nl = n + (4 - n % 4)
            if not bind_method == "s":
                nl -= 2
            split(
                file,
                name_trash_file + ".pdf",
                i * notebook_len,
                nl,
                bind_method, page_Numbers
            )
            pdfbooklet_new.pdfbooklet(
                name_trash_file + ".pdf", name_trash_file + "let.pdf", eng=eng
            )
            os.remove(name_trash_file + ".pdf")
            paths.append(name_trash_file + "let.pdf")

        tf = trash_file
        if pages_per_sheet == 2:
            path = old_path
            trash_file = path + file_name
        final_path = trash_file + "_merged.pdf"
        merge_pdfs(paths, output=final_path)
        for i in range((number_of_pages // notebook_len) + (number_of_pages % notebook_len > 0)):
            os.remove(tf + str(i + 1) + "let.pdf")
        if pages_per_sheet > 2:
            split_Even_Odd(final_path, trash_file)
            os.remove(final_path)

            counter = 1
            while pages_per_sheet / (counter ** 2) > 1:
                odd_path, even_path = moreThan(trash_file, combine_method, eng, counter)
                os.remove(trash_file + '_even' + str(counter - 1) + '.pdf')
                os.remove(trash_file + '_odd' + str(counter - 1) + '.pdf')
                counter += 1

            final_path = old_path + file_name[:-4] + " ready to print.pdf"
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
            cut_line_width, cut_line_height = (
                A4  # Full width of the page # Full height of the page
            )
        else:
            can = canvas.Canvas(packet, pagesize=(A4[1], A4[0]))
            cut_line_height, cut_line_width = (
                A4  # Full width of the page # Full height of the page
            )
        cut_line_x = 0  # X position for the horizontal cut line
        cut_line_y = 0  # Y position for the vertical cut line

        can.setStrokeColorRGB(0, 0, 0)  # Black color for the cut lines
        can.setDash(1, 3)  # Set dash pattern (3 units on, 3 units off)
        can.setLineWidth(1)
        if log(numP, 2) % 2 == 0:
            for j in range(1, int(sqrt(numP))):
                # Add horizontal cut line
                can.line(
                    cut_line_x,
                    j * cut_line_height / int(sqrt(numP)),
                    cut_line_x + cut_line_width,
                    j * cut_line_height / int(sqrt(numP)),
                )
                if j % 2 == 0:
                    # Add vertical cut line
                    can.line(
                        j * cut_line_width / int(sqrt(numP)),
                        cut_line_y,
                        j * cut_line_width / int(sqrt(numP)),
                        cut_line_y + cut_line_height,
                    )
        else:
            y = int(sqrt(numP / 2))
            x = y * 2
            for j in range(1, y):
                # Add horizontal cut line
                can.line(
                    cut_line_x,
                    j * cut_line_height / y,
                    cut_line_x + cut_line_width,
                    j * cut_line_height / y,
                )
            for j in range(1, x):
                if j % 2 == 0:
                    can.line(
                        j * cut_line_width / x,
                        cut_line_y,
                        j * cut_line_width / x,
                        cut_line_y + cut_line_height,
                    )
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
