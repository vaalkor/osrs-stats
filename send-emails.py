from mailersend import emails
import os
import json
import argparse

parser = argparse.ArgumentParser(description='This script sends a html file as an email to the players')
parser.add_argument('--html-file', dest='html_file', required=True, help='HTML Content for email')
args = parser.parse_args()


def get_env_var(name):
    try:
        return os.environ[name]
    except:
        return None


def create_recipient_object(player_name):
    return {
        "name": "player_name",
        "email": get_env_var(f'{player_name}_EMAIL'.replace(' ','_'))
    }


if(not get_env_var('MAILERSEND_API_KEY')):
    raise 'Could not find MAILERSEND_API_KEY environment variable.'

with open('players.json', 'r') as read_file:
    players = json.load(read_file)

players_with_emails = [x for x in players if get_env_var(f'{player_name}_EMAIL'.replace(' ','_'))]
print(f'Found emails for players: {players_with_emails}')

with open(args.html_file, 'r') as read_file:
    html = read_file.read()

mailer = emails.NewEmail()

mail_from = {
    "name": "OSRS Stats Bot",
    "email": "osts-stats@arbitrarydata.co.uk",
}

recipients = [create_recipient_object(x) for x in players_with_emails]

reply_to = [
    {
        "name": "osrs-stats",
        "email": "osts-stats@arbitrarydata.co.uk",
    }
]

mail_body = {}
mailer.set_mail_from(mail_from, mail_body)
mailer.set_mail_to(recipients, mail_body)
mailer.set_subject("Daily OSRS stats update!", mail_body)
mailer.set_html_content(html, mail_body)
mailer.set_plaintext_content("Sorry, all the juicy info in this email is in the HTML content!", mail_body)

# using print() will also return status code and data
print('Sending email!') 
mailer.send(mail_body)
