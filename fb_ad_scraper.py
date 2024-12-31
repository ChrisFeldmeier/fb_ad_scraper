import requests
import time
import random
import json
from datetime import datetime
import logging
from urllib.parse import urlencode, quote
import sys
from typing import Dict, Optional, List
import backoff
from bs4 import BeautifulSoup
import re
import uuid
import argparse
import browser_cookie3
import os
from dataclasses import dataclass, asdict
from datetime import datetime

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
class FacebookAd:
    """Data model for a Facebook ad"""
    id: str
    page_id: str
    page_name: str
    page_url: str
    snapshot_url: Optional[str] = None
    creation_time: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    delivery_start_time: Optional[str] = None
    delivery_end_time: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    link_url: Optional[str] = None
    platform: Optional[str] = None
    currency: Optional[str] = None
    spend_range: Optional[Dict] = None
    impressions_range: Optional[Dict] = None
    images: List[str] = None
    videos: List[str] = None
    fetch_time: str = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.videos is None:
            self.videos = []
        if self.fetch_time is None:
            self.fetch_time = datetime.now().isoformat()

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

class DataStorage:
    """Handles data storage and retrieval"""
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = ['ads', 'pages', 'raw', 'debug']
        for dir_name in directories:
            dir_path = os.path.join(self.base_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)

    def save_ads(self, ads: List[FacebookAd], page_id: str):
        """Save ads to JSON file"""
        filename = f"ads_{page_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.base_dir, 'ads', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(ad) for ad in ads], f, indent=2, ensure_ascii=False)
        logging.info(f"Saved {len(ads)} ads to {filepath}")

    def save_pages(self, pages: List[FacebookPage], query: str):
        """Save pages to JSON file"""
        filename = f"pages_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.base_dir, 'pages', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(page) for page in pages], f, indent=2, ensure_ascii=False)
        logging.info(f"Saved {len(pages)} pages to {filepath}")

    def save_raw_response(self, response_text: str, prefix: str, identifier: str):
        """Save raw response for debugging"""
        filename = f"{prefix}_{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.base_dir, 'raw', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logging.info(f"Saved raw response to {filepath}")

    def save_debug_info(self, data: Dict, prefix: str, identifier: str):
        """Save debug information"""
        filename = f"{prefix}_{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.base_dir, 'debug', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved debug info to {filepath}")

class RequestManager:
    """Handles API requests and rate limiting"""
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def wait_if_needed(self):
        """Ensure minimum delay between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ValueError),
        max_tries=3
    )
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a request with retry logic and rate limiting"""
        self.wait_if_needed()
        
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        
        return response 

class FacebookAdScraper:
    """Main scraper class for Facebook Ad Library"""
    def __init__(self, data_dir: str = "data"):
        self.request_manager = RequestManager()
        self.data_storage = DataStorage(data_dir)
        self.base_urls = {
            'graphql': "https://www.facebook.com/api/graphql/",
            'ads_library': "https://www.facebook.com/ads/library/async/search_ads/",
            'ads_archive': "https://www.facebook.com/ads/archive/render_ad/"
        }
        self.default_headers = {
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
            'priority': 'u=1, i'
        }
        self.cookies = {}
        self.doc_ids = {
            'search_pagination': '8539922039449935',
            'page_ads': '8993262700713050',
            'ad_details': '9407590475934210',
            'page_search': '9333890689970605'
        }
        self._init_session()

    def _get_browser_cookies(self) -> Dict[str, str]:
        """Get cookies from browser"""
        cookies = {}
        
        # Try Chrome with different profiles
        chrome_paths = [
            '~/Library/Application Support/Google/Chrome/Default/Cookies',
            '~/Library/Application Support/Google/Chrome/Profile 1/Cookies',
            '~/Library/Application Support/Google/Chrome/Profile 2/Cookies'
        ]
        
        for path in chrome_paths:
            try:
                chrome_cookies = browser_cookie3.chrome(
                    cookie_file=os.path.expanduser(path),
                    domain_name='.facebook.com'
                )
                chrome_dict = {cookie.name: cookie.value for cookie in chrome_cookies}
                if 'c_user' in chrome_dict and 'xs' in chrome_dict:
                    logging.info(f"Successfully retrieved cookies from Chrome path: {path}")
                    cookies.update(chrome_dict)
                    return cookies
            except Exception as e:
                logging.debug(f"Could not get cookies from Chrome path {path}: {str(e)}")

        # Try Firefox with different profiles
        firefox_paths = [
            '~/Library/Application Support/Firefox/Profiles',
            '~/Library/Mozilla/Firefox/Profiles'
        ]
        
        for base_path in firefox_paths:
            try:
                expanded_path = os.path.expanduser(base_path)
                if os.path.exists(expanded_path):
                    for profile in os.listdir(expanded_path):
                        profile_path = os.path.join(expanded_path, profile, 'cookies.sqlite')
                        if os.path.exists(profile_path):
                            try:
                                firefox_cookies = browser_cookie3.firefox(
                                    cookie_file=profile_path,
                                    domain_name='.facebook.com'
                                )
                                firefox_dict = {cookie.name: cookie.value for cookie in firefox_cookies}
                                if 'c_user' in firefox_dict and 'xs' in firefox_dict:
                                    logging.info(f"Successfully retrieved cookies from Firefox profile: {profile}")
                                    cookies.update(firefox_dict)
                                    return cookies
                            except Exception as e:
                                logging.debug(f"Could not get cookies from Firefox profile {profile}: {str(e)}")
            except Exception as e:
                logging.debug(f"Could not access Firefox path {base_path}: {str(e)}")

        # If no cookies found, try default browser_cookie3 behavior
        try:
            chrome_cookies = browser_cookie3.chrome(domain_name='.facebook.com')
            chrome_dict = {cookie.name: cookie.value for cookie in chrome_cookies}
            if 'c_user' in chrome_dict and 'xs' in chrome_dict:
                logging.info("Successfully retrieved cookies from default Chrome location")
                cookies.update(chrome_dict)
                return cookies
        except Exception as e:
            logging.debug(f"Could not get cookies from default Chrome location: {str(e)}")

        try:
            firefox_cookies = browser_cookie3.firefox(domain_name='.facebook.com')
            firefox_dict = {cookie.name: cookie.value for cookie in firefox_cookies}
            if 'c_user' in firefox_dict and 'xs' in firefox_dict:
                logging.info("Successfully retrieved cookies from default Firefox location")
                cookies.update(firefox_dict)
                return cookies
        except Exception as e:
            logging.debug(f"Could not get cookies from default Firefox location: {str(e)}")

        if not cookies:
            logging.error("Could not find valid Facebook cookies in any browser")
            logging.error("Please ensure you are logged into Facebook in Chrome or Firefox")
            logging.error("Chrome paths checked: " + ", ".join(chrome_paths))
            logging.error("Firefox paths checked: " + ", ".join(firefox_paths))
            raise ValueError("Please log into Facebook in Chrome or Firefox first")

        return cookies

    def _init_session(self):
        """Initialize session with required tokens"""
        try:
            # Get browser cookies
            browser_cookies = self._get_browser_cookies()
            if browser_cookies:
                self.cookies.update(browser_cookies)
                self.request_manager.session.cookies.update(browser_cookies)

            # First request to get initial cookies
            initial_response = self.request_manager.make_request(
                'GET',
                'https://www.facebook.com/',
                headers=self.default_headers
            )

            # Update cookies from initial response
            for cookie in initial_response.cookies:
                self.cookies[cookie.name] = cookie.value
            self.request_manager.session.cookies.update(self.cookies)

            # Make request to ads library to get additional tokens
            ads_response = self.request_manager.make_request(
                'GET',
                'https://www.facebook.com/ads/library/',
                headers=self.default_headers
            )

            # Update cookies from ads library response
            for cookie in ads_response.cookies:
                self.cookies[cookie.name] = cookie.value
            self.request_manager.session.cookies.update(self.cookies)

            # Extract tokens from HTML
            soup = BeautifulSoup(ads_response.text, 'html.parser')
            
            # Find fb_dtsg token
            for script in soup.find_all('script'):
                if script.string and 'DTSGInitData' in script.string:
                    dtsg_match = re.search(r'"DTSGInitData",\[\],{"token":"(.*?)"', script.string)
                    if dtsg_match:
                        fb_dtsg = dtsg_match.group(1)
                        self.cookies['fb_dtsg'] = fb_dtsg
                        logging.info("Successfully extracted fb_dtsg token")

                # Find LSD token
                if script.string and 'LSD' in script.string:
                    lsd_match = re.search(r'"LSD",\[\],{"token":"(.*?)"', script.string)
                    if lsd_match:
                        self.default_headers['x-fb-lsd'] = lsd_match.group(1)
                        logging.info("Successfully extracted LSD token")

            # Ensure we have all required cookies
            required_cookies = ['c_user', 'xs', 'fr', 'datr']
            missing_cookies = [cookie for cookie in required_cookies if cookie not in self.cookies]
            if missing_cookies:
                logging.warning(f"Missing required cookies: {missing_cookies}")
                raise ValueError("Missing required cookies for authentication")

            # Make a test request to verify authentication
            test_response = self.request_manager.make_request(
                'GET',
                'https://www.facebook.com/ads/library/async/search_ads/',
                headers=self.default_headers,
                params={'q': '', 'count': 1, 'active_status': 'all', 'ad_type': 'all', 'countries[0]': 'DE'}
            )

            if 'Nicht angemeldet' in test_response.text or 'Please log in' in test_response.text:
                raise ValueError("Authentication failed - Please ensure you are logged into Facebook in your browser")

            # Save debug info
            self.data_storage.save_debug_info(
                {
                    'cookies': self.cookies,
                    'headers': self.default_headers,
                    'authentication_status': 'success'
                },
                'session_init',
                datetime.now().strftime('%Y%m%d_%H%M%S')
            )

            logging.info("Session initialized successfully with authentication")

        except Exception as e:
            logging.error(f"Error initializing session: {str(e)}")
            raise

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON response with error handling"""
        try:
            # Handle multiple JSON objects
            if '\n' in response_text:
                for part in response_text.split('\n'):
                    if part.strip():
                        try:
                            data = json.loads(part)
                            if isinstance(data, dict):
                                return data
                        except json.JSONDecodeError:
                            continue
            
            # Handle single JSON object
            text = response_text.replace('for (;;);', '')
            return json.loads(text)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {str(e)}")
            raise

    def _extract_ad_data(self, node: Dict, page_data: Dict) -> FacebookAd:
        """Extract ad data from API response"""
        return FacebookAd(
            id=node.get('id'),
            page_id=page_data.get('id'),
            page_name=page_data.get('name'),
            page_url=page_data.get('url'),
            snapshot_url=node.get('snapshot_url'),
            creation_time=node.get('creation_time'),
            start_date=node.get('start_date'),
            end_date=node.get('end_date'),
            delivery_start_time=node.get('delivery_start_time'),
            delivery_end_time=node.get('delivery_end_time'),
            title=node.get('title'),
            body=node.get('body'),
            link_url=node.get('link_url'),
            platform=node.get('platform'),
            currency=node.get('currency'),
            spend_range=node.get('spend_range'),
            impressions_range=node.get('impressions_range'),
            images=[img.get('url') for img in node.get('images', [])] if node.get('images') else [],
            videos=[vid.get('url') for vid in node.get('videos', [])] if node.get('videos') else []
        )

    def get_page_ads(self, page_id: str, country: str = "DE") -> List[FacebookAd]:
        """Get all ads for a specific page"""
        try:
            data = {
                'av': self.cookies.get('c_user', ''),
                '__aaid': '0',
                '__user': self.cookies.get('c_user', ''),
                '__a': '1',
                '__req': 'v',
                '__hs': '20088.HYP:comet_plat_default_pkg.2.1.0.2.1',
                'dpr': '2',
                '__ccg': 'EXCELLENT',
                '__rev': '1019106461',
                '__s': 'k5lisp:4p4zwy:eyzfmg',
                '__hsi': '7454603510249310343',
                '__dyn': ('7xeUmxa13yoS1syUbFp432m2q1Dxu13wqovzEdF8ixy360CEbo9E3-xS6Ehw2nVEK12wvk0ie2O1VwBwXwEw'
                         'go9oO0n24oaEd86a3a1YwBgao6C0Mo6i588Egz898mwkE-U6-3e4UaEW0KrK2S1qxaawse5o4q0HUkw5CwSyES'
                         '0gq0K-1Lwqp8aE2cwAwQwr86C0nC1TwmUaE2Tw'),
                '__csr': 'hn25O9uJnKhAibkJqGLxtAAwgo561CwTwWzE460So1To2_w8S682Jw3Go00GLO0cNw',
                '__comet_req': '1',
                'fb_dtsg': self.cookies.get('fb_dtsg', ''),
                'jazoest': '25730',
                'lsd': self.default_headers.get('x-fb-lsd', ''),
                '__spin_r': '1019106461',
                '__spin_b': 'trunk',
                '__spin_t': str(int(time.time())),
                '__jssesw': '1',
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'AdLibrarySearchPaginationQuery',
                'variables': json.dumps({
                    'activeStatus': 'active',
                    'adType': 'ALL',
                    'bylines': [],
                    'collationToken': str(uuid.uuid4()),
                    'contentLanguages': [],
                    'countries': [country],
                    'cursor': None,
                    'excludedIDs': None,
                    'first': 30,
                    'isTargetedCountry': False,
                    'location': None,
                    'mediaType': 'all',
                    'multiCountryFilterMode': None,
                    'pageIDs': [],
                    'potentialReachInput': None,
                    'publisherPlatforms': [],
                    'queryString': '',
                    'regions': None,
                    'searchType': 'page',
                    'sessionID': str(uuid.uuid4()),
                    'sortData': None,
                    'source': None,
                    'startDate': None,
                    'v': '96184a',
                    'viewAllPageID': page_id
                }),
                'server_timestamps': True,
                'doc_id': '8539922039449935'
            }

            headers = self.default_headers.copy()
            headers.update({
                'x-fb-friendly-name': 'AdLibrarySearchPaginationQuery',
                'x-asbd-id': '129477',
                'priority': 'u=1, i',
                'sec-ch-ua-full-version-list': '"Google Chrome";v="131.0.6778.205", "Chromium";v="131.0.6778.205", "Not_A Brand";v="24.0.0.0"',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform-version': '"14.5.0"',
                'referer': f'https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&is_targeted_country=false&media_type=all&search_type=page&view_all_page_id={page_id}'
            })

            all_ads = []
            cursor = None
            page_number = 0

            while True:
                if cursor:
                    variables = json.loads(data['variables'])
                    variables['cursor'] = cursor
                    data['variables'] = json.dumps(variables)

                response = self.request_manager.make_request(
                    'POST',
                    self.base_urls['graphql'],
                    headers=headers,
                    data=data
                )

                # Save raw response
                self.data_storage.save_raw_response(
                    response.text,
                    f'page_ads_{page_id}',
                    f'page_{page_number}'
                )

                # Parse response
                json_data = self._parse_json_response(response.text)
                
                # Log the full response for debugging
                self.data_storage.save_debug_info(
                    json_data,
                    f'response_debug_{page_id}',
                    f'page_{page_number}'
                )
                
                # Extract ads from response
                if json_data and isinstance(json_data, dict):
                    if 'errors' in json_data:
                        logging.error(f"GraphQL errors: {json.dumps(json_data['errors'], indent=2)}")
                        break
                        
                    if 'data' in json_data:
                        ads_data = json_data['data'].get('ads_library_search', {})
                        
                        if isinstance(ads_data, dict) and 'edges' in ads_data:
                            new_ads = []
                            for edge in ads_data['edges']:
                                try:
                                    node = edge['node']
                                    page_data = {
                                        'id': node.get('page_id'),
                                        'name': node.get('page_name'),
                                        'url': node.get('page_url')
                                    }
                                    ad = self._extract_ad_data(node, page_data)
                                    new_ads.append(ad)
                                except Exception as e:
                                    logging.error(f"Error extracting ad data: {str(e)}")
                                    continue
                            
                            if new_ads:
                                all_ads.extend(new_ads)
                                logging.info(f"Found {len(new_ads)} ads on page {page_number + 1}. Total: {len(all_ads)}")
                                
                                # Check for next page
                                page_info = ads_data.get('page_info', {})
                                if page_info and page_info.get('has_next_page'):
                                    cursor = page_info.get('end_cursor')
                                    if cursor:
                                        page_number += 1
                                        time.sleep(random.uniform(2, 4))  # Add delay between pages
                                        continue
                        else:
                            logging.warning(f"Unexpected ads_data structure: {json.dumps(ads_data, indent=2)}")
                    else:
                        logging.warning("No data field in response")
                else:
                    logging.warning("Invalid JSON response structure")
                
                break

            # Save all collected ads
            if all_ads:
                self.data_storage.save_ads(all_ads, page_id)
                logging.info(f"Successfully saved {len(all_ads)} ads")
            else:
                logging.warning("No ads were collected")

            return all_ads

        except Exception as e:
            logging.error(f"Error getting page ads: {str(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Facebook Ad Library Scraper')
    parser.add_argument('--mode', type=str, required=True, choices=['page'],
                      help='Scraping mode: page (get ads by page ID)')
    parser.add_argument('--page-id', type=str, help='Page ID for page mode')
    parser.add_argument('--country', type=str, default='DE', help='Country code (default: DE)')
    parser.add_argument('--data-dir', type=str, default='data', help='Directory for storing data (default: data)')
    
    args = parser.parse_args()
    
    try:
        scraper = FacebookAdScraper(data_dir=args.data_dir)
        
        if args.mode == 'page':
            if not args.page_id:
                parser.error("--page-id is required for page mode")
            
            results = scraper.get_page_ads(args.page_id, args.country)
            logging.info(f"Successfully scraped {len(results)} ads for page ID: {args.page_id}")
            
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 