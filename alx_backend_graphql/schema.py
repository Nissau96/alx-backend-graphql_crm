"""
GraphQL Schema for ALX Backend GraphQL CRM Project

This module defines the main GraphQL schema that combines all queries,
mutations, and types for the CRM application.
"""

# alx_backend_graphql/schema.py

import graphene

class Query(graphene.ObjectType):
    """
    Defines the root query for Task 0.
    """
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query)