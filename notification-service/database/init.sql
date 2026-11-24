CREATE DATABASE UniBook_Notifications;
GO
USE UniBook_Notifications;
GO
CREATE TABLE Notifications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    event_type NVARCHAR(50) NOT NULL,
    reservation_id INT NOT NULL,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    message NVARCHAR(500) NOT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'Sent',
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO