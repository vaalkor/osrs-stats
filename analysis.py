import json
import argparse
import os.path as path
import os
import matplotlib.pyplot as plt
import datetime

parser = argparse.ArgumentParser(description='This script analysis the runescape stats and formulates emails to send out.')
parser.add_argument('--bucket-url', '-b', dest='bucket_url', required=False, help='S3 bucket url to store images in for graphs in emails. If this is not defined image links will just default to local links.')
parser.add_argument('--files', '-f', nargs='+', dest='files', required=True, help='1 or more files to parse')
args = parser.parse_args()

player_stats = {}
daily_stat_gains = {}
images_to_upload = []
timestamp = int(datetime.datetime.utcnow().timestamp())

css=('<style>table, th, td { border: 1px solid black;}'
'table { margin-left:30px}'
'</style>'
)

def create_image_link(image_name):
    print(image_name)
    print(args.bucket_url)
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
    plt.savefig(filename)


for file in args.files:
    with open(file, 'r') as read_file:
        data = json.load(read_file)
    
    if(not isinstance(data, list) or len(data) < 2 ):
        print(f'Skipping file: {file} as there are not enough data points')
        continue
    
    
    player_name = os.path.split(file)[1].replace('.json','')
    compute_daily_xp_gains(player_name, data)


def table_rows(player_name):
    result = ''
    for skill in daily_stat_gains[player_name]:
        print(f'table row for skill: {skill}')
        result+=\
('<tr>'
    f'<td>{skill}</td>'
    f'<td>{player_stats[player_name]["skills"][skill]["daily_xp_gain"]}</td>'
    f'<td>{player_stats[player_name]["skills"][skill]["previous_level"]} => {player_stats[player_name]["skills"][skill]["level"]}</td>'
'</tr>')
    return result


def create_daily_stats_table(player_name):
    table_string =\
('<table>'
    '<tr>'
        '<th>Skill</th>'
        '<th>XP Gain</th>'
        '<th>Level Gain</th>'
    '</tr>'
    f'{table_rows(player_name)}'
'</table>')
    return table_string
    

def daily_stats_email_segment():
    resultString = '<h2>Daily XP Gains (sorted by highest overall gains)</h2>'
    for player_name in sorted(daily_stat_gains.keys(), key=lambda x:-1*player_stats[x]['skills']['overall']['daily_xp_gain']):
        image_name = f'{timestamp}_{player_name}_daily_xp.png'
        images_to_upload.append(image_name)

        daily_xp_values = [player_stats[player_name]['skills'][x]['daily_xp_gain'] for x in daily_stat_gains[player_name][::-1]]
        plot_graph(daily_stat_gains[player_name][::-1], daily_xp_values, f'{player_name} XP gained previous day', image_name)
        
        table_string = create_daily_stats_table(player_name)
        resultString += f'<h3>{player_name} daily XP gains</h3><img src="{create_image_link(image_name)}"><img>{table_string}'

    return resultString
        

# Build email!
email_string = '<h1> Daily OSRS stats update! </h1><hr/>&nbsp'
if(len(daily_stat_gains.keys()) > 0):
    email_string += daily_stats_email_segment()

final_email = f'<html><head>{css}</head><body>{email_string}</body></html>'

with open('email_content.html', 'w') as f:
    f.write(final_email)

with open('images_to_upload.json', 'w') as f:
    json.dump(images_to_upload, f)