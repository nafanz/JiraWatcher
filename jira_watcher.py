import re
import requests
from prettytable import PrettyTable
import credentials


status_ignore = (
    'Approved',
    'Closed',
    'Rejected',
    'Declined',
)

issues_gitlog = set()
issues_qa = set()

for version in credentials.versions:
    version = credentials.jira.issue(version)
    for item in version['fields']['issuelinks']:
        try:
            issues_qa.add(item['inwardIssue']['key'])
        except KeyError:
            issues_qa.add(item['outwardIssue']['key'])
    for item in version['fields']['subtasks']:
        subtasks = credentials.jira.issue(item['key'])
        if subtasks['fields']['description'] is not None:
            issues_gitlog.update(
                re.findall(
                    '[A-Z]{2,}-\d+',
                    subtasks['fields']['description']
                )
            )

jira_table = PrettyTable()
jira_table.field_names = [
    'key',
    'status',
    'summary',
    'issuetype',
    'priority',
    'assignee',
    'creator',
]

jira_table.align = 'l'
jira_table.sortby = 'status'

report = open('report.txt', 'w')


def report_table(name, source):
    for i in source:
        try:
            ticket = credentials.jira.issue(i)
            if ticket['fields']['status']['name'] not in status_ignore:
                # Добавление наблюдателя
                credentials.jira.issue_add_watcher(
                    ticket['key'],
                    credentials.user_name
                )
                # Заполнение таблицы
                jira_table.add_row(
                    [
                        ticket['key'],
                        ticket['fields']['status']['name'],
                        ticket['fields']['summary'][:100] + '...' if len(ticket['fields']['summary']) > 100 else ticket['fields']['summary'],
                        ticket['fields']['issuetype']['name'],
                        ticket['fields']['priority']['name'],
                        ticket['fields']['assignee']['displayName'],
                        ticket['fields']['creator']['displayName'],
                    ]
                )
        # requests.exceptions.HTTPError: Issue Does Not Exist
        except requests.exceptions.HTTPError:
            pass

    jira_table.title = f'{name} (Total: {len(source)}, Not Closed: {jira_table.__getattr__("rowcount")})'

    report.write(jira_table.get_string())
    report.write('\n')

    jira_table.clear_rows()


report_table('Git Log', issues_gitlog)
report_table('Issue Links', issues_qa)
