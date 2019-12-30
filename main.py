from scrooge.config import *
from scrooge.calculations import *
from scrooge.io_functions import *


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

def original_shopping_lists():
    return copy.deepcopy(shopping_lists)

def original_budget():
    return copy.deepcopy(budgets)

cost_of_purchases = cost_of_items_by_buyer(
    original_shopping_lists()
)
cost_of_gifts_given = calculate_grand_totals_for_givers(original_shopping_lists())

debt_credit = copy.deepcopy(cost_of_purchases)
for name, cost in cost_of_gifts_given.items():
    debt_credit[name] = str(Decimal(debt_credit.get(name, 0)) - Decimal(cost))

table = generate_supertable(
    {'title': 'Cost of Purchases', 'data': cost_of_purchases},
    {'title': 'Cost of gifts given', 'data': cost_of_gifts_given},
    {'title': 'Debt/Credit', 'data': debt_credit}
)

render_report(table)
