<map version="0.9.0">
    <node TEXT="AdSpends Analytics Database Schema">
        <node TEXT="users">
            <node TEXT="id VARCHAR(50) PK Example: user_2qP4EhfYFjOzPVvUwvBx6Mj6h2R"/>
            <node TEXT="email VARCHAR(255) UNIQUE Example: onlyvisionsoftware@gmail.com"/>
            <node TEXT="created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"/>
        </node>

        <node TEXT="advertisers">
            <node TEXT="id VARCHAR(50) PK Example: cm2pvh6me002703meuv6uhijb"/>
            <node TEXT="facebook_page_id VARCHAR(50) Example: 20409006880"/>
            <node TEXT="facebook_page_name VARCHAR(255) Example: Shopify"/>
            <node TEXT="facebook_category VARCHAR(100) Example: Software"/>
            <node TEXT="facebook_likes BIGINT Example: 3134916"/>
            <node TEXT="facebook_is_delegate_page BOOLEAN DEFAULT FALSE"/>
            <node TEXT="facebook_page_about TEXT"/>
            <node TEXT="facebook_page_verification BOOLEAN"/>
            <node TEXT="facebook_profile_photo_uri TEXT"/>
            <node TEXT="facebook_cover_photo_uri TEXT"/>
            <node TEXT="facebook_alias VARCHAR(255)"/>
            <node TEXT="instagram_username VARCHAR(255)"/>
            <node TEXT="instagram_followers BIGINT"/>
            <node TEXT="instagram_verification BOOLEAN"/>
            <node TEXT="total_ads INT DEFAULT 0 Example: 173"/>
            <node TEXT="total_active_ads INT DEFAULT 0"/>
            <node TEXT="total_inactive_ads INT DEFAULT 0"/>
            <node TEXT="total_reach BIGINT Example: 226453416"/>
            <node TEXT="total_ad_spend DECIMAL(15,2) Example: 6793602.48"/>
            <node TEXT="total_images INT Example: 163"/>
            <node TEXT="total_videos INT Example: 5"/>
            <node TEXT="total_male_reach BIGINT"/>
            <node TEXT="total_female_reach BIGINT"/>
            <node TEXT="total_unknown_reach BIGINT"/>
            <node TEXT="last_ad_scraping_attempt TIMESTAMP"/>
            <node TEXT="last_ad_scraping_result VARCHAR(50) Example: success"/>
            <node TEXT="last_ad_scraping_job_id VARCHAR(50) Example: 966825"/>
            <node TEXT="last_brand_scraping_attempt TIMESTAMP"/>
            <node TEXT="last_brand_scraping_result VARCHAR(50)"/>
            <node TEXT="last_brand_scraping_job_id VARCHAR(50)"/>
            <node TEXT="advertiser_category_id VARCHAR(50) FK Example: cat_001"/>
            <node TEXT="profile_image_path VARCHAR(255) Example: meta/advertiser-profile-images/cm2pvh6me002703meuv6uhijb.jpg"/>
            <node TEXT="created_at TIMESTAMP"/>
            <node TEXT="updated_at TIMESTAMP"/>
        </node>

        <node TEXT="advertiser_categories">
            <node TEXT="id VARCHAR(50) PK Example: cat_001"/>
            <node TEXT="label VARCHAR(255) Example: Software"/>
            <node TEXT="german_translation VARCHAR(255) Example: Software"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="ads">
            <node TEXT="id VARCHAR(50) PK Example: cm2qhch1c08f603l3opij9fn6"/>
            <node TEXT="advertiser_id VARCHAR(50) FK Example: cm2pvh6me002703meuv6uhijb"/>
            <node TEXT="facebook_ad_id VARCHAR(50) Example: 1185520302553326"/>
            <node TEXT="total_reach BIGINT Example: 16403589"/>
            <node TEXT="eu_total_reach BIGINT Example: 19335867"/>
            <node TEXT="total_ad_spend DECIMAL(15,2) Example: 580076.01"/>
            <node TEXT="total_images INT DEFAULT 0"/>
            <node TEXT="total_videos INT DEFAULT 0"/>
            <node TEXT="ad_text TEXT Example: Rejoignez les millions d entrepreneurs qui vendent en ligne sur Shopify"/>
            <node TEXT="ad_visible_url VARCHAR(255) Example: SHOPIFY.COM"/>
            <node TEXT="ad_cta_text VARCHAR(255) Example: Demarrez votre essai gratuit des aujourd hui"/>
            <node TEXT="ad_cta_sub_text TEXT"/>
            <node TEXT="ad_href TEXT Example: https://www.shopify.com/fr/demarrer"/>
            <node TEXT="ad_downloaded_image VARCHAR(255) Example: meta/ad-images/cm4s2htgs013u01nvxg3hntkx-preview.jpg"/>
            <node TEXT="ad_downloaded_video VARCHAR(255)"/>
            <node TEXT="is_active BOOLEAN DEFAULT TRUE"/>
            <node TEXT="last_delivered_date TIMESTAMP Example: 2024-09-22"/>
            <node TEXT="last_data_point_id VARCHAR(50)"/>
            <node TEXT="created_at TIMESTAMP"/>
            <node TEXT="updated_at TIMESTAMP"/>
        </node>

        <node TEXT="ad_data_points">
            <node TEXT="id VARCHAR(50) PK Example: cm4s2htgs013t01nv2a6chafd"/>
            <node TEXT="ad_id VARCHAR(50) FK Example: cm2qhch1c08f603l3opij9fn6"/>
            <node TEXT="is_active BOOLEAN Example: true"/>
            <node TEXT="is_latest BOOLEAN DEFAULT FALSE Example: true"/>
            <node TEXT="eu_total_reach BIGINT Example: 19335867"/>
            <node TEXT="total_ad_spend DECIMAL(15,2) Example: 580076.01"/>
            <node TEXT="delivered_date DATE Example: 2024-09-22"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="geographic_stats">
            <node TEXT="id VARCHAR(50) PK Example: geo_001"/>
            <node TEXT="country_code CHAR(2) Example: FR"/>
            <node TEXT="total_reach BIGINT Example: 4900075"/>
            <node TEXT="total_ad_spend DECIMAL(15,2)"/>
            <node TEXT="percentage_distribution DECIMAL(5,2) Example: 33.57"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="age_demographics">
            <node TEXT="id VARCHAR(50) PK Example: age_001"/>
            <node TEXT="age_range VARCHAR(20) Example: 18-24"/>
            <node TEXT="total_reach BIGINT Example: 4541771"/>
            <node TEXT="total_ad_spend DECIMAL(15,2)"/>
            <node TEXT="percentage_distribution DECIMAL(5,2) Example: 30.75"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="gender_demographics">
            <node TEXT="id VARCHAR(50) PK Example: gender_001"/>
            <node TEXT="total_male_reach BIGINT Example: 10110101"/>
            <node TEXT="total_female_reach BIGINT Example: 4487170"/>
            <node TEXT="total_reach BIGINT Example: 14597271"/>
            <node TEXT="male_percentage DECIMAL(5,2) Example: 69.26"/>
            <node TEXT="female_percentage DECIMAL(5,2) Example: 30.74"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="landing_page_stats">
            <node TEXT="id VARCHAR(50) PK Example: lp_001"/>
            <node TEXT="landing_page VARCHAR(255) Example: shopify.com"/>
            <node TEXT="total_reach BIGINT Example: 3567890"/>
            <node TEXT="total_ad_spend DECIMAL(15,2) Example: 125678.45"/>
            <node TEXT="percentage_distribution DECIMAL(5,2) Example: 25.45"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="keyword_stats">
            <node TEXT="id VARCHAR(50) PK Example: kw_001"/>
            <node TEXT="keyword VARCHAR(255) Example: ecommerce"/>
            <node TEXT="total_reach BIGINT Example: 2345678"/>
            <node TEXT="total_ad_spend DECIMAL(15,2) Example: 98765.43"/>
            <node TEXT="percentage_distribution DECIMAL(5,2) Example: 18.75"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="creative_type_stats">
            <node TEXT="id VARCHAR(50) PK Example: ct_001"/>
            <node TEXT="creative_type VARCHAR(50) Example: image"/>
            <node TEXT="total_reach BIGINT Example: 4567890"/>
            <node TEXT="total_ad_spend DECIMAL(15,2) Example: 234567.89"/>
            <node TEXT="percentage_distribution DECIMAL(5,2) Example: 35.67"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>

        <node TEXT="platform_stats">
            <node TEXT="id VARCHAR(50) PK Example: ps_001"/>
            <node TEXT="platform_name VARCHAR(50) Example: facebook"/>
            <node TEXT="total_reach BIGINT Example: 5678901"/>
            <node TEXT="total_ad_spend DECIMAL(15,2) Example: 345678.90"/>
            <node TEXT="percentage_distribution DECIMAL(5,2) Example: 45.89"/>
            <node TEXT="created_at TIMESTAMP"/>
        </node>
    </node>
</map> 