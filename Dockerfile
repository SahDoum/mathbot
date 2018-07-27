FROM tiangolo/uwsgi-nginx-flask:python3.6

EXPOSE 443

COPY . /app
COPY nginx_ssl.conf /etc/nginx/conf.d/
RUN pip install --no-cache-dir -r requirements.txt