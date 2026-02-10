// Water product scraping script for Oasis Health app
const products = [];
const productIds = new Set();

// Function to extract basic product info from the current page
function extractVisibleProducts() {
  const productElements = document.querySelectorAll('[data-testid="product-card"], div[class*="cursor-pointer"]:has(img):has(p):not([role="option"])');
  const currentProducts = [];
  
  productElements.forEach(el => {
    const img = el.querySelector('img');
    const nameEl = el.querySelector('div, p, span');
    const scoreEl = el.querySelector('p');
    
    if (img && nameEl && img.alt && img.alt !== 'Oasis') {
      const name = img.alt;
      const scoreText = el.textContent;
      const scoreMatch = scoreText.match(/(\d+)\/100/);
      const score = scoreMatch ? parseInt(scoreMatch[1]) : null;
      
      if (name && score && !name.includes('Oasis')) {
        const product = {
          name: name,
          score: score,
          element: el,
          type: getProductType(name)
        };
        currentProducts.push(product);
      }
    }
  });
  
  return currentProducts;
}

// Function to determine product type based on name
function getProductType(name) {
  const lower = name.toLowerCase();
  if (lower.includes('sparkling')) return 'sparkling_water';
  if (lower.includes('flavored')) return 'flavored_water';
  if (lower.includes('delivery')) return 'water_delivery';
  return 'bottled_water';
}

// Function to determine packaging type
function getPackagingType(name) {
  const lower = name.toLowerCase();
  if (lower.includes('glass')) return 'glass';
  if (lower.includes('aluminum') || lower.includes('can')) return 'aluminum';
  if (lower.includes('plastic')) return 'plastic';
  if (lower.includes('carton')) return 'carton';
  if (lower.includes('gallon')) return 'plastic'; // Most gallons are plastic
  return 'glass'; // Default assumption for premium waters
}

// Function to determine source type
function getSourceType(name) {
  const lower = name.toLowerCase();
  if (lower.includes('spring')) return 'spring';
  if (lower.includes('mineral')) return 'mineral';
  if (lower.includes('volcanic')) return 'volcanic';
  if (lower.includes('artesian')) return 'artesian';
  if (lower.includes('glacial')) return 'spring'; // Glacial is typically spring
  return 'spring'; // Default assumption
}

// Extract products from current page
const currentPageProducts = extractVisibleProducts();
console.log(`Found ${currentPageProducts.length} products on current page:`);
currentPageProducts.forEach(p => console.log(`- ${p.name} (${p.score}/100)`));

currentPageProducts;