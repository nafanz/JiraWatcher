from atlassian import Jira

user_name = 'XXX'
user_password = 'XXX'

jira = Jira(
    url='https://jira.ХХХ.org',
    username=user_name,
    password=user_password
)

versions = (
    'QA-200',
    'QA-404'
)
