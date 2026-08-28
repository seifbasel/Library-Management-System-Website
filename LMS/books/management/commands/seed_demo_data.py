"""Seed the catalog with real books (using the cover images already
shipped in media/books/images/) plus a modest amount of realistic loan
history, so the catalog, dashboard-style stats, "most borrowed", and
overdue badges all have real data to show on a fresh clone.

Safe to re-run: everything is created with get_or_create.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from books.models import Book
from genre.models import Genre
from loans.models import Loan
from students.models import Student

BOOKS = [
    {
        "title": "Ball Four",
        "author": "Jim Bouton",
        "genre": "Nonfiction",
        "image": "BallFour.jpg",
        "pages": 464,
        "price": "16.99",
        "description": (
            "Jim Bouton's candid, funny diary of his 1969 season pitching for the "
            "Seattle Pilots and Houston Astros - one of the most influential sports "
            "books ever written."
        ),
    },
    {
        "title": "Birnam Wood",
        "author": "Eleanor Catton",
        "genre": "Fiction",
        "image": "Birnam_Wood.jpg",
        "pages": 432,
        "price": "28.00",
        "description": (
            "A guerrilla gardening collective clashes with a billionaire prepper in "
            "this tense, darkly funny thriller from the Booker Prize-winning author "
            "of The Luminaries."
        ),
    },
    {
        "title": "Pineapple Street",
        "author": "Jenny Jackson",
        "genre": "Fiction",
        "image": "Pineapple_street.jpg",
        "pages": 304,
        "price": "27.00",
        "description": (
            "A sharp, funny novel about three women marrying into - and born into - "
            "a wealthy Brooklyn Heights family, and what money does and doesn't buy."
        ),
    },
    {
        "title": "Shy",
        "author": "Max Porter",
        "genre": "Fiction",
        "image": "Shy.jpg",
        "pages": 128,
        "price": "22.00",
        "description": (
            "A slim, incantatory novel following one night in the mind of a "
            "troubled teenage boy who slips out of a home for young offenders."
        ),
    },
    {
        "title": "The Art of Simple Food II",
        "author": "Alice Waters",
        "genre": "Cooking",
        "image": "The_Art_of_Simple_Food_II.jpg",
        "pages": 352,
        "price": "35.00",
        "description": (
            "Alice Waters' follow-up collection of seasonal recipes and kitchen "
            "wisdom, built around cooking simply from the garden."
        ),
    },
    {
        "title": "The Whole Fish Cookbook",
        "author": "Josh Niland",
        "genre": "Cooking",
        "image": "The_Whole_Fish_Cookbook.jpg",
        "pages": 304,
        "price": "45.00",
        "description": (
            "Chef Josh Niland's James Beard Award-winning guide to using every "
            "part of a fish, from bones to offal, with new ways to cook and think "
            "about seafood."
        ),
    },
    {
        "title": "The World of Ice & Fire",
        "author": "George R. R. Martin, Elio M. García Jr. & Linda Antonsson",
        "genre": "Fantasy",
        "image": "The_world_of_ice__fire.jpg",
        "pages": 336,
        "price": "32.50",
        "description": (
            "The official illustrated history of Westeros and the world of A Song "
            "of Ice and Fire, from the Dawn Age to the events of the novels."
        ),
    },
    {
        "title": "Victory City",
        "author": "Salman Rushdie",
        "genre": "Fiction",
        "image": "Victory_city.jpg",
        "pages": 352,
        "price": "30.00",
        "description": (
            "A sweeping magical-realist epic narrated by a woman who lives for two "
            "hundred years and breathes a legendary city into being."
        ),
    },
    {
        "title": "The Flavor Equation",
        "author": "Nik Sharma",
        "genre": "Cooking",
        "image": "the_flavor_equation.jpg",
        "pages": 352,
        "price": "35.00",
        "description": (
            "Nik Sharma explores the science and emotion behind flavor, pairing "
            "each element - sight, sound, mouthfeel, aroma, taste - with recipes."
        ),
    },
    {
        "title": "The Book Artist",
        "author": "Mark Pryor",
        "genre": "Mystery",
        "image": "OIP.webp",
        "pages": 304,
        "price": "16.99",
        "description": (
            "Paris-based police detective Hugo Marston investigates the murder of "
            "an American art student in this entry in the Hugo Marston mystery series."
        ),
    },
]

# (book title, [days_ago each historical loan was borrowed for 14 days and returned])
RETURNED_LOAN_HISTORY = {
    "Victory City": [60, 35, 10],
    "Pineapple Street": [50, 20],
    "The World of Ice & Fire": [45, 15],
    "Birnam Wood": [25],
    "Ball Four": [18],
}

# (book title, borrower index, days_ago borrowed, period_days) - still active today
ACTIVE_LOANS = [
    ("Shy", 0, 3, 14),  # borrowed recently, not due yet
    ("The Whole Fish Cookbook", 1, 20, 14),  # borrowed 20 days ago for 14 days -> overdue
]

DEMO_READERS = [
    {"username": "demo_reader1", "email": "demo.reader1@example.com", "name": "Demo Reader One"},
    {"username": "demo_reader2", "email": "demo.reader2@example.com", "name": "Demo Reader Two"},
]


class Command(BaseCommand):
    help = "Seed the catalog with real books and a modest amount of demo loan history."

    def handle(self, *args, **options):
        readers = [self._get_or_create_reader(data) for data in DEMO_READERS]

        books_by_title = {}
        for entry in BOOKS:
            book = self._get_or_create_book(entry)
            books_by_title[entry["title"]] = book

        created_loans = 0
        today = timezone.localdate()

        for title, offsets in RETURNED_LOAN_HISTORY.items():
            book = books_by_title[title]
            for i, days_ago in enumerate(offsets):
                borrower = readers[i % len(readers)]
                borrowed_at = today - timedelta(days=days_ago)
                _, created = Loan.objects.get_or_create(
                    book=book,
                    borrower=borrower,
                    borrowed_at=borrowed_at,
                    defaults={
                        "due_at": borrowed_at + timedelta(days=14),
                        "returned_at": borrowed_at + timedelta(days=14),
                    },
                )
                created_loans += created

        for title, reader_index, days_ago, period_days in ACTIVE_LOANS:
            book = books_by_title[title]
            borrower = readers[reader_index]
            borrowed_at = today - timedelta(days=days_ago)
            if not Loan.objects.filter(book=book, returned_at__isnull=True).exists():
                Loan.objects.create(
                    book=book,
                    borrower=borrower,
                    borrowed_at=borrowed_at,
                    due_at=borrowed_at + timedelta(days=period_days),
                )
                created_loans += 1

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {len(books_by_title)} books and {created_loans} new loan record(s).")
        )

    def _get_or_create_reader(self, data):
        user, _ = User.objects.get_or_create(
            username=data["username"],
            defaults={"email": data["email"]},
        )
        Student.objects.get_or_create(
            user=user,
            defaults={"name": data["name"], "email": data["email"]},
        )
        return user

    def _get_or_create_book(self, entry):
        genre, _ = Genre.objects.get_or_create(name=entry["genre"])
        book, created = Book.objects.get_or_create(
            title=entry["title"],
            defaults={
                "author": entry["author"],
                "genre": genre,
                "pages": entry["pages"],
                "price": entry["price"],
                "description": entry["description"],
            },
        )
        if created or not book.image:
            book.image.name = f"books/images/{entry['image']}"
            book.save(update_fields=["image"])
        return book
