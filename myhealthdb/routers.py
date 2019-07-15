from myhealthdb.models import Hospital, Ward, Staff, Task

class HealthcareRouter(object):

    def db_for_read(self, model, **hints):
        """ reading SomeModel from otherdb """
        if model == Hospital or model == Ward or model == Staff or model == Task:
            return 'hospitals'
        return None

    def db_for_write(self, model, **hints):
        """ writing SomeModel to otherdb """
        if model == Hospital or model == Ward or model == Staff or model == Task:
            return 'hospitals'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):

        return True

#         # if obj1._DATABASE == obj2._DATABASE:
#         #    return True
#         # return None

#         # if obj1._meta.app_label == 'hospital1' or \
#         #    obj2._meta.app_label == 'hospital1':
#         #    return True
#         # return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        return True