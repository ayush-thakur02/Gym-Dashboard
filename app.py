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
st.set_page_config(page_title='44 Fitness Center', page_icon='💪', layout='wide')
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
            if first_name == "" or last_name == "" or phone == "" or emergency_phone == "" or house_no == "" or sector == "" or city == "" or selected_date == "":
                st.warning('All fields are required!')
                return
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


def create_new_payments():
    with st.form("payment_form", clear_on_submit=True):
        st.title('New Payment')

        s1, s2 = st.columns(2)
        with s1:
            phone = st.text_input('Phone')
            amount = st.selectbox('Amount', [1500, 4000, 7000, 12000, 3000, 5000, 8000])

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
            dob_date = user[4].strftime("%d %b %y")
            query = "SELECT SUM(Money) FROM payments WHERE Phone = %s"
            cursor.execute(query, (user[2],))
            total_amount_paid = cursor.fetchone()[0]
            table_data.append({'Name': user[1], 'Phone': user[2], 'Emergency': user[3],
                              'DOB': dob_date, 'Payments': total_amount_paid, 'Address': user[5]})
        st.table(table_data)

def display_payments():
    st.title('View Payments')
    search = st.text_input('Search by Name or Phone')
    query = "SELECT * FROM payments WHERE Name LIKE %s OR Phone LIKE %s ORDER BY ID DESC"
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

    x1, y1 = st.columns(2)
    with x1:
        search = st.text_input('Search by Name or Phone')
    with y1:
        date_filter = st.date_input(
            'Filter by Date', format="DD/MM/YYYY", min_value=None, max_value=None, value=None)

    query = "SELECT * FROM daily_entry WHERE (Name LIKE %s OR Phone LIKE %s)"
    params = (f"%{search}%", f"%{search}%")

    if date_filter:
        query += " AND Date = %s"
        params += (date_filter.strftime("%Y-%m-%d"),)  # Ensure date is in YYYY-MM-DD format

    cursor.execute(query, params)
    daily_entries = cursor.fetchall()

    if not daily_entries:
        st.warning('No entries found.')
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
                {'Name': entry[1], 'Date': entry_date, 'Time': entry_time_formatted, 'Phone': entry[2]})
        st.table(table_data)


page = st.sidebar.selectbox("Choose a page", ["New Registeration", "New Payment", "View Members", "View Payments", "Daily Entry"])

if page:
    if page == "New Registeration":
        create_new_user()
    elif page == "New Payment":
        create_new_payments()
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
