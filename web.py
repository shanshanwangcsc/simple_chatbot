import requests
from requests_html import HTMLSession

from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from urllib.parse import urljoin, urlparse
from langchain.docstore.document import Document
import fitz
session = HTMLSession()
class RecursiveWebLoader(WebBaseLoader):
    def __init__(self, base_url, depth=2):
        self.base_url = base_url
        self.depth = depth
        self.visited_urls = set()

    def load(self, url=None, depth=0):
        if url is None:
            url = self.base_url

        # Check if we've already visited this URL or if we've reached the maximum depth
        if url in self.visited_urls or depth > self.depth:
            return []

        # Mark the URL as visited
        self.visited_urls.add(url)
        documents = []
        # Fetch and parse the page
        if url.endswith('.pdf'):
            try:
                response = requests.get(url)
                response.raise_for_status()
                pdf_content = load_pdf_from_url(response.content)
                documents.append((url, pdf_content))
                print(f"Scraped PDF content from {url} (Depth: {depth})")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching PDF {url}: {e}")
        else:

            try:
                #response = requests.get(url)
                r = session.get(url)
                #r.html.render(sleep=3, timeout=20) # wait for 3s until the page fully loaded
                r.html.render() # wait for 3s until the page fully loaded
                soup = BeautifulSoup(r.html.raw_html, "html.parser")
                #response.raise_for_status()  # Raise an error for bad responses
                #soup = BeautifulSoup(response.content, 'html.parser')
            except (requests.RequestException, Exception) as e:
                print(f"Failed to load {url}: {e}")
                return []

            # Extract text content
            content = soup.get_text(separator=' ', strip=True)

            # Load the content into a LangChain Document
            documents.append((url ,content))
            print(f"Scraped content from {url} (Depth: {depth})")
            # Find all links on the page
            links = soup.find_all('a', href=True)
            #links = soup.select('a.my-class')
            #breakpoint()
            for link in links:
                href = link['href']
                # Create an absolute URL from the relative URLs
                full_url = urljoin(url, href)
                #print(full_url)
                #documents.extend(self.load(full_url, depth + 1))
                #Check if the link is internal (same domain)
                if urlparse(self.base_url).netloc == urlparse(full_url).netloc:
                # Recursively visit each internal link
                    documents.extend(self.load(full_url, depth + 1))

        return documents
def load_pdf_from_url(pdf_data):
    """Load PDF content using PyMuPDF (fitz) from a bytes-like object."""
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def create_langchain_docs(scraped_data):
    documents = []
    for url, content in scraped_data:
        doc = Document(page_content=content, metadata={"source": url})
        documents.append(doc)
    return documents

#web_url ="https://jessepharrison.github.io/"
#web_url = "https://shanwangshan.github.io/shanshanwang/"
#web_url ="https://sites.google.com/view/dr-dev/home"
# Initialize the recursive web loader
#loader = RecursiveWebLoader(base_url=web_url, depth=1)

# Load content recursively
#documents = loader.load()
#breakpoint()
# At this point, `documents` contains the content from the website and its child pages
