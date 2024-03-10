from db.model.team import Team


# Create the team repository class
class TeamRepository:
    def __init__(self, session):
        self.session = session

    def create_team(self, team):
        self.session.add(team)    
        self.session.commit()
        return team

    def get_team(self, team_id):        
        team = self.session.query(Team).filter_by(id=team_id).first()        
        return team

    def update_team(self, team_id, new_name):        
        team = self.session.query(Team).filter_by(id=team_id).first()
        team.name = new_name
        self.session.commit()        

    def delete_team(self, team_id):        
        team = self.session.query(Team).filter_by(id=team_id).first()
        self.session.delete(team)
        self.session.commit()        