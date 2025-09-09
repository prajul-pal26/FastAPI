
Problem Solved-
1- Divide the data into chunks 

2- delete the leads from the redis after sending the sms
3- delete the particular leads data from the redis
4- use reddis for in memory fast processing the leads data 
5- search the status with the actual meeting time 
6- 
END POINTS

# add_sms_leads 
    - Adding the leads data and divided into chunks and stored in redis
    
    INPUT-
        file
        chunk_size
        interval_seconds
        date_time
    
    OUTPUT-
        sms_upload:<upload_id>
        │
        ├── file_name              -->   "leads.csv"
        ├── msg1                   -->   "Hi, this is a reminder"
        ├── msg2                   -->   "Don't forget our meeting"
        │
        ├── 2025-09-08T15:00:00    ->   JSON array of leads (Chunk 1)
        │   └── [{"name": "John", "phone": "12345"}]
        │
        ├── 2025-09-08T15:10:00    ->   JSON array of leads (Chunk 2)
        │   └── [{"name": "Tom", "phone": "11111"}]

# view_sms_leads
    - Get all the Status in the redis
    
    USED CASES- 
        1-After adding the leads
        2-After sending the leads
        3-After deleting the leads
        4-After Adding/updating the message

    OUTPUT-
        [
            {
                "upload_id": "upload_b808733e",
                "file_name": "test_smaple.csv",
                "total_chunks": 5,
                "message1": "",
                "message2": "",
                "scheduled_times": [
                {
                    "timestamp": "2025-09-04T15:30:11",
                    "lead_count": 50
                },
                ]
            }
        ]
# manage_sms_messages
    INPUT-
        upload_id   - "upload_b808733e",
        new_msg1    - String
        new_msg2    - String
        delete_msg1 - True/False
        delete_msg2 - True/False 
    
    OUTPUT-
        Can be check in view_sms_leads

# send_sms_leads
    - Send the sms to the leads
    - This will remove the leads from the redis after sending the sms
    
# delete_sms_leads
    - Delete the leads from the redis 
     INPUT -
        upload_id   - "upload_b808733e"
