# Aim-security
Home task for Engineering position

### Server setup:
1. create venv: "python3 -m venv .venv" using python 3.10.11
2. run "pip install -r requirements.txt"
3. add the following env vars:
   * UVICORN_IP=localhost;
   * UVICORN_PORT=8000;
   * OPENAI_API_KEY=<YOUR_API_KEY>;
   * OPENAI_URL=<URL>;
4. run - run_server.py 
5. go to http://localhost:8000/docs and enjoy!

I would probably use uv https://github.com/astral-sh/uv or Poetry, but I'll use requirements.txt here

### Tradeoffs

Which Model should I use?

- Should it be fast or accurate?

Which DB should I use?

- At first I did it with in-memory cache and then changed to presistent sqlite
- Maybe it is better to use NoSql

How should I handle failure of OpenAI response?

- Retry which takes more time Or block and let the prompt to be sent again?