from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from lims.models.user import CustomUser
from lims.models.schedule import *
from lims.models.shipping import *
from lims.models.storage import *
from lims.models.patient import *
from lims.models.specimen import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', ]

schedule_models = [EventModel, SpecimenType, ScheduleModel]
specimen_models = [SpecimenModel, AliquotType, AliquotModel]
patient_models = [VisitModel, SourceModel, PatientModel]
storage_models = [BoxSlotModel, BoxModel, BoxTypeModel, StorageModel]
shipping_models = [ShipmentModel, DestinationModel, CarrierModel]

# user model
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(schedule_models)
admin.site.register(patient_models)
admin.site.register(specimen_models)
admin.site.register(storage_models)
admin.site.register(shipping_models)
