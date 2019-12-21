import csv
import os
import logging
import sys
import jinja2
from decimal import Decimal

from scrooge import config

logger = logging.getLogger(__name__)

def ingest_recipient_csv(name):
    with open(name, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]


def discover_csvs(path):
    return [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
        and f.endswith('.csv')
    ]


def csv_output(recipients_dict):
    for recipient, items in recipients_dict.items():
        if not items:
            continue
        print(f'=========== {recipient} ===========')
        writer = csv.DictWriter(sys.stdout, fieldnames=items[0].keys())
        writer.writerows(items)

def ingest_budget_file(filepath):
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        budget_table = [row for row in reader]
        # Strip off totals
        budget_table = [
            row[:-1] for row in budget_table[:-1]
        ]

        # Replace - with 0
        for row_index, row in enumerate(budget_table):
            logger.debug(f'Row: {row}')
            for col_index, col_value in enumerate(row):
                if col_value == '-':
                    budget_table[row_index][col_index] = 0
                elif row_index == 0 or col_index == 0:
                    continue
                logger.debug(f'col value: {col_value}')
                budget_table[row_index][col_index] = Decimal(
                    budget_table[row_index][col_index]
                )

        recipients = budget_table[0][1:]
        return {
            row[0]: {
                name: row[i + 1]
                for i, name in enumerate(recipients)
            }
            for row in budget_table[1:]
        }

def print_budget(budget_table):
    for person, budget_map in budget_table.items():
        print("=== %s ===" % person)
        for owed_person, amount in budget_map.items():
            print("%s: %s" % (owed_person.ljust(7), amount))


def render_report(sections):
    loader = jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR)
    env = jinja2.Environment(loader=loader)
    template = env.get_template("Report.html")
    output = template.render(sections=sections)
    with open(config.PROJECT_DIR + config.REPORT_FILENAME, 'w') as f:
        f.write(output)
