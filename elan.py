crud.py

from datetime import datetime, timedelta

def idealtime(userid: int, db: Session):
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")  # Format the current time

    # Fetch the current work session for the user
    work_session = db.query(models.WorkSession).filter(models.WorkSession.user_id == userid).order_by(models.WorkSession.id.desc()).first()

    if work_session:
        if work_session.end_time:
            # If end_time is set, create a new session
            new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
            db.add(new_session)
            db.commit()
        else:
            # If end_time is empty, set it to current_time and calculate total_time_worked
            work_session.end_time = current_time_str
            # Commit changes after setting end_time
            db.commit()

            # Calculate total_time_worked only if both start_time and end_time are present
            start_time = datetime.strptime(work_session.start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(work_session.end_time, "%Y-%m-%d %H:%M:%S")
            total_time = end_time - start_time

            # Store the total time worked as a string
            work_session.total_time_worked = str(total_time)
            db.commit()
    else:
        # Create a new session if none exists
        new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
        db.add(new_session)
        db.commit()

    return userid



def add_ideal_time(data_list: List[Dict], dict2: Dict[str, str]) -> List[Dict]:
    # Iterate over each dictionary in the list
    for data in data_list:
        # Extract the user from the current dictionary
        user = next(iter(data['user']), None)
        if user and user in dict2:
            # Add 'idealtime' to the dictionary if the user exists in dict2
            data['idealtime'] = dict2[user]
    
    return data_list


def calculate_total_time_for_all_users(
    picked_date: str,
    to_date: str,
    db: Session
) -> dict:
    

    # Parse the dates from the form assuming the format 'YYYY-MM-DD'
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    # If time is not provided, assume start time is 00:00:00 and end time is 23:59:59
    picked_date_start = picked_datett.replace(hour=0, minute=0, second=0)
    to_date_end = to_datett.replace(hour=23, minute=59, second=59)


    # Fetch all work sessions between the specified dates
    sessions = db.query(models.WorkSession).filter(
        models.WorkSession.start_time >= picked_date_start.strftime("%Y-%m-%d %H:%M:%S"),
        models.WorkSession.end_time <= to_date_end.strftime("%Y-%m-%d %H:%M:%S")
    ).all()

    # Dictionary to hold total time for each user
    user_total_time = defaultdict(timedelta)

    # Calculate the total time worked for each user
    for session in sessions:
        if session.start_time and session.end_time:
            start_time = datetime.strptime(session.start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(session.end_time, "%Y-%m-%d %H:%M:%S")
            user_total_time[session._user_table1.username] += (end_time - start_time)

    # Format the output
    formatted_output = {}
    for  total_time , _user_table1 in user_total_time.items():
        # Format total_time to HH:MM:SS
        formatted_output[f'{total_time}'] = str(_user_table1)
    print(type(picked_date),type(to_date))
    print(totalfivereports(db,picked_date,to_date,'userlist'),'final result ....................................................')
    updated_data_list = add_ideal_time(totalfivereports(db,picked_date,to_date,'userlist'), formatted_output)

    # Print the updated data list
    for item in updated_data_list:
        print(item)
    return updated_data_list

=============================================================
@app.post("/idealtimecalculation")
def idealtimecalculation(userid: Annotated[int, Form()], db: Session = Depends(get_db)):
    return crud.idealtime(userid, db)


@app.post("/calculate_total_time")
def calculate_total_time(
   picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],db: Session = Depends(get_db)
):

    # Call the CRUD function to calculate total time for all users
    total_time = crud.calculate_total_time_for_all_users(picked_date, to_date, db)

    return total_time 



main.py

==================================================================================================================

class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_table.user_id'))  
    start_time = Column(String,default='')
    end_time = Column(String,default='')
    total_time_worked = Column(String,default='')
    _user_table1 = relationship("User_table")


model.py

-----------------------------------------------------------------------------------------------------
