#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from urllib.parse import unquote
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from flask import Flask, jsonify, request

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['POST'])
    def talkToGemini():
        prompt = request.json['message']
        prompt = unquote(prompt)

        if request.json.get('image') is None:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            response = llm.invoke(prompt)
        else:
            llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {"type": "image_url", "image_url": request.json['image']},
                ]
            )
            response = llm.invoke([message])

        data = {}
        data['content'] = response.content
        return data

    return app


if __name__ == "__main__":
    # Create an instance of flask server when called directly
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
