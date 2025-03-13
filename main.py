import streamlit as st
import os
from pathlib import Path
import base64

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{Path(bin_file).name}">{file_label}</a>'
    return href

py_files = [f for f in os.listdir("scripts") if f.endswith(".py")]
video_files = [f for f in os.listdir("videos") if f.endswith(".mov")]
image_files = [f for f in os.listdir("images") if f.endswith(".jpg") or f.endswith(".png")]
fixed_image_files = [f for f in os.listdir("fixed_images") if f.endswith(".jpg") or f.endswith(".png")]
cad_files = [f for f in os.listdir("cad_files") if f.endswith(".stp") or f.endswith(".stl") or f.endswith(".zip")]
cad_images = [f for f in os.listdir("images") if f.lower().endswith(('.png', '.jpg', '.jpeg'))]


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "🚀 Atlas V-401 Rocket: CAD creation", "🐍 Python Scripts", "✈ Scratch-Built RC Drone"])

if page == "🏠 Home":
    st.title("Welcome to My Portfolio! 🛩️")
    st.write("This portfolio showcases a selection of personal and school projects that I have completed over the years. "
    "Use the **navigation bar** on the left to explore a project further.")
    st.markdown("---")
    st.write("**Phone Number**: 516-497-0677")
    st.write("**Email Address**: patrick.hillgarnder@gmail.com")
    st.write("**LinkedIn**: https://www.linkedin.com/in/patrick-hillgardner-854868263/")
    with open("assets/resume_v5.pdf", "rb") as file:
        resume_bytes = file.read()

    st.download_button(
    label="📄 **Download My Resume**",
    data=resume_bytes,
    file_name="Patrick_Hillgardner_Resume.pdf",
    mime="application/pdf"
)
    st.write(" ")
    st.image("headshot.jpeg", width=250)
    st.subheader("About the Author")
    st.write("My name is Patrick Hillgardner and I am a senior in aerospace engineering at the University of Illinois at Urbana-Champaign. "
    "My interests include propulsion, hypersonics, and engineering systems/aircraft design. "
    "My dream has been to serve the aerospace industry since I was very young, and I am determined to make that dream a reality!")

elif page == "🚀 Atlas V-401 Rocket: CAD creation":
    st.title("🚀 Atlas V-401 Rocket: CAD creation")
    st.write("This project is a to-scale CAD model of the Atlas V-401 rocket created using Siemens NX. ")
    st.info("🚧 **Interactive CAD Viewer Coming Soon!** 🚧\n\n "
        "Due to the size and complexity of this model, a web-based viewer is currently under development. "
        "You can download the CAD files below to view the model locally. "
        "The .stp file is more compatible with most softwares, whereas the .zip file contains the original NX file and all its components, including the RD-180 engine.")
    st.markdown("---")

    # Display images neatly in a grid
    cols = st.columns(2)
    for idx, img in enumerate(cad_images):
        with cols[idx % 2]:
            st.image(f"images/{img}", use_column_width=True,)
            st.markdown(f"<h8 style='text-align: center;'> CAD model render.", unsafe_allow_html=True)

    cols2 = st.columns(2)
    for idx2, img2 in enumerate(fixed_image_files):
        with cols[idx2 % 2]:
            st.image(f"fixed_images/{img2}", use_column_width=True)
    st.markdown(f"<h8 style='text-align: center;'> Real (left) vs. CAD model (right) exploded view.", unsafe_allow_html=True)
    
    st.markdown("---")

    st.subheader("Download CAD Files")

    for cad_file in cad_files:
        with open(f"cad_files/{cad_file}", "rb") as file2:
            file_bytes = file2.read()
        st.download_button(
            label=f"⬇️ Download {cad_file}",
            data=file_bytes,  # pass the bytes, not the file object
            file_name=cad_file,
            mime="application/octet-stream"
        )
    

elif page == "🐍 Python Scripts":
    st.title("🐍 Python Scripts")
    st.write("This page showcaases the Python scripts that I have created over the years.")
    st.write("**naca_4series_geoplotter.py** :  Python script that takes a user-entered 4-digit NACA airfoil and plots the normalized airfoil coordinates.")
    st.write("**hess_smith_panel_method.py** :  Hess-Smith 2D panel method code that takes a defined NACA airfoil anfd angle of attack and computes the lift coefficient, drag coefficient, moment coefficient, and plots the pressure coefficient distribution.")
    st.write("**hess_smith_panel_method_uinputs.py** :  Slightly modified version of the Hess-Smith panel method code that takes a user-entered 4-digit NACA airfoil, angle of attack, and number of panels and returns the resulting lift coefficient, drag coefficient, moment coefficient, and plots the pressure coefficient distribution.")
    selected_script = st.selectbox("Select a script:", py_files)
    if selected_script:
        with open(f"scripts/{selected_script}", "r") as file:
            code = file.read()
        with st.expander("📜 View Code (Click to Expand)"):
            st.code(code, language='python')
        st.markdown(get_binary_file_downloader_html(f"scripts/{selected_script}", "⬇️ Download Script"), unsafe_allow_html=True)

elif page == "✈ Scratch-Built RC Drone":
    st.title("✈ Scratch-Built RC Drone")
    st.write("In early January 2025, I created a fully functional remote control drone made entirely out of foam boards- "
    "the control surfaces and motor functions are shown in this video.")
    for video in video_files:
        st.video(f"videos/{video}")

