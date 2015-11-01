import requests
from bs4 import BeautifulSoup

from dateutil import parser
from sqlalchemy import create_engine, Column, Integer, String, Table, DateTime, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///spacemail.db')
session = sessionmaker(bind=engine)()

Base = declarative_base()


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(String)
    date = Column(DateTime)



import shutil

width = shutil.get_terminal_size((80, 20)).columns


def main():
    sess = requests.Session()
    sess.headers = {
        "User-Agent": "SpaceMail Scraper v1.0 - https://github.com/SunDwarf/spacemail-scraper.py",
        "Referer": "http://space.galaxybuster.net/go.php",
        "Origin": "http://space.galaxybuster.net"}
    while True:
        print("Retrieving message...")
        # Get header
        msg_header = sess.get("http://space.galaxybuster.net/lib/get.php")
        # Parse it
        soup = BeautifulSoup(msg_header.content, "html.parser")
        # Get all divs
        divs = soup.find_all("div")
        # If not null
        if divs:
            # Get ID
            mid = divs[0]["data-id"]
            print("ID:", mid)

            if not session.query(exists().where(Post.id == mid)).scalar():
                # Get message data
                msg = sess.post("http://space.galaxybuster.net/lib/view.php", data={"id": mid})
                # Parse it
                msg_soup = BeautifulSoup(msg.json()[0], "html.parser")
                subject = msg_soup.find(id="msgSubject")
                sender = msg_soup.find(id="msgSender")
                body = msg_soup.find(id="msgBody")
                date = msg_soup.find(id="msgDate")
                print("Subject:", subject.getText())
                print("From:", sender.getText())
                print("Body:", body.getText())
                print("Date:", date.getText(), "Formatted:", parser.parse(date.getText()))
                p = Post(id=mid, sender=sender.getText(), body=body.getText(), subject=subject.getText(),
                         date=parser.parse(date.getText()))
                session.add(p)
            else:
                print("Already seen before.")

        else:
            print("Returned empty.")
        session.commit()
        print("=" * width)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    main()
