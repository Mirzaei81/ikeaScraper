
import axios from 'axios'
import {Jimp,JimpMime} from "jimp"
import puppeteer, {ElementHandle, Puppeteer} from "puppeteer-core"
async function getProduct(sku:string) {
    const url = `https://zardaan.com/wp-json/wc/v3/products?sku=${sku}`;
    const headers = {
        'Authorization': 'Basic Y2tfYTdjNGVlM2U5NTc1MDI4MWQ5MTg1MmRlOTJkMjc1NWNkMDUyZGUyMjpjc18yNWU4NDQ4YzZkMWE1YzdkYTlhMGFlMDE0Y2M4ZWQ2YzViMGU2MWE5',
        'Content-Type': 'application/json',
        'Cookie': 'pxcelPage_c01002=1'
    };
    // Fetch product data
    const response = await axios.get(url, { headers });
    const zProd = response.data;

    // Process first 3 images
    const imgPath = []
    for (let img of zProd[0].images.slice(0, 2)) {
        // Download image
        const imgResponse = await axios.get(img.src, { responseType: 'arraybuffer' });
        const ext = img.src.split('.').pop().toUpperCase() === 'JPG' ? 'JPEG' : img.src.split('.').pop().toUpperCase();

        // Load and resize image
        const image = await Jimp.read(Buffer.from(imgResponse.data));
        image.resize({w: 600,h: 600}).write(`output_${img.id}.${ext.toLowerCase()}`);
        imgPath.push(`output_${img.id}.${ext.toLowerCase()}`);
    }
    const browser = await puppeteer.launch({executablePath:"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",headless:false})
    const page = await browser.newPage()
    page.setCookie({ name: "access-token",domain:"seller.snappshop.ir", value: "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMDUiLCJqdGkiOiJhMjg1M2Y3NzE5MzI2YzYxNGQ4ZWM2Y2ZlM2IwZjQ1MGYwMDk0ZWU4ZWM4ZGVkZmNiMTNjNjU1NGVmNTE3Y2U5YzgwMzQxZmJhMGY1OTg0MiIsImlhdCI6MTc0ODA4MDQ3MS45Mzk5MTYsIm5iZiI6MTc0ODA4MDQ3MS45Mzk5MTksImV4cCI6MTc0ODY4NTI3MS45MzQ3NDksInN1YiI6IjQyNzM5MjAiLCJzY29wZXMiOlsicm9sZTpzZWxsZXIiXSwiYXV0aG9yaXphdGlvbl9kZXRhaWxzIjpbeyJ0eXBlIjoicHVzaCIsImxvY2F0aW9ucyI6WyJjbHVzdGVyOjEwNS92aG9zdDpwcy9xdWV1ZTptcXR0LSovcm91dGluZy1rZXk6di1nZVpsODEiXSwiYWN0aW9ucyI6WyJyZWFkIiwid3JpdGUiLCJjb25maWd1cmUiXX0seyJ0eXBlIjoicHVzaCIsImxvY2F0aW9ucyI6WyJjbHVzdGVyOjEwNS92aG9zdDpwcy9leGNoYW5nZTphbXEudG9waWMvcm91dGluZy1rZXk6di1nZVpsODEiXSwiYWN0aW9ucyI6WyJyZWFkIl19XX0.o91zwFyBgoZSvV-99NJE7GxLAmrmbDBU0xopHZ66OU4rwFUNbxDOQRMIm6tvaw0EU7WFOQ9DFvfip5rYv4G0HIrkTRo0H_VcEEFww7rrQNhmUFriQBlCfP8LEDNNXMSbPZrGXMEvh_xyqsyTWYHrorTnuYcRUHPZh4tq465n6Fzhi5AskYJi55ayj3Y7p32EPKDKRFYX55KZ3XFoBfCwZ0z65ia-lH0LldDGspWP1SgAyikj6b3p7IZECqtNLawu5hCC_xd7jGx4fkgn4OwzjBZNztlRfpdVWxWArIRv8HQ3J1_9phi1nKTb_mPVhzJAXheLIhXfAEuKzRR4wxFYzqZVTGI-sXQrLuPO23_S4DwMCfnq1BALFbE0i2hOVFgyYFAg98W1-szodebNQivq5LmeN6a5gZRG7P38j5Ipg4RtllBP2yhKI6Wvqu1BoQzkpbMDpSC2FxpDMYshUkAzsypkrd6ZIr3br55hqeEPWdYDNMx8bVegl3ApR8fXg_jdnXop8kqIJ-LVJe3Aq0CzYNV6gkWVX4fL94VT0T9Q9AbPj7gBiH2jQBlgfSANHHZjKWEbU8mEIYFPCdAcgsRRb3BCStFCY4xzeZTKQmLHqGaXTwk0CqTaZxjGj-ey_E7QZOHdCGWtgYXuJUu2NrkkxBPoV78fn78SVSkFfPzqkHw" },
        { name: "uuid",domain:"seller.snappshop.ir", value: "7f42c8f3-2d57-4e8d-b172-683fc84c6f5b" }

    )
    await page.goto("https://seller.snappshop.ir/inventory/add-product")
    let  selector  = `::-p-xpath(//button[text()='درخواست ایجاد محصول جدید'])`
    await page.waitForSelector(selector)
    await page.click(selector)
        selector  = `::-p-xpath(//button[text()='متوجه شدم'])`
    await page.waitForSelector(selector)
    await page.click(selector)
    const input = (await page.$("#image-cover")) as ElementHandle<HTMLInputElement>

    await input?.uploadFile("./"+imgPath[0])
    await page.waitForSelector("#upload-images-step-image")
    const secInput = (await page.$("#upload-images-step-image"))  as ElementHandle<HTMLInputElement>
    await secInput?.uploadFile("./"+imgPath[1])
    selector  = `::-p-xpath(//button[text()='ثبت و ادامه'])`
    await page.waitForSelector(selector)
    const subButton = await page.$(selector)
    console.log("Submit button"+subButton)
    await delay(1000)
    await subButton?.click()
}
const delay = (ms:number)=>{
    return new Promise((resolve)=>setTimeout(resolve,ms)); 
}
getProduct("09509013")