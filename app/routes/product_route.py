from fastapi import Request, APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from app.models.user_model import User
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.services.product_service import ProductServices
from starlette.middleware.sessions import SessionMiddleware
from app.database import get_db
import stripe
import os
from dotenv import load_dotenv
load_dotenv()
stripe.api_key = os.getenv("STRIPE_KEY")

def process_payment(amount, currency="usd", source="tok_visa"):
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=source,
            description="Test Charge",
        )
        return charge
    except stripe.error.StripeError as e:
        return {"error": str(e)}

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.post("/buy")
async def buy_product(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    product_id = form_data.get('product_id')
    one_product = ProductServices(db)
    if product_id:
        product = await one_product.get_product_by_id(product_id)
        print(product)
        if product:
            product_dict = product.dict()
            if 'product' not in request.session or len(request.session['product']) == 0:
                request.session['product'] = [product_dict]
            else:
                request.session['product'].append(product_dict)
            return RedirectResponse(url="/cart", status_code=302)
    return None
    
@router.get("/product", response_class=HTMLResponse)
async def main_page(request: Request, db: Session = Depends(get_db)):
    if 'bought' in request.session:
        del request.session['bought']
    all_products = ProductServices(db)
    email = request.session.get("email")
    product_details = await all_products.get_all_products()
    product_details_dict = [product.dict() for product in product_details] 
    if not email:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(
        "product.html",
        {"request": request, "title": "Product Page", "email": email, "product": product_details_dict}
    )

@router.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    if not request.session.get("email"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "cart.html",
        {"request": request, "title": "Shopping Cart", "cart": request.session.get("product"), "bought": request.session.get("bought")}
    )

@router.post("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("product"):
        return RedirectResponse(url = "/cart", status_code=302)
    form_data = await request.form()
    product_id = form_data.get('id')
    product_information = await ProductServices(db).get_product_by_id(product_id)
    product_price = product_information.price
    product_name = product_information.name
    response = process_payment(product_price)
    print(response)
    del request.session['product']
    request.session['bought'] = [{"name": product_name, "price": product_price}]
    return RedirectResponse(url = "/cart", status_code=302)

@router.post("/clear_cart")
async def clear_cart(request: Request):
    del request.session['product']
    return RedirectResponse(url="/product", status_code=302)