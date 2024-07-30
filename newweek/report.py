from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import UploadFile,HTTPException
import pandas as pd
import json
from datetime import date,datetime,timedelta
import os
from zipfile import ZipFile
import tracemalloc
import shutil
from sqlalchemy import cast, or_,and_,func,Date
import csv
from datetime import datetime, timedelta
from io import BytesIO
import pendulum

def time_difference(time1 , time2):

    if time1 and time2:
        try:
            print(time1,time2,'two times')
            return time1 - time2
        except :
            return timedelta(hours=0)
    elif time1:
        time2 = datetime.now()
        try:
            print(time1,datetime.now(),'time 2 absent')
            return time1 - datetime.now()
        except :
            return timedelta(hours=0)
    else :
        time1 = datetime.now()
        try:
            print(time1,datetime.now(),'time 1 absent')
            return time1 - datetime.now()
        except :
            return timedelta(hours=0)

def convert_to_duration(value):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_duration = f"{hours}:{minutes}:{seconds}"
        
        return formatted_duration


def commoncalculation(db: Session,db_res, date: str):

            list_data = []
            date_time1 = datetime.now()
            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            for row in db_res:
                
                data = {}
                data["date"] = datetime.strptime(row.working_time, '%Y-%m-%d %H:%M:%S').date()
                data["user"] = row._user_table1.username
                data["Service_ID"] = row.Service_ID
                data["scope"] = row.Scope
                data["subscopes"] = row.From
                data["entity"] = row.name_of_entity
                data["status"] = row.work_status
                data["type_of_activity"] = row.type_of_activity
                data["Nature_of_Work"] = row._nature_of_work.work_name
                data["gst_tan"] = row.gst_tan
                data["estimated_d_o_d"] =  row.estimated_d_o_d
                data["no_of_items"] = row.no_of_items
                data["estimated_time"] =  row.estimated_time
                data["member_name"] = row._user_table1.firstname +' '+ row._user_table1.lastname

                working_time_report = datetime.strptime(row.working_time, date_time_formate_string)
                completed_time_report = None
                try:
                    completed_time_report = datetime.strptime(row.completed_time, date_time_formate_string)
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                hold_time_report = None
                break_time_report = None
                meeting_time_report = None
                call_time_report = None
                totalminus = None
                Totaltime = None
                

                current_time_report = datetime.now()
#---------------------------------------------------------------------------------------------------------------------- timing code for old start

                

                old_hold_start_time = None
                old_end_start_time = None
                old_hold_t1 = None
                old_end_t2 = None
                old_end = None

                try:
                    query = db.query(models.HOLD).filter(
                        models.HOLD.Service_ID == row.Service_ID,
                        models.HOLD.hold_time_start < date
                    ).order_by(func.abs(func.date(models.HOLD.hold_time_start) - date))

                    if query:
                        nu = query.count()
                        re = query.all()
                        # print(nu,date,'hhhhhhhhhhhhhhhhhhhh')
                        old_hold_start_time = re[nu-1].hold_time_start
                        old_hold_t1 = re[nu-1].hold_time_end
                    else:
                        print("No hold record found for Service_ID 14")
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")

                try:
                    query = db.query(models.END_OF_DAY).filter(
                        models.END_OF_DAY.Service_ID == row.Service_ID,
                        models.END_OF_DAY.end_time_start < date
                    ).order_by(func.abs(func.date(models.END_OF_DAY.end_time_start) - date))

                    if query:
                        nu = query.count()
                        re = query.all()
                       
                        old_end_start_time = re[nu-1].end_time_start
                        old_end_t2 = re[nu-1].end_time_end
                    else:
                        print("No hold record found for Service_ID 14")
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")


                # print(old_hold_start_time , old_end_start_time,'fffffffffffffffffffffffffffffffffffffffffffffffffffffff')
                try:
                  old_hold_start_time = datetime.strptime(old_hold_start_time, date_time_formate_string)
                #   print(old_hold_start_time)
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                # print(old_hold_start_time , old_end_start_time,'ggggggggggggggggggggggggggggggggggggggggggggg')
                try:
                  old_end_start_time = datetime.strptime(old_end_start_time, date_time_formate_string)
                 
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                
                try:
                    if old_hold_start_time > old_end_start_time:
                            old_end = old_hold_t1

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                
                try:
                    if  old_hold_start_time < old_end_start_time:
                            old_end = old_end_t2

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                try:
                    if  (old_hold_start_time==None) and  (old_end_start_time!=None):
                            old_end = old_end_t2
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                try:
                    if  (old_end_start_time==None) and  (old_hold_start_time!=None):
                            old_end = old_hold_t1
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")

                # print(old_end,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
#----------------------------------------------------------------------------------------------------   old start time end    




#---------------------------------------------------------------------------------------------------------------------- timing code for past today start
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                new_date = date_obj + timedelta(days=1)

                added_date = new_date.strftime('%Y-%m-%d')
                

                past_today_greater_end_end = None
                past_today_greater_hold_end = None
                past_hold_t1 = None
                past_end_t2 = None
                past_today_greater = None

                try:
                    query = db.query(models.HOLD).filter(
                        models.HOLD.Service_ID == row.Service_ID,
                        models.HOLD.hold_time_start < added_date
                    ).order_by(func.abs(func.date(models.HOLD.hold_time_start) - added_date))

                    if query:
                        nu = query.count()
                        re = query.all()
                        # print(nu,date,'hhhhhhhhhhhhhhhhhhhh')
                        past_today_greater_end_end = re[nu-1].hold_time_start
                        past_hold_t1 = re[nu-1].hold_time_end
                    else:
                        print("No hold record found for Service_ID 14")
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")

                try:
                    query = db.query(models.END_OF_DAY).filter(
                        models.END_OF_DAY.Service_ID == row.Service_ID,
                        models.END_OF_DAY.end_time_start < added_date
                    ).order_by(func.abs(func.date(models.END_OF_DAY.end_time_start) - added_date))

                    if query:
                        nu = query.count()
                        re = query.all()
                       
                        past_today_greater_hold_end = re[nu-1].end_time_start
                        past_end_t2 = re[nu-1].end_time_end
                    else:
                        print("No hold record found for Service_ID 14")
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")


                # print(past_today_greater_end_end , past_today_greater_hold_end,'fffffffffffffffffffffffffffffffffffffffffffffffffffffff')
                try:
                  past_today_greater_end_end = datetime.strptime(past_today_greater_end_end, date_time_formate_string)
                #   print(past_today_greater_end_end)
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                # print(past_today_greater_end_end , past_today_greater_hold_end,'ggggggggggggggggggggggggggggggggggggggggggggg')
                try:
                  past_today_greater_hold_end = datetime.strptime(past_today_greater_hold_end, date_time_formate_string)
                 
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                
                try:
                    if past_today_greater_end_end > past_today_greater_hold_end:
                            past_today_greater = past_hold_t1

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                
                try:
                    if  past_today_greater_end_end < past_today_greater_hold_end:
                            past_today_greater = past_end_t2

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                try:
                    if  (past_today_greater_end_end==None) and  (past_today_greater_hold_end!=None):
                            past_today_greater = past_end_t2
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")
                try:
                    if  (past_today_greater_hold_end==None) and  (past_today_greater_end_end!=None):
                            past_today_greater = past_hold_t1
                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")

                # print(past_today_greater,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
#----------------------------------------------------------------------------------------------------   timing code for past today start
    




                try:                    
                    query = db.query(models.HOLD).filter(
                        models.HOLD.Service_ID == row.Service_ID,
                        models.HOLD.hold_time_start.like(f"%{date}%"),
                        models.HOLD.hold_time_end.like(f"%{date}%")
                    )

                    for nq in query.all():
                        if hold_time_report != None:
                            hold_time_report = hold_time_report+time_difference(nq.hold_time_end,nq.hold_time_start)
                        else:
                            hold_time_report = time_difference(nq.hold_time_end,nq.hold_time_start)

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")

                try:                    
                    query = db.query(models.BREAK).filter(
                        models.BREAK.Service_ID == row.Service_ID,
                        models.BREAK.break_time_start.like(f"%{date}%"),
                        models.BREAK.break_time_end.like(f"%{date}%")
                    )

                    for nq in query.all():
                        if break_time_report != None:
                            break_time_report = break_time_report+time_difference(nq.break_time_end,nq.break_time_start)
                        else:
                            break_time_report = time_difference(nq.break_time_end,nq.break_time_start)

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")

                try:                    
                    query = db.query(models.MEETING).filter(
                        models.MEETING.Service_ID == row.Service_ID,
                        models.MEETING.meeting_time_start.like(f"%{date}%"),
                        models.MEETING.meeting_time_end.like(f"%{date}%")
                    )

                    for nq in query.all():
                        if meeting_time_report != None:
                            meeting_time_report = meeting_time_report+time_difference(nq.meeting_time_end,nq.meeting_time_start)
                        else:
                            meeting_time_report = time_difference(nq.meeting_time_end,nq.meeting_time_start)

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")

                try:                    
                    query = db.query(models.CALL).filter(
                        models.CALL.Service_ID == row.Service_ID,
                        models.CALL.call_time_start.like(f"%{date}%"),
                        models.CALL.call_time_end.like(f"%{date}%")
                    )

                    for nq in query.all():
                        if call_time_report != None:
                            call_time_report = call_time_report+time_difference(nq.call_time_end,nq.call_time_start)
                        else:
                            call_time_report = time_difference(nq.call_time_end,nq.call_time_start)

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")



                
                if hold_time_report!=None :
                        if totalminus  == None:
                            totalminus = hold_time_report
                        else: 
                            totalminus = totalminus+hold_time_report
                
                if  break_time_report!=None:
                        if totalminus  == None:
                            totalminus = break_time_report
                        else: 
                            totalminus = totalminus+break_time_report

                if  meeting_time_report!=None:
                        if totalminus  == None:
                            totalminus = meeting_time_report
                        else: 
                            totalminus = totalminus+meeting_time_report

                if  call_time_report!=None:
                        if totalminus  == None:
                            totalminus = call_time_report
                        else: 
                            totalminus = totalminus+call_time_report
#----------------------------------------------------------------------------------------------------- timing code


#---------------------------------------------------------- calculation code


                if completed_time_report:

                    if completed_time_report.date() == working_time_report.date():
                        
                        timei1 = working_time_report
                        timei2 = completed_time_report
                        timediff_f2 = time_difference(timei2,timei1)

                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['completed'] = Totaltime
                        except Exception as e:
                            
                            data['completed'] = timediff_f2
                            print(f"An unexpected error occurred: {e}")

                        # print(Totaltime,'same day')
                    else:
                        timei1 = old_end
                        timei2 = completed_time_report
                        timediff_f2 = time_difference(timei2,timei1)


                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['completed'] = Totaltime
                        except Exception as e:
                            data['completed'] = timediff_f2
                            print(f"An unexpected error occurred: {e}")

                        # print(Totaltime,'different day')

                elif working_time_report.date()==current_time_report.date():

                        timei1 = working_time_report
                        timei2 = current_time_report
                        timediff_f2 = time_difference(timei2,timei1)


                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['in_progress'] = Totaltime
                        except Exception as e:
                            data['in_progress'] = timediff_f2
                            print(f"An unexpected error occurred: {e}")
                        # print(Totaltime,'sameday not finished')

                else :

                    if old_hold_start_time and old_end_start_time:
                        if (old_hold_start_time > old_end_start_time) and (old_end.date() == current_time_report.date()) :

                            timei1 = current_time_report
                            timei2 = old_end
                            timediff_f2 = time_difference(timei1,timei2)


                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                                print(f"An unexpected error occurred: {e}")
                            # print(Totaltime,'sameday not finished')
                            # print(Totaltime,'hold')
                        
                        elif (old_hold_start_time < old_end_start_time) and (old_end.date() == current_time_report.date()):
                            timei1 = current_time_report
                            timei2 = old_end
                        
                            timediff_f2 = time_difference(timei1,timei2)

                            
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                                print(f"An unexpected error occurred: {e}")
                            # print(Totaltime,'sameday not finished')
                            
                    elif old_end_start_time and (old_end.date() == current_time_report.date()):
                        
                        timei1 = current_time_report
                        timei2 = old_end
                    
                        timediff_f2 = time_difference(timei1,timei2)

                        
                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['in_progress'] = Totaltime
                        except Exception as e:
                            data['in_progress'] = timediff_f2
                            print(f"An unexpected error occurred: {e}")
                        # print(Totaltime,'sameday not finished')
                    
                    elif old_hold_start_time and (old_end.date() == current_time_report.date()):
                            timei1 = current_time_report
                            timei2 = old_end
                            timediff_f2 = time_difference(timei1,timei2)

                            
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                                print(f"An unexpected error occurred: {e}")
                            # print(Totaltime,'sameday not finished')
                            


                try:

                    if completed_time_report!=None:

                        if (past_today_greater!=None) and (past_today_greater.date()!=current_time_report.date())   and (completed_time_report.date()!=past_today_greater.date()):


                                    timei1 = past_today_greater
                                    timei2 = old_end
                                    timediff_f2 = time_difference(timei1,timei2)


                                    try:  
                                        Totaltime = timediff_f2 - totalminus
                                        data['in_progress'] = Totaltime
                                    except Exception as e:
                                        data['in_progress'] = timediff_f2
                                        print(f"An unexpected error occurred: {e}")
                                    # print(Totaltime,'sameday not finished')

                                

                    else:

                        if (past_today_greater!=None) and (past_today_greater.date()!=current_time_report.date()):


                                    timei1 = past_today_greater
                                    timei2 = old_end
                                    timediff_f2 = time_difference(timei1,timei2)


                                    try:  
                                        Totaltime = timediff_f2 - totalminus
                                        data['in_progress'] = Totaltime
                                    except Exception as e:
                                        data['in_progress'] = timediff_f2
                                        print(f"An unexpected error occurred: {e}")

                                

                except Exception as e:
                
                    print(f"An unexpected error occurred: {e}")


#---------------------------------calculation code

                str_temp = ""
                str_temper = ""

                if row.work_status == "Work in Progress":

                    data["third_report_data"] = ""

                elif row.work_status == "Hold":

                    db_res3 = db.query(models.HOLD).filter(
                        models.HOLD.Service_ID == row.Service_ID,
                    ).all()
                    for hold_obj in db_res3:
                        data["third_report_data"] = hold_obj.remarks
                        str_temper = hold_obj.remarks

                elif row.work_status == "Meeting":

                    db_res3 = db.query(models.MEETING).filter(
                        models.MEETING.Service_ID == row.Service_ID,
                    ).all()
                    for meet_obj in db_res3:
                        data["third_report_data"] = meet_obj.remarks


                elif row.work_status == "Break":
                    db_res3 = db.query(models.BREAK).filter(
                        models.BREAK.Service_ID == row.Service_ID,
                    ).all()
                    for break_obj in db_res3:
                      
                        data["third_report_data"] = break_obj.remarks
                        
                elif row.work_status == "Clarification Call":
                    db_res3 = db.query(models.CALL).filter(
                        models.CALL.Service_ID == row.Service_ID,
                    ).all()
                    for call_obj in db_res3:
                      
                        data["third_report_data"] = call_obj.remarks

                elif row.work_status == "Completed":
                    data["third_report_data"] = row.remarks

                if row.work_status == "Completed":
                    try:
                        db_res3 = db.query(models.HOLD).filter(
                            models.HOLD.Service_ID == row.Service_ID,
                        ).all()
                        for hold_obj in db_res3:
                            str_temp = str_temp + hold_obj.remarks + ","
                    except:
                        str_temp = ""
                    try:
                        db_res3 = db.query(models.MEETING).filter(
                            models.MEETING.Service_ID == row.Service_ID,
                        ).all()
                        for meet_obj in db_res3:

                            str_temp = str_temp + meet_obj.remarks + ","

                    except:
                        str_temp = ""
                    try:
                        db_res3 = db.query(models.BREAK).filter(
                            models.BREAK.Service_ID == row.Service_ID,
                        ).all()
                        for break_obj in db_res3:
                            str_temp = str_temp + break_obj.remarks + ","
                    except:
                        str_temp = ""
                    try:
                        db_res3 = db.query(models.CALL).filter(
                            models.CALL.Service_ID == row.Service_ID,
                        ).all()
                        for call_obj in db_res3:
                            str_temp = str_temp + call_obj.remarks + ","
                        str_temp = str_temp + row.remarks + ","
                    except:
                        str_temp = ""

                # hold_time_report = None
                # break_time_report = None
                # meeting_time_report = None
                # call_time_report = None
                print(str(hold_time_report),break_time_report,call_time_report,meeting_time_report)
                try:
                    date['hold'] = str(hold_time_report)
                except:
                        None
                try:
                    date['break'] = str(break_time_report)
                except:
                        None
                try:
                    date['call'] = str(call_time_report)
                except:
                        None
                try:
                    date['meeting'] = str(meeting_time_report)
                except:
                        None
                # 'in_progress' 
                data['completed'] = Totaltime


                data["fourth_report"] = row.no_of_items
                data["fourth_report2"] = str_temp
                data["fifth_report"] = str_temper                    
                list_data.append(data)

                # break
            return list_data
#----------------------------------------------------------------------------


def common( db : Session , date : str , dataoptiopns   , option : str , statusdata : str):
            # dataoptiopns means entity , scope and sub scobe option means which report , statusdata means chargable or non-chargable
        # print(dataoptiopns,'000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        
        if option == "userlist" and statusdata == 'CHARGABLE':
            
            list_ddata1 = set()


            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            
            return commoncalculation(db,newquery, date)
            
        elif option == "userlist" and statusdata == 'Non-Charchable':

            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)
        
        elif option == "entitylist"  and statusdata == 'CHARGABLE':
            db_res = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.name_of_entity == dataoptiopns,
                or_(
                    models.TL.working_time.like(f"%{date}%"),
                    models.TL.reallocated_time.like(f"%{date}%"),
                )
                ).all()
            return commoncalculation(db,db_res, date)

        elif option == "entitylist"  and statusdata == 'Non-Charchable':
            
            db_res = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.name_of_entity == dataoptiopns,
                or_(
                    models.TL.working_time.like(f"%{date}%"),
                    models.TL.reallocated_time.like(f"%{date}%"),
                )
                ).all()
            return commoncalculation(db,db_res, date)


        elif option == "scopelist" and statusdata == 'CHARGABLE':
            
            db_res = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Scope == dataoptiopns,
                or_(
                    models.TL.working_time.like(f"%{date}%"),
                    models.TL.reallocated_time.like(f"%{date}%"),
                  
                )
                ).all()
            return commoncalculation(db,db_res, date)

        elif option == "scopelist" and statusdata == 'Non-Charchable':
            
            db_res = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Scope == dataoptiopns,
                or_(
                    models.TL.working_time.like(f"%{date}%"),
                    models.TL.reallocated_time.like(f"%{date}%"),
                
                )
                ).all()
            return commoncalculation(db,db_res, date)

        elif option == "subscope"  and statusdata == 'CHARGABLE':
            
            db_res = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.From == dataoptiopns,
                or_(
                    models.TL.working_time.like(f"%{date}%"),
                    models.TL.reallocated_time.like(f"%{date}%"),
                   
                )
                ).all()
            return commoncalculation(db,db_res, date)

        elif option == "subscope"  and statusdata == 'Non-Charchable':
            
            db_res = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.From == dataoptiopns,
                or_(
                    models.TL.working_time.like(f"%{date}%"),
                    models.TL.reallocated_time.like(f"%{date}%"),
                    
                )
                ).all()
            return commoncalculation(db,db_res, date)

def user_wise_report(db: Session,date: str,option: str):
    list_data = []
    list_ddata1 = set()


    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.working_time.like(f"%{date}%")    
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)

    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID == models.HOLD.Service_ID,
        or_(
            models.HOLD.hold_time_end.like(f"%{date}%"),
            models.TL.working_time.like(f"%{date}%")
        )
        
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)
    
    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID == models.END_OF_DAY.Service_ID,
        or_(
            models.END_OF_DAY.end_time_end.like(f"%{date}%"),
            models.TL.working_time.like(f"%{date}%")
        )
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)
        

# final query
    db_res =  db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID.in_(list_ddata1)
    ).all()


    finalfilter = set()

    Scopelist = set() # scope
    subscopeslist = set() # form
    userlist = set() 
    entitylist = set() # name of entity

    for row in db_res:
        userlist.add(row._user_table1.user_id)
        entitylist.add(row.name_of_entity)
        Scopelist.add(row.Scope)
        subscopeslist.add(row.From)
 
    if option == "userlist":
        
        finalfilter = userlist
        

    elif option == "entitylist":
        # Assuming db_res contains the result of your query
        for tl_obj in db_res:
            service_id = tl_obj.Service_ID
        # print(service_id,'Or do whatever you need with service_id')  # Or do whatever you need with service_id

        finalfilter = entitylist
    elif option == "scopelist":
        
        finalfilter = Scopelist
    elif option == "subscope":
        
        finalfilter = subscopeslist


    # print(userlist,"userlist")
    # print(entitylist, "entitylist")
    # print(Scopelist,"scopelist")
    # print(subscopeslist,"subscope")

    for usertof in finalfilter:

            

            combined_data = {
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set()
            }

            combined_datab = {
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set()
            }

            finalre = {
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': set(),
                'hold': set(),
                'break': set(),
                'time_diff_work': set(),
                'call': set(),
                'meeting': set(),
                'in_progress': set(),
                'completed': set(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set()
            }


            end_time = pendulum.duration()
            hold = pendulum.duration()
            breaks = pendulum.duration()
            time_diff_work = pendulum.duration()
            call = pendulum.duration()
            meeting = pendulum.duration()
            in_progress = pendulum.duration()
            completed = pendulum.duration() 
            no_itemsa = 0
            for entry in  common( db  , date  , usertof   , option  , 'Non-Charchable'):
                # print(entry,'newone non-chargable')
                for key in combined_datab.keys():
                    if key == 'date':
                            
                            combined_datab[key].add(entry[key])
                    elif key == 'end_time':
                        try : 
                            end_time = end_time + entry[key]
                            
                        except:
                            end_time = end_time + pendulum.duration(hours=0)
                    elif key == 'hold':
                        try : 
                            hold = hold + entry[key]
                           
                        except:
                            hold = hold +  pendulum.duration(hours=0)
                    elif key == 'break':
                        try : 
                            breaks = breaks + entry[key]
                            
                        except:
                            breaks = breaks + pendulum.duration(hours=0)
                    elif key == 'time_diff_work':
                        try : 
                            time_diff_work = time_diff_work + entry[key]

                        except:
                            time_diff_work = time_diff_work + pendulum.duration(hours=0)
                    elif key == 'call':
                        try : 
                            call = call + entry[key]
                           
                        except:
                            call = call + pendulum.duration(hours=0)
                    elif key == 'meeting':
                        try : 
                            meeting = meeting + entry[key]

                        except:
                            meeting = meeting + pendulum.duration(hours=0)
                    elif key == 'in_progress':
                        try : 

                            in_progress = in_progress + entry[key]
                            
                        except:
                            in_progress = in_progress + pendulum.duration(hours=0)
                    elif key == 'completed':
                        try : 
                            completed = completed + entry[key]
                          
                        except:
                            completed = completed +  pendulum.duration(hours=0)   
     
                    elif key == 'no_of_items':
                        
                        
                        try : 
                            no_itemsa = no_itemsa +  int(entry[key])
                         
                            
                            
                        except:
                            None                                                                                                                                                           
                    else:
                        combined_datab[key].add(entry[key])



            end_timea = pendulum.duration()
            holda = pendulum.duration()
            breaksa = pendulum.duration()
            time_diff_worka = pendulum.duration()
            calla = pendulum.duration()
            meetinga = pendulum.duration()
            in_progressa = pendulum.duration()
            completeda = pendulum.duration()
            no_items = 0
            for entry in common( db  , date  , usertof   , option  , 'CHARGABLE'):
                
                for key in combined_data.keys():
                    if key == 'date':
                            
                            combined_data[key].add(entry[key])
                    elif key == 'end_time':
                        try : 
                            end_timea = end_timea + entry[key]
                            
                        except:
                            end_timea = end_timea + pendulum.duration(hours=0)
                    elif key == 'hold':
                        try : 
                            holda = holda + entry[key]
                           
                        except:
                            holda = holda +  pendulum.duration(hours=0)
                    elif key == 'break':
                        try : 
                            breaksa = breaksa + entry[key]
                            
                        except:
                            breaksa = breaksa + pendulum.duration(hours=0)
                    elif key == 'time_diff_work':
                        try : 
                            time_diff_worka = time_diff_worka + entry[key]

                        except:
                            time_diff_worka = time_diff_worka + pendulum.duration(hours=0)
                    elif key == 'call':
                        try : 
                            calla = calla + entry[key]
                           
                        except:
                            calla = calla + pendulum.duration(hours=0)
                    elif key == 'meeting':
                        try : 
                            meetinga = meetinga + entry[key]

                        except:
                            meetinga = meetinga + pendulum.duration(hours=0)
                    elif key == 'in_progress':
                        try : 

                            in_progressa = in_progressa + entry[key]
                            
                        except:
                            in_progressa = in_progressa + pendulum.duration(hours=0)
                    elif key == 'completed':
                        try : 
                            completeda = completeda + entry[key]
                          
                        except:
                            completeda = completeda +  pendulum.duration(hours=0)   

                    elif key == 'no_of_items':
                        
                        try : 

                            no_items = no_items +  int(entry[key])
                         
                        except:
                            None                                                                                                                                                                                           
                    else:
                        combined_data[key].add(entry[key])

#-------------------------------------------------------------------------------------------------------

            combined_data['end_time'] = end_timea
            combined_data['hold'] = holda
            combined_data['break'] = breaksa
            combined_data['time_diff_work'] = time_diff_worka
            combined_data['call'] = calla
            combined_data['meeting'] = meetinga
            combined_data['in_progress'] = in_progressa
            combined_data['completed'] =  completeda
            combined_data['no_of_items'].add(no_items)
            # print(no_itemsa ,no_items,'rrrrrrrrrrrrrrrrrr')

            # # Print the values of these variables
            # print("end_timea:", end_timea.in_words())
            # print("holda:", holda.in_words())
            # print("breaksa:", breaksa.in_words())
            # print("time_diff_worka:", time_diff_worka.in_words())
            # print("calla:", calla.in_words())
            # print("meetinga:", meetinga.in_words())
            # print("in_progressa:", in_progressa.in_words())
            # print("completeda:", completeda.in_words())


            combined_datab['end_time'] = end_time 
            combined_datab['hold'] = hold 
            combined_datab['break'] = breaks 
            combined_datab['time_diff_work'] = time_diff_work 
            combined_datab['call'] = call 
            combined_datab['meeting'] = meeting 
            combined_datab['in_progress'] = in_progress 
            combined_datab['completed'] =  completed 
            combined_datab['no_of_items'].add(no_itemsa)

            # print(common( db  , date  , usertof   , option  , 'CHARGABLE'),usertof,'result--------------------------')

            # Print the values of these variables
            # print("end_time:", end_time.in_words())
            # print("hold:", hold.in_words())
            # print("breaks:", breaks.in_words())
            # print("time_diff_work:", time_diff_work.in_words())
            # print("call:", call.in_words())
            # print("meeting:", meeting.in_words())
            # print("in_progress:", in_progress.in_words())
            # print("completed:", completed.in_words())

            for key in finalre.keys():

                        if key == 'end_time':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'hold':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'break':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'time_diff_work':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'call':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'meeting':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'in_progress':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'completed':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'no_of_items':
                            finalre[key].add(no_items+no_itemsa)
                        elif key == 'chargable':
                            finalre[key].add(convert_to_duration(combined_data['in_progress']+combined_data['completed']))
                        elif key == 'non-chargable':
                            finalre[key].add(convert_to_duration(combined_datab['in_progress']+combined_datab['completed']))
                        elif key == 'total-time':
                            finalre[key].add(convert_to_duration(combined_data['in_progress']+combined_data['completed']+combined_datab['in_progress']+combined_datab['completed']))
                        else:
                            finalre[key] = combined_data[key].union(combined_datab[key])

# ------------------------------------------------------------------------------------            

            list_data.append(finalre)
           
    return list_data
