from flask import Flask, jsonify, request
from flasgger import Swagger

from services.book_service import BookService


def create_app(book_service: BookService) -> Flask:
    app = Flask(__name__)
    Swagger(app)

    @app.get("/books/<int:book_id>")
    def get_book_by_id(book_id: int):
        """
        Get book by ID.
        ---
        parameters:
          - in: path
            name: book_id
            type: integer
            required: true
            description: Book identifier.
        responses:
          200:
            description: Book found.
          404:
            description: Book not found.
        """
        book = book_service.get_book_by_id(book_id)
        if book is None:
            return jsonify({"message": "Book not found"}), 404
        return jsonify(book), 200

    @app.get("/books")
    def list_books():
        """
        List books with optional sorting.
        ---
        parameters:
          - in: query
            name: sort_by
            type: string
            required: false
            description: Sort field.
          - in: query
            name: order
            type: string
            enum: [asc, desc]
            required: false
            description: Sort order.
        responses:
          200:
            description: List of books.
          400:
            description: Validation error.
        """
        sort_by = request.args.get("sort_by")
        order = request.args.get("order")
        try:
            books = book_service.list_books(sort_by=sort_by, order=order)
        except ValueError as exc:
            return jsonify({"message": str(exc)}), 400
        return jsonify(books), 200

    @app.post("/books")
    def create_book():
        """
        Create a new book.
        ---
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [title, description, link, author, price, pages, rating]
        responses:
          201:
            description: Book created.
          400:
            description: Validation error.
        """
        payload = request.get_json(silent=True) or {}
        try:
            book = book_service.create_book(payload)
        except ValueError as exc:
            return jsonify({"message": str(exc)}), 400
        return jsonify(book), 201

    @app.put("/books/<int:book_id>")
    def update_book(book_id: int):
        """
        Update existing book.
        ---
        consumes:
          - application/json
        parameters:
          - in: path
            name: book_id
            type: integer
            required: true
            description: Book identifier.
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [title, description, link, author, price, pages, rating]
        responses:
          200:
            description: Book updated.
          400:
            description: Validation error.
          404:
            description: Book not found.
        """
        payload = request.get_json(silent=True) or {}
        try:
            book = book_service.update_book(book_id=book_id, payload=payload)
        except ValueError as exc:
            return jsonify({"message": str(exc)}), 400
        if book is None:
            return jsonify({"message": "Book not found"}), 404
        return jsonify(book), 200

    @app.delete("/books/<int:book_id>")
    def delete_book(book_id: int):
        """
        Delete a book.
        ---
        parameters:
          - in: path
            name: book_id
            type: integer
            required: true
            description: Book identifier.
        responses:
          200:
            description: Book deleted.
          404:
            description: Book not found.
        """
        deleted = book_service.delete_book(book_id=book_id)
        if not deleted:
            return jsonify({"message": "Book not found"}), 404
        return jsonify({"message": "Book deleted"}), 200

    @app.get("/books/stats")
    def get_books_stats():
        """
        Get aggregated stats for numeric book fields.
        ---
        responses:
          200:
            description: Aggregated stats.
        """
        stats = book_service.get_book_stats()
        return jsonify(stats), 200

    return app


def create_default_app() -> Flask:
    from providers import provide_book_repository

    return create_app(book_service=BookService(book_repository=provide_book_repository()))


if __name__ == "__main__":
    app = create_default_app()
    app.run(debug=True)
