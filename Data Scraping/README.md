# Task 1: Data Scraping – Experimentation and Approach

This folder contains my work and experiments for Task 1 of the Data Intern Assignment: scraping nutrient data from the Soil Health Dashboard.

## Approaches I Tried

## `1. requests + BeautifulSoup`

### Goal: 

- Try to access and parse the data directly using requests and bs4.

### Result: 
- Unsuccessful.

### Why: 
- The page is highly dynamic and relies on JavaScript to load content. HTML parsing was not feasible due to missing data elements in the static HTML response.

## `2. Selenium Automation`

### Goal: 
- Use Selenium to interact with dynamic elements and extract data.

### Result: 
- Partially successful.

### Challenges:

- Dynamic dropdowns for State → District → Block required careful wait handling.

- Interacting with dynamically updated tables was unreliable.

- Handling interruptions, retries, and ensuring complete data extraction was complex and time-consuming.

## `3. Export Button + CSV Download`

### Final Approach: 
- I switched to a more manual but stable method using Selenium to automate clicks on:

- The Export button

- Then the CSV button

### Result: 
- Successfully downloaded data as CSV files.

### Post-Processing: 
- Parsed and rearranged the downloaded files into the required folder structure.

### Outcome

- The final solution is working and error-free, but comes with a major drawback:

- It would easily take 50+ hours to scrape all the data due to the amount of manual export actions, page loading delays, and dependency on uninterrupted internet access.

### Notes

- This was a great learning experience in handling complex web scraping scenarios.

- I now have a better understanding of working with JavaScript-heavy sites and when to switch from scraping to alternative data collection strategies like browser automation and CSV exports.
