from flask import Flask, render_template, url_for, jsonify, request, redirect, session, flash
import psycopg2

app = Flask(__name__)
app.secret_key = '123'
cursor = None
def connect_db():
    db_link = 'postgres://mzlmdawh:68uKpdQLKb5UwzZces5mCIbhtG2yOH3o@batyr.db.elephantsql.com/mzlmdawh'

    conn = psycopg2.connect(db_link)
    return conn

def delete_from_db(table, _id, id_type):
    # Open connection
    conn = connect_db()
    curr = conn.cursor()

    # Table is the table you'll want to query, id_type is the specific attr, _id is the attr itself
    query = f'DELETE FROM {table} WHERE {id_type} = {_id}'
    print('executing', query)
    curr.execute(query)
    conn.commit()

    # Close connection
    curr.close()
    conn.close()

@app.route('/get_data', methods=['GET'])
def get_table(table):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        # Replace 'your_table_name' with the name of the table you want to query
        query = f"SELECT * FROM {table};"
        print('executing ', query)
        cursor.execute(query)
        # Fetch all data from the query result
        data = cursor.fetchall()
        # Close the cursor and database connection
        cursor.close()
        conn.close()
        # Convert data to a JSON response
        return data

    except Exception as e:
        print("ERROR")
        return jsonify({'error': str(e)})

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        custID = request.form.get('CustomerID')
        manID = request.form.get('ManagerID')
        session['customer_id_entered'] = custID
        print('custid', custID, 'manID', manID)
        if custID != '':
            return redirect(url_for('search_cus'))
        elif manID != '':
            return redirect(url_for('admin_dash'))
        else:
            return render_template('index.html')
    return render_template('index.html')

@app.route('/admin-dash')
def admin_dash():
    return render_template('admin-dashboard.html')

@app.route('/franchise')
def franchise():
    return render_template('franchise.html')

@app.route('/search-cus') #actually searches through purchases table
def search_cus():
    customer_id_entered = session.get('customer_id_entered')
    data = get_table('purchases')
    print('data1', data)
    newdata = [row for row in data if row[2] == int(customer_id_entered)]
    print('data',newdata, 'id', customer_id_entered)
    return render_template('search-cus.html', data=newdata)
@app.route('/search-cus/delete', methods=['GET', 'POST'])
def delete_cus(): #actually searches through purchases table
    if request.method == 'POST':
        id = request.form['del']
        delete_from_db('purchases', id, 'pur_id')
    return redirect(url_for('search_cus'))

@app.route('/search-cus/update', methods = ['GET', 'POST'])
def update_cus(): #actually deals with udating purchases
    if request.method == 'POST':
        print(request.form, 'adasdasdads')
        pur_id = request.form['1']
        data = get_table('purchases')
        purchase_id_exists = any(row[0] == int(pur_id) for row in data)
        if (purchase_id_exists):
            query = f"""
            UPDATE purchases
            SET pur_id = '{request.form['1']}', vin_id = '{request.form['2']}', cust_id = '{request.form['3']}', pur_cost = '{request.form['4']}'
            WHERE pur_id = {pur_id};
            """
            conn = connect_db()
            curr = conn.cursor()

            print('executing', query)

            curr.execute(query)
            conn.commit()
            curr.close()
            conn.close()



        elif all([request.form[item] != '' for item in request.form]):
            print("UPDATING CUSTOMER PURCHASE")
            # All items are accounted for
            query = f"""
            INSERT INTO purchases (pur_id, vin_id, cust_id, pur_cost) VALUES
             ('{request.form['1']}', '{request.form['2']}', '{request.form['3']}', '{request.form['4']}')
            """
            conn = connect_db()
            curr = conn.cursor()

            print('executing', query)

            curr.execute(query)
            conn.commit()
            curr.close()
            conn.close()
    return redirect(url_for('search_cus'))

# Vinyl operations

def isValidPrice(s):
    try:
        if float(s) or s.isdigit():
            return True
        else:
            return False
    except ValueError:
        return False
    
@app.route('/admin-vinyl')
def manager_vinyl():
    data = get_table('vinyls')
    print('data',data)
    return render_template('admin-vinyl.html', data=data)

@app.route('/admin-vinyl/delete', methods=['GET', 'POST'])
def delete_vinyl():
    if request.method == 'POST':
        vin_id = request.form['del']
        delete_from_db('vinyls', vin_id, 'vin_id')
    return redirect(url_for('manager_vinyl'))

@app.route('/admin-vinyl/update', methods=['GET', 'POST'])
def update_vinyl():
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()
        
        print(request.form)
        recordID = request.form['vinylID']
        recordName = request.form['updateName']
        recordArtist = request.form['updateArtist']
        recordGenre = request.form['updateGenre']
        recordPrice = request.form['updatePrice']
        if recordID == '' or recordName == '' or recordArtist == '' or recordGenre == '' or recordPrice == '':
            cursor.close()
            conn.close()
            print("vinyl update: one of the values is empty")
            flash("Empty Field*")
            return redirect(url_for('manager_vinyl'))

        if recordID.isdigit() == False:
            cursor.close()
            conn.close()
            print("vinyl update: invalid ID")
            flash("Invalid ID*")
            return redirect(url_for('manager_vinyl'))
        
        if isValidPrice(recordPrice) == False:
            cursor.close()
            conn.close()
            print("vinyl update: invalid price")
            flash("Invalid Price*")
            return redirect(url_for('manager_vinyl'))  
    
        query = f"""
            UPDATE vinyls
            SET vin_name = '{recordName}', vin_artist = '{recordArtist}', vin_genre = '{recordGenre}', vin_price = '{recordPrice}'
            WHERE vin_id = {recordID};
            """
        cursor.execute(query)
        print("executing vinyl update query")
        conn.commit()

        cursor.close()
        conn.close()
        
        return redirect(url_for('manager_vinyl'))


        

@app.route('/admin-vinyl/add', methods=['GET', 'POST'])
def add_vinyl():
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()
        print(request.form)
        
        recordName = request.form['inputName']
        recordArtist = request.form['inputArtist']
        recordGenre = request.form['inputGenre']
        recordPrice = request.form['inputPrice']
        
        if recordName == '' or recordArtist == '' or recordGenre == '' or recordPrice == '':
            cursor.close()
            conn.close()
            flash("Empty Field*")
            return redirect(url_for('manager_vinyl'))
        
        if isValidPrice(recordPrice) == False:
            cursor.close()
            conn.close()
            flash("Invalid Price*")
            return redirect(url_for('manager_vinyl'))
        
        query = f"INSERT INTO vinyls (vin_name, vin_artist, vin_genre, vin_price) VALUES ('{recordName}', '{recordArtist}', '{recordGenre}', '{recordPrice}');"
        cursor.execute(query)
        conn.commit()
        # Close the cursor and database connection
        cursor.close()
        conn.close()
        flash("Data Inserted Successfully*")
        return redirect(url_for('manager_vinyl'))
    
# Customer operations
@app.route('/admin-cust', methods=['GET', 'POST'])
def manager_cust(): #gets and displays the customer table
    if request.method == 'POST':
        if any([request.form[item] == '' for item in request.form]):
            flash("Error: Empty update field*")
            return redirect(url_for('manager_cust'))
        else:
            conn = connect_db()
            curr = conn.cursor()

            print(request.form)

            query = f"""
            UPDATE customers
            SET cust_fname = '{request.form['fname']}', cust_lname = '{request.form['lname']}', cust_phone = '{request.form['phone']}'
            WHERE cust_id = {request.form['upd-cust']};
            """

            print('executing', query)
            curr.execute(query)
            conn.commit()

            curr.close()
            conn.close()

    _data = get_table('customers')
    print('data', _data)
    return render_template('admin-cust.html', data=_data)

@app.route('/admin-cust/filter', methods=['GET'])
def filter_cust():
    conn = connect_db()
    curr = conn.cursor()

    print(request.form)

    filter_by_id = request.args.get('filter-by-id')

    if filter_by_id == '':
        return redirect(url_for('manager_cust'))

    query = f"""
    SELECT * FROM customers
    WHERE cust_id = {filter_by_id};
    """

    print('executing', query)
    curr.execute(query)
    data = curr.fetchall()
    conn.commit()

    curr.close()
    conn.close()
    return render_template('admin-cust.html', data=data)

@app.route('/admin-cust/delete', methods=['GET', 'POST'])
def delete_cust(): #deletes from customer table
    if request.method == 'POST':
        customer_id = request.form['del']
        delete_from_db('customers', customer_id, 'cust_id')
    return redirect(url_for('manager_cust'))

@app.route('/admin-cust/add-cust', methods=['POST'])
def add_cust(): #adds to customer table
    # make connecting
    # make cursor
    conn = connect_db()
    curr = conn.cursor()
    # make sql string using text inside text fields 
    fname = request.form['fname']
    lname = request.form['lname']
    phone = request.form['phone']

    if fname == '' or lname == '' or phone == '':
        flash("Error: You have an empty field*")
        return redirect(url_for('manager_cust'))
    
    query = f"INSERT INTO customers (cust_fname, cust_lname, cust_phone) VALUES ('{fname}', '{lname}', '{phone}');"
    # submit sql command
    curr.execute(query)
    conn.commit()
    # close connection and cursor
    curr.close()
    conn.close()
    return redirect(url_for('manager_cust'))


@app.route('/admin-cust/update', methods=['POST'])
def update_cust():
    #if request.method == 'POST':
    conn = connect_db()
    curr = conn.cursor()

    print(request.form)

    query = f"SELECT * FROM customers WHERE cust_id = {request.form['upd-cust']}"
    curr.execute(query)
    data = curr.fetchall()
    print(data[0])
    curr.close()
    conn.close()

    return render_template('update-cust.html', data=data[0])



# Manager operations
@app.route('/admin-mana', methods=['GET', 'POST'])
def manager_mana():
    if request.method == 'POST':
        if any([request.form[item] == '' for item in request.form]):
            return redirect(url_for('manager_mana'))
        else:
            conn = connect_db()
            curr = conn.cursor()

            print(request.form)

            query = f"""
            UPDATE managers
            SET mana_fname = '{request.form['fname']}', mana_lname = '{request.form['lname']}', mana_phone = '{request.form['phone']}'
            WHERE mana_id = {request.form['id']};
            """

            print('executing', query)
            curr.execute(query)
            conn.commit()

            curr.close()
            conn.close()

    data = get_table('managers')
    print('data', data)
    return render_template('admin-manager.html', data=data)

@app.route('/admin-mana/create', methods=['GET', 'POST'])
def create_mana():
    if request.method == 'POST':
        print(request.form)
        if all([request.form[item] != '' for item in request.form]):
            print("HELP")
            # All items are accounted for
            query = f"""
            INSERT INTO managers (mana_fname, mana_lname, mana_phone)
            VALUES ('{request.form['fname']}', '{request.form['lname']}', '{request.form['phone']}')
            """
            conn = connect_db()
            curr = conn.cursor()

            print('executing', query)

            curr.execute(query)
            conn.commit()
            curr.close()
            conn.close()
    return redirect(url_for('manager_mana'))

@app.route('/admin-mana/update', methods=['GET', 'POST'])
def update_mana():
    if request.method == 'POST':
        conn = connect_db()
        curr = conn.cursor()

        print(request.form)

        query = f"SELECT * FROM managers WHERE mana_id = {request.form['upd']}"
        curr.execute(query)
        data = curr.fetchall()
        print(data[0])
        curr.close()
        conn.close()
    return render_template('update-manager.html', data=data[0])

@app.route('/admin-mana/delete', methods=['GET', 'POST'])
def delete_mana():
    if request.method == 'POST':
        mana_id = request.form['del']
        delete_from_db('managers', mana_id, 'mana_id')
    return redirect(url_for('manager_mana')) 

if __name__ == "__main__": 
    app.run(debug=True) 
    #when going to debud set debug to False
