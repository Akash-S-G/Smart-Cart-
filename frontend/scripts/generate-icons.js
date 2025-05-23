const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

async function generateIcons() {
  const sizes = [192, 512];
  const inputSvg = path.join(__dirname, '../public/logo.svg');
  
  for (const size of sizes) {
    await sharp(inputSvg)
      .resize(size, size)
      .png()
      .toFile(path.join(__dirname, `../public/logo${size}.png`));
  }

  // Generate favicon
  await sharp(inputSvg)
    .resize(32, 32)
    .png()
    .toFile(path.join(__dirname, '../public/favicon.png'));
}

generateIcons().catch(console.error); 