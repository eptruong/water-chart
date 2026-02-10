const fs = require('fs');

// Helper functions
function getPackagingType(name) {
  const lower = name.toLowerCase();
  if (lower.includes('glass')) return 'glass';
  if (lower.includes('aluminum') || lower.includes('can')) return 'aluminum';
  if (lower.includes('plastic')) return 'plastic';
  if (lower.includes('carton')) return 'carton';
  if (lower.includes('gallon')) return 'plastic';
  return 'glass';
}

function getSourceType(name) {
  const lower = name.toLowerCase();
  if (lower.includes('spring')) return 'spring';
  if (lower.includes('mineral')) return 'mineral';
  if (lower.includes('volcanic')) return 'volcanic';
  if (lower.includes('artesian')) return 'artesian';
  if (lower.includes('glacial')) return 'spring';
  if (lower.includes('alkaline')) return 'municipal';
  if (lower.includes('purified') || lower.includes('distilled')) return 'municipal';
  return 'spring';
}

function getBrandFromName(name) {
  const words = name.split(' ');
  return words[0];
}

// All collected products
const allProducts = [
  {"name": "Aqua Carpatica Spring Water Glass Bottle", "score": 92, "type": "bottled_water"},
  {"name": "Hawaii Volcanic Still Glass Bottle", "score": 91, "type": "bottled_water"},
  {"name": "Hallstein Water Glass Bottle", "score": 91, "type": "bottled_water"},
  {"name": "Icelandic Glacial Water Glass Bottle", "score": 90, "type": "bottled_water"},
  {"name": "Icelandic Glacial Sparkling Water Glass Bottle", "score": 90, "type": "sparkling_water"},
  {"name": "Acqua Filette Natural Glass Bottle", "score": 90, "type": "bottled_water"},
  {"name": "Acqua Filette Gently Sparklin Glass Bottle", "score": 90, "type": "sparkling_water"},
  {"name": "Acqua Filette Very Sparkling Glass Bottle", "score": 90, "type": "sparkling_water"},
  {"name": "Icelandic Glacial Water Plastic Bottle", "score": 86, "type": "bottled_water"},
  {"name": "Galvanina Still Mineral Water Glass Bottle", "score": 86, "type": "bottled_water"},
  {"name": "Vellamo Still Spring Water Glass Bottle", "score": 85, "type": "bottled_water"},
  {"name": "Hawaii Volcanic Sparkling Glass Bottle", "score": 84, "type": "sparkling_water"},
  {"name": "Panama Blue Water Glass Bottle", "score": 83, "type": "bottled_water"},
  {"name": "Gerolsteiner Sparkling Mineral Water Glass Bottle", "score": 82, "type": "sparkling_water"},
  {"name": "Hallstein Water Gallon", "score": 81, "type": "water_delivery"},
  {"name": "Waiakea Alkaline Water Aluminum Bottle", "score": 80, "type": "bottled_water"},
  {"name": "Waiakea Hawaiian Volcanic Sparkling Water Aluminum Bottle", "score": 80, "type": "sparkling_water"},
  {"name": "Icelandic Glacial Still Water Can", "score": 79, "type": "bottled_water"},
  {"name": "Fontis Spring Bottled Water Gallon", "score": 79, "type": "bottled_water"},
  {"name": "Ophora Water Hyper-Oxygenated Half Gallon Glass Bottle", "score": 79, "type": "bottled_water"},
  {"name": "Flow Alkaline Cucumber + Mint Flavored Spring Water Carton", "score": 64, "type": "flavored_water"},
  {"name": "Mountain Valley Blackberry Pomegranate Flavored Sparkling Water Glass Bottle", "score": 50, "type": "flavored_water"},
  {"name": "365 Sparkling Water Lime Can", "score": 40, "type": "flavored_water"},
  {"name": "Perrier Pink Grapefruit Flavored Water Can", "score": 38, "type": "flavored_water"},
  {"name": "smartwater Cucumber Lime Plastic Bottle", "score": 38, "type": "flavored_water"},
  {"name": "MONTELLiER® Carbonated Natural Spring Water Lemon Can", "score": 38, "type": "flavored_water"},
  {"name": "Liquid Death Cherry Obituary Flavored Sparkling Water Can", "score": 33, "type": "flavored_water"},
  {"name": "Jana Flavored Water Plastic Bottle", "score": 30, "type": "flavored_water"},
  {"name": "Sprouts Organic Lemon Sparkling Mineral Water Glass Bottle", "score": 29, "type": "flavored_water"},
  {"name": "KOR LVL UP Organic Hydrate Orange Ginger Plastic Bottle", "score": 25, "type": "flavored_water"},
  {"name": "Sanzo Flavored Sparkling Water Can", "score": 23, "type": "flavored_water"},
  {"name": "B'EAU Collagen Water Can", "score": 23, "type": "flavored_water"},
  {"name": "Wild Noni Sparkling Can", "score": 23, "type": "flavored_water"},
  {"name": "Path Sparkling Flavored Water Can", "score": 20, "type": "flavored_water"},
  {"name": "Mela Watermelon Water Can", "score": 17, "type": "flavored_water"},
  {"name": "Highland Spring Sparkling Flavored Water Can", "score": 13, "type": "flavored_water"},
  {"name": "POPPI Lemon Lime Can", "score": 11, "type": "flavored_water"},
  {"name": "Lemon Perfect Hydrating Lemon Water Plastic Bottle", "score": 9, "type": "flavored_water"},
  {"name": "CORE Hydration+ Calm Plastic Bottle", "score": 9, "type": "flavored_water"},
  {"name": "Spindrift Sparkling Water Lemon Can", "score": 8, "type": "flavored_water"},
  {"name": "Icelandic Glacial Classic Carbonated Water Can", "score": 79, "type": "sparkling_water"},
  {"name": "Loonen Sparkling Water Glass Bottle", "score": 71, "type": "sparkling_water"},
  {"name": "Calistoga Sparkling Mineral Water Plastic Bottle", "score": 70, "type": "sparkling_water"},
  {"name": "Crystal Geyser Sparkling Spring Water", "score": 68, "type": "sparkling_water"},
  {"name": "Agua de Piedra Sparkling Mineral Water Glass Bottle", "score": 68, "type": "sparkling_water"},
  {"name": "Evian Sparkling Water Glass Bottle", "score": 65, "type": "sparkling_water"},
  {"name": "Crystal Geyser Sparkling Mineral Water", "score": 62, "type": "sparkling_water"},
  {"name": "Chilly Water Orginal Sparkling Water Can", "score": 57, "type": "sparkling_water"},
  {"name": "The Mountain Valley Sparkling Water Glass Bottle", "score": 52, "type": "sparkling_water"},
  {"name": "Voss Sparkling Water Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Chiarella Symposion Sparkling Natural Water Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Clearly Canadian Sparkling Mineral Water Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Sibilla Sparkling Water Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Santa Vittoria Sparkling Water Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Galvanina Sparkling Mineral Water Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Apollinaris Selection Sparkling Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Staatl. Fachingen Sparkling Water Glass Bottle", "score": 50, "type": "sparkling_water"},
  {"name": "Berkshire Springs Gallon", "score": 76, "type": "water_delivery"},
  {"name": "Kentwood Springs Artesian Water Gallon", "score": 75, "type": "water_delivery"},
  {"name": "Labrador Source Spring Water Gallon", "score": 59, "type": "water_delivery"},
  {"name": "Mountain Valley Spring Water Gallon", "score": 50, "type": "water_delivery"},
  {"name": "Bear Springs Canadian Spring Water Gallon", "score": 50, "type": "water_delivery"},
  {"name": "Alta Alkaline Water Gallon", "score": 50, "type": "water_delivery"},
  {"name": "Blue Falls Purified Water Gallon", "score": 46, "type": "water_delivery"},
  {"name": "Primo Spring Water Gallon", "score": 45, "type": "water_delivery"},
  {"name": "Sparkletts Spring Water Gallon", "score": 44, "type": "water_delivery"},
  {"name": "Clír Irish Spring Water Water Gallon", "score": 40, "type": "water_delivery"},
  {"name": "TriBeCa Spring Water Gallon", "score": 38, "type": "water_delivery"},
  {"name": "Phresh Waters Spring Water Gallon", "score": 35, "type": "water_delivery"},
  {"name": "Alka1 Alkaline Water Gallon", "score": 35, "type": "water_delivery"},
  {"name": "Primo Purified Water Gallon", "score": 31, "type": "water_delivery"},
  {"name": "Sparkletts Distilled Water Gallon", "score": 31, "type": "water_delivery"},
  {"name": "Menehune Purified Water Gallon", "score": 31, "type": "water_delivery"},
  {"name": "Sparkletts Purified Water Gallon", "score": 30, "type": "water_delivery"},
  {"name": "Ice River Springs Natural Spring Water Gallon", "score": 30, "type": "water_delivery"},
  {"name": "Canadian Springs Natural Spring Water", "score": 30, "type": "water_delivery"}
];

// Remove duplicates and process
const processedProducts = [];
const seen = new Set();

allProducts.forEach(product => {
  const key = product.name.toLowerCase().trim();
  if (!seen.has(key)) {
    seen.add(key);
    
    const processed = {
      id: null,
      name: product.name,
      score: product.score,
      type: product.type,
      image: null,
      brand: getBrandFromName(product.name),
      packaging: getPackagingType(product.name),
      source: getSourceType(product.name),
      details: null
    };
    
    processedProducts.push(processed);
  }
});

// Save to file
fs.writeFileSync('data.json', JSON.stringify(processedProducts, null, 2));
console.log(`Saved ${processedProducts.length} unique products to data.json`);

// Show summary
const typeCount = {};
processedProducts.forEach(p => {
  typeCount[p.type] = (typeCount[p.type] || 0) + 1;
});
console.log('By type:', typeCount);

// Show top brands
const brandCount = {};
processedProducts.forEach(p => {
  brandCount[p.brand] = (brandCount[p.brand] || 0) + 1;
});
const topBrands = Object.entries(brandCount)
  .sort(([,a], [,b]) => b - a)
  .slice(0, 10);
console.log('Top brands:', topBrands);