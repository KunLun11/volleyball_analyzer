from typing import Optional
from app.api_client import APIClient
from app.infrastructure.client import RabbitMQClient


api_client: Optional[APIClient] = None
rabbitmq_client: Optional[RabbitMQClient] = None
