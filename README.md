# Facebook Ad Library Scraper

A Python tool for scraping ad data from the Facebook Ad Library.

## Features

- Search for Facebook pages
- Get all active ads for a specific page
- Get detailed information about specific ads
- Saves raw responses for debugging
- Handles rate limiting and session management

## Installation

1. Clone the repository
2. Install the requirements:
```bash
pip install requests
```

## Usage

### Search for Pages

Search for Facebook pages by name:

```bash
python fb_ad_scraper.py --mode search --query "Snocks"
```

This will return a list of matching pages with their IDs, names, and verification status.

### Get Ads for a Page

Get all active ads for a specific page using the page ID:

```bash
python fb_ad_scraper.py --mode ads --page-id "109806077081081"
```

This will return detailed information about all active ads, including:
- Basic ad information
- Creative content (text, images, videos)
- Distribution and performance metrics
- Targeting information

### Get Detailed Ad Information

Get detailed information about a specific ad using its archive ID:

```bash
python fb_ad_scraper.py --mode detail --ad-archive-id "123456789" --page-id "109806077081081"
```

### Additional Options

- `--data-dir`: Specify custom directory for storing data (default: "data")

## Output Format

The scraper saves raw responses in the data directory with timestamps:
- `page_search_{query}_{timestamp}.txt`
- `page_ads_{page_id}_{timestamp}.txt`
- `ad_detail_{ad_archive_id}_{timestamp}.txt`

## Example Response

When searching for ads, you'll get detailed information like:

```
Detailed Ad Information:
====================================================================================================
Ad 1 (Archive ID: 123456789)
====================================================================================================

Basic Information:
Page Name: Example Page
Page ID: 109806077081081
Status: Active
Ad Creation Time: 2024-01-01
Ad Delivery Start: 2024-01-01
Ad Delivery Stop: 2024-12-31

Creative Content:
Body Text: Example ad text...

Ad Images:
Image 1:
Original URL: https://example.com/image.jpg
Resized URL: https://example.com/image_resized.jpg

Distribution & Performance:
Publisher Platforms: ['FACEBOOK', 'INSTAGRAM']
Currency: EUR
Impressions: {'text': '1K-2K'}
```

## Notes

- The scraper respects Facebook's rate limits
- Some fields may not be available for all ads
- Response format may change based on Facebook's API updates

## Error Handling

The scraper includes robust error handling:
- Logs errors to `fb_scraper.log`
- Saves raw responses for debugging
- Handles missing or null values gracefully

## Contributing

Feel free to submit issues and enhancement requests! 