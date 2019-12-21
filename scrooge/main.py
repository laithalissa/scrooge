from scrooge.config import *
from scrooge.calculations import *
from scrooge.io import *

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
result = calculate_credit_and_debt(
    original_shopping_lists(),
    original_budget()
)
sections = append_section(sections, 'Credit/Debts', result)

result = calculate_grand_totals_for_givers(original_shopping_lists())
table = json2html.convert(json=result, table_attributes='class="table"')
sections = append_section(sections, 'Giver totals', result)
render_report(sections)
