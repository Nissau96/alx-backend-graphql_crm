"""
GraphQL Schema for alx_backend_graphql_crm project

This module defines the main GraphQL schema for the CRM application.
It includes the Query class with basic GraphQL operations.
"""

# alx_backend_graphql/schema.py

import graphene
import crm.schema

class Query(crm.schema.Query, graphene.ObjectType):
    # This class inherits all queries from the crm app
    pass

class Mutation(crm.schema.Mutation, graphene.ObjectType):
    # This class inherits all mutations from the crm app
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)