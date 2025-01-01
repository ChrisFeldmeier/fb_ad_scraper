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
import re

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
    caption: Optional[str] = None
    cta_text: Optional[str] = None
    cta_type: Optional[str] = None
    link_url: Optional[str] = None
    image_url: Optional[str] = None
    platforms: List[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    delivery_start_date: Optional[str] = None
    delivery_end_date: Optional[str] = None
    countries: List[str] = None
    impressions: Optional[Dict] = None
    snapshot: Dict = None
    fetch_time: str = None

    def __post_init__(self):
        if self.fetch_time is None:
            self.fetch_time = datetime.now().isoformat()
        if self.platforms is None:
            self.platforms = []
        if self.countries is None:
            self.countries = []

class FacebookScraper:
    """Scraper for Facebook Ad Library"""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.session = requests.Session()
        os.makedirs(data_dir, exist_ok=True)
        
        # GraphQL doc_ids for different operations
        self.doc_ids = {
            'page_search': '9333890689970605',  # useAdLibraryTypeaheadSuggestionDataSourceQuery
            'page_ads': '8539922039449935'      # AdLibrarySearchPaginationQuery
        }
        
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
        self._extract_page_params()  # Extract parameters from Ad Library page

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
        
        # Get base parameters and add request specific ones
        data = self._get_request_params()
        data.update({
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'useAdLibraryTypeaheadSuggestionDataSourceQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': self.doc_ids['page_search']
        })

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
        
        # Get base parameters and add request specific ones
        data = self._get_request_params()
        data.update({
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'AdLibrarySearchPaginationQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': self.doc_ids['page_ads']
        })

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
            ad_archive_ids = set()
            
            # Get all edges from search results
            edges = data.get('data', {}).get('ad_library_main', {}).get('search_results_connection', {}).get('edges', [])
            
            for edge in edges:
                node = edge.get('node', {})
                collated_results = node.get('collated_results', [])
                
                for result in collated_results:
                    if not result:
                        continue
                        
                    ad_archive_id = result.get('ad_archive_id')
                    if not ad_archive_id:
                        continue
                        
                    ad_archive_ids.add(ad_archive_id)
                    
                    # Get snapshot data safely
                    snapshot = result.get('snapshot', {}) or {}
                    
                    # Extract body text safely
                    body_text = None
                    body = snapshot.get('body', {})
                    if isinstance(body, dict):
                        body_text = body.get('text')
                    elif isinstance(body, str):
                        body_text = body
                        
                    # Create ad object with all available fields
                    ad = {
                        'ad_archive_id': ad_archive_id,
                        'page_id': result.get('page_id'),
                        'page_name': result.get('page_name'),
                        'status': result.get('is_active'),
                        'ad_creation_time': result.get('start_date'),
                        'ad_delivery_start_time': result.get('start_date'),
                        'ad_delivery_stop_time': result.get('end_date'),
                        'currency': result.get('currency'),
                        'snapshot': snapshot,
                        'publisher_platforms': result.get('publisher_platform', []),
                        'languages': [],  # Not available in current response
                        'spend': None,  # Not available in current response
                        'impressions': result.get('impressions_with_index'),
                        'target_locations': [],  # Not available in current response
                        'target_ages': [],  # Not available in current response
                        'target_genders': [],  # Not available in current response
                        'target_interests': [],  # Not available in current response
                        'potential_reach': result.get('reach_estimate'),
                        'demographic_distribution': None,  # Not available in current response
                        'region_distribution': None,  # Not available in current response
                        'estimated_audience_size': None,  # Not available in current response
                        'ad_snapshot_url': None  # Not available in current response
                    }
                    ads.append(ad)

            logging.info(f"Found {len(ad_archive_ids)} unique ads (ad_archive_ids) for page ID: {page_id}")
            
            # Print detailed ad information
            if ads:
                print("\nDetailed Ad Information:")
                for i, ad in enumerate(ads, 1):
                    print("\n" + "=" * 100)
                    print(f"Ad {i} (Archive ID: {ad['ad_archive_id']})")
                    print("=" * 100)
                    
                    # Basic Information
                    print("\nBasic Information:")
                    print(f"Page Name: {ad['page_name']}")
                    print(f"Page ID: {ad['page_id']}")
                    print(f"Status: {ad['status']}")
                    print(f"Ad Creation Time: {ad['ad_creation_time']}")
                    print(f"Ad Delivery Start: {ad['ad_delivery_start_time']}")
                    print(f"Ad Delivery Stop: {ad['ad_delivery_stop_time']}")
                    
                    # Creative Content from Snapshot
                    snapshot = ad['snapshot']
                    if snapshot:
                        print("\nCreative Content:")
                        body = snapshot.get('body', {})
                        if isinstance(body, dict) and body.get('text'):
                            print(f"Body Text: {body['text']}")
                        elif isinstance(body, str):
                            print(f"Body Text: {body}")
                        
                        # Display image URLs from snapshot
                        images = snapshot.get('images', [])
                        if images:
                            print("\nAd Images:")
                            for idx, image in enumerate(images, 1):
                                if not isinstance(image, dict):
                                    continue
                                print(f"\nImage {idx}:")
                                if image.get('original_image_url'):
                                    print(f"Original URL: {image['original_image_url']}")
                                if image.get('resized_image_url'):
                                    print(f"Resized URL: {image['resized_image_url']}")
                        
                        # Display video URLs from snapshot
                        videos = snapshot.get('videos', [])
                        if videos:
                            print("\nAd Videos:")
                            for idx, video in enumerate(videos, 1):
                                if not isinstance(video, dict):
                                    continue
                                print(f"\nVideo {idx}:")
                                if video.get('video_hd_url'):
                                    print(f"HD URL: {video['video_hd_url']}")
                                if video.get('video_sd_url'):
                                    print(f"SD URL: {video['video_sd_url']}")
                                if video.get('video_preview_image_url'):
                                    print(f"Preview Image URL: {video['video_preview_image_url']}")
                        
                        # Display cards from snapshot
                        cards = snapshot.get('cards', [])
                        if cards:
                            print("\nCards:")
                            for idx, card in enumerate(cards, 1):
                                if not isinstance(card, dict):
                                    continue
                                print(f"\nCard {idx}:")
                                if card.get('body'):
                                    print(f"Body: {card['body']}")
                                if card.get('title'):
                                    print(f"Title: {card['title']}")
                                if card.get('caption'):
                                    print(f"Caption: {card['caption']}")
                                if card.get('cta_text'):
                                    print(f"CTA Text: {card['cta_text']}")
                                if card.get('link_url'):
                                    print(f"Link URL: {card['link_url']}")
                    
                    # Distribution & Performance
                    print("\nDistribution & Performance:")
                    print(f"Publisher Platforms: {ad['publisher_platforms']}")
                    print(f"Currency: {ad['currency']}")
                    print(f"Spend: {ad['spend']}")
                    print(f"Impressions: {ad['impressions']}")
                    print(f"Potential Reach: {ad['potential_reach']}")
                    
                    print("-" * 100)
            
            return ads

        except Exception as e:
            logging.error(f"Error getting page ads: {str(e)}")
            return []

    def get_ad_details(self, ad_archive_id: str, page_id: str) -> Optional[Dict]:
        """Get detailed information for a specific ad"""
        url = "https://www.facebook.com/api/graphql/"
        
        variables = {
            "adArchiveID": ad_archive_id,
            "pageID": page_id,
            "country": "DE",
            "sessionID": str(uuid.uuid4()),
            "source": None,
            "isAdNonPolitical": True,
            "isAdNotAAAEligible": False,
            "__relay_internal__pv__AdLibraryFinservGraphQLGKrelayprovider": True
        }
        
        # Get base parameters and add request specific ones
        data = self._get_request_params()
        data.update({
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'AdLibraryAdDetailsV2Query',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '9407590475934210'  # doc_id for ad details query
        })

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            
            # Save raw response
            self._save_raw_response(response.text, f"ad_detail_{ad_archive_id}")
            
            # Parse response
            data = self._parse_response(response.text)
            if not data or 'data' not in data:
                logging.error("Failed to parse ad detail response")
                return None

            # Extract ad details from response
            ad_details = data.get('data', {}).get('ad', {})
            
            if ad_details:
                print("\nDetailed Ad Information:")
                print("=" * 100)
                print(f"Ad Archive ID: {ad_archive_id}")
                print("=" * 100)
                
                # Print all available information
                print(json.dumps(ad_details, indent=2))
                
                return ad_details
            
            return None

        except Exception as e:
            logging.error(f"Error getting ad details: {str(e)}")
            return None

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

    def _extract_page_params(self):
        """Extract important parameters from Ad Library page"""
        try:
            response = self.session.get('https://www.facebook.com/ads/library/')
            if response.status_code == 200:
                page_content = response.text
                
                # Extract fb_dtsg token
                fb_dtsg_match = re.search(r'"DTSGInitData",\[\],{"token":"([^"]+)"', page_content)
                if fb_dtsg_match:
                    self.fb_dtsg = fb_dtsg_match.group(1)
                    logging.info(f"Found fb_dtsg token: {self.fb_dtsg}")
                
                # Extract client revision
                rev_match = re.search(r'"client_revision":(\d+),', page_content)
                if rev_match:
                    self.client_revision = rev_match.group(1)
                    logging.info(f"Found client revision: {self.client_revision}")
                
                # Extract LSD token
                lsd_match = re.search(r'"LSD",\[\],{"token":"([^"]+)"', page_content)
                if lsd_match:
                    self.lsd = lsd_match.group(1)
                    logging.info(f"Found LSD token: {self.lsd}")
                
                # Extract haste session
                hsi_match = re.search(r'"haste_session":"([^"]+)"', page_content)
                if hsi_match:
                    self.hsi = hsi_match.group(1)
                    logging.info(f"Found haste session: {self.hsi}")
                
                # Extract spin parameters
                spin_r_match = re.search(r'"__spin_r":(\d+),', page_content)
                if spin_r_match:
                    self.spin_r = spin_r_match.group(1)
                    logging.info(f"Found spin_r: {self.spin_r}")
                
                spin_b_match = re.search(r'"__spin_b":"([^"]+)"', page_content)
                if spin_b_match:
                    self.spin_b = spin_b_match.group(1)
                    logging.info(f"Found spin_b: {self.spin_b}")
                
                return True
                
        except Exception as e:
            logging.error(f"Error extracting page parameters: {str(e)}")
            return False

    def _get_request_params(self):
        """Generate parameters for GraphQL request"""
        return {
            'av': self.cookies.get('c_user', ''),
            '__user': self.cookies.get('c_user', ''),
            '__a': '1',
            '__req': self._get_next_req_id(),  # Increment request counter
            '__hs': getattr(self, 'hsi', ''),
            'dpr': '2',
            '__ccg': 'EXCELLENT',
            '__rev': getattr(self, 'client_revision', ''),
            '__s': self._generate_session_string(),
            '__hsi': str(int(time.time() * 1000)),
            '__dyn': '7xeUmxa13yoS1syUbFp432m2q1Dxu13wqovzEdF8ixy360CEbo9E3-xS6Ehw2nVEK12wvk0ie2O1VwBwXwEwgo9oO0n24oaEd86a3a1YwBgao6C0Mo6i588Egz898mwkE-U6-3e4UaEW0KrK2S1qxaawse5o4q0HUkw5CwSyES0gq0K-1Lwqp8aE2cwAwQwr86C0nC1TwmUaE2Tw',
            '__csr': self._generate_csr(),
            '__comet_req': '1',
            'fb_dtsg': getattr(self, 'fb_dtsg', ''),
            'jazoest': self._generate_jazoest(),
            'lsd': getattr(self, 'lsd', ''),
            '__spin_r': getattr(self, 'spin_r', ''),
            '__spin_b': getattr(self, 'spin_b', ''),
            '__spin_t': str(int(time.time())),
        }

    def _get_next_req_id(self):
        """Generate next request ID"""
        if not hasattr(self, '_req_counter'):
            self._req_counter = 0
        self._req_counter += 1
        return chr(97 + (self._req_counter % 26))  # a, b, c, ...

    def _generate_session_string(self):
        """Generate session string"""
        return f"{hex(int(time.time()))[2:]}:{hex(random.randint(0, 16**8))[2:]}"

    def _generate_csr(self):
        """Generate CSR parameter"""
        return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=32))

    def _generate_jazoest(self):
        """Generate jazoest parameter"""
        # Facebook uses a simple algorithm to generate this
        base = "2" + str(sum(ord(c) for c in self.fb_dtsg)) if hasattr(self, 'fb_dtsg') else "25730"
        return base

def main():
    parser = argparse.ArgumentParser(description='Facebook Ad Library Scraper')
    parser.add_argument('--mode', type=str, required=True, choices=['search', 'ads', 'detail'],
                      help='Scraping mode: search (find pages), ads (get ads by page ID), or detail (get detailed ad info)')
    parser.add_argument('--query', type=str, help='Search query for page search mode')
    parser.add_argument('--page-id', type=str, help='Page ID for ads mode')
    parser.add_argument('--ad-archive-id', type=str, help='Ad Archive ID for detail mode')
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
                
        elif args.mode == 'detail':
            if not args.ad_archive_id:
                parser.error("--ad-archive-id is required for detail mode")
            if not args.page_id:
                parser.error("--page-id is required for detail mode")
            ad_details = scraper.get_ad_details(args.ad_archive_id, args.page_id)
            if not ad_details:
                print(f"No details found for ad {args.ad_archive_id}")
                
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main() 