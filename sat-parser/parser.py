import re
import logging

logger = logging.getLogger(__name__)

import slate
import pandas as pd



class StudentReport(object):
	
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
	
	


class SectionReport(object):
    
    def __init__(self, score, correct, incorrect, omitted):
        self.score = score
        self.correct = correct
        self.incorrect = incorrect
        self.omitted = omitted
	
	@property
	def percent_correct(self):
		return float(self.correct) / self.total_questions
	
	@property
	def total_questions(self):
		return self.correct + self.incorrect + self.omitted
	
class MathReport(SectionReport):
	pass


class ReadingReport(SectionReport):
	pass


class WritingReport(SectionReport):
	
	def __init__(self, score, correct, incorrect, omitted, essay=None):
		super(WritingReport, self).__init__(score, correct, incorrect, omitted)
		self.essay = essay


class SectionParser(object):
	reports = dict(math=MathReport, writing=WritingReport, reading=ReadingReport)
	
	def __init__(self, page, report):
		self.page = page
		self.report = self.reports[report]
		
	def get_correct(self):
		return self.get_integer(self.page, 'Correct', 'Incorrect')
	
	def get_incorrect(self):
		return self.get_integer(self.page, 'Incorrect', 'Omitted')
	
	def get_score(self):
		return self.get_integer(self.page, 'Scaled Score', 'Percentage')
	
	def get_omitted(self):
		return self.get_integer(self.page, 'Omitted', 'Scaled Score')
	
	@classmethod
	def get_integer(cls, page, start_text, end_text):
		# match only characters of length from 0-5 arggh
		raw_text = re.findall('(?<=%s)(.{0,5})(?=%s)' % (start_text, end_text), page)
		if len(raw_text) > 1:
			logger.warning("Found multiple matches: %s" % raw_text)
		return int(raw_text[0])
	
	def to_report(self):
		correct = self.get_correct()
		incorrect = self.get_incorrect()
		omitted = self.get_omitted()
		score = self.get_score()
		return self.report(score, correct, incorrect, omitted)

def parse_section(page, report):
	parser = SectionParser(page, report)
	return parser.to_report()


class KaplanSATParser(object):
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.doc = None
    
    def get_doc_text(self):
        with open(self.filepath) as f:
            doc = slate.PDF(f)
		
		replace_unicode_chars = lambda s: s.replace('\xc2\xa0', ' ')       
        self.doc = [replace_unicode_chars(page) for page in doc]


class KaplanSATReport(object):
	
	def __init__(self, student_reports):
		self.student_reports = student_reports
	
	def __iter__(self):
		return iter(self.student_reports)
	
	def to_dataframe(self):
		data = [(s.first_name, s.last_name, s.score) for s in self.student_reports]
		return pd.DataFrame(data, columns=['first_name', 'last_name', 'score'])
    

def parser(doc):
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
	

def to_kaplan_report(student_pages):
	reports = []
	for name, student in students.items():
		math = parse_section(student[1], 'math')
		reading = parse_section(student[2], 'reading')
		writing = parse_section(student[2], 'writing')
		first_name, last_name = get_name(student[1])
		test_date = get_test_date(student[1])
		student_report = StudentReport(first_name, last_name, test_date, math, writing, reading)
		
		reports.append(student_report)
	return reports
	
	kaplan_report = KaplanReport()
	return kaplan_report 
	# page 1 = overall report, math report
	# page 2 = reading and writing report
	# page 3 = blank page
	# page 4,5 = responses to questions
	
	

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
    raw_text = re.findall('(?<=Test Date:)(.*)(?=Page)', page)[0]
    return pd.to_datetime(raw_text)

def get_page_num(page):
    raw_text = re.findall('(?<=Page)(.*)(?=of 5)', page)[0]
    return int(raw_text)