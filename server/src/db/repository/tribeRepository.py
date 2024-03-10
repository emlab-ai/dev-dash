from sqlalchemy.orm import sessionmaker
from db.model.tribe import Tribe

class TribeRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
    
    def add_tribe(self, tribe):
        session = self.Session()
        session.add(tribe)
        session.commit()
        session.close()

   
    def remove_tribe_by_id(self, tribe_id):
        session = self.Session()
        session.query(Tribe).filter_by(id=tribe_id).delete()
        session.commit()
        session.close()

    def get_tribes(self):
        session = self.Session()
        tribes = session.query(Tribe).all()
        session.close()
        return tribes

    def get_tribe_by_id(self, tribe_id):
        session = self.Session()
        tribe = session.query(Tribe).filter_by(id=tribe_id).first()
        session.close()
        return tribe

    def get_tribes_by_name(self, tribe_name):
        session = self.Session()
        matching_tribes = session.query(Tribe).filter_by(name=tribe_name).all()
        session.close()
        return matching_tribes