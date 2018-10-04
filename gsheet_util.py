import time
from traceback import format_exc

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

CREDENTIAL_FILE_PATH = 'credentials.json'
TOKEN_FILE_PATH = 'token.json'
GSHEET_ID = '1sCL178XB0hsScwCYt_xtkhVkLh--OXAALF7TpxHJR5A'
GSHEET_SNAME = 'sheet1'
PHYSICAL_SERVER_NUMBER = 1
MAX_GSHEET_REQUEST_NUMBER = 5


def _init_service():
    store = file.Storage(TOKEN_FILE_PATH)
    creds = store.get()
    if not creds or creds.invalid:
        # spreadsheet read/write permission.
        scopes = 'https://www.googleapis.com/auth/spreadsheets'
        flow = client.flow_from_clientsecrets(CREDENTIAL_FILE_PATH, scopes)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service


def _wait():
    time.sleep(PHYSICAL_SERVER_NUMBER)


service = None


def _assert_keys_are_str(keys):
    for key in keys:
        assert type(key) == str


def _get_header_row(gsheet_service):
    for _ in range(MAX_GSHEET_REQUEST_NUMBER):
        _wait()
        try:
            result = gsheet_service.values().get(
                spreadsheetId=GSHEET_ID,
                range='{}!A1:1'.format(GSHEET_SNAME)).execute()
            values = result.get('values', [])
            if len(values) > 0:
                columns = values[0]
            else:
                columns = []
            return columns
        except:
            print(format_exc())

    return None


def _update_header_row(gsheet_service, columns):
    for _ in range(MAX_GSHEET_REQUEST_NUMBER):
        _wait()
        try:
            result = gsheet_service.values().update(
                spreadsheetId=GSHEET_ID,
                range='{}!A1:1'.format(GSHEET_SNAME),
                valueInputOption="USER_ENTERED",
                body={'values': [columns]}).execute()
            # print(result)
            return True
        except:
            print(format_exc())
    return False


def _append_row(gsheet_service, columns, d):
    for _ in range(MAX_GSHEET_REQUEST_NUMBER):
        _wait()
        try:
            result = service.spreadsheets().values().append(
                spreadsheetId=GSHEET_ID,
                range='{}!A2'.format(GSHEET_SNAME),
                valueInputOption="USER_ENTERED",
                body={
                    'values': [[str(d.get(column, '')) for column in columns]]
                }).execute()
            # print(result)
            return True
        except:
            print(format_exc())
    return False


def gsheet_write_row_by_dict(d):
    """
        성공하면 True 리턴, 실패하면 False 리턴.
    """
    global service
    if service is None:
        service = _init_service()
    assert service

    gsheet_service = service.spreadsheets()
    assert gsheet_service

    keys = sorted(d.keys())
    _assert_keys_are_str(keys)

    columns = _get_header_row(gsheet_service)
    if columns is None:
        return False

    columns = columns + [key for key in keys if key not in columns]
    is_success = _update_header_row(gsheet_service, columns)
    if not is_success:
        return False

    return _append_row(gsheet_service, columns, d)
