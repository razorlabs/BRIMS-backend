from .models import PatientModel, SpecimenModel, AliquotModel

import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

class PatientType(DjangoObjectType):
    class Meta:
        model = PatientModel

class SpecimenType(DjangoObjectType):
    type = graphene.String()
    patientid = graphene.Int()

    class Meta:
        model = SpecimenModel
        description = " Specimens collected for a patient "

    # return actual type as string rather then type as an object
    # example: "Dried Blood Spot" instead of type{ type: "Dried Blood Spot"}
    def resolve_type(self, info):
        return '{}'.format(self.type.type)

    # override type field to return a string rather than an object
    def resolve_patientid(self, info):
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


class CreatePatientMutation(graphene.Mutation):
    id = graphene.Int()
    pid = graphene.String()
    external_id = graphene.String()

    class Arguments:
        pid = graphene.String()
        external_id = graphene.String()

    def mutate(self, info, pid, external_id):
        patient_input = PatientModel(pid=pid, external_id=external_id)
        patient_input.save()
        return CreatePatientMutation(
            id=patient_input.id,
            pid=patient_input.pid,
            external_id=patient_input.external_id,
        )

class Mutation(graphene.ObjectType):
    create_patient = CreatePatientMutation.Field()

class Query(graphene.ObjectType):
    # name here is what ends up in query (underscores end up camelCase for graphql spec)
    all_patients = graphene.List(PatientType)
    all_specimen = graphene.List(SpecimenType, patient=graphene.Int())
    all_aliquot = graphene.List(AliquotType, specimen=graphene.Int())
    patient = graphene.Field(PatientType,
                             id=graphene.Int(),
                             pid=graphene.String(),
                             external_id=graphene.String())

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
