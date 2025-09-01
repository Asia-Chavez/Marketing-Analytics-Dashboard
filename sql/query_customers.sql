SELECT
*
FROM dbo.customers

SELECT
*
FROM dbo.geography

-- ******************************************************
-- ******************************************************

-- SQL statement to join dim_customers with dim_geography to enrich customer data with geographic information
SELECT
	c.CustomerID, 
	c.CustomerName,
	c.Email,
	c.Gender,
	c.Age,
	g.Country,
	g.City
FROM
	dbo.customers AS c
LEFT JOIN
-- RIGHT JOIN
-- INNER JOIN
-- FULL OUTER JOIN
	dbo.geography g
ON
	c.GeographyID = g.GeographyID;

-- Can CASE this by age (young, old)
-- Can CASE by Country, City, Gender, etc.