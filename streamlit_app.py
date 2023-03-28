# streamlit_app.py
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

# Authentication
authenticator = stauth.Authenticate(
    {
        "usernames": {
            st.secrets["login_user"]: {
                "email": "test@test.com",
                "name": st.secrets["login_display_name"],
                "password": stauth.Hasher([st.secrets["login_password"]]).generate()[0],
            }
        }
    },
    "jk_lookup",
    "jk_lookup",
    30,
)

conn = connect(credentials=credentials)


@st.cache_data(ttl=600)
def get_dataframe():
    rows = conn.execute(
        f"""SELECT 
                    "รหัส" AS STRING,
                    "ชื่อสินค้า" AS STRING,
                    "หมายเหตุ/อื่นๆ" AS STRING,
                    "บรรจุ" AS STRING,
                    "ราคาตั้ง" AS STRING,
                    "ส่วนลด" AS STRING,
                    "ภาษี" AS STRING,
                    "วันที่อัพเดท" AS STRING,
                    "สถานะ" AS STRING
                FROM "{st.secrets["private_gsheets_url"]}"
                """,
        headers=1,
    )
    rows = rows.fetchall()

    df = pd.DataFrame(
        rows,
        columns=[
            "รหัส",
            "ชื่อสินค้า",
            "หมายเหตุ/อื่นๆ",
            "บรรจุ",
            "ราคาตั้ง",
            "ส่วนลด",
            "ภาษี",
            "วันที่อัพเดท",
            "สถานะ",
        ],
    )
    return df


def filter_dataframe():
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modification_container = st.container()

    with modification_container:
        column = ""
        left, right = st.columns((1, 20))

        user_text_input = right.text_input(
            f"Substring or regex in {column}",
        )

        df = get_dataframe()

    return df[df["ชื่อสินค้า"].str.contains(user_text_input, regex=False)]

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    st.dataframe(filter_dataframe(), use_container_width=True)
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

