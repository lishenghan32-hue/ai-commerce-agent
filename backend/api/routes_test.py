"""
Test API routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db

router = APIRouter()


@router.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    """
    Test database connection and CRUD operations
    - Insert a test Product if not exists
    - Query all Products
    - Return JSON response
    """
    from backend.models import Product
    import uuid

    # Check if test product exists
    test_product = db.query(Product).filter(
        Product.name == "测试商品-减肥咖啡"
    ).first()

    if not test_product:
        # Insert test product
        test_product = Product(
            id=uuid.uuid4(),
            name="测试商品-减肥咖啡",
            brand="测试品牌",
            category="饮料",
            description="这是一款测试用的减肥咖啡产品",
            product_url="https://v.douyin.com/test/",
            price="99元"
        )
        db.add(test_product)
        db.commit()
        db.refresh(test_product)
        inserted = True
    else:
        inserted = False

    # Query all products
    all_products = db.query(Product).all()

    return {
        "message": "Database test successful",
        "inserted": inserted,
        "product": test_product.to_dict() if test_product else None,
        "total_products": len(all_products),
        "products": [p.to_dict() for p in all_products]
    }
