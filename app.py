from flask import Flask, render_template, request, redirect, url_for,session,abort,send_from_directory,flash
import mysql.connector
from flask_cors import CORS
import json
from datetime import datetime
from flask import jsonify
import logging
from logging.config import dictConfig
import os
import traceback  
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

#mariadb connection info from config.json file
with open('config.json', 'r') as f:
    config = json.load(f)


mysql_user = config["mysql_user"]
mysql_password = config["mysql_password"]
mysql_host = config["mysql_host"]
mysql_database = config["mysql_database"]

try:
    
    mysql = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host=mysql_host,
        database=mysql_database
    )
except mysql.connector.Error as err:
    print("MySQL Error: {}".format(err))

print(os.getcwd())

app = Flask(__name__)
CORS(app)
#logging save in app.log
logging.basicConfig(filename='app.log', level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
#logging in the console
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app.secret_key = 'your_secret_key'

@app.teardown_request
def teardown_request(exception):
    if hasattr(app, 'mysql') and app.mysql:
        app.mysql.close()
@app.route("/add", methods=['POST'])
def add():
    if request.method == 'POST':
        brandName = request.form['Brand_Name']
        modelName = request.form['Model_Name']
        productName = request.form['Product_Name']
        serialNumber = request.form['Serial_Number']
        ProductSoldDate = request.form['Product_Sold_Date']

        cur = mysql.cursor()

        brand_s = 'INSERT INTO Brand(Brand_Name) VALUES(%s);'
        cur.execute(brand_s, (brandName,))
        mysql.commit()

        model_s = 'INSERT INTO Model(Model_Name) VALUES(%s);'
        cur.execute(model_s, (modelName,))
        mysql.commit()

        product_s = 'INSERT INTO Product(Product_Name, Serial_Number, Product_Sold_Date) VALUES(%s, %s, %s);'
        cur.execute(product_s, (productName, serialNumber, ProductSoldDate))
        mysql.commit()

        cur.close()

    else:
        return render_template('add.html')

    return '{"Result":"Success"}'

@app.route("/", methods=['GET'])
def hello():
    serial_number = request.args.get('serial_number', '')

    cur = mysql.cursor()

    sql_query = '''
        SELECT Brand.Brand_Name, Model.Model_Name, Product.Product_Name, Product.Serial_Number, Product.Product_Sold_Date
        FROM Product
        JOIN Model ON Product.Model_ID = Model.Model_ID
        JOIN Brand ON Model.Brand_ID = Brand.Brand_ID
        WHERE Product.Serial_Number = %s;
    '''

    cur.execute(sql_query, (serial_number,))
    rv = cur.fetchall()

    Results = []
    for row in rv:
        Result = {}
        Result['Brand_Name'] = row[0].replace('\n', ' ')
        Result['Model_Name'] = row[1]
        Result['Product_Name'] = row[2]
        Result['Serial_Number'] = row[3]
        Result['Product_Sold_Date'] = row[4].isoformat() if row[4] else None
        Results.append(Result)

    response = {'Results': Results, 'count': len(Results)}
    ret = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

    return ret

@app.route("/create_rma", methods=['GET'])
def create_rma():
    serial_number = request.args.get('serial_number', '')
    issue_description = request.args.get('issue_description', '')

    if not serial_number:
        return '{"error": "Serial_Number cannot be empty."}', 400

    cur = mysql.cursor()

    product_query = 'SELECT Product_ID FROM Product WHERE Serial_Number = %s;'
    cur.execute(product_query, (serial_number,))
    product_data = cur.fetchone()

    if not product_data:
        return '{"error": "Product not found for the given Serial_Number."}', 404

    product_id = product_data[0]

    current_date = datetime.now().strftime('%Y-%m-%d')

    rma_query = 'INSERT INTO RMA (Inspaction_Start_Date, Check_Issue, Product_ID) VALUES (%s, %s, %s);'
    cur.execute(rma_query, (current_date, issue_description, product_id))
    mysql.commit()

    cur.execute('SELECT LAST_INSERT_ID();')
    rma_id = cur.fetchone()[0]

    cur.close()

    response = {'RMA_ID': rma_id}
    ret = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

    return ret

@app.route("/check_rma_status", methods=['GET'])
def check_rma_status():
    serial_number = request.args.get('serial_number', '')

    cur = mysql.cursor(dictionary=True)

    rma_status_query = '''
        SELECT RMA.RMA_ID, RMA.Inspaction_Start_Date, RMA.Inspeciton_Completion_Date, RMA.Product_Defect,
               RMA.Check_Issue, RMA.Result_Issue, RMA.Product_ID, Product.Serial_Number, Product.Product_Name
        FROM RMA
        LEFT JOIN Product ON RMA.Product_ID = Product.Product_ID
        WHERE Product.Serial_Number = %s;
    '''

    cur.execute(rma_status_query, (serial_number,))
    rma_status = cur.fetchall()

    cur.close()

    return jsonify(rma_status)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            return send_from_directory('/var/www/html/login', 'index.html')
        return f(*args, **kwargs)
    return decorated_function
@app.route('/technical', methods=['GET'])
@login_required
def technical_page():
    cur = mysql.cursor(dictionary=True)

    rma_status_query = '''
        SELECT RMA.RMA_ID, RMA.Inspaction_Start_Date, RMA.Inspeciton_Completion_Date, RMA.Product_Defect,
               RMA.Check_Issue, RMA.Result_Issue, RMA.Product_ID, Product.Serial_Number, Product.Product_Name,
               Technician.Technician_ID
        FROM RMA
        LEFT JOIN Product ON RMA.Product_ID = Product.Product_ID
        LEFT JOIN Technician ON RMA.Technician_ID = Technician.Technician_ID
    '''
    
    cur.execute(rma_status_query)
    rma_status = cur.fetchall()

    cur.close()

    return send_from_directory('/var/www/html/technical', 'index.html')

@app.route('/technicians', methods=['GET'])
def get_technicians():
    cur = mysql.cursor(dictionary=True)
    cur.execute('SELECT * FROM Technician;')
    technicians = cur.fetchall()
    cur.close()
    return jsonify(technicians)


@app.route('/assign_technician', methods=['POST'])
def assign_technician():
    rma_id = request.form.get('rma_id')
    technician_id = request.form.get('technician_id')

    if not rma_id or not technician_id:
        return '{"error": "RMA_ID and Technician_ID are required."}', 400

    cur = mysql.cursor()

    update_query = 'UPDATE RMA SET Technician_ID = %s WHERE RMA_ID = %s;'
    cur.execute(update_query, (technician_id, rma_id))
    mysql.commit()

    cur.close()

    return '{"Result": "Success"}'



@app.route('/technical/rma_details', methods=['GET'])
def get_rma_details():
    rmaId = request.args.get('rmaId')

    if not rmaId:
        return jsonify({'error': 'RMA_ID is required.'}), 400

    cur = mysql.cursor(dictionary=True)
    

    rma_details_query = '''
        SELECT RMA.RMA_ID, RMA.Inspaction_Start_Date, RMA.Inspeciton_Completion_Date, RMA.Product_Defect,
               RMA.Check_Issue, RMA.Result_Issue, RMA.Product_ID, Product.Serial_Number, Product.Product_Name,
               Technician.Technician_ID, Technician.Tech_Name,
               Brand.Brand_Name, Brand.Brand_Details, Brand.Brand_Website, Brand.Brand_Category,
               Model.Model_Name, Model.Model_Category, Model.Model_Details,
               Customer.Customer_Name, Customer.Customer_Address, Customer.Customer_Phone, Customer.Customer_Email
        FROM RMA
        LEFT JOIN Product ON RMA.Product_ID = Product.Product_ID
        LEFT JOIN Technician ON RMA.Technician_ID = Technician.Technician_ID
        LEFT JOIN Model ON Product.Model_ID = Model.Model_ID
        LEFT JOIN Brand ON Model.Brand_ID = Brand.Brand_ID
        LEFT JOIN Customer ON Product.Customer_ID = Customer.Customer_ID
        WHERE RMA.RMA_ID = %s;
    '''

    cur.execute(rma_details_query, (rmaId,))
    rma_details = cur.fetchone()

    cur.close()

    if not rma_details:
        return jsonify({'error': 'RMA details not found.'}), 404

    return jsonify(rma_details)




@app.route('/update_rma', methods=['POST'])
def update_rma_details():
    try:
        rma_id = request.form.get('rma_id')
        
        result_issue = request.form.get('result_issue')

        if not rma_id or not result_issue:
            return jsonify({'error': 'RMA_ID are required.'}), 400

        cur = mysql.cursor()

        update_query = '''
            UPDATE RMA
            SET Result_Issue = %s
            WHERE RMA_ID = %s;
        '''
        cur.execute(update_query, (result_issue, rma_id))

        mysql.commit()

        cur.close()

        
        return render_template('rma-details.html', rma_id=rma_id, check_issue=check_issue, result_issue=result_issue)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_product_defect', methods=['POST'])
def update_product_defect():
    try:
        rma_id = request.form.get('rma_id')
        product_defect = request.form.get('product_defect')

        if not rma_id or not product_defect:
            return jsonify({'error': 'RMA_ID and Product_Defect are required.'}), 400

        cur = mysql.cursor()

        update_query = '''
            UPDATE RMA
            SET Product_Defect = %s
            WHERE RMA_ID = %s;
        '''
        cur.execute(update_query, (product_defect, rma_id))

        mysql.commit()

        cur.close()

        return jsonify({'success': 'Product Defect updated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import request, jsonify

@app.route('/update_inspection_completion_date', methods=['POST'])
def update_inspection_completion_date():
    try:
        data = request.json
        rma_id = data.get('rma_id')
        completion_date = data.get('completion_date')

        if not rma_id or not completion_date:
            return jsonify({'error': 'RMA_ID and completion_date are required.'}), 400

        cur = mysql.cursor()

        update_query = 'UPDATE RMA SET Inspeciton_Completion_Date = %s WHERE RMA_ID = %s;'
        cur.execute(update_query, (completion_date, rma_id))
        mysql.commit()

        cur.close()

        return jsonify({'success': 'Inspection completion date updated successfully.'}), 200
    except Exception as e:
        traceback.print_exc()  
        return jsonify({'error': str(e)}), 500


@app.route('/delete_rma', methods=['DELETE'])
def delete_rma():
    try:
        rma_id = request.args.get('rma_id')

        if not rma_id:
            return '{"error": "RMA_ID is required."}', 400

        cur = mysql.cursor()

        delete_query = 'DELETE FROM RMA WHERE RMA_ID = %s;'
        cur.execute(delete_query, (rma_id,))
        mysql.commit()

        cur.close()

        return jsonify({'success': 'RMA deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def hash_password(password):
    hashed_password = generate_password_hash(password)
    return hashed_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("Email:", email) 
        print("Password:", password)  
        cur = mysql.cursor()
        try:
            cur.execute("SELECT * FROM Technician WHERE Tech_Email = %s", (email,))
            technician = cur.fetchone()
            
            if technician and check_password_hash(technician[5], password):
                print(technician)
                session['loggedin'] = True
                print(session)
                session['email'] = email
                return send_from_directory('/var/www/html/login/static', 'redirect.html')

            else:
              
                return send_from_directory('/var/www/html/login', 'invalid.html')
        except Exception as e:
            abort(500, str(e))
        finally:
            cur.close()
    return jsonify({'error': 'Method not allowed'}), 405
def update_user_password(email, new_password):
    hashed_password = hash_password(new_password)
    
    cur = mysql.cursor()
    try:
        cur.execute("UPDATE Technician SET Pass = %s WHERE Tech_Email = %s", (hashed_password, email))
        mysql.commit()
    except Exception as e:
        mysql.rollback()
        raise e
    finally:
        cur.close()

    return new_password

#new_password_ali = generate_random_password()
#print("new passAli:", new_password_ali)
#update_user_password('alikula@example.com', new_password_ali)


#new_password_veli = generate_random_password()
#print("new passVeli:", new_password_veli)
#update_user_password('velimula@example.com', new_password_veli)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
       
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        cur = mysql.cursor()
        cur.execute("SELECT * FROM Technician WHERE Tech_Email = %s", (email,))
        existing_user = cur.fetchone()
        cur.close()
        if existing_user:
            return jsonify({'error': 'This email address is already registered.'})
        if not username or not email or not password or not confirm_password:
            return jsonify({'error': 'Please fill out all fields.'})
        elif password != confirm_password:
            return jsonify({'error': 'Passwords do not match.'})
        else:
            
            hashed_password = generate_password_hash(password)
           
            cur = mysql.cursor()
            try:
                cur.execute("INSERT INTO Technician (Tech_Name, Tech_Email, Pass) VALUES (%s, %s, %s)", (username, email, hashed_password))

                mysql.commit()
                flash('Successfully registered.', 'success')
                return send_from_directory('/var/www/html/login', 'index.html')
            except mysql.Error as err:
                flash(f"An error occurred during registration: {err}", 'error')
            finally:
                cur.close()

    return 'register'
def is_logged_in():
    logged_in = session.get('loggedin', False)
    print("Logged in users:", logged_in)
    return logged_in

@app.route('/logout')
def logout():
    session.clear()
    return send_from_directory('/var/www/html/login', 'index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080', debug=True, ssl_context=('/etc/letsencrypt/live/msubuntu.northeurope.cloudapp.azure.com/cert.pem', '/etc/letsencrypt/live/msubuntu.northeurope.cloudapp.azure.com/privkey.pem'))