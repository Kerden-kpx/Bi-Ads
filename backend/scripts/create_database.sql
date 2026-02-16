-- 创建数据库
CREATE DATABASE IF NOT EXISTS ads_data 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE ads_data;

-- 显示数据库信息
SELECT 'Database created successfully!' AS message;
SELECT DATABASE() AS current_database;

