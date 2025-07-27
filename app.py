from flask import Flask, request, jsonify, Response
from generate_insights import generate_insights_for_persona
from collections import OrderedDict
import json

app = Flask(__name__)

@app.route('/generate-insights', methods=['POST'])
def generate_insights():
    pdf_files = request.files.getlist('pdfs')
    persona = request.form.get('persona')
    job = request.form.get('job')
    result = generate_insights_for_persona(pdf_files, persona, job)

    ordered = OrderedDict([
        ("metadata", result["metadata"]),
        ("extracted_sections", result["extracted_sections"]),
        ("subsection_analysis", result["subsection_analysis"])
    ])

    return Response(json.dumps(ordered, indent=4), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)