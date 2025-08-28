# Import necessary libraries from Flask and requests
from flask import Flask, request, jsonify, render_template
import requests
import json

# Initialize the Flask application
app = Flask(__name__)

# Route for the home page, which serves the index.html file
@app.route('/')
def home():
    # render_template looks for files in a 'templates' folder, so we need to
    # tell it to look in the current directory.
    return render_template('index.html')

# Route to handle the chat requests
@app.route('/chat', methods=['POST'])
def chat():
    # Get the user's message from the incoming JSON data
    data = request.get_json()
    user_message = data.get('message', '')

    # Check if the message is empty
    if not user_message:
        return jsonify({'success': False, 'error': 'الرسالة فارغة.'}), 400

    try:
        # --- الخطوة 1: الحصول على مفتاح API من الخدمة المحددة ---
        api_key_service_url = "https://openai-key.api-droid.workers.dev/"
        key_response = requests.get(api_key_service_url)
        key_response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        key_data = key_response.json()
        key = key_data.get('key')

        if not key:
            raise ValueError('فشل في الحصول على مفتاح API من الخدمة.')

        # --- الخطوة 2: الاتصال بـ OpenAI API باستخدام المفتاح ---
        openai_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        # Define the message payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "أنت مساعد ذكاء اصطناعي مفيد. ردودك يجب أن تكون باللغة العربية."},
                {"role": "user", "content": user_message}
            ]
        }

        # Make the request to OpenAI
        openai_response = requests.post(openai_url, headers=headers, json=payload)
        openai_response.raise_for_status() # Raise an exception for bad status codes

        # Get the AI's response from the JSON data
        response_data = openai_response.json()
        ai_message = response_data.get("choices", [{}])[0].get("message", {}).get("content")

        if not ai_message:
            raise ValueError('الرد من OpenAI فارغ أو غير متوقع.')

        # Return the AI's message to the frontend as a JSON response
        return jsonify({'success': True, 'message': ai_message})

    except requests.exceptions.RequestException as e:
        # Catch network-related errors and bad status codes
        print(f"Error making API call: {e}")
        return jsonify({'success': False, 'error': f'خطأ في الاتصال: {str(e)}'}), 500
    except (ValueError, json.JSONDecodeError) as e:
        # Catch JSON parsing or key-related errors
        print(f"Error processing response: {e}")
        return jsonify({'success': False, 'error': f'خطأ في معالجة البيانات: {str(e)}'}), 500
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.'}), 500

# Run the Flask app
# The app will run on http://127.0.0.1:5000/
if __name__ == '__main__':
    app.run(debug=True, port=5000)
