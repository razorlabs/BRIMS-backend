from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, PatientModel, SpecimenModel, SpecimenType, AliquotModel, AliquotType, VisitModel, SourceModel, StorageModel, BoxTypeModel, BoxSlotModel, BoxModel, EventModel, ScheduleModel, CarrierModel, DestinationModel, ShipmentModel

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', ]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EventModel)
admin.site.register(PatientModel)
admin.site.register(SpecimenModel)
admin.site.register(SpecimenType)
admin.site.register(AliquotModel)
admin.site.register(AliquotType)
admin.site.register(VisitModel)
admin.site.register(SourceModel)
admin.site.register(StorageModel)
admin.site.register(BoxTypeModel)
admin.site.register(BoxModel)
admin.site.register(BoxSlotModel)
admin.site.register(ScheduleModel)
admin.site.register(CarrierModel)
admin.site.register(DestinationModel)
admin.site.register(ShipmentModel)
