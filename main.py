from flask import Flask, request, jsonify
from scraper import MorphicScraper
import re
from threading import Thread

app = Flask(__name__)
scraper = MorphicScraper()

def format_text(text):
    # Split the text into paragraphs
    paragraphs = text.split('\n\n')

    formatted_paragraphs = []
    for paragraph in paragraphs:
        # Remove extra spaces
        paragraph = re.sub(r'\s+', ' ', paragraph).strip()

        # Format headings
        if ':' in paragraph and len(paragraph.split(':')[0]) < 50:
            parts = paragraph.split(':', 1)
            paragraph = f"<h3>{parts[0].strip()}</h3><p>{parts[1].strip()}</p>"
        else:
            paragraph = f"{paragraph}"

        formatted_paragraphs.append(paragraph)

    # Join paragraphs
    formatted_text = '\n'.join(formatted_paragraphs)

    # Format lists
    formatted_text = re.sub(r'(?m)^(\s*)-\s', r'<li>', formatted_text)
    formatted_text = re.sub(r'(?s)(<li>.*?)((?=<li>)|$)', r'<ul>\1</li></ul>',
                            formatted_text)

    # Format bold text
    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>',
                            formatted_text)

    return formatted_text

@app.route('/search', methods=['POST'])
def search():
    user_input = request.json.get('query')
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    result = scraper.get_response(user_input)

    # Format the response text
    if 'response' in result:
        result['response'] = format_text(result['response'])

    return jsonify(result), 200

@app.route('/')
def home():
    return "Hello, I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == '__main__':
    keep_alive()