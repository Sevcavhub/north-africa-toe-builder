const pdf = require('pdf-parse');
const fs = require('fs');
const path = require('path');

const pdfPath = path.join(__dirname, 'Resource Documents', 'British_PRIMARY_SOURCES', '682349763-Battle-Orders-028-Desert-Rats-British-8th-Army-in-North-Africa-1941-43.pdf');

console.log('Testing PDF-parse API...');
console.log('PDF path:', pdfPath);

(async () => {
  try {
    // Method 1: Try with {data: buffer}
    console.log('\n[Test 1] Trying load with {data: buffer}...');
    const parser1 = new pdf.PDFParse({});
    const buffer = fs.readFileSync(pdfPath);
    await parser1.load({data: buffer});
    const text1 = await parser1.getText();
    console.log('✅ Success! Text length:', text1.length);
    process.exit(0);
  } catch (e1) {
    console.log('❌ Failed:', e1.message);

    try {
      // Method 2: Try with {url: filePath}
      console.log('\n[Test 2] Trying load with {url: filePath}...');
      const parser2 = new pdf.PDFParse({});
      await parser2.load({url: pdfPath});
      const text2 = await parser2.getText();
      console.log('✅ Success! Text length:', text2.length);
      process.exit(0);
    } catch (e2) {
      console.log('❌ Failed:', e2.message);

      try {
        // Method 3: Try with file:// URL
        console.log('\n[Test 3] Trying load with file:// URL...');
        const parser3 = new pdf.PDFParse({});
        const fileUrl = `file:///${pdfPath.replace(/\\/g, '/')}`;
        await parser3.load({url: fileUrl});
        const text3 = await parser3.getText();
        console.log('✅ Success! Text length:', text3.length);
        process.exit(0);
      } catch (e3) {
        console.log('❌ Failed:', e3.message);
        console.log('\n❌ All methods failed!');
        process.exit(1);
      }
    }
  }
})();
