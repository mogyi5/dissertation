from django.test import TestCase
from myhealthdb.models import *
from myhealthdb.forms import *
from django.db import IntegrityError
from django.core.exceptions import ValidationError

#tests for the hospital model
class HospitalTests(TestCase):

    #test if str is correct
    def test_return_name(self):
        hospital = Hospital.objects.create(name='hosp', type='general', address='add')
        self.assertEqual(str(hospital), hospital.name)

    #test if group is created on creation
    def test_group_created(self):
        hospital = Hospital.objects.create(name='hosp', type='general', address='add')
        try:
            Group.objects.get(name='hosp')
        except Group.DoesNotExist:
            self.fail('The Group did not get created with a Hospital')

    #test if name is invalid with numbers
    def test_name_valid_case(self):
        with self.assertRaises(ValidationError):
            hospital = Hospital.objects.create(name='hosp1', type='general', address='add')
            hospital.full_clean()

#tests for the patient model
class PatientTests(TestCase):

    #test if str is correct
    def test_return_name(self):
        cu = CustomUser.objects.create_user(username='cu1',email='cu@cu.com', password='myhealthdb', user_type='1' )
        pat = Patient.objects.create(baseuser=cu, first_name='pat', last_name='pot',sex= "F", dob= "2002-02-02")
        self.assertEqual(str(pat), pat.first_name + " " + pat.last_name)

    #test if nhs validator works (10 digit long number only)
    def test_nhs_validator_letters(self):
        cu = CustomUser.objects.create_user(username='cu1',email='cu@cu.com', password='myhealthdb', user_type='1' )
        pat = Patient.objects.create(baseuser=cu, first_name='pat', last_name='pot',sex= "F", dob= "2002-02-02")
        pat.full_clean()
        with self.assertRaises(ValidationError):
            pat.nhs_no = 'abcdefghij'
            pat.full_clean()

#tests for the staff model
class StaffTests(TestCase):

    #test if staff is added to a group on creation
    def test_save_group(self):
        hospital = Hospital.objects.create(name='hosp', type='general', address='add')
        ward = Ward.objects.create(name='ward', type='type', hospital=hospital)
        cu = CustomUser.objects.create_user(username='cu1',email='cu@cu.com', password='myhealthdb', user_type='3' )
        staff = Staff.objects.create(baseuser=cu, first_name='pat', last_name='pot', ward=ward)
        try:
            Group.objects.filter(members=staff)
        except Group.DoesNotExist:
            self.fail('The Staff did not get added to the group.')

#tests for the group model
class GroupTests(TestCase):

    #test if the slug is correct
    def test_slug(self):
        g = Group.objects.create(name='name of this group')
        self.assertEqual(g.slug, 'name-of-this-group')

    #test if the default type is false
    def test_type(self):
        g = Group.objects.create(name='name of this group')
        self.assertEqual(g.type, False)

#tests for the vital model
class VitalTests(TestCase):

    #test if the value of a vital can only be positive
    def test_positive_value(self):
        cu = CustomUser.objects.create_user(username='cu1',email='cu@cu.com', password='myhealthdb', user_type='1' )
        pat = Patient.objects.create(baseuser=cu, first_name='pat', last_name='pot',sex= "F", dob= "2002-02-02")
        with self.assertRaises(ValidationError):
            vital = Vital.objects.create(type='Weight', patient = pat, value=-2)
            vital.full_clean()

#tests for the hospital model
class PatientHospitalTests(TestCase):

    #test if a patient and hospital can only have one relationship
    def test_unique_test(self):
        cu = CustomUser.objects.create_user(username='cu1',email='cu@cu.com', password='myhealthdb', user_type='1' )
        pat = Patient.objects.create(baseuser=cu, first_name='pat', last_name='pot',sex= "F", dob= "2002-02-02")
        hospital = Hospital.objects.create(name='hosp', type='general', address='add')
        ph = PatientHospital.objects.create(patient=pat, hospital = hospital)
        with self.assertRaises(IntegrityError):
            PatientHospital.objects.create(patient=pat, hospital = hospital)


#test the views
class ViewsTests(TestCase):

    #test thhe index
    def test_index(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myhealthdb/index.html')

#test the forms
class FormTests(TestCase):

    #test immunization form for validity
    def test_immunization_form_data_valid(self):
        cu = CustomUser.objects.create_user(username='cu1',email='cu@cu.com', password='myhealthdb', user_type='1' )
        pat = Patient.objects.create(baseuser=cu, first_name='pat', last_name='pot',sex= "F", dob= "2002-02-02")
        form_data = {'date': '2019-08-22', 'amount':'30mg', 'added_by':pat, 'type':'ZIK', 'patient':pat}
        form = ImmunizationForm(user = pat, data=form_data)
        self.assertTrue(form.is_valid())

    #test shift form for validity, wrong times
    def test_shift_form_data_valid(self):
        hospital = Hospital.objects.create(name='hosp', type='general', address='add')
        ward = Ward.objects.create(name='ward', type='type', hospital=hospital)
        cu = CustomUser.objects.create_user(username='cu1',email='cu@cu.com', password='myhealthdb', user_type='3' )
        staff = Staff.objects.create(baseuser=cu, first_name='pat', last_name='pot', ward=ward)
        form_data = {'date': '2019-08-22', 'start':'12:00', 'end': '11:00', 'staff':staff}
        form = ShiftForm(data=form_data)
        self.assertFalse(form.is_valid())

    #test doctor condition form for validity
    def test_doctor_condition_form_data_valid(self):
        cu2 = CustomUser.objects.create_user(username='cu2',email='cu2@cu2.com', password='myhealthdb', user_type='1' )
        # staff = Staff.objects.create(baseuser=cu, first_name='pat', last_name='pot', ward=ward)
        pat = Patient.objects.create(baseuser=cu2, first_name='pat', last_name='pot',sex= "F", dob= "2002-02-02")
        form_data = {'start': '2019-08-22', 'type':'Allergy', 'reaction': 'bad', 'severity':'Low', 'title':'title', 'patient':pat}
        form = DoctorConditionForm(user=pat, data=form_data)
        self.assertTrue(form.is_valid())

    #test doctor medication form for validity, wrong dates
    def test_doctor_medication_form_data_valid(self):
        cu2 = CustomUser.objects.create_user(username='cu2',email='cu2@cu2.com', password='myhealthdb', user_type='1' )
        pat = Patient.objects.create(baseuser=cu2, first_name='pat', last_name='pot',sex= "F", dob= "2002-02-02")
        form_data = {'start': '2019-08-22', 'finish': '2019-08-20',  'type':'aspirin', 'reaction': 'bad', 'frequency':'2x a day'}
        form = DoctorMedicationForm(user=pat, data=form_data)
        self.assertFalse(form.is_valid())



    

