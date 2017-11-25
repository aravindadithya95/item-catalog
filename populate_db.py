from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

# Connect to the database
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine

# Create a database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


def populate_db():
    # Create users
    user1 = User(name="John Doe",
                email="johndoe@email.com",
                picture="http://voice4thought.org/wp-content/uploads/2016/08/default1.jpg")
    session.add(user1)
    session.commit()

    user2 = User(name="Jane Doe",
                email="janedoe@email.com",
                picture="http://voice4thought.org/wp-content/uploads/2016/08/default1.jpg")
    session.add(user2)
    session.commit()


    # Add categories
    soccer = Category(name="Soccer")
    session.add(soccer)
    session.commit()

    hockey = Category(name="Hockey")
    session.add(hockey)
    session.commit()

    cricket = Category(name="Cricket")
    session.add(cricket)
    session.commit()


    # Add items
    # Soccer
    soccer_ball = Item(
        name="Soccer Ball",
        description=(
            "A football, soccer ball, or association football ball is the ball "
            "used in the sport of association football."
        ),
        category_id=1,
        user_id=1
    )
    session.add(soccer_ball)
    session.commit()

    shinguard = Item(
        name="Shinguard",
        description=(
            "A shin guard or shin pad is a piece of equipment worn on the front of "
            "a player's shin to protect them from injury."
        ),
        category_id=1,
        user_id=1
    )
    session.add(shinguard)
    session.commit()

    soccer_cleats = Item(
        name="Soccer Cleats",
        description=(
            "Football boots, called cleats or soccer shoes in North America, are "
            "an item of footwear worn when playing football. Those designed for "
            "grass pitches have studs on the outsole to aid grip."
        ),
        category_id=1,
        user_id=1
    )
    session.add(soccer_cleats)
    session.commit()

    soccer_jersey = Item(
        name="Jersey",
        description=(
            "A jersey is an item of knitted clothing, traditionally in wool or "
            "cotton, with sleeves, worn as a pullover, as it does not open at the "
            "front, unlike a cardigan."
        ),
        category_id=1,
        user_id=2
    )
    session.add(soccer_jersey)
    session.commit()

    # Hockey
    hockey_stick = Item(
        name="Hockey Stick",
        description=(
            "A hockey stick is a piece of equipment used by the players in most "
            "forms of hockey to move the ball or puck."
        ),
        category_id=2,
        user_id=1
    )
    session.add(hockey_stick)
    session.commit()

    hockey_puck = Item(
        name="Puck",
        description=(
            "A hockey puck is a disk made of vulcanized rubber that serves the "
            "same functions in various games as a ball does in ball games."
        ),
        category_id=2,
        user_id=2
    )
    session.add(hockey_puck)
    session.commit()

    hockey_gloves = Item(
        name="Gloves",
        description=(
            "There are three styles of gloves worn by ice hockey players. Skaters "
            "wear similar gloves on each hand, while goaltenders wear gloves of "
            "different types on each hand."
        ),
        category_id=2,
        user_id=1
    )
    session.add(hockey_gloves)
    session.commit()

    # Cricket
    cricket_bat = Item(
        name="Bat",
        description=(
            "A cricket bat is a specialised piece of equipment used by batsmen in "
            "the sport of cricket to hit the ball, typically consisting of a cane "
            "handle attached to a flat-fronted willow-wood blade."
        ),
        category_id=3,
        user_id=1
    )
    session.add(cricket_bat)
    session.commit()

    cricket_ball = Item(
        name="Cricket Ball",
        description=(
            "A cricket ball is a hard, solid ball used to play cricket. A cricket "
            "ball consists of cork covered by leather, and manufacture is "
            "regulated by cricket law at first-class level."
        ),
        category_id=3,
        user_id=2
    )
    session.add(cricket_ball)
    session.commit()

    cricket_batting_gloves = Item(
        name="Batting Gloves",
        description=(
            "Batting gloves are a component in Bat-and-ball games sportswear. "
            "The glove covers one or both hands of a batter, providing comfort, "
            "prevention of blisters, warmth, improved grip, and shock absorption "
            "when hitting the ball."
        ),
        category_id=3,
        user_id=2
    )
    session.add(cricket_batting_gloves)
    session.commit()

    cricket_batting_pads= Item(
        name="Batting Pads",
        description=(
            "Pads (also called leg guards) are protective equipment used by "
            "batters in the sport of cricket They serve to protect the legs from "
            "impact by a hard ball at high speed which could otherwise cause "
            "injuries to the lower legs."
        ),
        category_id=3,
        user_id=2
    )
    session.add(cricket_batting_pads)
    session.commit()

    cricket_helmet = Item(
        name="Helmet",
        description=(
            "In the sport of cricket, batsmen often wear a helmet to protect "
            "themselves from injury or concussion by the cricket ball, which is "
            "very hard and can be bowled to them at speeds over 90 miles per hour "
            "(140 km/h)."
        ),
        category_id=3,
        user_id=2
    )
    session.add(cricket_helmet)
    session.commit()


if __name__ == '__main__':
    populate_db()
