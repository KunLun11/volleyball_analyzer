# import json
# import logging

# import aio_pika
# from asyncpg import Pool

# from app.domain.values.identifiers import ChatID
# from app.infrastructure.uow.postgres_uow import PostgresUnitOfWork
# from app.interfaces.rabbitmq_handlers.base import MessageHandler

# logger = logging.getLogger(__name__)


# class GetLiveMatchHandle(MessageHandler):
#     def __init__(self, postgres_pool: Pool, rabbitmq_bus):
#         self.pool = postgres_pool
#         self.rabbitmq_bus = rabbitmq_bus

#     async def handle(self, payload, message):
#         chat_id = payload.get("chat_id")
#         correlation_id = payload.get("correlation_id")
#         reply_to = payload.get("reply_to")

#         if not chat_id or not correlation_id or not reply_to:
#             logger.error(f"Missing required fields in payload: {payload}")
#             return

#         async with PostgresUnitOfWork(self.pool) as uow:
#             chat_id_obj = ChatID(chat_id)
#             match = await uow.matches().get_live_by_chat(chat_id_obj)

#             if match:
#                 matches_list = [self._serialize_match(match)]
#             else:
#                 matches_list = []

#             response = {
#                 "correlation_id": correlation_id,
#                 "matches": matches_list,
#             }

#             await self.rabbitmq_bus._channel.default_exchange.publish(
#                 aio_pika.Message(
#                     body=json.dumps(response).encode(),
#                     correlation_id=correlation_id,
#                     content_type="application/json",
#                 ),
#                 routing_key=reply_to,
#             )

#     def _serialize_match(self, match):
#         composition_a = [p.value for p in match.composition_a.get_players()]
#         composition_b = [p.value for p in match.composition_b.get_players()]
#         return {
#             "id": str(match.id.value),
#             "team_a_name": match.team_a_name.value,
#             "team_b_name": match.team_b_name.value,
#             "composition_a": composition_a,
#             "composition_b": composition_b,
#             "status": match.status.name,
#             "created_at": match.created_at.isoformat(),
#             "current_set": match.current_set.value,
#             "score_a": match.score.a.value,
#             "score_b": match.score.b.value,
#             "rotation_a": match.rotation.team_a.value,
#             "rotation_b": match.rotation.team_b.value,
#         }
