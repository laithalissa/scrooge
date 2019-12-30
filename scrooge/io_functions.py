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


loader = jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR)
env = jinja2.Environment(loader=loader)

def generate_table_html(top_headings, left_headings, table_rows):
    template = env.get_template("table.html")
    table_rows = [{'title': i[0], 'values': i[1]} for i in zip(left_headings, table_rows)]
    output = template.render({
        'headings': top_headings,
        'rows': table_rows
    })
    return output

def generate_supertable(*subtables):
    """
    Given a variable number of subtables, reformat the data
    so it can be rendered into one table. A subtable is simply
    a dictionary which looks like:
    {
      'title': 'Cost of Presents',
      'data': {
          'Laith': '4',
          'Abi'. '5.99'
       }
    }

    Subtables are then rendered as one big table, with missing
    keys filled in with a default value
    """
    DEFAULT_VALUE = '-'
    # Build a set of all "names" to appear on the left of the table
    all_keys = set()
    for d in subtables:
        all_keys.update(d['data'].keys())

    # Sort the keys so there's a standard order
    all_keys = sorted(list(all_keys))
    # Create a list of table headings to pass to the template...
    table_headings = []
    # ... and a list for the colums, in matching order
    table_data = []
    for d in subtables:
        table_headings.append(d['title'])
        column = []
        for key in all_keys:
            column.append(d['data'].get(key, DEFAULT_VALUE))
        table_data.append(column)

    table_rows = []
    for col_number in range(len(all_keys)):
        row = []
        for row_number in range(len(subtables)):
            row.append(
                table_data[row_number][col_number]
            )
        table_rows.append(row)

    return generate_table_html(table_headings, all_keys, table_rows)


def render_report(table):
    template = env.get_template("report.html")
    output = template.render(table=table)
    with open(config.PROJECT_DIR + config.REPORT_FILENAME, 'w') as f:
        f.write(output)
