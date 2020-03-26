from .models import Baptism, Confirmation, Marriage
import django_tables2 as tables

# This is the generic class of a selectable table.
class AbstractTable(tables.Table):
    id = tables.Column(attrs={
        'th': {'style': 'display:none;'},
        'td': {'style': 'display:none;'},
    })
    class Meta:
        
        row_attrs = {
            'class': 'selectable-row table-sm us'
        }
        template_name = 'django_tables2/bootstrap.html'
        template_name = 'sacrament/table.html'
        attrs = {'class': 'table table-hover selectable-table table-bordered records-table'}
    


# Custom tables start here.
class BaptismTable(AbstractTable):

    status = tables.Column(attrs={
        'td': {'class': 'status'},
    })
    
    class Meta(AbstractTable.Meta):
        model = Baptism
        exclude = ('registry_number','record_number', 'remarks',
            'mother_last_name', 'mother_first_name', 'mother_middle_name', 'mother_suffix',
            'father_last_name', 'father_first_name', 'father_middle_name', 'father_suffix',
        )  
        sequence = ('id', 'page_number', 'profile', 'status', 'date', 'target_price', 'minister', 'legitimacy')
        

class ConfirmationTable(AbstractTable):

    status = tables.Column(attrs={
        'td': {'class': 'status'},
    })
    
    class Meta(AbstractTable.Meta):
        model = Confirmation
        sequence = ('id', 'profile', 'status', 'minister')
        #exclude = ('target_price','minister','registry_number','page_number','record_number', 'remarks' )  
        #sequence = ('id', 'profile', 'status', 'date', 'target_price', 'minister')


class MarriageTable(AbstractTable):

    status = tables.Column(attrs={
        'td': {'class': 'status'},
    })
    
    class Meta(AbstractTable.Meta):
        model = Marriage
        #exclude = ('target_price','minister','registry_number','page_number','record_number', 'remarks' )  
        #sequence = ('id', 'profile', 'status', 'date', 'target_price', 'minister')