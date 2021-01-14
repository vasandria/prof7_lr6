class UserLogin():
    def fromDB(self, user_id, db):
        self.__user = db.getuser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return user

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])
