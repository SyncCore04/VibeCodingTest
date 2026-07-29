-- =====================================================
-- 用户管理系统 - 建表 SQL
-- 执行前请确保数据库 user_manage 已创建
-- =====================================================

CREATE DATABASE IF NOT EXISTS user_manage
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE user_manage;

DROP TABLE IF EXISTS t_user;
CREATE TABLE t_user (
    id          BIGINT       AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username    VARCHAR(50)  NOT NULL              COMMENT '用户名',
    phone       VARCHAR(20)  NOT NULL              COMMENT '手机号',
    email       VARCHAR(100) DEFAULT NULL          COMMENT '邮箱',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted     TINYINT      DEFAULT 0             COMMENT '逻辑删除: 0未删除 / 1已删除',
    INDEX idx_username (username),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

SELECT * FROM t_user;
