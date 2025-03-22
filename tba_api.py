import requests
import config_maker

def tba_request(url, key = None):
    if key == None:
        key = config_maker.read_global_config().tba_key
    r = requests.get(url, headers={'X-TBA-Auth-Key':key})
    return r.json()

def generate_team_data(event_key, key = None):
    data = [['team_num']]
    data.append(['smallint(45)'])
    r = tba_request(f'https://www.thebluealliance.com/api/v3/event/{event_key}/teams/simple', key)
    for item in r:
        data.append(str(item['team_number']))

    return data

def generate_match_data(event_key, key = None):
    import datetime
    data = [['match_num', 'timestamp', 'coral_scored_red', 'coral_scored_blue']]
    data.append(['smallint(45)', 'timestamp', 'smallint(45)', 'smallint(45)'])
    r = tba_request(f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches', key)
    data_buffer = []
    for item in r:
        if item['comp_level'] == 'qm':
            buffer = [item['match_number'], datetime.datetime.fromtimestamp(item['predicted_time'])]
            buffer.append(item['score_breakdown']['red']['teleopReef']['tba_botRowCount'] + item['score_breakdown']['red']['teleopReef']['tba_midRowCount'] + item['score_breakdown']['red']['teleopReef']['tba_topRowCount'])
            buffer.append(item['score_breakdown']['blue']['teleopReef']['tba_botRowCount'] + item['score_breakdown']['blue']['teleopReef']['tba_midRowCount'] + item['score_breakdown']['blue']['teleopReef']['tba_topRowCount'])
            data_buffer.append(buffer)
    data_buffer.sort(key = lambda sublist: sublist[0])
    return data + data_buffer

def generate_match_teams(event_key, key = None):
    data = [['match_num', 'team_number']]
    data.append(['smallint(45)', 'smallint(45)'])
    data_buffer = []
    r = tba_request(f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple', key)
    for item in r:
        if item['comp_level'] == 'qm':
            for team in item['alliances']['red']['team_keys'] + item['alliances']['blue']['team_keys']:
                print(int(item['match_number']))
                data_buffer.append([int(item['match_number']), str(team).replace('frc', '')])
    data_buffer.sort(key = lambda sublist: sublist[0])
    return data + data_buffer