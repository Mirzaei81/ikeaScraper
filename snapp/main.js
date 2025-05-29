"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = __importDefault(require("axios"));
const jimp_1 = require("jimp");
const puppeteer_core_1 = __importDefault(require("puppeteer-core"));
function getProduct(sku) {
    return __awaiter(this, void 0, void 0, function* () {
        const url = `https://zardaan.com/wp-json/wc/v3/products?sku=${sku}`;
        const headers = {
            'Authorization': 'Basic Y2tfYTdjNGVlM2U5NTc1MDI4MWQ5MTg1MmRlOTJkMjc1NWNkMDUyZGUyMjpjc18yNWU4NDQ4YzZkMWE1YzdkYTlhMGFlMDE0Y2M4ZWQ2YzViMGU2MWE5',
            'Content-Type': 'application/json',
            'Cookie': 'pxcelPage_c01002=1'
        };
        // Fetch product data
        const response = yield axios_1.default.get(url, { headers });
        const zProd = response.data;
        // Process first 3 images
        const imgPath = [];
        for (let img of zProd[0].images.slice(0, 2)) {
            // Download image
            const imgResponse = yield axios_1.default.get(img.src, { responseType: 'arraybuffer' });
            const ext = img.src.split('.').pop().toUpperCase() === 'JPG' ? 'JPEG' : img.src.split('.').pop().toUpperCase();
            // Load and resize image
            const image = yield jimp_1.Jimp.read(Buffer.from(imgResponse.data));
            image.resize({ w: 600, h: 600 }).write(`output_${img.id}.${ext.toLowerCase()}`);
            imgPath.push(`output_${img.id}.${ext.toLowerCase()}`);
        }
        const browser = yield puppeteer_core_1.default.launch({ executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", headless: false });
        const page = yield browser.newPage();
        page.setCookie({ name: "access-token", domain: "seller.snappshop.ir", value: "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMDUiLCJqdGkiOiJhMjg1M2Y3NzE5MzI2YzYxNGQ4ZWM2Y2ZlM2IwZjQ1MGYwMDk0ZWU4ZWM4ZGVkZmNiMTNjNjU1NGVmNTE3Y2U5YzgwMzQxZmJhMGY1OTg0MiIsImlhdCI6MTc0ODA4MDQ3MS45Mzk5MTYsIm5iZiI6MTc0ODA4MDQ3MS45Mzk5MTksImV4cCI6MTc0ODY4NTI3MS45MzQ3NDksInN1YiI6IjQyNzM5MjAiLCJzY29wZXMiOlsicm9sZTpzZWxsZXIiXSwiYXV0aG9yaXphdGlvbl9kZXRhaWxzIjpbeyJ0eXBlIjoicHVzaCIsImxvY2F0aW9ucyI6WyJjbHVzdGVyOjEwNS92aG9zdDpwcy9xdWV1ZTptcXR0LSovcm91dGluZy1rZXk6di1nZVpsODEiXSwiYWN0aW9ucyI6WyJyZWFkIiwid3JpdGUiLCJjb25maWd1cmUiXX0seyJ0eXBlIjoicHVzaCIsImxvY2F0aW9ucyI6WyJjbHVzdGVyOjEwNS92aG9zdDpwcy9leGNoYW5nZTphbXEudG9waWMvcm91dGluZy1rZXk6di1nZVpsODEiXSwiYWN0aW9ucyI6WyJyZWFkIl19XX0.o91zwFyBgoZSvV-99NJE7GxLAmrmbDBU0xopHZ66OU4rwFUNbxDOQRMIm6tvaw0EU7WFOQ9DFvfip5rYv4G0HIrkTRo0H_VcEEFww7rrQNhmUFriQBlCfP8LEDNNXMSbPZrGXMEvh_xyqsyTWYHrorTnuYcRUHPZh4tq465n6Fzhi5AskYJi55ayj3Y7p32EPKDKRFYX55KZ3XFoBfCwZ0z65ia-lH0LldDGspWP1SgAyikj6b3p7IZECqtNLawu5hCC_xd7jGx4fkgn4OwzjBZNztlRfpdVWxWArIRv8HQ3J1_9phi1nKTb_mPVhzJAXheLIhXfAEuKzRR4wxFYzqZVTGI-sXQrLuPO23_S4DwMCfnq1BALFbE0i2hOVFgyYFAg98W1-szodebNQivq5LmeN6a5gZRG7P38j5Ipg4RtllBP2yhKI6Wvqu1BoQzkpbMDpSC2FxpDMYshUkAzsypkrd6ZIr3br55hqeEPWdYDNMx8bVegl3ApR8fXg_jdnXop8kqIJ-LVJe3Aq0CzYNV6gkWVX4fL94VT0T9Q9AbPj7gBiH2jQBlgfSANHHZjKWEbU8mEIYFPCdAcgsRRb3BCStFCY4xzeZTKQmLHqGaXTwk0CqTaZxjGj-ey_E7QZOHdCGWtgYXuJUu2NrkkxBPoV78fn78SVSkFfPzqkHw" }, { name: "uuid", domain: "seller.snappshop.ir", value: "7f42c8f3-2d57-4e8d-b172-683fc84c6f5b" });
        yield page.goto("https://seller.snappshop.ir/inventory/add-product");
        let selector = `::-p-xpath(//button[text()='درخواست ایجاد محصول جدید'])`;
        yield page.waitForSelector(selector);
        yield page.click(selector);
        selector = `::-p-xpath(//button[text()='متوجه شدم'])`;
        yield page.waitForSelector(selector);
        yield page.click(selector);
        const input = (yield page.$("#image-cover"));
        yield (input === null || input === void 0 ? void 0 : input.uploadFile("./" + imgPath[0]));
        yield page.waitForSelector("#upload-images-step-image");
        const secInput = (yield page.$("#upload-images-step-image"));
        yield (secInput === null || secInput === void 0 ? void 0 : secInput.uploadFile("./" + imgPath[1]));
        selector = `::-p-xpath(//button[text()='ثبت و ادامه'])`;
        yield page.waitForSelector(selector);
        const subButton = yield page.$(selector);
        console.log("Submit button" + subButton);
        yield delay(1000);
        yield (subButton === null || subButton === void 0 ? void 0 : subButton.click());
    });
}
const delay = (ms) => {
    return new Promise((resolve) => setTimeout(resolve, ms));
};
getProduct("09509013");
