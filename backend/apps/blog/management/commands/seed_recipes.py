from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

from apps.blog.models import Recipe, Category

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial recipe data."

    def handle(self, *args, **options):
        if not User.objects.exists():
            self.stdout.write(self.style.ERROR("No users found. Please create a user first, e.g., a superuser."))
            return

        author = User.objects.first()
        self.stdout.write(f"Using author: {author.email}")

        recipes_data = [
            {
                "title": "Classic Pancakes",
                "description": "Fluffy homemade breakfast pancakes.",
                "instructions": """
        1. Mix flour, sugar, baking powder, and salt.
        2. Add milk, eggs, and melted butter.
        3. Whisk until smooth.
        4. Cook on a hot greased pan until golden brown.
        """,
                "prep_time": 10,
                "cook_time": 15,
                "servings": 4,
                "difficulty": "Easy",
                "category": "Breakfast",
                "tags": ["Easy", "Quick", "Breakfast", "Kid Friendly"],
            },
            {
                "title": "Creamy Chicken Pasta",
                "description": "Rich creamy pasta with grilled chicken.",
                "instructions": """
        1. Cook pasta until al dente.
        2. Grill seasoned chicken breast.
        3. Prepare cream sauce with garlic and parmesan.
        4. Combine pasta, sauce, and sliced chicken.
        """,
                "prep_time": 20,
                "cook_time": 25,
                "servings": 4,
                "difficulty": "Medium",
                "category": "Dinner",
                "tags": ["Creamy", "Chicken", "Pasta", "Comfort Food"],
            },
            {
                "title": "Spicy Beef Tacos",
                "description": "Mexican-style tacos with spicy minced beef.",
                "instructions": """
        1. Cook minced beef with taco seasoning.
        2. Warm taco shells.
        3. Fill with beef, lettuce, tomatoes, and cheese.
        4. Serve with salsa.
        """,
                "prep_time": 15,
                "cook_time": 20,
                "servings": 5,
                "difficulty": "Easy",
                "category": "Mexican Cuisine",
                "tags": ["Spicy", "Beef", "Street Food", "Quick"],
            },
            {
                "title": "Vegetable Stir Fry",
                "description": "Healthy mixed vegetable stir fry.",
                "instructions": """
        1. Chop vegetables evenly.
        2. Heat oil in a wok.
        3. Stir fry garlic and ginger.
        4. Add vegetables and soy sauce.
        5. Cook until tender-crisp.
        """,
                "prep_time": 15,
                "cook_time": 10,
                "servings": 3,
                "difficulty": "Easy",
                "category": "Vegetarian",
                "tags": ["Healthy", "Vegetarian", "Quick", "Low Fat"],
            },
            {
                "title": "Kenyan Pilau",
                "description": "Traditional Kenyan spiced rice dish.",
                "instructions": """
        1. Fry onions until caramelized.
        2. Add pilau masala and beef.
        3. Add rice and stock.
        4. Simmer until rice is fully cooked.
        """,
                "prep_time": 20,
                "cook_time": 45,
                "servings": 6,
                "difficulty": "Medium",
                "category": "Kenyan Cuisine",
                "tags": ["Traditional", "Rice Dish", "African Cuisine"],
            },
            {
                "title": "Chocolate Brownies",
                "description": "Rich fudgy chocolate brownies.",
                "instructions": """
        1. Melt butter and chocolate.
        2. Mix with sugar and eggs.
        3. Add flour and cocoa powder.
        4. Bake until set.
        """,
                "prep_time": 15,
                "cook_time": 30,
                "servings": 8,
                "difficulty": "Easy",
                "category": "Desserts",
                "tags": ["Chocolate", "Dessert", "Baked", "Sweet"],
            },
            {
                "title": "Grilled BBQ Wings",
                "description": "Smoky grilled chicken wings with BBQ sauce.",
                "instructions": """
        1. Marinate chicken wings.
        2. Grill until crispy.
        3. Brush with BBQ sauce.
        4. Serve hot.
        """,
                "prep_time": 25,
                "cook_time": 35,
                "servings": 4,
                "difficulty": "Medium",
                "category": "BBQ",
                "tags": ["BBQ", "Chicken", "Smoky", "Party Food"],
            },
            {
                "title": "Mango Smoothie",
                "description": "Refreshing tropical mango smoothie.",
                "instructions": """
        1. Add mangoes, yogurt, and ice into blender.
        2. Blend until smooth.
        3. Serve chilled.
        """,
                "prep_time": 5,
                "cook_time": 0,
                "servings": 2,
                "difficulty": "Easy",
                "category": "Smoothies",
                "tags": ["Healthy", "Smoothie", "Quick", "Summer Recipes"],
            },
            {
                "title": "Margherita Pizza",
                "description": "Classic Italian pizza with mozzarella and basil.",
                "instructions": """
        1. Prepare pizza dough.
        2. Spread tomato sauce evenly.
        3. Add mozzarella cheese.
        4. Bake until crust is golden.
        5. Garnish with basil leaves.
        """,
                "prep_time": 30,
                "cook_time": 20,
                "servings": 4,
                "difficulty": "Hard",
                "category": "Italian Cuisine",
                "tags": ["Pizza", "Italian Cuisine", "Cheese", "Baked"],
            },
            {
                "title": "Caesar Salad",
                "description": "Fresh salad with Caesar dressing and croutons.",
                "instructions": """
        1. Wash and chop lettuce.
        2. Prepare Caesar dressing.
        3. Toss lettuce with dressing.
        4. Top with croutons and parmesan cheese.
        """,
                "prep_time": 15,
                "cook_time": 0,
                "servings": 2,
                "difficulty": "Easy",
                "category": "Salads",
                "tags": ["Healthy", "Fresh", "Quick", "Low Carb"],
            },
        ]

        self.stdout.write("Seeding recipes...")

        for item in recipes_data:
            category, created = Category.objects.get_or_create(
                title=item["category"],
                defaults={"slug": slugify(item["category"])}
            )
            if created:
                self.stdout.write(f"Created category: {category.title}")

            # Check if a recipe with the same slug already exists
            slug = slugify(item["title"])
            if Recipe.objects.filter(slug=slug).exists():
                self.stdout.write(self.style.WARNING(f"Recipe '{item['title']}' already exists. Skipping."))
                continue

            recipe = Recipe.objects.create(
                title=item["title"],
                slug=slug,
                description=item["description"],
                instructions=item["instructions"],
                prep_time=item["prep_time"],
                cook_time=item["cook_time"],
                servings=item["servings"],
                difficulty=item["difficulty"],
                publish=timezone.now(),
                category=category,
                status="PB",
                author=author,
            )

            recipe.tags.add(*item["tags"])
            self.stdout.write(f"Created recipe: {recipe.title}")

        self.stdout.write(self.style.SUCCESS("Recipes seeded successfully."))
