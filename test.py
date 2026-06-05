import os, jmespath
import gzip
import json
from lxml import html
from parsel import Selector
from curl_cffi import requests
from db import *
import hashlib
from concurrent.futures import ThreadPoolExecutor
import re
create_state_table()

def write_html_direct_gzip(html_data, page_save_path, gz_file="output.html.gz"):
    os.makedirs(page_save_path, exist_ok=True)
    original_dir = os.getcwd()
    try:
        os.chdir(page_save_path)
        with gzip.open(gz_file, "wt", encoding="utf-8") as f:
            f.write(html_data)
        return os.path.abspath(gz_file)
    finally:
        os.chdir(original_dir)

def scrape_page(url, page_save_path="./saved_pages"):
    payload = {}
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"148.0.7778.217"',
    'sec-ch-ua-full-version-list': '"Chromium";v="148.0.7778.217", "Google Chrome";v="148.0.7778.217", "Not/A)Brand";v="99.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'cookie': 'launch=prod-mac; BIGipServerlgl-martindale-k8sw_24080_POOL=3515879434.4190.0000; laravel_session=eyJpdiI6IjVKRXMrM3FoQ3dHaE9EaFBjZEoyanc9PSIsInZhbHVlIjoiNm5meGtXTnp4djVjMTA4cWVxdzUxN3FjWjJGejJJSkMxVTl5aGFtWTgzZ2xDemUwQzZ5ckFkOTFKaFByZXJFY0VhVy9wbGVXeExkZTBma1BuenpYNHI4SGVwOUhsVkZ6cHZrVWthS09OcWY0UEVTZzNzNWZ3YkpEZ3FDVHcreFciLCJtYWMiOiI4OTAxN2IzMWIxOGMzMzc2MmNmOTRlYjFkY2Y3NjVkOGIwMjk5MGM1YTM1OGE0YjJiZjA3ZTUyOTkxMzBlZWFiIiwidGFnIjoiIn0%3D; mdcgeo={%22country%22:%22AE%22%2C%22state%22:%22DU%22}; cf_clearance=de4P_arQK0nKOdvdZy7mZv7DfEbp9KEVLTQfpnus_SQ-1780559267-1.2.1.1-Cwpqyr54WQl.EPEYdB5upYco2SsxHS4dWn3UCWFLy8zgA1FRJrpRNgQCVthQtYbAf8Fv5q1hGW_QrHhLJsflm.puzAbVZ7NCiHuq9ItjGgZHxv_Lw0nY0r_Y12Ql.UpR_T.jlfwM2uRYxf5NUNes_yaHpWUlKbvAmU2gs8SVSpu2eGlCz7HMaNiz_7dq0cjKz.6HVuRIKx8711RaOO566I64yIuuKqTTf1jWveWrzTQKTeudZ4VqlpRHwFGJbaShAcIuuEpMX2PRIZ_mCLs0E2e0Fx3gEbmscHEg5nspV8gb0SYrJj9UIfRsY21ZT9XzhUwx0PhJJLMAYWTX2PCdOg6EXadM9k7nHgEUlOxg8mog6G6j2wFjfOauGUZpr8OljLyljzNDnQvL5M1qMucRLDZZH7P0q49g7kdFfj2Bc1A; __cf_bm=FRqHWg4qOIRT2XCOvGgB6WaqzgSeuza_ch1p1H5zFEw-1780559267.1192873-1.0.1.1-uhLHFmfOdXTXFe6V1NOMIp12YqTs25HMyW9DK8iQihnkMG922xeFjsNLLFPSFxBiIQuGPqUE9AOqLwtrPQJCSs3JcloDBbXiAyP7qtig.MKNPIRqZQIxTmA44kv18KUc; AMCVS_5C64123F5245AF950A490D45%40AdobeOrg=1; AMCV_5C64123F5245AF950A490D45%40AdobeOrg=179643557%7CMCIDTS%7C20609%7CMCMID%7C43283088533697672644526034098362530356%7CMCAAMLH-1781164070%7C6%7CMCAAMB-1781164070%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1780566470s%7CNONE%7CvVersion%7C5.5.0; s_nr30=1780559270720-New; s_vnc365=1812095270721%26vn%3D1; s_ivc=true; s_tslv=1780559270723; s_inv=0; gpv_v12=Martindale.com%3ADirectory%3AProfileView%3AFirmProfile%3Alaw%20offices%20of%20marc%20friedman; s_sess=%20s_cc%3Dtrue%3B; stats=20260603234751524992C,,FIRM_PROFILE,,,; year=YnJvd3NlcklkPTIxMzY3MDk4MDk=; hour=c2Vzc2lvbklkPTIzMjc1MDE1NiZyZWZlckRvbWFpblNlbzRCPQ==; _ga_19ND86TN6P=GS2.1.s1780559275$o1$g0$t1780559275$j60$l0$h0; _ga=GA1.1.1809288235.1780559276; _ga_ZVZW1DXN1H=GS2.1.s1780559275$o1$g0$t1780559275$j60$l0$h439882263; invoca_session=%7B%22ttl%22%3A%222026-07-04T07%3A48%3A00.136Z%22%2C%22session%22%3A%7B%22invoca_id%22%3A%22i-011fe35e-eb26-47c2-c834-69d0f090d7fd%22%7D%2C%22config%22%3A%7B%22ce%22%3Atrue%2C%22fv%22%3Afalse%2C%22rn%22%3Afalse%7D%7D',
}
    
    gzip_filename = f"{hashlib.sha256(url.encode()).hexdigest()}.html.gz"
    
    if os.path.exists(os.path.join(page_save_path, gzip_filename)):
        print(f"Found existing gzip file for URL: {url} — loading from gzip.")
        with gzip.open(os.path.join(page_save_path, gzip_filename), 'rb') as f:
            html_text = f.read().decode('utf-8')
    else:
        response = requests.request("GET", url, headers=headers, data=payload, impersonate='chrome124')

        if response.status_code == 403:
            raise Exception(f"403 Forbidden: {url}")

        html_text = response.text
    
    write_html_direct_gzip(html_text, page_save_path, gz_file=gzip_filename)

    
    selector = Selector(html_text)


    tree = html.fromstring(html_text)
    
    script_nodes = tree.xpath("//script[@type='application/ld+json']/text()") 
    script_content = next(iter(script_nodes), "[]")
    json_data = json.loads(script_content)
    legal_service = next(iter(json_data), {}) if isinstance(json_data, list) else json_data
    title = legal_service.get('name','N/A')
    title = re.sub(r'\s+', ' ',  title)

    if url.endswith('/'):
            parts = url.strip('/').split('/')
            if parts[-1].endswith('-f'):
                firm_id = parts[-2].split('-')[-1]
            else:
                firm_id = parts[-1].split('-')[-1]
    else:
        parts = url.split('/')
        if parts[-1].endswith('-f'):
            firm_id = parts[-2].split('-')[-1]
        else:
            firm_id = parts[-1].split('-')[-1]

    address_url = f'https://www.martindale.com/organizations/{firm_id}/other-offices'
    address = fetch_address(address_url, html_text)

    aggregate_rating = legal_service.get('aggregateRating', {})
    if not aggregate_rating:
        aggregate_rating = {}
    details_node = tree.xpath("//div[contains(@class, 'truncate-text') and contains(@style, 'height:110px') or @data-prevheight='110']//text()")
    details_text = " ".join(details_node).strip() if details_node else "N/A"
    
    total_people_text = tree.xpath("//h2[contains(@id, 'people-h2')]/span[contains(@class, 'toggle-area__header-count')]/text()")
    total_people_count = int(next(iter(total_people_text), "(0)").strip("()"))

    office_contact = selector.xpath('(//a[contains(@href, "tel")]/span)[1]/text()').get()
    if not office_contact:
        office_contact = selector.xpath('(//a/@data-phone)[1]').get()
    website_url = selector.xpath('//a[contains(text(), "View Website")]/@href').get()

    people_list = []
    cards = tree.xpath("//div[contains(@class, 'people-widget-container')]//div[contains(@class, 'attorney-card')]")

    for card in cards:
        name_node = card.xpath(".//div[contains(@class, 'atty-name')]/a/text()")
        designation = card.xpath(".//span[contains(@class, 'atty-title')]//text()")
        rating_node = card.xpath(".//div[contains(@class, 'points')]/span/text()")
        review_count_node = card.xpath(".//div[contains(@class, 'number-reviews')]//span/text()")
        desc_node = card.xpath(".//div[contains(@class, 'aop')]/p/span/text()")
        
        people_list.append({
            "review_name": next(iter(name_node), "N/A").strip(),
            "designation": next(iter(designation), "N/A").strip(),
            "rating": next(iter(rating_node), "No Rating").strip(),
            "review_count": next(iter(review_count_node), "0 Reviews").strip(),
            "description": next(iter(desc_node), "N/A").strip()
        })

    result_data = {
        "url": url,
        "title": title,
        "address": address,
        "rating_value": aggregate_rating.get('ratingValue', 'N/A'),
        "review_count": str(aggregate_rating.get('reviewCount', 'N/A')),
        "worst_rating": aggregate_rating.get('worstRating', 'N/A'),
        "best_rating": aggregate_rating.get('bestRating', 'N/A'),
        "contact": office_contact if office_contact else "N/A",
        'website_url': website_url if website_url else "N/A",
        "details": details_text if details_text else "N/A",
        "areas_of_practice": legal_service.get('knowsAbout', []),
        "total_people_count": total_people_count,
        "attorneys": people_list if people_list else "N/A"
        }

    return result_data

def fetch_address(address_url, html_text):
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.martindale.com/organizations/2388314/other-offices?__cf_chl_tk=d6QfhE5bxXx8HajxEr3xx5Q.mU75G3B_ruTQcLbweS8-1780558661-1.0.1.1-ClGw8D9wBThiyqCPIpm7Odkhr_XqSgTiM7Qh0pN2L5c',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"148.0.7778.217"',
    'sec-ch-ua-full-version-list': '"Chromium";v="148.0.7778.217", "Google Chrome";v="148.0.7778.217", "Not/A)Brand";v="99.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'cookie': 'cf_clearance=ti2ShsN8dKupbJdZcgCtWCqlBq7OlZ9VIvjeDcUmNUE-1780558688-1.2.1.1-4DrL0KniCbZ.nTrcuXdDG5Q_DomMr37WznUPL7531q61NeL.dtT_8O4SXbFT.jNyMO3DILMp3VXaxcaWb84y0P7zvLhyT7dnz3MHEJSOw3EFqaD51pYksP4dNTELnrNoMueQgpMprX31iYpWAzbkXg3tdCK63Oo3n29ix2eNy9RW2J1hUirbA7DotEgT2Xc3TKAfGQ6CqwBHdESFqu8TCIpWcxkv_7DjWw8dpLTZ5dUx5u48UFpyFcgQvPRzFLiuMj6i47DQ5EA9z7V9iLGmA5pcWCE7EUx1jGeWos8kFthWIF4sGbIVKMvopfv.vynczNjDDDF8oXMJy1YWGlwnTjKZZvYkbeRjHVfyrsNaedSo9cCYNIDl_Etwz9SeIE.7TVuFyrgurN6aZStGbngzQdQAEIZN1Uya9nmGnk5F2gw; launch=prod-mac; BIGipServerlgl-martindale-k8sw_24080_POOL=3515879434.4190.0000; laravel_session=eyJpdiI6IkZnbWhta2hnNjhmRHJKblN6OFQxUmc9PSIsInZhbHVlIjoia2xsMHFJUlVsL0J4QkRGV0FIZmxnV2RsL2tDZXJrTjRrZHRRcHFTWEh2NkhFKzdPU3E0N0c0amZzMXRKRnQwa3NqdDRnYzR4dHpmN3J6b1dLNnVRa3dQNG5pckt3WXJ5bTAzSlY2OXd2ZFFtTkhrL2pVNENQOVBwdjRkWFZlZTQiLCJtYWMiOiI2MGMwNDYyOTQ4MDNkYzc1OWVlNTM4MTBjY2RhMGMyZTgxNGJmYzg4YTIyOTgxNmNmM2FjYzgwZDNjM2VmODFlIiwidGFnIjoiIn0%3D; __cf_bm=RXBOTSiI6R7D91CKX.zBBIRFFCXpuomZ2Cp_7.AQezM-1780559181.9531114-1.0.1.1-QxGXUmwFmsaQN804waVPh65_HZWXEh8Ttuj32FkGv.33IITPqGWc_c2fEoWp3Sc2QnDbknGtPJgyaUKJkSZJze..G9xbiR27O5F7UF_Jmsyht6sYjhLCtJcT9SD8tBcD',
}
    response = requests.get(address_url, headers=headers)

    if response.status_code == 403:
        print(f"403 Forbidden on address URL: {address_url} — returning empty address list.")
        return []

    address_text = response.text
    selector_address = Selector(address_text)
    selector_html = Selector(html_text) 

    address = []

    address_lines = selector_html.xpath('(//div[contains(@class, "office-address")])[1]//span//text()').getall()
    main_address = (
        ", ".join(
            l
            for l in [
                line.strip()
                for line in address_lines
                if (
                    line.strip()
                    and len(line) > 2
                    and "Open for Business" not in line
                    and "Offers Video Calls" not in line
                    and "Get Directions" not in line
                )
            ][1:]  
            if len(l) > 1
        )
        if address_lines
        else None
    )
    if not main_address:
        main_address = selector_html.xpath("string(//li[contains(@class,'masthead-list__item--bold')]/following-sibling::li[1])").get().strip()

    other_address_list = []
    other_addresses = selector_address.xpath('//div[contains(@class, "office-address")]')
    for other_address in other_addresses:
        other_address_lines = other_address.xpath('.//text()').getall()
        other_address = (
            ", ".join(
                l
                for l in [
                    line.strip()
                    for line in other_address_lines
                    if (
                        line.strip()
                        and len(line) > 2
                        and "Open for Business" not in line
                        and "Offers Video Calls" not in line
                        and "Get Directions" not in line
                    )
                ][1:]  
                if len(l) > 1
            )
            if other_address_lines
            else None
        )
        other_address = re.sub(r'\s+', ' ',  other_address)
        other_address = other_address.replace(" ,", ",")
        other_address_list.append(other_address)

    if main_address:
        main_address = re.sub(r'\s+', ' ',  main_address)
        main_address = main_address.replace(" ,", ",")
        address = [main_address] 
    address.extend(other_address_list)
    return address


def process(item):
    latest_id = item["id"]
    target_url = item["link"]
    city = item["city"]
    state = item["state"]
    category = item["category"].strip()

    print(f"\nScraping: {target_url}")

    try:
        scraped_json_output = scrape_page(
            target_url, page_save_path=save_directory
        )
        insert_scraped_data(
            data=scraped_json_output,
            city=city,
            state=state,
            category=category,
        )
        update_firmlink_status(latest_id)
    except Exception as e:
        if "403 Forbidden" in str(e):
            print(f"403 received for {target_url} — skipping insert and status update.")
        else:
            print(f"Error handling URL {target_url}: {e}")


if __name__ == "__main__":
    start = input("Enter a number")
    end =  input("Enter a number" )
    save_directory = "C:/Users/mihir.dudhat/Desktop/mihir"
    all_firm_links = fetch_firmlinks_batch(start, end)
    print(len(all_firm_links))
    with ThreadPoolExecutor(max_workers=4) as e:
        e.map(process, all_firm_links)
    
    print("\nAll tasks completed successfully!")