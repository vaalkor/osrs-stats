import json
import argparse
import os.path as path
import os
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='This script analysis the runescape stats and formulates emails to send out.')
parser.add_argument('--files', '-f', nargs='+', dest='files', required=True, help='1 or more files to parse')
args = parser.parse_args()

player_stats = {}
daily_stat_gains = {}


def compute_daily_xp_gains(player_name, player_data):
    global daily_stat_gains
    global player_stats
    
    previous_day = player_data[len(player_data)-2]
    current_day = player_data[len(player_data)-1]

    player_stats[player_name] = current_day

    for key in current_day['skills'].keys():
        current_day['skills'][key]['previous_xp'] = previous_day['skills'][key]['xp']
        current_day['skills'][key]['daily_xp_gain'] = int(current_day['skills'][key]['xp']) - int(previous_day['skills'][key]['xp'])
        current_day['skills'][key]['previous_level'] = int(current_day['skills'][key]['level']) - int(previous_day['skills'][key]['level'])
    
    daily_xp_gained_skills = [x for x in current_day['skills'].keys() if current_day['skills'][x]['daily_xp_gain'] > 0]
    if len(daily_xp_gained_skills) == 0:
        return
    daily_xp_gained_skills.sort(key=lambda x:-1*current_day['skills'][x]['daily_xp_gain'])

    daily_stat_gains[player_name] = daily_xp_gained_skills
    


def plot_graph(x_vals, y_vals):
    fig = plt.figure()
    ax=fig.add_subplot(111)
    # print(x_vals)
    # print(y_vals)
    ax.bar(x_vals, y_vals)
    plt.show()


for file in args.files:
    with open(file, 'r') as read_file:
        data = json.load(read_file)
    
    if(not isinstance(data, list) or len(data) < 2 ):
        print(f'Skipping file: {file} as there are not enough data points')
        continue
    
    
    player_name = os.path.split(file)[1].replace('.json','')
    compute_daily_xp_gains(player_name, data)
    # print(daily_stat_gains[player_name])
    # print(player_stats[player_name])
    # print([player_stats[player_name]['skills'][x]['daily_xp_gain'] for x in daily_stat_gains[player_name]])
    plot_graph(daily_stat_gains[player_name], [player_stats[player_name]['skills'][x]['daily_xp_gain'] for x in daily_stat_gains[player_name]])


print(json.dumps(daily_stat_gains, indent=2))
print('----------------------------------------')


# function ComputePlayerStats($PlayerDataList){
#     $previousDay = $PlayerDataList | select -last 2 | select -first 1
#     $currentDay = $PlayerDataList | select -last 1

#     $STATS.skills | %{
#         $currentDay.skills.$_ | Add-Member -MemberType NoteProperty -Name 'previous_day_xp' -Value $previousDay.skills."$_".xp
#         $currentDay.skills.$_ | Add-Member -MemberType NoteProperty -Name 'day_delta' -Value ($currentDay.skills."$_".xp - $previousDay.skills."$_".xp)
#     }
# }
# function GetPlayerDailyXpGains($currentDay){
#     $currentDay.skills `
#         | Get-Member -MemberType NoteProperty `
#         | ?{$currentDay.skills.($_.Name).day_delta -ne 0} `
#         | %{$_.Name} `
#         | Sort {$currentDay.skills.$_.day_delta}
# }

# Get-ChildItem "$PSScriptRoot/data" -Filter *.json | %{
#     $data = Get-Content $_.FullName | ConvertFrom-Json
#     if(($json | measure | select -ExpandProperty count) -lt 2){
#         "Skipping $($_.FullName) as it doesn't have 2 or more datapoints in it!"
#         return
#     }

#     ComputePlayerStats $data

#     $dailyXpGains = GetPlayerDailyXpGains $data
#     "==============================================="
#     "$($_.Name.Replace('.json', '')) daily XP gains:"
#     $playerStats
#     "==============================================="
    
# }


