-- Create db user specifically for this assignment3

-- --Use the master db
-- create login damg7245team7 with password='YourPassword';
-- create user damg7245team7 for login damg7245team7;

-- -- Use the amkdb
-- create user damg7245team7 for login damg7245team7;
-- create schema assignment3;
-- alter user damg7245team7 with default_schema = assignment3;
-- alter role db_datareader add member damg7245team7;
-- alter role db_datawriter add member damg7245team7;
-- alter role db_ddladmin add member damg7245team7;


-- Create the application tables

CREATE TABLE UserCredentials
(
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    user_email NVARCHAR(255) NOT NULL,
    user_salt VARBINARY(16) NOT NULL,
    user_hashpassword NVARCHAR(255) NOT NULL,
    created_datetime DATETIME NOT NULL DEFAULT GETDATE(),
    updated_datetime DATETIME,
    lastlogin_datetime DATETIME,
    active BIT NOT NULL DEFAULT 1
);

CREATE TABLE ChatHistory
(
    chat_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    user_question NVARCHAR(MAX) NOT NULL,
    system_answer NVARCHAR(MAX) NOT NULL,
    created_datetime DATETIME NOT NULL DEFAULT GETDATE()
);

ALTER TABLE ChatHistory
ADD CONSTRAINT FK_ChatHistory_UserCredentials
FOREIGN KEY (user_id)
REFERENCES UserCredentials(user_id);
