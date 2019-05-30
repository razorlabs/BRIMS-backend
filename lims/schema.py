import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required

from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model

from .models import PatientModel, SpecimenModel, AliquotModel, BoxModel, BoxTypeModel, BoxSlotModel, EventModel, ScheduleModel, SourceModel

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class PatientType(DjangoObjectType):
    source = graphene.String()
    class Meta:
        model = PatientModel

    def resolve_source(self, info):
        return '{}'.format(self.source.name)

class Box(DjangoObjectType):
    class Meta:
        model = BoxModel

class BoxType(DjangoObjectType):
    class Meta:
        model = BoxTypeModel

class BoxSlotType(DjangoObjectType):
    class Meta:
        model = BoxSlotModel

class EventType(DjangoObjectType):
    class Meta:
        model = EventModel

class ScheduleType(DjangoObjectType):
    class Meta:
        model = ScheduleModel


class SpecimenType(DjangoObjectType):
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



class AliquotType(DjangoObjectType):
    visit = graphene.String()
    type = graphene.String()
    specimenid = graphene.Int()
    class Meta:
        model = AliquotModel

    def resolve_specimenid(self, info):
        return '{}'.format(self.specimen.id)

    def resolve_visit(self, info):
        return '{}'.format(self.visit.label)

    def resolve_type(self, info):
        return '{}'.format(self.type.type)


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

class CreatePatientMutation(graphene.Mutation):
    """
    Allows creation of a patient from web UI or external source
    Arguments:
    id --
    pid --
    external_id --
    source -- should be set based on django settings (local system or remote)
    synced --
    """
    id = graphene.Int()
    pid = graphene.String()
    external_id = graphene.String()
    source = graphene.String()
    synced = graphene.Boolean()

    class Arguments:
        pid = graphene.String()
        external_id = graphene.String()
        source = graphene.String()
        synced = graphene.Boolean()

    def mutate(self, info, pid, **kwargs):
        external_id = kwargs.get('external_id', None)
        source = kwargs.get('source', 1)
        synced = kwargs.get('synced', False)

        patient_input = PatientModel(
            pid=pid,
            external_id=external_id,
            source=source,
            synced=synced)
        patient_input.save()

        return CreatePatientMutation(
            id=patient_input.id,
            pid=patient_input.pid,
            external_id=patient_input.external_id,
            source=patient_input.source,
            synced=patient_input.synced,
        )

class CreatePatientAPIMutation(graphene.Mutation):
    id = graphene.Int()
    pid = graphene.String()
    external_id = graphene.String()
    # Was the patient created in the local system or
    source = graphene.String()
    synced = graphene.Boolean()

    class Arguments:
        pid = graphene.String()
        external_id = graphene.String()
        source = graphene.String()
        synced = graphene.Boolean()

    def mutate(self, info, pid, **kwargs):
        external_id = kwargs.get('external_id', None)
        synced = kwargs.get('synced', True)

        patient_input = PatientModel(
            pid=pid,
            external_id=external_id,
            synced=synced)
        patient_input.save()

        return CreatePatientMutation(
            id=patient_input.id,
            pid=patient_input.pid,
            external_id=patient_input.external_id,
            synced=patient_input.synced,
        )

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_patient = CreatePatientMutation.Field()
    create_patient_api = CreatePatientAPIMutation.Field()
    create_user = CreateUser.Field()
    create_event = CreateEventMutation.Field()


class Query(graphene.ObjectType):
    # name here is what ends up in query
    # (underscores end up camelCase for graphql spec)
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    all_boxes = graphene.List(Box)
    all_slots = graphene.types.json.JSONString(id=graphene.Int())
    all_schedules = graphene.List(ScheduleType)
    all_patients = graphene.List(PatientType)
    all_events = graphene.List(EventType)
    all_specimen = graphene.List(SpecimenType, patient=graphene.Int())
    all_aliquot = graphene.List(AliquotType, specimen=graphene.Int())
    box_type = graphene.Field(BoxType, id=graphene.Int())
    patient = graphene.Field(PatientType,
                             id=graphene.Int(),
                             pid=graphene.String(),
                             external_id=graphene.String())
    box = graphene.Field(Box, id=graphene.Int())

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user

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

    def resolve_all_patients(self, info, **kwargs):
        return PatientModel.objects.all()

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
        external_id = kwargs.get('external_id')

        if id is not None:
            return PatientModel.objects.get(pk=id)

        if pid is not None:
            return PatientModel.objects.get(pid=pid)

        if external_id is not None:
            return PatientModel.objects.get(external_id=external_id)

        return None


schema = graphene.Schema(query=Query, mutation=Mutation)
