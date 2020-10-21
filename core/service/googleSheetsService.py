from google.oauth2.service_account import Credentials
import gspread

class GoogleSheetsService:
    def __init__(self, creds):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        g_creds = Credentials.from_service_account_info(creds, scopes=scopes)
        self.gspread = gspread.authorize(g_creds)
        
    def saveWriterContents(self, title, writer):
        google_sheet = self.gspread.create(title)
        self.gspread.import_csv(
            google_sheet.id,
            writer.get_contents()
        )
    
    def share_sheet_by_title(self, title, emails):
        sheet = self.gspread.open(title)
        
        for email in emails:
            sheet.share(email, perm_type='user', role='writer', email_message = "This is an auto generated google sheet for pager duty time sheets")