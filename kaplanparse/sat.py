import pandas as pd

from parser import parse_section, get_name, get_test_date,  \
                    SectionReport, KaplanReport, KaplanParser
from percentiles import SAT_TO_ACT


__all__ = [
    'SATParser',
    'to_sat_report',
    'KaplanSATReport'
]

class SATMathReport(SectionReport):
    name = "Math"


class SATReadingWritingReport(SectionReport):
    name = "Evidence-Based Reading & Writing"


# class SATWritingReport(SectionReport):
#     name = "WRITING"
#
#     def __init__(self, score, correct, incorrect, omitted, essay=None):
#         super(SATWritingReport, self).__init__(score, correct, incorrect, omitted)
#         self.essay = essay


class StudentSATReport(object):

    def __init__(self, first_name, last_name, test_date, math, reading_writing):
        self.first_name = first_name
        self.last_name = last_name
        self.test_date = test_date
        self.math = math
        self.reading_writing = reading_writing
        # self.reading = reading

    def __repr__(self):
        return "<%s %s %s>" % (self.__class__.__name__, self.name, self.score)

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def score(self):
        return self.math.score + self.reading_writing.score

    @property
    def equivalent_act(self):
        sat_score = int(self.score)
        act_score_found = False
        while sat_score > 0 and not act_score_found:
            try:
                act_score = SAT_TO_ACT[sat_score]
                act_score_found = True
            except KeyError:
                sat_score -= 10
                continue
        return act_score


class KaplanSATReport(KaplanReport):

    def to_dataframe(self):
        data = [(s.first_name, s.last_name, s.score, s.math.score,
                 s.reading_writing.score, s.equivalent_act)
                for s in self.student_reports]
        columns = ['first_name', 'last_name', 'composite', 'math',
                   'reading_writing', 'equivalent_act']
        return pd.DataFrame(data, columns=columns)


class SATParser(KaplanParser):

    def to_report(self, students):
        reports = []
        for name, student in students.items():
            math = parse_section(student[1], SATMathReport)
            reading_writing = parse_section(student[2], SATReadingWritingReport)
            # writing = parse_section(student[2], SATWritingReport)
            first_name, last_name = get_name(student[1])
            test_date = get_test_date(student[1])
            student_report = StudentSATReport(first_name, last_name, test_date, math, reading_writing)
            reports.append(student_report)

        kaplan_report = KaplanSATReport(reports)
        return kaplan_report

def to_sat_report(filepath):
    parser = SATParser(filepath)
    return parser.parse()
