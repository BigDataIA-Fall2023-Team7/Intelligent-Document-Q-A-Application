-- Use the mysql application dba user for this script
use db_damg7245team7;

CREATE TABLE IF NOT EXISTS `ApplicationLog` (
  `Application_LogId` int NOT NULL AUTO_INCREMENT,
  `Application_LogCorrelationID` varchar(255) DEFAULT NULL,
  `Application_Component` varchar(255) DEFAULT NULL,
  `Application_LogStatus` varchar(255) DEFAULT NULL,
  `Application_LogDetails` varchar(2000) DEFAULT NULL,
  `created_datetime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Application_LogId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

