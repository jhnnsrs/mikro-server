import logging
import channels_graphql_ws


from balder.schema import graphql_schema

logger = logging.getLogger(__name__)




class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""
    schema = graphql_schema
    # Uncomment to send keepalive message every 42 seconds.
    send_keepalive_every = 15

    # Uncomment to process requests sequentially (useful for tests).
    # strict_ordering = True

    async def on_connect(self, payload):
        """New client connection handler."""
        # You can `raise` from here to reject the connection.
        user = self.scope.get('user')
        logger.info(f"New client connected with user {self.scope.get('user')}")
