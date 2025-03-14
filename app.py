import streamlit as st
import mysql.connector
from datetime import date
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 80px; }
     a{text-decoration: none;}
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        link("https://www.linkedin.com/in/ayush-thakur02/", "Made By @AyushThakur"),
    ]
    layout(*myargs)

conn = mysql.connector.connect(
    host=st.secrets["db_host"],
    user=st.secrets["db_username"],
    password=st.secrets["db_password"],
    database=st.secrets["db_name"]
)

cursor = conn.cursor()
st.set_page_config(page_title='Plus Fitness Zone', page_icon='💪', layout='wide')
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');
            
*{
  font-family: "Poppins", sans-serif;
  font-weight: 400;
  font-style: normal;
}
</style>
""", unsafe_allow_html=True)

def create_new_user():
    with st.form("registration_form", clear_on_submit=True):
        st.title('User Registration')

        s1, s2 = st.columns(2)
        with s1:
            first_name = st.text_input('First Name')
            last_name = st.text_input('Last Name')

        with s2:
            phone = st.text_input('Phone')
            emergency_phone = st.text_input('Emergency Phone')

        a1, a2, a3 = st.columns(3)
        with a1:
            house_no = st.text_input('House No.')
        with a2:
            sector = st.text_input('Sector')
        with a3:
            city = st.text_input('City')

        min_date = date.today().replace(year=date.today().year - 100)
        max_date = date.today()

        selected_date = st.date_input(
            'Select Date of Birth', format="DD/MM/YYYY", min_value=min_date, max_value=max_date, value=None)
        submit = st.form_submit_button(label="Register", use_container_width=True)

        if submit:
            if first_name == "":
                return st.error("First Name Required!")
            if last_name == "":
                last_name = " "
            if phone == "":
                return st.error("Phone Number Required!")
            if emergency_phone == "":
                emergency_phone = 0
            if house_no == "":
                house_no = "<NA>"
            if sector == "":
                sector = "<NA>"
            if city == "":
                city = "<NA>"
        
            existing_query = "SELECT * FROM members WHERE Phone = %s"
            cursor.execute(existing_query, (phone,))
            existing_user = cursor.fetchone()

            if existing_user:
                st.error('Phone number already exists. Please use a different number.')
            else:
                name = first_name + " " + last_name
                address = f"House No: {house_no}, Sector: {sector}, {city}"

                insert_query = "INSERT INTO members (Name, Phone, Emergency_Phone, DOB, Address) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (name, phone,
                               emergency_phone, selected_date, address))
                conn.commit()
                st.success('User registered successfully!')


def edit_user():
    st.title('Edit User Details')
    
    # Search for user to edit
    phone_search = st.text_input('Enter Phone Number to Edit User')
    search_button = st.button('Search User')
    
    if search_button and phone_search:
        query = "SELECT * FROM members WHERE Phone = %s"
        cursor.execute(query, (phone_search,))
        user = cursor.fetchone()
        
        if not user:
            st.error(f"No user found with phone number: {phone_search}")
            return
        
        # Store the user details in session state for the form
        st.session_state.user_id = user[0]
        st.session_state.user_name = user[1]
        st.session_state.user_phone = user[2]
        st.session_state.user_emergency_phone = user[3]
        st.session_state.user_dob = user[4]
        st.session_state.user_address = user[5]
        
        # Parse the address into components
        address_parts = user[5].split(", ")
        house_no = ""
        sector = ""
        city = ""
        
        for part in address_parts:
            if "House No:" in part:
                house_no = part.replace("House No: ", "")
            elif "Sector:" in part:
                sector = part.replace("Sector: ", "")
            else:
                city = part
        
        if city.startswith(", "):
            city = city[2:]
        
        st.session_state.house_no = house_no
        st.session_state.sector = sector
        st.session_state.city = city
        
        # Parse name into first and last name
        name_parts = user[1].split(" ", 1)
        st.session_state.first_name = name_parts[0]
        st.session_state.last_name = name_parts[1] if len(name_parts) > 1 else ""

    # Check if we have user details to edit
    if 'user_id' in st.session_state:
        with st.form("edit_user_form"):
            st.subheader(f"Editing Details for {st.session_state.user_name}")
            
            s1, s2 = st.columns(2)
            with s1:
                first_name = st.text_input('First Name', value=st.session_state.first_name)
                last_name = st.text_input('Last Name', value=st.session_state.last_name)

            with s2:
                phone = st.text_input('Phone', value=str(st.session_state.user_phone))
                emergency_phone = st.text_input('Emergency Phone', 
                                               value="" if st.session_state.user_emergency_phone == 0 
                                               else str(st.session_state.user_emergency_phone))

            a1, a2, a3 = st.columns(3)
            with a1:
                house_no = st.text_input('House No.', value=st.session_state.house_no)
            with a2:
                sector = st.text_input('Sector', value=st.session_state.sector)
            with a3:
                city = st.text_input('City', value=st.session_state.city)

            min_date = date.today().replace(year=date.today().year - 100)
            max_date = date.today()

            selected_date = st.date_input(
                'Date of Birth', format="DD/MM/YYYY", 
                min_value=min_date, max_value=max_date, 
                value=st.session_state.user_dob if st.session_state.user_dob else None)
            
            update_button = st.form_submit_button(label="Update User", use_container_width=True)
            
            if update_button:
                if first_name == "":
                    st.error("First Name Required!")
                    return
                
                if phone == "":
                    st.error("Phone Number Required!")
                    return
                
                # Check if the new phone number conflicts with another user
                if phone != str(st.session_state.user_phone):
                    check_query = "SELECT * FROM members WHERE Phone = %s AND ID != %s"
                    cursor.execute(check_query, (phone, st.session_state.user_id))
                    existing_user = cursor.fetchone()
                    if existing_user:
                        st.error('Phone number already exists for another user. Please use a different number.')
                        return
                
                # Process and validate data
                if last_name == "":
                    last_name = " "
                if emergency_phone == "":
                    emergency_phone = 0
                if house_no == "":
                    house_no = "<NA>"
                if sector == "":
                    sector = "<NA>"
                if city == "":
                    city = "<NA>"
                
                # Update the user information
                name = first_name + " " + last_name
                address = f"House No: {house_no}, Sector: {sector}, {city}"
                
                update_query = """
                UPDATE members 
                SET Name = %s, Phone = %s, Emergency_Phone = %s, DOB = %s, Address = %s 
                WHERE ID = %s
                """
                cursor.execute(update_query, 
                              (name, phone, emergency_phone, selected_date, address, st.session_state.user_id))
                
                # Always update the name in payments table, and update phone if it changed
                if name != st.session_state.user_name or phone != str(st.session_state.user_phone):
                    update_payments_query = """
                    UPDATE payments
                    SET Phone = %s, Name = %s
                    WHERE Phone = %s
                    """
                    cursor.execute(update_payments_query, (phone, name, st.session_state.user_phone))
                    
                    # Update related records in daily_entry table
                    update_daily_entry_query = """
                    UPDATE daily_entry
                    SET Phone = %s, Name = %s
                    WHERE Phone = %s
                    """
                    cursor.execute(update_daily_entry_query, (phone, name, st.session_state.user_phone))
                
                # Commit changes to database
                conn.commit()
                
                # Clear the session state
                for key in ['user_id', 'user_name', 'user_phone', 'user_emergency_phone', 
                            'user_dob', 'user_address', 'first_name', 'last_name',
                            'house_no', 'sector', 'city']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.success('User details updated successfully!')

def create_new_payments():
    with st.form("payment_form", clear_on_submit=True):
        st.title('New Payment')

        s1, s2 = st.columns(2)
        with s1:
            phone = st.text_input('Phone')
            amount = st.selectbox('Amount', [1500, 4000, 7000, 12000, 3000, 5000, 8000, 1200, 3600, 2001, 5001, 9001, 15001, 3501, 8501, 16001, 25001])

        with s2:
            payment_date = st.date_input(
                'Payment Date', format="DD/MM/YYYY", min_value=None, max_value=date.today(), value=None)
            mode = st.selectbox('Payment Mode', ['UPI', 'Cash'])

        submit = st.form_submit_button(label="Submit", use_container_width=True)

        if submit:
            # Verify phone number from members table
            verify_query = "SELECT * FROM members WHERE Phone = %s"
            cursor.execute(verify_query, (phone,))
            verified_user = cursor.fetchone()

            if phone == "":
                st.warning('Phone number is required!')
                return
            elif not verified_user:
                st.error('Phone number does not exist. Please register first.')
                return

            # Check all fields are filled
            elif not all([amount, payment_date]):
                st.warning('All fields are required!')
                return

            # Check if the user exists in the members table
            existing_query = "SELECT * FROM members WHERE Phone = %s"
            cursor.execute(existing_query, (phone,))
            existing_user = cursor.fetchone()
            name = existing_user[1]
            if not existing_user:
                st.error('Phone number does not exist. Please register first.')
                return

            # Insert payment details into the payments table
            insert_query = "INSERT INTO payments (Name, Date, Phone, Mode, Money) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(
                insert_query, (name, payment_date, phone, mode, amount))
            conn.commit()

            st.success(
                f'Payment Submitted Successfully! For {name} of {amount} on {payment_date} via {mode}.')

def edit_payment():
    st.title('Edit Payment')
    
    # Initialize session state variables if they don't exist
    if 'search_phone' not in st.session_state:
        st.session_state.search_phone = ""
    if 'search_date' not in st.session_state:
        st.session_state.search_date = None
    if 'payments_found' not in st.session_state:
        st.session_state.payments_found = []
    if 'payment_displays' not in st.session_state:
        st.session_state.payment_displays = []
    if 'payment_ids' not in st.session_state:
        st.session_state.payment_ids = []
    
    # Search options
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        phone_search = st.text_input('Enter Phone Number to Find Payments', value=st.session_state.search_phone)
    with search_col2:
        date_filter = st.date_input('Filter by Date (Optional)', format="DD/MM/YYYY", value=st.session_state.search_date)
    
    search_button = st.button('Search Payments')
    
    # Update search criteria in session state
    if search_button:
        st.session_state.search_phone = phone_search
        st.session_state.search_date = date_filter
        
        # Fetch payments based on search criteria
        if phone_search:
            # Base query
            if date_filter:
                query = """
                SELECT * FROM payments 
                WHERE Phone = %s AND Date = %s 
                ORDER BY Date DESC
                """
                cursor.execute(query, (phone_search, date_filter))
            else:
                query = """
                SELECT * FROM payments 
                WHERE Phone = %s 
                ORDER BY Date DESC
                """
                cursor.execute(query, (phone_search,))
            
            payments = cursor.fetchall()
            st.session_state.payments_found = payments
            
            # Create display list for payments
            payment_ids = []
            payment_displays = []
            
            for payment in payments:
                payment_id = payment[0]
                payment_name = payment[1]
                payment_date = payment[2].strftime("%d %b %y")
                payment_amount = payment[5]
                payment_mode = payment[4]
                display_text = f"{payment_name} - {payment_date} - ₹{payment_amount} via {payment_mode}"
                
                payment_ids.append(payment_id)
                payment_displays.append(display_text)
            
            st.session_state.payment_ids = payment_ids
            st.session_state.payment_displays = payment_displays
    
    # Display search results if available
    if st.session_state.search_phone and st.session_state.payments_found:
        if not st.session_state.payments_found:
            st.warning('No payments found for the given criteria.')
        else:
            st.subheader("Select a payment to edit:")
            
            # Display selectbox with payments
            selected_payment_index = st.selectbox(
                "Choose payment to edit:",
                range(len(st.session_state.payment_displays)),
                format_func=lambda i: st.session_state.payment_displays[i]
            )
            
            # Get the selected payment details
            selected_payment_id = st.session_state.payment_ids[selected_payment_index]
            selected_payment = st.session_state.payments_found[selected_payment_index]
            
            # Store selected payment details
            payment_name = selected_payment[1]
            payment_date = selected_payment[2]
            payment_mode = selected_payment[4]
            payment_amount = selected_payment[5]
            
            # Display edit form
            with st.form(f"edit_payment_form_{selected_payment_id}"):
                st.subheader(f"Edit Payment for {payment_name}")
                
                e1, e2 = st.columns(2)
                with e1:
                    amount_options = [1500, 4000, 7000, 12000, 3000, 5000, 8000, 1200, 3600, 
                                      2001, 5001, 9001, 15001, 3501, 8501, 16001, 25001]
                    default_index = amount_options.index(payment_amount) if payment_amount in amount_options else 0
                    edit_amount = st.selectbox('Amount', amount_options, index=default_index)
                
                with e2:
                    min_date = None
                    max_date = date.today()
                    edit_date = st.date_input('Payment Date', value=payment_date,
                                              format="DD/MM/YYYY", min_value=min_date, max_value=max_date,
                                              key=f"date_{selected_payment_id}")
                    edit_mode = st.selectbox('Payment Mode', ['UPI', 'Cash'], 
                                            index=0 if payment_mode == 'UPI' else 1,
                                            key=f"mode_{selected_payment_id}")
                
                update_payment_button = st.form_submit_button("Update Payment", use_container_width=True)
                
                if update_payment_button:
                    # Update payment in database
                    # Update payment in database
                    update_query = """
                    UPDATE payments
                    SET Date = %s, Mode = %s, Money = %s
                    WHERE ID = %s
                    """
                    cursor.execute(update_query, (edit_date, edit_mode, edit_amount, selected_payment_id))
                    
                    st.success("Payment updated successfully!")
                    
                    # Update the payment in session state to reflect changes
                    for i, payment in enumerate(st.session_state.payments_found):
                        if payment[0] == selected_payment_id:
                            updated_payment = list(payment)
                            updated_payment[2] = edit_date
                            updated_payment[4] = edit_mode
                            updated_payment[5] = edit_amount
                            st.session_state.payments_found[i] = tuple(updated_payment)
                            
                            # Update the display text
                            updated_display = f"{payment_name} - {edit_date.strftime('%d %b %y')} - ₹{edit_amount} via {edit_mode}"
                            st.session_state.payment_displays[i] = updated_display
                            break
    elif st.session_state.search_phone:
        st.warning('No payments found for the given criteria.')

def display_registered_users():
    st.title('View Members')
    search = st.text_input('Search by Name or Phone')
    query = "SELECT * FROM members WHERE Name LIKE %s OR Phone LIKE %s ORDER BY ID DESC"
    cursor.execute(query, (f"%{search}%", f"%{search}%"))
    users = cursor.fetchall()

    if not users:
        st.warning('No users found.')
    else:
        table_data = []
        for user in users:
            
            if user[4] != None:
                dob_date = user[4].strftime("%d %b %y")
            else:
                dob_date = ""
                
            if user[2] == 0:
                phone_number = ""
            else:
                phone_number = str(user[2])
                
            if user[3] == 0:
                emergency_phone_number = ""
            else:
                emergency_phone_number = str(user[3])
                
            table_data.append({'Name': user[1], 'Phone': phone_number, 'Emergency': emergency_phone_number,
                              'DOB': dob_date, 'Address': user[5]})
        st.table(table_data)


def display_payments():
    st.title('View Payments')
    search = st.text_input('Search by Name or Phone')
    query = "SELECT * FROM payments WHERE Name LIKE %s OR Phone LIKE %s ORDER BY Date DESC"
    cursor.execute(query, (f"%{search}%", f"%{search}%"))
    payments = cursor.fetchall()

    if not payments:
        st.warning('No payments found.')
    else:
        table_data = []
        for payment in payments:
            # Format the date as "day month year"
            payment_date = payment[2].strftime("%d %b %y")
            table_data.append({'Name': payment[1], 'Date': payment_date,
                              'Phone': payment[3], 'Mode': payment[4], 'Amount': payment[5]})
        st.table(table_data)

def display_daily_entry():
    st.title('Daily Entry')

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    # Query to get today's entries
    query_today = """
    SELECT * FROM daily_entry 
    WHERE Date = %s 
    ORDER BY Sno DESC;
    """
    cursor.execute(query_today, (today_str,))
    daily_entries = cursor.fetchall()

    # Query to get entry counts by hour for today
    query_hourly = """
    SELECT HOUR(Time), COUNT(*) 
    FROM daily_entry 
    WHERE Date = %s 
    GROUP BY HOUR(Time) 
    ORDER BY HOUR(Time);
    """
    cursor.execute(query_hourly, (today_str,))
    hourly_data = cursor.fetchall()

    # Display graph
    st.subheader(f"Today's Entry Count ({today.strftime('%d %b %Y')})")
    
    if not hourly_data:
        st.info("No entries recorded for today yet.")
    else:
        hours = [entry[0] for entry in hourly_data]
        counts = [entry[1] for entry in hourly_data]
        
        # Create a complete hour range from gym opening to current hour
        current_hour = date.today().hour
        full_hour_range = list(range(5, min(current_hour + 1, 23)))  # Assuming gym opens at 5 AM
        complete_counts = [0] * len(full_hour_range)
        
        # Fill in the actual counts
        for i, hour in enumerate(hours):
            if hour in full_hour_range:
                idx = full_hour_range.index(hour)
                complete_counts[idx] = counts[i]
        
        # Format hour labels (5 AM, 6 AM, etc.)
        hour_labels = [f"{h} {'AM' if h < 12 else 'PM'}" for h in full_hour_range]
        
        # Plot the line chart
        chart_data = {"Hour": hour_labels, "Entries": complete_counts}
        st.line_chart(chart_data, x="Hour", y="Entries", height=300)
        
        # Total entries today
        total_entries = sum(counts)
        st.metric("Total Entries Today", total_entries)

    # Display today's entries in a table
    st.subheader("Today's Entry Log")
    if not daily_entries:
        st.warning('No entries found for today.')
    else:
        table_data = []
        for entry in daily_entries:
            entry_date = entry[3].strftime("%d %b %y")
            entry_time = entry[4].total_seconds()
            hours = int(entry_time // 3600)  
            minutes = int((entry_time % 3600) // 60)  
            seconds = int(entry_time % 60) 
            entry_time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            table_data.append(
                {'Name': entry[1], 'Time': entry_time_formatted, 'Phone': entry[2]})
        st.table(table_data)

    # Optional: Add a filter section that can be expanded
    with st.expander("Search Past Entries"):
        x1, y1 = st.columns(2)
        with x1:
            search = st.text_input('Search by Name or Phone')
        with y1:
            date_filter = st.date_input(
                'Filter by Date', format="DD/MM/YYYY", min_value=None, max_value=None, value=today)
        
        if search or date_filter != today:
            query = """
            SELECT * FROM daily_entry 
            WHERE (Name LIKE %s OR Phone LIKE %s) 
            AND Date = %s 
            ORDER BY Sno DESC;
            """
            cursor.execute(query, (f"%{search}%", f"%{search}%", date_filter))
            filtered_entries = cursor.fetchall()
            
            if not filtered_entries:
                st.warning('No entries found for your search criteria.')
            else:
                filter_table_data = []
                for entry in filtered_entries:
                    entry_date = entry[3].strftime("%d %b %y")
                    entry_time = entry[4].total_seconds()
                    hours = int(entry_time // 3600)  
                    minutes = int((entry_time % 3600) // 60)  
                    seconds = int(entry_time % 60) 
                    entry_time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    filter_table_data.append(
                        {'Name': entry[1], 'Date': entry_date, 'Time': entry_time_formatted, 'Phone': entry[2]})
                st.table(filter_table_data)


# Main navigation
page = st.sidebar.selectbox(
    "Choose a page", 
    ["New Registeration", "Edit User", "New Payment", "Edit Payment", "View Members", "View Payments", "Daily Entry"]
)

if page:
    if page == "New Registeration":
        create_new_user()
    elif page == "Edit User":
        edit_user()
    elif page == "New Payment":
        create_new_payments()
    elif page == "Edit Payment":
        edit_payment()
    elif page == "View Members":
        display_registered_users()
    elif page == "View Payments":
        display_payments()
    elif page == "Daily Entry":
        display_daily_entry()


footer()
# Close MySQL connection
cursor.close()
conn.close()
