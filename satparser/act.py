import pandas as pd

from parser import parse_section, get_name, get_test_date,  \
                    SectionReport, KaplanReport, KaplanParser
from percentiles import ACT_TO_SAT



class ACTEnglishReport(SectionReport):
    name = "ENGLISH"


class ACTMathReport(SectionReport):
    name = "MATH"


class ACTReadingReport(SectionReport):
    name = "READING"


class ACTScienceReport(SectionReport):
    name = "SCIENCE"


class StudentACTReport(object):

    def __init__(self, first_name, last_name, test_date, english, math,
                reading, science):
        self.first_name = first_name
        self.last_name = last_name
        self.test_date = test_date
        self.english = english
        self.math = math
        self.reading = reading
        self.science = science

    @property
    def score(self):
        total = self.english.score + self.math.score + self.reading.score + self.science.score
        avg = total / 4.
        return int(round(avg))

    @property
    def estimated_sat(self):
        act_score = int(self.score)
        return ACT_TO_SAT[act_score]


class KaplanACTReport(KaplanReport):

    def to_dataframe(self):
        data = [(s.first_name, s.last_name, s.score, s.english.score, s.math.score, s.reading.score, s.english.score)
                for s in self.student_reports]
        columns = ['first_name', 'last_name', 'overall_score', 'english_score',
                   'math_score', 'reading_score', 'science_score']
        return pd.DataFrame(data, columns=columns)



class ACTParser(KaplanParser):

    def to_report(self, students):
        reports = []
        for name, student in students.items():
            english = parse_section(student[1], ACTEnglishReport)
            math = parse_section(student[2], ACTMathReport)
            reading = parse_section(student[2], ACTReadingReport)
            science = parse_section(student[3], ACTScienceReport)
            first_name, last_name = get_name(student[1])
            test_date = get_test_date(student[1])
            student_report = StudentACTReport(first_name, last_name,
                                              test_date, english, math,
                                              reading, science)
            reports.append(student_report)

        kaplan_report = KaplanACTReport(reports)
        return kaplan_report
