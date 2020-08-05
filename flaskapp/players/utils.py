import pandas as pd
from flaskapp.models import AvailablePlayer, DraftedPlayer, User, Team
from flaskapp import db
from flask import current_app, url_for
from flask.cli import with_appcontext
from flask_login import current_user
import requests
from bs4 import BeautifulSoup

def create_available_players():
    file = r'C:/Users/barto/OneDrive/Desktop/Python/flaskapp/flaskapp/players/available_players.csv'
    df = pd.read_csv(file)
    for a,b,c in zip(df['player'], df['world_rank'], df['odds']):
        results = AvailablePlayer.query.filter_by(player=a).all()
        if not results:
            available_player = AvailablePlayer(player=a,world_rank=b,odds=c)
            db.session.add(available_player)
            db.session.commit()

def create_scoreboard():
#Creates team scoreboard
    result = db.session.query(User.username,
                              db.func.sum(DraftedPlayer.to_par_int), db.func.sum(DraftedPlayer.today_int)
                             ).join(DraftedPlayer,
                              User.id==DraftedPlayer.team_id).group_by(DraftedPlayer.team_id)
    scoreboard_df = pd.DataFrame(columns=['Team','TO PAR','TODAY'])
    data = []
    columns = list(scoreboard_df)
    for r in result:
        values = list(r)
        zipped = zip(columns, values)
        a_dictionary = dict(zipped)
        data.append(a_dictionary)
    scoreboard_df = scoreboard_df.append(data,True)
    return scoreboard_df


def activate_players():
    r = requests.get('https://www.espn.com/golf/leaderboard')
    html_content = r.text
    soup = BeautifulSoup(html_content)
    table_html = soup.find_all("a", attrs={"class": "AnchorLink leaderboard_player_name"})
    for player in table_html:
        name = player.text
        ap = AvailablePlayer.query.filter(AvailablePlayer.player.ilike(name)).first()
        if ap:
            print(name + ' is here!')
            ap.active=1
        else:
            ap = AvailablePlayer(player=name)
            ap.active=1
            db.session.add(ap)
            print('Good news! We added '+ name + ' to our database. First time we\'ve seen this jabroni!')
    db.session.commit()

def day2_leaderboard_final():
    r = requests.get('https://www.espn.com/golf/leaderboard')
    html_content = r.text
    soup = BeautifulSoup(html_content,"lxml")
    table_html = soup.find("table", attrs={"class": "Table Table--align-right"})
    stats = table_html.find_all("tr")
    for player in stats[1:]:
        data = player.find_all("td")
        name = data[1].text
        ap = AvailablePlayer.query.filter(AvailablePlayer.player.ilike(name)).first()
        if ap:
            ap.pos=data[0].text
            ap.to_par = data[2].text
            try:
                ap.to_par_int= int(ap.to_par)
            except:
                ap.to_par_int = 0

            ap.r1 = data[3].text
            ap.r2 = data[4].text
            ap.r3 = data[5].text
            ap.r4 = data[6].text
        else:
            available_player = AvailablePlayer(player=name)
            db.session.add(available_player)
    db.session.commit()

def update_leaderboard():
    r = requests.get('https://www.espn.com/golf/leaderboard')
    html_content = r.text
    soup = BeautifulSoup(html_content,"lxml")
    table_html = soup.find("table", attrs={"class": "Table Table--align-right"})
    stats = table_html.find_all("tr")
    for player in stats[1:]:
        data = player.find_all("td")
        name = data[2].text
        ap = AvailablePlayer.query.filter(AvailablePlayer.player.ilike(name)).first()
        if ap:
            ap.pos=data[0].text
            ap.to_par = data[3].text
            try:
                ap.to_par_int= int(ap.to_par)
            except:
                ap.to_par_int = 0

            ap.today = data[4].text
            try:
                ap.today_int= int(ap.today)
            except:
                ap.today_int = 0

            ap.thru = data[5].text

            if ap.thru =='F':
                ap.holes_remaining = 0
            elif ap.thru=='WD':
                ap.holes_remaining = 0
            elif ap.thru=='CUT':
                ap.holes_remaining = 0
            elif len(ap.thru) > 4:
                ap.holes_remaining = 18
            else:
                try:
                    ap.holes_remaining = 18-int(ap.thru)
                except:
                    ap.holes_remaining = 18


            ap.r1 = data[6].text
            ap.r2 = data[7].text
            ap.r3 = data[8].text
            ap.r4 = data[9].text
        else:
            available_player = AvailablePlayer(player=name)
            db.session.add(available_player)
    db.session.commit()

def clear_drafted_players():
    ap_list = AvailablePlayer.query.all()
    for player in ap_list:
        player.drafted_flag =0
    db.session.commit()

def update_player_images():
    ap_list = AvailablePlayer.query.all()
    for player in ap_list:
        if player.player_image == '1':
            player.player_image = url_for('static',filename='images/default_headshot.jpg')
            print(player.player_image)
    db.session.commit()

def update_team_scoreboard():
    team_list = Team.query.all()
    for team in team_list:
        player_list = []
        for player in team.players:
            player_list.append(player.player)
        df = pd.DataFrame(([p.pos, p.player,p.to_par, p.to_par_int,p.today,p.today_int,p.thru, p.holes_remaining]
                           for p in AvailablePlayer.query.filter(AvailablePlayer.player.in_(player_list))),
                     columns=['POS','PLAYER','TO_PAR','TO_PAR_INT','TODAY','TODAY_INT','THRU','Holes Remaining'])

        team.current_score_int = int(df['TO_PAR_INT'].sort_values(ascending=True).head(4).sum())

        if team.current_score_int== 0:
            current_score_label = 'E'
        elif team.current_score_int>0:
            current_score_label ='+'
        else:
            current_score_label = ''

        team.cut_players = 0
        team.holes_remaining = int(df['Holes Remaining'].sum())
        team.today_score_int = int(df['TODAY_INT'].sum())

        if team.today_score_int==0:
            today_label = 'E'
        elif team.today_score_int>0:
            today_label ='+'
        else:
            today_label = ''

        if current_score_label=='E':
            team.current_score = 'E'
        else:
            team.current_score = current_score_label + str(team.current_score_int)


        try:
            team.fourth_score = str(df.iloc[3]['PLAYER']) + ', '+str(df.iloc[3]['TO_PAR'])+ ', '+str(df.iloc[3]['THRU'])
        except:
            team.fourth_score = ''

        if today_label =='E':
            team.today_score="E"
        else:
            team.today_score = today_label + str(team.today_score_int)
        db.session.commit()
