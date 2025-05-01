from app.routes import product_route, user_route

def register(app):
    app.include_router(user_route.router)
    app.include_router(product_route.router)