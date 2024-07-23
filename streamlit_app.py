import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import gspread
from streamlit_authenticator.utilities.hasher import Hasher



# Authentication
authenticator = stauth.Authenticate(
    {
        "usernames": {
            st.secrets["login_user"]: {
                "email": "test@test.com",
                "name": st.secrets["login_display_name"],
                "password": Hasher([st.secrets["login_password"]]).generate()[0],
            }
        }
    },
    "jk_lookup",
    "jk_lookup",
    30,
)
 
 
 
@st.cache_data(ttl=600)
def get_dataframe():
    gc = gspread.service_account(filename='jksearch-6cb382d7aa47.json')
    sh = gc.open_by_key('1Dc_PuqpfiikinpPBlnsP1HLStQAIxy5A-_2QhvHbRWA')
    worksheet = sh.sheet1
    df = pd.DataFrame(worksheet.get_all_records(expected_headers=[
    "รหัส",
    "ชื่อสินค้า(Item_Description_JKSUPPLYANDMACHINERY)",
    "บรรจุ(Packaging)",
    "หน่วย",
    "ราคาตั้ง",
    "ส่วนลด",
    "ภาษี",
    "หมายเหตุ/อื่นๆ",
    "วันที่อัพเดทราคา",
    "สถานะ(วันที่อัพเดท-Status)",
    "Blanks1",
    "Blanks2",
    ]))
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
 
    df = df[~df["ชื่อสินค้า(Item_Description_JKSUPPLYANDMACHINERY)"].isna()]
    return df[df["ชื่อสินค้า(Item_Description_JKSUPPLYANDMACHINERY)"].str.contains(user_text_input, regex=False)]
 
name, authentication_status, username = authenticator.login()

 
if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    st.dataframe(filter_dataframe(), use_container_width=True)
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')