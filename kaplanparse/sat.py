import pandas as pd

from parser import parse_section, get_name, get_test_date,  \
                    SectionReport, KaplanReport, KaplanParser
from percentiles import SAT_TO_ACT



class SATMathReport(SectionReport):
    name = "MATH"


class SATReadingReport(SectionReport):
    name = "READING"


class SATWritingReport(SectionReport):
    name = "WRITING"

    def __init__(self, score, correct, incorrect, omitted, essay=None):
        super(SATWritingReport, self).__init__(score, correct, incorrect, omitted)
        self.essay = essay


class StudentSATReport(object):

    def __init__(self, first_name, last_name, test_date, math, writing, reading):
        self.first_name = first_name
        self.last_name = last_name
        self.test_date = test_date
        self.math = math
        self.writing = writing
        self.reading = reading

    @property
    def score(self):
        return self.math.score + self.reading.score + self.writing.score

    @property
    def estimated_act(self):
        sat_score = int(self.score)
        while sat_score > 0:
            try:
                act_score = SAT_TO_ACT[sat_score]
            except KeyError:
                sat_score -= 10
                continue
        return act_score


class KaplanSATReport(KaplanReport):

    def to_dataframe(self):
        data = [(s.first_name, s.last_name, s.score, s.math.score, s.writing.score, s.reading.score)
                for s in self.student_reports]
        columns = ['first_name', 'last_name', 'overall_score', 'math_score',
                   'writing_score', 'reading_score']
        return pd.DataFrame(data, columns=columns)


class SATParser(KaplanParser):

    def to_report(self, students):
        reports = []
        for name, student in students.items():
            math = parse_section(student[1], SATMathReport)
            reading = parse_section(student[2], SATReadingReport)
            writing = parse_section(student[2], SATWritingReport)
            first_name, last_name = get_name(student[1])
            test_date = get_test_date(student[1])
            student_report = StudentSATReport(first_name, last_name, test_date, math, writing, reading)
            reports.append(student_report)

        kaplan_report = KaplanSATReport(reports)
        return kaplan_report



