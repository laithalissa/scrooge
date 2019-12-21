import copy
import csv
import logging
import os
import sys

from decimal import Decimal

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


def update_budgets(shopping_lists, budgets):
    for recipient_name, item_list in shopping_lists.items():
        for item in item_list:
            logger.debug('Item "%s" buyer "%s" recipient "%s"', item['Present'], item['Buyer'], recipient_name)
            # Buying something for yourself doesn't affect the budget/debts
            if item['Buyer'] == recipient_name:
                logger.info('Skipping "%s" as buyer "%s" is also the recipient', item['Present'], item['Buyer'])
                continue

            if item['Buyer'] not in budgets:
                logger.info('Skipping "%s" as Buyer "%s" has no budget', item['Present'], item['Buyer'])
                continue

            budgets[item['Buyer']][recipient_name] -= Decimal(item['Cost'])
    return budgets

def print_budget(budget_table):
    for person, budget_map in budget_table.items():
        print("=== %s ===" % person)
        for owed_person, amount in budget_map.items():
            print("%s: %s" % (owed_person.ljust(7), amount))

def calculate_totals_for_givers(shopping_lists):
    recipient_reports = {}
    for recipient_name, item_list in shopping_lists.items():
        givers_spending = {}
        for item in item_list:
            giver = item['Giver']
            # Buying yourself something doesn't mean you get repaid!
            if recipient_name == giver:
                continue
            givers_spending[giver] = str(Decimal(givers_spending.get(giver, 0)) + Decimal(item['Cost']))
        recipient_reports[recipient_name] = givers_spending
    return recipient_reports


def calculate_credit_and_debt(shopping_lists, budgets):
    new_budget = update_budgets(copy.deepcopy(shopping_lists), copy.deepcopy(budgets))
    debt_map = {}
    for recipient_name, budget_map in new_budget.items():
        debt_map[recipient_name] = str(sum(budget_map.values()))
    return debt_map
