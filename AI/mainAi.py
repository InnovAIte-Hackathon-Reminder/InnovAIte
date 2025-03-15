from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from typing import List, Dict

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable isn't set. Pls set it in .env.") # check if API isEmpty boolean

genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)

class Event:
    def __init__(self, title: str, start: str, end: str, description: str, duration: str):
        self.title = title
        self.start = start
        self.end = end
        self.description = description
        self.duration = duration

    def to_dict(self):
        return {
            "title": self.title,
            "start": self.start,
            "end": self.end,
            "description": self.description,
            "duration": self.duration
        }

class Events:
    def __init__(self, events: List[Dict] = []):
        self.events = [Event(**event) for event in events]

    def add_event(self, title: str, start: str, end: str, description: str, duration: str):
        self.events.append(Event(title, start, end, description, duration))

    def get_events(self) -> List[Dict]:
        return [event.to_dict() for event in self.events]

@app.route('/arrange_calendar', methods=['POST'])
def arrange_calendar():
    try:
        data = request.get_json()
        calendar_data = data.get('calendar_data', []) #get the calendar data, set to empty list if none
        new_tasks = data.get('new_tasks', []) # get the new tasks, set to empty list if none
        user_preferences = data.get('user_preferences')

        if not user_preferences:
            return jsonify({"error": "Missing user_preferences"}), 400

        # Add new tasks to the calendar data
        for task in new_tasks:
            calendar_data.append(task)

        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Arrange the following calendar tasks according to the user's preferences.

        Calendar Data:
        {calendar_data}

        User Preferences:
        {user_preferences}

        All tasks in calendar array each have these keys: title, start, end, description, and duration.

        Output the rearranged calendar data in JSON array format, where each event has these keys: title, start, end, description, and duration.
        """

        response = model.generate_content(prompt)
        arranged_calendar_text = response.text

        try:
            arranged_calendar = json.loads(arranged_calendar_text)
        except json.JSONDecodeError:
            return jsonify({"error": "Gemini response was not valid JSON"}), 500

        if not isinstance(arranged_calendar, list):
            return jsonify({"error": "Gemini did not return a list of events"}), 500

        return jsonify({"arranged_calendar": arranged_calendar})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)