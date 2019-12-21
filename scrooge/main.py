from scrooge.config import *
from scrooge.calculations import *
from scrooge.io_functions import *

from json2html import json2html

logging.basicConfig(level=logging.DEBUG, filename='scrooge.log', filemode='w')
logger = logging.getLogger(__name__)


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

from pprint import pprint
# pprint(calculate_credit_and_debt(shopping_lists))

# new_budget = update_budgets(copy.deepcopy(shopping_lists), copy.deepcopy(budgets))
# pprint(new_budget)
# print_budget(new_budget)

def original_shopping_lists():
    return copy.deepcopy(shopping_lists)

def original_budget():
    return copy.deepcopy(budgets)

def append_section(_sections, _title, _result):
    _sections.append({
        'title': _title,
        'body': json2html.convert(
            json=_result,
            table_attributes='class="table"'
        )
    })
    return _sections


sections = []
sections = append_section(
    sections,
    'Original Budget',
    total_budget_per_person(original_budget())
)

# sections = append_section(
#     sections,
#     'Budget minus cost of purchases',
#     calculate_credit_and_debt(
#         original_shopping_lists(),
#         original_budget()
#     )
# )

cost_of_purchases = cost_of_items_by_buyer(
    original_shopping_lists()
)
sections = append_section(
    sections,
    'Cost of purchases (grouped by buyer)',
    cost_of_purchases
)

cost_of_gifts_given = calculate_grand_totals_for_givers(original_shopping_lists())
sections = append_section(
    sections,
    'Cost of gifts given',
    cost_of_gifts_given
)

debt_credit = copy.deepcopy(cost_of_purchases)
for name, cost in cost_of_gifts_given.items():
    debt_credit[name] = str(Decimal(debt_credit.get(name, 0)) - Decimal(cost))

sections = append_section(
    sections,
    'Debt/Credit',
    debt_credit
)

# print(sum([Decimal(d) for d in debt_credit.values()]))
render_report(sections)
