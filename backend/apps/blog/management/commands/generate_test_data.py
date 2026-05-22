import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from taggit.models import Tag, TaggedItem

from apps.blog.models import Category, Comment, Post

RECIPE_CATEGORIES = [
    "Breakfast",
    "Lunch",
    "Dinner",
    "Dessert",
    "Snacks",
    "Drinks",
    "Vegetarian",
    "Meal Prep",
]

RECIPE_TAGS = [
    "easy",
    "quick",
    "healthy",
    "comfort food",
    "high protein",
    "vegetarian",
    "vegan",
    "gluten free",
    "one pan",
    "weeknight",
    "kid friendly",
    "budget friendly",
    "make ahead",
    "meal prep",
    "fresh",
    "seasonal",
]

RECIPE_USERS = [
    ("Ava", "Stone"),
    ("Noah", "Park"),
    ("Maya", "Lopez"),
    ("Liam", "Nguyen"),
    ("Zoe", "Carter"),
    ("Ivy", "Reed"),
]

RECIPE_COMMENTS = [
    "Made this for dinner and it disappeared fast.",
    "I swapped in whole wheat pasta and it still worked well.",
    "This is going into my weekly meal prep rotation.",
    "Simple steps and the flavor is excellent.",
    "My family asked for seconds, so this is a keeper.",
    "I added extra herbs and it turned out great.",
    "Perfect for a busy weeknight and easy to follow.",
    "I baked it a little longer and the texture was spot on.",
]

RECIPE_POSTS = [
    {
        "title": "Overnight Oats with Berries and Honey",
        "category": "Breakfast",
        "tags": ["easy", "healthy", "make ahead", "fresh"],
        "summary": "A creamy breakfast jar with rolled oats, yogurt, berries, and a drizzle of honey.",
        "ingredients": [
            "1 cup rolled oats",
            "1 cup milk or oat milk",
            "1/2 cup Greek yogurt",
            "1 tablespoon chia seeds",
            "1/2 cup mixed berries",
            "1 tablespoon honey",
        ],
        "steps": [
            "Combine oats, milk, yogurt, and chia seeds in a jar or bowl.",
            "Stir well, cover, and refrigerate overnight.",
            "Top with berries and honey before serving.",
        ],
    },
    {
        "title": "Avocado Toast with Chili Flakes and Lemon",
        "category": "Breakfast",
        "tags": ["quick", "healthy", "vegetarian", "easy"],
        "summary": "A bright, savory toast topped with smashed avocado, lemon, and a little heat.",
        "ingredients": [
            "2 slices sourdough bread",
            "1 ripe avocado",
            "1 teaspoon lemon juice",
            "Pinch of salt",
            "Pinch of chili flakes",
            "Olive oil for drizzling",
        ],
        "steps": [
            "Toast the bread until golden and crisp.",
            "Mash the avocado with lemon juice and salt.",
            "Spread on toast, then finish with chili flakes and olive oil.",
        ],
    },
    {
        "title": "Spinach Feta Breakfast Wrap",
        "category": "Breakfast",
        "tags": ["meal prep", "high protein", "quick", "kid friendly"],
        "summary": "A portable breakfast wrap filled with eggs, spinach, and feta cheese.",
        "ingredients": [
            "2 eggs",
            "1 cup spinach",
            "2 tablespoons crumbled feta",
            "1 large tortilla",
            "1 teaspoon butter",
            "Salt and pepper",
        ],
        "steps": [
            "Scramble the eggs in butter with spinach, salt, and pepper.",
            "Warm the tortilla and spoon the filling into the center.",
            "Add feta, wrap tightly, and serve warm.",
        ],
    },
    {
        "title": "Blueberry Banana Pancakes",
        "category": "Breakfast",
        "tags": ["weekend", "easy", "fresh", "kid friendly"],
        "summary": "Fluffy pancakes with mashed banana and blueberries for a naturally sweet start.",
        "ingredients": [
            "1 ripe banana",
            "1 cup flour",
            "1 tablespoon sugar",
            "1 teaspoon baking powder",
            "1 cup milk",
            "1/2 cup blueberries",
        ],
        "steps": [
            "Mix the dry ingredients in a bowl.",
            "Stir in mashed banana and milk until just combined.",
            "Fold in blueberries and cook on a hot skillet until golden.",
        ],
    },
    {
        "title": "Chicken Caesar Lunch Wrap",
        "category": "Lunch",
        "tags": ["quick", "high protein", "easy", "weeknight"],
        "summary": "A crisp and creamy wrap with chicken, romaine, Parmesan, and Caesar dressing.",
        "ingredients": [
            "1 cup cooked chicken",
            "1 cup chopped romaine",
            "2 tablespoons Caesar dressing",
            "2 tablespoons Parmesan",
            "1 large tortilla",
            "Black pepper",
        ],
        "steps": [
            "Toss the chicken and romaine with Caesar dressing.",
            "Add Parmesan and black pepper.",
            "Wrap tightly in a tortilla and slice in half.",
        ],
    },
    {
        "title": "Roasted Veggie Quinoa Bowl",
        "category": "Lunch",
        "tags": ["healthy", "vegetarian", "meal prep", "fresh"],
        "summary": "A colorful grain bowl with quinoa, roasted vegetables, and tahini dressing.",
        "ingredients": [
            "1 cup cooked quinoa",
            "1 cup roasted vegetables",
            "2 tablespoons tahini",
            "1 tablespoon lemon juice",
            "1 teaspoon olive oil",
            "Salt and pepper",
        ],
        "steps": [
            "Layer quinoa and roasted vegetables in a bowl.",
            "Whisk tahini, lemon juice, olive oil, salt, and pepper.",
            "Drizzle the dressing over the bowl and serve.",
        ],
    },
    {
        "title": "Tomato Basil Soup with Grilled Cheese",
        "category": "Lunch",
        "tags": ["comfort food", "easy", "weeknight", "kid friendly"],
        "summary": "A cozy soup-and-sandwich lunch with a smooth tomato base and crispy cheese toasties.",
        "ingredients": [
            "2 cups tomato soup",
            "1 handful basil leaves",
            "2 slices bread",
            "2 slices cheddar cheese",
            "1 tablespoon butter",
            "Salt and pepper",
        ],
        "steps": [
            "Warm the tomato soup and stir in chopped basil.",
            "Assemble and grill the cheese sandwich in butter.",
            "Serve the soup with the sandwich on the side.",
        ],
    },
    {
        "title": "Turkey Pesto Panini",
        "category": "Lunch",
        "tags": ["quick", "high protein", "one pan", "weeknight"],
        "summary": "A pressed sandwich with turkey, pesto, mozzarella, and tomatoes.",
        "ingredients": [
            "2 slices ciabatta",
            "3 slices turkey",
            "1 tablespoon pesto",
            "2 slices mozzarella",
            "2 slices tomato",
            "Butter for the bread",
        ],
        "steps": [
            "Spread pesto on the bread and layer turkey, mozzarella, and tomato.",
            "Butter the outside of the sandwich.",
            "Press until crisp and the cheese is melted.",
        ],
    },
    {
        "title": "One Pan Lemon Herb Salmon",
        "category": "Dinner",
        "tags": ["one pan", "healthy", "high protein", "fresh"],
        "summary": "A bright salmon dinner with lemon, herbs, and tender vegetables.",
        "ingredients": [
            "2 salmon fillets",
            "1 lemon",
            "1 teaspoon dried herbs",
            "1 cup asparagus",
            "1 tablespoon olive oil",
            "Salt and pepper",
        ],
        "steps": [
            "Season salmon and vegetables with olive oil, herbs, salt, and pepper.",
            "Roast on a sheet pan until the salmon flakes easily.",
            "Finish with lemon juice and serve hot.",
        ],
    },
    {
        "title": "Creamy Mushroom Pasta",
        "category": "Dinner",
        "tags": ["comfort food", "easy", "vegetarian", "weeknight"],
        "summary": "Silky pasta with sauteed mushrooms, garlic, and a light cream sauce.",
        "ingredients": [
            "8 ounces pasta",
            "1 cup mushrooms",
            "2 cloves garlic",
            "1/2 cup cream",
            "2 tablespoons Parmesan",
            "Parsley for garnish",
        ],
        "steps": [
            "Cook pasta until al dente and reserve some cooking water.",
            "Saute mushrooms and garlic until fragrant.",
            "Stir in cream, Parmesan, and pasta until coated.",
        ],
    },
    {
        "title": "Sheet Pan Chicken Fajitas",
        "category": "Dinner",
        "tags": ["one pan", "quick", "kid friendly", "weeknight"],
        "summary": "Colorful chicken fajitas roasted on a single tray for an easy dinner.",
        "ingredients": [
            "2 chicken breasts",
            "1 bell pepper",
            "1 onion",
            "1 tablespoon fajita seasoning",
            "4 tortillas",
            "Lime wedges",
        ],
        "steps": [
            "Slice the chicken and vegetables, then toss with seasoning.",
            "Roast on a sheet pan until cooked through.",
            "Serve in tortillas with lime wedges.",
        ],
    },
    {
        "title": "Vegetable Coconut Curry",
        "category": "Dinner",
        "tags": ["vegetarian", "vegan", "comfort food", "healthy"],
        "summary": "A fragrant curry with coconut milk, chickpeas, and seasonal vegetables.",
        "ingredients": [
            "1 cup mixed vegetables",
            "1 cup chickpeas",
            "1 can coconut milk",
            "1 tablespoon curry paste",
            "1 cup rice",
            "Cilantro for garnish",
        ],
        "steps": [
            "Simmer curry paste with coconut milk until smooth.",
            "Add vegetables and chickpeas and cook until tender.",
            "Serve over rice and garnish with cilantro.",
        ],
    },
    {
        "title": "Garlic Butter Steak Bites",
        "category": "Dinner",
        "tags": ["high protein", "quick", "comfort food", "one pan"],
        "summary": "Seared steak bites finished in garlic butter for a rich and simple dinner.",
        "ingredients": [
            "1 pound steak",
            "2 tablespoons butter",
            "2 cloves garlic",
            "1 teaspoon rosemary",
            "Salt and pepper",
            "Mashed potatoes for serving",
        ],
        "steps": [
            "Pat steak dry, season generously, and sear in a hot pan.",
            "Add butter, garlic, and rosemary to coat the steak bites.",
            "Serve immediately over mashed potatoes.",
        ],
    },
    {
        "title": "Lentil and Sweet Potato Stew",
        "category": "Dinner",
        "tags": ["vegan", "healthy", "meal prep", "comfort food"],
        "summary": "A hearty stew with lentils, sweet potato, and warm spices.",
        "ingredients": [
            "1 cup lentils",
            "1 sweet potato",
            "1 onion",
            "2 cups vegetable broth",
            "1 teaspoon cumin",
            "1 teaspoon smoked paprika",
        ],
        "steps": [
            "Saute onion with spices until fragrant.",
            "Add lentils, sweet potato, and broth, then simmer until tender.",
            "Season to taste and serve warm.",
        ],
    },
    {
        "title": "Chocolate Chip Banana Muffins",
        "category": "Dessert",
        "tags": ["easy", "kid friendly", "budget friendly", "fresh"],
        "summary": "Soft muffins with ripe banana and pockets of melted chocolate.",
        "ingredients": [
            "2 ripe bananas",
            "1 1/2 cups flour",
            "1/2 cup sugar",
            "1 teaspoon baking powder",
            "1 egg",
            "1/2 cup chocolate chips",
        ],
        "steps": [
            "Mash the bananas and mix with the wet ingredients.",
            "Fold in the dry ingredients and chocolate chips.",
            "Bake until the tops spring back when touched.",
        ],
    },
    {
        "title": "No Bake Cheesecake Cups",
        "category": "Dessert",
        "tags": ["easy", "make ahead", "fresh", "weekend"],
        "summary": "Individual cheesecake cups layered with crumb crust and berries.",
        "ingredients": [
            "1 cup crushed cookies",
            "2 tablespoons melted butter",
            "8 ounces cream cheese",
            "1/4 cup sugar",
            "1 cup whipped topping",
            "Mixed berries",
        ],
        "steps": [
            "Mix cookie crumbs with butter and press into cups.",
            "Beat cream cheese with sugar and fold in whipped topping.",
            "Layer into cups and top with berries before chilling.",
        ],
    },
    {
        "title": "Lemon Olive Oil Cake",
        "category": "Dessert",
        "tags": ["seasonal", "fresh", "weekend", "easy"],
        "summary": "A tender citrus cake with a light crumb and glossy lemon glaze.",
        "ingredients": [
            "2 cups flour",
            "1 cup sugar",
            "3 eggs",
            "1/2 cup olive oil",
            "1 lemon, zested and juiced",
            "Powdered sugar for glaze",
        ],
        "steps": [
            "Whisk the wet ingredients together, then fold in the dry ingredients.",
            "Bake until a tester comes out clean.",
            "Finish with a simple lemon glaze after cooling.",
        ],
    },
    {
        "title": "Brown Butter Rice Krispie Treats",
        "category": "Dessert",
        "tags": ["kid friendly", "budget friendly", "easy", "weekend"],
        "summary": "A nostalgic treat upgraded with nutty brown butter and extra vanilla.",
        "ingredients": [
            "4 tablespoons butter",
            "1 bag marshmallows",
            "6 cups crispy rice cereal",
            "1 teaspoon vanilla",
            "Pinch of salt",
            "Sprinkles optional",
        ],
        "steps": [
            "Brown the butter in a large pot.",
            "Stir in marshmallows until melted, then add vanilla and salt.",
            "Fold in cereal, press into a pan, and cool before slicing.",
        ],
    },
    {
        "title": "Mango Lime Smoothie",
        "category": "Drinks",
        "tags": ["fresh", "healthy", "quick", "vegetarian"],
        "summary": "A bright smoothie with mango, lime, and yogurt for a refreshing snack.",
        "ingredients": [
            "1 cup frozen mango",
            "1/2 banana",
            "1/2 cup yogurt",
            "1/2 cup orange juice",
            "1 teaspoon lime juice",
            "Ice as needed",
        ],
        "steps": [
            "Add all ingredients to a blender.",
            "Blend until smooth and pour into a chilled glass.",
            "Serve immediately.",
        ],
    },
    {
        "title": "Iced Vanilla Cold Brew",
        "category": "Drinks",
        "tags": ["quick", "budget friendly", "easy", "weeknight"],
        "summary": "A simple coffee drink with cold brew, vanilla, and milk over ice.",
        "ingredients": [
            "1 cup cold brew coffee",
            "1/4 cup milk",
            "1 teaspoon vanilla syrup",
            "Ice",
            "Optional cinnamon",
            "Optional sweetener",
        ],
        "steps": [
            "Fill a glass with ice.",
            "Pour in cold brew, milk, and vanilla syrup.",
            "Stir and adjust sweetness to taste.",
        ],
    },
    {
        "title": "Sparkling Citrus Mocktail",
        "category": "Drinks",
        "tags": ["fresh", "seasonal", "easy", "make ahead"],
        "summary": "A non-alcoholic citrus drink with sparkling water and fresh herbs.",
        "ingredients": [
            "1/2 orange",
            "1/2 lemon",
            "1 teaspoon honey",
            "1 cup sparkling water",
            "Mint leaves",
            "Ice",
        ],
        "steps": [
            "Juice the citrus and stir with honey.",
            "Pour over ice and top with sparkling water.",
            "Garnish with mint and serve cold.",
        ],
    },
    {
        "title": "Roasted Chickpea Snack Mix",
        "category": "Snacks",
        "tags": ["healthy", "vegan", "meal prep", "budget friendly"],
        "summary": "A crunchy snack mix with roasted chickpeas, seeds, and spices.",
        "ingredients": [
            "1 cup chickpeas",
            "1 tablespoon olive oil",
            "1 teaspoon paprika",
            "1/2 cup nuts or seeds",
            "Salt to taste",
            "Optional chili powder",
        ],
        "steps": [
            "Toss chickpeas with oil and spices.",
            "Roast until crisp, then cool completely.",
            "Mix with nuts or seeds and store in an airtight container.",
        ],
    },
    {
        "title": "Peanut Butter Energy Bites",
        "category": "Snacks",
        "tags": ["make ahead", "quick", "kid friendly", "easy"],
        "summary": "No-bake bites made with oats, peanut butter, and honey.",
        "ingredients": [
            "1 cup oats",
            "1/2 cup peanut butter",
            "1/4 cup honey",
            "2 tablespoons mini chocolate chips",
            "1 tablespoon chia seeds",
            "Pinch of salt",
        ],
        "steps": [
            "Stir all ingredients together in a bowl.",
            "Roll into small balls and chill until firm.",
            "Store in the fridge for grab-and-go snacks.",
        ],
    },
    {
        "title": "Herb Hummus Veggie Plate",
        "category": "Snacks",
        "tags": ["healthy", "vegetarian", "fresh", "quick"],
        "summary": "A snack plate with hummus, crunchy vegetables, and warm pita.",
        "ingredients": [
            "1 cup hummus",
            "Carrot sticks",
            "Cucumber slices",
            "Bell pepper strips",
            "Warm pita",
            "Fresh herbs",
        ],
        "steps": [
            "Spread hummus on a plate or shallow bowl.",
            "Arrange vegetables and pita around the hummus.",
            "Finish with chopped herbs and a drizzle of olive oil.",
        ],
    },
]


class Command(BaseCommand):
    help = "Generate recipe-themed test data and remove the older sample content"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=6, help="Number of recipe authors to create")
        parser.add_argument("--categories", type=int, default=8, help="Number of recipe categories to create")
        parser.add_argument("--posts", type=int, default=24, help="Total number of recipe posts to create")
        parser.add_argument("--comments", type=int, default=72, help="Total number of comments to create")
        parser.add_argument(
            "--featured_ratio",
            type=float,
            default=0.12,
            help="Fraction of posts to mark as featured (0-1)",
        )
        parser.add_argument(
            "--no-reset",
            action="store_false",
            dest="reset",
            help="Keep the existing content instead of removing old test data first",
        )
        parser.set_defaults(reset=True)

    def _reset_demo_data(self):
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Category.objects.all().delete()
        TaggedItem.objects.all().delete()
        Tag.objects.all().delete()

        User = get_user_model()
        User.objects.filter(email__regex=r"^(user|chef)\d+@example\.com$").delete()

    def handle(self, *args, **options):
        User = get_user_model()
        num_users = options["users"]
        num_categories = options["categories"]
        num_posts = options["posts"]
        num_comments = options["comments"]
        featured_ratio = max(0.0, min(1.0, options["featured_ratio"]))

        if options["reset"]:
            self.stdout.write("Removing previous sample content...")
            self._reset_demo_data()

        self.stdout.write("Generating recipe test data...")

        users = []
        for index, (first_name, last_name) in enumerate(RECIPE_USERS[:num_users], start=1):
            email = f"chef{index}@example.com"
            user = User.objects.create_user(
                email=email,
                password="password",
                first_name=first_name,
                last_name=last_name,
            )
            users.append(user)

        if not users:
            self.stderr.write("No users available, aborting")
            return

        categories = []
        for name in RECIPE_CATEGORIES[:num_categories]:
            categories.append(Category.objects.create(name=name))

        posts = []
        recipe_cycle = [RECIPE_POSTS[i % len(RECIPE_POSTS)] for i in range(num_posts)]

        for index, recipe in enumerate(recipe_cycle, start=1):
            author = random.choice(users)
            category = next((item for item in categories if item.name == recipe["category"]), random.choice(categories))
            title = recipe["title"]
            if index > len(RECIPE_POSTS):
                title = f"{title} Batch {index}"

            publish = timezone.now() - timedelta(days=random.randint(0, 220))
            is_published = random.random() < 0.8

            post = Post.objects.create(
                title=title,
                slug=f"{slugify(title)}-{index}",
                body=self._build_recipe_body(recipe),
                created_at=publish - timedelta(hours=random.randint(1, 72)),
                publish=publish if is_published else None,
                category=category,
                status="PB" if is_published else "DF",
                author=author,
                is_featured=(random.random() < featured_ratio),
            )
            post.tags.add(*recipe["tags"])
            post.tags.add(*random.sample(RECIPE_TAGS, k=random.randint(1, 3)))
            posts.append(post)

        comment_total = max(num_comments, len(posts))
        for index in range(1, comment_total + 1):
            post = random.choice(posts)
            Comment.objects.create(
                post=post,
                name=f"Reader {index}",
                email=f"reader{index}@example.com",
                body=random.choice(RECIPE_COMMENTS),
            )

        self.stdout.write(self.style.SUCCESS("Recipe test data generation complete"))
        self.stdout.write(
            f"Users: {len(users)}, Categories: {len(categories)}, Posts: {len(posts)}, Comments: {comment_total}"
        )

    def _build_recipe_body(self, recipe):
        ingredients = "\n".join(f"- {item}" for item in recipe["ingredients"])
        steps = "\n".join(f"{step_number}. {step}" for step_number, step in enumerate(recipe["steps"], start=1))
        return (
            f"# {recipe['title']}\n\n"
            f"{recipe['summary']}\n\n"
            "## Ingredients\n"
            f"{ingredients}\n\n"
            "## Method\n"
            f"{steps}\n\n"
            "## Notes\n"
            "Serve immediately while warm or keep chilled for meal prep."
        )
