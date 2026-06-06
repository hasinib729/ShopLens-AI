import random
import datetime
import hashlib
from sqlalchemy.orm import Session
from app.database import models
from app.utils.config import settings

# Categories and matching products
CATEGORIES = {
    "running shoes": [
        {"title": "Nike Air Zoom Pegasus 40", "brand": "Nike", "price": 11999.0, "color": "Red", "desc": "High performance running shoe with responsive cushioning."},
        {"title": "Adidas Ultraboost Light", "brand": "Adidas", "price": 14999.0, "color": "Black", "desc": "Lightweight running shoes built for energy return."},
        {"title": "Puma Velocity Nitro 2", "brand": "Puma", "price": 7999.0, "color": "Blue", "desc": "All-in-one neutral running shoe for any distance."},
        {"title": "Asics Gel-Kayano 30", "brand": "Asics", "price": 12500.0, "color": "Red", "desc": "Maximum support and stability running shoe."},
        {"title": "Nike Revolution 6 Flyease", "brand": "Nike", "price": 3600.0, "color": "White", "desc": "Comfortable, easy-to-wear sneakers for daily run."}
    ],
    "handbags": [
        {"title": "Coach Leather Tote Bag", "brand": "Coach", "price": 24900.0, "color": "Brown", "desc": "Classic textured leather handbag with gold-tone hardware."},
        {"title": "Michael Kors Jet Set Travel Bag", "brand": "Michael Kors", "price": 18500.0, "color": "Black", "desc": "Saffiano leather top-zip tote bag."},
        {"title": "Kate Spade Spade Flower Jacquard Tote", "brand": "Kate Spade", "price": 15900.0, "color": "Blue", "desc": "Elegant woven jacquard bag with stripes."},
        {"title": "Fossil Rachel Satchel", "brand": "Fossil", "price": 8499.0, "color": "Tan", "desc": "Casual eco-leather satchel bag with cross-body strap."}
    ],
    "smartwatches": [
        {"title": "Apple Watch Series 9 GPS", "brand": "Apple", "price": 41900.0, "color": "Midnight", "desc": "Advanced health sensors, sleep tracking, and crash detection."},
        {"title": "Samsung Galaxy Watch 6", "brand": "Samsung", "price": 29999.0, "color": "Silver", "desc": "Personalized heart rate zones and advanced sleep coaching."},
        {"title": "Garmin Venu 3 Smartwatch", "brand": "Garmin", "price": 44900.0, "color": "Black", "desc": "GPS smartwatch with bright AMOLED display and built-in speaker."},
        {"title": "Fossil Gen 6 Smartwatch", "brand": "Fossil", "price": 22900.0, "color": "Brown", "desc": "Fast charging smartwatch on Wear OS by Google."}
    ],
    "gaming mouse": [
        {"title": "Logitech G502 LIGHTSPEED Wireless", "brand": "Logitech", "price": 9999.0, "color": "Black", "desc": "High performance wireless gaming mouse for FPS and MMO."},
        {"title": "Razer DeathAdder V3 Pro", "brand": "Razer", "price": 12900.0, "color": "White", "desc": "Ultra-lightweight wireless ergonomic esports gaming mouse."},
        {"title": "SteelSeries Rival 3 Wireless", "brand": "SteelSeries", "price": 4999.0, "color": "Black", "desc": "Dual wireless gaming mouse with long battery life."},
        {"title": "Corsair Dark Core RGB Pro", "brand": "Corsair", "price": 7499.0, "color": "Black", "desc": "Wireless gaming mouse with sub-1ms SLIPSTREAM technology."}
    ],
    "formal shirts": [
        {"title": "Louis Philippe Slim Fit Formal Shirt", "brand": "Louis Philippe", "price": 2499.0, "color": "Blue", "desc": "Premium cotton slim-fit shirt for business wear."},
        {"title": "Van Heusen Solid Formal Shirt", "brand": "Van Heusen", "price": 1899.0, "color": "White", "desc": "Classic white wrinkle-free formal shirt."},
        {"title": "Peter England Slim Fit Shirt", "brand": "Peter England", "price": 1299.0, "color": "Black", "desc": "Stretchable slim fit formal shirt for office."},
        {"title": "Arrow Classic Fit Striped Shirt", "brand": "Arrow", "price": 2199.0, "color": "Blue", "desc": "Cotton regular fit formal striped shirt."}
    ]
}

BRANDS = ["Nike", "Adidas", "Puma", "Asics", "Coach", "Michael Kors", "Kate Spade", "Fossil", "Apple", "Samsung", "Garmin", "Logitech", "Razer", "SteelSeries", "Corsair", "Louis Philippe", "Van Heusen", "Peter England", "Arrow"]
COLORS = ["Red", "Black", "Blue", "White", "Brown", "Tan", "Silver", "Midnight", "Green", "Grey"]

def get_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def seed_database(db: Session):
    # Check if database is already seeded
    if db.query(models.Product).count() > 0:
        return
    
    print("Seeding database...")
    
    # 1. Create default users (admin & user)
    # plain text passwords for mock seeder, hashed for simplicity
    admin_user = models.User(
        email="admin@shoplens.ai",
        hashed_password="pbkdf2:sha256:600000$mockedadminhash", # simple mock hash
        role="admin"
    )
    test_user = models.User(
        email="user@shoplens.ai",
        hashed_password="pbkdf2:sha256:600000$mockeduserhash",
        role="user"
    )
    db.add(admin_user)
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # 2. Insert Products
    db_products = []
    pid_counter = 1000
    for cat_name, items in CATEGORIES.items():
        for item in items:
            p_id = f"PROD{pid_counter}"
            pid_counter += 1
            # Mock image url
            img_hash = get_hash(item["title"])[:8]
            img_url = f"/static/images/products/{img_hash}.jpg"
            
            product = models.Product(
                product_id=p_id,
                title=item["title"],
                description=item["desc"],
                brand=item["brand"],
                category=cat_name,
                price=item["price"],
                image_url=img_url,
                rating=round(random.uniform(3.5, 4.9), 1),
                reviews_count=random.randint(10, 500),
                features={
                    "color": item["color"],
                    "brand": item["brand"],
                    "category": cat_name,
                    "style": "Modern"
                }
            )
            db.add(product)
            db_products.append(product)
            
    # Add a few extra random products to reach ~30 products
    for i in range(10):
        brand = random.choice(BRANDS)
        cat = random.choice(list(CATEGORIES.keys()))
        color = random.choice(COLORS)
        price = round(random.uniform(1000.0, 15000.0), 2)
        p_id = f"PROD{pid_counter}"
        pid_counter += 1
        
        title = f"{brand} Casual {cat[:-1].capitalize()} - {color}"
        desc = f"Premium quality {cat} designed by {brand} in {color} color."
        img_hash = get_hash(title)[:8]
        
        product = models.Product(
            product_id=p_id,
            title=title,
            description=desc,
            brand=brand,
            category=cat,
            price=price,
            image_url=f"/static/images/products/{img_hash}.jpg",
            rating=round(random.uniform(3.0, 4.8), 1),
            reviews_count=random.randint(5, 120),
            features={
                "color": color,
                "brand": brand,
                "category": cat
            }
        )
        db.add(product)
        db_products.append(product)
        
    db.commit()
    
    # Refresh all product IDs
    for p in db_products:
        db.refresh(p)
        
    # 3. Create active A/B experiments
    exp1 = models.ABExperiment(
        experiment_name="search_ranking_v2",
        model_a_name="cosine_relevance_v1",
        model_b_name="xgboost_ltr_v2",
        is_active=True
    )
    exp2 = models.ABExperiment(
        experiment_name="recommender_comparison",
        model_a_name="popularity_baseline",
        model_b_name="two_tower_v2",
        is_active=True
    )
    db.add(exp1)
    db.add(exp2)
    db.commit()
    
    # 4. Generate search logs & sessions & activity
    sessions = [f"sess_{get_hash(str(i))[:12]}" for i in range(15)]
    
    # Create User Sessions
    for sess_id in sessions:
        user_sess = models.UserSession(
            session_id=sess_id,
            user_id=test_user.id if random.random() > 0.3 else None,
            device=random.choice(["Desktop Chrome", "Mobile Safari", "Firefox Windows"]),
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 10))
        )
        db.add(user_sess)
        
        # Create Search Session summary
        q_count = random.randint(1, 8)
        click_count = random.randint(0, q_count)
        conversion = click_count > 0 and random.random() > 0.4
        
        search_sess = models.SearchSession(
            session_id=sess_id,
            user_id=user_sess.user_id,
            query_count=q_count,
            avg_latency=random.uniform(40.0, 180.0),
            click_count=click_count,
            conversion=conversion
        )
        db.add(search_sess)
        
    db.commit()
    
    # Create detailed activities
    queries = [
        "red running shoes under 5000", 
        "wireless mouse", 
        "black formal shirt slim fit", 
        "handbags Fossil", 
        "smartwatch Apple under 45000"
    ]
    
    for sess_id in sessions:
        # User activities
        p_views = random.sample(db_products, k=random.randint(1, 5))
        for p in p_views:
            # View event
            view_act = models.UserActivity(
                session_id=sess_id,
                user_id=test_user.id if "user" in sess_id else None,
                product_id=p.id,
                event_type="view",
                dwell_time=random.randint(5, 120),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=random.randint(1, 48))
            )
            db.add(view_act)
            
            # Click probability
            if random.random() > 0.4:
                click_act = models.UserActivity(
                    session_id=sess_id,
                    product_id=p.id,
                    event_type="click",
                    created_at=view_act.created_at + datetime.timedelta(seconds=random.randint(2, 10))
                )
                db.add(click_act)
                
                # Cart probability
                if random.random() > 0.5:
                    cart_act = models.UserActivity(
                        session_id=sess_id,
                        product_id=p.id,
                        event_type="cart",
                        created_at=click_act.created_at + datetime.timedelta(seconds=random.randint(5, 30))
                    )
                    db.add(cart_act)
                    
                    # Purchase probability
                    if random.random() > 0.6:
                        purchase_act = models.UserActivity(
                            session_id=sess_id,
                            product_id=p.id,
                            event_type="purchase",
                            created_at=cart_act.created_at + datetime.timedelta(seconds=random.randint(10, 60))
                        )
                        db.add(purchase_act)
                        
                        # Log A/B testing conversions
                        ab_log = models.ABExperimentLog(
                            experiment_name="search_ranking_v2",
                            session_id=sess_id,
                            group_name=random.choice(["A", "B"]),
                            query_text=random.choice(queries),
                            product_id=p.id,
                            is_clicked=True,
                            is_purchased=True
                        )
                        db.add(ab_log)
                        
        # Search queries
        for _ in range(random.randint(1, 3)):
            q = random.choice(queries)
            # Simulate query understanding
            cat = None
            if "shoes" in q: cat = "running shoes"
            elif "mouse" in q: cat = "gaming mouse"
            elif "shirt" in q: cat = "formal shirts"
            elif "handbags" in q: cat = "handbags"
            elif "smartwatch" in q: cat = "smartwatches"
            
            color = "Red" if "red" in q else ("Black" if "black" in q else None)
            brand = "Apple" if "Apple" in q else ("Fossil" if "Fossil" in q else None)
            price = 5000.0 if "5000" in q else (45000.0 if "45000" in q else None)
            
            s_log = models.SearchLog(
                session_id=sess_id,
                user_id=test_user.id if "user" in sess_id else None,
                query_text=q,
                search_type="text",
                parsed_category=cat,
                parsed_color=color,
                parsed_brand=brand,
                parsed_price_max=price,
                latency_ms=random.uniform(50.0, 150.0)
            )
            db.add(s_log)
            
    db.commit()
    
    # 5. Populate standard metrics over the last 7 days
    base_date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    for day in range(8):
        current_date = base_date + datetime.timedelta(days=day)
        
        # Search metrics
        search_met = models.SearchMetric(
            recall_at_10=round(random.uniform(0.81, 0.89), 3),
            precision_at_10=round(random.uniform(0.76, 0.84), 3),
            ndcg_at_10=round(random.uniform(0.79, 0.87), 3),
            mrr=round(random.uniform(0.80, 0.88), 3),
            query_coverage=round(random.uniform(0.92, 0.98), 3),
            zero_result_rate=round(random.uniform(0.01, 0.05), 3),
            logged_date=current_date
        )
        db.add(search_met)
        
        # Recommendation metrics
        rec_met = models.RecMetric(
            map=round(random.uniform(0.72, 0.79), 3),
            hit_rate=round(random.uniform(0.80, 0.87), 3),
            ctr=round(random.uniform(0.12, 0.19), 3),
            logged_date=current_date
        )
        db.add(rec_met)
        
    db.commit()
    print("Database seeding completed successfully!")
