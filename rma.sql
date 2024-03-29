CREATE TABLE `Brand` (
  `Brand_ID` Int,
  `Brand_Name` Varchar(20),
  `Brand_Details` XML,  --LONGTEXT instead of XML type, but data consists of XML code
  `Brand_Website` Varchar(255),
  `Brand_Category` Varchar(50),
  PRIMARY KEY (`Brand_ID`)
);

CREATE TABLE `ShippingtoBrand` (
  `Shipping_Brand_ID` Int,
  `Brand_ID` Int,
  `Shipping_Date` Date,
  `Return_Info` Varchar(255),
  `Cargo_Name` Varchar(50),
  PRIMARY KEY (`Shipping_Brand_ID`),
  FOREIGN KEY (`Brand_ID`) REFERENCES `Brand`(`Brand_ID`)
);

CREATE TABLE `Technician` (
  `Technician_ID` Int,
  `Tech_Name` Varchar(50),
  `Tech_Qual` Varchar(50),
  `Tech_Tiitle` Varchar(50),
  `Tech_Email` Varchar(50),
  `Tech_Pass` Varchar(255),
  PRIMARY KEY (`Technician_ID`)
);

CREATE TABLE `Model` (
  `Model_ID` Int,
  `Model_Name` Varchar(50),
  `Brand_ID` Int,
  `Model_Category` Varchar(50),
  `Model_Details` XML,
  PRIMARY KEY (`Model_ID`),
  FOREIGN KEY (`Brand_ID`) REFERENCES `Brand`(`Brand_ID`)
);

CREATE TABLE `Customer` (
  `Customer_ID` Int,
  `Customer_Name` Varchar(50),
  `Customer_Address` Varchar(255),
  `Customer_Phone` Varchar(20),
  `Customer_Email` Varchar(50),
  `Customer_Pass` Varchar(20),
  PRIMARY KEY (`Customer_ID`)
);

CREATE TABLE `Product` (
  `Product_ID` Int,
  `Product_Name` Varchar(50),
  `Product_Sold_Date` Date,
  `Serial_Number` Varchar(50),
  `Model_ID` Int,
  `Customer_ID` Int,
  `Product_Details` XML,
  PRIMARY KEY (`Product_ID`),
  FOREIGN KEY (`Model_ID`) REFERENCES `Model`(`Model_ID`),
  FOREIGN KEY (`Customer_ID`) REFERENCES `Customer`(`Customer_ID`)
);

CREATE TABLE `ReturntoCustomer` (
  `Return_Shipping_ID` Int,
  `Customer_ID` Int,
  `Cargo_Name` Varchar(50),
  `Shipping_Date` Date,
  `Return_Info` Varchar(255),
  PRIMARY KEY (`Return_Shipping_ID`),
  FOREIGN KEY (`Customer_ID`) REFERENCES `Customer`(`Customer_ID`)
);

CREATE TABLE `RMA` (
  `RMA_ID` Int,
  `Inspection_Start_Date` Date,
  `Inspection_Completion_Date` Date,
  `Product_Defect` Varchar(255),
  `Check_Issue` Varchar(255),
  `Result_Issue` Varchar(255),
  `Product_ID` Int,
  `Technician_ID` Int,
  `Return_Shipping_ID` Int,
  `Shipping_Brand_ID` Int,
  `RMAStatus` Varchar(50),
  `Warranty_Status` Varchar(20),
  PRIMARY KEY (`RMA_ID`),
  FOREIGN KEY (`Return_Shipping_ID`) REFERENCES `ReturntoCustomer`(`Return_Shipping_ID`),
  FOREIGN KEY (`Technician_ID`) REFERENCES `Technician`(`Technician_ID`),
  FOREIGN KEY (`Product_ID`) REFERENCES `Product`(`Product_ID`)
);

