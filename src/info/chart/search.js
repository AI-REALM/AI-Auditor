const puppeteer = require("puppeteer");
const fs = require("fs");

const address = process.argv[2]

async function fetchGraphQLData(query, variables) {
    const response = await fetch('https://api-scanner.defiyield.app/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Include any other headers you need to send
      },
      body: JSON.stringify({
        query,
        variables
      })
    });
  
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  
    const data = await response.json();
    return data;
  }

const search_query = `
  query($address: String!) {
    search(query: $address) {              
      type
        results {
          id
          address
          network
          name
          logo
          category
          score
          createdAt
          liquidity
          category
          whitelisted
        }
    }
  }`
const variables_search = {
    "address": address
  };

(async () => {

  const contract = await fetchGraphQLData(search_query, variables_search);
  const chain_info = await fetch('https://api.de.fi/v1/chains?enabled=true').then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Parse the response body as JSON
    }).then(data => {
        return data; // Here you have your JSON data
    }).catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
    });
  let returnValue
  returnValue = {
    contract: contract.data.search,
    chaininfo:chain_info
  };
  console.log(JSON.stringify(returnValue)); // Convert the object to a JSON string and print it
  process.exit(0);
})();