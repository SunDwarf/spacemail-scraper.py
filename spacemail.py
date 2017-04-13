import sys
import threading

import os
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from json import JSONDecodeError
from sqlalchemy import create_engine, Column, Integer, String, DateTime, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres@localhost:5432/spacemail')
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()

DEBUG = os.environ.get("SP_DEBUG", "true") != "false"


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(String)
    date = Column(DateTime)


def main(thread_id: int, debug: bool = True):
    # Postgres due to threads

    session = Session()
    sess = requests.Session()
    sess.headers = {
        "User-Agent": "SpaceMail Scraper v1.0 - https://github.com/SunDwarf/spacemail-scraper.py",
        "Referer": "http://space.galaxybuster.net/go.php",
        "Origin": "http://space.galaxybuster.net"}
    while True:
        debug and print("[Thread-{}] Retrieving message...".format(thread_id))
        # Get header
        try:
            msg_header = sess.get("http://space.galaxybuster.net/lib/get.php")
        except:
            debug and print("[Thread-{}] - Failed to get new message".format(thread_id))
            continue
        # Parse it
        soup = BeautifulSoup(msg_header.content, "html.parser")
        # Get all divs
        divs = soup.find_all("div")
        # If not null
        if divs:
            # Get ID
            mid = divs[0]["data-id"]
            debug and print("[Thread-{}] - ID:".format(thread_id), mid)

            if not session.query(exists().where(Post.id == mid)).scalar():
                # Get message data
                try:
                    msg = sess.post("http://space.galaxybuster.net/lib/view.php", data={"id": mid})
                except:
                    debug and print("Thread-{}] -".format(thread_id), "ID: {} -".format(mid),
                                    "Error fetching new post body.")

                try:
                    data = msg.json()[0]
                except JSONDecodeError:
                    debug and print("[Thread-{}] - ID: {} - Error decoding body ({})"
                                    .format(thread_id, mid, msg.text))
                    continue

                # Parse it
                try:
                    msg_soup = BeautifulSoup(data, "html.parser")
                    subject = msg_soup.find(id="msgSubject")
                    sender = msg_soup.find(id="msgSender")
                    body = msg_soup.find(id="msgBody")
                    date = msg_soup.find(id="msgDate")
                    debug and print("[Thread-{}] - Subject:".format(thread_id), subject.getText())
                    debug and print("[Thread-{}] - From:".format(thread_id), sender.getText())
                    debug and print("[Thread-{}] - Body:".format(thread_id), body.getText())
                    debug and print("[Thread-{}] - Date:".format(thread_id), date.getText(),
                                    "Formatted:", parser.parse(date.getText()))
                    p = Post(id=mid, sender=sender.getText(), body=body.getText(),
                             subject=subject.getText(),
                             date=parser.parse(date.getText()))
                    session.add(p)
                except:
                    print("[Thread-{}] -".format(thread_id), "Bad HTML body returned.")
            else:
                debug and print("[Thread-{}] - Already seen before.".format(thread_id))

        else:
            debug and print("[Thread-{}] - Returned empty.".format(thread_id))
        session.commit()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        threads = int(sys.argv[1])
    else:
        threads = 16
    Base.metadata.create_all(engine)
    print("Starting {} threads...".format(threads))
    for i in range(0, threads):
        th = threading.Thread(target=main, args=(i, DEBUG))
        th.start()
