"""
GraphQL Schema for ALX Backend GraphQL CRM Project

This module defines the main GraphQL schema that combines all queries,
mutations, and types for the CRM application.
"""

import graphene
import crm.schema

class Query(crm.schema.Query, graphene.ObjectType):
    # This class will inherit from crm.schema.Query
    # and any other app queries you may have
    pass

class Mutation(crm.schema.Mutation, graphene.ObjectType):
    # This class will inherit from crm.schema.Mutation
    # and any other app mutations you may have
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)