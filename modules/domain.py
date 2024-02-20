from sqlalchemy import (
    insert,
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Boolean,
    LargeBinary,
    Integer,
    select,
    column,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# create table with 
#from sqlalchemy import create_engine
# engine = create_engine('sqlite:///example.db')
# Base = declarative_base()
# Base.metadata.create_all(engine)

# https://www.slingacademy.com/article/sqlalchemy-how-to-create-a-table/

class BuildClubMembers(Base):
    __tablename__ = 'build_club_members'
    id = Column("id", String(256), primary_key=True),
    name = Column("name", String(256)),
    linkedin_url = Column("linkedin_url", String(512)),
    skill_1 = Column("skill_1", String(128)),
    skill_2 = Column("skill_2", String(128)),
    skill_3 = Column("skill_3", String(128)),
    skill_4 = Column("skill_4", String(128)),
    based_in_sydney = Column("based_in_sydney", String(256)),
    member_location = Column("member_location", String(256)),
    member_acceptance_in_club = Column("member_acceptance_in_club", Boolean()),
    ai_builder_linkedin_badge = Column("ai_builder_linkedin_badge", String(256)),
    referee = Column("referee", String(256)),
    referrer_name = Column("referrer_name", String(256)),
    assignee = Column("assignee", String(256)),
    status = Column("status", String(256)),
    phone_number = Column("phone_number", String(256)),
    are_you_building_in_squad = Column("are_you_building_in_squad", String(1024)),
    best_time_for_build_sessions = Column("best_time_for_build_sessions", String(1024)),
    keen_for_ai_meetup = Column("keen_for_ai_meetup", String(128)),
    expectation_from_joining_club = Column("expectation_from_joining_club", String(4096)),
    build_project = Column("build_project", String(4096)),
    past_work = Column("past_work", String(4096)),
    profile_picture = Column("profile_picture", LargeBinary())