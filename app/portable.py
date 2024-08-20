import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Define headers for the Googlebot user agent
googlebot_headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/W.X.Y.Z Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}

# Function to add a base tag to the HTML content
def add_base_tag(html_content, original_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_url = urlparse(original_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    
    if parsed_url.path and not parsed_url.path.endswith('/'):
        base_url = urljoin(base_url, parsed_url.path.rsplit('/', 1)[0] + '/')
    base_tag = soup.find('base')
    
    if not base_tag:
        new_base_tag = soup.new_tag('base', href=base_url)
        if soup.head:
            soup.head.insert(0, new_base_tag)
        else:
            head_tag = soup.new_tag('head')
            head_tag.insert(0, new_base_tag)
            soup.insert(0, head_tag)
    
    return str(soup)

# Function to bypass paywall by fetching content as Googlebot
def bypass_paywall(url):
    if url.startswith("http"):
        response = requests.get(url, headers=googlebot_headers)
        response.encoding = response.apparent_encoding
        return add_base_tag(response.text, response.url)

    try:
        return bypass_paywall("https://" + url)
    except requests.exceptions.RequestException:
        return bypass_paywall("http://" + url)

# Streamlit App layout
st.title("13ft Ladder - Paywall Bypass Tool")

# Dark Mode Toggle
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False

if st.checkbox("Toggle Dark Mode"):
    st.session_state['dark_mode'] = not st.session_state['dark_mode']

# Apply dark mode styles if enabled
if st.session_state['dark_mode']:
    st.markdown(
        """
        <style>
        body { background-color: #333; color: #FFF; }
        .stTextInput>div>input { background-color: #555; color: #FFF; }
        .stButton>button { background-color: #9b30ff; color: #FFF; }
        </style>
        """, unsafe_allow_html=True
    )

# Input form
link = st.text_input("Link of the website you want to remove paywall for:", "")

if st.button("Submit"):
    if link:
        try:
            article_html = bypass_paywall(link)
            st.container(article_html, unsafe_allow_html=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching the article: {e}")
    else:
        st.warning("Please enter a valid URL.")