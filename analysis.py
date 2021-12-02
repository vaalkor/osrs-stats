import json
import argparse
import os.path as path
import os
import matplotlib.pyplot as plt
import datetime
from utils import *

parser = argparse.ArgumentParser(description='This script analysis the runescape stats and formulates emails to send out.')
parser.add_argument('--bucket-url', dest='bucket_url', default=None, required=False, help='S3 bucket url to store images in for graphs in emails. If this is not defined image links will just default to local links.')
parser.add_argument('--files', nargs='+', dest='files', required=True, help='1 or more files to parse')
args = parser.parse_args()

average_daily_xp_all_time = {}
average_daily_xp_all_time
player_stats = {}
daily_stat_gains = {}
images_to_upload = []
timestamp = int(datetime.datetime.utcnow().timestamp())

def create_image_link(image_name):
    if(args.bucket_url):
        return f'{args.bucket_url}/{image_name}'
    return image_name


def compute_daily_xp_gains(player_name, player_data):
    global daily_stat_gains
    global player_stats
    
    previous_day = player_data[len(player_data)-2]
    current_day = player_data[len(player_data)-1]

    player_stats[player_name] = current_day

    for key in current_day['skills'].keys():
        current_day['skills'][key]['previous_xp'] = previous_day['skills'][key]['xp']
        current_day['skills'][key]['daily_xp_gain'] = int(current_day['skills'][key]['xp']) - int(previous_day['skills'][key]['xp'])
        current_day['skills'][key]['previous_level'] = int(previous_day['skills'][key]['level'])
    
    daily_xp_gained_skills = [x for x in current_day['skills'].keys() if current_day['skills'][x]['daily_xp_gain'] > 0]
    if len(daily_xp_gained_skills) == 0:
        return
    daily_xp_gained_skills.sort(key=lambda x:-1*current_day['skills'][x]['daily_xp_gain'])

    daily_stat_gains[player_name] = daily_xp_gained_skills
    


def plot_graph(x_vals, y_vals, title, filename):
    
    fig = plt.figure()
    ax=fig.add_subplot(111)
    ax.set_title(title)
    ax.bar(x_vals, y_vals)
    plt.xticks(range(len(x_vals)), x_vals, rotation='vertical')
    plt.tight_layout()
    plt.savefig(f'temp/{filename}')

#=======================================================#
#=======================================================#

try: os.mkdir('temp')
except: True

for file in args.files:
    with open(file, 'r') as read_file:
        data = json.load(read_file)
    
    if(not isinstance(data, list) or len(data) < 2 ):
        print(f'Skipping file: {file} as there are not enough data points')
        continue
    
    player_name = os.path.split(file)[1].replace('.json','')
    compute_daily_xp_gains(player_name, data)


def table_rows(player_name):
    def daily_stat_row(skill):
        xp_gain = player_stats[player_name]["skills"][skill]["daily_xp_gain"]
        level_gain = f'{player_stats[player_name]["skills"][skill]["previous_level"]} => {player_stats[player_name]["skills"][skill]["level"]}'
        return elem('tr', elems('td', skill, xp_gain, level_gain))
    test = [daily_stat_row(x) for x in daily_stat_gains[player_name]]
    print(test)
    return ''.join(test)


def create_daily_stats_table(player_name):
    return elem('table', elem('tr', elems('th', 'Skill', 'XP Gain', 'Level Gain')), table_rows(player_name))

   
def overall_daily_xp_gains():
    image_name = f'{timestamp}_overall_daily_xp.png'
    images_to_upload.append(image_name)

    players = sorted(daily_stat_gains.keys(), key=lambda x:-1*player_stats[x]['skills']['overall']['daily_xp_gain'])[::-1]
    xp_vals = [player_stats[x]['skills']['overall']['daily_xp_gain'] for x in players]
    plot_graph(players, xp_vals, f'Total XP gained previous day', image_name)   
    
    yield elem('h2', 'Overall XP gains')
    yield elem('img', src=create_image_link(image_name))
    yield elem('hr')

def daily_stats_email_segment():
    players_sorted_by_xp_gain = sorted(daily_stat_gains.keys(), key=lambda x:-1*player_stats[x]['skills']['overall']['daily_xp_gain'])

    yield elem('h2', 'Per Player daily XP Gains (sorted by highest overall gains)')

    def get_segment_for_player(player_name):
        image_name = f'{timestamp}_{player_name}_daily_xp.png'
        images_to_upload.append(image_name)

        daily_xp_values = [player_stats[player_name]['skills'][x]['daily_xp_gain'] for x in daily_stat_gains[player_name][::-1]]
        plot_graph(daily_stat_gains[player_name][::-1], daily_xp_values, f'{player_name} XP gained previous day', image_name)
        
        yield elem('h3', f'{player_name} daily XP gains')
        yield elem('img', src=create_image_link(image_name))
        yield create_daily_stats_table(player_name)
                

    for player_name in players_sorted_by_xp_gain:
        yield from get_segment_for_player(player_name)
       

# Build email!

with open('email_header.html', 'r') as read_file:
    email_header = read_file.read()

def email_body():
    yield elem('h1', 'Daily OSRS stats update!')
    yield '<hr/>&nbsp;'
    if(len(daily_stat_gains.keys()) > 0):
        yield from overall_daily_xp_gains()
        yield from daily_stats_email_segment()


def email():
    yield '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
    yield '<html xmlns="http://www.w3.org/1999/xhtml">'
    yield f'{email_header}'

    yield '<body>'
    yield from email_body()
    yield '</body>'
    yield '</html>'

final_email = concat_iterable(email())

with open('temp/email_content.html', 'w') as f:
    f.write(final_email)

with open('temp/images_to_upload.json', 'w') as f:
    json.dump(images_to_upload, f)
