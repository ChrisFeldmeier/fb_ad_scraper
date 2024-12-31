-- Create Database
CREATE DATABASE adspends_analytics;
USE adspends_analytics;

-- Users Table
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Advertiser Categories Table (moved before advertisers)
CREATE TABLE advertiser_categories (
    id VARCHAR(50) PRIMARY KEY,
    label VARCHAR(255) NOT NULL,
    german_translation VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Advertisers Table
CREATE TABLE advertisers (
    id VARCHAR(50) PRIMARY KEY,
    facebook_page_id VARCHAR(50),
    facebook_page_name VARCHAR(255),
    facebook_category VARCHAR(100),
    facebook_likes BIGINT,
    facebook_is_delegate_page BOOLEAN DEFAULT FALSE,
    facebook_page_about TEXT,
    facebook_page_verification BOOLEAN DEFAULT FALSE,
    facebook_profile_photo_uri TEXT,
    facebook_cover_photo_uri TEXT,
    facebook_alias VARCHAR(255),
    instagram_username VARCHAR(255),
    instagram_followers BIGINT,
    instagram_verification BOOLEAN,
    profile_image_path VARCHAR(255),
    total_ads INT DEFAULT 0,
    total_active_ads INT DEFAULT 0,
    total_inactive_ads INT DEFAULT 0,
    total_reach BIGINT DEFAULT 0,
    total_ad_spend DECIMAL(15,2) DEFAULT 0,
    total_images INT DEFAULT 0,
    total_videos INT DEFAULT 0,
    total_male_reach BIGINT DEFAULT 0,
    total_female_reach BIGINT DEFAULT 0,
    total_unknown_reach BIGINT DEFAULT 0,
    last_ad_scraping_attempt TIMESTAMP,
    last_ad_scraping_result VARCHAR(50),
    last_ad_scraping_job_id VARCHAR(50),
    last_brand_scraping_attempt TIMESTAMP,
    last_brand_scraping_result VARCHAR(50),
    last_brand_scraping_job_id VARCHAR(50),
    advertiser_category_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (advertiser_category_id) REFERENCES advertiser_categories(id)
);

-- Ads Table
CREATE TABLE ads (
    id VARCHAR(50) PRIMARY KEY,
    advertiser_id VARCHAR(50),
    facebook_ad_id VARCHAR(50) NOT NULL,
    total_reach BIGINT DEFAULT 0,
    total_images INT DEFAULT 0,
    total_videos INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    eu_total_reach BIGINT DEFAULT 0,
    total_ad_spend DECIMAL(15,2) DEFAULT 0,
    last_delivered_date TIMESTAMP,
    last_data_point_id VARCHAR(50),
    ad_text TEXT,
    ad_visible_url VARCHAR(255),
    ad_cta_text VARCHAR(255),
    ad_cta_sub_text TEXT,
    ad_href TEXT,
    ad_downloaded_image VARCHAR(255),
    ad_downloaded_video VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (advertiser_id) REFERENCES advertisers(id)
);

-- Ad Data Points Table
CREATE TABLE ad_data_points (
    id VARCHAR(50) PRIMARY KEY,
    ad_id VARCHAR(50),
    is_active BOOLEAN,
    is_latest BOOLEAN DEFAULT FALSE,
    eu_total_reach BIGINT,
    total_ad_spend DECIMAL(15,2),
    delivered_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ad_id) REFERENCES ads(id)
);

-- Ad Previews Table
CREATE TABLE ad_previews (
    id VARCHAR(50) PRIMARY KEY,
    data_point_id VARCHAR(50),
    ad_text TEXT,
    visible_url VARCHAR(255),
    cta_text VARCHAR(255),
    cta_sub_text TEXT,
    ad_href TEXT,
    downloaded_image_path VARCHAR(255),
    downloaded_video_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_point_id) REFERENCES ad_data_points(id)
);

-- Geographic Stats Table
CREATE TABLE geographic_stats (
    id VARCHAR(50) PRIMARY KEY,
    country_code CHAR(2),
    total_reach BIGINT,
    total_ad_spend DECIMAL(15,2),
    percentage_distribution DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Age Demographics Table
CREATE TABLE age_demographics (
    id VARCHAR(50) PRIMARY KEY,
    age_range VARCHAR(20),
    total_reach BIGINT,
    total_ad_spend DECIMAL(15,2),
    percentage_distribution DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gender Demographics Table
CREATE TABLE gender_demographics (
    id VARCHAR(50) PRIMARY KEY,
    total_male_reach BIGINT,
    total_female_reach BIGINT,
    total_reach BIGINT,
    male_percentage DECIMAL(5,2),
    female_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Landing Pages Stats Table
CREATE TABLE landing_page_stats (
    id VARCHAR(50) PRIMARY KEY,
    advertiser_id VARCHAR(50),
    landing_page_url TEXT,
    total_reach BIGINT,
    total_ad_spend DECIMAL(15,2),
    ad_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (advertiser_id) REFERENCES advertisers(id)
);

-- Keywords Stats Table
CREATE TABLE keyword_stats (
    id VARCHAR(50) PRIMARY KEY,
    keyword VARCHAR(255),
    ad_count INT,
    total_reach BIGINT,
    total_ad_spend DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creative Type Stats Table
CREATE TABLE creative_type_stats (
    id VARCHAR(50) PRIMARY KEY,
    creative_type VARCHAR(50),
    total_reach BIGINT,
    percentage_distribution DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Category Stats Table
CREATE TABLE category_stats (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(255),
    ad_count INT,
    total_sum DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Statistics Summary Table
CREATE TABLE statistics_summary (
    id VARCHAR(50) PRIMARY KEY,
    advertiser_count BIGINT,
    ad_count BIGINT,
    total_ad_spend DECIMAL(15,2),
    total_reach BIGINT,
    snapshot_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Auth Config Table
CREATE TABLE auth_config (
    id VARCHAR(50) PRIMARY KEY,
    object VARCHAR(50),
    first_name ENUM('on', 'off'),
    last_name ENUM('on', 'off'),
    email_address ENUM('on', 'off'),
    phone_number ENUM('on', 'off'),
    username ENUM('on', 'off'),
    password VARCHAR(50),
    single_session_mode BOOLEAN,
    enhanced_email_deliverability BOOLEAN,
    test_mode BOOLEAN,
    cookieless_dev BOOLEAN,
    url_based_session_syncing BOOLEAN,
    claimed_at TIMESTAMP,
    identification_requirements JSON,
    identification_strategies JSON,
    first_factors JSON,
    second_factors JSON,
    email_verification_strategies JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Display Config Table
CREATE TABLE display_config (
    id VARCHAR(50) PRIMARY KEY,
    instance_environment_type VARCHAR(50),
    application_name VARCHAR(255),
    logo_image_url TEXT,
    favicon_image_url TEXT,
    logo_link_url TEXT,
    home_url TEXT,
    sign_in_url TEXT,
    sign_up_url TEXT,
    user_profile_url TEXT,
    waitlist_url TEXT,
    organization_profile_url TEXT,
    create_organization_url TEXT,
    after_sign_in_url TEXT,
    after_sign_up_url TEXT,
    after_sign_out_one_url TEXT,
    after_sign_out_all_url TEXT,
    after_leave_organization_url TEXT,
    after_create_organization_url TEXT,
    after_switch_session_url TEXT,
    support_email VARCHAR(255),
    branded BOOLEAN,
    clerk_js_version VARCHAR(10),
    show_devmode_warning BOOLEAN,
    google_one_tap_client_id VARCHAR(255),
    help_url TEXT,
    privacy_policy_url TEXT,
    terms_url TEXT,
    captcha_public_key VARCHAR(255),
    captcha_public_key_invisible VARCHAR(255),
    captcha_widget_type VARCHAR(50),
    captcha_provider VARCHAR(50),
    captcha_oauth_bypass JSON,
    preferred_sign_in_strategy VARCHAR(50),
    experimental_force_oauth_first BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Theme Config Table
CREATE TABLE theme_config (
    id VARCHAR(50) PRIMARY KEY,
    display_config_id VARCHAR(50),
    buttons_font_color VARCHAR(50),
    buttons_font_family VARCHAR(255),
    buttons_font_weight VARCHAR(50),
    general_color VARCHAR(50),
    general_padding VARCHAR(50),
    general_box_shadow VARCHAR(255),
    general_font_color VARCHAR(50),
    general_font_family VARCHAR(255),
    general_border_radius VARCHAR(50),
    general_background_color VARCHAR(50),
    general_label_font_weight VARCHAR(50),
    accounts_background_color VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (display_config_id) REFERENCES display_config(id)
);

-- User Settings Table
CREATE TABLE user_settings (
    id VARCHAR(50) PRIMARY KEY,
    attributes JSON,
    sign_in_second_factor_required BOOLEAN,
    sign_up_captcha_enabled BOOLEAN,
    sign_up_progressive BOOLEAN,
    sign_up_mode VARCHAR(50),
    password_min_length INT,
    password_max_length INT,
    password_require_special_char BOOLEAN,
    password_require_numbers BOOLEAN,
    password_require_uppercase BOOLEAN,
    password_require_lowercase BOOLEAN,
    password_show_zxcvbn BOOLEAN,
    password_min_zxcvbn_strength INT,
    password_enforce_hibp BOOLEAN,
    password_allowed_special_characters VARCHAR(255),
    username_min_length INT,
    username_max_length INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organization Settings Table
CREATE TABLE organization_settings (
    id VARCHAR(50) PRIMARY KEY,
    enabled BOOLEAN,
    max_allowed_memberships INT,
    creator_role VARCHAR(50),
    domains_enabled BOOLEAN,
    domains_enrollment_modes JSON,
    domains_default_role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attack Protection Settings Table
CREATE TABLE attack_protection_settings (
    id VARCHAR(50) PRIMARY KEY,
    user_lockout_enabled BOOLEAN,
    user_lockout_max_attempts INT,
    user_lockout_duration_minutes INT,
    pii_enabled BOOLEAN,
    email_link_require_same_client BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social Auth Settings Table
CREATE TABLE social_auth_settings (
    id VARCHAR(50) PRIMARY KEY,
    provider VARCHAR(50),
    enabled BOOLEAN,
    required BOOLEAN,
    authenticatable BOOLEAN,
    block_email_subaddresses BOOLEAN,
    strategy VARCHAR(50),
    not_selectable BOOLEAN,
    deprecated BOOLEAN,
    name VARCHAR(255),
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes (removed duplicates)
CREATE INDEX idx_advertiser_fb_page_id ON advertisers(facebook_page_id);
CREATE INDEX idx_ads_advertiser_id ON ads(advertiser_id);
CREATE INDEX idx_ad_data_points_ad_id ON ad_data_points(ad_id);
CREATE INDEX idx_ad_data_points_delivered ON ad_data_points(delivered_date);
CREATE INDEX idx_geographic_stats_country ON geographic_stats(country_code);
CREATE INDEX idx_keyword_stats_keyword ON keyword_stats(keyword);
CREATE INDEX idx_landing_page_stats_advertiser ON landing_page_stats(advertiser_id);
CREATE INDEX idx_statistics_summary_date ON statistics_summary(snapshot_date);
CREATE INDEX idx_advertiser_category ON advertisers(advertiser_category_id);

-- Users Table
INSERT INTO users (id, email) VALUES 
('user_2qP4EhfYFjOzPVvUwvBx6Mj6h2R', 'onlyvisionsoftware@gmail.com');

-- Advertiser Categories Table
INSERT INTO advertiser_categories (id, label, german_translation) VALUES
('cat_001', 'Software', 'Software'),
('cat_002', 'Health/beauty', 'Gesundheit/Schönheit'),
('cat_003', 'Fashion Accessories', 'Mode-Accessoires'),
('cat_004', 'Interest', 'Interesse'),
('cat_005', 'Product/Service', 'Produkt/Dienstleistung'),
('cat_006', 'Retail Company', 'Einzelhandelsunternehmen'),
('cat_007', 'Automotive', 'Autos'),
('cat_008', 'Clothing', 'Bekleidung');

-- Advertisers Table
INSERT INTO advertisers (
    id, facebook_page_id, facebook_page_name, facebook_category, facebook_likes, 
    profile_image_path, total_ads, total_ad_spend, total_reach, total_images, 
    total_videos, last_ad_scraping_result, last_ad_scraping_job_id, advertiser_category_id
) VALUES 
('cm2pvh6me002703meuv6uhijb', '20409006880', 'Shopify', 'Software', 3134916, 'meta/advertiser-profile-images/cm2pvh6me002703meuv6uhijb.jpg', 173, 6793602.48, 226453416, 163, 5, 'success', '966825', 'cat_001'),
('cm2n4j86n001103l0kv3dcs7k', '165991287137890', 'Andreas Baulig', 'Interest', 14703, 'meta/advertiser-profile-images/cm2n4j86n001103l0kv3dcs7k.jpg', 44, 18951.24, 631708, 28, 16, 'success-no-ads', '966857', 'cat_004'),
('cm2pukafc00ll03mlj2qpusja', '1844332612465362', 'Polène', 'Fashion Accessories', NULL, 'meta/advertiser-profile-images/cm2pukafc00ll03mlj2qpusja.jpg', 110, 431913.75, 14397125, 107, 3, 'success', NULL, 'cat_003'),
('cm2puf10m00f103ldkxy2iig5', '116461257721234', 'Belle Body', 'Health/beauty', NULL, 'meta/advertiser-profile-images/cm2puf10m00f103ldkxy2iig5.jpg', 204, 431771.13, 14392371, 174, 30, 'success', NULL, 'cat_002'),
('cm2xs0kq003v903jy10aqj3nv', '1270817949729510', 'IL MAKIAGE', 'Health/beauty', NULL, 'meta/advertiser-profile-images/cm2xs0kq003v903jy10aqj3nv.jpg', 50, 431720.61, 14390687, 50, 0, 'success-no-ads', NULL, 'cat_002');

-- Ads Table
INSERT INTO ads (
    id, advertiser_id, facebook_ad_id, total_reach, eu_total_reach,
    total_ad_spend, last_delivered_date, ad_text, ad_visible_url,
    ad_cta_text, ad_href, ad_downloaded_image
) VALUES 
('cm2qhch1c08f603l3opij9fn6', 'cm2pvh6me002703meuv6uhijb', '1185520302553326', 16403589, 19335867, 580076.01, '2024-09-22', 'Rejoignez les millions d''entrepreneurs qui vendent en ligne sur Shopify.', 'SHOPIFY.COM', 'Démarrez votre essai gratuit dès aujourd''hui', 'https://www.shopify.com/fr/demarrer', 'meta/ad-images/cm4s2htgs013u01nvxg3hntkx-preview.jpg'),
('cm2qhb2gy06vu03l065ayhjp7', 'cm2pvh6me002703meuv6uhijb', '857362233091354', 10835510, 13888643, 416659.29, '2024-10-23', 'Sell more, build more, get more done. All in one place.', '', 'Try out Shopify for free.', 'https://www.shopify.com/free-trial/editions/summer2024', 'meta/ad-images/cm4lboyrq31xw01nv7h5t81ps-preview.jpg'),
('cm2qhc94o050o03kyzwmegsne', 'cm2pvh6me002703meuv6uhijb', '1952240558594607', 8792746, 11471029, 344130.87, '2024-09-22', 'Rejoignez les millions d''entrepreneurs qui vendent en ligne sur Shopify.', 'SHOPIFY.COM', 'Démarrez votre essai gratuit dès aujourd''hui', 'https://www.shopify.com/fr/demarrer', 'meta/ad-images/cm4s2htax011301nvt51k3fcv-preview.jpg'),
('cm3t6ku81045703jmf3x160ob', 'cm2pvh6me002703meuv6uhijb', '1279925443454753', 8107504, 9965764, 298972.92, '2024-11-08', 'There''s nothing like that first sale feeling. Launch your store and start selling today.', 'SHOPIFY.COM', 'Millions of first sales made here', 'https://www.shopify.com/de', 'meta/ad-images/cm4s2hsug00uj01nvf2pg6xiq-preview.jpg'),
('cm2ncmpet000p03jt0a7r22mc', 'cm2n4j86n001103l0kv3dcs7k', '382611271561287', 124845, 124845, 3745.35, '2024-09-17', NULL, NULL, NULL, 'https://www.business.de/wbt-training', 'meta/ad-images/cm2ncmpet000q03jt9ixjxkv8-preview.jpg');

-- Ad Data Points Table
INSERT INTO ad_data_points (id, ad_id, is_active, is_latest, eu_total_reach, total_ad_spend, delivered_date) VALUES
('cm4s2htgs013t01nv2a6chafd', 'cm2qhch1c08f603l3opij9fn6', true, true, 19335867, 580076.01, '2024-09-22'),
('cm4lboyrq31xv01nv4sauv1ev', 'cm2qhb2gy06vu03l065ayhjp7', true, true, 13888643, 416659.29, '2024-10-23'),
('cm4s2htax011201nvtty32819', 'cm2qhc94o050o03kyzwmegsne', true, true, 11471029, 344130.87, '2024-09-22'),
('dp_004', 'cm3t6ku81045703jmf3x160ob', true, true, 9965764, 298972.92, '2024-11-08'),
('dp_005', 'cm2ncmpet000p03jt0a7r22mc', false, true, 124845, 3745.35, '2024-09-17');

-- Geographic Stats Table
INSERT INTO geographic_stats (id, country_code, total_reach, percentage_distribution) VALUES 
('geo_001', 'FR', 4900075, 33.57),
('geo_002', 'IT', 4765194, 32.64),
('geo_003', 'DE', 2674172, 18.32),
('geo_004', 'ES', 2257829, 15.47),
('geo_005', 'AT', 388915096, 3.59),
('geo_006', 'PL', 365990601, 3.38);

-- Age Demographics Table
INSERT INTO age_demographics (id, age_range, total_reach, percentage_distribution) VALUES 
('age_001', '18-24', 4541771, 30.75),
('age_002', '25-34', 5654396, 38.28),
('age_003', '35-44', 2513230, 17.02),
('age_004', '45-54', 1246929, 8.44),
('age_005', '55-65+', 813124, 5.51);

-- Gender Demographics Table
INSERT INTO gender_demographics (id, total_male_reach, total_female_reach, total_reach, male_percentage, female_percentage) VALUES 
('gender_001', 10110101, 4487170, 14597271, 69.26, 30.74),
('gender_002', 144986495, 82776438, 227762933, 63.66, 36.34);

-- Landing Pages Stats Table
INSERT INTO landing_page_stats (id, advertiser_id, landing_page_url, total_reach, total_ad_spend, ad_count) VALUES 
('lp_001', 'cm2pvh6me002703meuv6uhijb', 'https://www.shopify.com/free-trial', 1594043.49, 47821.30, 9),
('lp_002', 'cm2pvh6me002703meuv6uhijb', 'https://www.shopify.com/fr/demarrer', 1183737.48, 35512.12, 3),
('lp_003', 'cm2pvh6me002703meuv6uhijb', 'https://www.shopify.com/de', 783495.33, 23504.86, 17),
('lp_004', 'cm2pvh6me002703meuv6uhijb', 'https://www.shopify.com/start', 552974.64, 16589.24, 5),
('lp_005', 'cm2pvh6me002703meuv6uhijb', 'https://www.shopify.com/free-trial/editions/summer2024', 505639.86, 15169.20, 2),
('lp_006', 'cm2pvh6me002703meuv6uhijb', 'https://www.shopify.com/de/free-trial', 465107.67, 13953.23, 3);

-- Keywords Stats Table
INSERT INTO keyword_stats (id, keyword, ad_count, total_reach, total_ad_spend) VALUES 
('kw_001', 'Shopify', 11, 241881.75, 7256.45),
('kw_002', 'tua', 3, 111805.68, 3354.17),
('kw_003', 'brand', 2, 97189.08, 2915.67),
('kw_004', 'Behalte', 1, 71067.57, 2132.03),
('kw_005', 'Image', 1, 71067.57, 2132.03),
('kw_006', 'Kontrolle', 1, 71067.57, 2132.03),
('kw_007', 'Marke', 1, 71067.57, 2132.03),
('kw_008', 'Minuten', 1, 71067.57, 2132.03),
('kw_009', 'Onlineshop', 1, 71067.57, 2132.03),
('kw_010', 'Startklar', 1, 71067.57, 2132.03);

-- Creative Type Stats Table
INSERT INTO creative_type_stats (id, creative_type, total_reach, percentage_distribution) VALUES 
('ct_001', 'Image', 10100905548, 86.38),
('ct_002', 'Video', 1593174146, 13.62),
('ct_003', 'Image', 223668891, 98.20),
('ct_004', 'Video', 4094042, 1.80);

-- Category Stats Table
INSERT INTO category_stats (id, category, ad_count, total_sum) VALUES 
('cat_stat_001', 'Bekleidung', 28284, 35901225.93),
('cat_stat_002', 'Produkt/Dienstleistung', 23155, 23202925.49),
('cat_stat_003', 'Autos', 1858, 11906094.69),
('cat_stat_004', 'Gesundheit/Schönheit', 7827, 11571111.12),
('cat_stat_005', 'Einzelhandelsunternehmen', 5352, 10510876.77);

-- Statistics Summary Table
INSERT INTO statistics_summary (id, advertiser_count, ad_count, total_ad_spend, total_reach, snapshot_date) VALUES 
('stats_001', 842496, 331069, 352845938.55, 11761531285, '2024-01-01'),
('stats_002', 842496, 331069, 352845938.55, 11761531285, '2024-01-02');

-- Auth Config Table (from environment.json)
INSERT INTO auth_config (
    id, object, first_name, last_name, email_address, phone_number, 
    username, password, single_session_mode, enhanced_email_deliverability,
    test_mode, cookieless_dev, url_based_session_syncing
) VALUES (
    'aac_2o15wqtcfHcbXCND8zz9tI6IMa8',
    'auth_config',
    'on', 'on', 'on', 'off',
    'off', 'required', true, false,
    false, false, false
);

-- Display Config Table (from environment.json)
INSERT INTO display_config (
    id, instance_environment_type, application_name, 
    logo_image_url, favicon_image_url, home_url, sign_in_url, sign_up_url,
    support_email, branded, clerk_js_version, show_devmode_warning
) VALUES (
    'display_config_2o15wtQ5K1Wd6U5BHscQixXNr2V',
    'production',
    'AdSpends.com',
    'https://img.clerk.com/eyJ0eXBlIjoicHJveHkiLCJzcmMiOiJodHRwczovL2ltYWdlcy5jbGVyay5kZXYvdXBsb2FkZWQvaW1nXzJwNmlJV0l2ME9JWHpiN1RMSXd1bXZCVUc2RyJ9',
    'https://img.clerk.com/eyJ0eXBlIjoicHJveHkiLCJzcmMiOiJodHRwczovL2ltYWdlcy5jbGVyay5kZXYvdXBsb2FkZWQvaW1nXzJwNmlKbnZJaVRIMHZZMUhBd3g3d2FqWGdjbiJ9',
    'https://adspends.com',
    'https://accounts.adspends.com/sign-in',
    'https://accounts.adspends.com/sign-up',
    'info@adspends.com',
    true,
    '5',
    false
);

-- Theme Config Table
INSERT INTO theme_config (
    id, display_config_id, buttons_font_color, buttons_font_family,
    buttons_font_weight, general_color, general_padding, general_box_shadow,
    general_font_color, general_font_family, general_border_radius,
    general_background_color, general_label_font_weight, accounts_background_color
) VALUES (
    'theme_001',
    'display_config_2o15wtQ5K1Wd6U5BHscQixXNr2V',
    '#ffffff',
    '"Source Sans Pro", sans-serif',
    '600',
    '#6c47ff',
    '1em',
    '0 2px 8px rgba(0, 0, 0, 0.2)',
    '#151515',
    '"Source Sans Pro", sans-serif',
    '0.5em',
    '#ffffff',
    '600',
    '#ffffff'
);

-- Organization Settings Table
INSERT INTO organization_settings (
    id, enabled, max_allowed_memberships, creator_role, 
    domains_enabled
) VALUES (
    'org_settings_001',
    true,
    5,
    'org:admin',
    false
);

-- Attack Protection Settings Table
INSERT INTO attack_protection_settings (
    id, user_lockout_enabled, user_lockout_max_attempts,
    user_lockout_duration_minutes, pii_enabled, email_link_require_same_client
) VALUES (
    'attack_protection_001',
    true,
    100,
    60,
    true,
    true
);

-- Social Auth Settings Table
INSERT INTO social_auth_settings (
    id, provider, enabled, required, authenticatable,
    block_email_subaddresses, strategy, not_selectable,
    deprecated, name, logo_url
) VALUES (
    'social_auth_001',
    'oauth_google',
    true,
    false,
    true,
    true,
    'oauth_google',
    false,
    false,
    'Google',
    'https://img.clerk.com/static/google.png'
);