from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from datetime import datetime
import os
import json
import random


# TODO: Use the @dag decorator to create a DAG that:
# * Runs every minute
# * Does not use catchup
@dag(
    "data_validation_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval="* * * * *",
    catchup=False,
    description=""
)
def data_quality_pipeline():

    CORRECT_PROB = 0.7

    def get_bookings_path(context):
        execution_date = context["execution_date"]
        file_date = execution_date.strftime("%Y-%m-%d_%H-%M")
        return f"/tmp/data/bookings/{file_date}/bookings.json"

    def get_exeptions_path(context):
        execution_date = context["execution_date"]
        file_date = execution_date.strftime("%Y-%m-%d_%H-%M")
        return f"/tmp/data/errors/{file_date}/errors_log.json"

    def generate_booking_id(i):
        if random.random() < CORRECT_PROB:
            return i + 1

        return ""

    def generate_listing_id():
        if random.random() < CORRECT_PROB:
            return random.choice([1, 2, 3, 4, 5])

        return ""

    def generate_user_id(correct_prob=0.7):
        return random.randint(1000, 5000) if random.random() < correct_prob else ""

    def generate_booking_time(execution_date):
        if random.random() < CORRECT_PROB:
            return execution_date.strftime('%Y-%m-%d %H:%M:%S')

        return ""

    def generate_status():
        if random.random() < CORRECT_PROB:
            return random.choice(["confirmed", "pending", "cancelled"])

        return random.choice(["unknown", "", "error"])

    @task
    def generate_bookings():
        context = get_current_context()
        booking_path = get_bookings_path(context)

        num_bookings = random.randint(5, 15)
        bookings = []

        for i in range(num_bookings):
            booking = {
                "booking_id": generate_booking_id(i),
                "listing_id": generate_listing_id(),
                "user_id": generate_user_id(),
                "booking_time": generate_booking_time(context["execution_date"]),
                "status": generate_status()
            }
            bookings.append(booking)

        directory = os.path.dirname(booking_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(booking_path, "w") as f:
            json.dump(bookings, f, indent=4)

        print(f"Written to file: {booking_path}")

    # TODO: Create a data quality check task that reads bookings data and validates every record.
    # For every invalid record it should return a validation record that includes:
    # * A record position in an input file
    # * A list of identified violations
    #
    # Here is a list of validations it should perform:
    # * Check if each of the fields is missing
    # * Check if the "status" field has one of the valid values
    #
    # It should write all found anomalies into an input file.

    @task
    def validate_bookings():
        context = get_current_context()
        booking_path = get_bookings_path(context)
        exeptions_path = get_exeptions_path(context)

        required_fields = {"booking_id", "listing_id", "user_id", "booking_time", "status"}
        status_values = {"status": {"confirmed", "pending", "cancelled"}}

        directory = os.path.dirname(exeptions_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(booking_path, "r") as f:
            read_bookings = json.load(f)
        
        errors = []
        for i, bk in enumerate(read_bookings):
            invalid_fields = []
            for field in required_fields:
                if field not in bk or bk[field] in (None, "", []):
                    invalid_fields.append((field, bk.get(field)))
            if invalid_fields:
                errors.append(f"Entry {i} has invalid fields: {invalid_fields}")
            
            #special check for status
            for field, valid in status_values.items(): 
                if field in bk and bk[field] not in valid:
                    errors.append(f"Entry {i} has nvalid value for '{field}': {bk[field]}")
        
        print(f"Validated bookings data {booking_path}. Errors detected: \n{len(errors)}")
        if (len(errors) > 0):
            with open(exeptions_path, "w") as f:
                json.dump(errors, f, indent=4)
            print(f"Errors log is available at {exeptions_path}")
        

    # TODO: Define dependencies between tasks
    generate_bookings() >> validate_bookings()

# TODO: Create an instance of the DAG
dag_exercise_1 = data_quality_pipeline()