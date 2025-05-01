from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import user_schema as user_schema
from sqlalchemy.sql import select, insert
from app.models import user_model as user_models
from fastapi import Request
import tracemalloc
from app import app
import os
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
tracemalloc.start()
import re
email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
password_regex = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$")



class UserServices:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user, request):
        if not self.session:
            raise ValueError("Session is not initialized")
        is_valid = await UserRegisterValidation(self.session).validate_user(user['email'], user['password'], request)
        if is_valid:
            return None
        
        query = insert(user_models.User).values(email=user['email'], password=user['password'])
        try:
            await self.session.execute(query)
            await self.session.commit()
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        return user.get('email')
    
    async def get_user_by_email(self, email: str, request: Request):
        if not self.session:
            raise ValueError("Session is not initialized")

        query = select(user_models.User).where(user_models.User.email == email)
        try:
            # Await the form data
            form_data = await request.form()
            password = form_data.get('password')

            result = await self.session.execute(query)
            user = result.scalars().first()

            if user and user.password == password:
                return user_schema.UserCreate.from_orm(user)
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        return None
    
class UserRegisterValidation:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate_user(self, email: str, password: str, request) -> bool:
        flag = False
        try:

            query = select(user_models.User).where(user_models.User.email == email)
            result = await self.session.execute(query)
            user = result.scalars().first()

            if user:
                if "flash_messages" not in request.session:
                    request.session["flash_messages"] = []
                request.session["flash_messages"].append({"email": "Please use a different email", "category": "error"})
                return True

            if not email_regex.match(email):
                if "flash_messages" not in request.session:
                    request.session["flash_messages"] = []
                request.session["flash_messages"].append({"email": "Invalid email format", "category": "error"})
                flag = True

            if len(email) < 5 or len(email) > 90:
                if "flash_messages" not in request.session:
                    request.session["flash_messages"] = []
                request.session["flash_messages"].append({"email": "Email must be between 5 and 90 characters", "category": "error"})
                flag = True

            if not password_regex.match(password):
                if "flash_messages" not in request.session:
                    request.session["flash_messages"] = []
                request.session["flash_messages"].append({"password": "Password must include at least one uppercase letter, one lowercase letter, one digit, and one special character", "category": "error"})
                flag = True

            if len(password) < 8 or len(password) > 32:
                if "flash_messages" not in request.session:
                    request.session["flash_messages"] = []
                request.session["flash_messages"].append({"password": "Password must be between 8 and 32 characters", "category": "error"})
                flag = True

            return flag 
        except Exception as e:
            print(f"Error validating user: {e}")
            return False