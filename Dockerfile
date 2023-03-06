FROM python:latest

RUN apt update -y
RUN apt install -y cron vim locales supervisor

RUN localedef -f UTF-8 -i ko_KR ko_KR.utf8
ENV LANG=ko_KR.utf8
ENV LC_ALL=ko_KR.utf8

RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

COPY supervisor-cron.conf /etc/supervisor/conf.d
COPY cronjob /etc/cron.d/cronjob
RUN chmod +x /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

RUN mkdir -p /python/danawa/product
RUN pip install BeautifulSoup4 urlopen redis

WORKDIR /python/danawa
COPY DanawaProduct.py /python/danawa
COPY loop.sh /python/danawa
RUN chmod -R +x /python/danawa
COPY entrypoint.sh /python/danawa

ENTRYPOINT ["bash", "/python/danawa/entrypoint.sh"]
