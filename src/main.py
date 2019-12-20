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


csv_files = [
    f for f in os.listdir(CSV_PATH_PREFIX)
    if os.path.isfile(os.path.join(CSV_PATH_PREFIX, f))
    and f.endswith('.csv')
]
recipients_files = [f for f in csv_files if not f.endswith(BUDGET_FILE_NAME)]

recipients = {}
for filename in recipients_files:
    recipients[(filename.split('.csv')[0])] = (
        ingest_csv(os.path.join(CSV_PATH_PREFIX, filename))
    )


for recipient, items in recipients.items():
    writer = csv.DictWriter(sys.stdout, fieldnames=items[0].keys())
    for item in items:
        writer.writerow(item)
    writer.writerows(items)



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