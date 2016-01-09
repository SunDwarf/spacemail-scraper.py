import requests
import threading
from bs4 import BeautifulSoup

import sys

from dateutil import parser
from sqlalchemy import create_engine, Column, Integer, String, Table, DateTime, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine('postgresql://postgres@localhost:5432/spacemail')
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)



Base = declarative_base()


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(String)
    date = Column(DateTime)


def main(thread_id: int):
    # Postgres due to threads

    session = Session()
    sess = requests.Session()
    sess.headers = {
        "User-Agent": "SpaceMail Scraper v1.0 - https://github.com/SunDwarf/spacemail-scraper.py",
        "Referer": "http://space.galaxybuster.net/go.php",
        "Origin": "http://space.galaxybuster.net"}
    while True:
        print("[Thread-{}] Retrieving message...".format(thread_id))
        # Get header
        try:
            msg_header = sess.get("http://space.galaxybuster.net/lib/get.php")
        except:
            print("[Thread-{}] - Failed to get new message".format(thread_id))
            continue
        # Parse it
        soup = BeautifulSoup(msg_header.content, "html.parser")
        # Get all divs
        divs = soup.find_all("div")
        # If not null
        if divs:
            # Get ID
            mid = divs[0]["data-id"]
            print("[Thread-{}] - ID:".format(thread_id), mid)

            if not session.query(exists().where(Post.id == mid)).scalar():
                # Get message data
                msg = sess.post("http://space.galaxybuster.net/lib/view.php", data={"id": mid})
                # Parse it
                msg_soup = BeautifulSoup(msg.json()[0], "html.parser")
                subject = msg_soup.find(id="msgSubject")
                sender = msg_soup.find(id="msgSender")
                body = msg_soup.find(id="msgBody")
                date = msg_soup.find(id="msgDate")
                print("[Thread-{}] - Subject:".format(thread_id), subject.getText())
                print("[Thread-{}] - From:".format(thread_id), sender.getText())
                print("[Thread-{}] - Body:".format(thread_id), body.getText())
                print("[Thread-{}] - Date:".format(thread_id), date.getText(),
                      "Formatted:", parser.parse(date.getText()))
                p = Post(id=mid, sender=sender.getText(), body=body.getText(), subject=subject.getText(),
                         date=parser.parse(date.getText()))
                session.add(p)
            else:
                print("[Thread-{}] - Already seen before.".format(thread_id))

        else:
            print("[Thread-{}] - Returned empty.".format(thread_id))
        session.commit()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        threads = int(sys.argv[1])
    else:
        threads = 16
    Base.metadata.create_all(engine)
    print("Starting {} threads...".format(threads))
    for i in range(0, threads):
        th = threading.Thread(target=main, args=(i,))
        th.start()
