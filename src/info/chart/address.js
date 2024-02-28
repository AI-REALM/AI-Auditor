const puppeteer = require("puppeteer");
const fs = require("fs");

const address = process.argv[2]

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}


(async () => {
  const browserURL = "http://127.0.0.1:9222";

  const browser = await puppeteer.connect({ browserURL });
  const page = await browser.newPage()
  await page.setViewport({ width:1600, height: 900});
  await page.goto(
    `https://de.fi/account/${address}/dashboard/portfolio-overview`,
    { waitUntil: 'networkidle0' }
  );
  try {
    let address 
    await page.waitForSelector('div.css-70qvj9 span', {timeout: 1000})
    address = await page.$$eval('div.css-70qvj9 span', (el) => el[0].getAttribute('aria-label'));
    let wallet = []
    await page.waitForSelector('div.five.wide.computer.sixteen.wide.mobile.sixteen.wide.tablet.column.jss154', {timeout: 1000})
    wallet = await page.$eval('div.five.wide.computer.sixteen.wide.mobile.sixteen.wide.tablet.column.jss154', (el) => el.textContent);
    // console.log(wallet)
    let crypto_info = []
    await page.waitForSelector('div.four.wide.computer.sixteen.wide.mobile.sixteen.wide.tablet.column.jss154', {timeout: 1000})
    crypto_info = await page.$$eval('div.four.wide.computer.sixteen.wide.mobile.sixteen.wide.tablet.column.jss154', (el) => el.map((e) => e.textContent));
    // console.log(crypto_info)
    let chain_info
    
    chain_info = await fetch('https://api.de.fi/v1/chains?enabled=true').then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Parse the response body as JSON
    }).then(data => {
        return data; // Here you have your JSON data
    }).catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
    });
    // console.log(chain_info)

    let returnValue = {
        address: address,
        wallet: wallet,
        cryptoInfo: crypto_info,
        chainInfo: chain_info
      };
    await page.close();
    await browser.disconnect();
    console.log(JSON.stringify(returnValue)); // Convert the object to a JSON string and print it
    process.exit(0);
  } catch {
    let returnValue = {
        errors: "empty account or invalid token",
      };
    await page.close();
    await browser.disconnect();
    console.log(JSON.stringify(returnValue)); // Convert the object to a JSON string and print it
    process.exit(0);
  }
})();


// document.querySelector('div.button-TPBYkbxL.button-gbkEfGm4.withText-gbkEfGm4.button-uO7HM85b.apply-common-tooltip.isInteractive-uO7HM85b').click()