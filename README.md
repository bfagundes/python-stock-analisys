Under construction.

To build the Environment inside project-root\.env
pip install virtualenv
virtualenv .env
source .env/Scripts/activate
pip install -r requirements.txt
pip list

To run
`.env/Scripts/activate`
`streamlit run code/app.py`
Access `http://localhost:8501`