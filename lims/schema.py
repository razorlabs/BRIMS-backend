from .models import PatientModel

import graphene
from graphene_django import DjangoObjectType


class PatientType(DjangoObjectType):
    class Meta:
        model = PatientModel


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
    # name here is what ends up in query (underscores end up camelCase for graphql mobile)
    all_patients = graphene.List(PatientType)
    patient = graphene.Field(PatientType,
                             id=graphene.Int(),
                             pid=graphene.String(),
                             external_id=graphene.String())

    def resolve_all_patients(self, info):
        return PatientModel.objects.all()

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
