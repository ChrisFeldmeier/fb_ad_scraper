# Facebook Ad Library Scraper

A Python tool for scraping ad data from the Facebook Ad Library. This tool allows you to search for Facebook pages, retrieve their ads, and get detailed information about specific ads.

## Features

- Search for Facebook pages by name
- Get all active ads for a specific page
- Get detailed ad information including targeting and demographics
- Save raw API responses for debugging
- Handle rate limiting and session management
- Detailed targeting information for ads (EU region)

## Installation

1. Clone the repository
2. Install the requirements:
```bash
pip install requests
```

## Usage

The scraper has three main modes of operation:

### 1. Search Mode

Search for Facebook pages by name:

```bash
python fb_ad_scraper.py --mode search --query "Snocks"
```

Example output:
```
Found Pages:
--------------------------------------------------------------------------------
Page ID             Name                           Verification    Category
--------------------------------------------------------------------------------
109806077081081    Snocks                         NOT_VERIFIED    Textilunternehmen
--------------------------------------------------------------------------------
Total pages found: 1
```

### 2. Ads Mode

Get all active ads for a specific page:

```bash
python fb_ad_scraper.py --mode ads --page-id "109806077081081"
```

Example output:
```
Detailed Ad Information:
====================================================================================================
Ad 1 (Archive ID: 569506902719378)
====================================================================================================

Basic Information:
Page Name: Snocks
Page ID: 109806077081081
Status: Active
Ad Creation Time: 2024-01-01
Ad Delivery Start: 2024-01-01
Ad Delivery Stop: 2024-12-31

Creative Content:
Body Text: Experience our premium basics...

Ad Images:
Image 1:
Original URL: https://scontent.xx.fbcdn.net/v/...
Resized URL: https://scontent.xx.fbcdn.net/v/...

Distribution & Performance:
Publisher Platforms: FACEBOOK, INSTAGRAM
Currency: EUR
Impressions: 10K-15K
```

### 3. Ad Detail Mode

Get detailed information about a specific ad:

```bash
python fb_ad_scraper.py --mode adsdetail --ad-archive-id "569506902719378" --page-id "109806077081081"
```

Example output:
```
Ad Details:
Archive ID: 569506902719378
Status: Active
Runtime: 2024-01-01 to 2024-12-31

Targeting Information:
Target Locations: Deutschland, Österreich
Gender: Alle
Age Range: 25-64
Total EU Reach: 785

Demographic Breakdown:
DE:
  25-34: Male: 28, Female: 10, Other: 0
  35-44: Male: 45, Female: 28, Other: 1
  45-54: Male: 105, Female: 49, Other: 4
  55-64: Male: 172, Female: 50, Other: 1

AT:
  25-34: Male: 10, Female: 11, Other: 1
  35-44: Male: 29, Female: 22, Other: 1
  45-54: Male: 58, Female: 16, Other: 1
  55-64: Male: 92, Female: 25, Other: 1

Creative Content:
Body Text: [Ad Text Content]

Performance Metrics:
Platforms: FACEBOOK, INSTAGRAM
Total Spend: €1,843

Publisher Information:
Page: Snocks (Textilunternehmen)
About: You focus on your purpose. We focus on your basics.🧦
Verification: NOT_VERIFIED
Facebook Likes: 24,540

Instagram: @snocks
Followers: 191,645
Verified: Yes
```

## Command Line Arguments

- `--mode`: Required. Choose between 'search', 'ads', or 'adsdetail'
- `--query`: Required for search mode. The search term for finding pages
- `--page-id`: Required for ads and adsdetail modes. The Facebook page ID
- `--ad-archive-id`: Required for adsdetail mode. The specific ad's archive ID
- `--data-dir`: Optional. Directory for storing data (default: "data")

## Data Storage

The scraper saves raw API responses in the data directory with timestamps:
- `page_search_{query}_{timestamp}.txt`
- `page_ads_{page_id}_{timestamp}.txt`
- `ad_detail_{ad_archive_id}_{timestamp}.txt`

## Error Handling

- Logs errors to `fb_scraper.log`
- Saves raw API responses for debugging
- Gracefully handles missing or null values
- Provides informative error messages

## Rate Limiting

The scraper respects Facebook's rate limits and includes:
- Session management
- Cookie handling
- Request throttling
- Error recovery

## Notes

- Some fields may not be available for all ads
- Targeting information is only available for EU region ads
- Response format may change based on Facebook's API updates
- Ad spend and reach information might be provided in ranges

## Contributing

Feel free to submit issues and enhancement requests! 