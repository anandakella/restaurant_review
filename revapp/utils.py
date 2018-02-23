import os
import re
from flask import jsonify

def to_string(data):
    if not isinstance(data, (list, tuple, dict)):
        return str(data) if isinstance(data, unicode) else data

def sanitize_number(phone):
    # sanitize the phone number
    if re.search(r'\W+' , phone):
        phone = re.sub(r'\W+','', phone).strip()
    return phone

def json_response(message, status_code=200):
    	response = jsonify(message)
	response.status_code = status_code
	return response

