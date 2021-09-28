import random
from datetime import datetime, timedelta
from random import randrange

from flask import current_app

from app import Config
from app.default.db_helpers import complete_last_activity, machine_schedule_active
from app.default.models import Machine, Job, Activity, ActivityCode, DemoSettings
from app.extensions import db
from app.login.models import User, UserSession


def create_new_demo_user(username, machine, simulation_datetime=None):
    if not simulation_datetime:
        simulation_datetime = datetime.now()
    user = User(username=username)
    user.set_password("secret_bot_password!!!")
    db.session.add(user)
    db.session.commit()
    user_session = UserSession(user_id=user.id,
                               machine_id=machine.id,
                               device_ip="",
                               timestamp_login=int(simulation_datetime.timestamp()),
                               active=True)
    db.session.add(user_session)
    db.session.commit()
    return user


def end_job(job, machine, simulation_datetime=None):
    current_app.logger.debug(f"ending job")
    if not simulation_datetime:
        simulation_datetime = datetime.now()
    job.end_time = simulation_datetime.timestamp()
    job.active = None
    complete_last_activity(machine_id=machine.id, timestamp_end=simulation_datetime.timestamp())
    db.session.commit()


def start_new_job(machine, user, simulation_datetime=None):
    # Run for the current time if no datetime given
    if not simulation_datetime:
        simulation_datetime = datetime.now()
    current_app.logger.debug(f"Starting new job")
    session = UserSession.query.filter_by(user_id=user.id, active=True).first()
    job = Job(start_time=simulation_datetime.timestamp(),
              user_id=user.id,
              wo_number=random.randint(1, 100000),
              planned_run_time=random.randint(1, 1000),
              planned_quantity=random.randint(1, 100),
              machine_id=machine.id,
              active=True,
              user_session_id=session.id)
    db.session.add(job)
    #db.session.commit()


def change_activity(machine, job, user, simulation_datetime=None):
    current_app.logger.debug(f"changing activity")
    # Run for the current time if no datetime given
    if not simulation_datetime:
        simulation_datetime = datetime.now()
    complete_last_activity(machine_id=machine.id, timestamp_end=simulation_datetime.timestamp())
    chance_the_activity_is_uptime = 0.8
    if random.random() < chance_the_activity_is_uptime:
        new_activity = Activity(machine_id=machine.id,
                                timestamp_start=simulation_datetime.timestamp(),
                                machine_state=1,
                                activity_code_id=Config.UPTIME_CODE_ID,
                                job_id=job.id,
                                user_id=user.id)
    else:
        # otherwise the activity is downtime
        new_activity = Activity(machine_id=machine.id,
                                timestamp_start=simulation_datetime.timestamp(),
                                machine_state=0,
                                activity_code_id=randrange(2, len(ActivityCode.query.all())),
                                job_id=job.id,
                                user_id=user.id)
    db.session.add(new_activity)
    #db.session.commit()


def simulate_machines(simulation_datetime=None):
    if not Config.DEMO_MODE:
        current_app.logger.warning("Fake data being created when app is not in DEMO_MODE")
    # Run for the current time if no datetime given
    if not simulation_datetime:
        simulation_datetime = datetime.now()
    for machine in Machine.query.all():
        chance_to_skip_simulation = 0.90
        if random.random() < chance_to_skip_simulation:
            current_app.logger.debug(f"skipping machine {machine.id} simulation")
            continue
        current_app.logger.debug(f"simulating machine action for machine {machine.id}")
        # Get the machine's user by using the machine id as the index on a fake names list. Create it if it does not exist
        username = names[machine.id]
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = create_new_demo_user(username, machine)
            start_new_job(machine, user)
        # Don't run jobs if the machine is not scheduled to be running
        if not machine_schedule_active(machine, dt=simulation_datetime):
            if user.has_job():
                current_job = Job.query.filter_by(user_id=user.id, active=True).first()
                end_job(current_job, machine, simulation_datetime)
            else:
                continue
        if user.has_job():
            current_job = Job.query.filter_by(user_id=user.id, active=True).first()
            chance_to_end_job = 0.03
            if random.random() < chance_to_end_job:
                end_job(current_job, machine, simulation_datetime)
            chance_to_change_activity = 0.2
            if random.random() < chance_to_change_activity:
                change_activity(machine, current_job, user, simulation_datetime)

        else:
            chance_to_start_job = 0.3
            if random.random() < chance_to_start_job:
                start_new_job(machine, user, simulation_datetime)
        DemoSettings.query.get(1).last_machine_simulation = simulation_datetime
    db.session.commit()


def backfill_missed_simulations():
    simulation_start = DemoSettings.query.get(1).last_machine_simulation
    if (datetime.now() - simulation_start) > timedelta(Config.DAYS_BACKFILL):
        simulation_start = datetime.now() - timedelta(Config.DAYS_BACKFILL)
    for i in dt_range(simulation_start, datetime.now(), Config.DATA_SIMULATION_FREQUENCY_SECONDS):
        simulate_machines(i)


def dt_range(start_dt, end_dt, frequency_seconds):
    """ Returns a generator for a range of datetimes between the two dates, at the frequency specified """
    current_iteration = start_dt
    while current_iteration <= end_dt:
        current_iteration = current_iteration + timedelta(seconds=frequency_seconds)
        yield current_iteration


names = [
    "Barry",
    "Pam",
    "Sterling",
    "Cheryl",
    "Ray",
    "Lana",
    "Brett",
    "Cyril",
    "Mallory",
    "Leonard",
    "Ron",
    "Arthur",
    "Mitsuko",
    "Alan",
    "Conway",
    "Algernop",
    "Katya",
    "Slater"
]