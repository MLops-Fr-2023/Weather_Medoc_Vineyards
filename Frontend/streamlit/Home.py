import os
import streamlit as st
import libs.tools as tools

tools.set_page_config()

images_path = tools.get_images_path()


def display_welcome_message():
    st.markdown("""---""")
    st.subheader("Here you are on the main page of our Vineyard Weather Forecast app!")
    st.write("")
    st.subheader("**Feel free to explore and use the capabilities of IA and transformers.**")
    st.write(' ')
    st.write(' ')
    subheader_text = "Please feel free to thumbs up our "
    github_url = "[github](https://github.com/MLops-Fr-2023/Weather_Medoc_Vineyards)"
    st.subheader(f'{subheader_text}{github_url}')
    st.markdown("""---""")


def main():
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        st.title('Welcome to :violet[Weather Forecast] 🍷')
        st.title(" ")

    with st.container():
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            display_welcome_message()

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(images_path + "wine.gif", width=400)


if __name__ == '__main__':
    main()

tools.display_side_bar()
