DROP TABLE IF EXISTS `star_messages`;
CREATE TABLE `star_messages`
(
    `id`           bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'User ID (Primary Key)',
    `user_id`      bigint(20) unsigned NOT NULL COMMENT 'User id',
    `message_id`   varchar(64)         NOT NULL COMMENT 'Unique message id',
    `hip`          varchar(32)         NOT NULL COMMENT 'HIP identifier',
    `from`         varchar(32)         NOT NULL COMMENT 'From whom send this message',
    `message`      text                NOT NULL COMMENT 'Message content',
    `is_deleted`   tinyint(1)          NOT NULL DEFAULT 0 COMMENT 'Soft delete flag (0: Active, 1: Deleted)',
    
    PRIMARY KEY (`id`),
    UNIQUE KEY `message_id` (`message_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Star messages table';