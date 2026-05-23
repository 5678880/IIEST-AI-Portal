from datetime import datetime
import uuid

# -----------------------------------
# CURRENT TIMESTAMP
# -----------------------------------

def get_current_timestamp():

    return datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"
    )

# -----------------------------------
# GENERATE UNIQUE ID
# -----------------------------------

def generate_unique_id():

    return str(uuid.uuid4())

# -----------------------------------
# STANDARD API RESPONSE
# -----------------------------------

def create_response(

    success=True,

    message="Success",

    data=None
):

    return {

        "success": success,

        "message": message,

        "timestamp": get_current_timestamp(),

        "data": data
    }

# -----------------------------------
# FORMAT PERCENTAGE
# -----------------------------------

def format_percentage(score, total):

    if total == 0:

        return 0

    percentage = (score / total) * 100

    return round(percentage, 2)

# -----------------------------------
# CLEAN TEXT
# -----------------------------------

def clean_text(text):

    return text.strip().lower()