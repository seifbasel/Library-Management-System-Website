from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from books.services import borrow_book
from genre.models import Genre


class BookIndexViewTests(TestCase):
    def setUp(self):
        self.fiction = Genre.objects.create(name="Fiction")
        self.history = Genre.objects.create(name="History")
        self.available = Book.objects.create(
            title="Available Adventures", author="Ann Author", price="9.99", genre=self.fiction
        )
        self.borrowed = Book.objects.create(
            title="Rare History", author="Hank Historian", price="14.99", genre=self.history
        )
        borrower = User.objects.create_user("reader", password="pass12345")
        borrow_book(book=self.borrowed, borrower=borrower, period_days=7)

    def test_no_filters_shows_all_books(self):
        response = self.client.get(reverse("books:index"))
        self.assertEqual(set(response.context["books"]), {self.available, self.borrowed})

    def test_search_matches_title_or_author(self):
        response = self.client.get(reverse("books:index"), {"q": "historian"})
        self.assertEqual(list(response.context["books"]), [self.borrowed])

    def test_genre_filter(self):
        response = self.client.get(reverse("books:index"), {"genre": self.fiction.id})
        self.assertEqual(list(response.context["books"]), [self.available])

    def test_availability_filter_excludes_borrowed_books(self):
        response = self.client.get(reverse("books:index"), {"availability": "available"})
        self.assertEqual(list(response.context["books"]), [self.available])

    def test_pagination_splits_results_across_pages(self):
        for i in range(15):
            Book.objects.create(title=f"Extra {i}", author="Bulk Author", price="1.00")
        response = self.client.get(reverse("books:index"))
        self.assertEqual(response.context["page_obj"].paginator.num_pages, 2)


class ShowBorrowedViewTests(TestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("books:borrowed"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("students:login"), response.url)

    def test_logged_in_user_sees_only_their_own_active_loans(self):
        owner = User.objects.create_user("owner", password="pass12345")
        other = User.objects.create_user("other", password="pass12345")
        my_book = Book.objects.create(title="Mine", author="A", price="9.99")
        their_book = Book.objects.create(title="Theirs", author="B", price="9.99")
        borrow_book(book=my_book, borrower=owner, period_days=7)
        borrow_book(book=their_book, borrower=other, period_days=7)

        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("books:borrowed"))

        self.assertEqual(response.status_code, 200)
        loans = list(response.context["loans"])
        self.assertEqual([loan.book for loan in loans], [my_book])


class ReturnToShelfViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        self.book = Book.objects.create(title="Test Book", author="A", price="9.99")
        self.loan = borrow_book(book=self.book, borrower=self.owner, period_days=7)

    def test_anonymous_user_is_redirected_to_login_and_loan_stays_active(self):
        response = self.client.post(reverse("books:return", args=[self.book.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("students:login"), response.url)
        self.assertFalse(Book.objects.get(pk=self.book.pk).is_available is True)

    def test_non_owner_cannot_return_someone_elses_book(self):
        self.client.login(username="other", password="pass12345")
        response = self.client.post(reverse("books:return", args=[self.book.id]))
        self.assertEqual(response.status_code, 404)
        self.loan.refresh_from_db()
        self.assertTrue(self.loan.is_active)

    def test_get_request_is_rejected(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("books:return", args=[self.book.id]))
        self.assertEqual(response.status_code, 405)

    def test_owner_can_return_their_own_book(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(reverse("books:return", args=[self.book.id]))
        self.assertRedirects(response, reverse("books:borrowed"))
        self.assertTrue(Book.objects.get(pk=self.book.pk).is_available)
