"""
GraphQL Schema for ALX Backend GraphQL CRM Project

This module defines the main GraphQL schema that combines all queries,
mutations, and types for the CRM application.
"""

# alx_backend_graphql_crm/schema.py

import graphene

# 1. Define a Query class that inherits from graphene.ObjectType
class Query(graphene.ObjectType):
    """
    Defines the root queries for the GraphQL API.
    """
    # 2. Define a field named 'hello' of type String
    #    The resolver function for this field simply returns a static string.
    hello = graphene.String(default_value="Hello, GraphQL!")

# 3. Create the schema instance, passing the root Query class
schema = graphene.Schema(query=Query)