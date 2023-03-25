FROM python:3.11
RUN pip install virtualenv
WORKDIR aiohttp_adv
COPY requirements.txt /aiohttp_adv/requirements.txt
RUN pip install --no-cache-dir -r /aiohttp_adv/requirements.txt
COPY . /aiohttp_adv
EXPOSE 8080
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8080"]