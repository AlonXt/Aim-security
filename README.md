# Aim-security
Home task for Engineering position

### Server setup:
1. create venv: "python3 -m venv .venv" using python 3.10.11
2. run "pipenv install"
3. add the following env vars:
   * UVICORN_IP=localhost;
   * UVICORN_PORT=8000;
   * OPENAI_API_KEY=<YOUR_API_KEY>;
   * OPENAI_URL=<URL>;
4. run - run_server.py 
5. go to http://localhost:8000/docs and enjoy!

I would probably use uv https://github.com/astral-sh/uv or Poetry, but I'll use requirements.txt here 