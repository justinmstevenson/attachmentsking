from bs4 import BeautifulSoup
import requests

# Function to get the content from the URL
def get_content(url):
    response = requests.get(url)
    return response.content

# Function to find all sitemap <loc> that contains /sitemap_products
def find_sitemap_locs(xml_content):
    soup = BeautifulSoup(xml_content, 'xml')
    sitemap_locs = [loc.text for loc in soup.find_all('loc') if '/sitemap_products' in loc.text]
    print(f"Found {len(sitemap_locs)} sitemap(s) containing '/sitemap_products'.")
    return sitemap_locs

product_index = 1
# Function to find the first <url> <loc> that contains /products from each sitemap
def find_product_locs(sitemap_locs):
    global product_index
    product_locs = []
    for sitemap_index, sitemap_url in enumerate(sitemap_locs, start=1):
        sitemap_content = get_content(sitemap_url)
        soup = BeautifulSoup(sitemap_content, 'xml')
        for url in soup.find_all('url'):
            loc = url.find('loc')
            if loc and '/products' in loc.text:
                product_locs.append(loc.text)
                print(f"Sitemap {sitemap_index}: Product {product_index}: URL {loc.text}")
                product_index += 1  # Increment product index for each sitemap
    return product_locs

# Main process
sitemap_url = 'https://zumasales.com/sitemap.xml'  # Replace with your sitemap URL
sitemap_content = get_content(sitemap_url)
sitemap_locs = find_sitemap_locs(sitemap_content)
product_locs = find_product_locs(sitemap_locs)

# Print the total count of product URLs
print(f"Total number of product URLs: {len(product_locs)}")
