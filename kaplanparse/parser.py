import abc
import re
import logging

logger = logging.getLogger(__name__)

import slate
import pandas as pd


def parse_section(page, report):
    # assert issubclass(report, SectionReport)
    parser = SectionParser(page, report)
    return parser.to_report()


def get_name(page):
    raw_text = re.findall('(?<=Name:)(.*)(?=Test Date)', page)[0]
    parts = raw_text.strip().split()
    if len(parts) == 2:
        first, last = parts
    # some students have middle names
    elif len(parts) == 3:
        first, _, last = parts
    else:
        raise ValueError("Can not parse student name: %s" % parts)
    return first, last

def get_test_date(page):
    raw_text = re.search('Test Date:(.*)Page\s[0-9]\sof\s[0-9]', page).groups()[0]
    return pd.to_datetime(raw_text)

def get_page_num(page):
    raw_text = re.search('Page\s([0-9])\sof\s[0-9](?:SAT|ACT)', page).groups()[0]
    return int(raw_text)


class SectionReport(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, score, correct, incorrect, omitted):
        self.score = score
        self.correct = correct
        self.incorrect = incorrect
        self.omitted = omitted

    def __add__(self, other):
        return self.score + other.score

    @abc.abstractproperty
    def name(self):
        pass

    @property
    def percent_correct(self):
        return float(self.correct) / self.total_questions

    @property
    def total_questions(self):
        return self.correct + self.incorrect + self.omitted



class SectionParser(object):

    def __init__(self, page, report):
        self.page = page
        self.report = report

    def get_correct(self):
        return self.get_integer(self.page, 'Correct', 'Incorrect')

    def get_incorrect(self):
        return self.get_integer(self.page, 'Incorrect', 'Omitted')

    def get_score(self):
        return self.get_integer(self.page, 'Scaled Score', 'Percentage')

    def get_omitted(self):
        return self.get_integer(self.page, 'Omitted', '(Scaled Score|% Correct)')

    def get_integer(self, page, start_text, end_text):
        name = self.report.name
        # truncate page because of duplicates e.g. 'READING' and 'WRITING'
        # sections on one page.
        # really big hack. Not sure how to deal with this because teh pdf
        # string looks like Evidence\xc2\xadBased Reading & Writing
        if 'Evidence-Based Reading & Writing' == name:
            page = page[page.find('Based Reading & Writing'):]
        else:
            page = page[page.find(name):]

        pattern = '{start_text}([0-9]+){end_text}'.format(start_text=start_text, end_text=end_text)
        raw_text = re.search(pattern, page).groups()[0]
        return int(raw_text)

    def to_report(self):
        correct = self.get_correct()
        incorrect = self.get_incorrect()
        omitted = self.get_omitted()
        score = self.get_score()
        return self.report(score, correct, incorrect, omitted)


class KaplanParser(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, filepath):
        self.filepath = filepath
        self.doc = None

    @abc.abstractmethod
    def to_report(self):
        pass

    def get_doc_text(self):
        with open(self.filepath) as f:
            doc = slate.PDF(f)
        return doc

    def parse(self):
        doc = self.get_doc_text()
        replace_unicode_chars = lambda s: s.replace('\xc2\xa0', ' ')
        doc = map(replace_unicode_chars, doc)
        students = self.parse_students(doc)
        kaplan_report = self.to_report(students)
        return kaplan_report

    def parse_students(self, doc):
        students = {}
        for page in doc:
            if page == '\x0c': # form feed char/ blank page
                continue
            first, last = get_name(page)
            if (first, last) not in students:
                students[(first, last)] = {}
            page_num = get_page_num(page)
            students[(first, last)][page_num] = page
        return students


class KaplanReport(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, student_reports):
        self.student_reports = student_reports

    def __repr__(self):
        return "<%s %s students>" % (self.__class__.__name__, len(self.student_reports))

    def __iter__(self):
        return iter(self.student_reports)

    @abc.abstractmethod
    def to_dataframe(self):
        pass
