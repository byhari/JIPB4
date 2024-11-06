import os
os.system('bash setup.sh')
import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime

# Function to check login credentials
def check_login(username, password):
    try:
        conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};Dbq=172.25.1.83:1521/empdb01;Uid=fasdollar;Pwd=fasdollar', timeout=10)
        cursor = conn.cursor()
        
        query = """
        SELECT ROLE_CODE, CH_USER_ACTIVE, CH_USER_CODE, VC_USERNAME
        FROM TAX_USERLOG_HARI
        WHERE VC_USERNAME = ? AND PASS = ?
        """
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result
    except pyodbc.Error as e:
        if 'ORA-12170' in str(e):
            st.error("Connection timeout, check your connection!")
        else:
            st.error(f"An error occurred: {e}")
        return None

# Function to fetch users with null ROLE_CODE
def fetch_users_with_null_role():
    try:
        conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};Dbq=172.25.1.83:1521/empdb01;Uid=fasdollar;Pwd=fasdollar', timeout=10)
        cursor = conn.cursor()
        
        query = """
        SELECT CH_USER_CODE, VC_USERNAME
        FROM TAX_USERLOG_HARI
        WHERE ROLE_CODE IS NULL
        """
        cursor.execute(query)
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return users
    except pyodbc.Error as e:
        if 'ORA-12170' in str(e):
            st.error("Connection timeout, check your connection!")
        else:
            st.error(f"An error occurred: {e}")
        return []

# Function to fetch company data
def fetch_companies(user_code):
    try:
        conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};Dbq=172.25.1.83:1521/empdb01;Uid=fasdollar;Pwd=fasdollar', timeout=10)
        cursor = conn.cursor()
        
        query = """
        SELECT COMPCODE, COMPANY_NAME, COMPCODENAME
        FROM USERCODE_COMPCODENAME_HARI
        WHERE CH_USER_CODE = ?
        """
        cursor.execute(query, (user_code,))
        companies = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return companies
    except pyodbc.Error as e:
        if 'ORA-12170' in str(e):
            st.error("Connection timeout, check your connection!")
        else:
            st.error(f"An error occurred: {e}")
        return []

# Function to fetch JI Journal data based on company code
def fetch_jipb_journal(comp_code):
    try:
        conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};Dbq=172.25.1.83:1521/empdb01;Uid=fasdollar;Pwd=fasdollar', timeout=10)
        cursor = conn.cursor()
        
        query = """
        SELECT VC_VOUCHER_NO, NU_CURRENCY_CODE, DT_VOUCHER_DATE, NARRATION_HD
        FROM JIPB_JI_HARI
        WHERE COMPCODE = ?
        """
        cursor.execute(query, (comp_code,))
        journals = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return journals
    except pyodbc.Error as e:
        if 'ORA-12170' in str(e):
            st.error("Connection timeout, check your connection!")
        else:
            st.error(f"An error occurred: {e}")
        return []

# Function to fetch records from JIPB_PB_HARI based on selected company and currency code
def fetch_jipb_pb_records(comp_code, currency_code):
    try:
        conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};Dbq=172.25.1.83:1521/empdb01;Uid=fasdollar;Pwd=fasdollar', timeout=10)
        cursor = conn.cursor()
        
        query = """
        SELECT * 
        FROM JIPB_PB_HARI
        WHERE COMPCODE = ? AND CUR = ?
        """
        cursor.execute(query, (comp_code, currency_code))
        
        # Fetch all records and column names
        records = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Convert NU_CURRENCY_CODE to numeric format
        records_numeric = []
        for record in records:
            record_list = list(record)
            record_list[columns.index('CUR')] = int(record_list[columns.index('CUR')])
            records_numeric.append(tuple(record_list))
        
        cursor.close()
        conn.close()
        
        return records_numeric, columns
    
    except pyodbc.Error as e:
        if 'ORA-12170' in str(e):
            st.error("Connection timeout, check your connection!")
        else:
            st.error(f"An error occurred: {e}")
        return [], []

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Function to handle exit
def handle_exit():
    st.session_state.clear()
    st.session_state['page'] = 'login'

# Login Page
# Login Page
if st.session_state['page'] == 'login':
    st.title('Login Page')

    username = st.text_input('Username', key='username').upper()
    password = st.text_input('Password', type='password', key='password').upper()

    if st.button('OK', key='login_ok_button'):
        if not username or not password:
            st.error('Please login first!')
        else:
            result = check_login(username, password)
            if result is None:
                st.error('Login failed, user name or password not match')
            else:
                role_code, user_active, user_code, vc_username = result
                if user_active == 'N':
                    st.error('Login failed, user is not active')
                else:
                    st.success('Login success')
                    st.session_state['user_code'] = user_code
                    st.session_state['vc_username'] = vc_username
                    st.session_state['page'] = 'jipb'

# Disabled SUBMIT and EXIT buttons
    #st.button('SUBMIT', disabled=True)
    #st.button('EXIT', disabled=True)

# JIPB Page
elif st.session_state['page'] == 'jipb':
    user_code = st.session_state.get('user_code')
    vc_username = st.session_state.get('vc_username')

    if user_code and vc_username:
        st.title(f'Welcome {vc_username}')

        #length_of_user_code = len(user_code)
        #st.write(f"The length of user_code is: {length_of_user_code}")
        
        companies = fetch_companies(user_code)
        company_names = [company[2] for company in companies]
        company_codes = [company[0] for company in companies]
        
        selected_company = st.selectbox('Select a Company', company_names)
        selected_company_index = company_names.index(selected_company)
        selected_company_code = company_codes[selected_company_index]
        
        jipb_journal_data = fetch_jipb_journal(selected_company_code)
        jipb_journal = [journal[0] for journal in jipb_journal_data]
        
        if jipb_journal:
            selected_ji = st.selectbox('Select a JI Journal', jipb_journal)

            #length_of_selected_ji = len(selected_ji)
            #st.write(f"The length of selected_ji is: {length_of_selected_ji}")

            #length_of_selected_company_code = len(selected_company_code)
            #st.write(f"The length of selected_company_code is: {length_of_selected_company_code}")

            #if len(selected_ji) > 10:
            #    st.error("The value of selected_ji exceeds the maximum length of 10 characters.")
            #else:
            #    st.write(f'Panjang {selected_ji} aman')
            
            # Find the corresponding NU_CURRENCY_CODE for the selected JI Journal
            selected_ji_index = jipb_journal.index(selected_ji)
            nu_currency_code = jipb_journal_data[selected_ji_index][1]
            voucher_date = jipb_journal_data[selected_ji_index][2]
            naration = jipb_journal_data[selected_ji_index][3]
            
            #st.write(f'FAS Unit : {selected_company}')
            #st.write(f'Voucher No : {selected_ji}')
            
            # Determine the currency type
            currency_type = "USD" if nu_currency_code == 1 else "IDR" if nu_currency_code == 2 else "Unknown"
            st.write(f'Currency : {nu_currency_code} ({currency_type})')

            # Format the voucher date
            run_dt = datetime.strptime(str(voucher_date), '%Y-%m-%d %H:%M:%S').strftime('%d-%b-%Y')
            st.write(f'Voucher date : {run_dt}')

            # Determine the naration
            st.write(f'Naration : {naration}')
            
            # Fetch records from JIPB_PB_HARI
            records, columns = fetch_jipb_pb_records(selected_company_code, nu_currency_code)
            if records:
                df = pd.DataFrame(records, columns=columns)

                # Hide the column
                df = df.drop(columns=['CUR'])
                
                # Add checkboxes
                df.insert(0, 'Select', False)
                
                # Display the DataFrame without the index
                edited_df = st.data_editor(df, hide_index=True, num_rows="dynamic")
                
                # Calculate selected records and total
                selected_df = edited_df[edited_df['Select']]
                selected_count = len(selected_df)
                total_sum = selected_df['NU_F_CURRENCY_DR'].replace(',', '').astype(float).sum() - selected_df['NU_F_CURRENCY_CR'].replace(',', '').astype(float).sum()

                st.write(f'Selected Records: {selected_count}')
                st.write(f'Total: {total_sum:,.2f}')

                #for index, row in selected_df.iterrows():
                #    length_of_index = len(str(index))
                #    st.write(f"The length of the index {index} is: {length_of_index}")

# Create a SUBMIT button for inserting selected records
if st.button('SUBMIT', key='submit_button'):
    selected_df = edited_df[edited_df['Select']]
    if selected_df.empty:
        st.error("Please select records first!")
    else:
        try:
            conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};Dbq=172.25.1.83:1521/empdb01;Uid=fasdollar;Pwd=fasdollar', timeout=10)
            cursor = conn.cursor()
            
            for index, row in selected_df.iterrows():
                vc_voucher_no = selected_ji
                
                # Fetch the maximum NU_SERIAL_NO and increment by 1 with conditions
                cursor.execute("""
                    SELECT MAX(NU_SERIAL_NO) 
                    FROM DT_INTERCOMP_PAYMENT_LINES 
                    WHERE COMPCODE = ? AND VC_VOUCHER_NO = ?
                """, (selected_company_code, vc_voucher_no))
                max_serial_no = cursor.fetchone()[0]
                nu_serial_no = max_serial_no + 1 if max_serial_no is not None else 1
                
                vc_bill_no = row['VC_BILL_NO']
                dt_bill_date = row['DT_BILL_DATE']
                created_by = user_code
                creation_date = voucher_date
                modified_by = user_code
                modification_date = voucher_date
                vc_cont_code = row['VC_CONT_CODE']
                vc_comp_code = row['VC_COMP_CODE']
                voucher_no = row['VC_VOUCHER_NO']
                compcode = row['COMPCODE']
                
                # Check if the record already exists
                check_query = """
                SELECT COUNT(*) 
                FROM DT_INTERCOMP_PAYMENT_LINES 
                WHERE VC_VOUCHER_NO = ? AND NU_SERIAL_NO = ?
                """
                cursor.execute(check_query, (vc_voucher_no, nu_serial_no))
                record_exists = cursor.fetchone()[0]
                
                if record_exists:
                    # If the record exists, increment the serial number until a unique one is found
                    while record_exists:
                        nu_serial_no += 0
                        cursor.execute(check_query, (vc_voucher_no, nu_serial_no))
                        record_exists = cursor.fetchone()[0]
                
                # Insert a new record
                insert_query = """
                INSERT INTO DT_INTERCOMP_PAYMENT_LINES (
                    VC_VOUCHER_NO, NU_SERIAL_NO, VC_BILL_NO, DT_BILL_DATE, CREATED_BY, CREATION_DATE,
                    MODIFIED_BY, MODIFICATION_DATE, VC_CONT_CODE, VC_COMP_CODE, VOUCHER_NO, COMPCODE
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, (
                    vc_voucher_no, nu_serial_no, vc_bill_no, dt_bill_date, created_by, creation_date,
                    modified_by, modification_date, vc_cont_code, vc_comp_code, voucher_no, compcode
                ))
            
            # Update PAYMENT_STATUS_CODE in DT_PURCHASE_HEADERS
            update_query = """
            UPDATE DT_PURCHASE_HEADERS
            SET PAYMENT_STATUS_CODE = 'P'
            WHERE COMPCODE = ? AND VC_VOUCHER_NO = ?
            """
            
            for index, row in selected_df.iterrows():
                cursor.execute(update_query, (str(row['COMPCODE']), str(row['VC_VOUCHER_NO'])))
            
            conn.commit()
            
            cursor.close()
            conn.close()
            
            st.success("Selected records have been successfully inserted and updated. The DataFrame has been refreshed.")
            st.session_state['show_refresh'] = True
        
        except pyodbc.Error as e:
            st.error(f"An error occurred while inserting or updating records: {e}")

# Show the REFRESH button if records have been submitted
if 'show_refresh' in st.session_state and st.session_state['show_refresh']:
    if st.button('REFRESH', key='refresh_button'):
        try:
            # Function to fetch records from DT_INTERCOMP_PAYMENT_LINES based on selected company code and voucher number
            def fetch_intercomp_payment_lines(comp_code, voucher_no):
                try:
                    conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};Dbq=172.25.1.83:1521/empdb01;Uid=fasdollar;Pwd=fasdollar', timeout=10)
                    cursor = conn.cursor()
        
                    query = """
                    SELECT VOUCHER_NO
                    FROM DT_INTERCOMP_PAYMENT_LINES
                    WHERE COMPCODE = ? AND VC_VOUCHER_NO = ?
                    """
                    cursor.execute(query, (comp_code, voucher_no))
                    records = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
        
                    cursor.close()
                    conn.close()
        
                    return records, columns
    
                except pyodbc.Error as e:
                    if 'ORA-12170' in str(e):
                        st.error("Connection timeout, check your connection!")
                    else:
                        st.error(f"An error occurred: {e}")
                    return [], []

            # Assuming selected_company_code and selected_ji are defined earlier in the script
            selected_company_index = company_names.index(selected_company)
            selected_company_code = company_codes[selected_company_index]

            # Fetch records from DT_INTERCOMP_PAYMENT_LINES based on selected company code and voucher number
            records, columns = fetch_intercomp_payment_lines(selected_company_code, selected_ji)

            # Ensure the data matches the expected shape before creating the DataFrame
            if records and len(records[0]) == len(columns):
                # Convert records to a list of lists to match the expected shape
                records_list = [list(record) for record in records]
    
                # Create a DataFrame with an auto-incremented serial number as the index
                df = pd.DataFrame(records_list, columns=columns)
                df.index += 1  # Start the index from 1
    
                # Display the DataFrame
                st.dataframe(df)
            else:
                st.error("The shape of the data does not match the expected number of columns.")
                    
        except pyodbc.Error as e:
            st.error(f"An error occurred while fetching records: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

if st.button('EXIT', key='exit_button'):
    handle_exit()

input("Press Enter to exit...")
