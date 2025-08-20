"""
GraphQL Schema for alx_backend_graphql_crm project

This module defines the main GraphQL schema for the CRM application.
It includes the Query class with basic GraphQL operations.
"""

import graphene


class Query(graphene.ObjectType):
    """
    Main Query class for GraphQL operations.
    
    This class inherits from graphene.ObjectType and defines
    all available query operations for the GraphQL API.
    """
    
    hello = graphene.String(description="A simple hello field that returns a greeting")
    
    def resolve_hello(self, info):
        """
        Resolver function for the hello field.
        
        Args:
            info: GraphQL resolve info object
            
        Returns:
            str: A greeting message
        """
        return "Hello, GraphQL!"


# Create the GraphQL schema
schema = graphene.Schema(query=Query)