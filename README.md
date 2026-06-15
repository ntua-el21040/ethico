# THUFIR - A VIrtual Ethics Advisor
**THUFIR** is a hybrid machine ethics system that helps users navigate moral dilemmas.

It integrates an LLM to converse with users and a mdodified version of the HERA Python library for moral reasoning.

THUFIR is currently not publicly available as a web-app, but can be run locally by cloning the repo and providing access to an LLM through API keys.


## Setup
The system requires the GNU-Linux operating system or using WSL on Windows. 

1. Clone the repo
2. Create and activate a Python virtual environment.
3. Create a `.env` file with your Anthropic or Groq keys 
4. Install dependencies: `pip install -r requirements.txt`
5. Set-up HERA: `cd ethics_engine && python setup.py install`
6. Run the app: `python app.py`