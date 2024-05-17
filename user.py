import streamlit as st
import mysql.connector
import datetime
from datetime import date
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb
from pytz import timezone

def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
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
st.set_page_config(page_title='44 Fitness Center', page_icon='💪', layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');
            
*{
  font-family: "Poppins", sans-serif;
  font-weight: 400;
  font-style: normal;
}

</style>
""", unsafe_allow_html=True)


def entry():
    with st.form("entry", clear_on_submit=True):
        st.title('Welcome to 44 FITNESS CENTER')
        phone = st.text_input('Enter your Phone Number')
        submit = st.form_submit_button(
            label="Submit", use_container_width=True)

        if submit:
            if phone == "":
                st.warning('Phone number is required!')
                return

            existing_query = "SELECT * FROM members WHERE Phone = %s"
            cursor.execute(existing_query, (phone,))
            existing_user = cursor.fetchone()

            if existing_user:
                payment_query = "SELECT * FROM payments WHERE Phone = %s ORDER BY Date DESC LIMIT 1"
                cursor.execute(payment_query, (phone,))
                latest_payment = cursor.fetchone()

                if latest_payment == None:
                    st.error('No payment found. Please make payment first.')
                    return

                if latest_payment:
                    if len(latest_payment) == 6: 
                        payment_amount = latest_payment[5]
                        payment_date = latest_payment[2]

                        global expiry_date

                        if payment_amount == 1500:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=30)
                        elif payment_amount == 4000:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=90)
                        elif payment_amount == 7000:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=180)
                        elif payment_amount == 12000:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=365)
                        elif payment_amount == 3000:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=90)
                        elif payment_amount == 5000:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=180)
                        elif payment_amount == 8000:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=365)
                        elif payment_amount == 1200:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=30)
                        elif payment_amount == 3600:
                            expiry_date = payment_date + \
                                datetime.timedelta(days=90)
                        today_date = date.today()
                        if today_date > expiry_date:
                            st.error(
                                'Your membership has expired. Please renew your membership to enter.')
                            return
                    else:
                        st.error(
                            "Incomplete payment data retrieved. Some Error occured in the database. Please contact Ayush.")
                        return
            else:
                st.error('User not found. Please register first.')
                return

            today_date = date.today()
            check_query = "SELECT * FROM daily_entry WHERE Phone = %s AND Date = %s"
            cursor.execute(check_query, (phone, str(today_date)))
            check_user = cursor.fetchone()

            if check_user:
                st.error('You have already checked in today.')
                return

            name = existing_user[1]

            if not existing_user:
                st.error('User not found. Please register first.')
                return

            current_time = datetime.datetime.now(timezone("Asia/Kolkata")).strftime("%H:%M:%S")

            insert_query = "INSERT INTO daily_entry (Name, Phone, Date, Time) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (name, phone,
                           today_date, current_time))
            conn.commit()
            st.success(
                f'Welcome {name}! You have successfully checked in at {current_time} on {today_date}.')

entry()

footer()

cursor.close()
conn.close()
