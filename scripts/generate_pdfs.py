import argparse
import slate
import os
import sys

from datetime import datetime

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(basedir)

#print(basedir)
from pyPdf import PdfFileWriter, PdfFileReader

import kaplanparse
from kaplanparse.parser import get_name




def parse_student_pages(doc):
    students = {}
    for i, page in enumerate(doc):
        if page == '\x0c': # form feed char/ blank page
            continue
        first, last = get_name(page)
        if (first, last) not in students:
            students[(first, last)] = []
        students[(first, last)].append(i)
    return students

def get_doc_text(filepath):
    # doesnt matter if use SAT or ACT parser:
    pdf = kaplanparse.act.ACTParser(filepath)
    doc = pdf.get_doc_text()
    replace_unicode_chars = lambda s: s.replace('\xc2\xa0', ' ')
    doc = map(replace_unicode_chars, doc)
    return doc


def get_student_pages(filepath):
    doc = get_doc_text(filepath)
    return parse_student_pages(doc)


def generate_pdfs(filepath, students, outputdir, test_type, date=None):
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    inputpdf = PdfFileReader(open(filepath, "rb"))

    for (first_name, last_name), pages in students.items():
        filename = "{test_type}_{date}_{first_name}_{last_name}.pdf".format(test_type=test_type,
                                                                        date=date, first_name=first_name,
                                                                       last_name=last_name)
        output = PdfFileWriter()
        for pagenum in pages:
            output.addPage(inputpdf.getPage(pagenum))
        with open(os.path.join(outputdir, filename), "wb+") as fout:
            output.write(fout)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split Kaplan SAT/ACT report into individual PDFs for each student.")
    parser.add_argument('-i', '--input', help="Filepath to PDF of Kaplan Diagnostic report")
    parser.add_argument('-t', '--testtype', help="Test type either SAT or ACT", choices=["act", "sat"])
    parser.add_argument('-o', '--output', help="Directory path to dump pdfs into")

    args = parser.parse_args()
    students = get_student_pages(args.input)
    generate_pdfs(args.input, students, args.output, test_type=args.testtype.upper())
