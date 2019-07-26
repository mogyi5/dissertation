from haystack import indexes
from myhealthdb.models import Patient


class PatientIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/patient_text.txt")
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    dob = indexes.DateTimeField(model_attr='dob')
    nhs_no = indexes.CharField(model_attr='nhs_no', null=True)
    ad_postcode = indexes.CharField(model_attr='ad_postcode', null=True)

    def get_model(self):
        return Patient

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()  #filter(pub_date__lte=datetime.datetime.now())
