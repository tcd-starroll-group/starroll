-- ============================================================
-- StarRoll Blog Table
-- ============================================================

-- Blog content table
DROP TABLE IF EXISTS `blog`;
CREATE TABLE `blog`
(
    `blog_id`          bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Blog ID (Primary Key)',
    `user_id`     bigint(20) unsigned NOT NULL COMMENT 'Author user ID (FK -> user.id)',
    `hip`         int(11)             NOT NULL COMMENT 'HIP star index the blog belongs to',
    `title`       varchar(256)        NOT NULL COMMENT 'Blog title',
    `content`     text                DEFAULT NULL COMMENT 'Blog content',
    `image_urls`  json                DEFAULT NULL COMMENT 'List of image URLs (JSON array)',
    `like_count`  int(11)             NOT NULL DEFAULT 0 COMMENT 'Cached like count',
    `comment_count` int(11)           NOT NULL DEFAULT 0 COMMENT 'Cached comment count',
    `created_at`  timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at`  timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    `is_deleted`  tinyint(1)          NOT NULL DEFAULT 0 COMMENT 'Soft delete flag (0: Active, 1: Deleted)',

    PRIMARY KEY (`blog_id`),
    KEY `idx_hip` (`hip`),
    KEY `idx_user_id` (`user_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Blog posts linked to stars';


-- Comments table
DROP TABLE IF EXISTS `blog_comment`;
CREATE TABLE `blog_comment`
(
    `comment_id`          bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Comment ID (Primary Key)',
    `blog_id`     bigint(20) unsigned NOT NULL COMMENT 'FK -> blog.id',
    `user_id`     bigint(20) unsigned NOT NULL COMMENT 'Commenter user ID (FK -> user.id)',
    `content`     varchar(1024)       NOT NULL COMMENT 'Comment text',
    `created_at`  timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `is_deleted`  tinyint(1)          NOT NULL DEFAULT 0 COMMENT 'Soft delete flag',

    PRIMARY KEY (`comment_id`),
    KEY `idx_blog_id` (`blog_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Blog comments';


-- Likes table
DROP TABLE IF EXISTS `blog_like`;
CREATE TABLE `blog_like`
(
    `like_id`          bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Like record ID',
    `blog_id`     bigint(20) unsigned NOT NULL COMMENT 'FK -> blog.id',
    `user_id`     bigint(20) unsigned NOT NULL COMMENT 'FK -> user.id',
    `created_at`  timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Like timestamp',

    PRIMARY KEY (`like_id`),
    UNIQUE KEY `uk_blog_user` (`blog_id`, `user_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Blog likes (one per user per blog)';


-- Saved table
DROP TABLE IF EXISTS `blog_save`;
CREATE TABLE `blog_save`
(
    `save_id`          bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Save record ID',
    `blog_id`     bigint(20) unsigned NOT NULL COMMENT 'FK -> blog.id',
    `user_id`     bigint(20) unsigned NOT NULL COMMENT 'FK -> user.id',
    `created_at`  timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Save timestamp',

    PRIMARY KEY (`save_id`),
    UNIQUE KEY `uk_blog_user` (`blog_id`, `user_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Blog saves / bookmarks';


-- report table
DROP TABLE IF EXISTS `blog_report`;
CREATE TABLE `blog_report`
(
    `report_id`          bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Report record ID',
    `blog_id`     bigint(20) unsigned NOT NULL COMMENT 'FK -> blog.id',
    `user_id`     bigint(20) unsigned NOT NULL COMMENT 'Reporter user ID (FK -> user.id)',
    `reason`      varchar(512)        DEFAULT '' COMMENT 'Report reason (optional)',
    `created_at`  timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Report timestamp',

    PRIMARY KEY (`report_id`),
    UNIQUE KEY `uk_blog_user` (`blog_id`, `user_id`),
    KEY `idx_blog_id` (`blog_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Blog reports';