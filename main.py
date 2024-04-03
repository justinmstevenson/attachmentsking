import requests
from bs4 import BeautifulSoup

# from time import sleep
from pprint import pprint
import csv
import re
import os
from urllib.parse import urljoin

product_links = []

def clean_data(text):
    return text.replace("\n", " ").replace("\r", "").replace("  ", "").strip()

# Loop through the pages from 1 to 41
for page_number in range(1, 42):
    print(f"Parsing page {page_number}")
    url = f"https://attachmentsking.com/collections/all?page={page_number}&grid_list=grid-view"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    for link in soup.find_all("a", href=True):
        if "/product" in link["href"]:
            # Add the link to the list if it's not already present
            full_link = f"https://attachmentsking.com{link['href']}"
            if full_link not in product_links:
                product_links.append(full_link)
# Count the number of unique product URLs
number_of_products = len(product_links)
for link in product_links:
    print(link)
print(f"Number of unique product URLs: {number_of_products}")


product_details = {}
counter = 0
images_directory = "images"

if not os.path.exists(images_directory):
    os.makedirs(images_directory)

for link in product_links:
    counter += 1
    print(f"Product # {counter}")
    # Initialize a dictionary to store the product details
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        sku = soup.find("div", id="productSKU").text.strip()
        product_details["SKU"] = sku.replace("SKU: ", "")
    except:
        product_details["SKU"] = ""

    sku_directory = os.path.join(images_directory, product_details["SKU"])
    # Create the sub-directory with the SKU name
    if not os.path.exists(sku_directory):
        os.makedirs(sku_directory)
    thumbnails = soup.select("#productThumbnails img")
    product_images = []
    for img in thumbnails:
        src = img["src"]
        # Remove everything past .jpg in the src attribute
        clean_src = re.sub(r"\?.*$", "", src)
        full_url = urljoin(url, clean_src)
        image_filename = os.path.basename(clean_src)
        image_path = os.path.join(sku_directory, image_filename)
        # Download and save the image
        with open(image_path, "wb") as f:
            f.write(requests.get(full_url).content)
        # Add the local path of the image to the list
        product_images.append(src)
    product_details["Images"] = product_images

    # Parse other product details
    try:
        product_details["Title"] = (
            soup.find("div", id="productTitle").text.strip()
            if soup.find("div", id="productTitle")
            else ""
        )
    except:
        product_details["Title"] = ""
    try:
        vendor_tag = soup.find("a", id="productVendor")
        product_details["Vendor"] = clean_data(
            vendor_tag.text.replace("Vendor: ", "")
            .replace("by:                ").strip()
        )
    except:
        product_details["Vendor"] = ""

    try:
        product_details["Vendor URL"] = vendor_tag["href"]
    except:
        product_details["Vendor URL"] = ""
    try:
        product_details["Weight"] = clean_data(
            soup.find("div", id="productWeight")
            .text.replace("Weight:                 ", "")
            .strip()
        )
    except:
        product_details["Weight"] = ""

    try:
        product_details["Description"] = soup.find(
            "div", id="productDescription"
        ).text.strip()
    except AttributeError:
        product_details["Description"] = ""

    try:
        rating_tag = soup.find("div", class_="loox-rating")
        product_details["Rating"] = rating_tag["title"] if rating_tag else ""
    except:
        product_details["Rating"] = ""

    try:
        shipping_returns = " ".join(p.text for p in soup.select(".productTabContent p"))
    except:
        shipping_returns = ""

    product_details["Shipping & Returns"] = shipping_returns
    pprint(product_details)
    with open("product_details.csv", "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=product_details.keys())
        writer.writerow(product_details)

print("Product details saved to product_details.csv")
