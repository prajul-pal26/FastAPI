# import logging
from datetime import datetime, timezone, timedelta
# from typing import Dict
# from dataclasses import dataclass
# from typing import List, Optional
# import os
# from configs.global_config import DB_RESOURCES_NAMES_TXT_DIR
# from common.common_utils import read_db_resource_value
# import pytz
# import pandas as pd
# from pydantic import BaseModel, Field, field_validator
# from pydantic import AnyUrl

# from common.common_utils import is_date_time_str_valid
# from utils.utilities import get_valid_phone_number

# from dvtools.api_utils import AppEmailLogger
# from dvtools.setup_logging import setup_logger
# from dvtools.api_config import BaseResponseModel, ResponseModel
# from dvtools.api_config import ROUTE_SMS
# from dvtools.api_config import DV_MANAGEMENT_SLACK_EMAIL, DEV_NOTIFY_SLACK_EMAIL
# from dvtools.slack.slack_logger import SlackLogger
# from dvtools.slack.icon_list import SPEECH_BALLOON

# # sms rate table config
# DB_NAME_TXT_FILE = "twilio_sms_config_table_name.txt"
# TABLE_NAME_FILE_PATH = os.path.join(DB_RESOURCES_NAMES_TXT_DIR, DB_NAME_TXT_FILE)
# DEFAULT_TABLE_NAME = "STAGING_TWILIO_SMS_CONFIG"
# CURRENT_TABLE_NAME = read_db_resource_value(TABLE_NAME_FILE_PATH, DEFAULT_TABLE_NAME)

# DEV_MODE = CURRENT_TABLE_NAME == DEFAULT_TABLE_NAME

# LOGGING_LEVEL = logging.INFO
# # LOGGING_LEVEL = logging.DEBUG
# logger = setup_logger(logger_name="sms", log_file_name="sms.log", logger_level=LOGGING_LEVEL)
# cc = [
#     "prakash@deepvidya.ai",
#     DEV_NOTIFY_SLACK_EMAIL
# ]

# if DEV_MODE:
#     cc = []

# email_logger = AppEmailLogger(routr_config=ROUTE_SMS, cc=cc)

# schedule_sms_email_cc = [
#     "prakash@deepvidya.ai",
#     "bharath@deepvidya.ai",
#     DV_MANAGEMENT_SLACK_EMAIL
# ]

# if DEV_MODE:
#     schedule_sms_email_cc = []

# schedule_sms_email_logger = AppEmailLogger(routr_config=ROUTE_SMS, cc=schedule_sms_email_cc)

# CODE_TEST_CHANNEL_ID = "C0870RTSXTK" # #code-test

# DEV_NOTIFY_CHANNEL_ID = "C06TQ9PF7DX"
# if DEV_MODE:
#     DEV_NOTIFY_CHANNEL_ID = CODE_TEST_CHANNEL_ID

# SUBJECT_PREFIX = "[dvtools:sms]"

# slack_logger = SlackLogger(to=DEV_NOTIFY_CHANNEL_ID, username="sms-api", icon_emoji=SPEECH_BALLOON, subject_prefix=SUBJECT_PREFIX)



# Two types of SMS will be send
type_webinar = "webinar"
type_sales_campaign = "sales_campaign"



# @dataclass(frozen=True)
# class ColumnsName:
#     PROSPECT_ID = "Prospect ID"
#     CONTACT_NUMBER = "Contact Number"
#     ALTERNAT_NUMBER = "Alternative Number"
#     IST_TIME_DIFF = "IST Time Diff"
#     LEAD_STAGE = "Lead Stage"
#     COUNTRY = "Country"
#     COLUMNS = (
#         PROSPECT_ID, CONTACT_NUMBER, ALTERNAT_NUMBER, IST_TIME_DIFF, LEAD_STAGE, COUNTRY
#     )

# class WebinarSendSMSModel(BaseModel):
#     prospect_id: str 
#     webinar_datetime: str
    


# @dataclass(frozen=True)
# class SmsRestrictedStages:
#     ENROLLMENT_DONE = "Enrollment Done"
#     NO_PHONE_NUMBER = "No Phone Number"
#     INVALID = "Invalid"
#     INVALID_NUMBER = "Invalid Number"
#     DND = "DND"
#     OUT_OF_TG = "Out of TG"
#     NOT_INTERESTED = "Not Interested"
#     # REJECTED = "Rejected"
#     SMS_RESTRICTED_STAGES = (
#         ENROLLMENT_DONE, NO_PHONE_NUMBER, INVALID, INVALID_NUMBER, DND, OUT_OF_TG  # NOT_INTERESTED,  # REJECTED
#     )


# @dataclass(frozen=True)
# class LiveWebinarConfig:
#     WEBINAR_LINK: AnyUrl = AnyUrl("https://opencv.org/ai-webinar")
#     FIRST_MSG: str = '[OpenCV AI Career Live-Webinar Reminder] - "3 Secrets to crack a $100K AI Job" will be LIVE in {0}. Webinar link: ' + str(WEBINAR_LINK)
#     SECOND_MSG: str = 'Dr. Satya Mallick (CEO of OpenCV) is LIVE now in the OpenCV Webinar! Ask your questions on CV, jobs & courses. Join here: ' + str(WEBINAR_LINK)
#     FIRST_SMS_BEFORE_WEBINAR_MAX: int = 2*60  # in minutes
#     FIRST_SMS_BEFORE_WEBINAR_MIN: int = 30    # in minutes


# class SalesCampaignConfig:
#     FIXED_MSG_SUFFIX = '{0} Hours - Early Bird Offer for Labor Day Sale at OpenCV to Enroll at 40% Discount on all courses. USE CODE: LABOR40 https://opencv.org/university/'
#     # FIXED_MSG_SUFFIX = 'New Course Launch! Get 50% off on "Advanced Vision Applications With DL & Transformers". Only {0} hours left. CODE: TX50 https://opencv.org/university/'
#     MESSAGE: str = f"Your_Custom_Message_Less_Than_{160 - len(FIXED_MSG_SUFFIX)+1}_Chars {FIXED_MSG_SUFFIX.format(16)}"


# class SMSConfigData(BaseModel):
#     first_msg: str
#     second_msg: str = LiveWebinarConfig.SECOND_MSG
#     webinar_link: AnyUrl = LiveWebinarConfig.WEBINAR_LINK
#     first_msg_before_webinar_max: int = LiveWebinarConfig.FIRST_SMS_BEFORE_WEBINAR_MAX
#     first_msg_before_webinar_min: int = LiveWebinarConfig.FIRST_SMS_BEFORE_WEBINAR_MIN
#     sales_campaign_msg: str = SalesCampaignConfig.MESSAGE
#     data_sms_cost_is_enable: dict = dict()
#     uploaded_webinars: dict = dict()
#     sent_sms_webinars: dict = dict()
#     uploaded_sales_campaign: dict = dict()
#     sent_sms_sales_campaign: dict = dict()


# class ResponseLiveWebinarConfig(BaseResponseModel):
#     data: SMSConfigData


# class PdDataFrameReturn(BaseModel):
#     is_success: bool
#     message: str = ""
#     data: pd.DataFrame = Field(default_factory=pd.DataFrame)

#     class Config:
#         arbitrary_types_allowed = True


# class SendSmsStats(BaseModel):
#     requested_sms_count: int = 0
#     actual_sms_count: int = 0
#     expected_dolor_required: float = 0.0
#     requested_countries: List[str] = Field(default_factory=list)
#     cant_send_sms_countries: List[str] = Field(default_factory=list)
#     sms_restricted_stages: List[str] = Field(default_factory=lambda: list(SmsRestrictedStages.SMS_RESTRICTED_STAGES))

#     class Config:
#         # Exclude sms_restricted_stages from being included in the JSON schema if necessary
#         json_encoders = {
#             type(SmsRestrictedStages.SMS_RESTRICTED_STAGES): lambda v: list(v)
#         }


# class ResponseSmsStats(BaseResponseModel):
#     data: SendSmsStats = SendSmsStats()


# class DateTime(BaseModel):
#     # PST Date and Time
#     HOURS: int
#     MINUTES: int
#     SECONDS: int
#     DAY: int
#     MONTH: int
#     YEAR: int
#     TIMEZONE: str = "-07:00"


# class SMSEligible(BaseModel):
#     eligible: bool = False
#     number: str = ""
#     message: str = ""
#     lead_id: str = ""
#     country: str = ""
#     cost: float = 0.0


# class SendSMSResponse(BaseResponseModel):
#     contact_number_info: SMSEligible
#     alternate_number_info: SMSEligible

# def timedelta_str_tzinfo(timedelta_str: str) -> timezone:
#     try:
#         # Parse the timedelta string (format: "+HH:MM" or "-HH:MM")
#         if timedelta_str == "US/Pacific":
#             return timezone(timedelta(hours=-7))

#         timedelta_str = timedelta_str.strip().replace("UTC", "")

#         sign = 1
#         start_index = 0
#         if timedelta_str[0] == '-':
#             sign = -1
#             start_index = 1
#         elif timedelta_str[0] == '+':
#             start_index = 1
#         parts = timedelta_str[start_index:].split(':')
#         hours = int(parts[0]) * sign
#         minutes = int(parts[1]) * sign if len(parts) > 1 else 0
        
#         return timezone(timedelta(hours=hours, minutes=minutes))
#     except Exception as e:
#         raise ValueError(f"Invalid timedelta format: {timedelta_str}. Use format like '+05:30' or '-07:00'. Error: {str(e)}")


class DateTimeValidator():
    datetime_str: str
    timedelta_str: str

    # @field_validator('datetime_str')
    def validate_datetime(cls, v):
        try:
            # Parse the datetime string without timezone
            dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            return dt
        except ValueError:
            raise ValueError("Invalid datetime format. Use YYYY-MM-DD HH:MM:SS.")

    # @field_validator('timedelta_str')
    def validate_timedelta(cls, v):
        return timedelta_str_tzinfo(v)
        
        
# class BulkPriceUpdateResponse(ResponseModel):
#     failed_countries_reason: Dict[str, str] = Field(default_factory=dict)


# class ResponseMSG:
#     LIVE_WEBINAR_RETRIEVE_SUCCESS: str = "SMS Configuration retrieved successfully."
#     REQUIRED_COLUMNS_ARE: str = "Required columns are"
#     COLUMNS_VALIDATED_SUCCESSFULLY = "Columns are validated successfully."
#     SEND_SMS_STATS_GENERATED_SUCCESSFULLY = "Send SMS stats generated successfully"
#     SEND_SMS_STATS_GENERATION_FAILED = "Send SMS stats generation failed"
#     NO_DATA_POINT_TO_GENERATE_STATES = "No data points to generate expected cost."
#     SEND_SMS_STATS_GENERATED_FOR_WEBINAR = "Send SMS stats generated for [{0} on {1}]"
#     SEND_SMS_STATS_GENERATED_FOR_WEBINAR_FAILED = "Send SMS stats generation failed for [{0} on {1}]"
#     SMS_HAS_BEEN_ALREADY_SCHEDULED = "SMS has been already scheduled for [{0} on {1}]"
#     LEADS_DATA_NOT_FOUND_FOR = "Leads data is not available for [{0} on {1}]"
#     SEND_SMS_SCHEDULED = "Sending sms scheduled for [{0} time {1}]."
#     SMS_LEAD_DATA_NOT_FOUND_FOR_WEBINAR = "SMS lead data not found for [{0} on {1}]"
#     SENDING_SMS_SCHEDULING_NOT_REQUESTED = "Scheduling SMS is not requested for [{0} on {1}]"
#     SCHEDULING_SMS_FOR_WEBINAR_REQUESTED = "Scheduling SMS for [{0} on {1}] requested"
#     SMS_NOT_ALLOWED_FOR_LEAD_STAGE = "SMS is not allowed for lead stage [{0}] for [{1} on {2}]"
#     WEBINAR_ALREADY_STARTED = "Webinar [{0} on {1}] already started. SMS will not be sent"
#     ELIGIBLE_FOR_SENDING_SMS = "Eligible to send SMS"
#     SMS_SENT_TO_CONTACT_NUMBER = "SMS sent/scheduled to contact number"
#     SMS_SENT_TO_ALTERNATE_NUMBER = "SMS sent/scheduled to alternate number"
#     SMS_SENT_TO_BOTH_NUMBERS = "SMS sent/scheduled to both numbers"
#     SMS_LEAD_DATA_CREATED: str = "SMS lead data created for [{0} on: {1}]"
#     SMS_LEAD_DATA_UPDATED: str = "SMS lead data updated for [{0} on: {1}]"
#     SMS_LEAD_DATA_DELETED: str = "SMS lead data deleted for [{0} on: {1}]"
#     SMS_LEAD_DATA_DOES_NOT_EXIST: str = "SMS lead data does not exist for [{0} on: {1}]"
#     SENT_SMS_INFO_NOT_AVAILABLE: str = "Sent SMS info not available for [{0} on: {1}]"
#     SENT_SMS_INFO_FOR_WEBINAR: str = "Sent SMS info for [{0} on: {1}]"
#     SENT_SMS_STATS: str = "Sent SMS stats for [{0} on: {1}]"
#     SMS_ALREADY_SCHEDULED_CANT_DELETE = "SMS already scheduled, can not be deleted [{0} on: {1}]"
#     SMS_COUNT_MUST_BE_1_OR_2 = "SMS count must be either one or two to schedule SMS [{0} on: {1}]"
#     SMS_SCHEDULE_NOT_REQUESTED = "SMS schedule is not requested for [{0} on: {1}]"
#     SMS_LENGTH_EXCEEDED = "Max allowed char count is {0} for [{1} on: {2}]"
#     BULK_PRICE_UPDATE_SUCCESS = "Bulk price update successful - updated_count: {0}, not_updated_count: {1}"


# class ResErrorMSG:
#     # Error message
#     NOT_CSV: str = "Error: File must be a CSV"
#     COLUMNS_NOT_AVAILABLE: str = "Column not available"
#     NUMBER_NOT_AVAILABLE_FOR_MSG: str = "Number not available for MSG"
#     NUMBER_IS_NOT_VALID: str = "Number is not valid"
#     SMS_DISABLED_FOR_COUNTRY: str = "SMS is disabled for the country"
#     SMS_ALREADY_SENT_TO: str = "SMS already sent to"
#     SMS_CANT_SEND_TO_ANY_NUMBER = "SMS can not be sent to any number"
#     BULK_PRICE_UPDATE_FAILED = "Bulk price update failed for all countries - updated_count: {0}, not_updated_count: {1}, failed_count: {2}"
#     BULK_PRICE_UPDATED_PARTIALLY = "Bulk price updated partially - updated_count: {0}, not_updated_count: {1}, failed_count: {2}"


# class SendMessageEndpointBody(BaseModel):
#     lead_id: str
#     # from_: Optional[str] = Field(default=None, alias="from")
#     to: List[str] | str
#     # Expected format: "YYYY-MM-DD HH:MM:SS" e.g., "2025-02-12 22:00:10"
#     schedule_datetime: Optional[str] = None
#     schedule_timezone: Optional[str] = None
#     body: str
#     ls_notes_body: Optional[str] = None

#     # @field_validator("ls_notes_body", mode="after")
#     # def validate_ls_notes_body(cls, value):
#     #     if value is None:
#     #         return cls.body

#     @field_validator("schedule_datetime")
#     def validate_schedule_datetime(cls, value):
#         if value is None:
#             return value

#         # First, try strict parsing using datetime.strptime
#         try:
#             datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
#             return value
#         except ValueError:
#             # If strict parse fails, try using dateparser as a fallback
#             dt = is_date_time_str_valid(date_time_str=value)
#             if dt is None:
#                 raise ValueError("schedule_datetime is not a valid date/time")
#             # Reformat the parsed datetime to the expected strict format
#             strict_format = dt.strftime("%Y-%m-%d %H:%M:%S")
#             if strict_format != value:
#                 raise ValueError("schedule_datetime must be in the format YYYY-MM-DD HH:MM:SS")
#             return value

#     # @field_validator("from_", mode="after")
#     # def validate_from(cls, value):
#     #     if value is None:
#     #         return value
#     #     validated = get_valid_phone_number(full_number=value, phone="")
#     #     # if validated_phone is None:
#     #     #     raise ValueError("Invalid phone number in 'from' field")
#     #     return None if validated is None else validated.strip().replace("-", "")

#     @field_validator("to", mode="after")
#     def validate_to(cls, value):
#         # Handle both a single string or a list of strings.
#         if isinstance(value, list):
#             validated_numbers = []

#             for num in value:
#                 validated = get_valid_phone_number(full_number=num, phone="")

#                 if validated is None:
#                     raise ValueError(f"Invalid phone number in one of the 'to' field: {num}")
#                     # continue

#                 else:
#                     validated = validated.strip().replace("-", "")
#                     validated_numbers.append(validated)

#             return list(set(validated_numbers))
#         else:
#             validated = get_valid_phone_number(full_number=value, phone="")

#             if validated is None:
#                 raise ValueError(f"Invalid phone number in 'to' field: {value}")

#             return None if validated is None else validated.strip().replace("-", "")


# if __name__ == "__main__":
#     print(SalesCampaignConfig.MESSAGE.format(16))
#     print(LiveWebinarConfig.FIRST_MSG.format("2 hours"))
#     print(LiveWebinarConfig.SECOND_MSG)
