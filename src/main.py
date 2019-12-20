import csv
import logging
import os
import sys

from decimal import Decimal

project_dir = os.path.join(os.path.dirname(__file__), '..')
CSV_PATH_PREFIX = os.path.join(project_dir, './res/csv/')
BUDGET_FILE_NAME = 'Budget.csv'

logging.basicConfig(level=logging.INFO)
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
            for col_index, col_value in enumerate(row):
                if col_value == '-':
                    budget_table[row_index][col_index] = 0
                elif row_index == 0 or col_index == 0:
                    continue

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


budgets = ingest_budget_file(os.path.join(CSV_PATH_PREFIX, BUDGET_FILE_NAME))
csv_files = discover_csvs(CSV_PATH_PREFIX)
shopping_list_files = [f for f in csv_files if not f.endswith(BUDGET_FILE_NAME)]

shopping_lists = {}
for filename in shopping_list_files:
    item_list = ingest_recipient_csv(os.path.join(CSV_PATH_PREFIX, filename))
    recipient_name = filename.split('.csv')[0]
    for item in item_list:
        item['recipient'] =  recipient_name
    shopping_lists[recipient_name] = item_list


for recipient_name, item_list in shopping_lists.items():
    for item in item_list:
        # Buying something for yourself doesn't affect the budget/debts
        if item['Buyer'] == recipient_name:
            logger.info('Skipping "%s" as buyer "%s" is also the recipient', item['Present'], item['Buyer'])
            continue

        if item['Buyer'] not in budgets:
            logger.info('Skipping "%s" as Buyer "%s" has no budget', item['Present'], item['Buyer'])
            continue

        logger.info('Item "%s" buyer "%s"', item['Present'], item['Buyer'])
        budgets[item['Buyer']][recipient_name] -= Decimal(item['Cost'])

def print_budget(budget_table):
    for person, budget_map in budget_table.items():
        print("=== %s ===" % person)
        for owed_person, amount in budget_map.items():
            print("%s: %s" % (owed_person.ljust(10), amount))

logging.shutdown()
print_budget(budgets)
