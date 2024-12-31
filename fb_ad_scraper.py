import requests
import json
import logging
import sys
import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import argparse
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fb_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class FacebookPage:
    """Data model for a Facebook page"""
    id: str
    name: str
    url: Optional[str] = None
    verification_status: Optional[str] = None
    fetch_time: str = None

    def __post_init__(self):
        if self.fetch_time is None:
            self.fetch_time = datetime.now().isoformat()

@dataclass
class FacebookAd:
    """Data model for a Facebook ad"""
    id: str
    page_id: str
    page_name: str
    title: Optional[str] = None
    body: Optional[str] = None
    snapshot_url: Optional[str] = None
    creation_time: Optional[str] = None
    fetch_time: str = None

    def __post_init__(self):
        if self.fetch_time is None:
            self.fetch_time = datetime.now().isoformat()

class FacebookScraper:
    """Scraper for Facebook Ad Library"""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.session = requests.Session()
        os.makedirs(data_dir, exist_ok=True)
        
        # Default cookies that seem to be required
        self.cookies = {
            'datr': '4SxPZUh5ui2ibThObJTg7Gfk',
            'c_user': '100001401300300',
            'ps_n': '1',
            'ps_l': '1',
            'oo': 'v1',
            'dpr': '1.7999999523162842',
            'sb': 'C0tgZxWq1EcVbQNrl4pca_tT',
            'fr': '15F1ccvaya1kduWHS.AWVlShrGaEOx_gX8XjP1KsX6vfw.Bnc7FK..AAA.0.0.BndAKq.AWWpP1WLcZM',
            'xs': '16:Ml14BMs_UQ3cjg:2:1699733852:-1:13648::AcX5IqEhPKWT3rrzLrJPdrbhy8FaZOiJrDdIWgzqR7C4vA'
        }
        
        self._setup_session()

    def _setup_session(self):
        """Setup session with default headers and cookies"""
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.facebook.com',
            'referer': 'https://www.facebook.com/ads/library/',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-asbd-id': '129477',
            'x-fb-friendly-name': 'useAdLibraryTypeaheadSuggestionDataSourceQuery',
            'x-fb-lsd': '1oMsaEuqGqy53uwEmB0Ecv'
        })
        
        # Update session cookies
        self.session.cookies.update(self.cookies)

    def search_pages(self, query: str) -> List[FacebookPage]:
        """Search for Facebook pages"""
        url = "https://www.facebook.com/api/graphql/"
        
        variables = {
            "queryString": query,
            "isMobile": False,
            "country": "DE",
            "adType": "ALL"
        }
        
        data = {
            'av': self.cookies.get('c_user', ''),
            '__user': self.cookies.get('c_user', ''),
            '__a': '1',
            '__req': 'z',
            '__hs': '20088.HYP:comet_plat_default_pkg.2.1.0.2.1',
            'dpr': '2',
            '__ccg': 'EXCELLENT',
            '__rev': '1019106461',
            '__s': '45kpqy:4p4zwy:eyzfmg',
            '__hsi': '7454603510249310343',
            '__dyn': '7xeUmxa13yoS1syUbFp432m2q1Dxu13wqovzEdF8ixy360CEbo9E3-xS6Ehw2nVEK12wvk0ie2O1VwBwXwEwgo9oO0n24oaEd86a3a1YwBgao6C0Mo6i588Egz898mwkE-U6-3e4UaEW0KrK2S1qxaawse5o4q0HUkw5CwSyES0gq0K-1Lwqp8aE2cwAwQwr86C0nC1TwmUaE2Tw',
            '__csr': 'hn25O9uJnKhAibkJqGLxtAAwgo561CwTwWzE460So1To2_w8S682Jw3Go00GLO0cNw',
            '__comet_req': '1',
            'fb_dtsg': 'NAcOag_5vxMjISOW5TqSct7wBqCgAaLpoGkRebRUTDTuGueVqtNQkhQ:16:1699733852',
            'jazoest': '25730',
            'lsd': '1oMsaEuqGqy53uwEmB0Ecv',
            '__spin_r': '1019106461',
            '__spin_b': 'trunk',
            '__spin_t': str(int(time.time())),
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'useAdLibraryTypeaheadSuggestionDataSourceQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '9333890689970605'
        }

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            
            # Save raw response
            self._save_raw_response(response.text, f"page_search_{query}")
            
            # Parse response
            data = self._parse_response(response.text)
            if not data or 'data' not in data:
                logging.error("Failed to parse page search response")
                return []

            pages = []
            page_results = data.get('data', {}).get('ad_library_main', {}).get('typeahead_suggestions', {}).get('page_results', [])
            for result in page_results:
                page = FacebookPage(
                    id=result.get('page_id'),
                    name=result.get('name'),
                    url=None,  # URL not provided in new response format
                    verification_status=result.get('verification')
                )
                if page.id:  # Only add if we got a valid ID
                    pages.append(page)

            logging.info(f"Found {len(pages)} pages for query: {query}")
            return pages

        except Exception as e:
            logging.error(f"Error searching pages: {str(e)}")
            return []

    def get_page_ads(self, page_id: str) -> List[FacebookAd]:
        """Get ads for a specific page"""
        url = "https://www.facebook.com/api/graphql/"
        
        variables = {
            "activeStatus": "active",
            "adType": "ALL",
            "bylines": [],
            "collationToken": str(uuid.uuid4()),
            "contentLanguages": [],
            "countries": ["DE"],
            "cursor": None,
            "excludedIDs": None,
            "first": 30,
            "isTargetedCountry": False,
            "location": None,
            "mediaType": "all",
            "multiCountryFilterMode": None,
            "pageIDs": [],
            "potentialReachInput": None,
            "publisherPlatforms": [],
            "queryString": "",
            "regions": None,
            "searchType": "page",
            "sessionID": str(uuid.uuid4()),
            "sortData": None,
            "source": None,
            "startDate": None,
            "v": "96184a",
            "viewAllPageID": page_id
        }
        
        data = {
            'av': '100001401300300',
            '__user': '100001401300300',
            '__a': '1',
            '__req': '10',
            '__hs': '20088.HYP:comet_plat_default_pkg.2.1.0.2.1',
            'dpr': '2',
            '__ccg': 'EXCELLENT',
            '__rev': '1019106461',
            '__s': '45kpqy:4p4zwy:eyzfmg',
            '__hsi': '7454603510249310343',
            '__dyn': '7xeUmxa13yoS1syUbFp432m2q1Dxu13wqovzEdF8ixy360CEbo9E3-xS6Ehw2nVEK12wvk0ie2O1VwBwXwEwgo9oO0n24oaEd86a3a1YwBgao6C0Mo6i588Egz898mwkE-U6-3e4UaEW0KrK2S1qxaawse5o4q0HUkw5CwSyES0gq0K-1Lwqp8aE2cwAwQwr86C0nC1TwmUaE2Tw',
            '__csr': 'hn25O9uJnKhAibkJqGLxtAAwgo561CwTwWzE460So1To2_w8S682Jw3Go00GLO0cNw',
            '__comet_req': '1',
            'fb_dtsg': 'NAcOag_5vxMjISOW5TqSct7wBqCgAaLpoGkRebRUTDTuGueVqtNQkhQ:16:1699733852',
            'jazoest': '25730',
            'lsd': '1oMsaEuqGqy53uwEmB0Ecv',
            '__spin_r': '1019106461',
            '__spin_b': 'trunk',
            '__spin_t': str(int(time.time())),
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'AdLibrarySearchPaginationQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '8539922039449935'
        }

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            
            # Save raw response
            self._save_raw_response(response.text, f"page_ads_{page_id}")
            
            # Parse response
            data = self._parse_response(response.text)
            if not data or 'data' not in data:
                logging.error("Failed to parse page ads response")
                return []

            ads = []
            edges = data.get('data', {}).get('ads_library_search', {}).get('edges', [])
            for edge in edges:
                node = edge.get('node', {})
                ad = FacebookAd(
                    id=node.get('id'),
                    page_id=page_id,
                    page_name=node.get('page_name'),
                    title=node.get('title'),
                    body=node.get('body'),
                    snapshot_url=node.get('snapshot_url'),
                    creation_time=node.get('creation_time')
                )
                ads.append(ad)

            logging.info(f"Found {len(ads)} ads for page ID: {page_id}")
            return ads

        except Exception as e:
            logging.error(f"Error getting page ads: {str(e)}")
            return []

    def _generate_session_id(self) -> str:
        """Generate a session ID"""
        return f"{int(time.time())}_{random.randint(1000, 9999)}"

    def _parse_response(self, response_text: str) -> Dict:
        """Parse response text to JSON"""
        try:
            # Remove potential "for (;;);" prefix
            if response_text.startswith('for (;;);'):
                response_text = response_text[9:]
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {str(e)}")
            return {}

    def _save_raw_response(self, response_text: str, prefix: str):
        """Save raw response for debugging"""
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logging.info(f"Saved raw response to {filepath}")

def main():
    parser = argparse.ArgumentParser(description='Facebook Ad Library Scraper')
    parser.add_argument('--mode', type=str, required=True, choices=['search', 'ads'],
                      help='Scraping mode: search (find pages) or ads (get ads by page ID)')
    parser.add_argument('--query', type=str, help='Search query for page search mode')
    parser.add_argument('--page-id', type=str, help='Page ID for ads mode')
    parser.add_argument('--data-dir', type=str, default='data', help='Directory for storing data')
    
    args = parser.parse_args()
    
    try:
        scraper = FacebookScraper(data_dir=args.data_dir)
        
        if args.mode == 'search':
            if not args.query:
                parser.error("--query is required for search mode")
            pages = scraper.search_pages(args.query)
            if pages:
                print("\nFound Pages:")
                print("-" * 80)
                print(f"{'Page ID':<20} {'Name':<30} {'Verification':<15} {'Category':<15}")
                print("-" * 80)
                for page in pages:
                    print(f"{page.id:<20} {page.name:<30} {page.verification_status:<15}")
                print("-" * 80)
                print(f"Total pages found: {len(pages)}")
                
        elif args.mode == 'ads':
            if not args.page_id:
                parser.error("--page-id is required for ads mode")
            ads = scraper.get_page_ads(args.page_id)
            if ads:
                print(f"\nFound {len(ads)} ads for page ID: {args.page_id}")
                
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main() 