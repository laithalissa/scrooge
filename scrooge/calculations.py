import copy
import csv
import logging
import os
import sys

from decimal import Decimal

logger = logging.getLogger(__name__)



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
