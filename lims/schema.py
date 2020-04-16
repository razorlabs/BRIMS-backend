import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required

from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model, logout
from django.conf import settings

from lims.models.user import *
from lims.models.schedule import *
from lims.models.shipping import *
from lims.models.storage import *
from lims.models.patient import *
from lims.models.specimen import *

"""
    .get is used on dictionary pull from kwargs allowing for a default value
    to be set during mutation. It is used elsewhere for consistency.
"""

class BoxModelType(DjangoObjectType):
    class Meta:
        model = BoxModel

class BoxType(DjangoObjectType):
    class Meta:
        model = BoxTypeModel

class BoxSlotType(DjangoObjectType):
    class Meta:
        model = BoxSlotModel

class CarrierModelType(DjangoObjectType):
    class Meta:
        model = CarrierModel

class DestinationModelType(DjangoObjectType):
    class Meta:
        model = DestinationModel

class ShipmentModelType(DjangoObjectType):
    class Meta:
        model = ShipmentModel

class StorageType(DjangoObjectType):
    class Meta:
        model = StorageModel

class StorageUI(graphene.ObjectType):
    key = graphene.String()
    title = graphene.String()
    content = graphene.List(StorageType)
    boxes = graphene.List(BoxModelType)
    css_icon = graphene.String()
    top_level = graphene.Boolean()


# TODO return list of ids from aliquot mutation
# https://stackoverflow.com/questions/51762817/get-query-to-return-list-of-values-instead-of-objects-in-graphene-django
class AliquotIdList(DjangoObjectType):
    id_list = graphene.List(graphene.Int)

    class Meta:
        model = AliquotModel

    def resolve_id_list(self, info):
        return [aliquot.id for aliquot in self.aliquot]


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class PatientType(DjangoObjectType):
    source = graphene.String()
    class Meta:
        model = PatientModel

    def resolve_source(self, info):
        return '{}'.format(self.source.name)

class VisitType(DjangoObjectType):
    class Meta:
        model = VisitModel


class EventType(DjangoObjectType):
    class Meta:
        model = EventModel

class ScheduleType(DjangoObjectType):
    class Meta:
        model = ScheduleModel

class SpecimenTypeModelType(DjangoObjectType):
    """
        Ugh I hate the name of this
        Various "types" of specimen
    """

    class Meta:
        model = SpecimenType

class AliquotTypeModelType(DjangoObjectType):
    """
        Hate the name here too
        Various "types" of aliquot
    """

    class Meta:
        model = AliquotType


class SpecimenModelType(DjangoObjectType):
    """
        type: returns the specimen type
        patientid: returns "PID" or the patient string used for study tracking
        patient: returns the internal lims id of patient for URL routing
    """
    type = graphene.String()
    patientid = graphene.String()
    patient = graphene.String()

    class Meta:
        model = SpecimenModel
        description = " Specimens collected for a patient "

    # return actual type as string rather then type as an object
    # example: "Dried Blood Spot" instead of type{ type: "Dried Blood Spot"}
    def resolve_type(self, info):
        return '{}'.format(self.type.type)

    # override type field to return a string rather than an object
    def resolve_patientid(self, info):
        return '{}'.format(self.patient.pid)

    def resolve_patient(self, info):
        return '{}'.format(self.patient.id)



class AliquotModelType(DjangoObjectType):
    visit = graphene.String()
    type = graphene.String()
    specimenid = graphene.Int()
    patient = graphene.String()
    class Meta:
        model = AliquotModel

    def resolve_patient(self, info):
        return '{}'.format(self.specimen.patient)

    def resolve_specimenid(self, info):
        return '{}'.format(self.specimen.id)

    def resolve_visit(self, info):
        return '{}'.format(self.visit.label)

    def resolve_type(self, info):
        return '{}'.format(self.type.type)

class ManifestType(graphene.ObjectType):
    """
        key: Box id
        name: Box description
        aliquot: all aliquot contained within a box
        Box slot row and column position to be included after all_slot refactor
    """
    key = graphene.String()
    name = graphene.String()
    aliquot = graphene.List(AliquotModelType)


class DeleteStorage(graphene.Mutation):
    id = graphene.Int()
    deleted = graphene.Boolean()
    class Arguments:
        id = graphene.Int()

    def mutate(self, info, **kwargs):
        id = kwargs.get('id', None)
        storage = StorageModel.objects.get(id=id)
        storage.delete()
        return DeleteStorage(deleted=True, id=id)

class CreateStorageMutation(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    description = graphene.String()
    container = graphene.Int()
    css_icon = graphene.String()


    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        container = graphene.Int()
        css_icon = graphene.String()

    def mutate(self, info, **kwargs):
        name = kwargs.get('name', None)
        description = kwargs.get('description', None)
        container = kwargs.get('container', None)
        css_icon = kwargs.get('css_icon', None)

        if container is not None:
            container = StorageModel.objects.get(id=container)
        else:
            container = None

        storage_input = StorageModel(
            name=name,
            description=description,
            container=container,
            css_icon=css_icon)
        storage_input.save()

        return CreateStorageMutation(
            id=storage_input.id,
            name=storage_input.name,
            description=storage_input.description,
            container=storage_input.container,
            css_icon=storage_input.css_icon,
        )


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)

class CreateEventMutation(graphene.Mutation):
    """
    Allows creation of an event
    """

    # event examples: visit1 baseline
    event = graphene.String()
    # the order in which the events should be displayed
    order = graphene.Int()

    class Arguments:
        event = graphene.String()
        order = graphene.Int()

    def mutate(self, info, event, order):
        event_input = EventModel(
            event=event,
            order=order
        )
        event_input.save()

        return CreateEventMutation(
            event=event_input.event,
            order=event_input.order,
        )

class CreateAliquotMutation(graphene.Mutation):
    """
    Allows creation of an aliquot from web UI or external source
    """
    id = graphene.Int()
    specimenid = graphene.Int()
    specimen = graphene.String()
    aliquottype = graphene.Int()
    visit = graphene.Int()
    collectdate = graphene.types.datetime.Date()
    collecttime = graphene.types.datetime.Time()
    volume = graphene.Float()
    notes = graphene.String()
    times = graphene.Int()

    class Arguments:
        specimenid = graphene.Int()
        aliquottype = graphene.Int()
        visit = graphene.Int()
        collectdate = graphene.types.datetime.Date()
        collecttime = graphene.types.datetime.Time()
        volume = graphene.Float()
        notes = graphene.String()
        times = graphene.Int()

    def mutate(self, info, **kwargs):
        times = kwargs.get('times', None)
        specimenid = kwargs.get('specimenid', None)
        aliquottype = kwargs.get('aliquottype', None)
        visit = kwargs.get('visit', None)
        specimen_object = SpecimenModel.objects.get(id=specimenid)
        aliquot_type_object = AliquotType.objects.get(id=aliquottype)
        visit_object = VisitModel.objects.get(id=visit)
        collectdate = kwargs.get('collectdate', None)
        collecttime = kwargs.get('collecttime', None)
        volume = kwargs.get('volume', None)
        notes = kwargs.get('notes', None)

        aliquot_input = AliquotModel(
            specimen=specimen_object,
            type=aliquot_type_object,
            visit=visit_object,
            collectdate=collectdate,
            collecttime=collecttime,
            volume=volume,
            notes=notes
        )

        for _ in range(times):
            # setting pk to None allows creation of multiple objects
            aliquot_input.pk = None
            aliquot_input.save()

        return CreateAliquotMutation(
            id=aliquot_input.id,
            specimen=aliquot_input.specimen,
            aliquottype=aliquot_input.type.id,
            visit=aliquot_input.visit.id,
            collectdate=aliquot_input.collectdate,
            collecttime=aliquot_input.collecttime,
            volume=aliquot_input.volume,
            notes=aliquot_input.notes,
        )



class CreateSpecimenMutation(graphene.Mutation):
    """
    Allows creation of a specimen from web UI or external source
    Arguments:
    patient: the ID of the patient associated with the specimen
    type: the specimen type
    volume: amount drawn
    collect_date: the date of collection
    collect_time: the time of collection
    notes: Any additional notes to associate with the specimen

    """

    id = graphene.Int()
    patient = graphene.Int()
    specimentype = graphene.Int()
    volume = graphene.Float()
    specimentype = graphene.String()
    collectdate = graphene.types.datetime.Date()
    collecttime = graphene.types.datetime.Time()
    notes = graphene.String()

    class Arguments:
        patient = graphene.Int()
        specimentype = graphene.Int()
        volume = graphene.Float()
        collectdate = graphene.types.datetime.Date()
        collecttime = graphene.types.datetime.Time()
        notes = graphene.String()


    def mutate(self, info, **kwargs):
        patient = kwargs.get('patient', None)
        specimentype = kwargs.get('specimentype', None)
        patient_object = PatientModel.objects.get(id=patient)
        specimen_type_object = SpecimenType.objects.get(id=specimentype)
        volume = kwargs.get('volume', None)
        collectdate = kwargs.get('collectdate', None)
        collecttime = kwargs.get('collecttime', None)
        notes = kwargs.get('notes', None)

        specimen_input = SpecimenModel(
            patient=patient_object,
            type=specimen_type_object,
            volume=volume,
            collectdate=collectdate,
            collecttime=collecttime,
            notes=notes
        )
        specimen_input.save()

        return CreateSpecimenMutation(
            id=specimen_input.id,
            specimentype=specimen_input.type,
            volume=specimen_input.volume,
            collectdate=specimen_input.collectdate,
            collecttime=specimen_input.collecttime,
            notes=specimen_input.notes,
        )


class EditPatientPidMutation(graphene.Mutation):
    id = graphene.Int()
    pid = graphene.String()

    class Arguments:
       id = graphene.Int()
       pid = graphene.String()

    def mutate(self, info, id, pid):
        target_patient = PatientModel.objects.get(pk=id)
        target_patient.pid = pid
        target_patient.save()

        return EditPatientPidMutation(
            id=target_patient.id,
            pid=target_patient.pid
        )


class CreatePatientMutation(graphene.Mutation):
    """
    Allows creation of a patient from web UI or external source
    Arguments:
    id --
    pid --
    source -- should be set based on django settings (local system or remote)
    synced -- has the patient been verified as existing in external system
    """
    id = graphene.Int()
    pid = graphene.String()
    drawschedule = graphene.Int()
    source = graphene.Int()
    synced = graphene.Boolean()

    class Arguments:
        pid = graphene.String()
        drawschedule = graphene.Int()
        source = graphene.Int()
        synced = graphene.Boolean()

    def mutate(self, info, pid, **kwargs):
        drawschedule = kwargs.get('drawschedule', None)
        source = kwargs.get('source', 1)
        synced = kwargs.get('synced', False)

        if drawschedule is not None:
            drawinput = ScheduleModel.objects.get(id=drawschedule)
        else:
            drawinput = None

        patient_input = PatientModel(
            pid=pid,
            draw_schedule=drawinput,
            source=SourceModel.objects.get(id=source),
            synced=synced)
        patient_input.save()

        return CreatePatientMutation(
            id=patient_input.id,
            pid=patient_input.pid,
            drawschedule=patient_input.draw_schedule,
            source=patient_input.source,
            synced=patient_input.synced,
        )


class LogoutMutation(graphene.Mutation):
    """
       Calls django-logout from mutation and returns redirect URL
       Redirect url acquisition converted to query
       leaving in codebase as example of logout from django internal session
    """

    redirect = graphene.String()

    @classmethod
    def mutate(cls, root, info):
        logout(info.context)
        redirect = settings.LOGOUT_REDIRECT_URL
        return cls(redirect=redirect)


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    delete_token_cookie = graphql_jwt.DeleteJSONWebTokenCookie.Field()
    delete_token_refresh = graphql_jwt.DeleteRefreshTokenCookie.Field()
    # leaving in codebase for example purposes, redirect url moved to query
    #logout = LogoutMutation.Field()
    create_patient = CreatePatientMutation.Field()
    create_specimen = CreateSpecimenMutation.Field()
    create_aliquot = CreateAliquotMutation.Field()
    create_user = CreateUser.Field()
    create_event = CreateEventMutation.Field()
    create_storage = CreateStorageMutation.Field()
    delete_storage = DeleteStorage.Field()
    edit_pid = EditPatientPidMutation.Field()


class Query(graphene.ObjectType):
    # name here is what ends up in query
    # (underscores end up camelCase for graphql spec)
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    redirect_url = graphene.String()
    search_specimen = graphene.List(PatientType, patient=graphene.String())
    all_shipments = graphene.List(ShipmentModelType)
    shipment_manifest = graphene.List(ManifestType, shipment=graphene.Int())
    all_boxes = graphene.List(BoxModelType)
    all_specimen_types = graphene.List(SpecimenTypeModelType)
    all_aliquot_types = graphene.List(AliquotTypeModelType)
    all_slots = graphene.types.json.JSONString(id=graphene.Int())
    all_schedules = graphene.List(ScheduleType)
    all_patients = graphene.List(PatientType, first=graphene.Int(), skip=graphene.Int())
    all_events = graphene.List(EventType)
    all_visits = graphene.List(VisitType)
    all_specimen = graphene.List(SpecimenModelType, patient=graphene.Int())
    all_aliquot = graphene.List(AliquotModelType, specimen=graphene.Int())
    all_storage = graphene.List(StorageType)
    # returns data specifically geared towards UI construction
    storage_ui = graphene.List(StorageUI)
    # type
    box_type = graphene.Field(BoxType, id=graphene.Int())
    patient = graphene.Field(PatientType,
                             id=graphene.Int(),
                             pid=graphene.String(),
                             )
    box = graphene.Field(BoxModelType, id=graphene.Int())

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in')
        return user

    def resolve_redirect_url(self, info):
        redirect = settings.LOGOUT_REDIRECT_URL
        return redirect

    def resolve_all_shipments(self, info):
        return ShipmentModel.objects.all()

    def resolve_shipment_manifest(self, info, **kwargs):
        target_shipment = kwargs.get('shipment')
        shipment = ShipmentModel.objects.get(pk=target_shipment)
        boxes = BoxModel.objects.filter(manifest=shipment)
        all_manifest = []

        for box in boxes:
            slots = BoxSlotModel.objects.filter(box=box.id)
            aliquot_list = []
            for slot in slots:
                aliquot_list.append(slot.content)
            all_manifest.append(ManifestType(key=box.id, name=box.name, aliquot=aliquot_list))
        return all_manifest

    def resolve_storage_ui(self, info):
        """
            StorageUI objects reflect StorageModel parent/child relationships

            The objecttype (StorageUI) is specifically constructed to make
            semantic-ui accordion building easier
            see: https://react.semantic-ui.com/modules/accordion/#advanced-nested

            key: reflects the accordion key (from storage object name)
            title: title for accordion title (from storage object description)
            content: Does this storage object contain other storage objects?
            (storage objects only store parent, children will be added if
            necessary or convenient)
            boxes: Does this storage object contain any boxes?
            css_icon: what icon should be displayed with this box?
            top_level: is the object a "top level" (no parent) object

            The frontend portion handles the inner display rendering as I am
            a firm believer in seperation of interests. Front end should handle
            front end UI problems. Backend should provide the data needed.
            I know the css_icon is an exception here, but that is a persistent
            piece of data.

            Also storing html in a db model seems like a bad idea in general
        """
        storage_return = []

        all_storage_objects = StorageModel.objects.all()
        for location in all_storage_objects:
            content = StorageModel.objects.filter(container=location.id)
            boxes_at_location = BoxModel.objects.filter(storage_location=location.id)
            if location.container is None:
                top_level = True
            else:
                top_level = False
            append_storage = StorageUI(key=("panel-" + location.name),
                                       title=location.name,
                                       content=content,
                                       boxes=boxes_at_location,
                                       css_icon=location.css_icon,
                                       top_level=top_level)
            storage_return.append(append_storage)



        return storage_return

    def resolve_storage_json(self, info):
        return None

    def resolve_search_specimen(self, info, **kwargs):
        """ for testing, to be deprecated for resolve_patient """
        patient = kwargs.get('patient')

        if patient is not None:
            return PatientModel.objects.filter(pid__contains=patient)

        return None

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_all_storage(self, info):
        return StorageModel.objects.all()

    def resolve_all_specimen_types(self, info, **kwargs):
        return SpecimenType.objects.all()

    def resolve_all_visits(self, info):
        return VisitModel.objects.all()

    # will need to adjust model/object to make specimen type parent
    def resolve_all_aliquot_types(self, info, **kwargs):
        return AliquotType.objects.all()

    def resolve_all_boxes(self, info, **kwargs):
        return BoxModel.objects.all()

    def resolve_all_events(self, info, **kwargs):
        return EventModel.objects.all()

    def resolve_box_type(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            box = BoxModel.objects.get(id=id)
            return (box.box_type)

    def resolve_all_schedules(self, info, **kwargs):
        return ScheduleModel.objects.all()

    def resolve_all_slots(self, info, **kwargs):
        box_json = {}
        id = kwargs.get('id')
        box = BoxModel.objects.get(id=id)
        # this can be editable in the future
        content_entry = "{patient} {aliquot} {aliquot_id}"
        box_json["name"] = box.name
        box_json["description"] = box.description
        # builds json object for ingestion by cell table in react
        # row goes first as JS is stuck with a for loop starting with row
        for slot in box.boxslotmodel_set.all():
            column = {}
            content = content_entry.format(
                patient=slot.content.specimen.patient,
                aliquot=slot.content,
                aliquot_id=slot.content.pk)
            column[slot.column_position] = content
            if box_json.get(slot.row_position) is not None:
                box_json[slot.row_position].update(column)
            else:
                box_json[slot.row_position] = column
        return box_json

    def resolve_box(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return BoxSlotModel.objects.all()

    def resolve_all_patients(self, info, first=None, skip=None, **kwargs):
        patient_data = PatientModel.objects.all().order_by('-pk')

        if skip:
            patient_data = patient_data[skip:]

        if first:
            patient_data = patient_data[:first]

        return patient_data

    def resolve_all_specimen(self, info, **kwargs):
        patient = kwargs.get('patient')
        if patient is not None:
            return SpecimenModel.objects.all().filter(patient=patient)
        return SpecimenModel.objects.all()

    def resolve_all_aliquot(self, info, **kwargs):
        specimen = kwargs.get('specimen')
        if specimen is not None:
            return AliquotModel.objects.all().filter(specimen=specimen)
        return AliquotModel.objects.all()

    def resolve_patient(self, info, **kwargs):
        id = kwargs.get('id')
        pid = kwargs.get('pid')

        if id is not None:
            return PatientModel.objects.get(pk=id)

        if pid is not None:
            return PatientModel.objects.get(pid=pid)

        return None


schema = graphene.Schema(query=Query, mutation=Mutation)
