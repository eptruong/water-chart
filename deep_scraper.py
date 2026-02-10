#!/usr/bin/env python3

import json
import re
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse, urljoin
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OasisScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.products = {}
        self.search_queries = self._build_search_queries()
        
    def _build_search_queries(self):
        """Build comprehensive list of search queries"""
        queries = []
        
        # Alphabet search
        queries.extend([chr(i) for i in range(ord('a'), ord('z') + 1)])
        
        # Water-related terms
        water_terms = [
            "water", "spring", "sparkling", "mineral", "purified", "alkaline", 
            "filtered", "electrolyte", "coconut", "flavored", "delivery", 
            "glacial", "artesian", "distilled", "natural", "volcanic", 
            "still", "gas", "carbonated", "enhanced", "raw", "structured"
        ]
        queries.extend(water_terms)
        
        # Brand names
        brands = [
            "evian", "fiji", "voss", "perrier", "pellegrino", "gerolsteiner",
            "aquafina", "dasani", "smartwater", "essentia", "core", "lifewtr",
            "topo chico", "mountain valley", "saratoga", "waiakea", "icelandic",
            "aqua carpatica", "hallstein", "hawaii volcanic", "crystal geyser",
            "nestle", "ozarka", "poland spring", "zephyrhills", "arrowhead",
            "deer park", "ice mountain", "pure life", "vittel", "badoit",
            "san pellegrino", "acqua panna", "hildon", "ty nant", "belu",
            "highland spring", "buxton", "harrogate", "malvern", "strathmore"
        ]
        queries.extend(brands)
        
        # Additional descriptive terms
        descriptive = [
            "glass", "plastic", "aluminum", "bottle", "can", "premium",
            "organic", "pure", "clean", "healthy", "premium", "luxury",
            "sustainable", "eco", "natural", "fresh", "crisp", "smooth"
        ]
        queries.extend(descriptive)
        
        return list(set(queries))  # Remove duplicates
    
    def search_api(self, query):
        """Search the Oasis API for products"""
        url = "https://www.live-oasis.com/search"
        payload = [query, 40, "$undefined"]
        
        try:
            logger.info(f"Searching for: {query}")
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            # Parse RSC format response
            content = response.text
            products = self._parse_rsc_response(content)
            
            for product in products:
                if 'slug' in product:
                    self.products[product['slug']] = product
                    
            logger.info(f"Found {len(products)} products for query '{query}'")
            return products
            
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
            return []
    
    def _parse_rsc_response(self, content):
        """Parse React Server Components response format"""
        products = []
        
        try:
            # Look for product data patterns in RSC stream
            # RSC often contains JSON-like structures embedded in the stream
            
            # Pattern 1: Look for score patterns
            score_matches = re.finditer(r'"score"\s*:\s*(\d+)', content)
            
            # Pattern 2: Look for product name patterns  
            name_matches = re.finditer(r'"name"\s*:\s*"([^"]+)"', content)
            
            # Pattern 3: Look for slug patterns
            slug_matches = re.finditer(r'"slug"\s*:\s*"([^"]+)"', content)
            
            # Pattern 4: Look for type patterns
            type_matches = re.finditer(r'"type"\s*:\s*"([^"]+)"', content)
            
            # Try to extract complete JSON objects
            json_pattern = r'\{[^{}]*"slug"[^{}]*\}'
            json_matches = re.finditer(json_pattern, content)
            
            for match in json_matches:
                try:
                    json_str = match.group()
                    # Clean up the JSON string
                    json_str = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', json_str)
                    product_data = json.loads(json_str)
                    if 'slug' in product_data:
                        products.append(product_data)
                except:
                    continue
            
            # Fallback: extract individual fields and try to match them
            if not products:
                # Extract all slugs, scores, names, types
                slugs = [m.group(1) for m in slug_matches]
                scores = [int(m.group(1)) for m in score_matches]
                names = [m.group(1) for m in name_matches]
                types = [m.group(1) for m in type_matches]
                
                # Try to match them up (assume they appear in similar order)
                min_len = min(len(slugs), len(scores), len(names))
                for i in range(min_len):
                    product = {
                        'slug': slugs[i],
                        'score': scores[i] if i < len(scores) else None,
                        'name': names[i] if i < len(names) else slugs[i],
                        'type': types[i] if i < len(types) else 'bottled_water'
                    }
                    products.append(product)
            
        except Exception as e:
            logger.error(f"Error parsing RSC response: {e}")
            # Try alternative parsing methods
            
            # Look for any URLs that might contain product slugs
            url_pattern = r'/product/([^/\s"]+)'
            url_matches = re.finditer(url_pattern, content)
            for match in url_matches:
                slug = match.group(1)
                products.append({'slug': slug, 'name': slug.replace('-', ' ').title()})
        
        return products
    
    def scrape_product_page(self, slug):
        """Scrape individual product page for detailed data"""
        url = f"https://www.live-oasis.com/product/{slug}"
        
        try:
            logger.info(f"Scraping product: {slug}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product data
            product_data = {
                'id': slug,
                'slug': slug,
                'contaminants': [],
                'total_contaminants': 0,
                'contaminants_above_guidelines': 0
            }
            
            # Get name
            name_el = soup.find('h1') or soup.find('title')
            if name_el:
                product_data['name'] = name_el.get_text().strip()
            else:
                product_data['name'] = slug.replace('-', ' ').title()
            
            # Get score
            score_patterns = [
                r'score["\']?\s*:\s*(\d+)',
                r'rating["\']?\s*:\s*(\d+)',
                r'(?:score|rating)\D+(\d+)'
            ]
            for pattern in score_patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    product_data['score'] = int(match.group(1))
                    break
            
            # Get brand (from name or specific element)
            brand_match = re.search(r'^([A-Z][a-zA-Z\s]+)', product_data.get('name', ''))
            if brand_match:
                product_data['brand'] = brand_match.group(1).strip()
            
            # Get packaging type
            packaging_keywords = {
                'glass': ['glass', 'bottle'],
                'plastic': ['plastic', 'pet', 'bottle'],  
                'aluminum': ['aluminum', 'can', 'aluminium'],
                'carton': ['carton', 'tetra']
            }
            
            text_content = response.text.lower()
            for packaging, keywords in packaging_keywords.items():
                if any(keyword in text_content for keyword in keywords):
                    product_data['packaging'] = packaging
                    break
            
            # Get source type
            source_keywords = {
                'spring': ['spring', 'natural spring'],
                'mineral': ['mineral', 'natural mineral'],
                'purified': ['purified', 'filtered', 'distilled'],
                'artesian': ['artesian'],
                'volcanic': ['volcanic'],
                'glacial': ['glacial', 'glacier']
            }
            
            for source, keywords in source_keywords.items():
                if any(keyword in text_content for keyword in keywords):
                    product_data['source'] = source
                    break
            
            # Get product type
            type_keywords = {
                'sparkling_water': ['sparkling', 'carbonated', 'gas'],
                'flavored_water': ['flavored', 'flavoured', 'flavor', 'fruit'],
                'water_delivery': ['delivery', 'service'],
                'bottled_water': ['still', 'natural', 'spring', 'water']
            }
            
            for water_type, keywords in type_keywords.items():
                if any(keyword in text_content for keyword in keywords):
                    product_data['type'] = water_type
                    break
            else:
                product_data['type'] = 'bottled_water'
            
            # Parse contaminant table
            contaminants = self._parse_contaminants(soup, response.text)
            product_data['contaminants'] = contaminants
            product_data['total_contaminants'] = len(contaminants)
            product_data['contaminants_above_guidelines'] = len([c for c in contaminants if c.get('status') in ['warning', 'fail']])
            
            # Get image URL
            img_el = soup.find('img', src=re.compile(r'\.(jpg|jpeg|png|webp)', re.IGNORECASE))
            if img_el:
                img_src = img_el.get('src')
                if img_src:
                    product_data['image'] = urljoin(url, img_src)
            
            logger.info(f"Successfully scraped {slug}: {len(contaminants)} contaminants found")
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping product {slug}: {e}")
            return None
    
    def _parse_contaminants(self, soup, html_content):
        """Extract contaminant data from product page"""
        contaminants = []
        
        try:
            # Look for contaminant table or data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Check if this looks like a contaminant table
                header_text = ' '.join([th.get_text() for th in table.find_all(['th', 'td'])][:3]).lower()
                if any(keyword in header_text for keyword in ['contaminant', 'detected', 'limit', 'ppb', 'ppm']):
                    
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            contaminant = {}
                            
                            # Try to extract contaminant name, detected amount, limits
                            texts = [cell.get_text().strip() for cell in cells]
                            
                            contaminant['name'] = texts[0]
                            
                            # Look for detected amount
                            for text in texts[1:]:
                                if re.search(r'\d+\.?\d*\s*(ppb|ppm|mg|μg)', text, re.IGNORECASE):
                                    contaminant['detected'] = text
                                    break
                            
                            # Look for legal limit
                            for text in texts[1:]:
                                if 'limit' in text.lower() or 'legal' in text.lower():
                                    contaminant['legal_limit'] = text
                                    break
                            
                            # Look for health guideline
                            for text in texts[1:]:
                                if 'health' in text.lower() or 'guideline' in text.lower():
                                    contaminant['health_guideline'] = text
                                    break
                            
                            # Determine status
                            if 'detected' in contaminant:
                                detected_val = self._extract_numeric_value(contaminant['detected'])
                                legal_val = self._extract_numeric_value(contaminant.get('legal_limit', ''))
                                health_val = self._extract_numeric_value(contaminant.get('health_guideline', ''))
                                
                                if legal_val and detected_val > legal_val:
                                    contaminant['status'] = 'fail'
                                elif health_val and detected_val > health_val:
                                    contaminant['status'] = 'warning'
                                else:
                                    contaminant['status'] = 'pass'
                            else:
                                contaminant['status'] = 'unknown'
                            
                            if contaminant.get('name'):
                                contaminants.append(contaminant)
            
            # Alternative: Look for JSON data containing contaminants
            json_matches = re.finditer(r'\{[^{}]*contaminant[^{}]*\}', html_content, re.IGNORECASE)
            for match in json_matches:
                try:
                    json_str = match.group()
                    data = json.loads(json_str)
                    if isinstance(data, dict) and 'name' in data:
                        contaminants.append(data)
                except:
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing contaminants: {e}")
        
        return contaminants
    
    def _extract_numeric_value(self, text):
        """Extract numeric value from text like '0.5 ppb'"""
        if not text:
            return None
        
        match = re.search(r'(\d+\.?\d*)', str(text))
        if match:
            return float(match.group(1))
        return None
    
    def run_full_scrape(self):
        """Run the complete scraping process"""
        logger.info("Starting comprehensive Oasis water product scrape...")
        
        # Phase 1: Search for all products
        all_products = {}
        for i, query in enumerate(self.search_queries):
            logger.info(f"Progress: {i+1}/{len(self.search_queries)} - Searching '{query}'")
            products = self.search_api(query)
            
            for product in products:
                if 'slug' in product:
                    all_products[product['slug']] = product
            
            # Rate limiting
            time.sleep(0.5)
        
        logger.info(f"Phase 1 complete: Found {len(all_products)} unique products")
        
        # Phase 2: Scrape individual product pages
        enriched_products = []
        for i, (slug, basic_data) in enumerate(all_products.items()):
            logger.info(f"Phase 2 progress: {i+1}/{len(all_products)} - Scraping {slug}")
            
            detailed_data = self.scrape_product_page(slug)
            if detailed_data:
                # Merge basic and detailed data
                final_product = {**basic_data, **detailed_data}
                enriched_products.append(final_product)
            
            # Rate limiting and save progress
            time.sleep(1)
            
            if (i + 1) % 10 == 0:  # Save every 10 products
                self._save_progress(enriched_products)
        
        logger.info(f"Scraping complete: {len(enriched_products)} products with detailed data")
        return enriched_products
    
    def _save_progress(self, products):
        """Save progress to data.json"""
        try:
            with open('/home/clawdbot-1/clawd/tools/water-chart/data.json', 'w') as f:
                json.dump(products, f, indent=2)
            logger.info(f"Progress saved: {len(products)} products")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

if __name__ == "__main__":
    scraper = OasisScraper()
    products = scraper.run_full_scrape()
    
    # Final save
    with open('/home/clawdbot-1/clawd/tools/water-chart/data.json', 'w') as f:
        json.dump(products, f, indent=2)
    
    print(f"\n🎉 Scraping complete! Found {len(products)} products with detailed contaminant data.")
    print("Data saved to data.json")