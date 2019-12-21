import copy
import logging

from decimal import Decimal

logger = logging.getLogger(__name__)

def update_budgets(shopping_lists, budgets):
    for recipient_name, item_list in shopping_lists.items():
        for item in item_list:
            buyer = item['Buyer']
            logger.debug('Item "%s" buyer "%s" recipient "%s"', item['Present'], buyer, recipient_name)
            # Buying something for yourself doesn't affect the budget/debts
            if buyer == recipient_name:
                logger.info('Skipping "%s" as buyer "%s" is also the recipient', item['Present'], buyer)
                continue

            if buyer not in budgets:
                logger.info('Skipping "%s" as Buyer "%s" has no budget', item['Present'], buyer)
                continue

            budgets[buyer][recipient_name] -= Decimal(item['Cost'])
    return budgets

def cost_of_items_by_buyer(shopping_lists):
    cost_map = {}
    for recipient_name, item_list in shopping_lists.items():
        for item in item_list:
            buyer = item['Buyer']
            logger.debug('Item "%s" buyer "%s" recipient "%s"', item['Present'], buyer, recipient_name)
            # Buying something for yourself doesn't affect the budget/debts
            if buyer == item['Giver'] == recipient_name:
                logger.info(
                    'Skipping "%s" as buyer "%s", giver and recipient are the same',
                    item['Present'],
                    buyer
                )
                continue

            cost_map[buyer] = str(Decimal(cost_map.get(buyer, 0)) + Decimal(item['Cost']))
    return cost_map

def unpack_shared_item(item):
    givers = item['Giver'].split('|')
    if len(givers) == 1:
        return [item]

    split_cost = round(Decimal(item['Cost'])/len(givers), 2)
    multipack = []
    for giver in givers:
        sub_item = copy.copy(item)
        sub_item['Cost'] = split_cost
        sub_item['Giver'] = giver
        multipack.append(sub_item)
    return multipack

def replace_unpacked_items(shopping_lists):
    new_lists = {}
    for recipient_name, item_list in shopping_lists.items():
        sharded_items = [
            unpack_shared_item(item)
            for item in item_list
        ]
        flat_list = [item for sublist in sharded_items for item in sublist]
        new_lists[recipient_name] = flat_list

    return new_lists


def calculate_grand_totals_for_givers(shopping_lists):
    shopping_lists = replace_unpacked_items(shopping_lists)
    givers_spending = {}
    for recipient_name, item_list in shopping_lists.items():
        for item in item_list:
            giver = item['Giver']
            # Buying yourself something doesn't mean you get repaid!
            if recipient_name == giver:
                continue
            givers_spending[giver] = str(Decimal(givers_spending.get(giver, 0)) + Decimal(item['Cost']))
    return givers_spending

def calculate_recipient_totals_for_givers(shopping_lists):
    shopping_lists = replace_unpacked_items(shopping_lists)
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


def budget_minus_cost_of_items(shopping_lists, budgets):
    new_budget = update_budgets(copy.deepcopy(shopping_lists), copy.deepcopy(budgets))
    debt_map = {}
    for recipient_name, budget_map in new_budget.items():
        debt_map[recipient_name] = str(sum(budget_map.values()))
    return debt_map

def total_budget_per_person(budgets):
    condensed_budget = {}
    for recipient_name, budget_map in budgets.items():
        condensed_budget[recipient_name] = str(sum(budget_map.values()))
    return condensed_budget
