-- View raw table
SELECT
*
FROM dbo.products

-- ******************************************************
-- ******************************************************

-- Determine Low, Medium, and High Prices
SELECT AVG(Price) AS mean, 
	   STDEV(Price) AS std,
	   MAX(Price) AS max,
	   MIN(Price) AS min,
	   (MAX(Price) - MIN(Price)) AS range
FROM dbo.products;

-- Query to categorize products based on their price
SELECT
	ProductID, -- Unique ID for each product
	ProductName, -- Name of each product
	Price, -- Price of each product
	--Category, -- Category for each product

	CASE -- Categroizes the products into price categories: Low, Medium, or High
		WHEN Price < 50 THEN 'Low'
		WHEN Price BETWEEN 50 AND 200 THEN 'Medium'
		ELSE 'High'
	END AS PriceCategory

FROM dbo.products;