import os
import numpy as np
import spacemail
import pandas as pd
from pandas import Series

# Fix sizes
from matplotlib import rcParams

from matplotlib import pyplot as plt

rcParams.update({'figure.autolayout': True})


def plot_dates_all():
    print("Plotting year/month posts...")
    df = pd.read_sql("SELECT date FROM post;", spacemail.engine)

    # Set date type
    df.date = df.date.astype("datetime64")

    # Group and plot
    pl = df.groupby([df.date.dt.year, df.date.dt.month]) \
        .count() \
        .plot(kind="bar", title="Posts grouped by year and month")

    # Set labels
    pl.set_xlabel("Dates (Year, Month)")
    pl.set_ylabel("Frequency")

    # Save
    fig = pl.get_figure()
    fig.savefig("plots/dates_all.png")


def plot_dates_no_spikes():
    print("Plotting year/month posts with no spikes...")
    df = pd.read_sql("SELECT date FROM post WHERE date(date) NOT BETWEEN date('2014-06-01') AND date('2014-08-01');",
                     spacemail.engine)

    # Set date type
    df.date = df.date.astype("datetime64")

    # Group and plot
    pl = df.groupby([df.date.dt.year, df.date.dt.month]) \
        .count() \
        .plot(kind="bar", title="Posts grouped by year and month")

    # Set labels
    pl.set_xlabel("Dates (Year, Month)")
    pl.set_ylabel("Frequency")

    # Save
    fig = pl.get_figure()
    fig.savefig("plots/dates_all_nospikes.png")


def plot_dates_jul_2014():
    print("Plotting dates for July 2014...")
    df = pd.read_sql("SELECT date FROM post WHERE date(date) BETWEEN date('2014-07-01') AND date('2014-07-31');",
                     spacemail.engine)

    # Set date type
    df.date = df.date.astype("datetime64")

    # Group and plot
    pl = df.groupby(df.date.dt.day) \
        .count() \
        .plot(kind="bar", title="Posts in July 2014 by Day")


    # Set labels
    pl.set_xlabel("Day of Month")
    pl.set_ylabel("Frequency")

    # Save
    fig = pl.get_figure()
    fig.savefig("plots/dates_jul_2014.png")

    plt.clf()
    plt.cla()


def plot_sad_grouped_graphs():
    print("Plotting words/frequency...")

    d = {"suicide": spacemail.session.query(spacemail.Post)
        .filter((spacemail.Post.body.ilike("%suicide%"))
                | (spacemail.Post.subject.ilike("%suicide%"))).count(),
         "abuse": spacemail.session.query(spacemail.Post)
             .filter((spacemail.Post.body.ilike("%abuse%"))
                     | (spacemail.Post.subject.ilike("%abuse%"))).count(),
         "depression": spacemail.session.query(spacemail.Post)
             .filter((spacemail.Post.body.ilike("%depress%"))
                     | (spacemail.Post.subject.ilike("%depress%"))).count(),
         "rape": spacemail.session.query(spacemail.Post)
             .filter((spacemail.Post.body.ilike("%rape%"))
                     | (spacemail.Post.subject.ilike("%rape%"))).count(),
         "kill": spacemail.session.query(spacemail.Post)
             .filter((spacemail.Post.body.ilike("%kill%"))
                     | (spacemail.Post.subject.ilike("%kill%"))).count(),
         "lonely": spacemail.session.query(spacemail.Post)
             .filter((spacemail.Post.body.ilike("%lonely%"))
                     | (spacemail.Post.subject.ilike("%lonely%"))).count(),
         "alone": spacemail.session.query(spacemail.Post)
             .filter((spacemail.Post.body.ilike("%alone%"))
                     | (spacemail.Post.subject.ilike("%alone%"))).count()}


    # Use matplotlib directly this time
    X = np.arange(len(d.keys()))

    # Plot bar
    plt.bar(X, d.values(), align='center', width=0.5, color='r')
    # Assign ticks
    plt.xticks(X, d.keys())

    # Set labels
    plt.xlabel("Word")
    plt.ylabel("Count")

    # Set title
    plt.title("Interesting word counts")

    # Set ymax
    ymax = max(d.values()) + 100
    plt.ylim(0, ymax)

    # Save it
    plt.savefig("plots/sad_words.png")

    # Cleanup
    plt.clf()
    plt.cla()

def plot_dumbass():
    print("Plotting dumbass words/frequency...")

    d = {"skype": spacemail.session.query(spacemail.Post)
         .filter((spacemail.Post.body.ilike("%skype%"))
                | (spacemail.Post.subject.ilike("%skype%"))).count(),
         "kik": spacemail.session.query(spacemail.Post)
         .filter((spacemail.Post.body.ilike("% kik %"))
                | (spacemail.Post.subject.ilike("% kik %"))).count(),
         "tumblr": spacemail.session.query(spacemail.Post)
         .filter((spacemail.Post.body.ilike("%tumblr%"))
                | (spacemail.Post.subject.ilike("%tumblr%"))).count()}


    # Use matplotlib directly this time
    X = np.arange(len(d.keys()))

    # Plot bar
    plt.bar(X, d.values(), align='center', width=0.5, color='r')
    # Assign ticks
    plt.xticks(X, d.keys())

    # Set labels
    plt.xlabel("Word")
    plt.ylabel("Count")

    # Set title
    plt.title("Interesting word counts")

    # Set ymax
    ymax = max(d.values()) + 100
    plt.ylim(0, ymax)

    # Save it
    plt.savefig("plots/dumbasses.png")

    # Cleanup
    plt.clf()
    plt.cla()


if __name__ == '__main__':

    if not os.path.exists("plots"):
        os.makedirs("plots")

    plot_dates_all()
    plot_dates_no_spikes()
    plot_dates_jul_2014()
    plot_sad_grouped_graphs()
    plot_dumbass()
    print("Plotted all.")
