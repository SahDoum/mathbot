FROM tiangolo/uwsgi-nginx-flask:python3.6

EXPOSE 443

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app
COPY nginx_ssl.conf /etc/nginx/conf.d/