window.addEventListener('DOMContentLoaded', (event) => {
    const books = document.querySelectorAll('.book');

    books.forEach(book => {
      const button = book.querySelector('button');
      const bookInfo = book.querySelector('.book-info');

      book.insertBefore(button, bookInfo.nextSibling); // Move button after bookInfo
    });
  });