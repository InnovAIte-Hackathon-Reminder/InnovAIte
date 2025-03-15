from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it in .env.")

genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/arrange_calendar', methods=['POST'])
def arrange_calendar():
    try:
        data = request.get_json()
        fixed_deadlines = data.get('fixed_deadlines', [])
        ai_assigned_tasks = data.get('ai_assigned_tasks', [])
        user_preferences = data.get('user_preferences')

        if not fixed_deadlines or not user_preferences:
            return jsonify({"error": "Missing required data"}), 400

        model = genai.GenerativeModel('gemini-pro')

        # Generate work events for deadlines (using user-provided duration)
        for deadline in fixed_deadlines:
            ai_assigned_tasks.append({
                "title": f"Work on {deadline['title']}",
                "duration": deadline['duration'],  # User-provided duration
                "deadline": deadline['deadline']
            })

        prompt_arrange = f"""
        Arrange the following tasks according to the user's preferences, respecting the fixed deadlines AND THE PROVIDED DURATION of the task.
        Based on the description, deadline, and provided time, what is the priority level (High, Medium, Low)? Just answer with one of the options "High", "Medium", or "Low".
        Based off what you think the priority level is, arrange the calendar accordingly.
        Tasks:
        {ai_assigned_tasks}

        User Preferences:
        {user_preferences}

        Output the rearranged tasks in a JSON array format, where each task has the following keys: title, start, end, description, and duration.
        """

        response = model.generate_content(prompt_arrange)
        arranged_tasks_text = response.text

        try:
            arranged_tasks = json.loads(arranged_tasks_text)
        except json.JSONDecodeError:
            return jsonify({"error": "Gemini response was not valid JSON"}), 500

        if not isinstance(arranged_tasks, list):
            return jsonify({"error": "Gemini did not return a list of tasks"}), 500

        return jsonify({"arranged_tasks": arranged_tasks})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)