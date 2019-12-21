from scrooge.functions import *

logging.basicConfig(level=logging.DEBUG, filename='scrooge.log', filemode='w')
logger = logging.getLogger(__name__)

project_dir = os.path.join(os.path.dirname(__file__), '..')
CSV_PATH_PREFIX = os.path.join(project_dir, './res/csv/')
BUDGET_FILE_NAME = 'Budget.csv'

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
pprint(calculate_totals_for_givers(copy.deepcopy(shopping_lists)))
#pprint(calculate_credit_and_debt(copy.deepcopy(shopping_lists)))
