import os
import sys
import argparse

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(basedir)

import kaplanparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split Kaplan SAT/ACT report into individual PDFs for each student.")
    parser.add_argument('-i', '--input', help="Filepath to PDF of Kaplan Diagnostic report")
    parser.add_argument('-t', '--testtype', help="Test type either SAT or ACT", choices=["act", "sat"])
    parser.add_argument('-o', '--output', help="Filename to dump csv into")

    args = parser.parse_args()
    
    report_generator = kaplanparse.to_sat_report if args.testtype == 'sat' else kaplanparse.to_act_report
    report = report_generator(args.input)
    df = report.to_dataframe()
    df.to_csv(args.output, index=False)