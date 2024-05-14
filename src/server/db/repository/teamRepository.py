from db.model.team import Team
from db.model.pagedResult import PagedResult
from db.repository.repository import Repository, process_paged_result
from sqlalchemy.orm import aliased

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

    def update_team(self, team):        
        self.session.merge(team)
        self.session.commit()        
        return team

    def delete_team(self, team_id):        
        team = self.session.query(Team).filter_by(id=team_id).first()
        self.session.delete(team)
        self.session.commit()        

    def list_all(self, tenant_id:int, limit:int = None, after=None, before=None, order_by:str=None) -> list[Team]:
        try:
            if before is not None and after is not None:
                raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
            
            ParentTeam = aliased(Team)
            query = self.session.query(Team, ParentTeam)
            query = query.filter(Team.tenant_id == tenant_id)
            total_count = query.count()

            query = query.outerjoin(ParentTeam, Team.parent_id == ParentTeam.id)
            if after:
                query = query.filter(Team.id > after)
                query = query.order_by(Team.id.asc())
            elif before:
                query = query.filter(Team.id < before)
                query = query.order_by(Team.id.desc())
            else:
                query = query.order_by(Team.id.asc())
            
            if limit:
                query = query.limit(limit+1)

            query = query.with_entities(
                Team.id,
                Team.name,
                Team.parent_id,
                Team.github_team_id,
                Team.tags,
                ParentTeam.name.label('parentName')
            )
            
            result = query.all()
            result = [item._asdict() for item in result]
            
            result, before_cursor, after_cursor = process_paged_result(result, limit, before, after)

            return PagedResult(result, total_count, before_cursor, after_cursor)
        except Exception as error:
            print("Error while listing git_stats:", error)
