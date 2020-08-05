from flask import render_template, request, Blueprint, url_for, flash, redirect
from flask_socketio import SocketIO, send
from flaskapp.models import AvailablePlayer, Team, DraftedPlayer, User
from flaskapp.players.utils import create_available_players, update_player_images, day2_leaderboard_final, clear_drafted_players, create_scoreboard, activate_players, update_leaderboard, update_team_scoreboard
import pandas as pd
from flaskapp import create_app, db
from flask_login import current_user, login_required
from flask_mobility.decorators import mobile_template
from sqlalchemy import and_
from sqlalchemy.sql import text
from sqlalchemy import create_engine
import os

engine = create_engine('sqlite:///C:\\Users\\barto\\OneDrive\\Desktop\\Python\\flaskapp\\flaskapp\\site.db')

players = Blueprint('players', __name__)


@players.route("/availableplayers", methods=("POST", "GET"))
def leaderboard():
    df = pd.DataFrame(([p.player, p.odds, p.world_rank, p.player_image, p.flag_image] for p in AvailablePlayer.query.filter(AvailablePlayer.world_rank >= 1).all()),
                 columns=['Player','Odds','World Rank','Player Image','Flag Image'])
    return render_template("leaderboard.html", column_names=df.columns.values,
    row_data=list(df.values.tolist()), zip=zip)


@players.route("/draft", methods=("POST", "GET"))
@mobile_template('{mobile/}draft.html')
@login_required
def draft(template):
    user_id = current_user.id
    df = pd.DataFrame(([p.player, p.player_image,  p.world_rank, p.odds  ] for p in AvailablePlayer.query.filter(AvailablePlayer.active==1, AvailablePlayer.drafted_flag==0)),
                 columns=['Player','Image','World Rank','Odds'])
    default_img = url_for('static',filename='images/default_headshot.jpg')
    df.replace(to_replace ='C:/Users/barto/OneDrive/Desktop/Python/flaskapp/flaskapp/static/images/default.jpg',
                            value =default_img)
    if request.method == 'POST':
        current_user.active_for_tournament = 1
        my_user = Team.query.filter(Team.user_id == user_id).first()
        if my_user:
            pass
        else:
            team = Team(user_id=user_id)
            db.session.add(team)
            db.session.commit()
        db.session.commit()
        player_list = request.form.getlist('draftcheckbox')
        current_players = DraftedPlayer.query.filter(DraftedPlayer.team_id==user_id).all()
        total_players = len(player_list) + len(current_players)
        drafted_players = 0
        team_length = len(current_players)+drafted_players
        if len(player_list)==0:
            flash(f'You haven\'t selected any players. Try again!','danger')
            redirect(url_for('players.draft'))
        elif total_players <6:
            for player in player_list:
                ap = AvailablePlayer.query.filter(AvailablePlayer.player==player).first()
                my_player = DraftedPlayer.query.filter(DraftedPlayer.player==player).first()
                if my_player:
                    flash(f'{player} has already been drafted!','danger')
                    redirect(url_for('players.draft'))
                else:
                    dp = DraftedPlayer(player=player, team_id=user_id)
                    db.session.add(dp)
                    ap.drafted_flag=1
                    db.session.commit()
                    drafted_players+=1
                    flash(f'You have successfully drafted {player}!', 'success')
            flash(f'You have {6-(drafted_players+len(current_players))} pick(s) remaining.','light')
            return redirect(url_for('players.draft'))
        elif total_players ==6:
            for player in player_list:
                ap = AvailablePlayer.query.filter(AvailablePlayer.player==player).first()
                my_player = DraftedPlayer.query.filter(DraftedPlayer.player==player).first()
                if my_player:
                    flash(f'{player} has already been drafted!','danger')
                    redirect(url_for('players.draft'))
                else:
                    dp = DraftedPlayer(player=player, team_id=user_id)
                    db.session.add(dp)
                    ap.drafted_flag=1
                    db.session.commit()
                    drafted_players+=1
            flash(f'Your team is now full!', 'success')
            return redirect(url_for('players.myteam'))

        elif len(current_players)==6:
            flash(f'Your team is already full! Drop some players and re-draft.','danger')
            return redirect(url_for('players.myteam'))
        else:
            flash(f'You cannot draft more than 6 players. There are already {len(current_players)} on your team and you attempted to draft {len(player_list)} additional players. Select {6-len(current_players)} or fewer players to continue. You can drop players via the My Team page.', 'danger')
            return redirect(url_for('players.draft'))
    return render_template(template, df=df)

@players.route("/teams", methods=("POST", "GET"))
def teams():
    df = pd.DataFrame(([t.players, t.user_id] for t in Team.query.all()),
                 columns=['Player','Team'])
    return render_template("leaderboard.html", column_names=df.columns.values,
    row_data=list(df.values.tolist()), zip=zip)

@players.route("/myteam", methods=("POST", "GET"))
@login_required
def myteam():
    user_id = current_user.id
    # update_players()
    myteam = db.session.query(DraftedPlayer.team_id,AvailablePlayer.pos,
                         AvailablePlayer.player, AvailablePlayer.player_image, AvailablePlayer.country, AvailablePlayer.to_par,
                         AvailablePlayer.to_par_int, AvailablePlayer.today,AvailablePlayer.today_int,
                          AvailablePlayer.thru,
                          AvailablePlayer.holes_remaining,
                         AvailablePlayer.r1,AvailablePlayer.r2,
                         AvailablePlayer.r3,AvailablePlayer.r4,
                        AvailablePlayer.world_rank, AvailablePlayer.odds
                         ).join(AvailablePlayer,AvailablePlayer.player==DraftedPlayer.player).filter(DraftedPlayer.team_id==user_id).all()
    myteam_df = pd.DataFrame(myteam,
              columns=['Team Id','POS','Player','Player Image','Country','To Par','To Par Int','Today','Today Int','Thru',
                       'Holes Remaining','R1','R2','R3','R4','World Rank','Odds']).sort_values(by=['To Par Int'])

    if request.method == 'POST':
        player_list = request.form.getlist('drop_player')
        for player in player_list:
            dp = DraftedPlayer.query.filter(DraftedPlayer.player==player, DraftedPlayer.team_id==user_id).first()
            ap = AvailablePlayer.query.filter(AvailablePlayer.player==dp.player).first()
            ap.drafted_flag = 0
            db.session.delete(dp)
            db.session.commit()
        flash('Those guys are outta here! Pick some new players!','success')
        return redirect(url_for('players.draft'))
    return render_template("myteam.html", df = myteam_df, username = current_user.username)

@players.route("/scoreboard")
@login_required
def game_scoreboard():
    # update_player_images()
    try:
        update_team_scoreboard()
    except:
        pass
    user = current_user.username
    drafted = db.session.query(DraftedPlayer.team_id, User.username,AvailablePlayer.pos,
                         AvailablePlayer.player, AvailablePlayer.to_par,
                         AvailablePlayer.to_par_int, AvailablePlayer.today,AvailablePlayer.today_int,
                          AvailablePlayer.thru,
                          AvailablePlayer.holes_remaining,
                         AvailablePlayer.r1,AvailablePlayer.r2,
                         AvailablePlayer.r3,AvailablePlayer.r4
                         ).outerjoin(AvailablePlayer,DraftedPlayer.player==AvailablePlayer.player).outerjoin(User,DraftedPlayer.team_id==User.id).all()
    drafted_df = pd.DataFrame(drafted,
                  columns=['Team Id','Username','POS','Player','To Par','To Par Int','Today','Today Int','Thru',
                           'Holes Remaining','R1','R2','R3','R4']).sort_values(by=['To Par Int'])
    team_leaderboard = db.session.query(Team.user_id, User.username, Team.current_score, Team.current_score_int,
                               Team.today_score, Team.today_score_int, Team.holes_remaining, Team.cut_players,
                               Team.fourth_score
                             ).join(User,Team.user_id==User.id).all()
    scoreboard_df = pd.DataFrame(team_leaderboard,
                  columns=['User ID','Username','Current Score','Current Score Int','Today','Today Int',
                           'Holes Remaining','Cut Players','4th Score']).sort_values(by=['Current Score Int'])

    df = pd.DataFrame(([p.player, p.player_image,  p.world_rank, p.odds, p.pos, p.to_par,p.to_par_int, p.today, p.today_int, p.thru, p.holes_remaining, p.r1, p.r2, p.r3, p.r4] for p in AvailablePlayer.query.filter(AvailablePlayer.active >= 1).all()),
                 columns=['Player','Image','World Rank','Odds', 'POS','To Par','To Par Int','Today','Today Int','Thru','Holes Remaining','R1','R2','R3','R4'])
    return render_template("scoreboard_layout.html",
    scoreboard_df=scoreboard_df,
    drafted_df=drafted_df,
    df=df,
    user=user
    )
