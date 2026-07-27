from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine, Base
from app.models import User, Vendor, Category, Product, Coupon, Review
from app.core.security import hash_password

def seed_database(db: Session):
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    # 1. Check if seed already performed
    if db.query(User).filter(User.email == "admin@ecommerce.com").first():
        print("[SEED] Database already populated.")
        return

    print("[SEED] Seeding database with initial multi-vendor demo data...")

    # 2. Categories
    cat_electronics = Category(name="Electronics & Gadgets", slug="electronics", icon="bi-laptop", description="Laptops, phones, audio & wearables")
    cat_fashion = Category(name="Fashion & Apparel", slug="fashion", icon="bi-bag", description="Trending clothes, jackets & accessories")
    cat_home = Category(name="Home & Living", slug="home-living", icon="bi-house-door", description="Furniture, decor & home essentials")
    cat_beauty = Category(name="Beauty & Care", slug="beauty-care", icon="bi-heart-pulse", description="Skincare, fragrances & wellness")

    db.add_all([cat_electronics, cat_fashion, cat_home, cat_beauty])
    db.commit()

    # 3. Users (Admin, 2 Vendors, 1 Customer)
    admin_user = User(
        email="admin@ecommerce.com",
        hashed_password=hash_password("admin123"),
        full_name="Platform Administrator",
        role="admin",
        is_verified=True,
        status="active"
    )

    vendor1_user = User(
        email="vendor1@technexus.com",
        hashed_password=hash_password("vendor123"),
        full_name="Alex Tech",
        role="vendor",
        is_verified=True,
        status="active"
    )

    vendor2_user = User(
        email="vendor2@stylecraft.com",
        hashed_password=hash_password("vendor123"),
        full_name="Sophia Style",
        role="vendor",
        is_verified=True,
        status="active"
    )

    customer_user = User(
        email="customer@gmail.com",
        hashed_password=hash_password("customer123"),
        full_name="John Doe",
        role="customer",
        is_verified=True,
        status="active"
    )

    db.add_all([admin_user, vendor1_user, vendor2_user, customer_user])
    db.commit()

    # 4. Vendors
    v1 = Vendor(
        user_id=vendor1_user.id,
        store_name="TechNexus Innovations",
        description="Premium flagship electronics, audio gear, and smart wearable technology.",
        logo_url="https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=150",
        rating=4.9,
        total_sales=12500.0,
        status="approved"
    )

    v2 = Vendor(
        user_id=vendor2_user.id,
        store_name="StyleCraft Threads",
        description="High quality urban apparel, designer leather jackets, and modern home decor.",
        logo_url="https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=150",
        rating=4.8,
        total_sales=8400.0,
        status="approved"
    )

    db.add_all([v1, v2])
    db.commit()

    # 5. Products
    p1 = Product(
        vendor_id=v1.id,
        category_id=cat_electronics.id,
        name="ProANC Wireless Noise-Canceling Earbuds",
        description="Active noise cancellation, 30-hour battery life, IPX7 water resistance, and crystal-clear acoustic drivers.",
        price=129.99,
        stock=25,
        image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600",
        rating_avg=4.8,
        rating_count=12
    )

    p2 = Product(
        vendor_id=v1.id,
        category_id=cat_electronics.id,
        name="UltraFit Smart Fitness Watch Series X",
        description="Heart rate tracking, SpO2 monitoring, built-in GPS, AMOLED touchscreen display with customizable watch faces.",
        price=189.50,
        stock=15,
        image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
        rating_avg=4.9,
        rating_count=28
    )

    p3 = Product(
        vendor_id=v2.id,
        category_id=cat_fashion.id,
        name="Vintage Heritage Genuine Leather Jacket",
        description="Handcrafted genuine distressed leather coat featuring breathable inner lining and heavy-duty YKK zippers.",
        price=245.00,
        stock=10,
        image_url="https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600",
        rating_avg=4.7,
        rating_count=8
    )

    p4 = Product(
        vendor_id=v2.id,
        category_id=cat_home.id,
        name="Ergonomic Lumbar Office Executive Chair",
        description="3D adjustable armrests, breathable high-density mesh, dynamic lumbar support and 360-degree silent swivel wheels.",
        price=299.00,
        stock=8,
        image_url="https://images.unsplash.com/photo-1580481072645-022f9a6d1294?w=600",
        rating_avg=5.0,
        rating_count=15
    )

    p5 = Product(
        vendor_id=v1.id,
        category_id=cat_electronics.id,
        name="Mechanical RGB Gaming Keyboard (Hot-Swappable)",
        description="Tactile mechanical switches, per-key RGB backlighting, aircraft-grade aluminum frame and detachable Type-C cable.",
        price=99.99,
        stock=40,
        image_url="https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600",
        rating_avg=4.6,
        rating_count=19
    )

    db.add_all([p1, p2, p3, p4, p5])
    db.commit()

    # 6. Coupons
    c1 = Coupon(
        code="WELCOME10",
        discount_type="percent",
        discount_value=10.0, # 10% off
        min_order_amount=50.0,
        max_uses=500,
        vendor_id=None, # Global
        is_active=True
    )

    c2 = Coupon(
        code="VENDOR20",
        discount_type="fixed",
        discount_value=20.0, # $20 off
        min_order_amount=100.0,
        max_uses=100,
        vendor_id=v1.id, # Specific to TechNexus
        is_active=True
    )

    db.add_all([c1, c2])
    db.commit()

    # 7. Reviews
    r1 = Review(
        product_id=p1.id,
        customer_id=customer_user.id,
        rating=5,
        comment="Absolutely phenomenal sound quality and battery life! The noise cancellation is top notch."
    )
    r2 = Review(
        product_id=p3.id,
        customer_id=customer_user.id,
        rating=5,
        comment="Superior leather craftsmanship. Fits perfectly and looks super stylish!"
    )
    db.add_all([r1, r2])
    db.commit()

    print("[SEED] Database seeding complete!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
