from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, HiddenField
from wtforms.validators import DataRequired


class StartJobForm(FlaskForm):
    machine_id = HiddenField()
    job_number = StringField('Job Number', validators=[DataRequired()])
    ideal_cycle_time = FloatField('Ideal Cycle Time (s)')

    submit = SubmitField('Set')


class EndJobForm(FlaskForm):
    machine_id = HiddenField()
    good_quantity = IntegerField("Good Quantity")
    rejects = IntegerField("Rejects")
    submit = SubmitField("End")
