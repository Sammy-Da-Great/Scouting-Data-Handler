import requests
import config_maker

def tba_request(url, key = None):
    if key == None:
        key = config_maker.read_global_config().tba_key
    r = requests.get(url, headers={'X-TBA-Auth-Key':key})
    return r.json()

def generate_team_data(event_key = None, key = None):
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
    data = [['match_num', 'competition', 'team_number', 'alliance']]
    data.append(['smallint(45)', 'varchar(45)', 'smallint(45)', 'varchar(45)'])
    data_buffer = []
    r = tba_request(f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple', key)
    for item in r:
        if item['comp_level'] == 'qm':
            for team in item['alliances']['red']['team_keys']:
                data_buffer.append([int(item['match_number']), event_key, str(team).replace('frc', ''), "red"])
            for team in item['alliances']['blue']['team_keys']:
                data_buffer.append([int(item['match_number']), event_key, str(team).replace('frc', ''), "blue"])
    data_buffer.sort(key = lambda sublist: sublist[0])
    return data + data_buffer

def get_coral_from_each_match(event_key, key = None):
    if key == None:
        key = config_maker.read_global_config().tba_key
    data = [['match_number', 'competition', 'red_auto_coral_l1', 'red_auto_coral_l2', 'red_auto_coral_l3', 'red_auto_coral_l4', 'red_tele_coral_l1', 'red_tele_coral_l2', 'red_tele_coral_l3', 'red_tele_coral_l4', 'blue_auto_coral_l1', 'blue_auto_coral_l2', 'blue_auto_coral_l3', 'blue_auto_coral_l4', 'blue_tele_coral_l1', 'blue_tele_coral_l2', 'blue_tele_coral_l3', 'blue_tele_coral_l4']]
    data.append(['smallint(45)', 'varchar(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)', 'smallint(45)'])
    data_buffer = []
    r = tba_request(f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches', key)
    for item in r:
        if item['comp_level'] == 'qm':
            data_buffer_buffer = []
            data_buffer_buffer.append(item['match_number'])
            data_buffer_buffer.append(event_key)

            if not(item['score_breakdown'] is None):

                red = item['score_breakdown']['red']
                blue = item['score_breakdown']['blue']

                for alliance in [red, blue]:
                    data_buffer_buffer.append(alliance['autoReef']['trough'])
                    data_buffer_buffer.append(alliance['autoReef']['tba_botRowCount'])
                    data_buffer_buffer.append(alliance['autoReef']['tba_midRowCount'])
                    data_buffer_buffer.append(alliance['autoReef']['tba_topRowCount'])
                    data_buffer_buffer.append(alliance['teleopReef']['trough'])
                    data_buffer_buffer.append(alliance['teleopReef']['tba_botRowCount'])
                    data_buffer_buffer.append(alliance['teleopReef']['tba_midRowCount'])
                    data_buffer_buffer.append(alliance['teleopReef']['tba_topRowCount'])
                
                data_buffer.append(data_buffer_buffer)
    
    data_buffer.sort(key = lambda sublist: sublist[0])
    return data + data_buffer