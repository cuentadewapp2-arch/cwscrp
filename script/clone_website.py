import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clone_website(base_url, output_folder="cloned_site"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Send a GET request to the base URL with headers
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            print(f'Error {response.status_code}: Could not fetch {base_url}')
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links on the page
        links = [urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True)]
        
        for link in links:
            try:
                # Add delay between requests
                time.sleep(1)
                response = requests.get(link, headers=headers)
                if response.status_code != 200:
                    print(f'Error {response.status_code}: Could not fetch {link}')
                    continue
                
                # Extract filename from URL
                filename = link.split('/')[-1]
                file_path = os.path.join(output_folder, filename)
                
                # Save content to file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                    print(f'Saved {filename}')
            except Exception as e:
                print(f'Error downloading {link}: {str(e)}')
                continue
    except Exception as e:
        print(f'Error cloning website: {str(e)}')

if __name__ == '__main__':
    clone_website('https://www.camwhores.tv/', 'camwhores_cloned')