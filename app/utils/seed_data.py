from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine, Base
from app.models import User, Vendor, Category, Product, Coupon, Review
from app.core.security import hash_password

def seed_database(db: Session):
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    # 1. Update product prices to Rupees if already seeded
    p1 = db.query(Product).filter(Product.id == 1).first()
    if p1 and p1.price < 500: # Old USD price
        print("[SEED] Updating existing products to Indian Rupee (₹) prices...")
        p_prices = {1: 3999.00, 2: 6499.00, 3: 8999.00, 4: 12499.00, 5: 4299.00}
        for pid, new_price in p_prices.items():
            p = db.query(Product).filter(Product.id == pid).first()
            if p:
                p.price = new_price
        
        # Update vendor sales
        v1 = db.query(Vendor).filter(Vendor.id == 1).first()
        if v1: v1.total_sales = 125000.0
        v2 = db.query(Vendor).filter(Vendor.id == 2).first()
        if v2: v2.total_sales = 84000.0

        # Update coupons
        c1 = db.query(Coupon).filter(Coupon.code == "WELCOME10").first()
        if c1: c1.min_order_amount = 1000.0
        c2 = db.query(Coupon).filter(Coupon.code == "VENDOR20").first()
        if c2:
            c2.code = "RAZOR500"
            c2.discount_value = 500.0
            c2.min_order_amount = 3000.0

        db.commit()
        print("[SEED] Updated to Rupees (₹) complete!")
        return

    if db.query(User).filter(User.email == "admin@ecommerce.com").first():
        return

    print("[SEED] Seeding database with Indian Rupee (₹) multi-vendor demo data...")

    # Categories
    cat_electronics = Category(name="Electronics & Gadgets", slug="electronics", icon="bi-laptop", description="Laptops, phones, audio & wearables")
    cat_fashion = Category(name="Fashion & Apparel", slug="fashion", icon="bi-bag", description="Trending clothes, jackets & accessories")
    cat_home = Category(name="Home & Living", slug="home-living", icon="bi-house-door", description="Furniture, decor & home essentials")
    cat_beauty = Category(name="Beauty & Care", slug="beauty-care", icon="bi-heart-pulse", description="Skincare, fragrances & wellness")

    db.add_all([cat_electronics, cat_fashion, cat_home, cat_beauty])
    db.commit()

    # Users
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

    # Vendors
    v1 = Vendor(
        user_id=vendor1_user.id,
        store_name="TechNexus Innovations",
        description="Premium flagship electronics, audio gear, and smart wearable technology.",
        logo_url="https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=150",
        rating=4.9,
        total_sales=125000.0,
        status="approved"
    )

    v2 = Vendor(
        user_id=vendor2_user.id,
        store_name="StyleCraft Threads",
        description="High quality urban apparel, designer leather jackets, and modern home decor.",
        logo_url="https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=150",
        rating=4.8,
        total_sales=84000.0,
        status="approved"
    )

    db.add_all([v1, v2])
    db.commit()

    # Products (Rupees ₹)
    p1 = Product(
        vendor_id=v1.id,
        category_id=cat_electronics.id,
        name="ProANC Wireless Noise-Canceling Earbuds",
        description="Active noise cancellation, 30-hour battery life, IPX7 water resistance, and crystal-clear acoustic drivers.",
        price=3999.00,
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
        price=6499.00,
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
        price=8999.00,
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
        price=12499.00,
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
        price=4299.00,
        stock=40,
        image_url="https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600",
        rating_avg=4.6,
        rating_count=19
    )

    db.add_all([p1, p2, p3, p4, p5])
    db.commit()

    # Coupons
    c1 = Coupon(
        code="WELCOME10",
        discount_type="percent",
        discount_value=10.0,
        min_order_amount=1000.0,
        max_uses=500,
        vendor_id=None,
        is_active=True
    )

    c2 = Coupon(
        code="RAZOR500",
        discount_type="fixed",
        discount_value=500.0,
        min_order_amount=3000.0,
        max_uses=100,
        vendor_id=v1.id,
        is_active=True
    )

    db.add_all([c1, c2])
    db.commit()

    # Reviews
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

    print("[SEED] Seeding in Rupees (₹) complete!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
