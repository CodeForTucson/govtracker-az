import requests
import typing
import json
from datetime import date
from bs4 import BeautifulSoup

class SirePub:

    _sirepub_url = "https://www.tucsonaz.gov/sirepub/meetresults.aspx?view=tabs&startdate={}&enddate={}"
    _sirepub_base_url = 'https://www.tucsonaz.gov/sirepub/{}'

    def __init__(self):
        pass

    def _get_meetings_request(self, start_date: date, end_date: date) -> str:

        fmt = '%m-%d-%Y'

        start_fmt_str = start_date.strftime(fmt)
        end_fmt_str = end_date.strftime(fmt)

        # returns xml document outside browser

        reply = requests.get(self._sirepub_url.format(start_fmt_str, end_fmt_str))

        return reply.content

    def get_meetings(self, start_date: date, end_date: date) -> str:

        return self._get_meetings_request(start_date, end_date)

    def parse_meetings_html(self, html: str) -> str:

        parser = 'html.parser'
        soup = BeautifulSoup(html, parser)

        sirepub_results = []

        # header isn't in table header tag
        for result_table_row in soup.find_all('tr')[1:]:

            date = result_table_row.find('td', { 'class' : 'tableCell_left' })
            meeting = result_table_row.find('td', { 'class' : 'tableCell_center' })
            documents = result_table_row.find_all('td', { 'class' : 'tableCell_right' })

            meeting = {
                "date": date.string.strip(),
                "meeting": meeting.string.strip(),
                "documents": []
            }

            for document_table_cell in documents:
                for anchor in document_table_cell.find_all('a'):
                    meeting.get("documents", []).append(self._sirepub_base_url.format(anchor.get('href')))
            
            sirepub_results.append(meeting)

        return sirepub_results

    def save_meetings_data(self, meetings, filename: str):

        with open(filename, 'w') as file:
            json.dump(meetings, file)

if __name__ == "__main__":
    
    city_tucson_sirepub = SirePub()

    start_date = date(2019, 1, 1)
    end_date = date(2019, 12, 31)
    
    sirepub_raw_results = city_tucson_sirepub.get_meetings(start_date, end_date)

    sirepub_results = city_tucson_sirepub.parse_meetings_html(sirepub_raw_results)

    city_tucson_sirepub.save_meetings_data(sirepub_results, 'meetings.json')

