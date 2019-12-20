import csv
import os
import sys

project_dir = os.path.join(os.path.dirname(__file__), '..')
CSV_PATH_PREFIX = os.path.join(project_dir, './res/csv/')
BUDGET_FILE_NAME = 'Budget.csv'

def ingest_csv(name):
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

csv_files = discover_csvs(CSV_PATH_PREFIX)
recipients_files = [f for f in csv_files if not f.endswith(BUDGET_FILE_NAME)]

recipients = {}
for filename in recipients_files:
    item_list = ingest_csv(os.path.join(CSV_PATH_PREFIX, filename))
    recipient_name = filename.split('.csv')[0]
    for item in item_list:
        item['recipient'] =  recipient_name
    recipients[recipient_name] = item_list




# presents = ingest_csv()
# print(presents)

# recipients = [
#     'Laith',
#     'Abi',
#     'David'
# ]

# errors = []
# for p in presents:
#     for field in ['buyer', 'receiver', 'giver']:
#         if getattr(p, field) not in recipients:
#             errors.append(
#                 f'Unexpected {field} in {p.__dict__}'
#             )
#
# print(errors)