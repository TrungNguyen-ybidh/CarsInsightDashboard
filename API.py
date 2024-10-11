import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
car_data = None

# Data Handling Functions
def load_data(filename):
    """Load the CSV data and return a DataFrame."""
    df = pd.read_csv(filename)
    return pd.DataFrame(df)

@app.route('/load_data', methods=['POST'])
def load_data_api():
    global car_data
    file_path = request.json.get('file_path')
    car_data = load_data(file_path)
    return jsonify({'message': 'Data loaded successfully!'})

# API Route to get catalog (filtered data)
@app.route('/get_catalog', methods=['GET'])
def get_catalog_api():
    global car_data
    brand = request.args.get('brand', 'All')
    year = int(request.args.get('year')) if request.args.get('year') else None
    price = float(request.args.get('price')) if request.args.get('price') else None

    # Apply filters to the dataset
    filtered_data = car_data[
        ((car_data['Brand'] == brand) if brand != 'All' else True) &
        (car_data['Year'] >= year if year else True) &
        (car_data['Price'] <= price if price else True)
    ]

    # Return the filtered catalog as JSON
    return filtered_data.to_json(orient='records'), 200

if __name__ == '__main__':
    car_data = load_data('car_price.csv')  # Load data at the start
    app.run(debug=True, port=5000)
