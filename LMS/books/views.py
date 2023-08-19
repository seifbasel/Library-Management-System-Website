from django.shortcuts import get_object_or_404, render,redirect
from books.models import Book
# Create your views here.
def index(request):
    books = Book.get_all_books()
    return render( request, "books/index.html", context={'books': books} )


def show(request, id):
    book = Book.get_book(id=id)
    return render( request, "books/show.html", context={'book': book})




# def book_creat_view(request):
#     book = Book.get_all_books()
#     if request.method == "POST":
#         title = request.POST['title']
#         author = request.POST['author']
#         price = request.POST['price']
#         description = request.POST['description']
#         image= request.POST['image']
    
#         book=Book()
#         book.title=title
#         book.author = author
#         book.price = price
#         book.description = description
#         book.image=image
#         book.save()
        

#         return redirect('books.index')
#     return render(request,'books/creat.html',context={'book':book})

# def delete(request, id):
#     book = get_object_or_404(Book, id=id)  # object from student model
#     book.delete()  # delete object from the database
#     return redirect('books.index')
