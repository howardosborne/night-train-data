import time
import os.path
from unidecode import unidecode
import cyrtranslit
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of the spreadsheet.
SAMPLE_SPREADSHEET_ID = "11UJtmICqz0QaKZd2aMRryD1Gc0F2qRl-WeyE4i-nguQ"

SHEETS_NOT_USED=["translations", "classes","view_ontd_map", "view_ontd_list", "routes_inactive", "trips_inactive", "queries",  "runs"]
SHEETS=["agencies", "stops", "routes", "trips", "trip_stop", "calendar", "calendar_dates"]
SHEETS_OUT=["agency", "stops", "routes", "trips", "stop_times", "calendar", "calendar_dates"]

# Fields that are parsed as time
TIME_FIELDS=["arrival_time", "departure_time"]

# Fields that are parsed as dates
DATE_FIELDS=["start_date", "end_date", "date"]

# Fields that are required to list the entry in the resulting file
REQUIRED_FIELDS={"stop_times":["stop_sequence"], "routes": ["route_type"]}

# Fields that are renamed Format: {sheet_name: {old_name: new_name}}
RENAME_FIELDS={"stop_times":{"train_stop_id": "stop_id"}, "routes":{"agency_1": "agency_id"}}

# ToDo: Find a bettwer way to do this. This is a workaround to get the columns
COLUMNS=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK","AL"]
HEAD="!1:1"

def extract_sheet(service, sheet_id):
    sheet = service.spreadsheets()
    columns = []

    # Read header and get columns
    head_values = sheet.get(spreadsheetId=SAMPLE_SPREADSHEET_ID, ranges=SHEETS[sheet_id]+HEAD, fields="sheets(data(rowData(values(userEnteredFormat,formattedValue,textFormatRuns))))").execute().get("sheets")[0].get("data")[0].get("rowData")[0].get("values")
    for (index, head_value) in enumerate(head_values):
      if head_value.get("formattedValue"):
        if not (head_value.get("userEnteredFormat")
                and head_value.get("userEnteredFormat").get("textFormat")
                and head_value.get("userEnteredFormat").get("textFormat").get("foregroundColor")
                and head_value.get("userEnteredFormat").get("textFormat").get("foregroundColor").get("blue") == 1):
          columns.append(COLUMNS[index])

    # Build query
    ranges = []
    for column in columns:
      ranges.append(SHEETS[sheet_id]+"!"+column+":"+column)

    # Read the data by query
    data = sheet.values().batchGet(spreadsheetId=SAMPLE_SPREADSHEET_ID, ranges=ranges).execute()

    list_data = []
    for column in data.get("valueRanges", []):
      values = column.get("values", []);
      head = values[0][0]
      if head in RENAME_FIELDS.get(SHEETS_OUT[sheet_id], {}):
        head = RENAME_FIELDS[SHEETS_OUT[sheet_id]][head]

      for (index, element) in enumerate(values[1:len(values)]):
        if index not in list_data:
          list_data.append({})
        if len(element) > 0:
          # Parse fields
          if head in TIME_FIELDS:
            try:
              date = time.strptime(element[0], '%H:%M')
              list_data[index][head] = time.strftime('%H:%M:%S', date)
            except Exception as e:
              print(e)
              list_data[index][head] = element[0]  
          elif head in DATE_FIELDS:
            try:
              date = time.strptime(element[0], '%Y-%m-%d')
              list_data[index][head] = time.strftime('%Y%m%d', date)
            except:
              list_data[index][head] = element[0]
          elif isinstance(element[0], str):
            list_data[index][head] = unidecode(cyrtranslit.to_latin(element[0]))
          else:
            list_data[index][head] = element[0]
    

    list_data = list(filter(None, list_data))
    df=pd.DataFrame(list_data)
    
    # calendar.txt / calendar_dates.txt requires all field set
    if SHEETS_OUT[sheet_id] == "calendar" or SHEETS_OUT[sheet_id] == "calendar_dates":
      df.dropna(inplace=True)

    if SHEETS_OUT[sheet_id] in REQUIRED_FIELDS:
      df.dropna(subset=REQUIRED_FIELDS[SHEETS_OUT[sheet_id]], inplace=True)

    df.to_csv("./out/data/"+SHEETS_OUT[sheet_id]+".txt", index=False)

def main():
  # Google Sheets API credentials
  creds = None

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    for sheet_id in range(len(SHEETS)):
      extract_sheet(service, sheet_id)

  except HttpError as err:
    print(err)

if __name__ == "__main__":
  main()