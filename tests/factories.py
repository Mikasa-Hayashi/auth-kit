import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.core.security import hash_password
from app.models.user import User


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    email = factory.Faker("email")  # type: ignore
    full_name = factory.Faker("name")  # type: ignore
    hashed_password = factory.LazyFunction(lambda: hash_password("testpass123"))  # type: ignore
    is_active = True
    is_google_user = False
