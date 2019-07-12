class HospitalRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read remote models go to remote database.
        """
        if hasattr(model._meta, 'in_db'):
            return model._meta.in_db
        return None


        # if model._meta.app_label == 'hospital1':
        #     return 'hospital1'
        # return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write remote models go to the remote database.
        """
        if hasattr(model._meta, 'in_db'):
            return model._meta.in_db
        return None
        # if model._meta.app_label == 'hospital1':
        #     return 'hospital1'
        # return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'hospital1' or \
           obj2._meta.app_label == 'hospital1':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        return True
        # if model._meta.app_label == 'hospital1':
        #     return 'hospital1'
        # return None