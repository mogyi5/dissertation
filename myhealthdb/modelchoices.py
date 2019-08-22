
#choices for the models and the forms included here.

#patient sex
SEX = (
    ('M', 'Male'),
    ('F', 'Female')
)

#customuser user_type
USER_TYPE_CHOICES = (
    (1, 'patient'),
    (2, 'doctor'),
    (3, 'receptionist'),
    (4, 'IT'),
)

#vital type
VITALTYPE = (
    ('Weight', 'Weight'),
    ('Height', 'Height'),
)

#condition type
CONDITION_TYPE = (
    ('Allergy', 'Allergy'),
    ('Heart Condition', 'Heart Condition'),
    ('Blindness', 'Blindness'),
    ('Deaf', 'Deaf'),
)

#condition severity
SEVERITY = (
    ('Minor', 'Minor'),
    ('Low', 'Low'),
    ('Moderate', 'Moderate'),
    ('Very High', 'Very High'),
    ('Severe', 'Severe'),
)

#hospital type
HOSPITAL_TYPE = (
    ('General Practice', 'General Practice'),
    ('General Hospital', 'General Hospital'),
    ('Specialized Hospital', 'Specialized Hospital')
)

#document type
DOC_TYPE = (
    ('Discharge Letter', 'Discharge Letter'),
    ('Lab Result', 'Lab Result'),
    ('Prescription', 'Prescription')
)

#event type
EVENT_TYPE = (
    ('Surgery', 'Surgery'),
    ('Consultation', 'Consultation'),
    ('Immunization', 'Immunization'),
    ('Emergency', 'Emergency'),
    ('Special', 'Special'),
    ('Shift', 'Shift'),
)

#immunization type
IMM_TYPE = (
    ('FLU', 'Influenza'),
    ('ZIK', 'Zika Virus'),
    ('MSL', 'Measles')
)

#hospital form interest
REASON = (
    ('I', 'Interest in Product'),
    ('P', 'Problem with the Product')
)
