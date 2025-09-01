SELECT *
FROM dbo.customer_journey

-- ******************************************************
-- ******************************************************

-- Common Table Expression (CTE) to identify and tag duplicate records
WITH DuplicateRecords AS (
	SELECT
		JourneyID,
		CustomerID,
		ProductID,
		VisitDate,
		Stage,
		Action,
		Duration,
		-- Use ROW_NUMBER() to assign a unique row number to each record w/in the partition defined below
		ROW_NUMBER() OVER (
			-- PARTITION BY groups the rows based on the specified columns that should be unique
			PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action
			-- ORDER BY defines how to order the rows w/in each partition (usually by a unique identifier)
			ORDER BY JourneyID
		) AS row_num -- This creates a new column 'row_num' that numbers each row w/in its partition
	FROM 
		dbo.customer_journey
)

-- Select all records from the CTE where row_num > 1, which indicates duplicate entries
SELECT *
FROM DuplicateRecords
WHERE row_num > 1 -- row_num = 1 filters out first occurance -- rown_num > 1 only shows duplicates
ORDER BY JourneyID

-- Outer query selects the final cleaned and standardized data
SELECT
	JourneyID,
	CustomerID,
	ProductID,
	VisitDate,
	Stage,
	Action,
	COALESCE(Duration, avg_duration) AS Duration
FROM
	(
		-- Subquery to process and clean the data
		SELECT
			JourneyID,
			CustomerID,
			ProductID,
			VisitDate,
			Upper(Stage) AS Stage, -- Converts Stage values to uppercase for consistency
			Action,
			Duration,
			AVG(Duration) OVER (PARTITION BY VisitDate) AS avg_duration, -- Calculates the average duration for each date
			ROW_NUMBER() OVER (
				PARTITION BY CustomerID, ProductID, VisitDate, UPPER(Stage), Action
				ORDER BY JourneyID
			) AS row_num
		FROM
			dbo.customer_journey
	) AS subquery
WHERE
	row_num = 1
ORDER BY
	JourneyID;
