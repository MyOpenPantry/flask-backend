from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from ..models.pantryitem import PantryItem
from ..database import db

class Items(Resource):
    def get(self, piname):
        item = PantryItem.query.get(piname)
        if item is None:
            return {"error":"No such item in the pantry"}
        return { f"{item.id}":f"{item.name}" }
    
    def put(self, piname):
        new_item = PantryItem(name=piname)
        try:
            db.session.add(new_item)
            db.session.commit()
        except:
            db.session.rollback()
            return {"error":"Error commiting transaction"}
        return ''