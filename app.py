from flask import Flask, request, render_template, redirect, url_for
from DBMC import film_db_manager, user_db_manager
from datetime import datetime
import webbrowser
from threading import Timer

# Create the Flask app and specify the templates folder
app = Flask(__name__, template_folder='db_film_templates')

# Function to log user search queries (only if results are found)
def log_user_query(keyword, genre, year, results_found):
    if not results_found:
        return
    try:
        query = """
        INSERT INTO search_queries (keyword, genre, year, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        params = (keyword, genre, year, datetime.now())
        user_db_manager.execute_query(query, params)
    except Exception as e:
        print(f"Error logging user query: {e}")

# Route: Home/Search page
@app.route('/', methods=['GET', 'POST'])
def search():
    combined_results = []
    keyword = request.form.get('keyword', '').lower() if request.method == 'POST' else ''
    genre_input = request.form.get('genre', '').lower() if request.method == 'POST' else ''
    year_input = request.form.get('year', '') if request.method == 'POST' else ''

    # If no filters are provided
    if request.method == 'POST' and not keyword and not genre_input and not year_input:
        return render_template('search.html', combined_results=[], keyword=keyword, genre_input=genre_input, year_input=year_input)

    # Search query execution
    if request.method == 'POST':
        try:
            base_query = """
            SELECT f.title, f.description, f.release_year, c.name AS category_name
            FROM film f
            LEFT JOIN film_category fc ON f.film_id = fc.film_id
            LEFT JOIN category c ON fc.category_id = c.category_id
            WHERE 1=1
            """
            params = []
            if keyword:
                base_query += " AND LOWER(f.title) LIKE %s"
                params.append(f"%{keyword}%")
            if genre_input:
                base_query += " AND LOWER(c.name) = %s"
                params.append(genre_input)
            if year_input.isdigit():
                base_query += " AND f.release_year = %s"
                params.append(int(year_input))

            combined_results = film_db_manager.execute_query(base_query, params)

            # Log the query if results were found
            log_user_query(keyword, genre_input, year_input, bool(combined_results))
        except Exception as e:
            print(f"Error executing search query: {e}")

    return render_template('search.html', combined_results=combined_results, keyword=keyword, genre_input=genre_input, year_input=year_input)

# Route: Top 10 user search queries
@app.route('/top-queries')
def top_queries():
    query = """
    SELECT keyword, genre, year, COUNT(*) as count
    FROM search_queries
    GROUP BY keyword, genre, year
    ORDER BY count DESC
    LIMIT 10
    """
    try:
        results = user_db_manager.execute_query(query)
    except Exception as e:
        return f"Error retrieving popular queries: {e}"

    if results is None:
        return "No results found or database connection error."

    return render_template('top_queries.html', results=results)

# Auto-open browser
def open_browser():
    try:
        webbrowser.open_new("http://127.0.0.1:5000")
    except Exception as e:
        print(f"Error opening browser: {e}")

# Application entry point
if __name__ == '__main__':
    try:
        Timer(1, open_browser).start()
        app.run(debug=False)
    except Exception as e:
        print(f"Application failed to start: {e}")
